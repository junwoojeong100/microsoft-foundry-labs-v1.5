"""Fixed native evaluation, explicit calibration controls, and immutable dev/holdout lineage."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time
from uuid import uuid4

from cloud import project_client
from evidence import Evidence, digest, serializable
from business_checks import check_business_evidence
from evaluation_data import DEFAULT_SUITE, SUITES, calibration_cases, load_cases, policy, suite_hash
from workshop import DATA, RESULTS, config_values, load_jsonl, save_json, validate_data

STATE = RESULTS / "native-evaluation.json"
FIELDS = ("id", "query", "response", "ground_truth", "expected_behavior", "evidence")


def settings_hash(suite: str = DEFAULT_SUITE) -> str:
    return digest({
        "suite": suite, "suite_sha256": suite_hash(suite),
        "judge": hashlib.sha256((DATA / "evaluation/judge.txt").read_bytes()).hexdigest(),
        "pass_threshold": 4, "gate": 0.9, "critical_failure_tolerance": 0,
    })


def prepare_rows(path: Path, split: str, suite: str = "legacy-v1") -> list[dict]:
    expected = {c["id"]: c for c in load_cases(suite, split)}
    rows = load_jsonl(path)
    if len(rows) != len(expected) or {r.get("id") for r in rows} != set(expected):
        raise ValueError("Partial, duplicate or mismatched split cannot be evaluated as complete.")
    items = []
    for row in rows:
        if row.get("status") != "completed" or not row.get("response", "").strip() or not row.get("response_id"):
            raise ValueError(f"{row.get('id')}: missing completed, real response evidence.")
        case = expected[row["id"]]
        if row.get("query") != case["query"]:
            raise ValueError("Actual question differs from the frozen dataset.")
        if suite != "legacy-v1" and (
            row.get("evaluation_suite") != suite or row.get("evaluation_suite_sha256") != suite_hash(suite)
        ):
            raise ValueError("Response evidence belongs to another evaluation suite.")
        evidence = {key: row.get(key) for key in ("tool_calls", "tool_definitions", "citations", "context", "retrieved_sources", "response_ids", "trace_id", "configuration", "contract", "raw_answer", "raw_attribution", "attribution_response_id", "grounding_contract")}
        items.append({
            "id": row["id"], "query": row["query"], "response": row["response"],
            "ground_truth": case["ground_truth"], "expected_behavior": case["expected_behavior"],
            "evidence": json.dumps(evidence, ensure_ascii=False),
            "automatic_checks": check_business_evidence(row, case, require_tool_definitions=suite == "automated-v3") if suite != "legacy-v1" else None,
        })
    return items


def setup(project, client, endpoint: str, model: str, evidence: Evidence, suite: str) -> dict:
    from azure.ai.projects.models import TestingCriterionAzureAIEvaluator

    judge = config_values()["FOUNDRY_JUDGE_DEPLOYMENT_NAME"]
    if not judge or judge == model:
        raise ValueError("Use an explicit judge deployment distinct from the target.")
    state_path = STATE if suite == "legacy-v1" else RESULTS / f"native-evaluation-{suite}.json"
    if state_path.exists():
        state = json.loads(state_path.read_text())
        if state["endpoint"] != endpoint or state["settings_hash"] != settings_hash(suite) or state["judge"] != judge:
            raise ValueError("Evaluation configuration drift. Preserve the old evaluation and start an explicit new experiment.")
        remote = project.beta.evaluators.get_version(state["evaluator_name"], state["evaluator_version"])
        if digest(remote.definition.as_dict()) != state["definition_hash"]:
            raise ValueError("Remote evaluator definition drift.")
        return state
    name = "contoso-business-" + uuid4().hex[:8]
    definition = {
        "type": "prompt", "prompt_text": (DATA / "evaluation/judge.txt").read_text(encoding="utf-8"),
        "init_parameters": {"type": "object", "properties": {
            "deployment_name": {"type": "string"}, "threshold": {"type": "number"},
        }, "required": ["deployment_name", "threshold"]},
        "data_schema": {"type": "object", "properties": {key: {"type": "string"} for key in FIELDS if key != "id"},
                        "required": [key for key in FIELDS if key != "id"]},
        "metrics": {"business": {"type": "ordinal", "min_value": 1, "max_value": 5,
                                "desirable_direction": "increase", "threshold": 4}},
    }
    evaluator = project.beta.evaluators.create_version(name=name, evaluator_version={
        "name": name, "evaluator_type": "custom", "categories": ["quality"],
        "display_name": "Contoso purchasing evidence judge", "definition": definition,
    })
    evidence.append("evaluator_created", evaluator)
    state = {
        "endpoint": endpoint, "judge": judge, "suite": suite, "settings_hash": settings_hash(suite),
        "evaluator_name": evaluator.name, "evaluator_version": evaluator.version,
        "definition_hash": digest(evaluator.definition.as_dict()),
    }
    save_json(state_path, state)
    criteria = [
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator", name="contoso_business", evaluator_name=evaluator.name,
            initialization_parameters={"deployment_name": judge, "threshold": 4},
            data_mapping={key: "{{item." + key + "}}" for key in FIELDS if key != "id"},
        ),
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator", name="relevance", evaluator_name="builtin.relevance",
            initialization_parameters={"deployment_name": judge, "threshold": 3},
            data_mapping={"query": "{{item.query}}", "response": "{{item.response}}"},
        ),
    ]
    evaluation = client.evals.create(
        name="Contoso fixed business and relevance evaluation",
        data_source_config={"type": "custom", "item_schema": {
            "type": "object", "properties": {key: {"type": "string"} for key in FIELDS}, "required": list(FIELDS),
        }, "include_sample_schema": True},
        testing_criteria=criteria,
    )
    state["eval_id"] = evaluation.id
    state["criteria"] = serializable(criteria)
    save_json(state_path, state)
    evidence.append("evaluation_created", evaluation)
    return state


def audit_items(
    items: list[dict], expected: dict[str, bool] | None = None, *,
    suite: str = "legacy-v1", automatic_checks: dict[str, dict] | None = None, split: str | None = None,
) -> dict:
    verdicts, contradictions = {}, []
    for item in items:
        case_id = item.get("datasource_item", {}).get("id")
        if not case_id or case_id in verdicts:
            raise ValueError("Native result is missing a unique datasource case ID.")
        results = item.get("results") or []
        business = [r for r in results if r.get("name") == "contoso_business"]
        if any(r.get("status") == "error" or (r.get("sample") or {}).get("error") for r in business):
            raise ValueError(f"{case_id}: evaluator execution error; partial results cannot pass.")
        scores = [r for r in business if isinstance(r.get("score"), (int, float)) and not isinstance(r.get("score"), bool)]
        details = [r for r in business if type(r.get("passed")) is bool]
        if len(scores) != 1 or len(details) != 1:
            raise ValueError(f"{case_id}: missing unambiguous native score/verdict.")
        result = details[0]
        score, passed = scores[0]["score"], result["passed"]
        if isinstance(score, bool) or not isinstance(score, (int, float)) or score not in {1, 2, 3, 4, 5} or type(passed) is not bool:
            raise ValueError(f"{case_id}: judge result missing a valid ordinal score and boolean passed.")
        if passed != (score >= 4):
            contradictions.append(case_id)
        checks = None if automatic_checks is None else automatic_checks.get(case_id)
        if suite != "legacy-v1" and expected is None and checks is None:
            raise ValueError(f"{case_id}: automated evidence checks are required.")
        verdicts[case_id] = {
            "passed": passed and (checks is None or checks["passed"]), "native_passed": passed,
            "score": score, "reason": result.get("reason"), "raw_result": business, "automatic_checks": checks,
        }
    report = {
        "judge_verdicts": verdicts, "contradictions": contradictions,
        "human_review_completed": False, "business_gate_passed": False,
        "evaluation_suite": suite,
        "human_review_required": suite == "legacy-v1",
        "human_review_status": "optional_guidance_only" if suite != "legacy-v1" else "not_performed",
    }
    if expected is not None:
        if set(verdicts) != set(expected):
            raise ValueError("Calibration controls are incomplete.")
        mismatches = [case_id for case_id in expected if verdicts[case_id]["passed"] != expected[case_id]]
        report.update(type="judge_control_calibration", mismatches=mismatches,
                      calibration_passed=not mismatches and not contradictions,
                      not_target_agent_evidence=True)
    else:
        if suite != "legacy-v1" and split not in {"dev", "holdout"}:
            raise ValueError("Automated native audit requires an explicit split.")
        cases = {c["id"]: c for c in load_cases(suite, split)}
        if not verdicts or not set(verdicts) <= cases.keys():
            raise ValueError("No valid business-case results.")
        rubric = policy(suite)
        critical = [key for key, value in verdicts.items() if not value["passed"] and cases[key]["category"] in rubric["zero_tolerance_categories"]]
        integrity_failures = [
            key for key, value in verdicts.items()
            if value["automatic_checks"] and set(value["automatic_checks"]["failures"]) - {
                "required_policy_evidence", "required_tool_execution", "unrequested_tool_execution", "tool_arguments"
            }
        ]
        rate = sum(v["passed"] for v in verdicts.values()) / len(verdicts)
        report.update(type="native_business_judge", pass_rate=rate, critical_failures=critical,
                      evidence_integrity_failures=integrity_failures,
                      business_gate_passed=rate >= rubric["minimum_pass_rate"] and not critical and not contradictions and not integrity_failures)
    return report


def run(args, evidence: Evidence) -> None:
    if args.command == "calibrate":
        controls = calibration_cases(args.suite)
        rows = [{key: row[key] for key in FIELDS} for row in controls]
        expected = {row["id"]: row["expected_pass"] for row in controls}
    else:
        if not args.input or not args.split:
            raise ValueError("run requires --input and --split dev|holdout.")
        rows, expected = prepare_rows(args.input, args.split, args.suite), None
    with project_client(evidence) as (project, _, endpoint, model), project.get_openai_client(max_retries=0, timeout=60) as client:
        state = setup(project, client, endpoint, model, evidence, args.suite)
        if "eval_id" not in state:
            raise RuntimeError("Previous native setup is partial. Inspect its receipt before starting a new evaluation.")
        evidence.append("submitted_ids", {"ids": [r["id"] for r in rows], "settings_hash": state["settings_hash"],
                                           "source_sha256": digest(rows), "purpose": args.command, "split": args.split})
        native = client.evals.runs.create(
            eval_id=state["eval_id"], name=evidence.run_id,
            data_source={"type": "jsonl", "source": {"type": "file_content", "content": [
                {"item": {key: row[key] for key in FIELDS}} for row in rows
            ]}},
        )
        evidence.append("run_created", native)
        receipt_path = RESULTS / (evidence.run_id + ".json")
        save_json(receipt_path, {"eval_id": state["eval_id"], "run_id": native.id, "status": native.status})
        deadline = time.monotonic() + 600
        while native.status not in {"completed", "failed", "canceled", "cancelled"} and time.monotonic() < deadline:
            time.sleep(10)
            native = client.evals.runs.retrieve(eval_id=state["eval_id"], run_id=native.id)
            evidence.append("run_status", native)
        if native.status not in {"completed", "failed", "canceled", "cancelled"}:
            evidence.append("cancel_requested", client.evals.runs.cancel(eval_id=state["eval_id"], run_id=native.id))
            raise RuntimeError("Native evaluation time limit reached; cancellation requested, verify terminal state.")
        items = [serializable(item) for item in client.evals.runs.output_items.list(eval_id=state["eval_id"], run_id=native.id)]
        evidence.append("native_output_items", items)
        save_json(receipt_path, {"eval_id": state["eval_id"], "run_id": native.id, "status": native.status, "items": items})
        if native.status != "completed" or len(items) != len(rows):
            raise RuntimeError("Native evaluation failed or returned partial results; originals retained.")
        checks = {row["id"]: row["automatic_checks"] for row in rows} if args.command != "calibrate" and args.suite != "legacy-v1" else None
        audit = audit_items(items, expected, suite=args.suite, automatic_checks=checks, split=args.split)
        save_json(RESULTS / (evidence.run_id + "-audit.json"), audit)
        evidence.append("audit", audit)
        print(json.dumps(audit, ensure_ascii=False, indent=2))
        if audit["contradictions"] or expected is not None and not audit["calibration_passed"]:
            raise RuntimeError("Judge audit failed; do not lower the threshold or claim target quality.")
        if expected is None and not audit["business_gate_passed"]:
            raise RuntimeError("Business gate failed; original results and fixed thresholds are retained.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "calibrate", "run"])
    parser.add_argument("--input", type=Path)
    parser.add_argument("--split", choices=["dev", "holdout"])
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--suite", choices=SUITES, default=DEFAULT_SUITE)
    parser.add_argument("--new-experiment", action="store_true", help="Archive the local binding; retain the remote evaluation and all prior results.")
    args = parser.parse_args()
    if args.command == "prepare":
        if not args.input or not args.split:
            raise ValueError("prepare requires --input and --split.")
        rows = prepare_rows(args.input, args.split, args.suite)
        print(json.dumps({"rows": len(rows), "source_sha256": digest(rows), "settings_hash": settings_hash(args.suite),
                          "evidence_failures": [r["id"] for r in rows if r.get("automatic_checks") and not r["automatic_checks"]["passed"]]}))
        return
    if not args.live:
        print(f"PLAN ONLY: native {args.command}. Calibration controls are not target-agent results.")
        return
    state_path = STATE if args.suite == "legacy-v1" else RESULTS / f"native-evaluation-{args.suite}.json"
    if args.new_experiment and state_path.exists():
        archived = state_path.with_name("native-evaluation-history-" + uuid4().hex[:8] + ".json")
        state_path.rename(archived)
        print(f"Previous evaluation binding retained: {archived.name}")
    evidence = Evidence("native-" + args.command)
    try:
        run(args, evidence)
    except (ValueError, RuntimeError, OSError) as exc:
        evidence.failure(exc)
        raise
    finally:
        print(f"Evidence: {evidence.path}")


if __name__ == "__main__":
    main()
