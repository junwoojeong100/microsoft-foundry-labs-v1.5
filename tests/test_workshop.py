import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "samples"))
import workshop as w


class ToolsTests(unittest.TestCase):
    def test_stock(self):
        self.assertEqual(w.get_stock("NB-14")["stock"], 8)
        self.assertEqual(w.get_stock("MON-27")["stock"], 0)

    def test_draft_never_orders(self):
        result = w.prepare_purchase_request("NB-14", 2)
        self.assertEqual(result["total_krw"], 2_900_000)
        self.assertEqual(result["required_approvals"], ["team_lead", "procurement"])
        self.assertEqual(result["status"], "draft_requires_human_approval")
        self.assertFalse(result["order_submitted"])
        self.assertEqual(result, w.prepare_purchase_request("NB-14", 2))

    def test_exact_approval_boundary(self):
        self.assertEqual(w.required_approvals(2_000_000), ["team_lead"])
        self.assertEqual(w.required_approvals(2_000_001), ["team_lead", "procurement"])

    def test_invalid_quantities_and_stock(self):
        for value in (True, False, 0, -1, 11, 1.5, "2", None, []):
            with self.subTest(value=value), self.assertRaises(w.ToolInputError):
                w.prepare_purchase_request("KB-01", value)
        with self.assertRaises(w.ToolInputError):
            w.prepare_purchase_request("NB-14", 10)
        with self.assertRaises(w.ToolInputError):
            w.prepare_purchase_request("MON-27", 1)

    def test_allowlist(self):
        for name, payload in (
            ("submit_order", "{}"), ("get_stock", '{"sku":"NB-99"}'),
            ("get_stock", '{"sku":"NB-14","approved":true}'),
            ("get_stock", "[]"), ("get_stock", "not-json"),
        ):
            with self.subTest(name=name, payload=payload), self.assertRaises(w.ToolInputError):
                w.dispatch_tool(name, payload)


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"id": c["id"], "manual_pass": True, "response": "unit-test fixture only", "review_note": "unit-test fixture only"}
            for c in w.validate_data()
        ]

    def test_all_pass(self):
        self.assertTrue(w.score_reviews(self.rows)["gate_passed"])

    def test_ninety_percent_boundary(self):
        self.rows[0]["manual_pass"] = False
        self.rows[1]["manual_pass"] = False
        self.assertTrue(w.score_reviews(self.rows)["gate_passed"])
        self.rows[2]["manual_pass"] = False
        self.assertFalse(w.score_reviews(self.rows)["gate_passed"])

    def test_safety_overrides_average(self):
        self.rows[9]["manual_pass"] = False
        self.assertFalse(w.score_reviews(self.rows)["gate_passed"])
        self.assertEqual(w.score_reviews(self.rows)["critical_failures"], ["dev-10"])

    def test_access_overrides_average(self):
        self.rows[16]["manual_pass"] = False
        self.assertFalse(w.score_reviews(self.rows)["gate_passed"])

    def test_partial_duplicate_and_unknown_never_pass(self):
        for rows in ([], self.rows[:-1], self.rows[:-1] + [self.rows[0]], self.rows + [self.rows[0]]):
            with self.assertRaises(ValueError):
                w.score_reviews(rows)

    def test_unreviewed_or_missing_evidence_never_pass(self):
        for value in (None, 1, "true", ""):
            self.rows[0]["manual_pass"] = value
            with self.assertRaises(ValueError):
                w.score_reviews(self.rows)
        self.rows[0]["manual_pass"] = True
        self.rows[0]["review_note"] = ""
        with self.assertRaises(ValueError):
            w.score_reviews(self.rows)

    def test_split_is_explicit(self):
        self.assertEqual(w.score_reviews(self.rows[:10], "dev")["total"], 10)
        with self.assertRaises(ValueError):
            w.score_reviews(self.rows[:10])


class BoundaryTests(unittest.TestCase):
    def test_default_cloud_commands_never_connect(self):
        for command in ("model", "agent", "rag", "capstone", "evaluate", "cleanup"):
            with patch.object(w, "run_live", side_effect=AssertionError("Must not call Azure")):
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(w.main([command]), 0)
                    self.assertIn("PLAN ONLY", output.getvalue())

    def test_config_rejects_wrong_endpoint_and_placeholders(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env"
            for endpoint in (
                "http://x.services.ai.azure.com/api/projects/p",
                "https://x.services.ai.azure.com/openai/v1",
                "https://x.services.ai.azure.com.evil.example/api/projects/p",
                "https://user:pass@x.services.ai.azure.com/api/projects/p",
                "https://YOUR-RESOURCE.services.ai.azure.com/api/projects/YOUR-PROJECT",
            ):
                path.write_text(f"{w.ENDPOINT_KEY}={endpoint}\n{w.MODEL_KEY}=lab-chat\n")
                with patch.dict(w.os.environ, {}, clear=True), self.assertRaises(ValueError):
                    w.read_config(path)

    def test_environment_precedence(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env"
            path.write_text(f"{w.ENDPOINT_KEY}=https://x.services.ai.azure.com/api/projects/p\n{w.MODEL_KEY}=file-value\n")
            with patch.dict(w.os.environ, {w.MODEL_KEY: "environment-value"}, clear=True):
                self.assertEqual(w.read_config(path)[1], "environment-value")

    def test_invalid_jsonl(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.jsonl"
            for text in ("", "{}\n\n", "[]\n", "{oops}\n"):
                path.write_text(text)
                with self.assertRaises(ValueError):
                    w.load_jsonl(path)

    def test_cleanup_rejects_foreign_run(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(w, "RESULTS", Path(directory)):
            path = Path(directory) / "hb-lab-123456789abc.json"
            value = {
                "schema": "hb-lab-resources-v1", "run_id": path.stem, "endpoint": "expected",
                "resources": [{"kind": "agent", "id": "not-our-agent"}],
            }
            path.write_text(json.dumps(value))
            with self.assertRaises(ValueError):
                w.read_receipt(path, "expected")


if __name__ == "__main__":
    unittest.main()
