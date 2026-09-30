import json
from pathlib import Path
import sys
from types import SimpleNamespace as Obj
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
import hosted_runtime
from business_checks import check_business_evidence
from evidence import Budget
from search_lab import policy_chunks


def function_call(name, arguments, call_id):
    call = Obj(type="function_call", name=name, arguments=json.dumps(arguments), call_id=call_id)
    call.model_dump = lambda **_: {
        "type": "function_call", "name": call.name, "arguments": call.arguments, "call_id": call.call_id,
    }
    return call


def response(identifier, calls=(), text=""):
    return Obj(id=identifier, status="completed", output=list(calls), output_text=text, usage=None, model="fixture")


class SequentialToolTests(unittest.TestCase):
    def run_turn(self, first, second):
        source_id = "CONTOSO-PROC-2026-09-s3"
        final = response("final", text=json.dumps({
            "answer": "One draft requires human approval; no order or payment was made.",
            "citation_ids": [source_id],
        }))
        attribution = response("attribution", text=json.dumps({"citation_ids": [source_id]}))
        client = Obj(responses=Obj(create=Mock(side_effect=[
            response("first", first), response("second", second), final, attribution,
        ])))
        search = Obj(retrieve=Mock(return_value=policy_chunks()), policy_scope=Mock(return_value=[]))
        row = hosted_runtime.execute_turn(
            client, search, "fixture", {"query": "First check KB-01 stock, then create one draft for quantity 10."},
            Obj(append=Mock()), Budget(),
        )
        return row, client

    def test_stock_then_draft_finishes_before_a_separate_grounded_answer(self):
        row, client = self.run_turn(
            [function_call("get_stock", {"sku": "KB-01"}, "stock")],
            [function_call("prepare_purchase_request", {"sku": "KB-01", "quantity": 10}, "draft")],
        )
        drafts = [call for call in row["tool_calls"] if call["name"] == "prepare_purchase_request"]
        self.assertEqual(len(drafts), 1)
        self.assertTrue(drafts[0]["output"]["ok"])
        self.assertEqual(drafts[0]["output"]["result"]["quantity"], 10)
        final = client.responses.create.call_args_list[2].kwargs
        self.assertEqual(final["tools"], [])
        self.assertEqual(final["tool_choice"], "none")
        self.assertTrue(all(item["role"] == "user" for item in final["input"]))
        evidence = json.loads(final["input"][0]["content"])
        self.assertTrue(any(call["call_id"] == "draft" for call in evidence["tool_results"]))
        self.assertTrue(check_business_evidence(row, {"required_tools": ["prepare_purchase_request"]})["passed"])

    def test_duplicate_draft_is_rejected_and_linked_to_the_real_first_call(self):
        original = hosted_runtime.dispatch_tool
        with patch.object(hosted_runtime, "dispatch_tool", wraps=original) as dispatch:
            row, _ = self.run_turn(
                [function_call("prepare_purchase_request", {"sku": "KB-01", "quantity": 10}, "draft-first")],
                [function_call("prepare_purchase_request", {"quantity": 10, "sku": "KB-01"}, "draft-repeat")],
            )
        self.assertEqual(sum(call.args[0] == "prepare_purchase_request" for call in dispatch.call_args_list), 1)
        duplicate = row["tool_calls"][-1]
        self.assertEqual(duplicate["execution"], "rejected_before_execution")
        self.assertEqual(duplicate["duplicate_of"], "draft-first")
        self.assertFalse(duplicate["output"]["ok"])
        self.assertTrue(check_business_evidence(row, {"required_tools": ["prepare_purchase_request"]})["passed"])
        duplicate["duplicate_of"] = "not-executed"
        self.assertFalse(check_business_evidence(row, {})["passed"])


if __name__ == "__main__":
    unittest.main()
