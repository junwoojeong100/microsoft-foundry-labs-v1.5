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
from evaluation_data import DEFAULT_SUITE, SUITES, calibration_cases, load_cases, policy, suite_hash, verify_development_freeze
from lab_profile import validation_for
from workshop import DATA, LANGUAGE, RESULTS, ROOT, config_values, load_jsonl, save_json, validate_data

STATE = RESULTS / "native-evaluation.json"
FIELDS = ("id", "query", "response", "ground_truth", "expected_behavior", "evidence")


def settings_hash(suite: str = DEFAULT_SUITE) -> str:
    return digest({
        "suite": suite, "suite_sha256": suite_hash(suite),
        "judge": hashlib.sha256((DATA / "evaluation/judge.txt").read_bytes()).hexdigest(),
        "pass_threshold": 4, "gate": 0.9, "critical_failure_tolerance": 0,
    })


def prepare_rows(path: Path, split: str, suite: str = "legacy-v1") -> list[dict]:
    if suite == "automated-v5" and split == "holdout":
        verify_gate(suite, "dev")
    expected = {c["id"]: c for c in load_cases(suite, split)}
    rows = load_jsonl(path)
    if len(rows) != len(expected) or {r.get("id") for r in rows} != set(expected):
        raise ValueError("Partial, duplicate or mismatched split cannot be evaluated as complete.")
    items = []
    for row in rows:
        if row.get("status") != "completed" or not row.get("response", "").strip() or not row.get("response_id"):
            raise ValueError(f"{row.get('id')}: missing completed, real response evidence.")
        if suite == "automated-v5" and row.get("tool_authorization_contract") != "explicit-request-v2":
            raise ValueError("New v5 evidence must be explicit-request-v2; v1 is historical replay only.")
        case = expected[row["id"]]
        if row.get("query") != case["query"]:
            raise ValueError("Actual question differs from the frozen dataset.")
        if suite.startswith("automated-") and (
            row.get("evaluation_suite") != suite or row.get("evaluation_suite_sha256") != suite_hash(suite)
        ):
            raise ValueError("Response evidence belongs to another evaluation suite.")
        evidence = {key: row.get(key) for key in ("tool_calls", "tool_definitions", "citations", "context", "retrieved_sources", "response_ids", "trace_id", "configuration", "contract", "raw_answer", "raw_attribution", "attribution_response_id", "grounding_contract", "tool_authorization_contract", "request_permissions", "required_policy_citations")}
        items.append({
            "id": row["id"], "query": row["query"], "response": row["response"],
            "ground_truth": case["ground_truth"], "expected_behavior": case["expected_behavior"],
            "evidence": json.dumps(evidence, ensure_ascii=False),
            "automatic_checks": check_business_evidence(
                row, case, require_tool_definitions=suite in {"automated-v3", "automated-v4", "automated-v5"},
                require_tool_authorization=suite in {"automated-v4", "automated-v5"},
                expected_authorization_contract="explicit-request-v2" if suite == "automated-v5" else None,
            ) if suite.startswith("automated-") else None,
        })
    return items


def setup(project, client, endpoint: str, model: str, evidence: Evidence, suite: str) -> dict:
    from azure.ai.projects.models import TestingCriterionAzureAIEvaluator
    from openai import NotFoundError

    judge = config_values()["FOUNDRY_JUDGE_DEPLOYMENT_NAME"]
    if not judge or judge == model:
        raise ValueError("Use an explicit judge deployment distinct from the target.")
    state_path = STATE if suite == "legacy-v1" else RESULTS / f"native-evaluation-{suite}.json"
    binding_path = validation_for(ROOT) / suite / "evaluation-binding.json"
    if not state_path.exists() and binding_path.exists():
        binding = json.loads(binding_path.read_text())
        if binding["environment_sha256"] == digest(endpoint):
            if binding["settings_hash"] != settings_hash(suite) or binding["judge"] != judge:
                raise ValueError("Shared evaluator binding differs from the frozen suite/judge; preserve it and start a new experiment.")
            save_json(state_path, {**binding, "endpoint": endpoint})
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
    for attempt in range(3):
        try:
            evaluation = client.evals.create(
                name="Contoso English business and relevance evaluation" if LANGUAGE == "en" else "Contoso fixed business and relevance evaluation",
                data_source_config={"type": "custom", "item_schema": {
                    "type": "object", "properties": {key: {"type": "string"} for key in FIELDS}, "required": list(FIELDS),
                }, "include_sample_schema": True},
                testing_criteria=criteria,
            )
            break
        except NotFoundError as exc:
            evidence.failure(exc)
            if evaluator.name not in str(exc) or "evaluator" not in str(exc).lower() or attempt == 2:
                raise
            time.sleep(5)
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
        if suite == "automated-v5" and any(
            result.get("status") in {"error", "errored", "skipped", "failed"}
            or result.get("error") or (result.get("sample") or {}).get("error")
            for result in results
        ):
            raise ValueError(f"{case_id}: evaluator execution error or skipped result; no complete gate.")
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
        if suite.startswith("automated-") and expected is None and checks is None:
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
        "quality_release": False if suite == "basic-learning" else None,
        "learning_only": suite == "basic-learning",
    }
    if expected is not None:
        if set(verdicts) != set(expected):
            raise ValueError("Calibration controls are incomplete.")
        mismatches = [case_id for case_id in expected if verdicts[case_id]["passed"] != expected[case_id]]
        report.update(type="judge_control_calibration", mismatches=mismatches,
                      calibration_passed=not mismatches and not contradictions,
                      not_target_agent_evidence=True)
    else:
        if suite.startswith("automated-") and split not in {"dev", "holdout"}:
            raise ValueError("Automated native audit requires an explicit split.")
        cases = {c["id"]: c for c in load_cases(suite, split)}
        if not verdicts or not set(verdicts) <= cases.keys():
            raise ValueError("No valid business-case results.")
        if suite.startswith("automated-") and set(verdicts) != cases.keys():
            raise ValueError("Native business-case results are incomplete; a partial split cannot pass.")
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


def check_native_completeness(native: dict, expected: int) -> None:
    counts = native.get("result_counts") or {}
    if (
        native.get("status") != "completed" or native.get("error")
        or counts.get("total") != expected or counts.get("errored") != 0 or counts.get("skipped", 0) != 0
        or any(type(counts.get(key)) is not int for key in ("passed", "failed", "errored", "total"))
        or counts.get("passed", 0) + counts.get("failed", 0) != expected
        or len(native.get("items", [])) != expected
    ):
        raise ValueError("Native run has missing, errored, skipped or inconsistent rows; original results are retained.")


def gate_receipt(suite: str, stage: str) -> Path:
    if suite != "automated-v5" or stage not in {"calibration", "dev"}:
        raise ValueError("A v5 gate receipt requires calibration or dev.")
    local = RESULTS / f"{suite}-{stage}-gate.json"
    shared = validation_for(ROOT) / suite / f"{stage}-gate.json"
    return shared if not local.exists() and shared.exists() else local


def verify_gate(suite: str, stage: str) -> dict:
    """Recheck preserved originals, not just a success flag, before opening the exam."""
    receipt = json.loads(gate_receipt(suite, stage).read_text(encoding="utf-8"))
    if receipt.get("suite_sha256") != suite_hash(suite) or receipt.get("settings_hash") != settings_hash(suite):
        raise ValueError("Gate belongs to a different frozen suite or judge.")
    if receipt.get("judge") != config_values()["FOUNDRY_JUDGE_DEPLOYMENT_NAME"]:
        raise ValueError("Judge deployment changed after calibration; holdout remains unopened.")
    native_path = (ROOT / receipt["native_path"]).resolve()
    if not any(native_path.is_relative_to(directory.resolve())
               for directory in (RESULTS, validation_for(ROOT) / suite)):
        raise ValueError("Gate native evidence must remain inside the owned results or suite evidence directory.")
    native = json.loads(native_path.read_text(encoding="utf-8"))
    if digest(native) != receipt["native_sha256"]:
        raise ValueError("Gate native originals changed.")
    if stage == "calibration":
        expected = {row["id"]: row["expected_pass"] for row in calibration_cases(suite)}
        check_native_completeness(native, len(expected))
        audit = audit_items(native["items"], expected, suite=suite)
        if not audit["calibration_passed"]:
            raise ValueError("All eight judge controls must pass before target collection.")
    else:
        calibration = verify_gate(suite, "calibration")
        if any(calibration[key] != receipt[key] for key in ("environment_sha256", "judge", "definition_hash", "eval_id")):
            raise ValueError("Dev and calibration environments or native judges differ.")
        source = (ROOT / receipt["input_path"]).resolve()
        if not source.is_relative_to(ROOT.resolve()):
            raise ValueError("Dev gate input escaped the checked-out experiment.")
        if hashlib.sha256(source.read_bytes()).hexdigest() != receipt["input_sha256"]:
            raise ValueError("Dev originals changed after native evaluation.")
        rows = prepare_rows(source, "dev", suite)
        check_native_completeness(native, len(rows))
        audit = audit_items(native["items"], suite=suite, split="dev",
                            automatic_checks={row["id"]: row["automatic_checks"] for row in rows})
        if not audit["business_gate_passed"]:
            raise ValueError("A complete calibrated dev pass is required; holdout remains unopened.")
        if target_configuration(load_jsonl(source)) != receipt["configuration"]:
            raise ValueError("Dev runtime or environment differs from its gate receipt.")
    return receipt


def target_configuration(rows: list[dict]) -> dict:
    configurations = [{
        "environment_sha256": row.get("environment_sha256"), "hosted_version": row.get("hosted_version"),
        "runtime_sha256": row.get("contract", {}).get("sha256"),
        "effective_prompt_sha256": row.get("effective_prompt_sha256"),
        "model": row.get("model"), "model_deployment": row.get("model_deployment"),
    } for row in rows]
    if (not configurations or any(row.get("execution_location") != "azure" for row in rows)
            or any(not all(value.values()) for value in configurations)
            or any(value != configurations[0] for value in configurations)):
        raise ValueError("A release gate needs one complete, consistent actual Azure candidate, not local/fixture evidence.")
    return configurations[0]


def wait_for_native(client, evaluation: str, native, evidence: Evidence):
    from openai import OpenAIError

    terminal = {"completed", "failed", "canceled", "cancelled"}
    deadline = time.monotonic() + 600
    monitor_error = None
    try:
        while native.status not in terminal:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(10, remaining))
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            native = client.evals.runs.retrieve(eval_id=evaluation, run_id=native.id, timeout=min(60, remaining))
            evidence.append("run_status", native)
    except (OpenAIError, OSError) as exc:
        evidence.failure(exc)
        monitor_error = exc
    if native.status in terminal:
        return native, False, None
    deadline = time.monotonic() + 90
    try:
        evidence.append("cancel_requested", client.evals.runs.cancel(eval_id=evaluation, run_id=native.id, timeout=30))
    except (OpenAIError, OSError) as exc:
        evidence.failure(exc)
    for attempt in range(6):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        native = client.evals.runs.retrieve(eval_id=evaluation, run_id=native.id, timeout=min(30, remaining))
        evidence.append("cancel_status", native)
        if native.status in terminal:
            return native, monitor_error is None, monitor_error
        if attempt < 5:
            time.sleep(min(5, max(0, deadline - time.monotonic())))
    raise RuntimeError("Native evaluation cancellation unconfirmed within 90 seconds; exact run may still be active.")


def run(args, evidence: Evidence) -> None:
    if args.suite == "automated-v5":
        verify_development_freeze(args.suite)
        if args.command != "calibrate":
            verify_gate(args.suite, "calibration" if args.split == "dev" else "dev")
    if args.command == "calibrate":
        controls = calibration_cases(args.suite)
        rows = [{key: row[key] for key in FIELDS} for row in controls]
        expected = {row["id"]: row["expected_pass"] for row in controls}
    else:
        if not args.input or not args.split:
            raise ValueError("run requires --input and --split dev|holdout.")
        rows, expected = prepare_rows(args.input, args.split, args.suite), None
    with project_client(evidence) as (project, _, endpoint, model), project.get_openai_client(max_retries=0, timeout=60) as client:
        if args.suite == "automated-v5":
            stage = "calibration" if args.command == "calibrate" else args.split
            marker = RESULTS / f"native-{suite_hash(args.suite)[:16]}-{stage}-attempt.json"
            with marker.open("x", encoding="utf-8") as handle:
                json.dump({"run_id": evidence.run_id, "stage": stage, "purpose": "single native attempt; no resampling"}, handle)
            if args.command != "calibrate":
                if target_configuration(load_jsonl(args.input))["environment_sha256"] != digest(endpoint):
                    raise ValueError("Native judge and actual target evidence belong to different projects.")
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
        native, timed_out, monitor_error = wait_for_native(client, state["eval_id"], native, evidence)
        result = {
            "eval_id": state["eval_id"], "run_id": native.id, "status": native.status,
            "result_counts": serializable(native.result_counts), "error": serializable(native.error),
            "timed_out": timed_out,
            "monitor_error": None if monitor_error is None else {
                "type": type(monitor_error).__name__, "message": str(monitor_error),
            },
        }
        save_json(receipt_path, result)
        if monitor_error is not None:
            raise RuntimeError("Native polling failed; the terminal cancellation readback is retained.") from monitor_error
        if timed_out:
            raise RuntimeError("Native evaluation reached its 600-second limit; terminal cancellation readback retained.")
        items = [serializable(item) for item in client.evals.runs.output_items.list(eval_id=state["eval_id"], run_id=native.id)]
        evidence.append("native_output_items", items)
        result["items"] = items
        save_json(receipt_path, result)
        if args.suite == "automated-v5":
            check_native_completeness(result, len(rows))
        if native.status != "completed" or len(items) != len(rows):
            raise RuntimeError("Native evaluation failed or returned partial results; originals retained.")
        checks = {row["id"]: row["automatic_checks"] for row in rows} if args.command != "calibrate" and args.suite.startswith("automated-") else None
        audit = audit_items(items, expected, suite=args.suite, automatic_checks=checks, split=args.split)
        save_json(RESULTS / (evidence.run_id + "-audit.json"), audit)
        evidence.append("audit", audit)
        print(json.dumps(audit, ensure_ascii=False, indent=2))
        if audit["contradictions"] or expected is not None and not audit["calibration_passed"]:
            raise RuntimeError("Judge audit failed; do not lower the threshold or claim target quality.")
        if expected is None and not audit["business_gate_passed"]:
            raise RuntimeError("Business gate failed; original results and fixed thresholds are retained.")
        if args.suite == "automated-v5" and (expected is not None or args.split == "dev"):
            stage = "calibration" if expected is not None else "dev"
            receipt = {
                "suite_sha256": suite_hash(args.suite), "settings_hash": settings_hash(args.suite),
                "environment_sha256": digest(endpoint), "native_path": receipt_path.relative_to(ROOT).as_posix(),
                "native_sha256": digest(result), "eval_id": state["eval_id"], "run_id": native.id,
                "judge": state["judge"], "definition_hash": state["definition_hash"],
            }
            if stage == "dev":
                receipt.update(
                    input_path=args.input.resolve().relative_to(ROOT).as_posix(),
                    input_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),
                    configuration=target_configuration(load_jsonl(args.input)),
                )
            with gate_receipt(args.suite, stage).open("x", encoding="utf-8") as handle:
                json.dump(receipt, handle, indent=2)


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
