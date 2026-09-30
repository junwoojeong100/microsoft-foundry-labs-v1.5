"""Deterministic checks over real execution evidence, separate from semantic judging."""

import json

from grounding import parse_answer
from search_lab import validate_hits
from workshop import ToolInputError, dispatch_tool, function_schemas


def check_business_evidence(row: dict, case: dict, *, require_tool_definitions: bool = False) -> dict:
    failures = []
    sources = row.get("retrieved_sources")
    citations = row.get("citations")
    calls = row.get("tool_calls")
    if row.get("status") != "completed" or not row.get("response_id") or not row.get("response", "").strip():
        failures.append("completed_real_response")
    if row.get("grounding_contract") != "required-search-and-citations-v2":
        failures.append("grounding_contract")
    if require_tool_definitions and row.get("tool_definitions") != function_schemas():
        failures.append("runtime_tool_definition_evidence")
    if not isinstance(sources, list) or not sources or any(not isinstance(s, dict) for s in sources):
        failures.append("actual_retrieval")
        sources = []
    if not isinstance(citations, list) or not citations or any(not isinstance(c, dict) for c in citations):
        failures.append("nonempty_citations")
        citations = []
    if not isinstance(calls, list) or any(not isinstance(c, dict) for c in calls):
        failures.append("actual_tool_records")
        calls = []
    try:
        validate_hits(sources)
        rendered, selected = parse_answer(row.get("raw_answer", ""), {s["id"]: s for s in sources})
        if rendered != row.get("response") or [s["id"] for s in selected] != [s.get("id") for s in citations]:
            failures.append("unchanged_model_selected_citations")
    except (ValueError, RuntimeError, KeyError, TypeError):
        failures.append("citation_provenance")
    selected_ids = {c.get("id") for c in citations}
    if not set(case.get("required_citations", [])) <= selected_ids:
        failures.append("required_policy_evidence")
    retrievals = [c for c in calls if c.get("name") == "search_policies" and c.get("execution") == "server_required"]
    if len(retrievals) != 1 or not retrievals[0].get("output", {}).get("ok"):
        failures.append("required_server_search")
    else:
        returned = retrievals[0]["output"].get("result")
        try:
            query_arguments = json.loads(retrievals[0].get("arguments", ""))
        except (json.JSONDecodeError, TypeError):
            query_arguments = None
        if returned != sources or query_arguments != {"query": row.get("query")}:
            failures.append("server_search_result_link")
    names = {call.get("name") for call in calls}
    if not set(case.get("required_tools", [])) <= names:
        failures.append("required_tool_execution")
    if set(case.get("forbidden_tools", [])) & names:
        failures.append("unrequested_tool_execution")
    expected_arguments = case.get("expected_tool_arguments", {})
    for call in calls:
        if call.get("name") == "search_policies":
            continue
        if call.get("name") not in {"get_stock", "prepare_purchase_request"} or not call.get("call_id"):
            failures.append("tool_allowlist_and_call_id")
            continue
        try:
            arguments = json.loads(call["arguments"])
            if call["name"] in expected_arguments and arguments != expected_arguments[call["name"]]:
                failures.append("tool_arguments")
            expected = dispatch_tool(call["name"], call["arguments"])
        except ToolInputError:
            output = call.get("output", {})
            if output.get("ok") is not False or output.get("error", {}).get("code") != "invalid_tool_request":
                failures.append("tool_rejection_preserved")
        except (json.JSONDecodeError, KeyError, TypeError):
            failures.append("tool_argument_shape")
        else:
            if call.get("output") != {"ok": True, "result": expected}:
                failures.append("authentic_business_tool_output")
    if row.get("execution_location") == "azure" and not row.get("trace_id"):
        failures.append("remote_trace_id")
    return {"type": "deterministic_business_evidence", "passed": not failures, "failures": sorted(set(failures))}
