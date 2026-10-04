from contextlib import contextmanager
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace as Obj
import unittest
from unittest.mock import MagicMock, Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
import instruction_lab
from lab_profile import active_prompt


class InstructionLearningTests(unittest.TestCase):
    def test_only_baseline_and_current_prompts_are_exposed(self):
        for directory in (ROOT / "data/prompts", ROOT / "data/en/prompts"):
            self.assertEqual({path.name for path in directory.glob("agent-v*.txt")}, {"agent-v1.txt", "agent-v2.txt"})
        self.assertEqual(active_prompt().name, "agent-v2.txt")

    def test_both_languages_use_the_same_twelve_precommitted_cases(self):
        before = json.loads((ROOT / "data/evaluation/instruction-comparison.json").read_text())["cases"]
        after = json.loads((ROOT / "data/en/evaluation/instruction-comparison.json").read_text())["cases"]
        self.assertEqual(len(before), 12)
        self.assertEqual([row["id"] for row in before], [row["id"] for row in after])
        for ko, en in zip(before, after, strict=True):
            self.assertEqual([(x["id"], x["sources"], x["critical"]) for x in ko["checks"]],
                             [(x["id"], x["sources"], x["critical"]) for x in en["checks"]])
            self.assertEqual(len({check["id"] for check in ko["checks"]}), len(ko["checks"]))

    def test_plan_has_no_cloud_calls_or_predetermined_improvement(self):
        output = io.StringIO()
        with patch.object(sys, "argv", ["instruction_lab.py"]), patch.object(instruction_lab, "project_client") as client, \
                patch("sys.stdout", output):
            instruction_lab.main()
        plan = json.loads(output.getvalue())
        self.assertEqual(plan["same_cases_per_version"], 12)
        self.assertEqual(plan["model_calls"], 0)
        self.assertEqual(plan["model_calls_if_approved"], 24)
        self.assertEqual(plan["bilingual_target_calls_max"], 48)
        self.assertEqual(plan["bilingual_collection_max_seconds"], 1200)
        self.assertFalse(plan["score_improvement_guaranteed"])
        client.assert_not_called()

    def test_scoring_uses_answer_and_sources_not_the_version_name(self):
        sources = {"CONTOSO-PROC-2026-09-s2": {
            "id": "CONTOSO-PROC-2026-09-s2", "filename": "procurement-policy.md", "section": "2", "content": "Fixture.",
        }}
        case = {"checks": [{"id": "cap", "pattern": "1500000", "sources": list(sources),
                            "requirement": "Fixture.", "critical": True}]}
        good = json.dumps({"answer": "1500000", "citation_ids": list(sources)})
        bad = json.dumps({"answer": "Cannot answer the public part.", "citation_ids": list(sources)})
        self.assertEqual(instruction_lab.score(good, case, sources)["matched"], 1)
        self.assertEqual(instruction_lab.score(bad, case, sources)["matched"], 0)
        with self.assertRaises(RuntimeError):
            instruction_lab.score('{"answer":"1500000","citation_ids":["invented"]}', case, sources)

    def fixture_cases(self):
        return [{"id": f"case-{index}", "checks": [
            {"id": f"check-{check}", "critical": check == 0} for check in range(3)
        ]} for index in range(12)]

    def rows(self, first, second):
        result = []
        for index in range(12):
            pair_hash = f"same-input-{index}"
            for version, matched in (("v1", first), ("v2", second)):
                checks = {f"check-{check}": {"matched": check < matched, "critical": check == 0}
                          for check in range(3)}
                result.append({
                    "id": f"case-{index}", "instructions": version, "status": "completed",
                    "model": "fixture-model", "query": f"question-{index}", "input_sha256": pair_hash,
                    "response_id": f"response-{version}-{index}", "usage": None,
                    "latency_seconds": 1.0, "checklist": {
                        "matched": matched, "total": 3, "checks": checks,
                        "critical_failures": [] if matched else [f"check-0"],
                    },
                })
        return result

    def test_ties_regressions_and_partial_runs_cannot_be_called_improvements(self):
        cases = self.fixture_cases()
        for first, second, expected in ((1, 3, "improved"), (3, 3, "unchanged"), (3, 1, "regressed")):
            report = instruction_lab.summarize(self.rows(first, second), cases)
            self.assertEqual(report["local_checklist"]["outcome"], expected)
            self.assertFalse(report["quality_release"])
        with self.assertRaisesRegex(ValueError, "complete comparison"):
            instruction_lab.summarize(self.rows(1, 3)[:-1], cases)
        rows = self.rows(1, 3)
        rows[1]["model"] = "different-fixture-model"
        with self.assertRaisesRegex(ValueError, "mixed target deployment"):
            instruction_lab.summarize(rows, cases)

    def test_existing_comparison_stops_before_cloud(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "comparison.json"
            path.write_text('{"preserved":true}')
            with patch.object(sys, "argv", ["instruction_lab.py", "--live", "--output", str(path)]), \
                    patch.object(instruction_lab, "project_client") as client, self.assertRaisesRegex(ValueError, "do not resample"):
                instruction_lab.main()
            self.assertEqual(path.read_text(), '{"preserved":true}')
            client.assert_not_called()

    def test_fresh_owned_environment_does_not_depend_on_historical_validation(self):
        from test_model_capacity import scope
        receipt = scope()
        receipt["model_deployments"]["chat"] = "contoso-chat"
        endpoint = receipt["project_endpoint"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "results").mkdir()
            (root / "results/azure-environment.json").write_text(json.dumps(receipt))
            observed = {"chat": {"model": "gpt-6-sol", "version": "2026-09-22", "ready": True}}
            with patch.object(instruction_lab, "ROOT", root), \
                    patch.object(instruction_lab, "RESULTS", root / "results"), \
                    patch.object(instruction_lab, "inspect_deployments", return_value=(observed, {})) as inspect:
                profile = instruction_lab.verify_profile(endpoint, "contoso-chat")
                inspect.assert_called_once()
                with self.assertRaisesRegex(ValueError, "differs"):
                    instruction_lab.verify_profile(endpoint, "not-owned")
                self.assertEqual(inspect.call_count, 1)
                observed["chat"]["ready"] = False
                with self.assertRaisesRegex(ValueError, "TPM/RPM"):
                    instruction_lab.verify_profile(endpoint, "contoso-chat")
            self.assertEqual(profile["model"], "gpt-6-sol")
            self.assertEqual(profile["model_version"], "2026-09-22")
            self.assertEqual(profile["model_deployment"], "contoso-chat")
            self.assertEqual(profile["receipt_sources"], ["results/azure-environment.json"])

    def mock_target(self, project):
        project.deployments.get.return_value.as_dict.return_value = {
            "name": "fixture-model", "modelName": "gpt-6-sol", "modelVersion": "2026-09-22",
        }

    def test_one_pair_per_case_uses_identical_inputs_and_no_answer_key(self):
        source = next(row["id"] for row in instruction_lab.policy_chunks())
        raw = json.dumps({"answer": "fixture", "citation_ids": [source]})
        responses = [Obj(status="completed", id=f"fixture-response-{index}", model="fixture-model",
                         output_text=raw, output=[], usage=None) for index in range(24)]
        client = Obj(responses=Obj(create=Mock(side_effect=responses)))
        project = MagicMock()
        self.mock_target(project)
        project.get_openai_client.return_value.__enter__.return_value = client

        @contextmanager
        def context():
            yield project, None, "fixture-not-azure", "fixture-model"

        with tempfile.TemporaryDirectory() as directory, patch.object(instruction_lab, "RESULTS", Path(directory)), \
                patch.object(instruction_lab, "project_client", context), \
                patch.object(instruction_lab, "verify_profile", return_value={"fixture": True}), \
                patch.dict(sys.modules, {"openai": Obj(OpenAIError=RuntimeError)}):
            result = instruction_lab.compare(Path(directory) / "comparison.json", reasoning_effort="low")
        self.assertEqual(client.responses.create.call_count, 24)
        paired = {}
        for call in client.responses.create.call_args_list:
            arguments = call.kwargs
            self.assertEqual(arguments["max_output_tokens"], 2048)
            self.assertEqual(arguments["tools"], [])
            paired.setdefault(instruction_lab.digest(arguments["input"]), []).append(arguments)
        self.assertEqual(len(paired), 12)
        for pair in paired.values():
            self.assertEqual(len(pair), 2)
            self.assertEqual(pair[0]["input"], pair[1]["input"])
            self.assertEqual(pair[0]["model"], pair[1]["model"])
            self.assertEqual(pair[0]["text"], pair[1]["text"])
            self.assertEqual(pair[0]["reasoning"], {"effort": "low"})
            self.assertEqual(pair[0]["reasoning"], pair[1]["reasoning"])
            self.assertNotEqual(pair[0]["instructions"], pair[1]["instructions"])
            self.assertNotIn("checks", json.loads(pair[0]["input"]))
            self.assertNotIn("requirement", json.loads(pair[0]["input"]))
        self.assertEqual(result["comparison"]["local_checklist"]["outcome"], "unchanged")
        self.assertEqual(result["comparison"]["usage_latency"]["by_instruction"]["v1"]["responses"], 12)
        self.assertFalse(result["quality_release"])

    def test_failed_request_keeps_partial_originals_without_retry_or_winning_score(self):
        source = next(row["id"] for row in instruction_lab.policy_chunks())
        raw = json.dumps({"answer": "fixture", "citation_ids": [source]})
        response = Obj(status="completed", id="fixture-response", model="fixture-model",
                       output_text=raw, output=[], usage=None)
        client = Obj(responses=Obj(create=Mock(side_effect=[response, OSError("fixture transport failure")])))
        project = MagicMock()
        self.mock_target(project)
        project.get_openai_client.return_value.__enter__.return_value = client

        @contextmanager
        def context():
            yield project, None, "fixture-not-azure", "fixture-model"

        with tempfile.TemporaryDirectory() as directory, patch.object(instruction_lab, "RESULTS", Path(directory)), \
                patch.object(instruction_lab, "project_client", context), \
                patch.object(instruction_lab, "verify_profile", return_value={"fixture": True}), \
                patch.dict(sys.modules, {"openai": Obj(OpenAIError=RuntimeError)}):
            path = Path(directory) / "comparison.json"
            with self.assertRaisesRegex(OSError, "fixture transport"):
                instruction_lab.compare(path)
            recorded = json.loads(path.read_text())
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(client.responses.create.call_count, 2)
        self.assertEqual(recorded["status"], "failed")
        self.assertEqual(len(recorded["rows"]), 1)
        self.assertNotIn("comparison", recorded)
        self.assertEqual(recorded["rows"][0]["raw_answer"], raw)
        self.assertFalse(recorded["quality_release"])


if __name__ == "__main__":
    unittest.main()
