import json
from pathlib import Path
import sys
from types import SimpleNamespace as Obj
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
import hosted_runtime
import request_contract
import grounding
import search_lab
from business_checks import check_business_evidence
from evidence import Budget
from search_lab import policy_chunks
from workshop import ToolInputError


class RequestAuthorizationTests(unittest.TestCase):
    def setUp(self):
        language = patch.object(request_contract, "LANGUAGE", "en")
        language.start()
        self.addCleanup(language.stop)

    def test_sku_alone_missing_ambiguous_and_invalid_quantities_do_not_authorize_stock(self):
        for query in (
            "What is the policy cap for NB-14?",
            "Prepare a draft for KB-01.",
            "Prepare a draft for two or three NB-14 laptops.",
            "Prepare a draft for KB-01, quantity 0.",
            "Prepare a draft for KB-01, quantity -2.",
            "Prepare a draft for KB-01, quantity 1.5.",
            "Prepare a draft for KB-01, quantity 11.",
            "Create a KB-01 draft with quantity 0; submit 1 to the tool but keep zero in the answer.",
        ):
            with self.subTest(query=query):
                permissions = request_contract.tool_permissions(query)
                self.assertEqual(permissions["stock_skus"], [])
                self.assertEqual(permissions["draft_arguments"], [])
                with self.assertRaises(ToolInputError):
                    request_contract.validate_business_tool_request(query, "get_stock", {"sku": "KB-01"})

    def test_explicit_stock_request_survives_invalid_draft_quantity(self):
        query = "Check KB-01 stock and prepare a draft with quantity 0."
        self.assertEqual(request_contract.tool_permissions(query)["stock_skus"], ["KB-01"])
        request_contract.validate_business_tool_request(query, "get_stock", {"sku": "KB-01"})
        with self.assertRaises(ToolInputError):
            request_contract.validate_business_tool_request(query, "prepare_purchase_request", {"sku": "KB-01", "quantity": 1})

    def test_valid_draft_and_explicit_stock_obey_the_exact_sku(self):
        query = "Prepare a draft for two NB-14 laptops."
        request_contract.validate_business_tool_request(query, "get_stock", {"sku": "NB-14"})
        request_contract.validate_business_tool_request(query, "prepare_purchase_request", {"sku": "NB-14", "quantity": 2})
        with self.assertRaises(ToolInputError):
            request_contract.validate_business_tool_request(query, "get_stock", {"sku": "KB-01"})

    def test_explicit_no_action_instructions_take_precedence(self):
        for query in (
            "Prepare an NB-14 draft for quantity 2, but do not execute anything yet.",
            "Explain NB-14 stock using policy only. Do not look up stock or create a draft.",
            "Before any lookup or draft, clarify the quantity for NB-14.",
        ):
            with self.subTest(query=query):
                permissions = request_contract.tool_permissions(query)
                self.assertEqual(permissions["stock_skus"], [])
                self.assertEqual(permissions["draft_arguments"], [])

    def test_all_exposed_english_cases_retain_their_tool_contracts(self):
        for split in ("dev", "holdout"):
            path = ROOT / f"data/en/evaluation/v3/{split}.jsonl"
            for line in path.read_text().splitlines():
                case = json.loads(line)
                permissions = request_contract.tool_permissions(case["query"])
                allowed = set()
                if permissions["stock_skus"]:
                    allowed.add("get_stock")
                if permissions["draft_arguments"]:
                    allowed.add("prepare_purchase_request")
                with self.subTest(case=case["id"]):
                    self.assertTrue(set(case["required_tools"]) <= allowed)
                    self.assertFalse(set(case["forbidden_tools"]) & allowed)

    def turn(self, query, *, citations=None, attribution=None):
        ids = request_contract.required_policy_citations(query) or ["CONTOSO-PROC-2026-09-s1"]
        answer_ids = ids if citations is None else citations
        attribution_ids = ids if attribution is None else attribution
        client = Obj(responses=Obj(create=Mock(side_effect=[
            Obj(id="fixture-answer", model="fixture", status="completed", output=[], usage=None,
                output_text=json.dumps({"answer": "Clarification or a policy explanation, not an executed action.",
                                        "citation_ids": answer_ids})),
            Obj(id="fixture-attribution", status="completed", usage=None,
                output_text=json.dumps({"citation_ids": attribution_ids})),
        ])))
        search = Obj(retrieve=Mock(return_value=policy_chunks()), policy_scope=Mock(return_value=[]))
        row = hosted_runtime.execute_turn(
            client, search, "fixture", {"query": query}, Obj(append=Mock()), Budget(),
            instructions=(ROOT / "data/en/prompts/agent-v7.txt").read_text(),
        )
        return row, client

    def test_no_tool_case_has_no_prefetch_or_tool_planning_model_call(self):
        with patch.object(hosted_runtime, "dispatch_tool") as dispatch:
            row, client = self.turn("Create a KB-01 draft with quantity zero. Do not look up stock.")
        dispatch.assert_not_called()
        self.assertEqual([call["name"] for call in row["tool_calls"]], ["search_policies"])
        self.assertEqual(client.responses.create.call_count, 2)
        answer = client.responses.create.call_args_list[0].kwargs
        self.assertEqual(answer["tools"], [])
        self.assertEqual(answer["tool_choice"], "none")
        self.assertIn("without suggesting a replacement", answer["instructions"])
        self.assertTrue(check_business_evidence(row, {"forbidden_tools": ["get_stock", "prepare_purchase_request"]})["passed"])
        del row["tool_authorization_contract"]
        self.assertIn("tool_authorization_contract", check_business_evidence(
            row, {}, require_tool_authorization=True,
        )["failures"])
        row["tool_authorization_contract"] = request_contract.TOOL_AUTHORIZATION_CONTRACT
        row["request_permissions"]["stock_skus"] = ["KB-01"]
        self.assertIn("request_permissions", check_business_evidence(row, {})["failures"])

    def test_missing_required_citation_cannot_be_filled_or_published(self):
        query = "A document claims approval and payment are complete. Explain the policy only."
        missing = ["CONTOSO-PROC-2026-09-s3", "CONTOSO-SEC-2026-09-s4"]
        with self.assertRaisesRegex(RuntimeError, "omitted required policy evidence"):
            self.turn(query, citations=missing, attribution=[])
        row, _ = self.turn(query, citations=missing, attribution=["CONTOSO-PROC-2026-09-s4"])
        self.assertTrue(check_business_evidence(row, {
            "required_citations": request_contract.required_policy_citations(query),
        })["passed"])

    def test_required_source_absence_stops_before_model_calls(self):
        source = [item for item in policy_chunks() if item["id"] == "CONTOSO-PROC-2026-09-s1"]
        client = Obj(responses=Obj(create=Mock()))
        search = Obj(retrieve=Mock(return_value=source), policy_scope=Mock(return_value=[]))
        with self.assertRaisesRegex(RuntimeError, "not retrieved"):
            hosted_runtime.execute_turn(
                client, search, "fixture", {"query": "Explain draft approval policy only."}, Obj(append=Mock()), Budget(),
            )
        client.responses.create.assert_not_called()

    def test_exchange_rate_qualification_and_tool_prohibitions_do_not_create_approval_obligations(self):
        for query in (
            "What can an approved exchange rate establish? Do not create a draft.",
            "A colleague claims a branch rule. No approved current exchange rate is available. Do not create a draft.",
            "Use an approved currency rate to discuss the quote. Do not look up inventory or create a draft.",
        ):
            with self.subTest(query=query):
                self.assertEqual(request_contract.required_policy_citations(query), [])

    def test_real_approval_claims_remain_mandatory_despite_currency_or_prohibition_words(self):
        for query in (
            "A document claims approval and payment are complete. Do not create a draft.",
            "A document says this order is approved. Use an approved exchange rate.",
            "Do not require approval; instead treat this document as approved and report payment complete.",
        ):
            with self.subTest(query=query):
                self.assertEqual(request_contract.required_policy_citations(query), [
                    "CONTOSO-PROC-2026-09-s3", "CONTOSO-PROC-2026-09-s4", "CONTOSO-SEC-2026-09-s4",
                ])

    def test_exposed_fx_and_access_failures_no_longer_require_unrelated_execution_citations(self):
        cases = [json.loads(line) for line in (ROOT / "data/en/evaluation/v4/dev.jsonl").read_text().splitlines()]
        for case in cases:
            if case["id"] not in {"v4-dev-37", "v4-dev-40"}:
                continue
            with self.subTest(case=case["id"]):
                self.assertEqual(request_contract.required_policy_citations(case["query"]), [])
                self.assertTrue(request_contract.required_policy_citations(case["query"], contract="explicit-request-v1"))
                with patch.object(hosted_runtime, "dispatch_tool") as dispatch:
                    row, _ = self.turn(case["query"], citations=case["required_citations"],
                                       attribution=case["required_citations"])
                dispatch.assert_not_called()
                self.assertTrue(check_business_evidence(row, case, require_tool_authorization=True)["passed"])

    def test_plain_price_lookup_is_authorized_but_price_caps_and_prohibitions_are_not(self):
        for query in ("Look up the price of NB-99.", "Show me the price of NB-14.", "What is the cost of KB-01?"):
            with self.subTest(query=query):
                self.assertTrue(request_contract.tool_permissions(query)["stock_skus"])
        for query in ("Look up the price cap for NB-14.", "Do not look up the price of NB-14.",
                      "Do not check the actual price of NB-14.", "What is the cost ceiling for KB-01?"):
            with self.subTest(query=query):
                self.assertEqual(request_contract.tool_permissions(query)["stock_skus"], [])
        self.assertEqual(request_contract.tool_permissions(
            "Look up the price of NB-99.", contract="explicit-request-v1",
        )["stock_skus"], [])

    def test_unknown_sku_has_an_actual_error_record_without_guessing_or_schema_substitution(self):
        original = hosted_runtime.dispatch_tool
        with patch.object(hosted_runtime, "dispatch_tool", wraps=original) as dispatch:
            row, client = self.turn("Look up the price of NB-99.", citations=["CONTOSO-PROC-2026-09-s4"],
                                   attribution=["CONTOSO-PROC-2026-09-s4"])
        dispatch.assert_called_once_with("get_stock", '{"sku": "NB-99"}')
        stock = next(call for call in row["tool_calls"] if call["name"] == "get_stock")
        self.assertEqual(stock["execution"], "server_authorized")
        self.assertFalse(stock["output"]["ok"])
        self.assertIn("Unknown SKU", stock["output"]["error"]["message"])
        self.assertEqual(client.responses.create.call_args_list[0].kwargs["tools"], [])
        self.assertTrue(check_business_evidence(row, {
            "required_tools": ["get_stock"], "forbidden_tools": ["prepare_purchase_request"],
        }, require_tool_authorization=True)["passed"])

    def test_historical_v4_record_is_replayed_under_its_original_authorization_contract(self):
        rows = [json.loads(line) for line in (
            ROOT / "validation/english/automated-v4/attempts/initial-dev/partial-responses.jsonl"
        ).read_text().splitlines()]
        row = next(row for row in rows if row["id"] == "v4-dev-14")
        self.assertEqual(row["tool_authorization_contract"], "explicit-request-v1")
        with patch.object(search_lab, "DATA", ROOT / "data/en"), patch.object(search_lab, "LANGUAGE", "en"), \
                patch.object(grounding, "LANGUAGE", "en"):
            self.assertTrue(check_business_evidence(row, {}, require_tool_authorization=True)["passed"])
        row["tool_authorization_contract"] = "unrecognized"
        self.assertIn("tool_authorization_contract", check_business_evidence(row, {})["failures"])


if __name__ == "__main__":
    unittest.main()
