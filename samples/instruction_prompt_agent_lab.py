"""Run the fixed v1/v2 comparison through version-pinned Foundry Prompt Agents."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import time

from azure.ai.projects.models import PromptAgentDefinition
from cloud import project_client
from evidence import Budget, digest, redacted, serializable
from grounding import answer_format
from instruction_lab import (
    EXPECTED_SCOPE,
    MAX_CALLS_PER_LANGUAGE,
    MAX_OUTPUT_TOKENS,
    TARGET_DEPLOYMENT,
    TARGET_MODEL,
    TARGET_MODEL_VERSION,
    cases,
    model_input,
    score,
    summarize,
    verify_profile,
)
from search_lab import policy_chunks
from workshop import DATA, LANGUAGE, RESULTS, ROOT, ensure_response

MAX_SECONDS_PER_LANGUAGE = 600
MAX_BILINGUAL_SECONDS = 1200
PROMPT_AGENT_NAMES = {
    "ko": "contoso-instruction-eval-ko-20261001",
    "en": "contoso-instruction-eval-en-20261001",
}
RUBRIC = ROOT / "data/evaluation/instruction-judge.txt"


def _definition(instructions: str, schema: dict) -> PromptAgentDefinition:
    return PromptAgentDefinition(
        model=TARGET_DEPLOYMENT,
        instructions=instructions,
        tools=[],
        tool_choice="none",
        text=schema,
        reasoning={"effort": "low"},
    )


def _write(handle, report: dict) -> None:
    handle.seek(0)
    handle.write(json.dumps(redacted(report), ensure_ascii=False, indent=2) + "\n")
    handle.truncate()
    handle.flush()
    os.fsync(handle.fileno())


def _create_versions(project, agent_name: str, prompts: dict[str, str], schema: dict, report: dict, persist) -> dict:
    existing = {agent.name for agent in project.agents.list(limit=100)}
    if agent_name in existing:
        expected_labels = {"1": "v1", "2": "v2"}
        versions = {}
        for version, label in expected_labels.items():
            recorded = project.agents.get_version(agent_name, version).as_dict()
            expected_definition = _definition(prompts[label], schema).as_dict()
            if (
                recorded.get("name") != agent_name
                or str(recorded.get("version")) != version
                or recorded.get("status") != "active"
                or recorded.get("metadata", {}).get("instruction_version") != label
                or recorded.get("metadata", {}).get("evaluation_only") != "true"
                or recorded.get("definition") != expected_definition
            ):
                raise ValueError(
                    f"Existing Prompt Agent {agent_name!r} version {version} does not match "
                    "the approved active instruction definition; refusing to invoke or modify it."
                )
            versions[label] = version
        report["prompt_agent_versions"] = {
            "agent_name": agent_name,
            "versions": versions,
            "status": "active",
        }
        persist()
        return versions

    versions = {}
    for label in ("v1", "v2"):
        created = project.agents.create_version(
            agent_name=agent_name,
            definition=_definition(prompts[label], schema),
            description="Evaluation-only Contoso purchasing Prompt Agent; synthetic data, no tools.",
            metadata={"instruction_version": label, "evaluation_only": "true"},
        )
        version = str(created.version)
        state = created.status
        deadline = time.monotonic() + 120
        while state != "active" and time.monotonic() < deadline:
            time.sleep(5)
            created = project.agents.get_version(agent_name, version)
            state = created.status
        if state != "active":
            raise RuntimeError(f"Prompt Agent {agent_name} version {version} did not become active.")
        versions[label] = version
        report["prompt_agent_versions"] = {
            "agent_name": agent_name,
            "versions": versions.copy(),
            "status": "active",
        }
        persist()
    return versions


def compare(output: Path, *, max_seconds: int = MAX_SECONDS_PER_LANGUAGE) -> dict:
    from azure.core.exceptions import AzureError
    from openai import OpenAIError

    if LANGUAGE not in PROMPT_AGENT_NAMES:
        raise ValueError("Prompt Agent comparison supports only the checked-in ko/en projects.")
    if type(max_seconds) is not int or not 60 <= max_seconds <= MAX_SECONDS_PER_LANGUAGE:
        raise ValueError(f"Per-language collection time must be between 60 and {MAX_SECONDS_PER_LANGUAGE} seconds.")
    if not output.resolve().is_relative_to(RESULTS.resolve()):
        raise ValueError("Keep Prompt Agent comparison originals inside results/.")
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)

    caseset = cases()
    sources = {row["id"]: row for row in policy_chunks()}
    prompts = {
        f"v{version}": (DATA / f"prompts/agent-v{version}.txt").read_text(encoding="utf-8")
        for version in (1, 2)
    }
    case_file = DATA / "evaluation/instruction-comparison.json"
    schema = answer_format(list(sources))
    shared_input_hashes = {}
    report = {
        "schema": "contoso-instruction-prompt-agent-comparison",
        "language": LANGUAGE,
        "status": "started",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "execution_location": "azure_prompt_agent",
        "execution_source": "Foundry Prompt Agent, invoked by pinned agent_reference version",
        "prompt_agent_count": 1,
        "prompt_agent_versions_created": 2,
        "instructions_sha256": {
            label: hashlib.sha256(text.encode()).hexdigest() for label, text in prompts.items()
        },
        "cases_sha256": digest(caseset),
        "case_file_sha256": hashlib.sha256(case_file.read_bytes()).hexdigest(),
        "rubric_sha256": hashlib.sha256(RUBRIC.read_bytes()).hexdigest(),
        "context_sha256": digest(sources),
        "rows": [],
        "model_calls_max": MAX_CALLS_PER_LANGUAGE,
        "max_seconds": max_seconds,
        "bilingual_collection_max_seconds": MAX_BILINGUAL_SECONDS,
        "retries": 0,
        "holdout_cases": 0,
        "optimizer_jobs": 0,
        "context_source": "Checked-in synthetic policy text; not a live Search retrieval.",
        "shared_wrapper": {
            "input_fields": ["query", "grounding_context", "context_kind", "available_tools"],
            "available_tools": [],
            "version_specific_guidance_in_wrapper": False,
            "target_input_contains_case_criteria_or_reference_answers": False,
            "output_schema_sha256": digest(schema),
        },
        "quality_release": False,
        "reasoning_effort": "low",
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "target_model_deployment": TARGET_DEPLOYMENT,
        "target_model": TARGET_MODEL,
        "target_model_version": TARGET_MODEL_VERSION,
        "target_calls": 0,
    }

    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        persist = lambda: _write(handle, report)
        persist()
        try:
            with project_client() as (project, _, endpoint, model), project.get_openai_client(
                max_retries=0, timeout=60,
            ) as client:
                if model != TARGET_DEPLOYMENT:
                    raise ValueError("Project configuration does not select the approved GPT-6 Sol deployment.")
                target = project.deployments.get(model).as_dict()
                if (target.get("name") != TARGET_DEPLOYMENT
                        or target.get("modelName") != TARGET_MODEL
                        or target.get("modelVersion") != TARGET_MODEL_VERSION):
                    raise ValueError("Foundry deployment readback differs from gpt-6-sol / 2026-09-22.")
                ownership = verify_profile(endpoint, model)
                if ownership["language"] != LANGUAGE:
                    raise ValueError("The endpoint ownership receipt belongs to a different language project.")
                report.update(
                    ownership=ownership,
                    project_endpoint_sha256=digest(endpoint),
                    model_deployment=model,
                    model_identity=serializable(target),
                )
                agent_name = PROMPT_AGENT_NAMES[LANGUAGE]
                versions = _create_versions(project, agent_name, prompts, schema, report, persist)
                report["prompt_agent_versions"] = {
                    "agent_name": agent_name,
                    "versions": versions,
                    "status": "active",
                    "definition_sha256": report["instructions_sha256"],
                    "model_deployment": model,
                    "tools": [],
                }
                persist()

                budget = Budget(
                    max_requests=MAX_CALLS_PER_LANGUAGE,
                    max_tokens=500_000,
                    max_seconds=max_seconds,
                )
                deadline = time.monotonic() + max_seconds
                for case_index, case in enumerate(caseset):
                    shared_input = model_input(case, sources)
                    shared_input_hashes[case["id"]] = digest(shared_input)
                    order = ("v1", "v2") if case_index % 2 == 0 else ("v2", "v1")
                    for label in order:
                        budget.before_request(
                            token_reservation=len(shared_input) + len(prompts[label]) + MAX_OUTPUT_TOKENS,
                        )
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            raise TimeoutError("Per-language Prompt Agent response budget exhausted.")
                        started = time.monotonic()
                        response = client.responses.create(
                            input=shared_input,
                            extra_body={"agent_reference": {
                                "type": "agent_reference",
                                "name": agent_name,
                                "version": versions[label],
                            }},
                            max_output_tokens=MAX_OUTPUT_TOKENS,
                            store=False,
                            timeout=min(60, remaining),
                        )
                        row = {
                            "id": case["id"],
                            "instructions": label,
                            "call_order": len(report["rows"]) + 1,
                            "query": case["query"],
                            "status": response.status,
                            "response_id": response.id,
                            "model": response.model,
                            "raw_answer": response.output_text,
                            "input_sha256": shared_input_hashes[case["id"]],
                            "request_id": getattr(response, "_request_id", None),
                            "usage": serializable(response.usage),
                            "latency_seconds": round(time.monotonic() - started, 3),
                            "agent_name": agent_name,
                            "agent_version": versions[label],
                        }
                        report["rows"].append(row)
                        report["target_calls"] = len(report["rows"])
                        persist()
                        raw = ensure_response(response)
                        if response.model not in {TARGET_DEPLOYMENT, TARGET_MODEL}:
                            raise ValueError("Prompt Agent response model differs from the verified GPT-6 Sol deployment.")
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
        except (AzureError, OpenAIError, ValueError, RuntimeError, OSError, TimeoutError) as exc:
            report["status"] = "failed"
            report["operation_error"] = {"type": type(exc).__name__, "message": str(exc)}
            raise
        finally:
            report["finished_at"] = datetime.now(timezone.utc).isoformat()
            persist()
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS / f"instruction-prompt-agent-{LANGUAGE}.json",
    )
    parser.add_argument("--max-seconds", type=int, default=MAX_SECONDS_PER_LANGUAGE)
    parser.add_argument("--live", action="store_true", help="Create pinned Prompt Agent versions and collect 24 responses.")
    args = parser.parse_args()
    if not args.live:
        print(json.dumps({
            "plan_only": True,
            "language": LANGUAGE,
            "agent_name": PROMPT_AGENT_NAMES.get(LANGUAGE),
            "prompt_agent_versions": ["v1", "v2"],
            "model_deployment": TARGET_DEPLOYMENT,
            "model": TARGET_MODEL,
            "model_version": TARGET_MODEL_VERSION,
            "same_fixed_cases_per_version": 12,
            "model_calls": 0,
            "model_calls_if_approved": MAX_CALLS_PER_LANGUAGE,
            "max_seconds": args.max_seconds,
            "bilingual_collection_max_seconds": MAX_BILINGUAL_SECONDS,
            "optimizer_jobs": 0,
            "holdout_cases": 0,
            "quality_release": False,
        }, ensure_ascii=False, indent=2))
        return
    if args.output.exists():
        raise ValueError("Prompt Agent comparison original already exists; inspect it instead of rerunning.")
    result = compare(args.output, max_seconds=args.max_seconds)
    print(json.dumps({
        "status": result["status"],
        "target_calls": result["target_calls"],
        "agent": result["prompt_agent_versions"],
        "comparison": result["comparison"]["local_checklist"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
