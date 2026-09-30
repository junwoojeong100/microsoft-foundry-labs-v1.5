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


def correlation_report(rows: list[dict], result: dict) -> dict:
    trace_ids, response_ids = set(), set()
    for table in result.get("tables", []):
        columns = [column["name"] for column in table["columns"]]
        for values in table["rows"]:
            record = dict(zip(columns, values, strict=True))
            if record.get("operation_Id"):
                trace_ids.add(record["operation_Id"])
            if record.get("responseId"):
                response_ids.add(record["responseId"])
    missing = [row["id"] for row in rows if (
        row.get("trace_id") not in trace_ids if row.get("trace_id") else row.get("response_id") not in response_ids
    )]
    report = {
        "input_rows": len(rows), "correlated_rows": len(rows) - len(missing), "missing_case_ids": missing,
        "model_response_spans_observed": sum(row.get("response_id") in response_ids for row in rows),
        "request_trace_ids_observed": sum(row.get("trace_id") in trace_ids for row in rows),
    }
    if missing:
        raise RuntimeError(f"Partial trace correlation: {report}. Missing telemetry is not a pass.")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--app-id", required=True)
    parser.add_argument("--agent", default="contoso-purchasing")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    rows = load_jsonl(args.input)
    query = query_for(rows, args.agent)
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
    report = correlation_report(rows, result)
    evidence.append("correlation", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Evidence: {evidence.path}")


if __name__ == "__main__":
    main()
