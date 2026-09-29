"""One bounded purchasing turn, shared by local and hosted Invocations."""

from __future__ import annotations

import json
import re
import time
from typing import Any

from cloud import project_client
from evidence import Budget, Evidence, digest, runtime_contract
from search_lab import Search
from workshop import DATA, ToolInputError, dispatch_tool, ensure_response, function_schemas

MAX_OUTPUT_TOKENS = 2048
MAX_ROUNDS = 5
MAX_CALLS = 8


def validate_request(value: Any) -> dict[str, str]:
    if not isinstance(value, dict) or not set(value) <= {"query", "case_id", "run_id"} or "query" not in value:
        raise ValueError("Expected query and optional case_id/run_id only.")
    if not isinstance(value["query"], str) or not value["query"].strip() or len(value["query"]) > 4000:
        raise ValueError("query must contain 1..4000 characters.")
    for key in ("case_id", "run_id"):
        if key in value and (not isinstance(value[key], str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", value[key])):
            raise ValueError(f"Invalid {key}.")
    return value


def tool_schemas() -> list[dict[str, Any]]:
    return [{"type": "function", **item} for item in function_schemas()] + [{
        "type": "function", "name": "search_policies",
        "description": "Retrieve authoritative synthetic Contoso policies with source IDs. Use before answering policy questions.",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}},
                       "required": ["query"], "additionalProperties": False},
        "strict": True,
    }]


def current_trace_id() -> str | None:
    try:
        from opentelemetry import trace
    except ImportError:
        return None
    context = trace.get_current_span().get_span_context()
    return format(context.trace_id, "032x") if context.is_valid else None


def cited_sources(text: str, sources: dict[str, dict]) -> list[dict]:
    cited_ids = set(re.findall(r"CONTOSO-(?:PROC|EXP|SEC)-\d{4}-\d{2}-s\d+", text))
    if not cited_ids <= sources.keys():
        raise RuntimeError("Answer cited a source that was never retrieved.")
    citations = {key: {**sources[key], "citation_kind": "explicit_section_id", "citation_text": key} for key in cited_ids}
    for match in re.finditer(r"\[([A-Za-z0-9_-]+\.md)(?:,\s*|\s+)(\d+(?:\s*,\s*\d+)*)\s*(?:절)?\]", text):
        for section in re.findall(r"\d+", match[2]):
            found = [s for s in sources.values() if s["filename"] == match[1] and s["section"] == section]
            if len(found) != 1:
                raise RuntimeError("Text citation does not identify one actually retrieved section.")
            source = found[0]
            citations[source["id"]] = {**source, "citation_kind": "text_reference", "citation_text": match[0]}
    return [citations[key] for key in sorted(citations)]


def execute_turn(
    client, search, model: str, payload: dict[str, str], evidence: Evidence, budget: Budget,
    *, instructions: str | None = None,
) -> dict[str, Any]:
    payload = validate_request(payload)
    inputs: list[Any] = [{"role": "user", "content": payload["query"]}]
    prompt = instructions if instructions is not None else (DATA / "prompts/agent-v4.txt").read_text(encoding="utf-8")
    prompt += (
        "\nHosted 검색 도구는 search_policies다. 정책 답변의 인용은 실제 반환된 절 ID를 "
        "[CONTOSO-PROC-2026-09-s2]처럼 적는다. 반환되지 않은 ID는 만들지 않는다."
    )
    tool_calls, response_ids, sources = [], [], {}
    input_tokens = output_tokens = 0
    started = time.monotonic()
    for _ in range(MAX_ROUNDS):
        budget.before_request(token_reservation=len(json.dumps(inputs, ensure_ascii=False)) + MAX_OUTPUT_TOKENS)
        response = client.responses.create(
            model=model, instructions=prompt, input=inputs, tools=tool_schemas(),
            max_output_tokens=MAX_OUTPUT_TOKENS, store=False,
        )
        evidence.append("model_response", response)
        response_ids.append(response.id)
        if response.usage:
            input_tokens += response.usage.input_tokens
            output_tokens += response.usage.output_tokens
            budget.record_tokens(response.usage.input_tokens + response.usage.output_tokens)
        if response.status != "completed":
            ensure_response(response)
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            text = ensure_response(response)
            citations = cited_sources(text, sources)
            result = {
                "status": "completed", **payload, "response": text,
                "model_deployment": model, "model": response.model,
                "response_id": response.id, "response_ids": response_ids,
                "request_id": getattr(response, "_request_id", None),
                "trace_id": current_trace_id(), "contract": runtime_contract(),
                "effective_prompt_sha256": digest(prompt),
                "tool_calls": tool_calls, "retrieved_sources": list(sources.values()),
                "citations": citations,
                "input_tokens": input_tokens, "output_tokens": output_tokens,
                "latency_seconds": round(time.monotonic() - started, 3),
                "manual_pass": None, "review_note": "",
            }
            evidence.append("completed", result)
            return result
        if len(tool_calls) + len(calls) > MAX_CALLS:
            raise RuntimeError("Hosted tool-call budget exceeded before executing extra calls.")
        # Preserve the complete model output, including reasoning and call IDs.
        inputs.extend(item.model_dump(exclude_none=True) for item in response.output)
        for call in calls:
            try:
                if call.name == "search_policies":
                    arguments = json.loads(call.arguments)
                    if not isinstance(arguments, dict) or set(arguments) != {"query"} or not isinstance(arguments["query"], str):
                        raise ToolInputError("search_policies requires one string query.")
                    hits = search.retrieve(arguments["query"])
                    hits = list({item["id"]: item for item in [*hits, *search.policy_scope()]}.values())
                    for item in hits:
                        sources[item["id"]] = item
                    value = {"ok": True, "result": hits}
                else:
                    value = {"ok": True, "result": dispatch_tool(call.name, call.arguments)}
            except (ToolInputError, json.JSONDecodeError) as exc:
                value = {"ok": False, "error": {"code": "invalid_tool_request", "message": str(exc)}}
                evidence.append("tool_rejected", value)
            entry = {"call_id": call.call_id, "name": call.name, "arguments": call.arguments, "output": value}
            tool_calls.append(entry)
            evidence.append("tool_result", entry)
            inputs.append({"type": "function_call_output", "call_id": call.call_id, "output": json.dumps(value, ensure_ascii=False)})
    raise RuntimeError("Hosted turn limit exceeded; no success-shaped fallback.")


def invoke(payload: dict[str, str]) -> dict[str, Any]:
    from azure.ai.agentserver.optimization import load_config

    payload = validate_request(payload)
    evidence = Evidence("hosted-turn")
    budget = Budget(max_requests=12, max_tokens=60_000, max_seconds=300)
    config = load_config()
    if not config.model or config.model == "CONFIGURE-MODEL-BEFORE-DEPLOY":
        raise ValueError("Build with a configured model deployment before local/Azure invocation.")
    with project_client(evidence) as (project, cred, _, model), project.get_openai_client(max_retries=0, timeout=60) as client:
        try:
            return execute_turn(
                client, Search(cred, client, evidence, budget), config.model, payload, evidence, budget,
                instructions=config.compose_instructions(),
            )
        except (ValueError, RuntimeError, OSError) as exc:
            evidence.failure(exc)
            raise
