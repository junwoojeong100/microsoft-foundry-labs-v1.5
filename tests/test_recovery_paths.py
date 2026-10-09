"""Recovery paths: a failed first attempt must never strand a learner (offline, no Azure calls)."""

import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch
import zipfile
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
sys.path.insert(0, str(ROOT / "scripts"))
import ast
import azure_environment as environment
import build_guide
import check_links
import check_pages
import instruction_prompt_agent_lab as prompt_lab
import lab_cli
import original_files
import package_guide
import stop_sessions
import toolbox_lab
import workshop
from check_independence import check as check_independence

SUBSCRIPTION = "00000000-0000-0000-0000-000000000001"
RG_NAME = "rg-contoso-a-261009abcdef"
PROJECT_ENDPOINT = "https://example.services.ai.azure.com/api/projects/contoso-workshop"


def ledger_state(*, created: bool, **extra) -> dict:
    state = {
        "schema": "contoso-environment-v1", "run_id": "contoso-a-261009abcdef", "language": workshop.LANGUAGE,
        "subscription": SUBSCRIPTION, "tenant": "tenant", "location": "eastus", "resource_group": RG_NAME,
        "resource_group_id": f"/subscriptions/{SUBSCRIPTION}/resourceGroups/{RG_NAME}",
        "account_name": "ai-contoso-a-261009abcdef", "project_name": "contoso-workshop",
        "search_name": "srch-contoso-a-261009abcdef",
        "operations": [{"step": "create-rg", "status": "succeeded"}] if created else [],
        **extra,
    }
    return state


class FakeAz:
    """Records az calls; `group create` fails until `allow_create` is set."""

    def __init__(self, *, group_exists: bool = False, allow_create: bool = True, tags: dict | None = None):
        self.calls: list[tuple] = []
        self.group_exists = group_exists
        self.allow_create = allow_create
        self.tags = tags

    def __call__(self, *args, **kwargs):
        self.calls.append(args)
        if args[:2] == ("account", "show"):
            return {"id": SUBSCRIPTION, "tenantId": "tenant", "state": "Enabled"}
        if args[:2] == ("group", "exists"):
            return self.group_exists
        if args[:2] == ("group", "show"):
            return {"id": f"/subscriptions/{SUBSCRIPTION}/resourceGroups/{RG_NAME}",
                    "tags": self.tags if self.tags is not None else {"validationRun": "contoso-a-261009abcdef"}}
        if args[:2] == ("group", "create"):
            if not self.allow_create:
                raise RuntimeError("az group create failed: ERROR: (RequestDisallowedByPolicy)")
            return {"id": f"/subscriptions/{SUBSCRIPTION}/resourceGroups/{args[args.index('--name') + 1]}"}
        raise AssertionError(f"Unexpected az call: {args}")

    def created(self) -> bool:
        return any(call[:2] == ("group", "create") for call in self.calls)


def create_args(**overrides) -> argparse.Namespace:
    values = {"subscription": SUBSCRIPTION, "location": "eastus", "cost_authorization": "test budget"}
    return argparse.Namespace(**{**values, **overrides})


class EnvironmentTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.ledger = self.directory / "azure-environment.json"
        for name, value in (("LEDGER", self.ledger), ("ENV_FILE", self.directory / ".env")):
            patcher = patch.object(environment, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def write_ledger(self, state: dict) -> None:
        self.ledger.write_text(json.dumps(state), encoding="utf-8")


class CreateRecoveryTests(EnvironmentTestCase):
    def test_location_must_be_a_region_code_before_anything_is_written(self):
        fake = FakeAz()
        with patch.object(environment, "az", fake), self.assertRaisesRegex(ValueError, "region code such as eastus"):
            environment.create(create_args(location="East US"))
        self.assertEqual(fake.calls, [])
        self.assertFalse(self.ledger.exists())

    def test_failed_create_is_archived_and_the_same_command_succeeds_on_retry(self):
        denied = FakeAz(allow_create=False)
        with patch.object(environment, "az", denied), self.assertRaises(RuntimeError):
            environment.create(create_args())
        self.assertTrue(self.ledger.exists())
        first_run = json.loads(self.ledger.read_text(encoding="utf-8"))["run_id"]

        allowed = FakeAz(group_exists=False)
        with patch.object(environment, "az", allowed), contextlib.redirect_stdout(io.StringIO()):
            environment.create(create_args())
        archived = list(self.directory.glob("azure-environment.failed-*.json"))
        self.assertEqual(len(archived), 1)
        self.assertEqual(json.loads(archived[0].read_text(encoding="utf-8"))["run_id"], first_run)
        current = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertNotEqual(current["run_id"], first_run)
        self.assertIn({"step": "create-rg", "status": "succeeded"}, current["operations"])
        self.assertTrue(allowed.created())

    def test_an_interrupted_create_adopts_the_resource_group_it_owns(self):
        self.write_ledger(ledger_state(created=False))
        fake = FakeAz(group_exists=True)
        output = io.StringIO()
        with patch.object(environment, "az", fake), contextlib.redirect_stdout(output):
            environment.create(create_args())
        self.assertFalse(fake.created())
        self.assertTrue(json.loads(output.getvalue())["recovered"])
        state = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertIn({"step": "create-rg", "status": "succeeded", "recovered": True}, state["operations"])
        self.assertEqual(list(self.directory.glob("azure-environment.failed-*.json")), [])

    def test_a_resource_group_that_is_not_proven_ours_is_never_adopted(self):
        self.write_ledger(ledger_state(created=False))
        fake = FakeAz(group_exists=True, tags={"validationRun": "someone-else"})
        with patch.object(environment, "az", fake), self.assertRaisesRegex(ValueError, "not proven to belong"):
            environment.create(create_args())
        self.assertFalse(fake.created())
        self.assertTrue(self.ledger.exists())

    def test_a_finished_ledger_is_never_overwritten_or_marked_failed(self):
        self.write_ledger(ledger_state(created=True))
        before = self.ledger.read_text(encoding="utf-8")
        fake = FakeAz()
        with patch.object(environment, "az", fake), self.assertRaisesRegex(environment.LocalError, "will not be overwritten"):
            environment.create(create_args())
        self.assertEqual(fake.calls, [])
        self.assertEqual(self.ledger.read_text(encoding="utf-8"), before)

    def test_missing_ledger_is_explained_instead_of_a_traceback(self):
        with self.assertRaisesRegex(environment.LocalError, "L01 step 3 creates it"):
            environment.load_ledger()


class SearchOrderTests(EnvironmentTestCase):
    def test_prerequisites_are_checked_before_the_billable_service_is_created(self):
        state = ledger_state(created=True)  # no "foundation" outputs yet
        fake = MagicMock()
        with patch.object(environment, "owned", return_value=state), patch.object(environment, "az", fake):
            with self.assertRaisesRegex(ValueError, "nothing was created"):
                environment.search()
        fake.assert_not_called()

    def test_an_interrupted_search_run_resumes_only_the_missing_role_grants(self):
        search_id = f"/subscriptions/{SUBSCRIPTION}/resourceGroups/{RG_NAME}/providers/Microsoft.Search/searchServices/srch"
        state = ledger_state(
            created=True, search_id=search_id,
            foundation={"projectPrincipalId": {"value": "project-principal"}},
            role_assignments=[{"id": "a", "scope": search_id, "role": "Search Service Contributor"}],
        )
        calls = []

        def fake_az(*args, **kwargs):
            calls.append(args)
            if args[:3] == ("search", "service", "list"):
                return [{"id": search_id, "name": "srch-contoso-a-261009abcdef", "tags": {"validationRun": state["run_id"]}}]
            if args[:3] == ("role", "assignment", "create"):
                return {"id": "grant-" + args[args.index("--role") + 1]}
            raise AssertionError(f"Unexpected az call: {args}")

        with patch.object(environment, "owned", return_value=state), patch.object(environment, "az", fake_az), \
                patch.object(environment, "current_user_id", return_value="user-principal"), \
                patch.object(environment, "persist"), patch.object(environment, "status"):
            environment.search()
        self.assertFalse(any(call[:3] == ("search", "service", "create") for call in calls))
        granted = [call[call.index("--role") + 1] for call in calls if call[:3] == ("role", "assignment", "create")]
        self.assertEqual(granted, ["Search Index Data Contributor", "Search Index Data Reader"])

    def test_a_foreign_search_service_is_still_refused(self):
        state = ledger_state(created=True, foundation={"projectPrincipalId": {"value": "p"}})
        with patch.object(environment, "owned", return_value=state), \
                patch.object(environment, "current_user_id", return_value="u"), \
                patch.object(environment, "az", return_value=[{"id": "other", "name": "other", "tags": {}}]):
            with self.assertRaisesRegex(ValueError, "Search already exists"):
                environment.search()


class PlanOutputTests(EnvironmentTestCase):
    def plan(self, *argv) -> tuple[str, dict]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            environment.main(list(argv))
        first, _, rest = output.getvalue().partition("\n")
        return first, json.loads(rest) if rest.strip() else {}

    def test_create_plan_says_what_would_be_created_without_azure_calls(self):
        with patch.object(environment, "az", MagicMock(side_effect=AssertionError("no Azure call in plan mode"))):
            first, detail = self.plan("create", "--location", "eastus")
        self.assertTrue(first.startswith("PLAN ONLY: create"))
        self.assertEqual(detail["would_create"]["location"], "eastus")
        self.assertIn("validationRun=<run id>", detail["would_create"]["tags"])
        self.assertEqual(detail["azure_calls"], 0)
        self.assertIn("--cost-authorization", detail["needed_to_run"])

    def test_roles_plan_matches_the_four_grants_the_live_step_makes(self):
        _, detail = self.plan("roles")
        planned = [(item["to"], item["role"], item["scope"]) for item in detail["would_grant"]]
        self.assertEqual(planned, list(environment.ROLE_PLAN))
        state = ledger_state(created=True, foundation={
            "projectId": {"value": "project-id"}, "accountId": {"value": "account-id"},
            "projectPrincipalId": {"value": "project-principal"},
        })
        calls = []

        def fake_az(*args, **kwargs):
            calls.append(args)
            return {"id": "grant"}

        with patch.object(environment, "owned", return_value=state), patch.object(environment, "az", fake_az), \
                patch.object(environment, "current_user_id", return_value="user"), \
                patch.object(environment, "persist"), contextlib.redirect_stdout(io.StringIO()):
            environment.roles()
        live = [(call[call.index("--assignee-object-id") + 1], call[call.index("--role") + 1], call[call.index("--scope") + 1])
                for call in calls]
        foundry_user = "53ca6127-db72-4b80-b1b0-d745d6d5456d"
        self.assertEqual(live, [
            ("user", foundry_user, "project-id"),
            ("user", "Cognitive Services OpenAI User", "account-id"),
            ("project-principal", "Cognitive Services OpenAI User", "account-id"),
            ("project-principal", foundry_user, "account-id"),
        ])

    def test_monitoring_plan_reads_the_limits_from_the_bicep_template(self):
        _, detail = self.plan("monitoring")
        bicep = (ROOT / "infra/observability.bicep").read_text(encoding="utf-8")
        days = bicep.split("retentionInDays:")[1].split()[0].rstrip(",")
        quota = bicep.split("dailyQuotaGb:")[1].split()[0].rstrip(",}")
        self.assertIn(f"{days}-day retention, {quota} GB/day", detail["would_create"][0])

    def test_search_plan_warns_that_the_service_is_billed_while_it_exists(self):
        _, detail = self.plan("search")
        self.assertIn("billed for as long as it exists", detail["may_incur_cost"])


class EnvStepTests(EnvironmentTestCase):
    def run_env(self, *, write: bool) -> dict:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            environment.env_step(argparse.Namespace(write=write))
        return json.loads(output.getvalue())

    def finished_ledger(self) -> dict:
        return ledger_state(
            created=True, project_endpoint=PROJECT_ENDPOINT,
            model_deployments={"chat": "contoso-chat", "judge": "contoso-judge", "embedding": "contoso-embedding"},
        )

    def test_plan_mode_shows_the_four_settings_and_changes_nothing(self):
        self.write_ledger(self.finished_ledger())
        env = self.directory / ".env"
        env.write_text("FOUNDRY_PROJECT_ENDPOINT=https://YOUR-RESOURCE.services.ai.azure.com/api/projects/YOUR-PROJECT\n", encoding="utf-8")
        before = env.read_text(encoding="utf-8")
        result = self.run_env(write=False)
        self.assertFalse(result["written"])
        self.assertEqual(result["settings"]["FOUNDRY_PROJECT_ENDPOINT"], "updated")
        self.assertEqual(result["settings"]["FOUNDRY_JUDGE_DEPLOYMENT_NAME"], "added")
        self.assertEqual(env.read_text(encoding="utf-8"), before)

    def test_write_updates_only_the_four_settings_and_keeps_everything_else(self):
        self.write_ledger(self.finished_ledger())
        env = self.directory / ".env"
        env.write_text(
            "# my notes\nexport FOUNDRY_PROJECT_ENDPOINT=https://old.services.ai.azure.com/api/projects/old # stale\n"
            "FOUNDRY_SEARCH_ENDPOINT=https://search.example\nFOUNDRY_MODEL_DEPLOYMENT_NAME=old\n"
            "FOUNDRY_MODEL_DEPLOYMENT_NAME=duplicate\n",
            encoding="utf-8",
        )
        result = self.run_env(write=True)
        self.assertTrue(result["written"])
        text = env.read_text(encoding="utf-8")
        self.assertIn("# my notes", text)
        self.assertIn("FOUNDRY_SEARCH_ENDPOINT=https://search.example", text)
        self.assertEqual(text.count("FOUNDRY_MODEL_DEPLOYMENT_NAME="), 1)
        values = workshop.config_values(env)
        self.assertEqual(values["FOUNDRY_PROJECT_ENDPOINT"], PROJECT_ENDPOINT)
        self.assertEqual(values["FOUNDRY_MODEL_DEPLOYMENT_NAME"], "contoso-chat")
        self.assertEqual(values["FOUNDRY_JUDGE_DEPLOYMENT_NAME"], "contoso-judge")
        self.assertEqual(values["FOUNDRY_EMBEDDING_DEPLOYMENT_NAME"], "contoso-embedding")
        self.assertEqual(self.run_env(write=False)["settings"], {key: "unchanged" for key in result["settings"]})

    def test_new_env_file_is_private(self):
        self.write_ledger(self.finished_ledger())
        self.run_env(write=True)
        self.assertEqual((self.directory / ".env").stat().st_mode & 0o777, 0o600)

    def test_env_needs_a_finished_foundation_step(self):
        self.write_ledger(ledger_state(created=True))
        with self.assertRaisesRegex(environment.LocalError, "Finish L01 step 4"):
            self.run_env(write=True)
        self.assertFalse((self.directory / ".env").exists())


class EnvFileTests(unittest.TestCase):
    def values(self, text: str) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env"
            path.write_text(text, encoding="utf-8")
            with patch.dict(os.environ, {}, clear=True):
                return workshop.config_values(path)

    def test_common_hand_edits_are_accepted(self):
        values = self.values(
            "\ufeffexport FOUNDRY_PROJECT_ENDPOINT=https://x.services.ai.azure.com/api/projects/p\n"
            'FOUNDRY_MODEL_DEPLOYMENT_NAME="contoso-chat"  # my chat model\n'
            "FOUNDRY_JUDGE_DEPLOYMENT_NAME=contoso-judge # judge\n"
        )
        self.assertEqual(values["FOUNDRY_PROJECT_ENDPOINT"], "https://x.services.ai.azure.com/api/projects/p")
        self.assertEqual(values["FOUNDRY_MODEL_DEPLOYMENT_NAME"], "contoso-chat")
        self.assertEqual(values["FOUNDRY_JUDGE_DEPLOYMENT_NAME"], "contoso-judge")

    def test_language_belongs_to_the_shell_and_the_error_says_so(self):
        with self.assertRaisesRegex(ValueError, "shell setting.*export FOUNDRY_LAB_LANGUAGE=en"):
            self.values("FOUNDRY_LAB_LANGUAGE=en\n")

    def test_unknown_settings_list_the_allowed_names(self):
        with self.assertRaisesRegex(ValueError, r"\.env:1: unknown setting 'AZURE_KEY'.*FOUNDRY_PROJECT_ENDPOINT"):
            self.values("AZURE_KEY=secret\n")

    def test_endpoint_mistakes_get_specific_advice(self):
        for endpoint, expected in (
            ("https://YOUR-RESOURCE.services.ai.azure.com/api/projects/YOUR-PROJECT", "still the example text"),
            ("https://actual-resource.services.ai.azure.com/api/projects/contoso-workshop-en", "still the example text"),
            ("https://실제-리소스.services.ai.azure.com/api/projects/실제-프로젝트", "still the example text"),
            ("https://x.services.ai.azure.com/openai/v1", "not a model /openai/v1 endpoint"),
            ("https://example.com/api/projects/p", "public-cloud Foundry project endpoint"),
        ):
            with self.subTest(endpoint=endpoint), self.assertRaisesRegex(ValueError, expected):
                workshop.validate_endpoint(endpoint)

    def test_valid_endpoints_that_contain_placeholder_looking_words_are_accepted(self):
        for endpoint in ("https://r.services.ai.azure.com/api/projects/openai-demo",
                         "https://factual-resource-1.services.ai.azure.com/api/projects/contoso-workshop"):
            with self.subTest(endpoint=endpoint):
                self.assertEqual(workshop.validate_endpoint(endpoint + "/"), endpoint)

    def report(self, text: str | None, ledger: dict | None = None) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            path, record = Path(directory) / ".env", Path(directory) / "ledger.json"
            if text is not None:
                path.write_text(text, encoding="utf-8")
            if ledger is not None:
                record.write_text(json.dumps(ledger), encoding="utf-8")
            with patch.dict(os.environ, {}, clear=True):
                return workshop.env_report(path, record)

    def test_doctor_treats_the_template_as_not_ready_yet_but_not_as_a_problem(self):
        template = (ROOT / ".env.example").read_text(encoding="utf-8")
        lines = self.report(template)
        self.assertFalse([line for line in lines if line.startswith("PROBLEM")], lines)
        self.assertIn("project endpoint: not set yet (expected until L01 step 5)", lines)
        self.assertEqual(self.report(None), [".env: not configured yet; L01 step 5 fills it in."])

    def test_doctor_flags_a_broken_env_and_a_mismatch_with_the_ownership_record(self):
        self.assertTrue(self.report("FOUNDRY_LAB_LANGUAGE=en\n")[0].startswith("PROBLEM .env:1"))
        text = f"FOUNDRY_PROJECT_ENDPOINT={PROJECT_ENDPOINT}\nFOUNDRY_MODEL_DEPLOYMENT_NAME=contoso-chat\n"
        good = {"project_endpoint": PROJECT_ENDPOINT, "model_deployments": {"chat": "contoso-chat"}}
        self.assertIn("matches results/azure-environment.json", self.report(text, good))
        other = {**good, "project_endpoint": "https://other.services.ai.azure.com/api/projects/other"}
        self.assertTrue(any(line.startswith("PROBLEM .env endpoint differs") for line in self.report(text, other)))
        renamed = {**good, "model_deployments": {"chat": "another-chat"}}
        self.assertTrue(any(line.startswith("PROBLEM .env chat deployment differs") for line in self.report(text, renamed)))

    def test_doctor_exit_code_follows_the_problems(self):
        output = io.StringIO()
        with patch.object(workshop, "env_report", return_value=["PROBLEM broken"]), contextlib.redirect_stdout(output):
            self.assertEqual(workshop.main(["doctor"]), 1)
        self.assertIn(".env check: PROBLEM broken", output.getvalue())
        with patch.object(workshop, "env_report", return_value=["project endpoint: not set yet (expected until L01 step 5)"]), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(workshop.main(["doctor"]), 0)


class RetryableOriginalTests(unittest.TestCase):
    def test_failure_before_any_azure_change_frees_the_path_and_keeps_the_record(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "original.json"
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr), self.assertRaises(ValueError):
                with original_files.retryable_original(output) as attempt:
                    os.close(original_files.open_original(output, attempt))
                    output.write_text('{"status": "failed"}', encoding="utf-8")
                    raise ValueError("not signed in")
            self.assertFalse(output.exists())
            kept = list(Path(directory).glob("original.failed-*.json"))
            self.assertEqual([path.read_text(encoding="utf-8") for path in kept], ['{"status": "failed"}'])
            self.assertIn("No Azure change was made", stderr.getvalue())

    def test_failure_after_an_azure_change_keeps_the_original_in_place(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "original.json"
            with self.assertRaises(RuntimeError):
                with original_files.retryable_original(output) as attempt:
                    os.close(original_files.open_original(output, attempt))
                    attempt.side_effects = True
                    raise RuntimeError("timed out")
            self.assertTrue(output.exists())
            self.assertEqual(list(Path(directory).glob("original.failed-*.json")), [])

    def test_an_original_this_call_did_not_create_is_never_touched(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "original.json"
            output.write_text("earlier run", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                with original_files.retryable_original(output) as attempt:
                    original_files.open_original(output, attempt)
            self.assertEqual(output.read_text(encoding="utf-8"), "earlier run")

    def test_prompt_agent_collection_can_be_rerun_after_a_preflight_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            results = Path(directory)
            output = results / "instruction-prompt-agent-test.json"

            @contextlib.contextmanager
            def not_signed_in():
                raise ValueError("Please run 'az login' to set up an account.")
                yield

            with patch.object(prompt_lab, "RESULTS", results), patch.object(prompt_lab, "project_client", not_signed_in), \
                    contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaisesRegex(ValueError, "az login"):
                    prompt_lab.compare(output)
            self.assertFalse(output.exists())
            (record,) = results.glob("instruction-prompt-agent-test.failed-*.json")
            kept = json.loads(record.read_text(encoding="utf-8"))
            self.assertEqual((kept["status"], kept["target_calls"]), ("failed", 0))

    def test_prompt_agent_original_stays_once_an_agent_version_may_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            results = Path(directory)
            output = results / "instruction-prompt-agent-test.json"
            project = MagicMock()
            deployment = {"name": "contoso-chat", "modelName": prompt_lab.TARGET_MODEL, "modelVersion": prompt_lab.TARGET_MODEL_VERSION}
            project.deployments.get.return_value.as_dict.return_value = deployment

            @contextlib.contextmanager
            def signed_in():
                yield project, None, PROJECT_ENDPOINT, "contoso-chat"

            with patch.object(prompt_lab, "RESULTS", results), patch.object(prompt_lab, "project_client", signed_in), \
                    patch.object(prompt_lab, "verify_profile", return_value={"language": workshop.LANGUAGE}), \
                    patch.object(prompt_lab, "_create_versions", side_effect=RuntimeError("did not become active")):
                with self.assertRaisesRegex(RuntimeError, "did not become active"):
                    prompt_lab.compare(output)
            self.assertTrue(output.exists())
            self.assertEqual(list(results.glob("*.failed-*.json")), [])


class EntryPointWiringTests(unittest.TestCase):
    def test_no_entry_point_shadows_the_imported_lab_runner(self):
        checked = 0
        for path in sorted([*(ROOT / "samples").glob("*.py"), *(ROOT / "scripts").glob("*.py")]):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            bound = {alias.asname or alias.name for node in tree.body if isinstance(node, ast.ImportFrom)
                     and node.module == "lab_cli" for alias in node.names if alias.name == "run"}
            if not bound:
                continue
            checked += 1
            defined = {node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
            defined |= {target.id for node in tree.body if isinstance(node, ast.Assign)
                        for target in node.targets if isinstance(target, ast.Name)}
            with self.subTest(script=path.name):
                self.assertFalse(bound & defined, f"{path.name} defines a top-level name that replaces the imported runner")
        self.assertGreaterEqual(checked, 14)

    def test_entry_points_that_once_collided_start_and_print_usage(self):
        import subprocess
        for script in ("a2a_lab.py", "memory_lab.py", "routine_lab.py", "multi_agent.py"):
            with self.subTest(script=script):
                result = subprocess.run([sys.executable, str(ROOT / "samples" / script), "--help"],
                                        capture_output=True, text=True, timeout=120)
                self.assertEqual(result.returncode, 0, result.stderr[-400:])
                self.assertIn("usage:", result.stdout)


class CliWrapperTests(unittest.TestCase):
    def run_main(self, main) -> tuple[int, str]:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as caught:
            lab_cli.run(main)
        return caught.exception.code, stderr.getvalue()

    def test_expected_errors_become_one_line_with_exit_code_two(self):
        def fail():
            raise ValueError("Approval required: repeat with --approve-tool EXACT_NAME.")

        code, text = self.run_main(fail)
        self.assertEqual((code, text), (2, "ERROR: Approval required: repeat with --approve-tool EXACT_NAME.\n"))

    def test_task_group_wrapping_is_removed(self):
        def fail():
            raise ExceptionGroup("unhandled errors in a TaskGroup", [ExceptionGroup("inner", [ValueError("real cause")])])

        self.assertEqual(self.run_main(fail), (2, "ERROR: real cause\n"))

    def test_service_errors_point_to_the_troubleshooting_table(self):
        from azure.core.exceptions import AzureError

        def fail():
            raise AzureError("(AuthorizationFailed) no permission")

        code, text = self.run_main(fail)
        self.assertEqual(code, 2)
        self.assertIn("ERROR: (AuthorizationFailed) no permission", text)
        self.assertIn("troubleshooting", text)

    def test_unexpected_errors_and_debug_mode_keep_the_traceback(self):
        def bug():
            raise KeyError("missing")

        with self.assertRaises(KeyError):
            lab_cli.run(bug)

        def fail():
            raise ValueError("shown with a traceback in debug mode")

        with patch.dict(os.environ, {"FOUNDRY_LAB_DEBUG": "1"}), self.assertRaises(ValueError):
            lab_cli.run(fail)

    def test_return_codes_and_interrupts(self):
        self.assertEqual(self.run_main(lambda: 3)[0], 3)
        self.assertEqual(self.run_main(lambda: None)[0], 0)

        def interrupted():
            raise KeyboardInterrupt

        self.assertEqual(self.run_main(interrupted)[0], 130)


class ToolboxApprovalTests(unittest.TestCase):
    def test_the_intended_approval_stop_is_recorded_and_shown_as_the_real_error(self):
        evidence = MagicMock()
        evidence.path = Path("results/evidence.jsonl")
        wrapped = ExceptionGroup("unhandled errors in a TaskGroup", [ValueError("Approval required: review arguments")])
        argv = ["toolbox_lab.py", "call", "--local", "--tool", "get_stock", "--arguments", "{}"]

        def raise_wrapped(coroutine):
            coroutine.close()
            raise wrapped

        with patch.object(sys, "argv", argv), patch.object(toolbox_lab, "Evidence", return_value=evidence), \
                patch.object(toolbox_lab.asyncio, "run", side_effect=raise_wrapped), \
                contextlib.redirect_stdout(io.StringIO()) as shown:
            with self.assertRaises(ValueError) as caught:
                toolbox_lab.main()
        self.assertEqual(str(caught.exception), "Approval required: review arguments")
        evidence.failure.assert_called_once_with(caught.exception)
        self.assertIn("Evidence: results/evidence.jsonl", shown.getvalue())


class StopSessionsTests(unittest.TestCase):
    def test_every_recorded_session_is_attempted_even_after_a_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "results").mkdir()
            for index, agent in enumerate(("not-ours", "contoso-purchasing", "contoso-purchasing")):
                (root / "results" / f"contoso-hosted-client-{index}-session.json").write_text(
                    json.dumps({"agent": agent, "session_id": f"session-{index}"}), encoding="utf-8")
            stopped = []

            def fake_run(command, **kwargs):
                if command[4] == "stop":
                    stopped.append(command[5])
                    return MagicMock(returncode=1 if command[5] == "session-1" else 0, stdout="", stderr="")
                return MagicMock(returncode=0, stdout=json.dumps({"status": "idle"}))

            evidence = MagicMock()
            evidence.path = Path("evidence.jsonl")
            with patch.object(stop_sessions, "ROOT", root), patch.object(stop_sessions, "Evidence", return_value=evidence), \
                    patch.object(stop_sessions.subprocess, "run", side_effect=fake_run):
                with self.assertRaisesRegex(RuntimeError, "not confirmed for 2 of 3"):
                    stop_sessions.main()
            self.assertEqual(stopped, ["session-1", "session-2"])


class WorkshopPlanTests(unittest.TestCase):
    def plan(self, command: str) -> str:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(workshop.main([command]), 0)
        return output.getvalue()

    def test_capstone_plan_states_the_limits_the_live_run_enforces(self):
        text = self.plan("capstone")
        budget = workshop.RUN_BUDGET
        self.assertIn(f"at most {budget['max_requests']} requests, {budget['max_tokens']:,} tokens", text)
        self.assertIn(f"{budget['max_seconds']} seconds", text)
        self.assertIn(f"At most {workshop.MAX_ROUNDS} model rounds and {workshop.MAX_TOOL_CALLS} function calls.", text)
        self.assertNotIn("function calls", self.plan("agent"))

    def test_model_plan_states_its_single_request(self):
        self.assertIn("one model request with at most 2,048 output tokens", self.plan("model"))


class RepositoryHygieneTests(unittest.TestCase):
    def test_codespaces_installs_the_pinned_azd_and_agent_extension(self):
        release = json.loads((ROOT / "content/release.json").read_text(encoding="utf-8"))
        feature = json.loads((ROOT / ".devcontainer/devcontainer.json").read_text(encoding="utf-8"))["features"][
            "ghcr.io/azure/azure-dev/azd:0"]
        self.assertEqual(feature["version"], release["azd"])
        self.assertEqual(feature["extensions"], f"azure.ai.agents --version {release['agent_extension']}")

    def test_learner_text_does_not_carry_the_authoring_tool_marker(self):
        for path in [*(ROOT / "docs").rglob("*.md"), ROOT / "README.md", ROOT / "README.ko.md"]:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertNotIn("AZURE_DEV_USER_AGENT", path.read_text(encoding="utf-8"))

    def test_every_virtualenv_and_private_env_variant_is_ignored(self):
        lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn(".venv*/", lines)
        self.assertIn(".env.*", lines)
        self.assertLess(lines.index(".env.*"), lines.index("!.env.example"))

    def test_guide_footer_offers_a_feedback_path_and_the_sample_receipt_has_a_purpose(self):
        labels = json.loads((ROOT / "content/reader-labels.json").read_text(encoding="utf-8"))
        for language in ("ko", "en"):
            self.assertIn("feedback", labels[language])
            self.assertNotIn("합성 영수증", labels[language]["receipt"])
        self.assertTrue((ROOT / ".github/ISSUE_TEMPLATE/guide-problem.yml").is_file())
        self.assertTrue((ROOT / "LICENSE").read_text(encoding="utf-8").startswith("MIT License"))
        for html in ("index.html", "index.ko.html"):
            self.assertIn("issues/new/choose", (ROOT / html).read_text(encoding="utf-8"))


class DeferredImageTests(unittest.TestCase):
    def test_png_figures_reserve_their_size_and_load_lazily(self):
        image = '<img alt="x" src="assets/portal/01-home.png" />'
        self.assertEqual(
            build_guide.deferred_image(image, "assets/portal/01-home.png"),
            '<img alt="x" src="assets/portal/01-home.png" loading="lazy" decoding="async" width="1440" height="1000" />',
        )
        svg = build_guide.deferred_image('<img alt="x" src="assets/architecture.svg" />', "assets/architecture.svg")
        self.assertIn('loading="lazy" decoding="async"', svg)
        self.assertNotIn("width=", svg)

    def test_every_generated_figure_is_deferred(self):
        for html in ("index.html", "index.ko.html"):
            text = (ROOT / html).read_text(encoding="utf-8")
            figures = text.count("<figure")
            self.assertGreater(figures, 10)
            self.assertEqual(len(re.findall(r'<figure[^>]*><img [^>]*loading="lazy" decoding="async"', text)), figures)


class PackagingTests(unittest.TestCase):
    FILES = [ROOT / ".nojekyll", ROOT / "LICENSE", ROOT / "THIRD_PARTY_NOTICES"]

    def test_the_same_sources_give_the_same_zip_with_fixed_entry_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory) / "a.zip", Path(directory) / "b.zip"
            package_guide.write_archive(first, self.FILES)
            time.sleep(1.1)  # a different wall-clock time must not change any entry
            package_guide.write_archive(second, self.FILES)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            year, month, day = (int(part) for part in build_guide.RELEASE["edition"].split("-"))
            with zipfile.ZipFile(first) as archive:
                for info in archive.infolist():
                    self.assertEqual(info.date_time, (year, month, day, 0, 0, 0))
                    self.assertEqual(info.create_system, 3)
                    self.assertIn(info.external_attr >> 16, (0o644, 0o755))
                self.assertEqual(archive.namelist(), sorted(archive.namelist()))

    def test_check_reports_missing_extra_and_changed_members(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "kit.zip"
            package_guide.write_archive(target, self.FILES[:2])
            self.assertEqual(package_guide.mismatches(target, self.FILES[:2]), [])
            missing = package_guide.mismatches(target, self.FILES)
            self.assertEqual(missing, [f"missing from ZIP: {package_guide.NAME}/THIRD_PARTY_NOTICES"])
            extra = package_guide.mismatches(target, self.FILES[:1])
            self.assertEqual(extra, [f"not in the kit sources: {package_guide.NAME}/LICENSE"])
            with patch.object(package_guide.zlib, "crc32", return_value=1):
                changed = package_guide.mismatches(target, self.FILES[:2])
            self.assertEqual(len(changed), 2)
            self.assertTrue(all(item.startswith("differs from the source file") for item in changed))
            self.assertEqual(package_guide.mismatches(Path(directory) / "none.zip", self.FILES), ["missing archive: none.zip"])

    def test_a_failed_verification_keeps_the_published_zip(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(package_guide, "ROOT", Path(directory).resolve()):
            published = Path(directory).resolve() / "downloads" / "kit.zip"
            published.parent.mkdir()
            published.write_bytes(b"previous verified kit")
            with patch.dict(package_guide.RELEASE, {"archive": "downloads/kit.zip"}), \
                    patch.object(package_guide, "collect_files", return_value=[]), \
                    patch.object(package_guide, "load_portal_captures", return_value=[]), \
                    patch.object(package_guide, "write_archive", side_effect=lambda target, files: target.write_bytes(b"partial")), \
                    patch.object(package_guide, "verify_archive", side_effect=ValueError("verification failed")), \
                    patch.object(sys, "argv", ["package_guide.py"]):
                with self.assertRaisesRegex(ValueError, "verification failed"):
                    package_guide.main()
            self.assertEqual(published.read_bytes(), b"previous verified kit")
            self.assertEqual([path.name for path in published.parent.iterdir()], ["kit.zip"])


class LinkAndPageCheckTests(unittest.TestCase):
    def test_pages_changed_after_the_review_date_are_reported_newest_first(self):
        rows = [
            {"url": "a", "document_ms_date": "2026-10-01T00:00:00Z"},
            {"url": "b", "document_ms_date": "2026-09-30T00:00:00Z"},
            {"url": "c", "document_ms_date": None},
            {"url": "d", "document_ms_date": "2026-10-06T00:00:00Z"},
        ]
        self.assertEqual(check_links.changed_since_review(rows, "2026-09-30"), [
            {"url": "d", "document_ms_date": "2026-10-06"}, {"url": "a", "document_ms_date": "2026-10-01"},
        ])

    def test_transient_failures_are_retried_but_a_real_404_is_not(self):
        outcomes = [{"reachable": False, "http_status": 503}, {"reachable": False, "http_status": None},
                    {"reachable": True, "http_status": 200}]
        with patch.object(check_links, "inspect_once", side_effect=outcomes), patch.object(check_links.time, "sleep"):
            self.assertTrue(check_links.inspect_url("https://learn.microsoft.com/x")["reachable"])
        with patch.object(check_links, "inspect_once", return_value={"reachable": False, "http_status": 404}) as once:
            self.assertFalse(check_links.inspect_url("https://learn.microsoft.com/x")["reachable"])
        self.assertEqual(once.call_count, 1)

    def test_the_pages_check_waits_for_a_file_that_is_not_published_yet(self):
        class Response:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def read(self):
                return b"published"

        errors = [HTTPError("u", 404, "Not Found", {}, None), URLError("reset"), Response()]
        with patch.object(check_pages, "urlopen", side_effect=errors), patch.object(check_pages.time, "sleep"):
            self.assertEqual(check_pages.fetch("https://example.invalid/file"), b"published")
        with patch.object(check_pages, "urlopen", side_effect=HTTPError("u", 403, "Forbidden", {}, None)), \
                patch.object(check_pages.time, "sleep") as pause, self.assertRaises(HTTPError):
            check_pages.fetch("https://example.invalid/file")
        pause.assert_not_called()

    def test_learner_facing_text_cannot_point_at_the_archived_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder in ("samples", "scripts", "infra", "hosted", ".github", ".devcontainer", "docs", "content", "data", "assets"):
                (root / folder).mkdir()
            for name in ("azure.yaml", "package.json", "README.md", "README.ko.md"):
                (root / name).write_text("ok", encoding="utf-8")
            self.assertEqual(check_independence(root)["reference_repository_dependencies"], 0)
            (root / "docs" / "start.md").write_text("see microsoft-" + "foundry-labs-v1.3", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must be self-contained"):
                check_independence(root)
            (root / "docs" / "start.md").write_text("ok", encoding="utf-8")
            (root / ".devcontainer" / "post-create.sh").write_text("cd /Users/someone/lab", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Personal/external filesystem dependency"):
                check_independence(root)


if __name__ == "__main__":
    unittest.main()
