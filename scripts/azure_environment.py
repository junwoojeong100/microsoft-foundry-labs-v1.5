"""Create an isolated workshop RG; never deletes resources or changes a subscription default."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from workshop import save_json

LEDGER = ROOT / "results/azure-environment.json"


def persist(state: dict) -> None:
    if LEDGER.exists():
        current = json.loads(LEDGER.read_text(encoding="utf-8"))
        for key in ("operations", "role_assignments"):
            items = current.get(key, []) + state.get(key, [])
            state[key] = list({json.dumps(item, sort_keys=True): item for item in items}.values())
        state = {**current, **state}
    save_json(LEDGER, state)


def az(*args: str, timeout: int = 180) -> object:
    result = subprocess.run(
        ["az", *args, "--only-show-errors", "--output", "json"],
        text=True, capture_output=True, timeout=timeout, check=False,
    )
    if result.returncode:
        # Azure commands here never return keys, access tokens, or connection secrets.
        raise RuntimeError(f"az {args[0]} {args[1]} failed: {result.stderr.strip()}")
    return json.loads(result.stdout) if result.stdout.strip() else None


def owned() -> dict:
    state = json.loads(LEDGER.read_text(encoding="utf-8"))
    group = az("group", "show", "--subscription", state["subscription"], "--name", state["resource_group"])
    if group["id"].lower() != state["resource_group_id"].lower() or group.get("tags", {}).get("validationRun") != state["run_id"]:
        raise ValueError("RG identity/ownership mismatch. No changes are allowed.")
    return state


def create(args: argparse.Namespace) -> None:
    if LEDGER.exists():
        raise ValueError("An environment ledger already exists. It will not be overwritten.")
    if not args.subscription or not args.location:
        raise ValueError("--subscription and --location are required.")
    account = az("account", "show", "--subscription", args.subscription)
    if account["state"] != "Enabled":
        raise ValueError("Subscription is not enabled.")
    suffix = datetime.now(timezone.utc).strftime("%y%m%d") + uuid4().hex[:6]
    run_id = f"contoso-a-{suffix}"
    rg = f"rg-{run_id}"
    if az("group", "exists", "--subscription", args.subscription, "--name", rg):
        raise ValueError("Name collision; no existing RG will be reused.")
    state = {
        "schema": "contoso-environment-v1", "run_id": run_id,
        "repository": "junwoojeong100/microsoft-foundry-labs-v1.5", "repository_id": 1396573688,
        "subscription": account["id"], "tenant": account["tenantId"], "location": args.location,
        "resource_group": rg,
        "resource_group_id": f"/subscriptions/{account['id']}/resourceGroups/{rg}",
        "account_name": f"ai-{run_id}", "project_name": "contoso-workshop",
        "search_name": f"srch-{run_id}", "created_at": datetime.now(timezone.utc).isoformat(),
        "cost_authorization": args.cost_authorization,
        "retention": "Do not delete. Stop sessions and schedules; retain resources until explicit approval.",
        "resources": [], "operations": [],
    }
    persist(state)
    group = az(
        "group", "create", "--subscription", account["id"], "--name", rg, "--location", args.location,
        "--tags", "repository=microsoft-foundry-labs-v1.5", "scenario=Contoso", f"validationRun={run_id}",
        "retention=retain-until-explicit-approval",
    )
    state["resource_group_id"] = group["id"]
    state["operations"].append({"step": "create-rg", "status": "succeeded"})
    persist(state)
    print(json.dumps({"resource_group": rg, "location": args.location, "ledger": str(LEDGER.relative_to(ROOT))}))


def foundation(args: argparse.Namespace) -> None:
    state = owned()
    required = ("chat_model", "chat_version", "judge_model", "judge_version", "embedding_model", "embedding_version", "model_sku")
    if any(not getattr(args, key) for key in required):
        raise ValueError("Explicit model names, versions, and SKU are required; check regional catalog/quota first.")
    existing = az("resource", "list", "--subscription", state["subscription"], "--resource-group", state["resource_group"])
    if existing and not args.resume:
        raise ValueError("Foundation requires an empty owned RG. Inspect any partial deployment; never overwrite automatically.")
    for resource in existing:
        if resource.get("tags", {}).get("validationRun") != state["run_id"]:
            raise ValueError("A resource is not tagged as owned by this run; resume refused.")
    parameters = {
        "accountName": state["account_name"], "projectName": state["project_name"], "runId": state["run_id"],
        "chatModel": args.chat_model, "chatVersion": args.chat_version,
        "judgeModel": args.judge_model, "judgeVersion": args.judge_version,
        "embeddingModel": args.embedding_model, "embeddingVersion": args.embedding_version,
        "modelSku": args.model_sku, "capacity": args.capacity,
    }
    deployment = az(
        "deployment", "group", "create", "--subscription", state["subscription"],
        "--resource-group", state["resource_group"], "--name", "contoso-foundation",
        "--template-file", str(ROOT / "infra/main.bicep"), "--parameters",
        *[f"{key}={value}" for key, value in parameters.items()], timeout=1200,
    )
    state["foundation"] = deployment["properties"]["outputs"]
    project = az(
        "rest", "--method", "get",
        "--url", state["foundation"]["projectId"]["value"] + "?api-version=2025-06-01",
    )
    endpoints = project["properties"]["endpoints"]
    state["project_endpoint"] = endpoints["AI Foundry API"].rstrip("/")
    state["model_deployments"] = {"chat": "contoso-chat", "judge": "contoso-judge", "embedding": "contoso-embedding"}
    state["model_configuration"] = parameters
    state["operations"].append({"step": "foundation", "status": deployment["properties"]["provisioningState"]})
    persist(state)
    status()


def roles() -> None:
    state = owned()
    user = az("ad", "signed-in-user", "show", "--query", "id")
    scope = state["foundation"]["projectId"]["value"]
    grants = [
        (user, "User", "53ca6127-db72-4b80-b1b0-d745d6d5456d", scope),
        (user, "User", "Cognitive Services OpenAI User", state["foundation"]["accountId"]["value"]),
        (state["foundation"]["projectPrincipalId"]["value"], "ServicePrincipal",
         "Cognitive Services OpenAI User", state["foundation"]["accountId"]["value"]),
        (state["foundation"]["projectPrincipalId"]["value"], "ServicePrincipal",
         "53ca6127-db72-4b80-b1b0-d745d6d5456d", state["foundation"]["accountId"]["value"]),
    ]
    for principal, principal_type, role, resource in grants:
        record = az(
            "role", "assignment", "create", "--subscription", state["subscription"],
            "--assignee-object-id", principal, "--assignee-principal-type", principal_type,
            "--role", role, "--scope", resource,
        )
        state.setdefault("role_assignments", []).append({"id": record["id"], "scope": resource, "role": role})
    persist(state)
    print("Project-scoped Foundry User assignment recorded; no subscription role was created.")


def search() -> None:
    state = owned()
    services = az("search", "service", "list", "--subscription", state["subscription"], "--resource-group", state["resource_group"])
    if services:
        raise ValueError("Search already exists in this RG. Inspect ownership instead of overwriting.")
    resource = az(
        "search", "service", "create", "--subscription", state["subscription"],
        "--resource-group", state["resource_group"], "--name", state["search_name"],
        "--location", state["location"], "--sku", "basic", "--partition-count", "1", "--replica-count", "1",
        "--identity-type", "SystemAssigned", "--disable-local-auth", "true",
        "--tags", "repository=microsoft-foundry-labs-v1.5", "scenario=Contoso", f"validationRun={state['run_id']}",
        "--semantic-search", "free", timeout=600,
    )
    state["search_id"] = resource["id"]
    state["search_endpoint"] = f"https://{state['search_name']}.search.windows.net"
    persist(state)
    user = az("ad", "signed-in-user", "show", "--query", "id")
    for principal, principal_type, role in [
        (user, "User", "Search Service Contributor"),
        (user, "User", "Search Index Data Contributor"),
        (state["foundation"]["projectPrincipalId"]["value"], "ServicePrincipal", "Search Index Data Reader"),
    ]:
        grant = az(
            "role", "assignment", "create", "--subscription", state["subscription"],
            "--assignee-object-id", principal, "--assignee-principal-type", principal_type,
            "--role", role, "--scope", resource["id"],
        )
        state.setdefault("role_assignments", []).append({"id": grant["id"], "scope": resource["id"], "role": role})
    persist(state)
    status()


def monitoring() -> None:
    state = owned()
    if state.get("monitoring"):
        raise ValueError("Monitoring has already been recorded; no existing resource is overwritten.")
    deployment = az(
        "deployment", "group", "create", "--subscription", state["subscription"],
        "--resource-group", state["resource_group"], "--name", "contoso-observability",
        "--template-file", str(ROOT / "infra/observability.bicep"), "--parameters",
        f"accountName={state['account_name']}", f"projectName={state['project_name']}", f"runId={state['run_id']}",
        timeout=600,
    )
    state["monitoring"] = deployment["properties"]["outputs"]
    persist(state)
    status()


def status() -> None:
    state = owned()
    # Recover safe outputs after a partial/interrupted client, without repeating deployment.
    deployments = az("deployment", "group", "list", "--subscription", state["subscription"],
                     "--resource-group", state["resource_group"])
    for item in deployments:
        if item["name"] == "contoso-observability" and item["properties"]["provisioningState"] == "Succeeded":
            state["monitoring"] = item["properties"]["outputs"]
    state["resources"] = az(
        "resource", "list", "--subscription", state["subscription"], "--resource-group", state["resource_group"],
        "--query", "[].{id:id,name:name,type:type,location:location}",
    )
    state["last_checked_at"] = datetime.now(timezone.utc).isoformat()
    if state.get("foundation"):
        state["model_inventory"] = az(
            "cognitiveservices", "account", "deployment", "list", "--subscription", state["subscription"],
            "--resource-group", state["resource_group"], "--name", state["account_name"],
            "--query", "[].{id:id,name:name,model:properties.model,sku:sku,state:properties.provisioningState}",
        )
    persist(state)
    print(json.dumps(state["resources"], ensure_ascii=False, indent=2))


def throughput(capacity: int) -> None:
    if not 1 <= capacity <= 100:
        raise ValueError("Capacity must be 1..100; quota is not a spend cap.")
    state = owned()
    for key, deployment_name in state["model_deployments"].items():
        current = az("cognitiveservices", "account", "deployment", "show", "--subscription", state["subscription"],
                     "--resource-group", state["resource_group"], "--name", state["account_name"],
                     "--deployment-name", deployment_name)
        model = current["properties"]["model"]
        if current["sku"]["name"] not in {"Standard", "GlobalStandard", "DataZoneStandard"}:
            raise ValueError("Refuse throughput changes on reserved/provisioned deployments.")
        az("rest", "--method", "put", "--url", current["id"] + "?api-version=2025-06-01",
           "--body", json.dumps({
               "sku": {"name": current["sku"]["name"], "capacity": capacity},
               "properties": {"model": {key: model[key] for key in ("name", "version", "format")},
                              "versionUpgradeOption": "NoAutoUpgrade"},
           }), timeout=300)
        state["operations"].append({"step": "throughput", "deployment": key, "capacity": capacity, "model_unchanged": model})
        persist(state)
    print(f"Owned online deployments now have capacity {capacity}; no PTU or token-spend limit was implied.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", choices=["create", "foundation", "roles", "search", "monitoring", "status", "throughput"])
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--subscription")
    parser.add_argument("--location")
    parser.add_argument("--cost-authorization", help="Record the user's explicit monetary limit or explicit no-limit authorization.")
    for field in ("chat-model", "chat-version", "judge-model", "judge-version", "embedding-model", "embedding-version"):
        parser.add_argument("--" + field)
    parser.add_argument("--model-sku", choices=["GlobalStandard", "DataZoneStandard", "Standard"])
    parser.add_argument("--capacity", type=int, default=10)
    parser.add_argument("--resume", action="store_true", help="Explicitly resume only owned partial foundation resources.")
    args = parser.parse_args()
    if not args.live:
        print(f"PLAN ONLY: {args.step}; no Azure calls or changes.")
        return
    if args.step == "create":
        if not args.cost_authorization:
            raise ValueError("Record explicit --cost-authorization before creating the environment.")
        create(args)
    elif args.step == "foundation":
        if not 1 <= args.capacity <= 100:
            raise ValueError("Capacity must be 1..100; verify model-specific quota units.")
        foundation(args)
    elif args.step == "throughput":
        throughput(args.capacity)
    else:
        {"roles": roles, "search": search, "monitoring": monitoring, "status": status}[args.step]()


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        if LEDGER.exists():
            state = json.loads(LEDGER.read_text(encoding="utf-8"))
            state["operations"].append({
                "at": datetime.now(timezone.utc).isoformat(), "status": "failed", "error": str(exc),
            })
            persist(state)
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
