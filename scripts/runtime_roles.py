"""Assign only an owned Contoso agent's minimum runtime roles in the new RG."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from cloud import project_client
from evidence import Evidence
from azure_environment import az, owned, persist


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", required=True)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if not args.live:
        print("PLAN ONLY: project-scoped agent access and owned Search/model inference only.")
        return
    state = owned()
    allowed = {"contoso-purchasing", "contoso-purchasing-responses"}
    a2a_path = ROOT / "results/a2a.json"
    if a2a_path.exists():
        a2a = json.loads(a2a_path.read_text())
        if a2a["endpoint"] != state["project_endpoint"]:
            raise ValueError("A2A receipt project mismatch.")
        allowed.update({a2a["caller"], a2a["worker"]})
    if args.agent not in allowed:
        raise ValueError("Agent is outside the local owned receipts.")
    evidence = Evidence("runtime-rbac")
    with project_client(evidence) as (project, _, endpoint, _):
        if endpoint != state["project_endpoint"]:
            raise ValueError("Configured project is outside the owned RG.")
        agent = project.agents.get(args.agent)
        principal = agent.instance_identity.principal_id
    grants = [("eed3b665-ab3a-47b6-8f48-c9382fb1dad6", state["foundation"]["projectId"]["value"])]
    if args.agent in {"contoso-purchasing", "contoso-purchasing-responses"}:
        grants = [
            ("53ca6127-db72-4b80-b1b0-d745d6d5456d", state["foundation"]["projectId"]["value"]),
            ("Search Index Data Reader", state["search_id"]),
            ("Cognitive Services OpenAI User", state["foundation"]["accountId"]["value"]),
        ]
    for role, scope in grants:
        result = az("role", "assignment", "create", "--subscription", state["subscription"],
                    "--assignee-object-id", principal, "--assignee-principal-type", "ServicePrincipal",
                    "--role", role, "--scope", scope)
        entry = {"id": result["id"], "role": role, "scope": scope, "agent": args.agent}
        state.setdefault("role_assignments", []).append(entry)
        evidence.append("role_assigned", entry)
        persist(state)
    print(f"Assigned {len(grants)} scoped runtime roles; no subscription-wide role.")


if __name__ == "__main__":
    main()
