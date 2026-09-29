"""Correlate real response/trace IDs with Application Insights; missing rows stay missing."""

import argparse
import json
from pathlib import Path
import re

from cloud import Rest, credential
from evidence import Budget, Evidence
from workshop import load_jsonl


def query_for(rows: list[dict], agent: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9-]+", agent):
        raise ValueError("Invalid agent name.")
    responses = [row["response_id"] for row in rows if row.get("response_id")]
    traces = [row["trace_id"] for row in rows if row.get("trace_id")]
    if not responses and not traces:
        raise ValueError("Input contains no real response or trace IDs.")
    return f"""
let responseIds = dynamic({json.dumps(responses)});
let traceIds = dynamic({json.dumps(traces)});
let agentRequests = materialize(
    requests
    | where timestamp > ago(24h)
    | extend agent = coalesce(tostring(customDimensions["gen_ai.agent.name"]), tostring(customDimensions["azure.ai.agentserver.agent_name"]))
    | where agent == "{agent}" or operation_Id in (traceIds)
    | project operation_Id
);
union dependencies, requests, traces
| where timestamp > ago(24h)
| extend responseId = tostring(customDimensions["gen_ai.response.id"]),
         agentVersion = tostring(customDimensions["gen_ai.agent.id"])
| where responseId in (responseIds) or operation_Id in (traceIds)
| where operation_Id in (agentRequests) or responseId in (responseIds)
| project timestamp, operation_Id, id, operation_ParentId, responseId, agentVersion, name, success, duration
| take 200
""".strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--app-id", required=True)
    parser.add_argument("--agent", default="contoso-purchasing")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    query = query_for(load_jsonl(args.input), args.agent)
    print(query)
    if not args.live:
        print("PLAN ONLY: no log query.")
        return
    if not re.fullmatch(r"[0-9a-fA-F-]{36}", args.app_id):
        raise ValueError("Expected the Application Insights app ID, not an instrumentation key.")
    evidence = Evidence("trace")
    with credential() as cred:
        rest = Rest("https://api.applicationinsights.io", cred, "https://api.applicationinsights.io/.default",
                    evidence, Budget(max_requests=1))
        result = rest.request("POST", f"/v1/apps/{args.app_id}/query", {"query": query, "timespan": "P1D"})
    count = sum(len(table["rows"]) for table in result.get("tables", []))
    evidence.append("correlation", {"rows": count, "input": args.input.name})
    if count == 0:
        raise RuntimeError("No correlated telemetry. Ingestion delay/permissions/configuration must be investigated.")
    print(f"Correlated {count} telemetry rows. Evidence: {evidence.path}")


if __name__ == "__main__":
    main()
