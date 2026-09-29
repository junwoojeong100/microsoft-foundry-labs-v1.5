"""Explicit administrator opt-in: new RG identity, one GitHub Environment, no client secrets."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from evidence import Evidence
from search_lab import configuration
from workshop import config_values, save_json
from azure_environment import az, owned, persist

REPO = "junwoojeong100/foundry-labs-v1.5"
ENVIRONMENT = "contoso-validation"


def gh(*args: str, body: dict | None = None):
    result = subprocess.run(
        ["gh", *args], cwd=ROOT, text=True, capture_output=True, check=False, timeout=90,
        input=json.dumps(body) if body is not None else None,
    )
    if result.returncode:
        raise RuntimeError(f"GitHub operation failed: {result.stderr.strip()}")
    return json.loads(result.stdout) if result.stdout.strip() else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if not args.live:
        print("PLAN ONLY: new user-assigned identity + environment-bound federation + approved branch policy.")
        return
    if args.branch in {"main", "master"} or not args.branch.startswith("feat/"):
        raise ValueError("Setup is restricted to an explicit feature branch, never main.")
    repository = gh("repo", "view", REPO, "--json", "isPrivate")
    if not repository["isPrivate"]:
        raise ValueError("Repository A must remain private.")
    state = owned()
    if state.get("oidc"):
        raise ValueError("OIDC is already recorded; inspect existing identity/environment, do not overwrite.")
    environments = gh("api", f"repos/{REPO}/environments")
    if any(item["name"] == ENVIRONMENT for item in environments["environments"]):
        raise ValueError("Test environment already exists without this ownership receipt; setup refused.")
    evidence = Evidence("oidc-setup")
    name = "id-" + state["run_id"]
    existing = az("identity", "list", "--subscription", state["subscription"], "--resource-group", state["resource_group"])
    if any(item["name"] == name for item in existing):
        raise ValueError("Identity name collision; never overwrite existing access.")
    identity = az("identity", "create", "--subscription", state["subscription"],
                  "--resource-group", state["resource_group"], "--name", name, "--location", state["location"],
                  "--tags", f"validationRun={state['run_id']}", "repository=foundry-labs-v1.5")
    state["oidc"] = {
        "identity_id": identity["id"], "client_id": identity["clientId"], "principal_id": identity["principalId"],
        "environment": ENVIRONMENT, "branch": args.branch, "resources_created": ["identity"],
    }
    persist(state)
    subject = f"repo:{REPO}:environment:{ENVIRONMENT}"
    federation = az(
        "identity", "federated-credential", "create", "--subscription", state["subscription"],
        "--resource-group", state["resource_group"], "--identity-name", name, "--name", "github-contoso-validation",
        "--issuer", "https://token.actions.githubusercontent.com", "--subject", subject,
        "--audiences", "api://AzureADTokenExchange",
    )
    state["oidc"].update(federation_id=federation["id"], subject=subject)
    persist(state)
    for role, scope in [
        ("Reader", state["resource_group_id"]),
        ("53ca6127-db72-4b80-b1b0-d745d6d5456d", state["foundation"]["projectId"]["value"]),
        ("Cognitive Services OpenAI User", state["foundation"]["accountId"]["value"]),
    ]:
        grant = az("role", "assignment", "create", "--subscription", state["subscription"],
                   "--assignee-object-id", identity["principalId"], "--assignee-principal-type", "ServicePrincipal",
                   "--role", role, "--scope", scope)
        state.setdefault("role_assignments", []).append({"id": grant["id"], "role": role, "scope": scope, "purpose": "oidc"})
        persist(state)
    environment = gh("api", "--method", "PUT", f"repos/{REPO}/environments/{ENVIRONMENT}", "--input", "-", body={
        "deployment_branch_policy": {"protected_branches": False, "custom_branch_policies": True},
    })
    evidence.append("environment_created", {"id": environment["id"], "name": environment["name"]})
    branch_policy = gh("api", "--method", "POST", f"repos/{REPO}/environments/{ENVIRONMENT}/deployment-branch-policies",
                       "--input", "-", body={"name": args.branch, "type": "branch"})
    evidence.append("branch_policy", branch_policy)
    search, config = configuration(), config_values()
    variables = {
        "AZURE_CLIENT_ID": identity["clientId"], "AZURE_TENANT_ID": state["tenant"],
        "AZURE_SUBSCRIPTION_ID": state["subscription"], "AZURE_RESOURCE_GROUP": state["resource_group"],
        "AZURE_AI_PROJECT_ID": state["foundation"]["projectId"]["value"],
        "AZURE_AI_PROJECT_ENDPOINT": state["project_endpoint"],
        "FOUNDRY_MODEL_DEPLOYMENT_NAME": config["FOUNDRY_MODEL_DEPLOYMENT_NAME"],
        "FOUNDRY_SEARCH_ENDPOINT": search["endpoint"], "FOUNDRY_SEARCH_INDEX": search["index"],
        "FOUNDRY_KNOWLEDGE_BASE": search["knowledge_base"],
        "FOUNDRY_EMBEDDING_DEPLOYMENT_NAME": config["FOUNDRY_EMBEDDING_DEPLOYMENT_NAME"],
        "FOUNDRY_EMBEDDING_ENDPOINT": config["FOUNDRY_EMBEDDING_ENDPOINT"],
        "FOUNDRY_JUDGE_DEPLOYMENT_NAME": config["FOUNDRY_JUDGE_DEPLOYMENT_NAME"],
    }
    for key, value in variables.items():
        if not value:
            raise ValueError(f"Missing nonsecret CI configuration: {key}")
        gh("variable", "set", key, "--repo", REPO, "--env", ENVIRONMENT, "--body", value)
    state["oidc"]["resources_created"].append("github_environment_and_variables")
    persist(state)
    evidence.append("configured", {"subject": subject, "branch": args.branch, "variables": list(variables), "client_secret_created": False})
    print(f"Configured OIDC for {REPO}/{ENVIRONMENT}; only branch {args.branch}. Repository remains private.")


if __name__ == "__main__":
    main()
