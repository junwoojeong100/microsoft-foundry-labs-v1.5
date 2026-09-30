import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "validation/english/automated-v4"


def record(name):
    return json.loads((DIRECTORY / name).read_text(encoding="utf-8"))


class LiveV4EvidenceTests(unittest.TestCase):
    def test_incomplete_actual_dev_is_not_a_native_or_holdout_pass(self):
        report = record("report.json")
        quality = record("quality.json")
        self.assertFalse(report["quality_release"])
        self.assertEqual(report["calibration"]["matched"], 8)
        self.assertEqual(quality["dev"]["required"], 40)
        self.assertEqual(quality["dev"]["attempted"], 37)
        self.assertEqual(quality["dev"]["completed_responses"], 36)
        self.assertEqual(quality["dev"]["runtime_failed"], ["v4-dev-37"])
        self.assertEqual(quality["dev"]["not_executed"], ["v4-dev-38", "v4-dev-39", "v4-dev-40"])
        self.assertFalse(quality["dev"]["complete_business_gate_passed"])
        self.assertIsNone(quality["dev"]["native_pass_rate"])
        self.assertEqual(quality["holdout"]["executed"], 0)
        manifest = json.loads((ROOT / "data/en/evaluation/v4/holdout-manifest.json").read_text())
        self.assertEqual(quality["holdout"]["sha256"], manifest["sha256"])
        rows = [json.loads(line) for line in (DIRECTORY / "attempts/initial-dev/partial-responses.jsonl").read_text().splitlines()]
        self.assertEqual(len(rows), 37)
        self.assertEqual(rows[-1]["status"], "failed")
        for row in rows[:-1]:
            self.assertEqual(row["tool_authorization_contract"], "explicit-request-v1")
            self.assertIn("request_permissions", row)
            self.assertIn("required_policy_citations", row)

    def test_service_success_cannot_hide_native_errors_or_invent_candidate_improvement(self):
        optimizer = record("optimizer.json")
        self.assertEqual(optimizer["service_status"], "succeeded")
        self.assertEqual(optimizer["outcome"], "operational_failure")
        self.assertEqual(optimizer["native_baseline"]["result_counts"]["total"], 40)
        self.assertEqual(optimizer["native_baseline"]["result_counts"]["errored"], 3)
        self.assertEqual(optimizer["native_baseline"]["result_counts"]["passed"], 37)
        self.assertEqual(optimizer["generated_candidates"], 0)
        self.assertFalse(optimizer["candidate_promoted"])
        self.assertFalse(optimizer["quality_improvement_claimed"])
        self.assertFalse(optimizer["timeout_reached"])
        self.assertFalse(optimizer["cancellation_requested"])

    def test_scoped_closeout_does_not_invent_a_global_idle_or_admin_confirmation(self):
        operations = record("operations.json")
        self.assertEqual(operations["recorded_sessions_stopped"], 5)
        self.assertEqual(len({row["id"] for row in operations["sessions"]}), 5)
        for row in operations["sessions"]:
            self.assertEqual(row["status"], "idle")
            self.assertTrue(row["stopped_at"])
        self.assertFalse(operations["global_idle_claimed"])
        self.assertIn("500", operations["global_optimizer_inventory"])
        self.assertFalse(operations["resources_deleted"])
        administrator = record("report.json")["administrator"]
        self.assertEqual(administrator["owned_failed_deployments_read"], 1)
        self.assertFalse(administrator["external_workspace_current_existence_checked"])
        self.assertFalse(administrator["administrator_contacted"])
        self.assertFalse(administrator["policy_or_permissions_changed"])


if __name__ == "__main__":
    unittest.main()
