import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace as Obj
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
sys.path.insert(0, str(ROOT / "scripts"))
import evidence
import evaluation_lab
import hosted_client
import hosted_runtime
import optimizer_lab
import search_lab
import workshop
from check_independence import check


class ContosoTests(unittest.TestCase):
    def test_corpus_and_business_rules(self):
        chunks = search_lab.policy_chunks()
        self.assertEqual(len(chunks), 13)
        self.assertEqual(len({c["document_id"] for c in chunks}), 3)
        policy = next(c for c in chunks if c["id"] == "CONTOSO-PROC-2026-09-s3")
        self.assertIn("2,000,000원을 초과", policy["content"])
        self.assertEqual(workshop.prepare_purchase_request("NB-14", 2)["total_krw"], 2_900_000)

    def test_receipt_and_multimodal_answer_match(self):
        expected = json.loads((ROOT / "data/receipt.expected.json").read_text())
        self.assertIn(expected["document_id"], (ROOT / "data/receipt.html").read_text())
        self.assertIn(expected["document_id"], (ROOT / "docs/18-multimodal.md").read_text())

    def test_independent_executable_surfaces(self):
        self.assertEqual(check()["reference_repository_dependencies"], 0)

    def test_retrieval_never_substitutes_local_answer(self):
        canonical = search_lab.policy_chunks()[0]
        self.assertEqual(search_lab.validate_hits([canonical]), [canonical])
        for changed in ({**canonical, "content": "invented"}, {**canonical, "id": "unknown"}):
            with self.assertRaises(ValueError):
                search_lab.validate_hits([changed])

    def test_index_vector_and_semantic_contract(self):
        schema = search_lab.index_schema("contoso-test")
        vector = next(f for f in schema["fields"] if f["name"] == "content_vector")
        self.assertEqual(vector["dimensions"], 1536)
        self.assertEqual(schema["semantic"]["configurations"][0]["name"], "contoso-semantic")

    def test_legacy_cleanup_receipt_remains_readable_without_relabel(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(workshop, "RESULTS", Path(directory)):
            path = Path(directory) / "hb-lab-123456789abc.json"
            old = {"schema": "hb-lab-resources-v1", "run_id": path.stem, "endpoint": "expected", "resources": []}
            path.write_text(json.dumps(old))
            self.assertEqual(workshop.read_receipt(path, "expected"), old)


class EvidenceTests(unittest.TestCase):
    def test_budget_limits_before_next_request(self):
        budget = evidence.Budget(max_requests=1, max_tokens=10)
        budget.before_request(5)
        with self.assertRaises(RuntimeError):
            budget.before_request()
        budget = evidence.Budget(max_tokens=10)
        with self.assertRaises(RuntimeError):
            budget.before_request(11)
        self.assertEqual(budget.requests, 0)

    def test_trace_id_is_not_invented(self):
        self.assertIsNone(hosted_runtime.current_trace_id())

    def test_hosted_evidence_uses_writable_home_not_code(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(evidence.os.environ, {"FOUNDRY_AUTH_MODE": "managed_identity"}), patch.object(Path, "home", return_value=Path(directory)):
                record = evidence.Evidence("unit")
                self.assertEqual(record.path.parent, Path(directory) / ".contoso/evidence")

    def test_text_citations_only_normalize_actual_sources(self):
        source = search_lab.policy_chunks()[0]
        text = f"[{source['filename']}, {source['section']}]"
        citations = hosted_runtime.cited_sources(text, {source["id"]: source})
        self.assertEqual(citations[0]["citation_text"], text)
        self.assertEqual(citations[0]["citation_kind"], "text_reference")
        with self.assertRaises(RuntimeError):
            hosted_runtime.cited_sources("[invented.md, 4]", {source["id"]: source})
    def test_redaction_and_append_only(self):
        with tempfile.TemporaryDirectory() as directory:
            sink = evidence.Evidence("unit", root=Path(directory))
            sink.append("tool", {"authorization": "secret", "api_key": "secret", "x": "Bearer sample-token"})
            rows = workshop.load_jsonl(sink.path)
            self.assertEqual(len(rows), 2)
            self.assertNotIn("secret", sink.path.read_text())
            self.assertEqual(rows[1]["payload"]["x"], "Bearer [REDACTED]")

    def test_hosted_input_is_bounded(self):
        for value in ({}, {"query": ""}, {"query": "x" * 4001}, {"query": "ok", "approved": True}, {"query": "ok", "run_id": "../secret"}):
            with self.assertRaises(ValueError):
                hosted_runtime.validate_request(value)

    def test_raw_http_errors_cannot_pass(self):
        value, headers = hosted_client.parse_raw_http('HTTP/1.1 200 OK\r\nX-Ms-Agent-Version: 2\r\n\r\n{"ok":true}')
        self.assertTrue(value["ok"])
        self.assertEqual(headers["x-ms-agent-version"], "2")
        with self.assertRaises(RuntimeError):
            hosted_client.parse_raw_http('HTTP/1.1 502 Failed\n\n{"error":"upstream"}')
        with self.assertRaises(ValueError):
            hosted_client.parse_raw_http('{"response":"success-shaped non-HTTP"}')

    def test_responses_stream_requires_actual_terminal_event(self):
        body = 'event: response.completed\ndata: {"type":"response.completed","response":{"status":"completed","id":"unit"}}\n\n'
        raw = "HTTP/2.0 200 OK\nContent-Type: text/event-stream\n\n" + body
        value, _ = hosted_client.parse_raw_http(raw, allow_responses_stream=True)
        self.assertEqual(value["id"], "unit")
        with self.assertRaises(ValueError):
            hosted_client.parse_raw_http(raw.replace("response.completed", "response.output_text.delta"), allow_responses_stream=True)

class EvaluationContractTests(unittest.TestCase):
    def result(self, case_id, score, passed):
        return {"datasource_item": {"id": case_id}, "results": [{"name": "contoso_business", "score": score, "passed": passed}]}

    def test_native_contradiction_is_failure(self):
        result = evaluation_lab.audit_items([self.result("dev-01", 5, False)])
        self.assertEqual(result["contradictions"], ["dev-01"])
        self.assertFalse(result["business_gate_passed"])

    def test_native_missing_and_invalid_scores_rejected(self):
        for score, passed in ((None, True), (True, True), (4, "true"), (float("nan"), True)):
            with self.assertRaises(ValueError):
                evaluation_lab.audit_items([self.result("dev-01", score, passed)])

    def test_calibration_is_not_agent_quality(self):
        report = evaluation_lab.audit_items([self.result("cal-x", 1, False)], {"cal-x": False})
        self.assertTrue(report["calibration_passed"])
        self.assertTrue(report["not_target_agent_evidence"])
        self.assertFalse(report["human_review_completed"])
        self.assertFalse(report["business_gate_passed"])

    def test_optimizer_uses_only_dev_and_no_promotion(self):
        request = optimizer_lab.payload("contoso", "1", "judge", "optimizer")["inputs"]
        self.assertNotIn("validation_dataset", request)
        ids = {r["criteria"][0]["name"] for r in request["train_dataset"]["items"]}
        self.assertEqual(ids, {c["id"] for c in workshop.validate_data() if c["split"] == "dev"})
        self.assertEqual(request["options"]["max_candidates"], 2)
        self.assertIn("Contoso", request["options"]["optimization_config"]["system_prompt"])

    def test_partial_and_failed_records_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "partial.jsonl"
            path.write_text(json.dumps({"id": "dev-01", "status": "failed", "response": ""}) + "\n")
            with self.assertRaises(ValueError):
                evaluation_lab.prepare_rows(path, "dev")


class HostedTurnTests(unittest.TestCase):
    def test_exact_tool_call_result_and_model_version(self):
        call = Obj(type="function_call", name="prepare_purchase_request", arguments='{"sku":"NB-14","quantity":2}', call_id="call_unit")
        call.model_dump = lambda **_: {"type": "function_call", "name": call.name, "arguments": call.arguments, "call_id": call.call_id}
        first = Obj(id="resp_unit1", status="completed", output=[call], usage=Obj(input_tokens=20, output_tokens=10))
        final = Obj(id="resp_unit2", status="completed", output=[], output_text="초안이며 승인·주문은 하지 않았습니다.", usage=Obj(input_tokens=30, output_tokens=10), model="unit-model-version")
        client = Obj(responses=Obj(create=Mock(side_effect=[first, final])))
        sink = Obj(append=Mock())
        row = hosted_runtime.execute_turn(client, Mock(), "unit-model", {"query": "NB-14 2대 초안"}, sink, evidence.Budget())
        self.assertEqual(row["model"], "unit-model-version")
        self.assertEqual(row["tool_calls"][0]["call_id"], "call_unit")
        self.assertFalse(row["tool_calls"][0]["output"]["result"]["order_submitted"])
        self.assertEqual(row["input_tokens"], 50)

    def test_fabricated_citation_fails(self):
        result = Obj(id="resp_unit", status="completed", output=[], output_text="CONTOSO-PROC-2026-09-s2", usage=None)
        with self.assertRaisesRegex(RuntimeError, "never retrieved"):
            hosted_runtime.execute_turn(Obj(responses=Obj(create=Mock(return_value=result))), Mock(), "model",
                                        {"query": "정책"}, Obj(append=Mock()), evidence.Budget())


if __name__ == "__main__":
    unittest.main()
