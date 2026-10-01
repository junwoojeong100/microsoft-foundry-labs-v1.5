import hashlib
import json
from pathlib import Path
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "validation/current"


def record(name):
    return json.loads((DIRECTORY / name).read_text(encoding="utf-8"))


class LatestEvidenceTests(unittest.TestCase):
    def test_all_native_rows_do_not_override_the_critical_business_failure(self):
        quality = record("quality.json")
        dev = quality["dev"]
        self.assertEqual(dev["required"], 40)
        self.assertEqual(dev["attempted"], 40)
        self.assertEqual(dev["completed_responses"], 40)
        self.assertEqual(dev["collection_attempts"], 1)
        self.assertEqual(dev["native_runs"], 1)
        self.assertEqual(dev["native_passes"], 40)
        self.assertEqual(dev["business_passes"], 39)
        self.assertEqual(dev["pass_rate"], 0.975)
        self.assertEqual(dev["native_counts"], {"total": 40, "passed": 40, "failed": 0, "errored": 0, "skipped": 0})
        self.assertEqual(dev["critical_failures"], ["v5-dev-30"])
        self.assertFalse(dev["complete_business_gate_passed"])
        self.assertFalse(quality["quality_release"])
        self.assertFalse(quality["failed_cases_resampled"])
        self.assertFalse(quality["criteria_changed"])
        self.assertFalse(quality["original_answers_rewritten"])
        self.assertEqual(len(record("native-dev.json")["items"]), 40)

    def test_failed_access_evidence_and_unopened_holdout_remain_explicit(self):
        diagnosis = record("dev30-diagnosis.json")
        self.assertEqual(diagnosis["category"], "access")
        self.assertEqual(diagnosis["automatic_checks"]["failures"], ["required_policy_evidence"])
        self.assertTrue(diagnosis["native_passed"])
        self.assertEqual(diagnosis["native_score"], 4)
        self.assertFalse(diagnosis["business_passed"])
        self.assertEqual(diagnosis["business_tools_executed"], [])
        self.assertEqual(diagnosis["missing_citation_groups"], [
            ["CONTOSO-PROC-2026-09-s5", "CONTOSO-SEC-2026-09-s1"],
        ])
        quality = record("quality.json")
        self.assertEqual(quality["holdout"]["executed"], 0)
        self.assertFalse(quality["holdout"]["opened_for_target_evaluation"])
        self.assertFalse((DIRECTORY / "dev-gate.json").exists())
        self.assertFalse((DIRECTORY / "holdout-responses.jsonl").exists())
        manifest_path = ROOT / "data/en/evaluation/v5/holdout-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        self.assertTrue(manifest["sealed"])
        self.assertEqual(manifest["rows"], 10)
        self.assertEqual(manifest["release_status"], "sealed_unexecuted")
        self.assertEqual(quality["holdout"]["sha256"], manifest["sha256"])
        self.assertEqual(quality["holdout"]["seal_manifest_sha256"], hashlib.sha256(manifest_path.read_bytes()).hexdigest())

    def test_v5_exports_retain_actual_v2_authorization_and_citation_provenance(self):
        rows = [json.loads(line) for line in (DIRECTORY / "dev-responses.jsonl").read_text().splitlines()]
        self.assertEqual(len(rows), 40)
        self.assertEqual(len({row["id"] for row in rows}), 40)
        for row in rows:
            self.assertEqual(row["tool_authorization_contract"], "explicit-request-v2")
            self.assertEqual(row["execution_location"], "azure")
            self.assertEqual(row["hosted_version"], "4")
            self.assertEqual(row["evaluation_suite"], "automated-v5")
            for key in ("request_permissions", "required_policy_citations", "raw_answer",
                        "raw_attribution", "retrieved_sources", "tool_calls", "citations", "response_id", "trace_id"):
                self.assertIn(key, row)
        calibration = record("calibration.json")
        self.assertTrue(calibration["calibration_passed"])
        self.assertEqual(calibration["controls"], 8)
        self.assertEqual(calibration["matched"], 8)

    def test_smokes_and_local_cli_rejection_are_distinct_preserved_observations(self):
        first, second = record("invocations-smoke.json"), record("responses-smoke.json")
        for smoke in (first, second):
            self.assertEqual(smoke["version"], "4")
            self.assertEqual(smoke["tool_authorization_contract"], "explicit-request-v2")
            self.assertTrue(smoke["checks"]["passed"])
            self.assertFalse(smoke["quality_release"])
        self.assertEqual(first["effective_prompt_sha256"], second["effective_prompt_sha256"])
        rejected = record("attempts/responses-cli-rejection.json")
        self.assertEqual(rejected["status"], "failed_before_target_invocation")
        self.assertFalse(rejected["target_request_submitted"])
        self.assertFalse(rejected["candidate_source_changed"])

    def test_distinct_v5_freeze_preserves_the_pre_exam_sources(self):
        with zipfile.ZipFile(DIRECTORY / "source-snapshot.zip") as archive:
            frozen = json.loads(archive.read("data/en/evaluation/v5/development-freeze.json"))
            self.assertEqual(frozen["suite"], "automated-v5")
            self.assertEqual(len(frozen["files"]), 34)
            self.assertEqual(frozen["tool_authorization_contract"], "explicit-request-v2")
            self.assertFalse(frozen["final_holdout_exists_at_freeze"])
            self.assertFalse(any("holdout" in name for name in archive.namelist()))
            for name, expected in frozen["files"].items():
                self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(), expected)

    def test_optimizer_service_success_cannot_hide_error_or_replace_dev_originals(self):
        optimizer = record("optimizer.json")
        self.assertEqual(optimizer["outcome"], "operational_failure")
        self.assertEqual(optimizer["service_status"], "succeeded")
        self.assertEqual(optimizer["service_duration_seconds"], 647)
        self.assertEqual(optimizer["native_baseline"]["result_counts"],
                         {"total": 40, "passed": 38, "failed": 1, "errored": 1, "skipped": 0})
        self.assertEqual(optimizer["native_baseline"]["errored_case_ids"], ["v5-dev-08"])
        self.assertEqual(optimizer["native_baseline"]["failed_case_ids"], ["v5-dev-27"])
        self.assertEqual(optimizer["native_baseline"]["authentic_engine_records"], 39)
        self.assertEqual(optimizer["generated_candidates"], 0)
        self.assertFalse(optimizer["candidate_promoted"])
        self.assertFalse(optimizer["quality_improvement_claimed"])
        self.assertEqual(optimizer["dev_cases"], 40)
        self.assertEqual(optimizer["holdout_cases"], 0)
        self.assertEqual(optimizer["max_seconds"], 1200)
        self.assertLessEqual(optimizer["observed_cleanup_elapsed_seconds"], 180)
        items = {row["case_id_from_exact_query"]: row for row in record("optimizer-native.json")["items"]}
        self.assertEqual(len(items), 40)
        self.assertEqual(items["v5-dev-08"]["sample_output_text"], "")
        self.assertFalse(items["v5-dev-27"]["metrics"][0]["passed"])
        self.assertTrue(items["v5-dev-27"]["automatic_checks_on_preserved_engine_output"]["passed"])
        self.assertFalse(record("quality.json")["dev"]["verdicts"]["v5-dev-30"]["passed"])

    def test_scoped_closeout_and_historical_preservation_are_not_global_claims(self):
        operations = record("operations.json")
        self.assertEqual(operations["status"], "scoped_closeout_verified")
        self.assertEqual(operations["recorded_sessions_stopped"], 5)
        self.assertEqual(len({row["id"] for row in operations["sessions"]}), 5)
        for row in operations["sessions"]:
            self.assertTrue(row["ownership_verified"])
            self.assertTrue(row["stop_verified"])
            self.assertEqual(row["status"], "idle")
            self.assertTrue(row["stopped_at"])
        self.assertEqual(len(operations["optimizer_jobs"]), 1)
        self.assertTrue(operations["optimizer_jobs"][0]["terminal"])
        self.assertEqual(len(operations["native_runs"]), 3)
        self.assertFalse(operations["global_idle_claimed"])
        self.assertFalse(operations["resources_deleted"])
        current = record("instructions.json")
        self.assertFalse(current["latest_actual_azure"]["matches_new_v2_instructions"])
        self.assertFalse(current["v2_live_improvement_established"])
        self.assertFalse(current["historical_archive"]["history_rewritten"])
        for name, original in current["retained_originals"].items():
            self.assertEqual(hashlib.sha256((DIRECTORY / name).read_bytes()).hexdigest(), original["sha256"])



if __name__ == "__main__":
    unittest.main()
