"""Compare one agent with a two-agent MAF workflow; plan-only without --live."""

from __future__ import annotations

import argparse
import asyncio
from collections.abc import Mapping, Sequence
import json
from pathlib import Path
import sys
import time
from typing import Protocol

from evidence import Evidence, digest
from workshop import DATA, LANGUAGE, RESULTS, read_config

MAX_SECONDS = 180
MAX_OUTPUT_TOKENS = 2048
CALLS = {"single": 1, "sequential": 2, "compare": 3}
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


def build_drafter(client, name="drafter", *, policy: str | None = None):
    from agent_framework import Agent

    if policy is None:
        policy = (DATA / "policies/procurement-policy.md").read_text(encoding="utf-8")
    return Agent(
        client=client, name=name,
        instructions=(
            "Draft purchasing guidance in English using only the following synthetic policy. You have no tool or order authority.\n"
            if LANGUAGE == "en" else "다음 합성 정책만 사용해 구매 안내 초안을 작성한다. 도구·주문 권한은 없다.\n"
        ) + policy,
        default_options={"max_tokens": MAX_OUTPUT_TOKENS, "store": False},
    )


def build_workflow(client, *, policy: str | None = None):
    from agent_framework import Agent, WorkflowBuilder

    if policy is None:
        policy = (DATA / "policies/procurement-policy.md").read_text(encoding="utf-8")
    drafter = build_drafter(client, policy=policy)
    reviewer = Agent(
        client=client, name="reviewer",
        instructions=(
            "Compare the draft with the policy. Check the total and approval boundaries, then return corrected guidance in English. "
            "State explicitly that this is a review draft, not an approval or an order.\n"
            if LANGUAGE == "en" else
            "이전 초안을 정책과 대조하라. 총액과 승인 경계를 검사하고 수정한 최종 안내를 한국어로 답하라. "
            "실제 승인·주문이 아니라 검토 초안임을 명시하라.\n"
        ) + policy,
        default_options={"max_tokens": MAX_OUTPUT_TOKENS, "store": False},
    )
    return WorkflowBuilder(
        start_executor=drafter, output_from=[reviewer], max_iterations=4,
        intermediate_output_from=[drafter],
    ).add_edge(drafter, reviewer).build()


def response_record(response: ResponseLike, role: str) -> dict:
    if not response.text.strip() or not response.response_id or response.finish_reason != "stop":
        raise RuntimeError(f"{role}: expected a nonempty, completed response with its actual ID.")
    usage = response.usage_details or {}
    counts = [usage.get(key) for key in ("input_token_count", "output_token_count")]
    if any(value is not None and (type(value) is not int or value < 0) for value in counts):
        raise ValueError(f"{role}: invalid reported token usage.")
    return {
        "role": role, "response_id": response.response_id, "answer": response.text,
        "input_tokens": counts[0], "output_tokens": counts[1],
        "total_tokens": sum(counts) if all(value is not None for value in counts) else None,
        "usage_complete": all(value is not None for value in counts),
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


async def compare_paths(client, mode: str, question: str, evidence: Evidence, *, policy: str | None = None) -> dict:
    if mode not in CALLS:
        raise ValueError("Choose single, sequential, or compare.")
    if policy is None:
        policy = (DATA / "policies/procurement-policy.md").read_text(encoding="utf-8")
    paths = {}
    if mode in {"single", "compare"}:
        agent = build_drafter(client, name="single", policy=policy)
        started = time.perf_counter()
        response = await agent.run(question)
        paths["single"] = path_record([response_record(response, "single")], time.perf_counter() - started)
        evidence.append("single_completed", paths["single"])
    if mode in {"sequential", "compare"}:
        workflow = build_workflow(client, policy=policy)
        started = time.perf_counter()
        events = await workflow.run(question)
        elapsed = time.perf_counter() - started
        stages = [
            one_response(events.get_intermediate_outputs(), "drafter"),
            one_response(events.get_outputs(), "reviewer"),
        ]
        paths["sequential"] = path_record(stages, elapsed)
        evidence.append("sequential_completed", paths["sequential"])
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


async def run(mode: str, case: str, evidence: Evidence, endpoint: str, model: str) -> dict:
    from agent_framework.foundry import FoundryChatClient
    from azure.ai.projects.aio import AIProjectClient
    from azure.identity.aio import AzureCliCredential

    async with (
        AzureCliCredential(process_timeout=30) as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, retry_total=0,
                        connection_timeout=15, read_timeout=60) as project,
    ):
        client = FoundryChatClient(project_client=project, model=model)
        client.client.max_retries = 0
        client.client.timeout = 60.0
        async with client.client:
            report = await compare_paths(client, mode, QUESTIONS[LANGUAGE][case], evidence)
    return {
        "schema": "contoso-maf-comparison-v1", "language": LANGUAGE, "case": case,
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
    args = parser.parse_args(argv)
    if not args.live:
        print(f"PLAN ONLY: {args.mode}; at most {CALLS[args.mode]} model calls if approved. No Azure requests.")
        print(json.dumps({"mode": args.mode, "case": args.case, "language": LANGUAGE,
                          "model_calls_if_approved": CALLS[args.mode], "max_seconds": MAX_SECONDS,
                          "max_output_tokens": MAX_OUTPUT_TOKENS, "retries": 0}, ensure_ascii=False))
        return 0
    endpoint, model = read_config()
    verify_scope(endpoint, args.receipt)
    from agent_framework import AgentFrameworkException
    from azure.core.exceptions import AzureError
    from openai import OpenAIError

    evidence = Evidence("multiagent")
    try:
        report = asyncio.run(asyncio.wait_for(
            run(args.mode, args.case, evidence, endpoint, model), timeout=MAX_SECONDS,
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
    raise SystemExit(main())
