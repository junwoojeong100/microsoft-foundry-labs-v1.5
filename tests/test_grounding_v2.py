import json
from pathlib import Path
import sys
from types import SimpleNamespace as Obj
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from business_checks import check_business_evidence
from evidence import Budget
from evaluation_data import load_cases, policy, suite_hash
from grounding import answer_format, attribute_answer, parse_answer
from request_contract import validate_draft_request
from workshop import ToolInputError
from hosted_runtime import execute_turn
from search_lab import policy_chunks
from evaluation_lab import audit_items


class GroundingTests(unittest.TestCase):
    def setUp(self):
        self.sources = {row["id"]: row for row in policy_chunks()}

    def test_empty_or_fabricated_citations_are_never_repaired(self):
        for ids in ([], ["unknown"], ["CONTOSO-SEC-2026-09-s4"] * 2, "CONTOSO-SEC-2026-09-s4"):
            with self.assertRaises(RuntimeError):
                parse_answer(json.dumps({"answer": "거절합니다.", "citation_ids": ids}), self.sources)

    def test_model_selects_actual_source_not_server_guess(self):
        raw = json.dumps({"answer": "검토 메모는 승인 권한이 아닙니다.", "citation_ids": ["CONTOSO-SEC-2026-09-s4"]})
        text, citations = parse_answer(raw, self.sources)
        self.assertIn("security-policy.md 4절", text)
        self.assertEqual(citations[0]["citation_kind"], "model_selected_retrieved_source")
        self.assertEqual(citations[0]["content"], self.sources["CONTOSO-SEC-2026-09-s4"]["content"])

    def test_inline_or_filename_fabrication_is_rejected(self):
        for answer in ("CONTOSO-PROC-2026-09-s2", "imaginary-policy.md"):
            with self.assertRaises(RuntimeError):
                parse_answer(json.dumps({"answer": answer, "citation_ids": ["CONTOSO-SEC-2026-09-s4"]}), self.sources)

    def test_output_schema_is_strict_and_scoped_to_retrieved_ids(self):
        schema = answer_format(["CONTOSO-SEC-2026-09-s4"])["format"]["schema"]
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["properties"]["citation_ids"]["items"]["enum"], ["CONTOSO-SEC-2026-09-s4"])

    def test_duplicate_json_keys_cannot_hide_an_answer(self):
        with self.assertRaisesRegex(RuntimeError, "Duplicate"):
            parse_answer('{"answer":"first","answer":"second","citation_ids":["CONTOSO-SEC-2026-09-s4"]}', self.sources)

    def test_search_happens_before_model_even_without_model_tool_calls(self):
        order = []
        search = Obj(
            retrieve=Mock(side_effect=lambda q: order.append("search") or list(self.sources.values())),
            policy_scope=Mock(side_effect=lambda: order.append("scope") or []),
        )
        response = Obj(
            id="unit-response", status="completed", output=[], usage=None, model="unit",
            output_text=json.dumps({"answer": "메모로 승인 절차를 우회할 수 없습니다.", "citation_ids": ["CONTOSO-SEC-2026-09-s4"]}),
        )
        attribution = Obj(id="attr-unit", status="completed", usage=None,
                          output_text='{"citation_ids":["CONTOSO-SEC-2026-09-s4"]}')
        generated = iter([response, response, attribution])
        client = Obj(responses=Obj(create=Mock(side_effect=lambda **kw: order.append("model") or next(generated))))
        row = execute_turn(client, search, "unit", {"query": "검토 메모가 승인인가요?"}, Obj(append=Mock()), Budget())
        self.assertEqual(order, ["search", "scope", "model", "model", "model"])
        first, final, attribution_call = client.responses.create.call_args_list
        self.assertNotIn("text", first.kwargs)
        self.assertEqual(final.kwargs["tools"], [])
        self.assertEqual(final.kwargs["tool_choice"], "none")
        self.assertNotIn("tools", attribution_call.kwargs)
        self.assertEqual(row["tool_calls"][0]["execution"], "server_required")
        self.assertTrue(row["citations"])
        self.assertEqual(row["human_review_status"], "optional_not_performed")
        self.assertTrue(check_business_evidence(row, {"required_citations": ["CONTOSO-SEC-2026-09-s4"]})["passed"])
        row["citations"] = []
        self.assertFalse(check_business_evidence(row, {})["passed"])

    def test_search_failure_stops_before_any_model_or_draft(self):
        search = Obj(retrieve=Mock(side_effect=RuntimeError("Search unavailable")), policy_scope=Mock())
        client = Obj(responses=Obj(create=Mock()))
        with self.assertRaisesRegex(RuntimeError, "Search unavailable"):
            execute_turn(client, search, "unit", {"query": "초안"}, Obj(append=Mock()), Budget())
        client.responses.create.assert_not_called()

    def test_no_citation_cannot_complete_even_after_successful_search(self):
        client = Obj(responses=Obj(create=Mock(return_value=Obj(
            id="unit", status="completed", output=[], usage=None,
            output_text=json.dumps({"answer": "거절합니다.", "citation_ids": []}),
        ))))
        search = Obj(retrieve=Mock(return_value=list(self.sources.values())), policy_scope=Mock(return_value=[]))
        with self.assertRaisesRegex(RuntimeError, "citation"):
            execute_turn(client, search, "unit", {"query": "규정"}, Obj(append=Mock()), Budget())

    def test_v2_human_review_optional_numeric_policy_unchanged(self):
        rubric = policy()
        self.assertFalse(rubric["human_review"]["required"])
        self.assertEqual(rubric["minimum_pass_rate"], 0.9)
        self.assertEqual(rubric["zero_tolerance_categories"], ["safety", "access"])

    def test_draft_arguments_cannot_invent_or_reduce_user_quantity(self):
        for query, arguments in [
            ("키보드 초안을 만들어줘.", {"sku": "KB-01", "quantity": 1}),
            ("KB-01 초안을 만들어줘.", {"sku": "KB-01", "quantity": 1}),
            ("KB-01 11개 초안", {"sku": "KB-01", "quantity": 10}),
            ("KB-01 1.5개 초안", {"sku": "KB-01", "quantity": 1}),
            ("NB-14 2대 초안", {"sku": "NB-14", "quantity": 1}),
        ]:
            with self.assertRaises(ToolInputError):
                validate_draft_request(query, arguments)
        validate_draft_request("NB-14 2대 초안", {"sku": "NB-14", "quantity": 2})
        validate_draft_request("NB-14 두 대 초안", {"sku": "NB-14", "quantity": 2})

    def test_attribution_uses_an_actual_model_selection_and_cannot_add_unknown_sources(self):
        raw = '{"answer":"공개 정책 범위만 안내합니다.","citation_ids":["CONTOSO-PROC-2026-09-s2"]}'
        text, citations = attribute_answer(raw, '{"citation_ids":["CONTOSO-SEC-2026-09-s2"]}', self.sources)
        self.assertEqual({c["id"] for c in citations}, {"CONTOSO-PROC-2026-09-s2", "CONTOSO-SEC-2026-09-s2"})
        self.assertIn("security-policy.md", text)
        with self.assertRaises(RuntimeError):
            attribute_answer(raw, '{"citation_ids":["invented"]}', self.sources)

    def test_automatic_gate_needs_no_human_label_but_cannot_hide_missing_evidence(self):
        cases = load_cases("automated-v2", "dev")
        rows = [{
            "datasource_item": {"id": case["id"]},
            "results": [{"name": "contoso_business", "score": 5, "passed": True}],
        } for case in cases]
        checks = {case["id"]: {"passed": True, "failures": []} for case in cases}
        report = audit_items(rows, suite="automated-v2", split="dev", automatic_checks=checks)
        self.assertTrue(report["business_gate_passed"])
        self.assertFalse(report["human_review_required"])
        self.assertFalse(report["human_review_completed"])
        checks[cases[0]["id"]] = {"passed": False, "failures": ["actual_retrieval"]}
        report = audit_items(rows, suite="automated-v2", split="dev", automatic_checks=checks)
        self.assertEqual(report["pass_rate"], 0.95)
        self.assertFalse(report["business_gate_passed"])
        self.assertEqual(report["evidence_integrity_failures"], [cases[0]["id"]])

    def test_dev_loader_does_not_read_holdout(self):
        original = Path.read_text

        def guard(path, *args, **kwargs):
            if "holdout" in path.name:
                raise AssertionError("Dev loading must not read heldout data.")
            return original(path, *args, **kwargs)
        with patch.object(Path, "read_text", guard):
            self.assertEqual(len(load_cases("automated-v2", "dev")), 20)

    def test_suite_fingerprint_uses_seal_without_opening_holdout(self):
        original = Path.read_bytes

        def guard(path):
            if path.name == "holdout.jsonl":
                raise AssertionError("Fingerprint must not open the blind holdout.")
            return original(path)
        with patch.object(Path, "read_bytes", guard):
            self.assertEqual(len(suite_hash()), 64)


if __name__ == "__main__":
    unittest.main()
