"""Deterministic checks over real execution evidence, separate from semantic judging."""

import json

from grounding import attribute_answer, parse_answer
from search_lab import validate_hits
from workshop import ToolInputError, dispatch_tool, function_schemas
from request_contract import (
    TOOL_AUTHORIZATION_CONTRACTS,
    required_policy_citations, tool_permissions, validate_business_tool_request, validate_draft_request,
)


def check_business_evidence(
    row: dict, case: dict, *, require_tool_definitions: bool = False, require_tool_authorization: bool = False,
    expected_authorization_contract: str | None = None,
) -> dict:
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
        source_map = {s["id"]: s for s in sources}
        rendered, selected = (
            attribute_answer(row.get("raw_answer", ""), row["raw_attribution"], source_map)
            if row.get("raw_attribution") is not None else parse_answer(row.get("raw_answer", ""), source_map)
        )
        if rendered != row.get("response") or [s["id"] for s in selected] != [s.get("id") for s in citations]:
            failures.append("unchanged_model_selected_citations")
    except (ValueError, RuntimeError, KeyError, TypeError):
        failures.append("citation_provenance")
    selected_ids = {c.get("id") for c in citations}
    authorization_contract = row.get("tool_authorization_contract")
    authorized = isinstance(authorization_contract, str) and authorization_contract in TOOL_AUTHORIZATION_CONTRACTS
    if authorization_contract is not None and not authorized:
        failures.append("tool_authorization_contract")
    if require_tool_authorization and not authorized:
        failures.append("tool_authorization_contract")
    if expected_authorization_contract is not None and authorization_contract != expected_authorization_contract:
        failures.append("tool_authorization_contract")
    if authorized:
        if row.get("request_permissions") != tool_permissions(row["query"], contract=authorization_contract):
            failures.append("request_permissions")
        required = required_policy_citations(row["query"], contract=authorization_contract)
        if row.get("required_policy_citations") != required or not set(required) <= selected_ids:
            failures.append("required_policy_evidence")
    if not set(case.get("required_citations", [])) <= selected_ids:
        failures.append("required_policy_evidence")
    for alternatives in case.get("required_citation_groups", []):
        if not isinstance(alternatives, list) or not alternatives or not set(alternatives) & selected_ids:
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
    names = {call.get("name") for call in calls if call.get("execution") != "rejected_before_execution"}
    if not set(case.get("required_tools", [])) <= names:
        failures.append("required_tool_execution")
    if set(case.get("forbidden_tools", [])) & names:
        failures.append("unrequested_tool_execution")
    expected_arguments = case.get("expected_tool_arguments", {})
    completed_drafts = {}
    for call in calls:
        if call.get("name") == "search_policies":
            continue
        if (call.get("name") not in {"get_stock", "prepare_purchase_request"}
                or not isinstance(call.get("call_id"), str) or not call["call_id"]):
            failures.append("tool_allowlist_and_call_id")
            continue
        if call.get("duplicate_of") is not None:
            original = completed_drafts.get(call["duplicate_of"]) if isinstance(call["duplicate_of"], str) else None
            output = call.get("output", {})
            try:
                same_arguments = original is not None and json.loads(call["arguments"]) == json.loads(original["arguments"])
            except (KeyError, TypeError, json.JSONDecodeError):
                same_arguments = False
            if (
                call["name"] != "prepare_purchase_request"
                or call.get("execution") != "rejected_before_execution"
                or call["call_id"] == call["duplicate_of"] or not same_arguments
                or not isinstance(output, dict) or set(output) != {"ok", "error"} or output.get("ok") is not False
                or not isinstance(output.get("error"), dict)
                or output.get("error", {}).get("code") != "duplicate_tool_request"
            ):
                failures.append("duplicate_tool_provenance")
            continue
        try:
            arguments = json.loads(call["arguments"])
            if authorized:
                validate_business_tool_request(row["query"], call["name"], arguments, contract=authorization_contract)
            elif call["name"] == "prepare_purchase_request":
                validate_draft_request(row["query"], arguments)
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
            elif call["name"] == "prepare_purchase_request" and call.get("execution") != "rejected_before_execution":
                completed_drafts[call["call_id"]] = call
    if row.get("execution_location") == "azure" and not row.get("trace_id"):
        failures.append("remote_trace_id")
    return {"type": "deterministic_business_evidence", "passed": not failures, "failures": sorted(set(failures))}
