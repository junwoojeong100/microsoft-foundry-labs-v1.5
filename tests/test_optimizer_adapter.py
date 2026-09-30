import importlib.util
import asyncio
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("optimizer_responses_adapter", ROOT / "hosted/optimizer_responses.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class OptimizerAdapterTests(unittest.TestCase):
    def test_instruction_only_candidate_explicitly_inherits_baseline_model(self):
        self.assertEqual(adapter.resolved_model(None, "approved-model", optimizer_overlay=True),
                         ("approved-model", "explicit_baseline_inheritance"))

    def test_invalid_baseline_or_explicit_empty_model_is_not_silently_defaulted(self):
        for model, baseline, overlay in [
            (None, "approved-model", False), ("", "approved-model", True),
            (None, "", True), (None, "CONFIGURE-MODEL-BEFORE-DEPLOY", True),
        ]:
            with self.assertRaises(ValueError):
                adapter.resolved_model(model, baseline, optimizer_overlay=overlay)

    def test_explicit_candidate_model_is_not_replaced(self):
        self.assertEqual(adapter.resolved_model("candidate-model", "baseline-model", optimizer_overlay=True),
                         ("candidate-model", "candidate"))


class OptimizerCancellationTests(unittest.IsolatedAsyncioTestCase):
    async def test_cancelled_request_waiting_for_gate_never_starts_inference(self):
        class Host:
            def response_handler(self, handler):
                self.handler = handler
                return handler

        class Stream:
            def __init__(self, **kwargs):
                pass

            def emit_created(self):
                return "created"

            def emit_in_progress(self):
                return "in_progress"

            def emit_incomplete(self, reason):
                return "incomplete:" + reason

        ready, release = asyncio.Event(), asyncio.Event()
        invocations = Mock()
        async def invoke(function, payload):
            invocations(payload)
            ready.set()
            await release.wait()
            return {"fixture": True}
        async def text():
            return "Synthetic question"
        async def consume(stream):
            return [event async for event in stream]
        module = SimpleNamespace(ResponsesAgentServerHost=Host, ResponseEventStream=Stream)
        with patch.dict(sys.modules, {"azure.ai.agentserver.responses": module}), \
                patch.object(adapter.asyncio, "to_thread", side_effect=invoke):
            app = adapter.create_app()
            context = SimpleNamespace(response_id="fixture", get_input_text=text)
            first_cancel, queued_cancel = asyncio.Event(), asyncio.Event()
            first = asyncio.create_task(consume(app.handler({}, context, first_cancel)))
            await ready.wait()
            queued = asyncio.create_task(consume(app.handler({}, context, queued_cancel)))
            await asyncio.sleep(0)
            queued_cancel.set()
            first_cancel.set()
            release.set()
            outputs = await asyncio.gather(first, queued)
        self.assertEqual(invocations.call_count, 1)
        self.assertEqual(outputs, [["created", "in_progress", "incomplete:cancelled"]] * 2)


if __name__ == "__main__":
    unittest.main()
