import asyncio
import contextlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
import local_lab
import multi_agent
import prepare_practice
import prepare_tuning


def response(name="fixture", usage=True, finish="stop", text="Synthetic fixture answer"):
    return SimpleNamespace(
        text=text, response_id=name, finish_reason=finish,
        usage_details={"input_token_count": 10, "output_token_count": 5} if usage else None,
    )


class MultiAgentExerciseTests(unittest.TestCase):
    def test_live_runner_uses_the_exact_verified_configuration_snapshot(self):
        endpoint = "https://contoso-fixture.services.ai.azure.com/api/projects/lab"
        evidence = Mock(path=Path("results/synthetic-fixture.jsonl"))
        report = {"paths": {"single": {"usage_complete": True}}}
        modules = {
            "agent_framework": SimpleNamespace(AgentFrameworkException=RuntimeError),
            "azure.core.exceptions": SimpleNamespace(AzureError=RuntimeError),
            "openai": SimpleNamespace(OpenAIError=RuntimeError),
        }
        with patch.dict(sys.modules, modules), patch.object(
            multi_agent, "read_config", return_value=(endpoint, "fixture-model"),
        ) as config, patch.object(multi_agent, "verify_scope") as verify, patch.object(
            multi_agent, "Evidence", return_value=evidence,
        ), patch.object(
            multi_agent, "check_ready", return_value={"chat": {"subscription": "fixture-subscription"}},
        ) as readiness, patch.object(
            multi_agent, "run", new_callable=AsyncMock, return_value=report,
        ) as run, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(multi_agent.main(["--mode", "compare", "--live"]), 0)
        config.assert_called_once()
        verify.assert_called_once_with(endpoint, multi_agent.RESULTS / "azure-environment.json")
        readiness.assert_called_once_with(
            multi_agent.RESULTS / "azure-environment.json", ("chat",), 1,
            expected_endpoint=endpoint, expected_deployment="fixture-model",
        )
        run.assert_awaited_once_with(
            "compare", "purchase", evidence, endpoint, "fixture-model", subscription="fixture-subscription",
        )

    def test_plan_never_initializes_sdk_or_writes_evidence(self):
        with contextlib.redirect_stdout(io.StringIO()) as output, patch.object(
            multi_agent, "run", new_callable=AsyncMock,
        ) as run, patch.object(multi_agent, "Evidence") as evidence:
            self.assertEqual(multi_agent.main(["--mode", "compare"]), 0)
        self.assertIn('"model_calls_if_approved": 3', output.getvalue())
        run.assert_not_called()
        evidence.assert_not_called()

    def test_comparison_preserves_three_originals_and_actual_usage(self):
        agent = SimpleNamespace(run=AsyncMock(return_value=response("single")))
        events = SimpleNamespace(
            get_intermediate_outputs=lambda: [response("draft")],
            get_outputs=lambda: [response("review")],
        )
        workflow = SimpleNamespace(run=AsyncMock(return_value=events))
        client = object()
        with patch.object(multi_agent, "build_drafter", return_value=agent) as single_builder, patch.object(
            multi_agent, "build_workflow", return_value=workflow,
        ) as workflow_builder:
            report = asyncio.run(multi_agent.compare_paths(
                client, "compare", "same synthetic question", Mock(), policy="same synthetic policy",
            ))
        single_builder.assert_called_once_with(client, name="single", policy="same synthetic policy")
        workflow_builder.assert_called_once_with(client, policy="same synthetic policy")
        self.assertEqual(report["policy_sha256"], multi_agent.digest("same synthetic policy"))
        agent.run.assert_awaited_once_with("same synthetic question")
        workflow.run.assert_awaited_once_with("same synthetic question")
        self.assertEqual(report["paths"]["single"]["total_tokens"], 15)
        self.assertEqual(report["paths"]["sequential"]["total_tokens"], 30)
        self.assertEqual(report["sequential_minus_single"]["total_tokens"], 15)
        self.assertEqual(
            [stage["response_id"] for stage in report["paths"]["sequential"]["stages"]],
            ["draft", "review"],
        )
        self.assertFalse(report["quality_release"])

    def test_missing_usage_is_not_zero(self):
        record = multi_agent.response_record(response(usage=False), "drafter")
        self.assertFalse(record["usage_complete"])
        self.assertIsNone(record["total_tokens"])
        path = multi_agent.path_record([record], 1.0)
        self.assertIsNone(path["total_tokens"])

    def test_incomplete_empty_or_duplicate_responses_are_rejected(self):
        for item in (response(finish="length"), response(text=""), response(name=None)):
            with self.subTest(item=item), self.assertRaises(RuntimeError):
                multi_agent.response_record(item, "reviewer")
        with self.assertRaises(RuntimeError):
            multi_agent.one_response([response(), response()], "drafter")
        with self.assertRaises(ValueError):
            asyncio.run(multi_agent.compare_paths(object(), "unknown", "fixture", Mock()))

    def test_ownership_must_match_endpoint_and_language(self):
        with tempfile.TemporaryDirectory() as temporary:
            receipt = Path(temporary) / "scope.json"
            state = {
                "account_name": "contoso-fixture", "project_name": "lab",
                "project_endpoint": "https://contoso-fixture.services.ai.azure.com/api/projects/lab",
                "language": multi_agent.LANGUAGE,
            }
            receipt.write_text(json.dumps(state))
            multi_agent.verify_scope(state["project_endpoint"], receipt)
            with self.assertRaises(ValueError):
                multi_agent.verify_scope("https://other.services.ai.azure.com/api/projects/lab", receipt)
            state["language"] = "en" if multi_agent.LANGUAGE == "ko" else "ko"
            receipt.write_text(json.dumps(state))
            with self.assertRaises(ValueError):
                multi_agent.verify_scope(state["project_endpoint"], receipt)


class FakeLocalModel:
    id = "contoso-local-fixture"

    def __init__(self, *, cached=True, loaded=False, finish="stop"):
        self.is_cached = cached
        self.is_loaded = loaded
        self.unload_calls = 0
        self.client = SimpleNamespace(
            settings=SimpleNamespace(max_tokens=None),
            complete_chat=Mock(return_value=SimpleNamespace(choices=[
                SimpleNamespace(finish_reason=finish, message=SimpleNamespace(content="Synthetic local fixture"))
            ])),
        )

    def load(self):
        self.is_loaded = True

    def unload(self):
        self.unload_calls += 1
        self.is_loaded = False

    def download(self, callback):
        self.is_cached = True

    def get_chat_client(self):
        return self.client


class LocalExerciseTests(unittest.TestCase):
    def manager(self, model):
        return SimpleNamespace(
            catalog=SimpleNamespace(get_model=Mock(return_value=model)),
            download_and_register_eps=Mock(),
        )

    def test_plan_does_not_import_native_sdk(self):
        with patch.dict(sys.modules, {"foundry_local_sdk": None}), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(local_lab.main(["chat"]), 0)
        self.assertFalse(json.loads(output.getvalue())["sdk_initialized"])

    def test_chat_is_bounded_and_unloads_the_same_model(self):
        model = FakeLocalModel()
        report = local_lab.exercise(self.manager(model), "chat", "fixture", "sentence", False)
        self.assertEqual(model.client.settings.max_tokens, 256)
        self.assertEqual(model.unload_calls, 1)
        self.assertTrue(report["unloaded"])
        self.assertEqual(report["execution"], "on_device_not_azure")
        model.client.complete_chat.assert_called_once_with(local_lab.messages("sentence"))

    def test_truncated_generation_still_unloads(self):
        model = FakeLocalModel(finish="length")
        with self.assertRaises(RuntimeError):
            local_lab.exercise(self.manager(model), "chat", "fixture", "sentence", False)
        self.assertEqual(model.unload_calls, 1)

    def test_missing_cache_and_borrowed_load_are_not_used(self):
        for model in (FakeLocalModel(cached=False), FakeLocalModel(loaded=True)):
            with self.subTest(model=model), self.assertRaises(RuntimeError):
                local_lab.exercise(self.manager(model), "chat", "fixture", "sentence", False)
            self.assertEqual(model.unload_calls, 0)
            model.client.complete_chat.assert_not_called()

    def test_download_requires_its_own_opt_in(self):
        model = FakeLocalModel(cached=False)
        manager = self.manager(model)
        with self.assertRaises(ValueError):
            local_lab.exercise(manager, "download", "fixture", "sentence", False)
        manager.download_and_register_eps.assert_not_called()
        report = local_lab.exercise(manager, "download", "fixture", "sentence", True)
        self.assertTrue(report["cached"])
        model.client.complete_chat.assert_not_called()

    def test_only_style_changes_between_comparison_inputs(self):
        for language in ("ko", "en"):
            with patch.object(local_lab, "LANGUAGE", language):
                sentence, checklist = local_lab.messages("sentence"), local_lab.messages("checklist")
            self.assertEqual(sentence[1], checklist[1])
            self.assertNotEqual(sentence[0], checklist[0])


class PracticeWalkthroughTests(unittest.TestCase):
    chapters = {"governance": "21-governance.md", "delivery": "22-delivery.md"}
    counts = {"governance": (5, 2), "delivery": (5, 3)}

    def test_documented_repairs_fix_real_copied_exercises_in_both_languages(self):
        for lab, chapter in self.chapters.items():
            solutions = []
            for directory in ("docs", "docs/en"):
                text = (ROOT / directory / chapter).read_text()
                match = re.search(rf"<!-- solution:{lab} -->\s*```python\n(.*?)\n```", text, re.S)
                self.assertIsNotNone(match, (directory, lab))
                solutions.append(match[1])
            self.assertEqual(*solutions, "The same local contract applies in both languages.")
            with self.subTest(lab=lab), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                shutil.copytree(ROOT / "data/exercises" / lab, root / "data/exercises" / lab)
                destination = prepare_practice.prepare(lab, Path("practice") / lab, root=root)
                command = [sys.executable, "-m", "unittest", "discover", "-s", str(destination), "-p", "test_exercise.py", "-v"]
                environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
                before = subprocess.run(command, cwd=root, env=environment, capture_output=True, text=True, timeout=30)
                cases, failures = self.counts[lab]
                self.assertEqual(before.returncode, 1, before.stdout + before.stderr)
                self.assertIn(f"Ran {cases} tests", before.stderr)
                self.assertIn(f"failures={failures}", before.stderr)
                tests_before = (destination / "test_exercise.py").read_bytes()
                (destination / "exercise.py").write_text(solutions[0] + "\n")
                after = subprocess.run(command, cwd=root, env=environment, capture_output=True, text=True, timeout=30)
                self.assertEqual(after.returncode, 0, after.stdout + after.stderr)
                self.assertEqual((destination / "test_exercise.py").read_bytes(), tests_before)
                with self.assertRaises(FileExistsError):
                    prepare_practice.prepare(lab, Path("practice") / lab, root=root)
                with self.assertRaises(ValueError):
                    prepare_practice.prepare(lab, Path("docs"), root=root)

    def test_practice_workflow_is_manual_and_has_no_azure_or_write_permission(self):
        text = (ROOT / "data/exercises/delivery/workflow.yml").read_text()
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("contents: read", text)
        self.assertIn("practice/delivery", text)
        self.assertNotRegex(text, r"secrets\.|id-token:|contents: write|az login|azd|azure/login")

    def test_each_flagged_module_has_a_concrete_bilingual_experiment(self):
        for language, directory, labels in (
            ("ko", "docs", ("직접 해보기", "한 가지 바꾸기", "결과 설명하기")),
            ("en", "docs/en", ("Try it", "Change one thing", "Explain the result")),
        ):
            for filename in ("15-multiagent.md", "21-governance.md", "22-delivery.md"):
                text = (ROOT / directory / filename).read_text()
                with self.subTest(language=language, filename=filename):
                    self.assertIn('class="practice-block"', text)
                    for label in labels:
                        self.assertIn("**" + label, text)

    def test_orchestration_lesson_exposes_four_builders_and_capacity_preflight(self):
        for directory in ("docs", "docs/en"):
            text = (ROOT / directory / "15-multiagent.md").read_text()
            with self.subTest(directory=directory):
                for builder in ("SequentialBuilder", "ConcurrentBuilder", "GroupChatBuilder", "HandoffBuilder"):
                    self.assertIn(builder, text)
                for mode in multi_agent.ORCHESTRATIONS:
                    self.assertIn(f"--mode {mode} --live", text)
                self.assertIn("model_capacity.py check --roles chat --live", text)
                self.assertIn("2,048", text)
                self.assertIn("100,000", text)

    def test_cu_configuration_uses_supported_types_and_preserves_expected_fields(self):
        for data in ("data", "data/en"):
            schema = json.loads((ROOT / data / "exercises/receipt-analyzer.json").read_text())
            self.assertEqual(schema["baseAnalyzerId"], "prebuilt-document")
            fields = schema["fieldSchema"]["fields"]
            self.assertEqual(set(fields), {"document_id", "date", "currency", "quantity", "unit_price", "total", "approval_status"})
            self.assertEqual(fields["quantity"]["type"], "number")
            self.assertEqual(fields["date"]["type"], "date")
            self.assertEqual(fields["approval_status"]["enum"], ["pending", "approved", "unknown"])
            for field in fields.values():
                self.assertIn(field["type"], {"string", "number", "date"})
                if field["method"] == "extract":
                    self.assertTrue(field["estimateSourceAndConfidence"])

    def test_tuning_copy_repair_preserves_the_original_and_exact_split(self):
        for language, data in (("ko", "data"), ("en", "data/en")):
            original = (ROOT / data / "tuning/examples.json").read_bytes()
            examples = json.loads(original)
            with self.subTest(language=language), tempfile.TemporaryDirectory() as temporary:
                source = Path(temporary) / "examples.json"
                destination = Path(temporary) / "generated"
                expected = examples[0]["label"]
                examples[0]["label"] = "POLCIY"
                source.write_text(json.dumps(examples))
                with self.assertRaisesRegex(ValueError, "Unrecognized training label"):
                    prepare_tuning.prepare(destination, source)
                self.assertFalse(destination.exists())
                examples[0]["label"] = expected
                source.write_text(json.dumps(examples))
                with patch.object(prepare_tuning, "SYSTEM", "Synthetic format exercise"):
                    self.assertEqual(prepare_tuning.prepare(destination, source), (16, 8))
                self.assertTrue((destination / "train.jsonl").read_bytes().startswith(b"\xef\xbb\xbf"))
                self.assertEqual((ROOT / data / "tuning/examples.json").read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
