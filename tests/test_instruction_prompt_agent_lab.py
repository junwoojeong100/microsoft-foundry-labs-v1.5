import io
import json
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace as Obj
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
import instruction_prompt_agent_lab


class InstructionPromptAgentTests(unittest.TestCase):
    def test_plan_is_read_only_and_bounded(self):
        output = io.StringIO()
        with patch.object(sys, "argv", ["instruction_prompt_agent_lab.py"]), \
                patch("sys.stdout", output), patch.object(instruction_prompt_agent_lab, "project_client") as project:
            instruction_prompt_agent_lab.main()
        plan = json.loads(output.getvalue())
        self.assertTrue(plan["plan_only"])
        self.assertEqual(plan["model_calls"], 0)
        self.assertEqual(plan["model_calls_if_approved"], 24)
        self.assertEqual(plan["bilingual_collection_max_seconds"], 1200)
        self.assertEqual(plan["prompt_agent_versions"], ["v1", "v2"])
        self.assertEqual(plan["optimizer_jobs"], 0)
        self.assertEqual(plan["holdout_cases"], 0)
        project.assert_not_called()

    def test_prompt_definition_pins_model_instructions_schema_and_no_tools(self):
        schema = {"format": {"type": "json_schema", "name": "test", "strict": True,
                             "schema": {"type": "object"}}}
        value = instruction_prompt_agent_lab._definition("v1 only", schema).as_dict()
        self.assertEqual(value["kind"], "prompt")
        self.assertEqual(value["model"], "contoso-gpt-6-sol")
        self.assertEqual(value["instructions"], "v1 only")
        self.assertEqual(value["tools"], [])
        self.assertEqual(value["tool_choice"], "none")
        self.assertEqual(value["text"], schema)
        self.assertEqual(value["reasoning"], {"effort": "low"})

    def test_creates_exactly_two_versioned_prompts_on_one_new_agent(self):
        project = MagicMock()
        project.agents.list.return_value = []
        project.agents.create_version.side_effect = [
            Obj(version="1", status="active"),
            Obj(version="2", status="active"),
        ]
        state = {}

        def persist():
            state["versions"] = dict(report["prompt_agent_versions"]["versions"])

        report = {}
        versions = instruction_prompt_agent_lab._create_versions(
            project,
            "contoso-instruction-eval-ko-20261001",
            {"v1": "simple", "v2": "procedural"},
            {"format": {"type": "json_schema"}},
            report,
            persist,
        )
        self.assertEqual(versions, {"v1": "1", "v2": "2"})
        self.assertEqual(project.agents.create_version.call_count, 2)
        self.assertEqual(
            [call.kwargs["metadata"]["instruction_version"] for call in project.agents.create_version.call_args_list],
            ["v1", "v2"],
        )
        self.assertEqual({call.kwargs["agent_name"] for call in project.agents.create_version.call_args_list},
                         {"contoso-instruction-eval-ko-20261001"})
        self.assertEqual(state["versions"], {"v1": "1", "v2": "2"})

    def test_reuses_only_exact_active_versions_of_the_existing_agent(self):
        project = MagicMock()
        project.agents.list.return_value = [Obj(name="contoso-instruction-eval-en-20261001")]
        schema = {"format": {"type": "json_schema", "name": "test", "strict": True,
                             "schema": {"type": "object"}}}
        prompts = {"v1": "simple", "v2": "procedural"}
        project.agents.get_version.side_effect = [
            Obj(as_dict=lambda: {
                "name": "contoso-instruction-eval-en-20261001",
                "version": "1",
                "status": "active",
                "metadata": {"instruction_version": "v1", "evaluation_only": "true"},
                "definition": instruction_prompt_agent_lab._definition(prompts["v1"], schema).as_dict(),
            }),
            Obj(as_dict=lambda: {
                "name": "contoso-instruction-eval-en-20261001",
                "version": "2",
                "status": "active",
                "metadata": {"instruction_version": "v2", "evaluation_only": "true"},
                "definition": instruction_prompt_agent_lab._definition(prompts["v2"], schema).as_dict(),
            }),
        ]
        report = {}
        persist = MagicMock()
        versions = instruction_prompt_agent_lab._create_versions(
            project,
            "contoso-instruction-eval-en-20261001",
            prompts,
            schema,
            report,
            persist,
        )
        self.assertEqual(versions, {"v1": "1", "v2": "2"})
        self.assertEqual(report["prompt_agent_versions"]["status"], "active")
        self.assertEqual(project.agents.get_version.call_count, 2)
        project.agents.create_version.assert_not_called()
        persist.assert_called_once()

    def test_refuses_to_invoke_a_mismatched_existing_agent(self):
        project = MagicMock()
        project.agents.list.return_value = [Obj(name="contoso-instruction-eval-en-20261001")]
        project.agents.get_version.return_value.as_dict.return_value = {
            "name": "contoso-instruction-eval-en-20261001",
            "version": "1",
            "status": "active",
            "metadata": {"instruction_version": "v1", "evaluation_only": "true"},
            "definition": {},
        }
        with self.assertRaisesRegex(ValueError, "does not match the approved active instruction definition"):
            instruction_prompt_agent_lab._create_versions(
                project,
                "contoso-instruction-eval-en-20261001",
                {"v1": "simple", "v2": "procedural"},
                {"format": {"type": "json_schema"}},
                {},
                lambda: None,
            )
        project.agents.create_version.assert_not_called()


if __name__ == "__main__":
    unittest.main()
