import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
sys.path.insert(0, str(ROOT / "scripts"))
import evaluation_data
import hosted_client
import prepare_eval_v4
import share_evidence


class QualityRevisionTests(unittest.TestCase):
    def test_shared_evidence_preserves_actual_authorization_fields(self):
        fields = {
            "tool_authorization_contract": "explicit-request-v1",
            "request_permissions": {"stock_skus": [], "draft_arguments": []},
            "required_policy_citations": ["CONTOSO-PROC-2026-09-s4"],
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "fixture.jsonl"
            source.write_text(json.dumps({"id": "fixture-only", **fields, "headers": {"private": "excluded"}}) + "\n")
            with patch.object(share_evidence, "ROOT", root), \
                    patch.object(share_evidence, "validation_for", return_value=root / "validation"), \
                    patch.object(share_evidence, "prepare_rows"), \
                    patch.object(sys, "argv", [
                        "share_evidence.py", "--input", str(source), "--split", "dev", "--suite", "automated-v3",
                    ]):
                share_evidence.main()
            exported = json.loads((root / "validation/automated-v3/dev-responses.jsonl").read_text())
            for key, value in fields.items():
                self.assertEqual(exported[key], value)
            self.assertNotIn("headers", exported)

    def test_all_consumed_cases_and_judge_controls_are_preserved_without_oracle_changes(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".build", prefix="quality-v4-") as temporary:
            directory = Path(temporary)
            with patch.object(prepare_eval_v4, "DIRECTORY", directory):
                prepare_eval_v4.prepare()
                prepare_eval_v4.prepare()
            original = [
                json.loads(line) for split in ("dev", "holdout")
                for line in (ROOT / f"data/en/evaluation/v3/{split}.jsonl").read_text().splitlines()
            ]
            actual = [json.loads(line) for line in (directory / "dev.jsonl").read_text().splitlines()]
            self.assertEqual(len(actual), 40)
            for before, after in zip(original, actual, strict=True):
                self.assertEqual(
                    {key: value for key, value in before.items() if key not in {"id", "split", "origin"}},
                    {key: value for key, value in after.items() if key not in {"id", "split", "origin"}},
                )
                self.assertEqual(after["origin"]["id"], before["id"])
                self.assertEqual(after["origin"]["previous_origin"], before.get("origin"))
                self.assertEqual(after["split"], "dev")
            self.assertEqual((directory / "calibration.jsonl").read_bytes(),
                             (ROOT / "data/en/evaluation/v3/calibration.jsonl").read_bytes())
            old_policy = json.loads((ROOT / "data/en/evaluation/v3/rubric.json").read_text())
            new_policy = json.loads((directory / "rubric.json").read_text())
            for key in ("minimum_pass_rate", "native_pass_threshold", "zero_tolerance_categories",
                        "required_holdout_cases", "human_review", "pass_definition"):
                self.assertEqual(old_policy[key], new_policy[key])
            (directory / "dev.jsonl").write_text("do not overwrite\n")
            with patch.object(prepare_eval_v4, "DIRECTORY", directory), self.assertRaisesRegex(ValueError, "not be overwritten"):
                prepare_eval_v4.prepare()

    def test_freeze_drift_and_path_escape_fail_closed(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".build", prefix="freeze-v4-") as temporary:
            root = Path(temporary)
            directory = root / "data/en/evaluation/v4"
            directory.mkdir(parents=True)
            source = root / "runtime.py"
            source.write_text("frozen runtime\n")
            freeze = {
                "schema": "contoso-development-freeze-v2", "suite": "automated-v4", "language": "en",
                "files": {"runtime.py": hashlib.sha256(source.read_bytes()).hexdigest()},
            }
            path = directory / "development-freeze.json"
            path.write_text(json.dumps(freeze))
            with patch.object(evaluation_data, "LANGUAGE", "en"):
                evaluation_data.verify_development_freeze("automated-v4", root=root)
                source.write_text("changed runtime\n")
                with self.assertRaisesRegex(ValueError, "Frozen development input changed"):
                    evaluation_data.verify_development_freeze("automated-v4", root=root)
                freeze["files"] = {"../outside": "not-used"}
                path.write_text(json.dumps(freeze))
                with self.assertRaisesRegex(ValueError, "Frozen development input changed"):
                    evaluation_data.verify_development_freeze("automated-v4", root=root)

    def test_consumed_english_holdout_collection_stops_before_configuration_or_cloud(self):
        with patch.object(hosted_client, "LANGUAGE", "en"), patch.object(sys, "argv", [
            "hosted_client.py", "evaluate", "--suite", "automated-v3", "--split", "holdout",
            "--version", "2", "--live",
        ]), patch.object(hosted_client, "read_config") as config, \
                patch.object(hosted_client, "load_cases") as load, \
                self.assertRaisesRegex(ValueError, "consumed"):
            hosted_client.main()
        config.assert_not_called()
        load.assert_not_called()

    def test_english_current_dev_loader_never_opens_new_holdout_or_seal(self):
        script = r"""
import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, 'samples')
from evaluation_data import DEFAULT_SUITE, load_cases, policy
from lab_profile import active_prompt
original = Path.read_text
def guard(path, *args, **kwargs):
    if 'holdout' in path.name:
        raise AssertionError('Development must not open new holdout data or its seal')
    return original(path, *args, **kwargs)
with patch.object(Path, 'read_text', guard):
    assert DEFAULT_SUITE == 'automated-v5'
    assert len(load_cases(split='dev')) == 40
    assert policy()['minimum_pass_rate'] == 0.9
    assert policy()['native_pass_threshold'] == 4
    assert active_prompt().name == 'agent-v2.txt'
"""
        result = subprocess.run([sys.executable, "-c", script], cwd=ROOT, text=True, capture_output=True,
                                env={**os.environ, "FOUNDRY_LAB_LANGUAGE": "en"}, timeout=30, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_korean_defaults_are_preserved(self):
        self.assertEqual(evaluation_data.DEFAULT_SUITE, "automated-v3")
        self.assertNotIn("automated-v4", evaluation_data.SUITES)
        self.assertNotIn("automated-v5", evaluation_data.SUITES)



    def test_changed_candidate_cannot_collect_more_v4_targets(self):
        with patch.object(hosted_client, "LANGUAGE", "en"), \
                patch.object(hosted_client, "SUITES", (*hosted_client.SUITES, "automated-v4")), patch.object(sys, "argv", [
            "hosted_client.py", "evaluate", "--suite", "automated-v4", "--split", "dev",
            "--version", "3", "--live",
        ]), patch.object(hosted_client, "verify_development_freeze", side_effect=ValueError("Frozen input changed")), \
                patch.object(hosted_client, "read_config") as config, \
                self.assertRaisesRegex(ValueError, "Frozen input changed"):
            hosted_client.main()
        config.assert_not_called()


if __name__ == "__main__":
    unittest.main()
