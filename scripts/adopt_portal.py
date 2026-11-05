"""Verify an existing portal-created scope with read-only Azure calls; never provision or grant access."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from azure_environment import LEDGER
from lab_cli import run
from model_capacity import Management, validate_scope
from workshop import LANGUAGE, read_config

API_VERSION = "2025-06-01"


def verified_scope(subscription, resource_group, run_id, endpoint, deployment, *,
                   search_service=None, embedding_deployment=None, management=None):
    subscription = str(UUID(subscription))
    for name in (resource_group, run_id, deployment):
        if not re.fullmatch(r"[A-Za-z0-9_.-]{1,90}", name):
            raise ValueError("Use exact resource names and the existing validationRun tag.")
    if not resource_group.startswith("rg-contoso-"):
        raise ValueError("Only a dedicated rg-contoso-* workshop group can be adopted.")
    project = re.fullmatch(
        r"https://([a-z0-9][a-z0-9-]{1,63})\.services\.ai\.azure\.com/api/projects/([A-Za-z0-9_.-]{1,90})",
        endpoint,
    )
    if not project:
        raise ValueError("Use the existing Microsoft Foundry project endpoint from L01.")
    if bool(search_service) != bool(embedding_deployment):
        raise ValueError("Hosted adoption needs both --search-service and --embedding-deployment.")
    for name in (search_service, embedding_deployment):
        if name and not re.fullmatch(r"[A-Za-z0-9-]{1,64}", name):
            raise ValueError("Invalid Search service or embedding deployment name.")
    management = management or Management()
    account_name, project_name = project.groups()
    group_id = f"/subscriptions/{subscription}/resourceGroups/{resource_group}"
    account_id = group_id + f"/providers/Microsoft.CognitiveServices/accounts/{account_name}"
    project_id = account_id + f"/projects/{project_name}"
    account = management.call("account", "show", "--subscription", subscription)
    tenant = str(UUID(account["tenantId"]))
    if account["id"].lower() != subscription:
        raise ValueError("The signed-in subscription differs from the requested scope.")
    group = management.call("group", "show", "--subscription", subscription, "--name", resource_group)
    if (
        group["id"].lower() != group_id.lower()
        or group.get("tags", {}).get("validationRun") != run_id
        or group.get("tags", {}).get("repository") != "microsoft-foundry-labs-v1.5"
    ):
        raise ValueError("Resource group identity/ownership tags mismatch; no ownership receipt was written.")

    def resource(identifier):
        value = management.call(
            "rest", "--method", "get", "--url", identifier + f"?api-version={API_VERSION}",
            "--subscription", subscription,
        )
        if value.get("id", "").lower() != identifier.lower():
            raise ValueError("Azure returned a resource outside the exact requested scope.")
        if value.get("properties", {}).get("provisioningState") != "Succeeded":
            raise ValueError("The existing resource is not Succeeded; do not adopt an incomplete deployment.")
        return value

    foundry = resource(account_id)
    if foundry.get("kind") != "AIServices":
        raise ValueError("The selected account is not a Microsoft Foundry AIServices resource.")
    current_project = resource(project_id)
    actual_endpoint = current_project["properties"].get("endpoints", {}).get("AI Foundry API", "").rstrip("/")
    if actual_endpoint != endpoint:
        raise ValueError("The actual project endpoint differs from .env.")
    chat = resource(account_id + f"/deployments/{deployment}")
    models = {"chat": chat["properties"].get("model")}
    state = {
        "schema": "contoso-environment-v1", "repository_id": 1396573688,
        "repository": "junwoojeong100/microsoft-foundry-labs-v1.5", "language": LANGUAGE,
        "subscription": subscription, "tenant": tenant, "resource_group": resource_group,
        "resource_group_id": group_id, "location": foundry["location"],
        "run_id": run_id, "account_name": account_name, "project_name": project_name,
        "project_endpoint": endpoint, "model_deployments": {"chat": deployment},
        "model_configuration": {},
        "foundation": {"accountId": {"value": account_id}, "projectId": {"value": project_id}},
        "ownership_source": "portal_read_only_verification",
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "role_assignments": [],
    }
    if search_service:
        search_id = group_id + f"/providers/Microsoft.Search/searchServices/{search_service}"
        search = management.call(
            "rest", "--method", "get", "--url", search_id + "?api-version=2025-05-01",
            "--subscription", subscription,
        )
        if (
            search.get("id", "").lower() != search_id.lower()
            or search.get("properties", {}).get("provisioningState") != "succeeded"
        ):
            raise ValueError("The existing Search service is outside scope or not succeeded.")
        embedding = resource(account_id + f"/deployments/{embedding_deployment}")
        state["model_deployments"]["embedding"] = embedding_deployment
        models["embedding"] = embedding["properties"].get("model")
        state.update(search_name=search_service, search_id=search_id,
                     search_endpoint=f"https://{search_service}.search.windows.net")
    for role, model in models.items():
        if not isinstance(model, dict) or any(
            not isinstance(model.get(field), str) or not model[field] for field in ("name", "version")
        ):
            raise ValueError(f"{role}: the actual deployment must report its model name and version.")
        state["model_configuration"].update({
            role + "Model": model["name"], role + "Version": model["version"],
        })
    state["operations"] = [{
        "step": "adopt-portal", "status": "verified", "resource_changes": 0,
        "management_reads": management.calls,
    }]
    return validate_scope(state, roles=tuple(models))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subscription", required=True)
    parser.add_argument("--resource-group", required=True)
    parser.add_argument("--run-id", required=True, help="Exact existing validationRun tag from L01.")
    parser.add_argument("--search-service", help="Existing, approved Search service in the same group.")
    parser.add_argument("--embedding-deployment", help="Existing embedding deployment in the same Foundry account.")
    parser.add_argument("--live", action="store_true", help="Allow 5 or 7 scoped reads, no resource changes.")
    args = parser.parse_args(argv)
    if not args.live:
        print("PLAN ONLY: verify an existing portal scope with 5 or 7 reads; no Azure calls or local writes.")
        return 0
    if LEDGER.exists() or LEDGER.is_symlink() or LEDGER.parent.is_symlink():
        raise ValueError("An ownership receipt already exists or its directory is a link. Reuse it; never overwrite it.")
    endpoint, deployment = read_config()
    state = verified_scope(
        args.subscription, args.resource_group, args.run_id, endpoint, deployment,
        search_service=args.search_service, embedding_deployment=args.embedding_deployment,
    )
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(LEDGER, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(f"Verified existing portal scope: {LEDGER.relative_to(ROOT)}. Resource changes: 0. No model invocation.")
    return 0


if __name__ == "__main__":
    run(main)
