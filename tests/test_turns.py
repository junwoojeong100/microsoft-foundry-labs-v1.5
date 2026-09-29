import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace as Obj
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "samples"))
import prepare_tuning
import workshop as w


def response(output, text="", status="completed"):
    return Obj(
        id="resp_test", status=status, output=output, output_text=text,
        usage=Obj(input_tokens=100, output_tokens=30),
    )


class TurnTests(unittest.TestCase):
    def client(self, responses):
        client = Obj(
            conversations=Obj(create=Mock(return_value=Obj(id="conv_test"))),
            responses=Obj(create=Mock(side_effect=responses)),
        )
        return client

    def test_tool_result_returned_to_same_conversation(self):
        call = Obj(type="function_call", name="get_stock", arguments='{"sku":"NB-14"}', call_id="call_1")
        client = self.client([response([call]), response([], "실습 재고는 8개입니다.")])
        receipt = Obj(add=Mock())
        row = w.run_turn(client, "agent_test", "재고?", receipt)
        submitted = client.responses.create.call_args.kwargs
        self.assertEqual(submitted["conversation"], "conv_test")
        self.assertEqual(submitted["input"][0]["call_id"], "call_1")
        self.assertTrue(json.loads(submitted["input"][0]["output"])["ok"])
        self.assertIsNone(row["manual_pass"])
        self.assertEqual(row["input_tokens"], 200)

    def test_tool_error_is_explicit(self):
        call = Obj(type="function_call", name="prepare_purchase_request", arguments='{"sku":"MON-27","quantity":1}', call_id="call_1")
        client = self.client([response([call]), response([], "품절이어서 초안을 만들지 못했습니다.")])
        with contextlib.redirect_stderr(io.StringIO()) as errors:
            row = w.run_turn(client, "agent_test", "초안", Obj(add=Mock()))
        self.assertIn("TOOL_REJECTED", errors.getvalue())
        self.assertFalse(row["tool_calls"][0]["output"]["ok"])
        self.assertIn("No draft", row["tool_calls"][0]["output"]["error"]["message"])

    def test_retrieved_context_is_actual_not_answer_key(self):
        citation = Obj(model_dump=lambda: {"type": "file_citation", "file_id": "file_test"})
        retrieval = Obj(type="file_search_call", results=[Obj(text="실제 검색 결과")])
        message = Obj(type="message", content=[Obj(type="output_text", annotations=[citation])])
        row = w.run_turn(self.client([response([retrieval, message], "답변")]), "agent", "질문", Obj(add=Mock()))
        self.assertEqual(row["context"], "실제 검색 결과")
        self.assertEqual(row["citations"][0]["file_id"], "file_test")

    def test_incomplete_and_empty_output_do_not_pass(self):
        for output in (response([], "", "incomplete"), response([], " "), response([], "", "failed")):
            with self.assertRaises(RuntimeError):
                w.run_turn(self.client([output]), "agent", "질문", Obj(add=Mock()))

    def test_budget_stops_before_execution(self):
        calls = [
            Obj(type="function_call", name="get_stock", arguments='{"sku":"NB-14"}', call_id=str(index))
            for index in range(w.MAX_TOOL_CALLS + 1)
        ]
        with self.assertRaisesRegex(RuntimeError, "budget"):
            w.run_turn(self.client([response(calls)]), "agent", "질문", Obj(add=Mock()))

    def test_turn_limit(self):
        call = Obj(type="function_call", name="get_stock", arguments='{"sku":"NB-14"}', call_id="repeat")
        with self.assertRaisesRegex(RuntimeError, "Turn limit"):
            w.run_turn(self.client([response([call])] * w.MAX_ROUNDS), "agent", "질문", Obj(add=Mock()))


class IngestionTests(unittest.TestCase):
    def test_completed_ingestion(self):
        files = Obj(create=Mock(return_value=Obj(status="in_progress")), retrieve=Mock(return_value=Obj(status="completed")))
        client = Obj(vector_stores=Obj(files=files))
        with patch.object(w.time, "monotonic", side_effect=[0, 0, 2]), patch.object(w.time, "sleep"):
            w.index_file(client, "file_test", "vs_test")
        files.create.assert_called_once()
        files.retrieve.assert_called_once()
        self.assertEqual(files.retrieve.call_args.kwargs["file_id"], "file_test")

    def test_ingestion_failure_and_timeout_are_not_success(self):
        files = Obj(create=Mock(return_value=Obj(status="failed")), retrieve=Mock())
        client = Obj(vector_stores=Obj(files=files))
        with self.assertRaisesRegex(RuntimeError, "did not complete"):
            w.index_file(client, "file_test", "vs_test")
        files.create.return_value = Obj(status="in_progress")
        with patch.object(w.time, "monotonic", side_effect=[0, 181]), self.assertRaisesRegex(RuntimeError, "timed out"):
            w.index_file(client, "file_test", "vs_test")
        files.retrieve.assert_not_called()


class TuningTests(unittest.TestCase):
    def test_synthetic_training_format_and_no_overlap(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "tuning"
            self.assertEqual(prepare_tuning.prepare(target), (16, 8))
            train = w.load_jsonl(target / "train.jsonl")
            validation = w.load_jsonl(target / "validation.jsonl")
            self.assertTrue((target / "train.jsonl").read_bytes().startswith(b"\xef\xbb\xbf"))
            queries = lambda rows: {row["messages"][1]["content"] for row in rows}
            self.assertFalse(queries(train) & queries(validation))
            self.assertEqual(len(train), 16)
            self.assertTrue(all(row["messages"][0]["content"] == prepare_tuning.SYSTEM for row in train + validation))


if __name__ == "__main__":
    unittest.main()
