from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace as Obj
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
import optimizer_lab

ENDPOINT = "https://owned.services.ai.azure.com/api/projects/workshop"


def session(identifier, *, version="2", created=150, candidate=None):
    indicator = {"type": "version_ref", "agent_version": version}
    if candidate:
        indicator.update(type="candidate_ref", candidate_id=candidate)
    return {"agent_session_id": identifier, "version_indicator": indicator, "created_at": created, "status": "active"}


class OptimizerReconciliationTests(unittest.TestCase):
    def setUp(self):
        sdk_errors = patch.dict(sys.modules, {"azure.core.exceptions": Obj(AzureError=RuntimeError)})
        sdk_errors.start()
        self.addCleanup(sdk_errors.stop)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / ".build", prefix="optimizer-reconcile-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.evidence = Obj(append=Mock(), failure=Mock(), run_id="contoso-optimizer-fixture")
        self.job = {"id": "opt_fixture", "status": "cancelled", "created_at": 100, "updated_at": 200}
        self.project = Mock()
        for target, value in (("RESULTS", self.root),):
            patcher = patch.object(optimizer_lab, target, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        sleeper = patch.object(optimizer_lab.time, "sleep")
        sleeper.start()
        self.addCleanup(sleeper.stop)

    def simulate(self, rows, visible):
        state = {row["agent_session_id"]: dict(row) for row in rows}
        sweep = {"number": 0}
        def listing(*args, **kwargs):
            index = min(sweep["number"], len(visible) - 1)
            sweep["number"] += 1
            return [dict(state[key]) for key in visible[index]]
        def show(agent, identifier, **kwargs):
            self.assertEqual(agent, "owned-agent")
            return dict(state[identifier])
        def stop(agent, identifier, **kwargs):
            self.assertEqual(agent, "owned-agent")
            state[identifier].update(status="idle", stopped_at="2026-09-30T14:00:00Z")
        self.project.agents.list_sessions.side_effect = listing
        self.project.agents.get_session.side_effect = show
        self.project.agents.stop_session.side_effect = stop
        return state

    def reconcile(self, before=()):
        return optimizer_lab.reconcile_sessions(
            self.project, "owned-agent", "2", set(before), "opt_fixture", self.job, self.evidence,
            endpoint=ENDPOINT,
        )

    def test_late_candidates_are_discovered_without_stopping_unrelated_sessions(self):
        rows = [
            session("prior", created=90), session("baseline"),
            session("late", created=210, candidate="cand_opt_fixture_late"),
            session("other-version", version="3"),
            session("other-job", candidate="cand_opt_foreign_late"),
            session("after-tail", created=381),
        ]
        early = ["prior", "baseline", "other-version", "other-job", "after-tail"]
        self.simulate(rows, [early, early, [*early, "late"]])
        result = self.reconcile(before={"prior"})
        self.assertEqual(result["status"], "observed_quiescence")
        self.assertEqual(result["passes"], 6)
        self.assertGreaterEqual(result["quiet_passes"], 2)
        self.assertEqual(result["stopped_session_ids"], ["baseline", "late"])
        self.assertEqual([call.args[1] for call in self.project.agents.stop_session.call_args_list], ["baseline", "late"])
        self.assertEqual(self.project.agents.list_sessions.call_count, 6)
        self.assertEqual(json.loads((self.root / "contoso-optimizer-fixture-cleanup.json").read_text()), result)

    def test_actual_draft_version_shape_and_late_baseline_are_owned_and_stopped(self):
        rows = [
            session("draft-a", version="draft-123456", created=180),
            session("draft-b", version="draft-123456", created=190),
            session("late-baseline", created=218),
            session("foreign-draft", version="draft-987654", created=190),
        ]
        state = self.simulate(rows, [[], [], [row["agent_session_id"] for row in rows]])
        def version(agent, number, **kwargs):
            return {
                "name": agent, "version": number, "definition": {
                    "kind": "hosted", "environment_variables": {
                        "OPTIMIZATION_CANDIDATE_ID": "cand_opt_fixture_0001" if number == "draft-123456" else "cand_opt_foreign_0001",
                        "OPTIMIZATION_RESOLVE_ENDPOINT": ENDPOINT + "/optimization/config",
                    },
                },
            }
        self.project.agents.get_version.side_effect = version
        stop = self.project.agents.stop_session.side_effect
        def reset_created_at(agent, identifier, **kwargs):
            stop(agent, identifier, **kwargs)
            state[identifier]["created_at"] = 999
        self.project.agents.stop_session.side_effect = reset_created_at
        result = self.reconcile()
        self.assertEqual(result["stopped_session_ids"], ["draft-a", "draft-b", "late-baseline"])
        self.assertEqual(self.project.agents.get_version.call_count, 2)
        self.assertEqual(self.project.agents.stop_session.call_count, 3)
        self.assertEqual(result["status"], "observed_quiescence")

    def test_draft_version_resolver_must_belong_to_the_recorded_project(self):
        self.simulate([session("draft", version="draft-123456")], [["draft"]])
        self.project.agents.get_version.return_value = {
            "name": "owned-agent", "version": "draft-123456", "definition": {
                "kind": "hosted", "environment_variables": {
                    "OPTIMIZATION_CANDIDATE_ID": "cand_opt_fixture_0001",
                    "OPTIMIZATION_RESOLVE_ENDPOINT": "https://foreign.services.ai.azure.com/api/projects/foreign/config",
                },
            },
        }
        with self.assertRaisesRegex(RuntimeError, "unverified definition/resolver"):
            self.reconcile()
        self.project.agents.stop_session.assert_not_called()

    def test_new_session_in_final_pass_is_stopped_but_not_claimed_settled(self):
        self.simulate([session("late", candidate="cand_opt_fixture_last", created=210)], [[], [], [], [], [], ["late"]])
        with self.assertRaisesRegex(RuntimeError, "not settled"):
            self.reconcile()
        report = json.loads((self.root / "contoso-optimizer-fixture-cleanup.json").read_text())
        self.assertEqual(report["status"], "unverified")
        self.assertEqual(report["stopped_session_ids"], ["late"])
        self.assertIn("error", report)

    def test_one_denied_stop_does_not_prevent_other_known_session_cleanup(self):
        self.simulate([session("denied"), session("owned")], [["denied", "owned"]])
        original = self.project.agents.stop_session.side_effect
        def stop(agent, identifier, **kwargs):
            if identifier == "denied":
                raise RuntimeError("Scoped stop denied")
            return original(agent, identifier, **kwargs)
        self.project.agents.stop_session.side_effect = stop
        with self.assertRaisesRegex(RuntimeError, "cleanup is incomplete"):
            self.reconcile()
        self.assertEqual([call.args[1] for call in self.project.agents.stop_session.call_args_list], ["denied", "owned"])
        report = json.loads((self.root / "contoso-optimizer-fixture-cleanup.json").read_text())
        self.assertEqual(report["stopped_session_ids"], ["owned"])
        self.assertEqual(report["status"], "unverified")

    def test_deadline_is_separate_from_and_does_not_extend_job_deadline(self):
        with patch.object(optimizer_lab.time, "monotonic", side_effect=[0, 181]), \
                self.assertRaisesRegex(RuntimeError, "budget exhausted"):
            self.reconcile()
        self.project.agents.list_sessions.assert_not_called()
        self.project.agents.stop_session.assert_not_called()
        self.assertEqual(json.loads((self.root / "contoso-optimizer-fixture-cleanup.json").read_text())["status"], "unverified")

    def test_sdk_full_pagination_is_bounded_and_not_silently_truncated(self):
        self.project.agents.list_sessions.return_value = iter(session(f"s-{number}") for number in range(101))
        with self.assertRaisesRegex(RuntimeError, "exceeded 100"):
            optimizer_lab.sessions("owned-agent", self.evidence, project=self.project)
        self.project.agents.stop_session.assert_not_called()

    def test_more_than_ten_owned_sessions_fails_without_extra_stops(self):
        rows = [session(f"s-{number:02}") for number in range(11)]
        self.simulate(rows, [[row["agent_session_id"] for row in rows]])
        with self.assertRaisesRegex(RuntimeError, "bounded cleanup limit"):
            self.reconcile()
        self.assertEqual(self.project.agents.stop_session.call_count, 10)

    def test_session_must_have_real_stopped_readback(self):
        self.simulate([session("never-stops")], [["never-stops"]])
        self.project.agents.stop_session.side_effect = None
        with self.assertRaisesRegex(RuntimeError, "no verified stopped state"):
            self.reconcile()
        self.assertEqual(self.project.agents.get_session.call_count, 7)

    def test_timestamp_shapes_and_terminal_identity_are_checked(self):
        self.assertEqual(optimizer_lab.timestamp("1970-01-01T00:02:30Z", "test"), 150)
        self.assertEqual(optimizer_lab.timestamp(datetime.fromtimestamp(150, timezone.utc), "test"), 150)
        for value in (True, float("nan"), float("inf"), None):
            with self.assertRaises(ValueError):
                optimizer_lab.timestamp(value, "test")
        for number, changes in enumerate(({"id": "opt_foreign"}, {"status": "in_progress"})):
            self.job = {**self.job, "id": "opt_fixture", "status": "cancelled", **changes}
            self.evidence.run_id = f"contoso-optimizer-fixture-{number}"
            with self.assertRaisesRegex(RuntimeError, "terminal owned job"):
                self.reconcile()
        self.project.agents.list_sessions.assert_not_called()

    def test_timeout_keeps_progress_and_does_not_guess_a_service_cause(self):
        operations = Mock()
        operations.get_optimization_job.return_value = {
            **self.job, "status": "in_progress",
            "result": {"candidates": [{"candidate_id": "cand_opt_fixture_baseline", "avg_score": 0.7}]},
        }
        with self.assertRaises(TimeoutError):
            optimizer_lab.monitor(operations, "opt_fixture", self.evidence, max_seconds=1200)
        timeout = next(call.args[1] for call in self.evidence.append.call_args_list if call.args[0] == "optimizer_timeout")
        self.assertFalse(timeout["deadline_extended"])
        self.assertEqual(timeout["candidates"][0]["avg_score"], 0.7)
        self.assertIn("not established", timeout["cause"])
        self.assertEqual(operations.get_optimization_job.call_count, 1)
        self.assertLessEqual(operations.get_optimization_job.call_args.kwargs["read_timeout"], 60)

    def test_ci_serializes_optimizer_and_evaluation_in_each_owned_language_environment(self):
        workflow = (ROOT / ".github/workflows/azure-validation.yml").read_text()
        self.assertIn("group: contoso-approved-azure-${{ inputs.language }}\n", workflow)
        self.assertIn("cancel-in-progress: false", workflow)


if __name__ == "__main__":
    unittest.main()
