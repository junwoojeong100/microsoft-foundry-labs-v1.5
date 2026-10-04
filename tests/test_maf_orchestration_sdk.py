"""Exercise real orchestration builders with a deterministic, non-network chat client."""

import asyncio
import importlib.util
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
import multi_agent

SDK_AVAILABLE = importlib.util.find_spec("agent_framework_orchestrations") is not None
if SDK_AVAILABLE:
    from agent_framework import (
        AgentFrameworkException, BaseChatClient, ChatMiddlewareLayer, ChatResponse,
        Content, FunctionInvocationLayer, Message,
    )

    class RecordingClient(FunctionInvocationLayer, ChatMiddlewareLayer, BaseChatClient):
        def __init__(self):
            super().__init__()
            self.calls = []
            self.active = 0
            self.maximum_active = 0

        async def _inner_get_response(self, *, messages, stream, options, **kwargs):
            if stream:
                raise ValueError("This test client does not simulate streaming.")
            instruction = str(options.get("instructions", "")) + "\n" + "\n".join(message.text for message in messages)
            roles = re.findall(r"Role: ([a-z-]+)\.", instruction)
            if not roles:
                raise ValueError("Test request has no role label.")
            role = roles[0]
            index = len(self.calls) + 1
            self.calls.append({"role": role, "messages": [message.to_dict() for message in messages],
                               "instructions": options.get("instructions")})
            self.active += 1
            self.maximum_active = max(self.maximum_active, self.active)
            try:
                await asyncio.sleep(0.01)
                if role == "coordinator":
                    tools = [tool.name for tool in options.get("tools", [])]
                    if "handoff_to_policy" not in tools:
                        raise ValueError("The real HandoffBuilder did not expose its routing tool.")
                    contents = [Content.from_function_call(
                        call_id=f"fixture-call-{index}", name="handoff_to_policy", arguments={},
                    )]
                    finish = "tool_calls"
                else:
                    contents = [Content.from_text(f"Synthetic fixture from {role}, call {index}.")]
                    finish = "stop"
                return ChatResponse(
                    messages=[Message(role="assistant", contents=contents, author_name=role)],
                    response_id=f"fixture-response-{index}", finish_reason=finish,
                    usage_details={"input_token_count": 10, "output_token_count": 5},
                )
            finally:
                self.active -= 1


@unittest.skipUnless(SDK_AVAILABLE, "Install requirements-advanced.txt to run the real SDK checks.")
class OrchestrationSDKTests(unittest.TestCase):
    def run_pattern(self, mode, *, policy="Synthetic Contoso policy.", max_calls=None):
        async def exercise():
            client = RecordingClient()
            evidence = Mock()
            audit = multi_agent.CallAudit(evidence, max_calls or multi_agent.CALLS[mode], interval=0)
            report = await multi_agent.compare_paths(
                client, mode, "Explain the synthetic purchasing policy.", evidence, policy=policy, audit=audit,
            )
            return client, audit, report
        return asyncio.run(exercise())

    def test_sequential_forwards_the_actual_draft_to_the_reviewer(self):
        client, audit, report = self.run_pattern("sequential")
        self.assertEqual([item["role"] for item in client.calls], ["drafter", "reviewer"])
        history = str(client.calls[1]["messages"])
        self.assertIn("Synthetic fixture from drafter", history)
        self.assertEqual(len(audit.records), len(client.calls))
        self.assertEqual(len(report["paths"]["sequential"]["stages"]), 2)

    def test_concurrent_fans_out_and_preserves_all_three_originals(self):
        client, audit, report = self.run_pattern("concurrent")
        self.assertEqual({item["role"] for item in client.calls}, {"policy", "budget", "risk"})
        self.assertGreaterEqual(client.maximum_active, 2)
        self.assertEqual(len(audit.records), 3)
        self.assertEqual(len(report["paths"]["concurrent"]["final_messages"]), 3)

    def test_group_chat_returns_to_the_drafter_after_review(self):
        client, audit, report = self.run_pattern("group-chat")
        self.assertEqual([item["role"] for item in client.calls], ["drafter", "reviewer", "drafter"])
        self.assertIn("Synthetic fixture from reviewer", str(client.calls[2]["messages"]))
        self.assertEqual(len(audit.records), 3)
        self.assertFalse(report["quality_release"])

    def test_handoff_uses_the_sdk_tool_and_invokes_a_specialist(self):
        client, audit, report = self.run_pattern("handoff")
        self.assertEqual([item["role"] for item in client.calls], ["coordinator", "policy"])
        self.assertEqual(len(audit.records), len(client.calls))
        self.assertIn("handoff_to_policy", audit.records[0]["handoff_calls"])
        self.assertFalse(report["paths"]["handoff"]["human_approval_performed"])

    def test_compare_preserves_the_single_plus_sequential_baseline(self):
        client, audit, report = self.run_pattern("compare")
        self.assertEqual([item["role"] for item in client.calls], ["drafter", "drafter", "reviewer"])
        self.assertEqual(client.calls[0]["instructions"], client.calls[1]["instructions"])
        self.assertEqual([item["role"] for item in audit.records], ["single", "drafter", "reviewer"])
        self.assertEqual(len(audit.records), 3)
        self.assertEqual(report["sequential_minus_single"]["total_tokens"], 15)

    def test_request_budget_stops_before_an_extra_backend_call(self):
        async def exercise():
            client = RecordingClient()
            evidence = Mock()
            audit = multi_agent.CallAudit(evidence, 1, interval=0)
            with self.assertRaises((RuntimeError, AgentFrameworkException)):
                await multi_agent.compare_paths(
                    client, "sequential", "Synthetic question.", evidence, policy="Synthetic policy.", audit=audit,
                )
            self.assertEqual(len(client.calls), 1)
        asyncio.run(exercise())

    def test_input_budget_includes_agent_instructions_before_any_backend_call(self):
        async def exercise():
            client = RecordingClient()
            evidence = Mock()
            audit = multi_agent.CallAudit(evidence, 2, interval=0)
            with self.assertRaises((ValueError, RuntimeError, AgentFrameworkException)):
                await multi_agent.compare_paths(
                    client, "sequential", "Synthetic question.", evidence, policy="x" * 30_000, audit=audit,
                )
            self.assertEqual(client.calls, [])
        asyncio.run(exercise())


if __name__ == "__main__":
    unittest.main()
