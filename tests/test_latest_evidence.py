import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "validation/current"
sys.path.insert(0, str(ROOT / "samples"))
from evidence import digest
from instruction_evaluation import audit


def record(name):
    return json.loads((DIRECTORY / name).read_text(encoding="utf-8"))


class LatestEvidenceTests(unittest.TestCase):
    def test_actual_gpt6_measurement_is_complete_but_not_an_improvement(self):
        report = record("report.json")
        self.assertEqual(report["target_model"], "gpt-6-sol")
        self.assertEqual(report["target_model_version"], "2026-09-22")
        self.assertEqual(report["status"], "measured_no_observed_v2_improvement")
        self.assertEqual(report["target_calls"], 12)
        self.assertEqual(report["native_runs"], 4)
        self.assertFalse(report["target_resampling"])
        self.assertFalse(report["quality_release"])
        for language, expected in (("ko", 9), ("en", 8)):
            row = report["languages"][language]
            self.assertEqual(row["target_response_count"], 6)
            self.assertEqual(row["target_collection_attempts"], 1)
            self.assertEqual(row["local_checklist"]["scores"], {"v1": expected, "v2": expected})
            self.assertEqual(row["local_checklist"]["delta"], 0)
            self.assertFalse(row["v2_measured_improvement"])
            self.assertEqual(set(row["native_delta"].values()), {0})

    def test_exact_prompt_and_case_inputs_remain_bound_to_original_responses(self):
        current = record("instructions.json")
        self.assertTrue(current["v2_live_comparison_completed"])
        self.assertFalse(current["v2_live_improvement_established"])
        self.assertFalse(current["score_improvement_guaranteed"])
        for language in ("ko", "en"):
            data = ROOT / "data" / ("en" if language == "en" else "")
            responses = record(f"{language}/responses.json")
            self.assertEqual(responses["status"], "completed")
            self.assertEqual(responses["language"], language)
            self.assertEqual(responses["model_deployment"], "contoso-gpt-6-sol")
            self.assertEqual(responses["reasoning_effort"], "low")
            self.assertEqual(responses["max_output_tokens"], 2048)
            self.assertEqual(len(responses["rows"]), 6)
            cases = json.loads((data / "evaluation/instruction-comparison.json").read_text())["cases"]
            self.assertEqual(responses["cases_sha256"], digest(cases))
            for version in ("v1", "v2"):
                self.assertEqual(hashlib.sha256((data / f"prompts/agent-{version}.txt").read_bytes()).hexdigest(),
                                 responses["instructions_sha256"][version])
            for case in cases:
                pair = [row for row in responses["rows"] if row["id"] == case["id"]]
                self.assertEqual({row["instructions"] for row in pair}, {"v1", "v2"})
                self.assertEqual({row["query"] for row in pair}, {case["query"]})
                self.assertEqual(len({row["input_sha256"] for row in pair}), 1)
                self.assertEqual(len({row["response_id"] for row in pair}), 2)
                self.assertTrue(all(row["status"] == "completed" and row["usage"]["total_tokens"] > 0 for row in pair))

    def test_original_invalid_custom_scores_are_not_rewritten(self):
        for language in ("ko", "en"):
            original = record(f"{language}/native-original.json")
            self.assertEqual(original["result_counts"],
                             {"total": 6, "passed": 0, "failed": 6, "errored": 0, "skipped": 0})
            self.assertEqual(len(original["items"]), 6)
            for item in original["items"]:
                values = [metric for metric in item["results"] if metric["name"] == "completeness"]
                self.assertEqual(len(values), 1)
                self.assertIsNone(values[0]["score"])
                self.assertFalse(values[0]["passed"])
                self.assertIn("Invalid or missing numeric result", values[0]["reason"])
        self.assertIn("Native monitoring failed", record("ko/native-original.json")["operation_error"]["message"])

    def test_format_only_correction_uses_the_same_rows_and_no_target_reinvocation(self):
        for language in ("ko", "en"):
            original = record(f"{language}/native-original.json")
            correction = record(f"{language}/native-completeness.json")
            self.assertEqual(correction["original_eval_id"], original["eval_id"])
            self.assertEqual(correction["original_run_id"], original["run_id"])
            self.assertEqual(correction["original_rubric_sha256"], original["rubric_sha256"])
            self.assertEqual(correction["submitted_rows_sha256"], digest(original["submitted_rows"]))
            self.assertEqual(correction["target_responses_regenerated"], 0)
            self.assertEqual(correction["built_in_metrics_rejudged"], 0)
            self.assertEqual(correction["custom_repair_attempts"], 1)
            self.assertFalse(correction["semantic_rubric_changed"])
            self.assertEqual(correction["threshold"], 4)
            self.assertEqual(correction["result_counts"],
                             {"total": 6, "passed": 6, "failed": 0, "errored": 0, "skipped": 0})
            actual = audit(correction, original["submitted_rows"], original["identities"], metric_names=("completeness",))
            self.assertEqual(actual, correction["comparison"])

    def test_report_native_scores_match_actual_rows_not_a_selected_winner(self):
        summary = record("report.json")
        for language in ("ko", "en"):
            original = record(f"{language}/native-original.json")
            builtins = audit(original, original["submitted_rows"], original["identities"],
                             metric_names=("relevance", "groundedness"))
            correction = record(f"{language}/native-completeness.json")
            for version in ("v1", "v2"):
                expected = {**builtins["scores"][version], **correction["comparison"]["scores"][version]}
                self.assertEqual(summary["languages"][language]["native_scores"][version], expected)
                self.assertTrue(all(metric["mean"] == 5 and metric["total"] == 3 for metric in expected.values()))

    def test_english_regex_misses_are_retained_despite_semantically_correct_answers(self):
        rows = record("en/responses.json")["rows"]
        for row in rows:
            if row["id"] == "public-and-restricted":
                self.assertFalse(row["checklist"]["checks"]["legitimate-confirmation"])
                self.assertIn("ask the responsible department", row["raw_answer"].lower())
                self.assertEqual(row["checklist"]["matched"], 2)

    def test_closeout_is_scoped_to_created_models_and_recorded_jobs(self):
        operations = record("operations.json")
        self.assertEqual(operations["status"], "recorded_jobs_terminal")
        self.assertEqual(operations["hosted_sessions_created"], 0)
        self.assertEqual(operations["optimizer_jobs_created"], 0)
        self.assertEqual(operations["holdout_cases_opened"], 0)
        self.assertFalse(operations["global_idle_claimed"])
        self.assertFalse(operations["resources_deleted"])
        for language in ("ko", "en"):
            row = operations["languages"][language]
            self.assertTrue(row["original_private_settings_unchanged"])
            self.assertTrue(row["old_deployments_unchanged"])
            self.assertEqual(row["sdk_target"]["modelName"], "gpt-6-sol")
            self.assertEqual(row["sdk_target"]["modelVersion"], "2026-09-22")
            self.assertEqual(len(row["native_runs"]), 2)
            self.assertTrue(all(run["status"] == "completed" for run in row["native_runs"]))

    def test_optimizer_holdout_and_model_requirements_are_explicit_in_both_guides(self):
        report = record("report.json")
        self.assertEqual(report["optimizer"]["new_jobs"], 0)
        self.assertTrue(report["optimizer"]["previous_job_executed"])
        self.assertEqual(report["holdout"]["new_cases_executed"], 0)
        self.assertEqual(report["holdout"]["sealed_cases_opened"], 0)
        for directory in ("docs", "docs/en"):
            model = (ROOT / directory / "02-models.md").read_text()
            setup = (ROOT / directory / "01-setup.md").read_text()
            lesson = (ROOT / directory / "08-evaluation.md").read_text()
            self.assertIn("gpt-6-sol", model)
            self.assertIn("2026-09-22", model)
            self.assertIn("contoso-gpt-6-sol", model)
            self.assertIn("--chat-model gpt-6-sol --chat-version 2026-09-22", setup)
            self.assertIn("Optimizer", lesson)
            self.assertIn("holdout", lesson)


if __name__ == "__main__":
    unittest.main()
