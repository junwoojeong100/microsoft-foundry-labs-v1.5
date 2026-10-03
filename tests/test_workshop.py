import contextlib
from copy import deepcopy
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


class SavedResultTests(unittest.TestCase):
    def setUp(self):
        self.row = {
            "id": "manual-01", "status": "completed", "query": "Synthetic Contoso request",
            "response": "Original answer.\nNot a real order.", "response_id": "resp_synthetic",
            "configuration": {
                "language": w.LANGUAGE, "agent_name": "contoso-fixture",
                "agent_version": "7", "model_deployment": "synthetic-chat",
            },
            "tool_calls": [{
                "name": "prepare_purchase_request", "call_id": "call_synthetic",
                "arguments": '{"sku":"NB-14","quantity":2}',
                "output": {"ok": True, "result": {"total_krw": 2900000, "order_submitted": False}},
            }],
            "citations": [{"type": "file_citation", "file_id": "file_synthetic", "filename": "policy.md"}],
        }

    def test_reading_is_local_and_preserves_original_files_and_values(self):
        for language in ("ko", "en"):
            with self.subTest(language=language), tempfile.TemporaryDirectory() as directory:
                row = deepcopy(self.row)
                row["configuration"]["language"] = language
                path = Path(directory) / "responses.jsonl"
                path.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
                original = path.read_bytes()
                with (
                    patch.object(w, "LANGUAGE", language),
                    patch.object(w, "run_live", side_effect=AssertionError("No Azure calls")),
                    patch.object(w, "read_config", side_effect=AssertionError("No .env or credentials")),
                    contextlib.redirect_stdout(io.StringIO()) as output,
                ):
                    self.assertEqual(w.main(["read-result", "--input", str(path)]), 0)
                text = output.getvalue()
                for value in (row["response"], row["response_id"], row["query"], "call_synthetic",
                              "2900000", '"order_submitted": false', "file_synthetic", "policy.md"):
                    self.assertIn(value, text)
                self.assertIn("no automatic quality verdict" if language == "en" else "품질 자동 판정 아님", text)
                self.assertEqual(path.read_bytes(), original)
                self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_failed_rows_remain_failures_alongside_completed_rows(self):
        failed = {
            "id": "manual-02", "status": "failed", "query": "Synthetic failed request",
            "response": "", "error_type": "RuntimeError", "configuration": self.row["configuration"],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "responses.jsonl"
            path.write_text("\n".join(json.dumps(row) for row in (self.row, failed)) + "\n")
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(w.main(["read-result", "--input", str(path)]), 1)
            self.assertIn("failed", output.getvalue())
            self.assertIn("RuntimeError", output.getvalue())
            self.assertIn(self.row["response"], output.getvalue())

    def test_empty_observations_do_not_invent_evidence(self):
        self.row.update(tool_calls=[], citations=[])
        text = w.format_saved_responses([self.row])
        self.assertIn("[]", text)
        self.assertNotIn("2900000", text)
        self.assertNotIn("file_synthetic", text)

    def test_rejected_tool_output_is_not_replaced_with_a_draft(self):
        self.row["tool_calls"][0]["output"] = {
            "ok": False, "error": {"code": "invalid_tool_request", "message": "Insufficient stock"},
        }
        text = w.format_saved_responses([self.row])
        self.assertIn('"ok": false', text)
        self.assertIn("Insufficient stock", text)
        self.assertNotIn("2900000", text)

    def test_malformed_and_foreign_records_are_explicit_errors(self):
        defects = [
            {"status": "incomplete"}, {"response": ""}, {"response_id": None},
            {"tool_calls": None}, {"citations": None}, {"tool_calls": [{}]},
            {"configuration": {"language": "other"}}, {"query": ""},
            {"agent_name": "another-agent"}, {"agent_version": "different-version"},
        ]
        for changes in defects:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                w.format_saved_responses([{**self.row, **changes}])
        for record in ({}, {"schema": "contoso-lab-resources-v1"}, {"comparison": {}}):
            with self.subTest(record=record), self.assertRaises(ValueError):
                w.format_saved_responses([record])
        with self.assertRaises(ValueError):
            w.format_saved_responses([])

    def test_live_option_is_not_supported_by_the_reader(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            w.main(["read-result", "--input", "not-used.jsonl", "--live"])
        self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
