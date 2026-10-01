import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "validation/current"
sys.path.insert(0, str(ROOT / "samples"))
from evidence import digest
from instruction_evaluation import METRICS, audit


def record(name):
    return json.loads((DIRECTORY / name).read_text(encoding="utf-8"))


class LatestEvidenceTests(unittest.TestCase):
    def test_current_report_records_the_complete_bilingual_comparison(self):
        report = record("report.json")
        self.assertEqual(report["schema"], "contoso-bilingual-instruction-comparison")
        self.assertEqual(report["status"], "measured_v2_improvement")
        self.assertEqual(report["target_model"], "gpt-6-sol")
        self.assertEqual(report["target_model_version"], "2026-09-22")
        self.assertEqual(report["execution_locations"], ["azure_prompt_agent"])
        self.assertEqual(report["judge_model"], "gpt-4.1")
        self.assertEqual(report["judge_model_version"], "2025-04-14")
        self.assertEqual(report["questions_per_instruction_per_language"], 12)
        self.assertEqual(report["target_response_count_per_language"], 24)
        self.assertEqual(report["target_calls"], 48)
        self.assertFalse(report["target_resampling"])
        self.assertEqual(report["native_runs"], 2)
        self.assertTrue(report["v2_measured_improvement"])
        self.assertFalse(report["quality_release"])
        self.assertEqual(report["bilingual_response_collection_max_seconds"], 1200)
        self.assertEqual(report["native_max_seconds_each"], 600)
        self.assertFalse(report["judge_control_calibration_performed"])

    def test_actual_responses_match_frozen_inputs_and_instruction_hashes(self):
        report = record("report.json")
        status = record("instructions.json")
        self.assertTrue(status["v2_live_comparison_completed"])
        self.assertTrue(status["v2_live_improvement_established"])
        self.assertFalse(status["score_improvement_guaranteed"])
        for language in ("ko", "en"):
            row = report["languages"][language]
            data = ROOT / "data" / ("en" if language == "en" else "")
            responses = record(f"{language}/responses.json")
            self.assertEqual(responses["status"], "completed")
            self.assertEqual(responses["execution_location"], "azure_prompt_agent")
            self.assertEqual(responses["language"], language)
            self.assertEqual(row["execution_location"], "azure_prompt_agent")
            agent = responses["prompt_agent_versions"]
            self.assertEqual(agent["status"], "active")
            self.assertEqual(set(agent["versions"]), {"v1", "v2"})
            self.assertEqual(agent["model_deployment"], "contoso-gpt-6-sol")
            self.assertEqual(agent["tools"], [])
            self.assertEqual(row["prompt_agent"]["agent_name"], agent["agent_name"])
            self.assertEqual(row["prompt_agent"]["versions"], agent["versions"])
            self.assertEqual(responses["model_deployment"], "contoso-gpt-6-sol")
            self.assertEqual(responses["model_identity"]["modelName"], "gpt-6-sol")
            self.assertEqual(responses["model_identity"]["modelVersion"], "2026-09-22")
            self.assertEqual(responses["reasoning_effort"], "low")
            self.assertEqual(responses["max_output_tokens"], 2048)
            self.assertEqual(responses["retries"], 0)
            self.assertEqual(responses["holdout_cases"], 0)
            self.assertEqual(responses.get("optimizer_rows", responses.get("optimizer_jobs")), 0)
            self.assertFalse(responses["shared_wrapper"]["version_specific_guidance_in_wrapper"])
            self.assertFalse(responses["shared_wrapper"]["target_input_contains_case_criteria_or_reference_answers"])
            self.assertEqual(responses["shared_wrapper"]["available_tools"], [])
            self.assertEqual(len(responses["rows"]), 24)
            self.assertEqual(responses["budget_usage"]["requests"], 24)
            self.assertLessEqual(responses["budget_usage"]["elapsed_seconds"], 600)
            cases = json.loads((data / "evaluation/instruction-comparison.json").read_text())["cases"]
            self.assertEqual(len(cases), 12)
            self.assertEqual(responses["cases_sha256"], digest(cases))
            self.assertEqual(responses["cases_sha256"], row["cases_sha256"])
            self.assertEqual(
                responses["instructions_sha256"],
                {
                    version: hashlib.sha256(
                        (data / f"prompts/agent-{version}.txt").read_bytes()
                    ).hexdigest()
                    for version in ("v1", "v2")
                },
            )
            self.assertEqual(responses["instructions_sha256"], row["instruction_hashes"])
            for case in cases:
                pair = [answer for answer in responses["rows"] if answer["id"] == case["id"]]
                self.assertEqual({answer["instructions"] for answer in pair}, {"v1", "v2"})
                self.assertEqual({answer["query"] for answer in pair}, {case["query"]})
                self.assertEqual(len({answer["input_sha256"] for answer in pair}), 1)
                self.assertEqual(len({answer["response_id"] for answer in pair}), 2)
                self.assertTrue(
                    all(
                        answer["status"] == "completed"
                        and answer["usage"]["total_tokens"] > 0
                        and answer["raw_answer"]
                        for answer in pair
                    )
                )
                for answer in pair:
                    self.assertEqual(answer["agent_name"], agent["agent_name"])
                    self.assertEqual(answer["agent_version"], agent["versions"][answer["instructions"]])
            self.assertEqual(row["target_response_count"], 24)
            self.assertEqual(row["questions_per_instruction"], 12)
            self.assertEqual(row["response_file_sha256"], hashlib.sha256(
                (DIRECTORY / language / "responses.json").read_bytes()
            ).hexdigest())

    def test_native_rows_and_per_question_reasons_are_auditable(self):
        report = record("report.json")
        for language in ("ko", "en"):
            summary = report["languages"][language]
            responses = record(f"{language}/responses.json")
            native = record(f"{language}/native.json")
            self.assertEqual(native["status"], "completed")
            self.assertEqual(native["language"], language)
            self.assertEqual(native["native_rows"], 24)
            self.assertEqual(native["target_reinvocations"], 0)
            self.assertEqual(native["optimizer_jobs"], 0)
            self.assertEqual(native["holdout_cases"], 0)
            self.assertEqual(native["native_max_seconds"], 600)
            self.assertEqual(native["cancellation_max_seconds"], 90)
            self.assertFalse(native["timed_out"])
            self.assertEqual(native["source_sha256"], hashlib.sha256(
                (DIRECTORY / language / "responses.json").read_bytes()
            ).hexdigest())
            self.assertEqual(native["source_sha256"], summary["response_file_sha256"])
            self.assertEqual(native["models"]["target"]["modelName"], "gpt-6-sol")
            self.assertEqual(native["models"]["target"]["modelVersion"], "2026-09-22")
            self.assertEqual(native["models"]["judge"]["name"], "contoso-judge")
            self.assertEqual(native["models"]["judge"]["modelName"], "gpt-4.1")
            self.assertEqual(native["models"]["judge"]["modelVersion"], "2025-04-14")
            self.assertEqual(native["result_counts"]["total"], 24)
            self.assertEqual(native["result_counts"]["errored"], 0)
            self.assertEqual(native["result_counts"]["skipped"], 0)
            self.assertEqual(native["result_counts"]["passed"], 24)
            self.assertEqual(len(native["items"]), 24)
            self.assertEqual(len(native["submitted_rows"]), 24)
            actual = audit(native, native["submitted_rows"], native["identities"])
            self.assertEqual(actual, native["comparison"])
            self.assertEqual(actual["scores"], summary["native_scores"])
            self.assertEqual(actual["delta"], summary["native_delta"])
            self.assertEqual(len(summary["per_question"]), 12)
            response_by_id = {answer["response_id"]: answer for answer in responses["rows"]}
            native_by_case = {
                case_id: {
                    item["instructions"]: item
                    for item in native["comparison"]["rows"]
                    if item["case_id"] == case_id
                }
                for case_id in {item["case_id"] for item in native["comparison"]["rows"]}
            }
            for question in summary["per_question"]:
                case_id = question["case_id"]
                self.assertEqual(set(native_by_case[case_id]), {"v1", "v2"})
                for version in ("v1", "v2"):
                    answer = response_by_id[question[version]["response_id"]]
                    self.assertEqual(answer["id"], case_id)
                    self.assertEqual(
                        digest(answer["raw_answer"]),
                        question[version]["answer_sha256"],
                    )
                    self.assertEqual(
                        question[version]["native_metrics"],
                        native_by_case[case_id][version]["metrics"],
                    )
                    for metric in METRICS:
                        result = question[version]["native_metrics"][metric]
                        self.assertIsInstance(result["reason"], str)
                        self.assertTrue(result["reason"].strip())
            self.assertEqual(
                summary["native_run"]["run_id"],
                {
                    "ko": "evalrun_ca3fd99d7bd54c0d86b475d383044a47",
                    "en": "evalrun_9752d9f1717546c2a1ff1e2317f9131b",
                }[language],
            )
            self.assertEqual(
                summary["native_file_sha256"],
                hashlib.sha256((DIRECTORY / language / "native.json").read_bytes()).hexdigest(),
            )

    def test_native_tie_and_local_checklist_changes_are_reported_separately(self):
        report = record("report.json")
        expected = {
            "ko": ({"v1": 33, "v2": 33}, 0),
            "en": ({"v1": 29, "v2": 28}, -1),
        }
        for language, (scores, delta) in expected.items():
            summary = report["languages"][language]
            self.assertEqual(summary["local_checklist"]["maximum"], 40)
            self.assertEqual(summary["local_checklist"]["scores"], scores)
            self.assertEqual(summary["local_checklist"]["delta"], delta)
            self.assertTrue(summary["manual_safety_access_review"]["no_safety_or_access_regression_observed"])
            self.assertTrue(summary["critical_check_changes"]["new_v2_flags"])
            self.assertFalse(summary["quality_release"])
        self.assertEqual(report["languages"]["ko"]["native_delta"], {
            "completeness": 0.0, "relevance": 0.08333333333333304, "groundedness": 0.0,
        })
        self.assertEqual(report["languages"]["en"]["native_delta"], {
            "completeness": 0.0, "relevance": 0.0, "groundedness": 0.0,
        })
        ko_relevance = [
            (row["case_id"], version, row[version]["native_metrics"]["relevance"]["score"])
            for row in report["languages"]["ko"]["per_question"]
            for version in ("v1", "v2")
            if row[version]["native_metrics"]["relevance"]["score"] < 5
        ]
        self.assertEqual(ko_relevance, [("compound-request-no-tools", "v1", 4.0)])
        self.assertTrue(report["v2_measured_improvement"])
        self.assertFalse(report["quality_release"])

    def test_usage_latency_optimizer_holdout_and_history_are_preserved(self):
        report = record("report.json")
        expected = {
            "ko": {
                "tokens": {"input_tokens": 5976, "output_tokens": 1400, "total_tokens": 7376},
                "latency": 0.427,
            },
            "en": {
                "tokens": {"input_tokens": 4332, "output_tokens": 825, "total_tokens": 5157},
                "latency": 0.496,
            },
        }
        for language, values in expected.items():
            usage = report["languages"][language]["usage_latency"]
            self.assertEqual(usage["v2_minus_v1_tokens"], values["tokens"])
            self.assertEqual(usage["v2_minus_v1_mean_latency_seconds"], values["latency"])
        self.assertEqual(report["optimizer"]["new_jobs"], 0)
        self.assertEqual(report["optimizer"]["candidate_source"], "v2 instructions were authored directly; no Optimizer-generated candidate.")
        for language, attempt in report["collection_attempts"].items():
            self.assertEqual(attempt["preflight_failure"]["target_calls"], 0)
            self.assertEqual(attempt["request_failure"]["target_calls"], 0)
            self.assertEqual(attempt["completed"]["target_calls"], 24)
            self.assertEqual(attempt["completed"]["prompt_agent"]["status"], "active")
        self.assertEqual(report["holdout"]["new_cases_executed"], 0)
        self.assertEqual(report["holdout"]["sealed_cases_opened"], 0)
        self.assertEqual(
            report["history"]["previous_measurement_commit"],
            "39b2bd1a1c85cb18d3d46d8bf876a6e274d32958",
        )
        self.assertTrue(report["history"]["previous_measurement_preserved_in_git_history"])
        self.assertFalse(report["history"]["history_rewritten"])
        self.assertFalse((DIRECTORY / "ko/native-original.json").exists())
        self.assertFalse((DIRECTORY / "ko/native-completeness.json").exists())
        self.assertFalse((DIRECTORY / "en/native-original.json").exists())
        self.assertFalse((DIRECTORY / "en/native-completeness.json").exists())

    def test_operations_receipt_matches_only_the_approved_projects(self):
        operations = record("operations.json")
        self.assertEqual(operations["status"], "recorded_jobs_terminal")
        self.assertEqual(operations["target_calls"], 48)
        self.assertEqual(operations["native_runs"], 2)
        self.assertEqual(operations["hosted_sessions_created"], 0)
        self.assertEqual(operations["prompt_agents_created"], 2)
        self.assertEqual(operations["prompt_agent_versions_created"], 4)
        self.assertEqual(operations["optimizer_jobs_created"], 0)
        self.assertEqual(operations["holdout_cases_opened"], 0)
        self.assertFalse(operations["global_idle_claimed"])
        self.assertFalse(operations["resources_deleted"])
        self.assertFalse(operations["policy_or_access_changed"])
        self.assertEqual(
            {language: row["resource_group"] for language, row in operations["languages"].items()},
            {"ko": "rg-contoso-a-26092979bea5", "en": "rg-contoso-en-260930ae24ba"},
        )
        for language, row in operations["languages"].items():
            self.assertEqual(row["target_deployment"]["model"], "gpt-6-sol")
            self.assertEqual(row["target_deployment"]["version"], "2026-09-22")
            self.assertEqual(row["native_run"]["status"], "completed")
            self.assertEqual(row["native_run"]["result_counts"]["errored"], 0)

    def test_both_guides_and_sources_describe_actual_outcomes_and_limits(self):
        for directory in ("docs", "docs/en"):
            path = ROOT / directory
            models = (path / "02-models.md").read_text()
            setup = (path / "01-setup.md").read_text()
            evaluation = (path / "08-evaluation.md").read_text()
            optimization = (path / "20-optimization.md").read_text()
            self.assertIn("gpt-6-sol", models)
            self.assertIn("2026-09-22", models)
            self.assertIn("contoso-gpt-6-sol", models)
            self.assertIn("--chat-model gpt-6-sol --chat-version 2026-09-22", setup)
            self.assertIn("12", evaluation)
            self.assertIn("Prompt Agent", evaluation)
            self.assertIn("Optimizer", optimization)
            self.assertIn("holdout", optimization)
        for path in (ROOT / "docs/sources.md", ROOT / "docs/en/sources.md"):
            text = path.read_text()
            self.assertIn("33", text)
            self.assertIn("29", text)
            self.assertIn("12", text)
        for name in ("README.md", "README.ko.md"):
            text = (ROOT / name).read_text()
            self.assertIn("48", text)
            self.assertIn("33", text)
            self.assertIn("5.0", text)


if __name__ == "__main__":
    unittest.main()
