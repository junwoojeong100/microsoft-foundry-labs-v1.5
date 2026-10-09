"""Run bounded Agent Framework orchestrations; plan-only without --live."""

from __future__ import annotations

import argparse
import asyncio
from collections.abc import Mapping, Sequence
import json
from pathlib import Path
import sys
import time
from typing import Protocol

from evidence import Budget, Evidence, digest
from model_capacity import INPUT_BUDGET, MIN_START_INTERVAL, STARTS_PER_MINUTE, check_ready, estimate_tokens
from lab_cli import run as run_cli
from workshop import DATA, LANGUAGE, RESULTS, read_config

MAX_SECONDS = 180
MAX_OUTPUT_TOKENS = 2048
CALLS = {"single": 1, "sequential": 2, "compare": 3, "concurrent": 3, "group-chat": 3, "handoff": 4}
ORCHESTRATIONS = ("sequential", "concurrent", "group-chat", "handoff")
QUESTIONS = {
    "ko": {
        "purchase": "단가 145만 원인 노트북 2대를 구매하려 한다. 정책과 승인 절차를 안내해줘.",
        "boundary": "합성 구매 총액이 정확히 200만 원일 때와 200만 1원일 때 필요한 승인을 각각 설명해줘. 실제 주문은 하지 마.",
    },
    "en": {
        "purchase": "I need two laptops at KRW 1,450,000 each. Explain the purchasing policy and approval process.",
        "boundary": "Explain the required approvals for synthetic purchase totals of exactly KRW 2,000,000 and KRW 2,000,001. Do not place an order.",
    },
}


class ResponseLike(Protocol):
    text: str
    response_id: str | None
    finish_reason: str | None
    usage_details: Mapping[str, int | None] | None


class CallAudit:
    def __init__(self, evidence: Evidence, max_calls: int, *, interval: float = MIN_START_INTERVAL):
        self.evidence = evidence
        self.budget = Budget(max_requests=max_calls, max_tokens=max_calls * (INPUT_BUDGET + MAX_OUTPUT_TOKENS),
                             max_seconds=MAX_SECONDS)
        self.records: list[dict] = []
        self.starts: list[float] = []
        self.lock = asyncio.Lock()
        self.interval = interval

    def middleware(self, role: str):
        from agent_framework import ChatMiddleware, ChatResponse

        audit = self

        class RecordCall(ChatMiddleware):
            async def process(self, context, call_next):
                if context.stream:
                    raise ValueError("This bounded exercise records complete non-streaming responses.")
                options = context.options or {}
                maximum = options.get("max_tokens")
                if type(maximum) is not int or not 1 <= maximum <= MAX_OUTPUT_TOKENS:
                    raise ValueError("The orchestration output-token bound is missing or exceeded.")
                request = {
                    "messages": [message.to_dict() for message in context.messages],
                    "instructions": options.get("instructions", ""),
                }
                payload = json.dumps(request, ensure_ascii=False)
                estimate = estimate_tokens(payload) + 256 * len(options.get("tools") or [])
                if estimate > INPUT_BUDGET:
                    raise ValueError("Conversation exceeds the planned input budget; reduce context before a new run.")
                async with audit.lock:
                    now = time.monotonic()
                    recent = [value for value in audit.starts if now - value < 60]
                    wait = max(0.0, audit.starts[-1] + audit.interval - now) if audit.starts else 0.0
                    if len(recent) >= STARTS_PER_MINUTE:
                        wait = max(wait, recent[0] + 60 - now)
                    if wait:
                        await asyncio.sleep(wait)
                    audit.budget.before_request(estimate + maximum)
                    started = time.monotonic()
                    audit.starts.append(started)
                await call_next()
                if not isinstance(context.result, ChatResponse):
                    raise RuntimeError("The model returned no complete chat response.")
                record = response_record(context.result, role, allow_handoff=role == "coordinator")
                if any(item["response_id"] == record["response_id"] for item in audit.records):
                    raise RuntimeError("Duplicate response ID; do not count a replay as a new model call.")
                record.update({
                    "started_after_seconds": round(started - audit.budget.started, 6),
                    "elapsed_seconds": round(time.monotonic() - started, 6),
                    "estimated_input_tokens": estimate,
                    "input_sha256": digest(request),
                    "input_authors": [message.author_name for message in context.messages],
                })
                if record["usage_complete"]:
                    audit.budget.record_tokens(record["total_tokens"])
                audit.records.append(record)
                audit.evidence.append("model_call_completed", {**record, "input": request})

        return RecordCall()


def build_role(client, name: str, instruction: str, policy: str, audit: CallAudit | None = None):
    from agent_framework import Agent

    language = "English" if LANGUAGE == "en" else "Korean"
    instruction_role = "drafter" if name == "single" else name
    return Agent(
        client=client, name=name, description=instruction,
        instructions=f"Role: {instruction_role}. Answer concisely in {language}. {instruction}\n"
        "Use only the synthetic policy below and the conversation. No stock lookup, real approval, "
        "order, payment, or external side effect is available. Do not claim any such action.\n" + policy,
        default_options={"max_tokens": MAX_OUTPUT_TOKENS, "store": False},
        require_per_service_call_history_persistence=True,
        middleware=[audit.middleware(name)] if audit is not None else [],
    )


def build_drafter(client, name="drafter", *, policy: str | None = None, audit: CallAudit | None = None):
    if policy is None:
        policy = (DATA / "policies/procurement-policy.md").read_text(encoding="utf-8")
    return build_role(client, name, "Draft purchasing guidance; revise it if a review is present.", policy, audit)


def build_workflow(client, *, policy: str | None = None, pattern: str = "sequential",
                   audit: CallAudit | None = None):
    from agent_framework.orchestrations import ConcurrentBuilder, GroupChatBuilder, HandoffBuilder, SequentialBuilder

    if policy is None:
        policy = (DATA / "policies/procurement-policy.md").read_text(encoding="utf-8")
    drafter = build_drafter(client, policy=policy, audit=audit)
    reviewer = build_role(
        client, "reviewer",
        "Read the preceding draft in the conversation. Review totals, approval boundaries and omissions; "
        "return corrected guidance, not a business approval.", policy, audit,
    )
    if pattern == "sequential":
        return SequentialBuilder(participants=[drafter, reviewer], intermediate_output_from=[drafter]).build()
    policy_agent = build_role(client, "policy", "Explain applicable policy caps and approvers.", policy, audit)
    budget_agent = build_role(client, "budget", "Check the requested quantities, arithmetic and budget boundaries.", policy, audit)
    if pattern == "concurrent":
        risk = build_role(client, "risk", "Identify unknown facts and any unperformed actions that must not be claimed.", policy, audit)
        return ConcurrentBuilder(
            participants=[policy_agent, budget_agent, risk],
            intermediate_output_from=[policy_agent, budget_agent, risk],
        ).build()
    if pattern == "group-chat":
        def select_speaker(state):
            names = list(state.participants)
            return names[state.current_round % len(names)]

        return GroupChatBuilder(
            participants=[drafter, reviewer], selection_func=select_speaker, max_rounds=3,
            termination_condition=lambda messages: sum(message.role == "assistant" for message in messages) >= 3,
            intermediate_output_from=[drafter, reviewer],
        ).build()
    if pattern == "handoff":
        coordinator = build_role(
            client, "coordinator",
            "Transfer this request to policy for rules/approvals or budget for arithmetic. "
            "Use a handoff tool instead of answering the purchasing question yourself.", policy, audit,
        )
        return (
            HandoffBuilder(
                participants=[coordinator, policy_agent, budget_agent],
                termination_condition=lambda messages: any(
                    message.role == "assistant" and message.author_name in {"policy", "budget"} and message.text.strip()
                    for message in messages
                ),
            )
            .with_start_agent(coordinator)
            .add_handoff(coordinator, [policy_agent, budget_agent])
            .build()
        )
    raise ValueError(f"Unknown orchestration: {pattern}")


def response_record(response: ResponseLike, role: str, *, allow_handoff: bool = False) -> dict:
    handoffs = [
        content.name for message in getattr(response, "messages", [])
        for content in message.contents
        if content.type == "function_call" and isinstance(content.name, str) and content.name.startswith("handoff_to_")
    ]
    complete = response.finish_reason == "stop" and bool(response.text.strip())
    routed = allow_handoff and response.finish_reason == "tool_calls" and bool(handoffs)
    if not response.response_id or not (complete or routed):
        raise RuntimeError(f"{role}: expected a nonempty, completed response with its actual ID.")
    usage = response.usage_details or {}
    counts = [usage.get(key) for key in ("input_token_count", "output_token_count")]
    if any(value is not None and (type(value) is not int or value < 0) for value in counts):
        raise ValueError(f"{role}: invalid reported token usage.")
    return {
        "role": role, "response_id": response.response_id, "answer": response.text,
        "input_tokens": counts[0], "output_tokens": counts[1],
        "total_tokens": sum(counts) if all(value is not None for value in counts) else None,
        "usage_complete": all(value is not None for value in counts), "handoff_calls": handoffs,
    }


def one_response(outputs: Sequence[ResponseLike], role: str) -> dict:
    if len(outputs) != 1:
        raise RuntimeError(f"{role}: expected exactly one response, found {len(outputs)}.")
    return response_record(outputs[0], role)


def path_record(stages: list[dict], elapsed: float) -> dict:
    complete = all(stage["usage_complete"] for stage in stages)
    return {
        "elapsed_seconds": round(elapsed, 6), "stages": stages,
        "total_tokens": sum(stage["total_tokens"] for stage in stages) if complete else None,
        "usage_complete": complete,
    }


async def compare_paths(client, mode: str, question: str, evidence: Evidence, *, policy: str | None = None,
                        audit: CallAudit | None = None) -> dict:
    if mode not in CALLS:
        raise ValueError("Choose a supported bounded orchestration or baseline.")
    if policy is None:
        policy = (DATA / "policies/procurement-policy.md").read_text(encoding="utf-8")
    paths = {}
    kwargs = {"policy": policy}
    if audit is not None:
        kwargs["audit"] = audit
    if mode in {"single", "compare"}:
        agent = build_drafter(client, name="single", **kwargs)
        first_call = len(audit.records) if audit is not None else 0
        started = time.perf_counter()
        response = await agent.run(question)
        stages = audit.records[first_call:] if audit is not None else [response_record(response, "single")]
        if len(stages) != 1 or stages[0]["role"] != "single":
            raise RuntimeError("The single-agent baseline must preserve exactly one model response.")
        paths["single"] = path_record(stages, time.perf_counter() - started)
        evidence.append("single_completed", paths["single"])
    if mode in {"sequential", "compare"}:
        workflow = build_workflow(client, **kwargs)
        first_call = len(audit.records) if audit is not None else 0
        started = time.perf_counter()
        events = await workflow.run(question)
        elapsed = time.perf_counter() - started
        if not events.get_outputs():
            raise RuntimeError("Sequential execution returned no final answer.")
        stages = audit.records[first_call:] if audit is not None else [
            one_response(events.get_intermediate_outputs(), "drafter"),
            one_response(events.get_outputs(), "reviewer"),
        ]
        if [stage["role"] for stage in stages] != ["drafter", "reviewer"]:
            raise RuntimeError("Sequential execution must preserve the actual drafter and reviewer calls.")
        paths["sequential"] = path_record(stages, elapsed)
        evidence.append("sequential_completed", paths["sequential"])
    if mode in {"concurrent", "group-chat", "handoff"}:
        if audit is None:
            audit = CallAudit(evidence, CALLS[mode])
        workflow = build_workflow(client, policy=policy, pattern=mode, audit=audit)
        started = time.perf_counter()
        events = await workflow.run(question)
        outputs = events.get_outputs()
        if not outputs:
            raise RuntimeError(f"{mode}: no workflow output; partial model calls are retained in evidence.")
        roles = {item["role"] for item in audit.records}
        if mode == "concurrent" and roles != {"policy", "budget", "risk"}:
            raise RuntimeError("Concurrent execution did not return every requested perspective.")
        if mode == "group-chat" and (len(audit.records) != 3 or roles != {"drafter", "reviewer"}):
            raise RuntimeError("Group chat did not complete the bounded three-turn conversation.")
        if mode == "handoff" and (
            not any(item["handoff_calls"] for item in audit.records)
            or not roles.intersection({"policy", "budget"})
        ):
            raise RuntimeError("No actual specialist handoff was observed; do not substitute a direct answer.")
        paths[mode] = {
            **path_record(audit.records, time.perf_counter() - started),
            "final_messages": [
                {"author": message.author_name, "text": message.text}
                for output in outputs for message in output.messages if message.text.strip()
            ],
            "workflow_state": str(events.get_final_state()),
            "human_approval_performed": False,
        }
        evidence.append("orchestration_completed", {"pattern": mode, **paths[mode]})
    delta = None
    if mode == "compare":
        single, sequential = paths["single"], paths["sequential"]
        delta = {
            "elapsed_seconds": round(sequential["elapsed_seconds"] - single["elapsed_seconds"], 6),
            "total_tokens": sequential["total_tokens"] - single["total_tokens"]
            if single["usage_complete"] and sequential["usage_complete"] else None,
        }
    return {"paths": paths, "sequential_minus_single": delta, "policy_sha256": digest(policy), "quality_release": False}


def verify_scope(endpoint: str, receipt: Path) -> None:
    state = json.loads(receipt.read_text(encoding="utf-8"))
    expected = f"https://{state['account_name']}.services.ai.azure.com/api/projects/{state['project_name']}"
    if (
        endpoint != state.get("project_endpoint") or endpoint != expected
        or state.get("language", "ko") != LANGUAGE
    ):
        raise ValueError("Project/language differs from the administrator-provided ownership receipt.")


async def run(mode: str, case: str, evidence: Evidence, endpoint: str, model: str, *, subscription: str) -> dict:
    from agent_framework.foundry import FoundryChatClient
    from azure.ai.projects.aio import AIProjectClient
    from azure.identity.aio import AzureCliCredential

    async with (
        AzureCliCredential(subscription=subscription, process_timeout=30) as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, retry_total=0,
                        connection_timeout=15, read_timeout=60) as project,
    ):
        client = FoundryChatClient(project_client=project, model=model)
        client.client.max_retries = 0
        client.client.timeout = 60.0
        async with client.client:
            audit = CallAudit(evidence, CALLS[mode])
            report = await compare_paths(client, mode, QUESTIONS[LANGUAGE][case], evidence, audit=audit)
    return {
        "schema": "contoso-maf-orchestrations-v1", "language": LANGUAGE, "case": case, "mode": mode,
        "execution": "local_maf_with_azure_model", "model_deployment": model,
        "project_endpoint_sha256": digest(endpoint), "max_model_calls": CALLS[mode],
        "max_output_tokens": MAX_OUTPUT_TOKENS, "max_seconds": MAX_SECONDS, "retries": 0,
        "question": QUESTIONS[LANGUAGE][case],
        **report,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--mode", choices=CALLS, default="sequential")
    parser.add_argument("--case", choices=QUESTIONS["en"], default="purchase")
    parser.add_argument("--receipt", type=Path, default=RESULTS / "azure-environment.json")
    parser.add_argument("--learners", type=int, default=1)
    args = parser.parse_args(argv)
    if not args.live:
        print(f"PLAN ONLY: {args.mode}; at most {CALLS[args.mode]} model calls if approved. No Azure requests.")
        print(json.dumps({"mode": args.mode, "case": args.case, "language": LANGUAGE,
                          "model_calls_if_approved": CALLS[args.mode], "max_seconds": MAX_SECONDS,
                          "max_output_tokens": MAX_OUTPUT_TOKENS, "retries": 0}, ensure_ascii=False))
        return 0
    endpoint, model = read_config()
    verify_scope(endpoint, args.receipt)
    readiness = check_ready(args.receipt, ("chat",), args.learners,
                            expected_endpoint=endpoint, expected_deployment=model)
    from agent_framework import AgentFrameworkException
    from azure.core.exceptions import AzureError
    from openai import OpenAIError

    evidence = Evidence("multiagent")
    try:
        report = asyncio.run(asyncio.wait_for(
            run(args.mode, args.case, evidence, endpoint, model, subscription=readiness["chat"]["subscription"]),
            timeout=MAX_SECONDS,
        ))
        evidence.append("completed", report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if any(not path["usage_complete"] for path in report["paths"].values()):
            print("WARNING: token usage is incomplete; null is not zero and no token comparison is established.", file=sys.stderr)
    except (AgentFrameworkException, AzureError, OpenAIError, RuntimeError, ValueError, OSError, TimeoutError) as error:
        evidence.failure(error)
        raise
    finally:
        print(f"Evidence: {evidence.path}")
    return 0


if __name__ == "__main__":
    run_cli(main)
