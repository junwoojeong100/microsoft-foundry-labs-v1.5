import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
import instruction_evaluation
import instruction_lab
from evidence import digest


class InstructionNativeTests(unittest.TestCase):
    def fixtures(self, *, improved=True):
        rows, mapping, items = [], {}, []
        for index, version in enumerate(("v1", "v2")):
            for number in range(12):
                identifier = f"opaque-{index}-{number}"
                row = {"id": identifier, "query": f"fixture-{number}",
                       "expected_behavior": "Answer the synthetic question.", "response": "Fixture only.",
                       "context": "Fixture context."}
                rows.append(row)
                mapping[identifier] = {"instructions": version, "case_id": f"fixture-{number}", "response_id": f"fixture-{identifier}"}
                value = 5 if version == "v2" and improved else 3
                items.append({"datasource_item": dict(row), "results": [
                    {"name": name, "score": value, "passed": value >= 4, "status": "completed", "reason": "Local fixture only."}
                    for name in instruction_evaluation.METRICS
                ]})
        native = {"status": "completed", "error": None,
                  "result_counts": {"total": 24, "passed": 12 if improved else 0, "failed": 12 if improved else 24, "errored": 0, "skipped": 0},
                  "items": items}
        return native, rows, mapping

    def test_plan_has_no_cloud_calls_or_added_optimizer_holdout(self):
        stream = io.StringIO()
        with patch.object(sys, "argv", ["instruction_evaluation.py"]), patch("sys.stdout", stream), \
                patch.object(instruction_evaluation, "project_client") as project:
            instruction_evaluation.main()
        result = json.loads(stream.getvalue())
        self.assertEqual(result["target_calls"], 0)
        self.assertEqual(result["native_runs_if_approved"], 1)
        self.assertEqual(result["rows"], 24)
        self.assertEqual(result["metrics"], ["completeness", "relevance", "groundedness"])
        self.assertEqual(result["optimizer_jobs"], 0)
        self.assertEqual(result["holdout_cases"], 0)
        project.assert_not_called()

    def test_audit_uses_native_scores_and_never_calls_this_a_release_pass(self):
        native, rows, mapping = self.fixtures()
        result = instruction_evaluation.audit(native, rows, mapping)
        self.assertEqual(result["scores"]["v1"]["completeness"]["mean"], 3)
        self.assertEqual(result["scores"]["v2"]["completeness"]["mean"], 5)
        self.assertEqual(result["scores"]["v1"]["completeness"]["total"], 12)
        self.assertEqual(result["delta"]["completeness"], 2)
        self.assertFalse(result["quality_release"])
        self.assertFalse(result["judge_control_calibration_performed"])

    def test_tie_remains_a_tie(self):
        result = instruction_evaluation.audit(*self.fixtures(improved=False))
        self.assertEqual(set(result["delta"].values()), {0})
        self.assertEqual(result["scores"]["v2"]["groundedness"]["passed"], 0)

    def test_errored_skipped_partial_or_rewritten_rows_fail_closed(self):
        native, rows, mapping = self.fixtures()
        changed = []
        for key in ("errored", "skipped"):
            item = copy.deepcopy(native)
            item["result_counts"][key] = 1
            changed.append(item)
        item = copy.deepcopy(native)
        item["items"].pop()
        changed.append(item)
        item = copy.deepcopy(native)
        item["items"][0]["datasource_item"]["response"] = "Altered"
        changed.append(item)
        item = copy.deepcopy(native)
        item["items"][0] = item["items"][1]
        changed.append(item)
        for item in changed:
            with self.assertRaises(ValueError):
                instruction_evaluation.audit(item, rows, mapping)

    def test_native_score_verdict_and_reason_must_be_complete_and_consistent(self):
        native, rows, mapping = self.fixtures()
        for change in ({"score": True}, {"score": float("nan")}, {"score": 4.5},
                       {"passed": True}, {"reason": None}, {"status": "error"}):
            item = copy.deepcopy(native)
            item["items"][0]["results"][0].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                instruction_evaluation.audit(item, rows, mapping)

    def test_split_custom_score_and_verdict_entries_are_supported(self):
        native, rows, mapping = self.fixtures()
        metric = native["items"][0]["results"][0]
        native["items"][0]["results"][:1] = [
            {**metric, "metric": "custom_score", "passed": None, "reason": None},
            {**metric, "score": None},
        ]
        result = instruction_evaluation.audit(native, rows, mapping)
        self.assertEqual(result["scores"]["v1"]["completeness"]["mean"], 3)

    def test_preparation_masks_version_labels_and_preserves_identical_inputs(self):
        import hashlib
        sources = {row["id"]: row for row in instruction_evaluation.policy_chunks()}
        cases = instruction_lab.cases()
        raw = json.dumps({"answer": "Fixture only.", "citation_ids": [next(iter(sources))]})
        rows = [{
            "id": case["id"], "instructions": version, "status": "completed",
            "model": "fixture", "query": case["query"], "raw_answer": raw,
            "response_id": f"fixture-{version}-{case['id']}",
            "input_sha256": digest(instruction_lab.model_input(case, sources)),
            "usage": None, "latency_seconds": 0.0,
            "checklist": instruction_lab.score(raw, case, sources),
        } for case in cases for version in ("v1", "v2")]
        report = {
            "language": instruction_evaluation.LANGUAGE, "status": "completed", "execution_location": "azure_model",
            "cases_sha256": digest(cases), "context_sha256": digest(sources), "rows": rows,
            "comparison": instruction_lab.summarize(rows, cases),
            "reasoning_effort": "low", "max_output_tokens": 2048, "retries": 0,
            "case_file_sha256": hashlib.sha256(
                (instruction_evaluation.DATA / "evaluation/instruction-comparison.json").read_bytes()
            ).hexdigest(),
            "rubric_sha256": hashlib.sha256(instruction_evaluation.RUBRIC.read_bytes()).hexdigest(),
            "shared_wrapper": {
                "output_schema_sha256": digest(instruction_lab.answer_format(list(sources))),
                "version_specific_guidance_in_wrapper": False,
                "target_input_contains_case_criteria_or_reference_answers": False,
            },
            "instructions_sha256": {f"v{v}": hashlib.sha256((instruction_evaluation.DATA / f"prompts/agent-v{v}.txt").read_bytes()).hexdigest()
                                    for v in (1, 2)},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(report))
            _, native_rows, mapping = instruction_evaluation.prepare(path)
            self.assertEqual(len(native_rows), 24)
            for row in native_rows:
                self.assertEqual(set(row), {"id", "query", "expected_behavior", "response", "context"})
                self.assertNotIn("v1", row["id"])
                self.assertNotIn("v2", row["id"])
                self.assertTrue(row["expected_behavior"].startswith("- "))
                self.assertIn(mapping[row["id"]]["instructions"], {"v1", "v2"})
                self.assertNotIn(mapping[row["id"]]["instructions"], row["expected_behavior"])
            report["instructions_sha256"]["v2"] = "changed"
            path.write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError, "Instructions changed"):
                instruction_evaluation.prepare(path)

    def test_preparation_requires_each_prompt_answer_to_use_its_pinned_agent_version(self):
        import hashlib
        sources = {row["id"]: row for row in instruction_evaluation.policy_chunks()}
        cases = instruction_lab.cases()
        raw = json.dumps({"answer": "Fixture only.", "citation_ids": [next(iter(sources))]})
        versions = {"v1": "1", "v2": "2"}
        agent_name = "contoso-instruction-eval-fixture"
        rows = [{
            "id": case["id"], "instructions": version, "status": "completed",
            "model": "gpt-6-sol", "query": case["query"], "raw_answer": raw,
            "response_id": f"fixture-{version}-{case['id']}",
            "input_sha256": digest(instruction_lab.model_input(case, sources)),
            "usage": None, "latency_seconds": 0.0,
            "checklist": instruction_lab.score(raw, case, sources),
            "agent_name": agent_name, "agent_version": versions[version],
        } for case in cases for version in ("v1", "v2")]
        report = {
            "schema": "contoso-instruction-prompt-agent-comparison",
            "language": instruction_evaluation.LANGUAGE, "status": "completed",
            "execution_location": "azure_prompt_agent",
            "cases_sha256": digest(cases), "context_sha256": digest(sources), "rows": rows,
            "comparison": instruction_lab.summarize(rows, cases),
            "reasoning_effort": "low", "max_output_tokens": 2048, "retries": 0,
            "model_identity": {"name": "contoso-gpt-6-sol", "modelName": "gpt-6-sol", "modelVersion": "2026-09-22"},
            "prompt_agent_versions": {"agent_name": agent_name, "versions": versions, "status": "active"},
            "case_file_sha256": hashlib.sha256(
                (instruction_evaluation.DATA / "evaluation/instruction-comparison.json").read_bytes()
            ).hexdigest(),
            "rubric_sha256": hashlib.sha256(instruction_evaluation.RUBRIC.read_bytes()).hexdigest(),
            "shared_wrapper": {
                "output_schema_sha256": digest(instruction_lab.answer_format(list(sources))),
                "version_specific_guidance_in_wrapper": False,
                "target_input_contains_case_criteria_or_reference_answers": False,
            },
            "instructions_sha256": {
                f"v{v}": hashlib.sha256(
                    (instruction_evaluation.DATA / f"prompts/agent-v{v}.txt").read_bytes()
                ).hexdigest() for v in (1, 2)
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "prompt-agent.json"
            path.write_text(json.dumps(report))
            _, native_rows, identities = instruction_evaluation.prepare(path)
            self.assertEqual(len(native_rows), 24)
            self.assertEqual({item["instructions"] for item in identities.values()}, {"v1", "v2"})
            report["rows"][0]["agent_version"] = "2"
            path.write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError, "not pinned"):
                instruction_evaluation.prepare(path)

    def test_existing_native_result_is_not_overwritten_or_rejudged(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "native.json"
            path.write_text('{"preserved":true}')
            with patch.object(sys, "argv", ["instruction_evaluation.py", "--live", "--output", str(path)]), \
                    patch.object(instruction_evaluation, "evaluate") as evaluate, self.assertRaisesRegex(ValueError, "instead of rerunning"):
                instruction_evaluation.main()
            evaluate.assert_not_called()
            self.assertEqual(path.read_text(), '{"preserved":true}')

    def test_sdk_prompt_requires_the_actual_numeric_result_contract(self):
        prompt = instruction_evaluation.RUBRIC.read_text()
        self.assertIn('integer "result" from 1 through 5', prompt)
        self.assertIn('string "reason"', prompt)

    def test_failed_numeric_result_is_not_zero_or_an_improvement(self):
        native, rows, identities = self.fixtures()
        native["items"][0]["results"][0].update(
            score=None, passed=False, reason="Please provide a valid evaluator. Invalid or missing numeric result",
        )
        with self.assertRaisesRegex(ValueError, "Incomplete or contradictory"):
            instruction_evaluation.audit(native, rows, identities)
        result = instruction_evaluation.audit(native, rows, identities, metric_names=("relevance", "groundedness"))
        self.assertNotIn("completeness", result["scores"]["v1"])
        self.assertFalse(result["quality_release"])


if __name__ == "__main__":
    unittest.main()
