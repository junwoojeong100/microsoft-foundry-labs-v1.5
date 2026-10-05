import contextlib
import io
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "samples"))
import first_response as lesson


class FirstResponseTests(unittest.TestCase):
    def test_default_plan_shows_the_input_without_reading_cloud_config(self):
        with patch.object(lesson, "read_config", side_effect=AssertionError("No cloud configuration in plan mode")):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(lesson.main([]), 0)

        self.assertIn("PLAN ONLY", output.getvalue())
        self.assertIn(lesson.DEFAULT_QUERIES[lesson.LANGUAGE], output.getvalue())

    def test_custom_query_is_visible_in_the_plan_only(self):
        query = "Use only the synthetic purchasing policy."
        with patch.object(lesson, "read_config", side_effect=AssertionError("No cloud configuration in plan mode")):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(lesson.main(["--query", query]), 0)

        self.assertIn(f"input={query}", output.getvalue())

    def test_long_query_is_rejected_before_any_cloud_configuration(self):
        with patch.object(lesson, "read_config", side_effect=AssertionError("No cloud configuration in plan mode")):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    lesson.main(["--query", "x" * (lesson.MAX_QUERY_CHARACTERS + 1)])

        self.assertEqual(raised.exception.code, 2)

    def test_live_call_is_single_bounded_request(self):
        query = "Synthetic policy question"
        with (
            patch.object(lesson, "read_config", return_value=("https://example.services.ai.azure.com/api/projects/lab", "lab-model")),
            patch("azure.ai.projects.AIProjectClient") as project_factory,
            patch("azure.identity.AzureCliCredential") as credential_factory,
        ):
            project = project_factory.return_value.__enter__.return_value
            client = project.get_openai_client.return_value.__enter__.return_value
            client.responses.create.return_value = SimpleNamespace(
                status="completed",
                output_text="Synthetic answer",
                id="resp_synthetic",
            )

            result = lesson.call_model(query)

        self.assertEqual(result, ("Synthetic answer", "resp_synthetic"))
        credential_factory.assert_called_once_with(process_timeout=30)
        project_factory.assert_called_once_with(
            endpoint="https://example.services.ai.azure.com/api/projects/lab",
            credential=credential_factory.return_value.__enter__.return_value,
            retry_total=0,
        )
        project.get_openai_client.assert_called_once_with(max_retries=0, timeout=60.0)
        client.responses.create.assert_called_once_with(
            model="lab-model",
            input=query,
            max_output_tokens=lesson.MAX_OUTPUT_TOKENS,
            store=False,
        )


if __name__ == "__main__":
    unittest.main()
