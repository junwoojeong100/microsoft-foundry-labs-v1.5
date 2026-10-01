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

    def test_both_languages_use_the_same_three_checklist_topics(self):
        before = json.loads((ROOT / "data/evaluation/instruction-comparison.json").read_text())["cases"]
        after = json.loads((ROOT / "data/en/evaluation/instruction-comparison.json").read_text())["cases"]
        self.assertEqual(len(before), 3)
        for ko, en in zip(before, after, strict=True):
            self.assertEqual(ko["id"], en["id"])
            self.assertEqual([(x["id"], x["sources"]) for x in ko["checks"]],
                             [(x["id"], x["sources"]) for x in en["checks"]])

    def test_plan_has_no_cloud_calls_or_predetermined_improvement(self):
        output = io.StringIO()
        with patch.object(sys, "argv", ["instruction_lab.py"]), patch.object(instruction_lab, "project_client") as client, \
                patch("sys.stdout", output):
            instruction_lab.main()
        plan = json.loads(output.getvalue())
        self.assertEqual(plan["same_cases_per_version"], 3)
        self.assertEqual(plan["model_calls"], 0)
        self.assertEqual(plan["model_calls_if_approved"], 6)
        self.assertFalse(plan["score_improvement_guaranteed"])
        client.assert_not_called()

    def test_scoring_uses_answer_and_sources_not_the_version_name(self):
        sources = {"CONTOSO-PROC-2026-09-s2": {
            "id": "CONTOSO-PROC-2026-09-s2", "filename": "procurement-policy.md", "section": "2", "content": "Fixture.",
        }}
        case = {"checks": [{"id": "cap", "pattern": "1500000", "sources": list(sources)}]}
        good = json.dumps({"answer": "1500000", "citation_ids": list(sources)})
        bad = json.dumps({"answer": "Cannot answer the public part.", "citation_ids": list(sources)})
        self.assertEqual(instruction_lab.score(good, case, sources)["matched"], 1)
        self.assertEqual(instruction_lab.score(bad, case, sources)["matched"], 0)
        with self.assertRaises(RuntimeError):
            instruction_lab.score('{"answer":"1500000","citation_ids":["invented"]}', case, sources)

    def rows(self, first, second):
        return [{"id": str(index), "instructions": version, "status": "completed", "model": "fixture",
                 "checklist": {"matched": score}}
                for index in range(3) for version, score in (("v1", first), ("v2", second))]

    def test_ties_regressions_and_partial_runs_cannot_be_called_improvements(self):
        cases = [{"id": str(i), "checks": [{}, {}, {}]} for i in range(3)]
        for first, second, expected in ((1, 3, "improved"), (3, 3, "unchanged"), (3, 1, "regressed")):
            report = instruction_lab.summarize(self.rows(first, second), cases)
            self.assertEqual(report["outcome"], expected)
            self.assertFalse(report["quality_release"])
        with self.assertRaisesRegex(ValueError, "partial"):
            instruction_lab.summarize(self.rows(1, 3)[:-1], cases)
        rows = self.rows(1, 3)
        rows[1]["model"] = "different-fixture-model"
        with self.assertRaisesRegex(ValueError, "model versions changed"):
            instruction_lab.summarize(rows, cases)

    def test_existing_comparison_stops_before_cloud(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "comparison.json"
            path.write_text('{"preserved":true}')
            with patch.object(sys, "argv", ["instruction_lab.py", "--live", "--output", str(path)]), \
                    patch.object(instruction_lab, "project_client") as client, self.assertRaisesRegex(ValueError, "resample"):
                instruction_lab.main()
            self.assertEqual(path.read_text(), '{"preserved":true}')
            client.assert_not_called()

    def test_one_pair_per_case_uses_identical_inputs_and_no_answer_key(self):
        raw = '{"answer":"fixture","citation_ids":["CONTOSO-PROC-2026-09-s2"]}'
        client = Obj(responses=Obj(create=Mock(return_value=Obj(
            status="completed", id="fixture-response", model="fixture-model", output_text=raw, output=[], usage=None,
        ))))
        project = MagicMock()
        project.get_openai_client.return_value.__enter__.return_value = client

        @contextmanager
        def context():
            yield project, None, "fixture-not-azure", "fixture-model"

        with tempfile.TemporaryDirectory() as directory, patch.object(instruction_lab, "RESULTS", Path(directory)), \
                patch.object(instruction_lab, "project_client", context), \
                patch.dict(sys.modules, {"openai": Obj(OpenAIError=RuntimeError)}):
            result = instruction_lab.compare(Path(directory) / "comparison.json", reasoning_effort="low")
        self.assertEqual(client.responses.create.call_count, 6)
        calls = client.responses.create.call_args_list
        for first, second in zip(calls[::2], calls[1::2], strict=True):
            self.assertEqual(first.kwargs["input"], second.kwargs["input"])
            self.assertEqual(first.kwargs["model"], second.kwargs["model"])
            self.assertEqual(first.kwargs["text"], second.kwargs["text"])
            self.assertEqual(first.kwargs["reasoning"], {"effort": "low"})
            self.assertEqual(first.kwargs["reasoning"], second.kwargs["reasoning"])
            self.assertNotEqual(first.kwargs["instructions"], second.kwargs["instructions"])
            self.assertNotIn("checks", json.loads(first.kwargs["input"]))
        self.assertEqual(result["comparison"]["outcome"], "unchanged")
        self.assertFalse(result["quality_release"])

    def test_failed_request_keeps_partial_originals_without_retry_or_winning_score(self):
        raw = '{"answer":"fixture","citation_ids":["CONTOSO-PROC-2026-09-s2"]}'
        response = Obj(status="completed", id="fixture-response", model="fixture-model",
                       output_text=raw, output=[], usage=None)
        client = Obj(responses=Obj(create=Mock(side_effect=[response, OSError("fixture transport failure")])))
        project = MagicMock()
        project.get_openai_client.return_value.__enter__.return_value = client

        @contextmanager
        def context():
            yield project, None, "fixture-not-azure", "fixture-model"

        with tempfile.TemporaryDirectory() as directory, patch.object(instruction_lab, "RESULTS", Path(directory)), \
                patch.object(instruction_lab, "project_client", context), \
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
