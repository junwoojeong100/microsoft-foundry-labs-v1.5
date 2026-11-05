"""Exercise real orchestration builders with a deterministic, non-network chat client."""

import asyncio
import importlib.util
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
import multi_agent

SDK_AVAILABLE = importlib.util.find_spec("agent_framework_orchestrations") is not None
if SDK_AVAILABLE:
    from agent_framework import (
        AgentFrameworkException,
    )
    from maf_fixture import FixtureChatClient as RecordingClient, run_fixture


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

    def test_offline_cli_runs_all_patterns_without_cloud_configuration(self):
        for mode, calls in (("sequential", 2), ("concurrent", 3), ("group-chat", 3), ("handoff", 2)):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary, patch.dict(
                "os.environ", {"CONTOSO_EVIDENCE_DIRECTORY": temporary},
            ), patch.object(multi_agent, "read_config") as config, patch.object(
                multi_agent, "check_ready",
            ) as readiness, contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(multi_agent.main(["--mode", mode, "--offline"]), 0)
                report = json.loads(output.getvalue().split("\nEvidence: ", 1)[0])
                self.assertEqual(report["fixture_calls"], calls)
                self.assertEqual(report["execution"], "local_sdk_fixture")
                self.assertEqual(report["azure_calls"], 0)
                self.assertEqual(report["usage_source"], "synthetic_fixture_not_billing")
                self.assertFalse(report["quality_release"])
                records = [json.loads(line) for path in Path(temporary).glob("*.jsonl") for line in path.read_text().splitlines()]
                self.assertEqual(records[-1]["event"], "completed")
                self.assertEqual(records[-1]["payload"]["execution"], "local_sdk_fixture")
                config.assert_not_called()
                readiness.assert_not_called()

    def test_offline_and_live_cannot_be_combined(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            multi_agent.main(["--offline", "--live"])

    def test_offline_network_guard_is_active_during_real_workflow_execution(self):
        import socket

        async def attempt(*args, **kwargs):
            socket.getaddrinfo("contract.invalid", 443)
        with patch.object(multi_agent, "compare_paths", side_effect=attempt), self.assertRaisesRegex(
            RuntimeError, "forbid DNS",
        ):
            asyncio.run(run_fixture("sequential", "purchase", Mock()))


if __name__ == "__main__":
    unittest.main()
