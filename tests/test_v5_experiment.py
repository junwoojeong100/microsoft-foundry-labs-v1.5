import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
sys.path.insert(0, str(ROOT / "scripts"))
import business_checks
import evaluation_data
import evaluation_lab
import hosted_client
import optimizer_lab
import prepare_eval_v5
import share_evidence
from evidence import digest


class V5PreparationTests(unittest.TestCase):
    def test_inherits_exact_dev_and_controls_without_opening_any_holdout(self):
        original = Path.read_text

        def guard(path, *args, **kwargs):
            if "holdout" in path.name:
                raise AssertionError("Development must not open a holdout or seal.")
            return original(path, *args, **kwargs)

        with tempfile.TemporaryDirectory() as temporary, patch.object(Path, "read_text", guard):
            directory = Path(temporary)
            with patch.object(prepare_eval_v5, "DIRECTORY", directory), contextlib.redirect_stdout(io.StringIO()):
                prepare_eval_v5.prepare()
                prepare_eval_v5.prepare()
            before = [json.loads(line) for line in (ROOT / "data/en/evaluation/v4/dev.jsonl").read_text().splitlines()]
            after = [json.loads(line) for line in (directory / "dev.jsonl").read_text().splitlines()]
            self.assertEqual(len(after), 40)
            for old, new in zip(before, after, strict=True):
                self.assertEqual({k: v for k, v in old.items() if k not in {"id", "origin"}},
                                 {k: v for k, v in new.items() if k not in {"id", "origin"}})
                self.assertEqual(new["origin"]["id"], old["id"])
                self.assertEqual(new["origin"]["previous_origin"], old["origin"])
            self.assertEqual((directory / "calibration.jsonl").read_bytes(),
                             (ROOT / "data/en/evaluation/v4/calibration.jsonl").read_bytes())
            old = json.loads((ROOT / "data/en/evaluation/v4/rubric.json").read_text())
            new = json.loads((directory / "rubric.json").read_text())
            for key in set(old) - {"suite", "description", "legacy_evidence"}:
                self.assertEqual(new[key], old[key])
            (directory / "dev.jsonl").write_text("preserved failure\n")
            with patch.object(prepare_eval_v5, "DIRECTORY", directory), self.assertRaisesRegex(ValueError, "not be overwritten"):
                prepare_eval_v5.prepare()

    def test_fingerprint_covers_v5_collection_judging_optimization_and_export(self):
        paths = {path.relative_to(ROOT).as_posix() for path in prepare_eval_v5.freeze_paths()}
        self.assertTrue({
            "samples/request_contract.py", "samples/hosted_client.py", "samples/evaluation_lab.py",
            "samples/optimizer_lab.py", "scripts/build_hosted.py", "scripts/ci_live.py",
            "scripts/share_evidence.py", "data/en/evaluation/v5/dev.jsonl", "data/en/prompts/agent-v7.txt",
        } <= paths)
        self.assertFalse(any("holdout" in path for path in paths))
        self.assertFalse(any("evaluation/v4/" in path for path in paths))

    def test_new_authorization_version_cannot_be_downgraded_to_historical_v1(self):
        row = {
            "query": "Explain policy only.", "tool_authorization_contract": "explicit-request-v1",
            "request_permissions": {}, "required_policy_citations": [],
        }
        result = business_checks.check_business_evidence(row, {}, expected_authorization_contract="explicit-request-v2")
        self.assertIn("tool_authorization_contract", result["failures"])
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "responses.jsonl"
            path.write_text(json.dumps({
                **row, "id": "fixture", "status": "completed", "response": "Fixture only", "response_id": "fixture",
            }) + "\n")
            with patch.object(evaluation_lab, "load_cases", return_value=[{"id": "fixture"}]), \
                    self.assertRaisesRegex(ValueError, "v1 is historical replay only"):
                evaluation_lab.prepare_rows(path, "dev", "automated-v5")

    def test_frozen_v5_drift_fails_before_cloud(self):
        with patch.object(hosted_client, "LANGUAGE", "en"), \
                patch.object(hosted_client, "SUITES", (*hosted_client.SUITES, "automated-v5")), \
                patch.object(sys, "argv", ["hosted_client.py", "evaluate", "--suite", "automated-v5",
                                         "--split", "dev", "--version", "4", "--live"]), \
                patch.object(hosted_client, "verify_development_freeze", side_effect=ValueError("Frozen input changed")), \
                patch.object(hosted_client, "read_config") as config, self.assertRaisesRegex(ValueError, "Frozen input changed"):
            hosted_client.main()
        config.assert_not_called()

    def test_holdout_gate_precedes_case_loading_configuration_and_cloud(self):
        with patch.object(hosted_client, "SUITES", (*hosted_client.SUITES, "automated-v5")), \
                patch.object(sys, "argv", ["hosted_client.py", "evaluate", "--suite", "automated-v5",
                                         "--split", "holdout", "--version", "4", "--live"]), \
                patch.object(hosted_client, "verify_development_freeze"), \
                patch.object(evaluation_lab, "verify_gate", side_effect=ValueError("dev incomplete")) as gate, \
                patch.object(hosted_client, "load_cases") as load, patch.object(hosted_client, "read_config") as config, \
                self.assertRaisesRegex(ValueError, "dev incomplete"):
            hosted_client.main()
        gate.assert_called_once_with("automated-v5", "dev")
        load.assert_not_called()
        config.assert_not_called()

    def test_optimizer_dev_loader_cannot_open_any_holdout(self):
        script = """
import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, 'samples')
from optimizer_lab import dev_cases, payload
from evaluation_data import DEFAULT_SUITE
original = Path.read_text
def guard(path, *args, **kwargs):
    if 'holdout' in path.name:
        raise AssertionError('Optimizer must not open a holdout or seal')
    return original(path, *args, **kwargs)
with patch.object(Path, 'read_text', guard):
    assert DEFAULT_SUITE == 'automated-v5'
    cases = dev_cases(DEFAULT_SUITE)
    request = payload('agent', '4', 'judge', 'reflection', cases=cases,
                      prompt_path=Path('data/en/prompts/agent-v7.txt'))
    assert len(request['inputs']['train_dataset']['items']) == 40
    assert 'validation_dataset' not in request['inputs']
    assert request['inputs']['options']['max_candidates'] == 2
    assert request['inputs']['options']['max_stalls'] == 1
"""
        result = subprocess.run([sys.executable, "-c", script], cwd=ROOT, text=True, capture_output=True,
                                env={**os.environ, "FOUNDRY_LAB_LANGUAGE": "en"}, timeout=30, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_v5_cannot_extend_optimizer_budget(self):
        args = SimpleNamespace(max_seconds=1201, suite="automated-v5", resume=None)
        with patch.object(optimizer_lab, "verify_development_freeze"), patch.object(optimizer_lab, "read_config") as config, \
                self.assertRaisesRegex(ValueError, "1200"):
            optimizer_lab.run(args, Mock())
        config.assert_not_called()


class V5NativeGateTests(unittest.TestCase):
    def native(self):
        return {
            "status": "completed", "error": None,
            "result_counts": {"total": 40, "passed": 38, "failed": 2, "errored": 0},
            "items": [{} for _ in range(40)],
        }

    def test_missing_errored_skipped_and_inconsistent_native_rows_are_not_success(self):
        evaluation_lab.check_native_completeness(self.native(), 40)
        for changes in (
            {"errored": 1}, {"skipped": 1}, {"total": 39}, {"passed": 40}, {"passed": True},
        ):
            native = self.native()
            native["result_counts"].update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                evaluation_lab.check_native_completeness(native, 40)
        native = self.native()
        native["items"].pop()
        with self.assertRaises(ValueError):
            evaluation_lab.check_native_completeness(native, 40)

    def test_secondary_metric_errors_are_not_hidden_by_business_score(self):
        for status in ("error", "skipped"):
            items = [{"datasource_item": {"id": "fixture"}, "results": [
                {"name": "contoso_business", "score": 5, "passed": True},
                {"name": "relevance", "status": status},
            ]}]
            with self.assertRaisesRegex(ValueError, "execution error or skipped"):
                evaluation_lab.audit_items(items, {"fixture": True}, suite="automated-v5")

    def test_local_and_mixed_evidence_cannot_authorize_holdout(self):
        row = {
            "execution_location": "azure", "environment_sha256": "fixture", "hosted_version": "4",
            "contract": {"sha256": "fixture"}, "effective_prompt_sha256": "fixture",
            "model": "fixture", "model_deployment": "fixture",
        }
        self.assertEqual(evaluation_lab.target_configuration([row])["hosted_version"], "4")
        for rows in ([], [{**row, "execution_location": "local"}], [row, {**row, "hosted_version": "5"}]):
            with self.assertRaises(ValueError):
                evaluation_lab.target_configuration(rows)

    def test_collection_deadline_prevents_the_next_request(self):
        with patch.object(hosted_client.time, "monotonic", return_value=1200):
            self.assertEqual(hosted_client.remaining_seconds(1205, 310), 5)
            with self.assertRaises(TimeoutError):
                hosted_client.remaining_seconds(1200, 310)

    def test_native_timeout_is_cancelled_and_observed_without_a_second_run(self):
        client = Mock()
        active = SimpleNamespace(id="fixture-run", status="in_progress")
        client.evals.runs.retrieve.return_value = SimpleNamespace(id="fixture-run", status="cancelled")
        with patch.dict(sys.modules, {"openai": SimpleNamespace(OpenAIError=RuntimeError)}), \
                patch.object(evaluation_lab.time, "monotonic", side_effect=[0, 600, 601, 602]), \
                patch.object(evaluation_lab.time, "sleep"):
            result, timed_out, error = evaluation_lab.wait_for_native(client, "fixture-eval", active, Mock())
        self.assertTrue(timed_out)
        self.assertIsNone(error)
        self.assertEqual(result.status, "cancelled")
        client.evals.runs.create.assert_not_called()
        client.evals.runs.cancel.assert_called_once()

    def test_polling_failure_is_not_misreported_as_a_timeout_or_success(self):
        client = Mock()
        active = SimpleNamespace(id="fixture-run", status="in_progress")
        client.evals.runs.retrieve.side_effect = [OSError("fixture transport failure"),
                                                 SimpleNamespace(id="fixture-run", status="cancelled")]
        with patch.dict(sys.modules, {"openai": SimpleNamespace(OpenAIError=RuntimeError)}), \
                patch.object(evaluation_lab.time, "monotonic", side_effect=[0, 1, 2, 3, 4]), \
                patch.object(evaluation_lab.time, "sleep"):
            result, timed_out, error = evaluation_lab.wait_for_native(client, "fixture-eval", active, Mock())
        self.assertFalse(timed_out)
        self.assertIsInstance(error, OSError)
        self.assertEqual(result.status, "cancelled")
        client.evals.runs.cancel.assert_called_once()

    def test_altered_native_gate_originals_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            results = root / "results"
            results.mkdir()
            native = self.native()
            path = results / "native.json"
            path.write_text(json.dumps(native))
            receipt = {"suite_sha256": "suite", "settings_hash": "settings", "judge": "fixture-judge", "native_path": "results/native.json",
                       "native_sha256": digest(native)}
            (results / "automated-v5-calibration-gate.json").write_text(json.dumps(receipt))
            native["result_counts"]["errored"] = 1
            path.write_text(json.dumps(native))
            with patch.object(evaluation_lab, "ROOT", root), patch.object(evaluation_lab, "RESULTS", results), \
                    patch.object(evaluation_lab, "suite_hash", return_value="suite"), \
                    patch.object(evaluation_lab, "settings_hash", return_value="settings"), \
                    patch.object(evaluation_lab, "config_values", return_value={"FOUNDRY_JUDGE_DEPLOYMENT_NAME": "fixture-judge"}), \
                    self.assertRaisesRegex(ValueError, "originals changed"):
                evaluation_lab.verify_gate("automated-v5", "calibration")


if __name__ == "__main__":
    unittest.main()
