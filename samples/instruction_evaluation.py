"""Evaluate the existing v1/v2 answers once in Foundry; never reinvoke the target."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import time
from uuid import uuid4

from cloud import project_client
from evaluation_lab import check_native_completeness, wait_for_native
from evidence import Evidence, digest, redacted, serializable
from grounding import answer_format, parse_answer
from instruction_lab import cases, model_input, score, summarize, verify_profile
from search_lab import policy_chunks
from workshop import DATA, LANGUAGE, RESULTS, ROOT, config_values

RUBRIC = ROOT / "data/evaluation/instruction-judge.txt"
METRICS = ("completeness", "relevance", "groundedness")
FIELDS = ("id", "query", "expected_behavior", "response", "context")
THRESHOLD = 4


def prepare(source: Path) -> tuple[dict, list[dict], dict]:
    recorded = json.loads(source.read_text(encoding="utf-8"))
    expected = cases()
    sources = {row["id"]: row for row in policy_chunks()}
    execution_location = recorded.get("execution_location")
    if (recorded.get("language") != LANGUAGE or recorded.get("status") != "completed"
            or execution_location not in {"azure_model", "azure_prompt_agent"}
            or recorded.get("cases_sha256") != digest(expected) or recorded.get("context_sha256") != digest(sources)
            or recorded.get("reasoning_effort") != "low" or recorded.get("max_output_tokens") != 2048
            or recorded.get("retries") != 0):
        raise ValueError("Native comparison requires the complete actual answers and unchanged language/questions/context.")
    if execution_location == "azure_prompt_agent":
        prompt_agents = recorded.get("prompt_agent_versions", {})
        versions = prompt_agents.get("versions", {})
        model_identity = recorded.get("model_identity", {})
        if (recorded.get("schema") != "contoso-instruction-prompt-agent-comparison"
                or prompt_agents.get("status") != "active"
                or not prompt_agents.get("agent_name")
                or set(versions) != {"v1", "v2"}
                or not isinstance(recorded.get("model_deployment"), str)
                or not recorded["model_deployment"]
                or model_identity.get("name") != recorded["model_deployment"]
                or model_identity.get("modelName") != "gpt-6-sol"
                or model_identity.get("modelVersion") != "2026-09-22"):
            raise ValueError("Prompt Agent native evaluation requires two verified, active instruction versions.")
    if (recorded.get("case_file_sha256") != hashlib.sha256((DATA / "evaluation/instruction-comparison.json").read_bytes()).hexdigest()
            or recorded.get("rubric_sha256") != hashlib.sha256(RUBRIC.read_bytes()).hexdigest()
            or recorded.get("shared_wrapper", {}).get("output_schema_sha256") != digest(answer_format(list(sources)))
            or recorded.get("shared_wrapper", {}).get("version_specific_guidance_in_wrapper") is not False
            or recorded.get("shared_wrapper", {}).get("target_input_contains_case_criteria_or_reference_answers") is not False):
        raise ValueError("The precommitted evaluation rubric or common target-input contract changed.")
    hashes = {f"v{version}": hashlib.sha256((DATA / f"prompts/agent-v{version}.txt").read_bytes()).hexdigest()
              for version in (1, 2)}
    if recorded.get("instructions_sha256") != hashes:
        raise ValueError("Instructions changed after target collection; do not relabel or resample the answers.")
    if len(recorded.get("rows", [])) != 24 or summarize(recorded["rows"], expected) != recorded.get("comparison"):
        raise ValueError("Recorded comparison is partial or its original local checks changed.")
    by_id = {row["id"]: row for row in expected}
    native_rows, identities = [], {}
    for row in recorded["rows"]:
        case = by_id[row["id"]]
        if (row["query"] != case["query"] or row["input_sha256"] != digest(model_input(case, sources))
                or not row.get("response_id") or row.get("checklist") != score(row["raw_answer"], case, sources)):
            raise ValueError("A target answer differs from its actual question, context, or preserved checks.")
        if execution_location == "azure_prompt_agent" and (
            row.get("agent_name") != prompt_agents["agent_name"]
            or row.get("agent_version") != versions.get(row["instructions"])
        ):
            raise ValueError("A Prompt Agent answer is not pinned to its recorded instruction version.")
        text, _ = parse_answer(row["raw_answer"], sources)
        opaque = uuid4().hex
        identities[opaque] = {"case_id": row["id"], "instructions": row["instructions"], "response_id": row["response_id"]}
        native_rows.append({
            "id": opaque,
            "query": row["query"],
            "expected_behavior": "\n".join(f"- {check['requirement']}" for check in case["checks"]),
            "response": text,
            "context": json.dumps(list(sources.values()), ensure_ascii=False),
        })
    native_rows.sort(key=lambda row: row["id"])
    return recorded, native_rows, identities


def audit(native: dict, rows: list[dict], identities: dict, *, metric_names: tuple[str, ...] = METRICS) -> dict:
    if not metric_names or len(set(metric_names)) != len(metric_names) or not set(metric_names) <= set(METRICS):
        raise ValueError("Expected distinct supported comparison metrics.")
    check_native_completeness(native, len(rows))
    expected = {row["id"]: row for row in rows}
    judged = {}
    for item in native["items"]:
        source = item.get("datasource_item") or {}
        identifier = source.get("id")
        if identifier not in expected or identifier in judged or any(source.get(key) != expected[identifier][key] for key in FIELDS):
            raise ValueError("Native output lacks unique exact source rows.")
        metrics = {}
        for name in metric_names:
            values = [value for value in item.get("results", []) if value.get("name") == name]
            if not values or any(
                value.get("status") in {"error", "errored", "skipped", "failed"} or value.get("error")
                or (value.get("sample") or {}).get("error") for value in values
            ):
                raise ValueError(f"Missing or errored native metric: {name}.")
            scores = [value["score"] for value in values if type(value.get("score")) in (int, float)]
            verdicts = [value for value in values if type(value.get("passed")) is bool]
            if (len(scores) != 1 or len(verdicts) != 1 or not math.isfinite(scores[0])
                    or scores[0] not in {1, 2, 3, 4, 5}
                    or verdicts[0]["passed"] != (scores[0] >= THRESHOLD)
                    or not isinstance(verdicts[0].get("reason"), str) or not verdicts[0]["reason"].strip()):
                raise ValueError(f"Incomplete or contradictory native score/verdict/reason: {name}.")
            metrics[name] = {"score": scores[0], "passed": verdicts[0]["passed"], "reason": verdicts[0]["reason"]}
        judged[identifier] = {**identities[identifier], "metrics": metrics}
    if set(judged) != set(expected):
        raise ValueError("Missing native comparison rows.")
    scores = {}
    for version in ("v1", "v2"):
        selected = [row for row in judged.values() if row["instructions"] == version]
        if len(selected) != 12:
            raise ValueError("Each instruction version requires all twelve native results.")
        scores[version] = {
            name: {"mean": sum(row["metrics"][name]["score"] for row in selected) / 12,
                   "passed": sum(row["metrics"][name]["passed"] for row in selected), "total": 12}
            for name in metric_names
        }
    return {
        "scores": scores, "delta": {name: scores["v2"][name]["mean"] - scores["v1"][name]["mean"] for name in metric_names},
        "rows": list(judged.values()), "quality_release": False, "judge_control_calibration_performed": False,
        "scope": "One uncalibrated 24-row Foundry development evaluation, not an independent holdout or release gate.",
    }


def evaluate(source: Path, output: Path) -> dict:
    from azure.ai.projects.models import TestingCriterionAzureAIEvaluator
    from azure.core.exceptions import AzureError
    from openai import OpenAIError

    recorded, rows, identities = prepare(source)
    if not output.resolve().is_relative_to(RESULTS.resolve()):
        raise ValueError("Keep native originals inside results/.")
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    evidence = Evidence("instruction-native")
    report = {
        "schema": "contoso-instruction-native", "language": LANGUAGE, "status": "started",
        "started_at": datetime.now(timezone.utc).isoformat(), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "rubric_sha256": hashlib.sha256(RUBRIC.read_bytes()).hexdigest(), "threshold": THRESHOLD,
        "identities": identities, "submitted_rows": rows, "quality_release": False,
        "target_reinvocations": 0, "optimizer_jobs": 0, "holdout_cases": 0,
        "native_max_seconds": 600, "cancellation_max_seconds": 90,
        "native_rows": 24,
    }
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        def persist():
            handle.seek(0)
            handle.write(json.dumps(redacted(report), ensure_ascii=False, indent=2) + "\n")
            handle.truncate()
            handle.flush()

        persist()
        try:
            with project_client(evidence) as (project, _, endpoint, model), project.get_openai_client(max_retries=0, timeout=60) as client:
                if recorded["project_endpoint_sha256"] != digest(endpoint) or recorded["model_deployment"] != model:
                    raise ValueError("Native evaluator project/model differs from the collected answers.")
                ownership = verify_profile(endpoint, model, roles=("chat", "judge"))
                judge = config_values()["FOUNDRY_JUDGE_DEPLOYMENT_NAME"]
                if not judge or judge != ownership["judge_deployment"] or judge == model:
                    raise ValueError("Use the distinct judge deployment in the owned-environment receipt.")
                judge_identity = project.deployments.get(judge).as_dict()
                if (judge_identity.get("modelName") != "gpt-4.1"
                        or judge_identity.get("modelVersion") != "2025-04-14"):
                    raise ValueError("Judge readback differs from the precommitted gpt-4.1 / 2025-04-14.")
                report["ownership"] = ownership
                report["models"] = {role: serializable(project.deployments.get(name))
                                    for role, name in (("target", model), ("judge", judge))}
                builtin = {name: serializable(project.beta.evaluators.get_version("builtin." + name, "latest"))
                           for name in ("relevance", "groundedness")}
                report["builtin_catalog"] = builtin
                evaluator_name = "contoso-learning-completeness-" + uuid4().hex[:8]
                evaluator = project.beta.evaluators.create_version(
                    name=evaluator_name,
                    evaluator_version={
                        "name": evaluator_name, "evaluator_type": "custom", "categories": ["quality"],
                        "display_name": "Contoso instruction completeness",
                        "definition": {
                            "type": "prompt", "prompt_text": RUBRIC.read_text(encoding="utf-8"),
                            "init_parameters": {"type": "object", "properties": {
                                "deployment_name": {"type": "string"}, "threshold": {"type": "number"},
                            }, "required": ["deployment_name", "threshold"]},
                            "data_schema": {"type": "object", "properties": {
                                key: {"type": "string"} for key in FIELDS[1:]
                            }, "required": list(FIELDS[1:])},
                            "metrics": {"completeness": {"type": "ordinal", "min_value": 1, "max_value": 5,
                                                        "desirable_direction": "increase", "threshold": THRESHOLD}},
                        },
                    },
                )
                report["custom_evaluator"] = serializable(evaluator)
                evidence.append("evaluator_created", evaluator)
                persist()
                criteria = [TestingCriterionAzureAIEvaluator(
                    type="azure_ai_evaluator", name="completeness", evaluator_name=evaluator.name,
                    evaluator_version=evaluator.version, initialization_parameters={"deployment_name": judge, "threshold": THRESHOLD},
                    data_mapping={key: "{{item." + key + "}}" for key in FIELDS[1:]},
                )]
                for name in ("relevance", "groundedness"):
                    fields = ("query", "response") if name == "relevance" else ("query", "response", "context")
                    criteria.append(TestingCriterionAzureAIEvaluator(
                        type="azure_ai_evaluator", name=name, evaluator_name="builtin." + name,
                        evaluator_version=builtin[name]["version"],
                        initialization_parameters={"deployment_name": judge, "threshold": THRESHOLD},
                        data_mapping={key: "{{item." + key + "}}" for key in fields},
                    ))
                report["criteria"] = serializable(criteria)
                time.sleep(5)
                group = client.evals.create(
                    name=f"Contoso {LANGUAGE} instruction comparison",
                    data_source_config={"type": "custom", "item_schema": {
                        "type": "object", "properties": {key: {"type": "string"} for key in FIELDS},
                        "required": list(FIELDS),
                    }, "include_sample_schema": True},
                    testing_criteria=criteria,
                )
                report["eval_id"] = group.id
                persist()
                native = client.evals.runs.create(
                    eval_id=group.id, name=f"Contoso {LANGUAGE} v1-v2 one comparison",
                    data_source={"type": "jsonl", "source": {"type": "file_content", "content": [{"item": row} for row in rows]}},
                )
                report.update(run_id=native.id, status=native.status)
                evidence.append("run_created", native)
                persist()
                print(json.dumps({"eval_id": group.id, "run_id": native.id, "rows": len(rows), "target_reinvocations": 0}), flush=True)
                native, timed_out, monitor_error = wait_for_native(client, group.id, native, evidence)
                report.update(
                    status=native.status, result_counts=serializable(native.result_counts),
                    error=serializable(native.error), timed_out=timed_out, report_url=native.report_url,
                )
                persist()
                if monitor_error is not None:
                    raise RuntimeError("Native monitoring failed; cancellation readback retained.") from monitor_error
                if timed_out:
                    raise RuntimeError("Native comparison exceeded 600 seconds; no rerun is permitted.")
                report["items"] = [serializable(item) for item in client.evals.runs.output_items.list(
                    eval_id=group.id, run_id=native.id, limit=50,
                )]
                evidence.append("native_output_items", report["items"])
                persist()
                report["comparison"] = audit(report, rows, identities)
                evidence.append("audit", report["comparison"])
        except (AzureError, OpenAIError, ValueError, RuntimeError, OSError) as exc:
            evidence.failure(exc)
            report["operation_error"] = {"type": type(exc).__name__, "message": str(exc)}
            raise
        finally:
            report["finished_at"] = datetime.now(timezone.utc).isoformat()
            persist()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=RESULTS / f"instruction-comparison-{LANGUAGE}.json")
    parser.add_argument("--output", type=Path, default=RESULTS / f"instruction-native-{LANGUAGE}.json")
    parser.add_argument("--live", action="store_true", help="Submit one native evaluation over 24 existing answers.")
    args = parser.parse_args()
    if not args.live:
        print(json.dumps({"plan_only": True, "target_calls": 0, "native_runs_if_approved": 1,
                          "rows": 24, "metrics": METRICS, "threshold": THRESHOLD,
                          "native_max_seconds": 600, "cancellation_max_seconds": 90,
                          "optimizer_jobs": 0, "holdout_cases": 0, "quality_release": False}, indent=2))
        return
    if args.output.exists():
        raise ValueError("Native originals already exist; inspect them instead of rerunning the judge.")
    report = evaluate(args.input, args.output)
    print(json.dumps({"status": report["status"], "result_counts": report["result_counts"],
                      "scores": report["comparison"]["scores"], "delta": report["comparison"]["delta"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
