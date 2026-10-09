"""Collect one bounded v1/v2 development comparison; never retry or use holdout."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import time

from cloud import project_client
from evidence import Budget, digest, redacted, serializable
from grounding import answer_format, parse_answer
from lab_cli import run
from model_capacity import Management, inspect_deployments, load_scope, require_ready, requirements
from original_files import Attempt, open_original, retryable_original
from search_lab import policy_chunks
from workshop import DATA, LANGUAGE, RESULTS, ROOT, config_values, ensure_response

TARGET_DEPLOYMENT = "contoso-chat"
TARGET_MODEL = "gpt-6-sol"
TARGET_MODEL_VERSION = "2026-09-22"
MAX_CALLS_PER_LANGUAGE = 24
MAX_SECONDS_PER_LANGUAGE = 600
MAX_OUTPUT_TOKENS = 2048

def cases() -> list[dict]:
    comparison = json.loads((DATA / "evaluation/instruction-comparison.json").read_text(encoding="utf-8"))
    contract = comparison.get("comparison_contract", {})
    if (
        contract.get("cases_per_language") != 12
        or contract.get("target_responses_per_language") != MAX_CALLS_PER_LANGUAGE
        or contract.get("target_responses_total_max") != 48
        or contract.get("reference_answers_in_target_input") is not False
        or contract.get("criteria_hidden_from_target_model") is not True
        or contract.get("holdout_is_sealed") is not True
    ):
        raise ValueError("The bilingual 12-case development comparison contract changed.")
    rows = comparison.get("cases", [])
    if len(rows) != 12 or len({row.get("id") for row in rows}) != 12:
        raise ValueError("The learning comparison requires exactly 12 unique, fixed questions.")
    for row in rows:
        if set(row) != {"id", "risk_dimensions", "query", "checks"} or not row["query"] or len(row["checks"]) < 3:
            raise ValueError(f"Unexpected comparison case or checklist shape: {row.get('id')}.")
        check_ids = set()
        for check in row["checks"]:
            if (set(check) != {"id", "requirement", "pattern", "sources", "critical"}
                    or not check["requirement"] or not check["sources"] or type(check["critical"]) is not bool):
                raise ValueError(f"Invalid precommitted evaluator criterion: {row['id']}.")
            if check["id"] in check_ids:
                raise ValueError(f"Duplicate criterion ID in {row['id']}.")
            check_ids.add(check["id"])
            re.compile(check["pattern"])
    return rows


def score(raw: str, case: dict, sources: dict) -> dict:
    parse_answer(raw, sources)
    answer = json.loads(raw)
    selected = set(answer["citation_ids"])
    checks = {
        check["id"]: {
            "matched": bool(re.search(check["pattern"], answer["answer"], re.I | re.S))
            and set(check["sources"]) <= selected,
            "critical": check["critical"],
            "required_sources": check["sources"],
        }
        for check in case["checks"]
    }
    failed_critical = [key for key, value in checks.items() if value["critical"] and not value["matched"]]
    return {
        "matched": sum(value["matched"] for value in checks.values()),
        "total": len(checks),
        "checks": checks,
        "critical_failures": failed_critical,
        "scope": "Supporting mechanical text-and-citation checks only; native Foundry judgments are the primary quality evidence.",
    }


def model_input(case: dict, sources: dict) -> str:
    return json.dumps({
        "query": case["query"],
        "grounding_context": list(sources.values()),
        "context_kind": "supplied_synthetic_documents_not_a_tool_execution",
        "available_tools": [],
    }, ensure_ascii=False)


def comparison_outcome(delta: float) -> str:
    return "improved" if delta > 0 else "unchanged" if delta == 0 else "regressed"


def summarize(rows: list[dict], expected: list[dict]) -> dict:
    expected_ids = {case["id"] for case in expected}
    if len(rows) != MAX_CALLS_PER_LANGUAGE:
        raise ValueError("A complete comparison requires one v1 and one v2 response for all 12 cases.")
    if len({row["model"] for row in rows}) != 1 or any(row["status"] != "completed" for row in rows):
        raise ValueError("A failed response or mixed target deployment cannot establish a comparison.")
    by_case = {}
    for row in rows:
        if row["id"] not in expected_ids:
            raise ValueError("Unexpected question in the comparison.")
        by_case.setdefault(row["id"], []).append(row)
    if set(by_case) != expected_ids or any(
        len(pair) != 2 or {row["instructions"] for row in pair} != {"v1", "v2"}
        or len({row["input_sha256"] for row in pair}) != 1
        or len({row["query"] for row in pair}) != 1
        or len({row["response_id"] for row in pair}) != 2
        for pair in by_case.values()
    ):
        raise ValueError("Every question needs exactly one matched pair with identical model input.")

    by_version = {
        version: [row for row in rows if row["instructions"] == version]
        for version in ("v1", "v2")
    }
    if any(len(selected) != len(expected_ids) for selected in by_version.values()):
        raise ValueError("Each instruction version must have exactly 12 completed answers.")
    scores = {
        version: sum(row["checklist"]["matched"] for row in selected)
        for version, selected in by_version.items()
    }
    maximum = sum(len(case["checks"]) for case in expected)
    case_comparison = {}
    for case_id, pair in by_case.items():
        case_comparison[case_id] = {
            version: next(row for row in pair if row["instructions"] == version)["checklist"]
            for version in ("v1", "v2")
        }
    metrics = {}
    for version, selected in by_version.items():
        usage = [row.get("usage") for row in selected]
        metrics[version] = {
            "responses": len(selected),
            "input_tokens": sum(row["input_tokens"] for row in usage) if all(usage and isinstance(row, dict) and type(row.get("input_tokens")) is int for row in usage) else None,
            "output_tokens": sum(row["output_tokens"] for row in usage) if all(usage and isinstance(row, dict) and type(row.get("output_tokens")) is int for row in usage) else None,
            "total_tokens": sum(row["total_tokens"] for row in usage) if all(usage and isinstance(row, dict) and type(row.get("total_tokens")) is int for row in usage) else None,
            "mean_latency_seconds": round(sum(row["latency_seconds"] for row in selected) / len(selected), 3),
            "total_latency_seconds": round(sum(row["latency_seconds"] for row in selected), 3),
        }
    token_delta = {
        key: metrics["v2"][key] - metrics["v1"][key]
        if type(metrics["v1"][key]) is int and type(metrics["v2"][key]) is int else None
        for key in ("input_tokens", "output_tokens", "total_tokens")
    }
    latency_delta = round(metrics["v2"]["mean_latency_seconds"] - metrics["v1"]["mean_latency_seconds"], 3)
    checklist_delta = scores["v2"] - scores["v1"]
    critical_failures = {
        version: [
            {"case_id": row["id"], "criteria": row["checklist"]["critical_failures"]}
            for row in by_version[version] if row["checklist"]["critical_failures"]
        ]
        for version in ("v1", "v2")
    }
    return {
        "local_checklist": {
            "scores": scores, "maximum": maximum, "delta": checklist_delta,
            "outcome": comparison_outcome(checklist_delta), "per_case": case_comparison,
            "critical_failures": critical_failures,
            "scope": "Mechanical text-and-citation coverage; supporting only, not semantic quality or a release gate.",
        },
        "usage_latency": {
            "by_instruction": metrics, "v2_minus_v1_tokens": token_delta,
            "v2_minus_v1_mean_latency_seconds": latency_delta,
        },
        "quality_release": False,
        "scope": "One paired development comparison on 12 exposed teaching questions; not independent generalization or release approval.",
    }


def verify_profile(endpoint: str, model: str, *, roles: tuple[str, ...] = ("chat",)) -> dict:
    receipt = load_scope(RESULTS / "azure-environment.json", language=LANGUAGE, roles=roles)
    if receipt["project_endpoint"].rstrip("/") != endpoint.rstrip("/") or receipt["model_deployments"]["chat"] != model:
        raise ValueError("The owned-environment receipt differs from the selected project/model.")
    deployments, _ = inspect_deployments(receipt, requirements(), roles, Management())
    require_ready(deployments)
    target = deployments["chat"]
    if target["model"] != TARGET_MODEL or target["version"] != TARGET_MODEL_VERSION:
        raise ValueError("The owned deployment is not the required gpt-6-sol / 2026-09-22.")
    return {
        "repository_id": 1396573688,
        "language": LANGUAGE,
        "resource_group": receipt["resource_group"],
        "project": receipt["project_name"],
        "project_endpoint_sha256": digest(endpoint),
        "receipt_sources": ["results/azure-environment.json"],
        "model_deployment": model,
        "judge_deployment": receipt["model_deployments"].get("judge"),
        "model": TARGET_MODEL,
        "model_version": TARGET_MODEL_VERSION,
        "capacity_readback": deployments,
    }


def compare(output: Path, *, reasoning_effort: str | None = "low", max_seconds: int = MAX_SECONDS_PER_LANGUAGE) -> dict:
    # A failure before the first model request (no sign-in, wrong deployment name) keeps its record under
    # a .failed-<time> name, so the same command can be run again after the cause is fixed.
    with retryable_original(output) as attempt:
        return _compare(output, reasoning_effort, max_seconds, attempt)


def _compare(output: Path, reasoning_effort: str | None, max_seconds: int, attempt: Attempt) -> dict:
    from azure.core.exceptions import AzureError
    from openai import OpenAIError

    if type(max_seconds) is not int or not 60 <= max_seconds <= MAX_SECONDS_PER_LANGUAGE:
        raise ValueError(f"Per-language response collection must be between 60 and {MAX_SECONDS_PER_LANGUAGE} seconds.")
    caseset = cases()
    sources = {row["id"]: row for row in policy_chunks()}
    prompts = {f"v{version}": (DATA / f"prompts/agent-v{version}.txt").read_text(encoding="utf-8") for version in (1, 2)}
    if any(not set(check["sources"]) <= sources.keys() for case in caseset for check in case["checks"]):
        raise ValueError("A fixed evaluation criterion cites an unknown source.")
    case_file = DATA / "evaluation/instruction-comparison.json"
    rubric_file = ROOT / "data/evaluation/instruction-judge.txt"
    if not output.resolve().is_relative_to(RESULTS.resolve()):
        raise ValueError("Keep raw comparison originals inside results/.")
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor = open_original(output, attempt)
    report = {
        "schema": "contoso-instruction-comparison",
        "language": LANGUAGE,
        "status": "started",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "instructions_sha256": {name: hashlib.sha256(text.encode()).hexdigest() for name, text in prompts.items()},
        "cases_sha256": digest(caseset),
        "case_file_sha256": hashlib.sha256(case_file.read_bytes()).hexdigest(),
        "rubric_sha256": hashlib.sha256(rubric_file.read_bytes()).hexdigest(),
        "context_sha256": digest(sources),
        "rows": [],
        "model_calls_max": MAX_CALLS_PER_LANGUAGE,
        "max_seconds": max_seconds,
        "bilingual_collection_max_seconds": 1200,
        "retries": 0,
        "holdout_cases": 0,
        "optimizer_rows": 0,
        "context_source": "Checked-in synthetic policy text; not a live Search retrieval.",
        "shared_wrapper": {
            "input_fields": ["query", "grounding_context", "context_kind", "available_tools"],
            "available_tools": [],
            "version_specific_guidance_in_wrapper": False,
            "target_input_contains_case_criteria_or_reference_answers": False,
            "output_schema_sha256": digest(answer_format(list(sources))),
        },
        "quality_release": False,
        "reasoning_effort": reasoning_effort,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
    }
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        def persist() -> None:
            handle.seek(0)
            handle.write(json.dumps(redacted(report), ensure_ascii=False, indent=2) + "\n")
            handle.truncate()
            handle.flush()

        persist()
        try:
            with project_client() as (project, _, endpoint, model), project.get_openai_client(
                max_retries=0, timeout=60,
            ) as client:
                ownership = verify_profile(endpoint, model)
                target = project.deployments.get(model).as_dict()
                if (target.get("name") != model
                        or target.get("modelName") != TARGET_MODEL
                        or target.get("modelVersion") != TARGET_MODEL_VERSION):
                    raise ValueError("Foundry deployment readback differs from gpt-6-sol / 2026-09-22.")
                report.update(
                    ownership=ownership,
                    project_endpoint_sha256=digest(endpoint),
                    model_deployment=model,
                    model_identity=serializable(target),
                    execution_location="azure_model",
                    tools_executed=0,
                )
                persist()
                budget = Budget(max_requests=MAX_CALLS_PER_LANGUAGE, max_tokens=500_000, max_seconds=max_seconds)
                deadline = time.monotonic() + max_seconds
                schema = answer_format(list(sources))
                for case_index, case in enumerate(caseset):
                    shared_input = model_input(case, sources)
                    order = ("v1", "v2") if case_index % 2 == 0 else ("v2", "v1")
                    for version in order:
                        budget.before_request(
                            token_reservation=len(shared_input) + len(prompts[version]) + MAX_OUTPUT_TOKENS,
                        )
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            raise TimeoutError("Per-language response-collection budget exhausted.")
                        started = time.monotonic()
                        attempt.side_effects = True
                        response = client.responses.create(
                            model=model,
                            instructions=prompts[version],
                            input=shared_input,
                            text=schema,
                            tools=[],
                            tool_choice="none",
                            max_output_tokens=MAX_OUTPUT_TOKENS,
                            store=False,
                            timeout=min(60, remaining),
                            **({"reasoning": {"effort": reasoning_effort}} if reasoning_effort else {}),
                        )
                        row = {
                            "id": case["id"],
                            "instructions": version,
                            "call_order": len(report["rows"]) + 1,
                            "query": case["query"],
                            "status": response.status,
                            "response_id": response.id,
                            "model": response.model,
                            "raw_answer": response.output_text,
                            "input_sha256": digest(shared_input),
                            "request_id": getattr(response, "_request_id", None),
                            "usage": serializable(response.usage),
                            "latency_seconds": round(time.monotonic() - started, 3),
                        }
                        report["rows"].append(row)
                        persist()
                        raw = ensure_response(response)
                        if response.model not in {model, TARGET_MODEL}:
                            raise ValueError("Response model field differs from the verified target deployment.")
                        row["checklist"] = score(raw, case, sources)
                        if response.usage:
                            budget.record_tokens(response.usage.total_tokens)
                        persist()
                report["comparison"] = summarize(report["rows"], caseset)
                report["status"] = "completed"
                report["budget_usage"] = {
                    "requests": budget.requests,
                    "max_requests": budget.max_requests,
                    "tokens": budget.tokens,
                    "max_tokens": budget.max_tokens,
                    "elapsed_seconds": round(time.monotonic() - budget.started, 3),
                    "max_seconds": budget.max_seconds,
                }
        except (AzureError, OpenAIError, OSError, ValueError, RuntimeError) as exc:
            report.update(status="failed", error={"type": type(exc).__name__, "message": str(exc)})
            raise
        finally:
            report["finished_at"] = datetime.now(timezone.utc).isoformat()
            persist()
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Explicitly allow 24 paid model calls once for this language.")
    parser.add_argument("--output", type=Path, default=RESULTS / f"instruction-comparison-{LANGUAGE}.json")
    parser.add_argument("--reasoning-effort", choices=["none", "low", "medium", "high", "xhigh"], default="low",
                        help="Use the same reasoning setting for both instructions (default: low).")
    parser.add_argument("--max-seconds", type=int, default=MAX_SECONDS_PER_LANGUAGE,
                        help="Per-language bound; the bilingual collection is limited to 1200 seconds total.")
    args = parser.parse_args()
    if type(args.max_seconds) is not int or not 60 <= args.max_seconds <= MAX_SECONDS_PER_LANGUAGE:
        raise ValueError(f"Per-language response collection must be between 60 and {MAX_SECONDS_PER_LANGUAGE} seconds.")
    if not args.live:
        print(json.dumps({
            "plan_only": True,
            "language": LANGUAGE,
            "instructions": ["v1", "v2"],
            "same_cases_per_version": len(cases()),
            "model_calls": 0,
            "model_calls_if_approved": MAX_CALLS_PER_LANGUAGE,
            "bilingual_target_calls_max": 48,
            "per_language_collection_max_seconds": args.max_seconds,
            "bilingual_collection_max_seconds": 1200,
            "maximum_local_checklist_score": sum(len(case["checks"]) for case in cases()),
            "target_deployment": config_values()["FOUNDRY_MODEL_DEPLOYMENT_NAME"] or TARGET_DEPLOYMENT,
            "target_model": TARGET_MODEL,
            "target_model_version": TARGET_MODEL_VERSION,
            "new_agent_deployments": 0,
            "optimizer_jobs": 0,
            "holdout_cases": 0,
            "output": str(args.output),
            "score_improvement_guaranteed": False,
            "reasoning_effort": args.reasoning_effort,
        }, ensure_ascii=False, indent=2))
        return
    if args.output.exists():
        raise ValueError("A comparison already exists. Preserve it; do not resample until a better score appears.")
    result = compare(args.output, reasoning_effort=args.reasoning_effort, max_seconds=args.max_seconds)
    print(json.dumps({
        "language": LANGUAGE,
        "status": result["status"],
        "responses": len(result["rows"]),
        "local_checklist": result["comparison"]["local_checklist"]["scores"],
        "outcome": result["comparison"]["local_checklist"]["outcome"],
        "usage_latency": result["comparison"]["usage_latency"],
        "quality_release": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run(main)
