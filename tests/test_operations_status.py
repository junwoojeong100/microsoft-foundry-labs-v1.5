from contextlib import contextmanager, redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import operations_status as operations


class OperationsStatusTests(unittest.TestCase):
    def test_custom_routine_receipts_are_discovered_without_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "custom-scheduled.json").write_text(json.dumps({
                "schema": "contoso-routine-v2", "name": "owned-timer", "endpoint": "fixture-endpoint",
            }))
            (root / "manifest.json").write_text('{"triggers":{}}')
            with patch.object(operations, "RESULTS", root):
                rows = operations.routine_receipts("fixture-endpoint")
                self.assertEqual([row["name"] for row in rows], ["owned-timer"])
                self.assertEqual(rows[0]["receipt_file"], "custom-scheduled.json")
                with self.assertRaisesRegex(ValueError, "mismatch"):
                    operations.routine_receipts("another-endpoint")

    def run_closeout(self, *, enabled=False):
        project = MagicMock()
        project.agents.list.return_value = [SimpleNamespace(name="contoso-purchasing")]
        project.agents.get.return_value.versions.latest.version = "1"
        project.agents.list_sessions.return_value = [
            SimpleNamespace(agent_session_id="owned-session", status="idle", stopped_at=None),
        ]
        project.beta.agents.list_optimization_jobs.return_value = []
        project.beta.schedules.list.return_value = []
        project.beta.agent_insight_monitors.list.return_value = []

        @contextmanager
        def client(evidence):
            yield project, None, "fixture-endpoint", "fixture-model"

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "arbitrary-receipt.json").write_text(json.dumps({
                "schema": "contoso-routine-v2", "name": "owned-timer", "endpoint": "fixture-endpoint",
            }))
            with patch.object(operations, "RESULTS", root), \
                    patch.object(operations, "owned", return_value={
                        "resource_group": "owned-rg", "project_endpoint": "fixture-endpoint",
                    }), patch.object(operations, "project_client", client), \
                    patch.object(operations, "Evidence"), \
                    patch.object(operations, "azd", return_value={"name": "owned-timer", "enabled": enabled}) as azd, \
                    redirect_stdout(io.StringIO()):
                if enabled:
                    with self.assertRaisesRegex(RuntimeError, "Active work remains"):
                        operations.main()
                else:
                    operations.main()
            report = json.loads((root / "operations-status.json").read_text())
        project.agents.get.assert_called_once_with("contoso-purchasing")
        self.assertEqual(azd.call_args.args[2:], ("show", "owned-timer"))
        return report

    def test_optional_undeployed_adapter_is_not_required_for_closeout(self):
        report = self.run_closeout()
        self.assertEqual(report["not_deployed_agents"], ["contoso-purchasing-responses"])
        self.assertFalse(report["active_work_observed"])
        self.assertFalse(report["resources_deleted"])
        self.assertFalse(report["quality_evaluation_performed"])

    def test_custom_active_routine_blocks_closeout_and_is_preserved(self):
        report = self.run_closeout(enabled=True)
        self.assertTrue(report["active_work_observed"])
        self.assertTrue(report["routines"][0]["enabled"])


if __name__ == "__main__":
    unittest.main()
