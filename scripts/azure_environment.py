"""Create an isolated workshop RG; never deletes resources or changes a subscription default."""

from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time
from uuid import UUID, uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from workshop import LANGUAGE, save_json

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
        # Command arguments never contain keys, access tokens, or connection secrets.
        raise RuntimeError(f"az {args[0]} {args[1]} failed: {result.stderr.strip()}")
    return json.loads(result.stdout) if result.stdout.strip() else None


def owned(*, verify_location: bool = False) -> dict:
    state = json.loads(LEDGER.read_text(encoding="utf-8"))
    if state.get("language", "ko") != LANGUAGE:
        raise ValueError("Selected language differs from the owned environment. No changes are allowed.")
    group = az("group", "show", "--subscription", state["subscription"], "--name", state["resource_group"])
    if group["id"].lower() != state["resource_group_id"].lower() or group.get("tags", {}).get("validationRun") != state["run_id"]:
        raise ValueError("RG identity/ownership mismatch. No changes are allowed.")
    if verify_location and (
        state.get("repository_id") != 1396573688
        or group.get("tags", {}).get("repository") != "microsoft-foundry-labs-v1.5"
        or not isinstance(group.get("location"), str)
        or group["location"].lower() != str(state.get("location", "")).lower()
    ):
        raise ValueError("Foundation repository/region does not match the owned resource group.")
    return state


def current_user_id(state: dict) -> str:
    account = az("account", "show", "--subscription", state["subscription"])
    if account["tenantId"] != state["tenant"] or account["user"]["type"] != "user":
        raise ValueError("Environment setup requires the signed-in user in the owned tenant.")
    token = az("account", "get-access-token", "--subscription", state["subscription"],
               "--resource", "https://management.azure.com", "--query", "accessToken")
    try:
        encoded = token.split(".")[1]
        claims = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
        principal = str(UUID(claims["oid"]))
        if claims["tid"] != state["tenant"] or claims.get("idtyp") == "app":
            raise ValueError("Caller identity does not match the approved user and tenant.")
    except (KeyError, ValueError, IndexError, TypeError) as exc:
        raise ValueError("Cannot verify the signed-in user's identity from the ARM credential.") from exc
    return principal


def create(args: argparse.Namespace) -> None:
    if LEDGER.exists():
        raise ValueError("An environment ledger already exists. It will not be overwritten.")
    if not args.subscription or not args.location:
        raise ValueError("--subscription and --location are required.")
    account = az("account", "show", "--subscription", args.subscription)
    if account["state"] != "Enabled":
        raise ValueError("Subscription is not enabled.")
    suffix = datetime.now(timezone.utc).strftime("%y%m%d") + uuid4().hex[:6]
    run_id = f"contoso-{'en' if LANGUAGE == 'en' else 'a'}-{suffix}"
    rg = f"rg-{run_id}"
    if az("group", "exists", "--subscription", args.subscription, "--name", rg):
        raise ValueError("Name collision; no existing RG will be reused.")
    state = {
        "schema": "contoso-environment-v1", "run_id": run_id, "language": LANGUAGE,
        "repository": "junwoojeong100/microsoft-foundry-labs-v1.5", "repository_id": 1396573688,
        "subscription": account["id"], "tenant": account["tenantId"], "location": args.location,
        "resource_group": rg,
        "resource_group_id": f"/subscriptions/{account['id']}/resourceGroups/{rg}",
        "account_name": f"ai-{run_id}", "project_name": "contoso-workshop-en" if LANGUAGE == "en" else "contoso-workshop",
        "search_name": f"srch-{run_id}", "created_at": datetime.now(timezone.utc).isoformat(),
        "cost_authorization": args.cost_authorization,
        "retention": "Do not delete. Stop sessions and schedules; retain resources until explicit approval.",
        "resources": [], "operations": [],
    }
    persist(state)
    group = az(
        "group", "create", "--subscription", account["id"], "--name", rg, "--location", args.location,
        "--tags", "repository=microsoft-foundry-labs-v1.5", "scenario=Contoso", f"validationRun={run_id}",
        "retention=retain-until-explicit-approval", f"language={LANGUAGE}",
    )
    state["resource_group_id"] = group["id"]
    state["operations"].append({"step": "create-rg", "status": "succeeded"})
    persist(state)
    print(json.dumps({"resource_group": rg, "location": args.location, "ledger": str(LEDGER.relative_to(ROOT))}))


def foundation(args: argparse.Namespace) -> None:
    from model_capacity import (
        Management, ROLES, initial_capacity_plan, inspect_deployments, model_catalog,
        require_ready, requirements, validate_deployment,
    )

    state = owned(verify_location=True)
    required = ("chat_model", "chat_version", "judge_model", "judge_version", "embedding_model", "embedding_version", "model_sku")
    if any(not getattr(args, key) for key in required):
        raise ValueError("Explicit model names, versions, and SKU are required; check regional catalog/quota first.")
    existing = az("resource", "list", "--subscription", state["subscription"], "--resource-group", state["resource_group"])
    if existing and not args.resume:
        raise ValueError("Foundation requires an empty owned RG. Inspect any partial deployment; never overwrite automatically.")
    for resource in existing:
        if resource.get("tags", {}).get("validationRun") != state["run_id"]:
            raise ValueError("A resource is not tagged as owned by this run; resume refused.")
    management = Management(az)
    models = {
        role: {"name": getattr(args, role + "_model"), "version": getattr(args, role + "_version")}
        for role in ROLES
    }
    deployment_names = {role: "contoso-" + role for role in ROLES}
    account_id = state["resource_group_id"] + "/providers/Microsoft.CognitiveServices/accounts/" + state["account_name"]
    current_models = {}
    if any(resource["id"].lower() == account_id.lower() for resource in existing):
        inventory = management.call(
            "cognitiveservices", "account", "deployment", "list", "--subscription", state["subscription"],
            "--resource-group", state["resource_group"], "--name", state["account_name"],
        )
        if not isinstance(inventory, list):
            raise ValueError("Cannot verify existing model allocations for resume.")
        for current in inventory:
            for role, name in deployment_names.items():
                expected_id = account_id + "/deployments/" + name
                if str(current.get("id", "")).lower() == expected_id.lower():
                    validate_deployment(current, expected_id)
                    tags = current.get("tags") or {}
                    if not isinstance(tags, dict) or tags.get("validationRun", state["run_id"]) != state["run_id"]:
                        raise ValueError("Existing model belongs to a different run; resume refused.")
                    if role in current_models:
                        raise ValueError("Duplicate model deployment readback; resume refused.")
                    current_models[role] = current
    catalog = model_catalog(state, management)
    quota = management.call(
        "cognitiveservices", "usage", "list", "--subscription", state["subscription"],
        "--location", state["location"],
    )
    plan = initial_capacity_plan(
        catalog, quota, models, args.model_sku, learners=args.learners,
        max_capacity=args.max_capacity, existing=current_models,
    )
    parameters = {
        "accountName": state["account_name"], "projectName": state["project_name"], "runId": state["run_id"],
        "chatModel": args.chat_model, "chatVersion": args.chat_version,
        "judgeModel": args.judge_model, "judgeVersion": args.judge_version,
        "embeddingModel": args.embedding_model, "embeddingVersion": args.embedding_version,
        "modelSku": args.model_sku,
        **{role + "Capacity": plan["roles"][role]["capacity"] for role in ROLES},
        "preservedDeployments": plan["preserved_deployments"],
    }
    state["initial_model_capacity_plan"] = plan
    state["model_configuration"] = parameters
    state["model_deployments"] = deployment_names
    state["operations"].append({"step": "foundation-capacity-plan", "status": "verified", "roles": plan["roles"]})
    persist(state)
    print(json.dumps({"initial_model_capacities": plan["roles"], "model_calls": 0}, ensure_ascii=False, indent=2))
    deployment = az(
        "deployment", "group", "create", "--subscription", state["subscription"],
        "--resource-group", state["resource_group"], "--name", "contoso-foundation",
        "--template-file", str(ROOT / "infra/main.bicep"), "--parameters",
        *[f"{key}={json.dumps(value) if isinstance(value, dict) else value}" for key, value in parameters.items()],
        timeout=1200,
    )
    if deployment["properties"]["provisioningState"] != "Succeeded":
        raise RuntimeError("Foundation deployment did not complete successfully; no model test was sent.")
    state["foundation"] = deployment["properties"]["outputs"]
    project = az(
        "rest", "--method", "get",
        "--url", state["foundation"]["projectId"]["value"] + "?api-version=2025-06-01",
    )
    endpoints = project["properties"]["endpoints"]
    state["project_endpoint"] = endpoints["AI Foundry API"].rstrip("/")
    persist(state)
    readiness, _ = inspect_deployments(state, requirements(args.learners), ROLES, Management(az))
    require_ready(readiness)
    state["initial_model_capacity_verified"] = {
        "checked_at": datetime.now(timezone.utc).isoformat(), "deployments": readiness,
    }
    state["operations"].append({"step": "foundation", "status": deployment["properties"]["provisioningState"]})
    persist(state)
    status()


def roles() -> None:
    state = owned()
    user = current_user_id(state)
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
    user = current_user_id(state)
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


def reflection(args: argparse.Namespace) -> None:
    from optimizer_lab import REFLECTION_MODELS

    if args.reflection_model not in REFLECTION_MODELS or not args.reflection_version or not 1 <= args.capacity <= 100:
        raise ValueError("Specify a supported reflection model/version and capacity 1..100.")
    state = owned()
    name = "contoso-reflection"
    if state.get("reflection"):
        raise ValueError("A reflection deployment receipt already exists; inspect it instead of recreating.")
    catalog = az("cognitiveservices", "model", "list", "--subscription", state["subscription"], "--location", state["location"])
    if not any(
        item["model"]["name"] == args.reflection_model and item["model"]["version"] == args.reflection_version
        and "GlobalStandard" in {sku["name"] for sku in item["model"].get("skus", [])}
        for item in catalog
    ):
        raise ValueError("The selected reflection model/version does not support GlobalStandard here.")
    quota = az("cognitiveservices", "usage", "list", "--subscription", state["subscription"], "--location", state["location"])
    usage = next((item for item in quota if item["name"]["value"] == f"OpenAI.GlobalStandard.{args.reflection_model}"), None)
    if usage is None or usage["limit"] - usage["currentValue"] < args.capacity:
        raise ValueError("Insufficient verified reflection quota; no deployment was submitted.")
    existing = az("cognitiveservices", "account", "deployment", "list", "--subscription", state["subscription"],
                  "--resource-group", state["resource_group"], "--name", state["account_name"])
    if any(item["name"] == name for item in existing):
        raise ValueError("An unrecorded reflection deployment already exists; it will not be overwritten.")
    account_id = state["resource_group_id"] + "/providers/Microsoft.CognitiveServices/accounts/" + state["account_name"]
    if account_id.lower() != state["foundation"]["accountId"]["value"].lower():
        raise ValueError("The account ID is outside the owned group.")
    resource_id = account_id + "/deployments/" + name
    state["reflection"] = {"id": resource_id, "name": name, "model": args.reflection_model,
                           "version": args.reflection_version, "capacity": args.capacity, "status": "requested"}
    persist(state)
    az("rest", "--method", "put", "--url", resource_id + "?api-version=2025-06-01", "--body", json.dumps({
        "sku": {"name": "GlobalStandard", "capacity": args.capacity},
        "properties": {"model": {"format": "OpenAI", "name": args.reflection_model, "version": args.reflection_version},
                       "versionUpgradeOption": "NoAutoUpgrade"},
    }), timeout=120)
    deadline = time.monotonic() + 300
    for _ in range(15):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        current = az("rest", "--method", "get", "--url", resource_id + "?api-version=2025-06-01",
                     timeout=max(1, min(60, int(remaining))))
        state["reflection"]["status"] = current["properties"]["provisioningState"]
        if state["reflection"]["status"] == "Succeeded":
            state["operations"].append({"step": "reflection", "status": "Succeeded", "deployment": name})
            persist(state)
            print(json.dumps(state["reflection"], indent=2))
            return
        if state["reflection"]["status"] in {"Failed", "Canceled"}:
            persist(state)
            raise RuntimeError("Reflection deployment failed; its original receipt is retained.")
        time.sleep(min(5, max(0, deadline - time.monotonic())))
    persist(state)
    raise RuntimeError("Reflection deployment was not confirmed within the bounded wait; inspect the receipt.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", choices=["create", "foundation", "roles", "search", "monitoring", "status", "throughput", "reflection"])
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--subscription")
    parser.add_argument("--location")
    parser.add_argument("--cost-authorization", help="Record the user's explicit monetary limit or explicit no-limit authorization.")
    for field in ("chat-model", "chat-version", "judge-model", "judge-version", "embedding-model", "embedding-version",
                  "reflection-model", "reflection-version"):
        parser.add_argument("--" + field)
    parser.add_argument("--model-sku", choices=["GlobalStandard", "DataZoneStandard", "Standard"])
    parser.add_argument("--capacity", type=int, help="Legacy throughput/reflection capacity units; not used for foundation.")
    parser.add_argument("--learners", type=int, default=1, help="Simultaneous learners used to size initial model TPM/RPM.")
    parser.add_argument("--max-capacity", type=int, default=100, help="Ceiling for new/increased capacity units per model.")
    parser.add_argument("--resume", action="store_true", help="Explicitly resume only owned partial foundation resources.")
    args = parser.parse_args(argv)
    if args.step == "foundation":
        from model_capacity import requirements
        plan = requirements(args.learners)
        if args.capacity is not None:
            raise ValueError("Foundation derives role capacities from recommended TPM/RPM; use --learners and --max-capacity, not --capacity.")
        if not 1 <= args.max_capacity <= 10000:
            raise ValueError("The capacity ceiling must be 1..10000 units per deployment.")
    elif args.step in {"throughput", "reflection"} and args.capacity is None:
        args.capacity = 10
    if not args.live:
        print(f"PLAN ONLY: {args.step}; no Azure calls or changes.")
        if args.step == "foundation":
            print(json.dumps({
                "recommended": plan["roles"],
                "capacity_resolution": "Resolve SKU unit rates, allowed capacity and quota before deployment.",
                "max_capacity": args.max_capacity, "azure_calls": 0,
            }, ensure_ascii=False, indent=2))
        return
    if args.step == "create":
        if not args.cost_authorization:
            raise ValueError("Record explicit --cost-authorization before creating the environment.")
        create(args)
    elif args.step == "foundation":
        foundation(args)
    elif args.step == "reflection":
        reflection(args)
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
