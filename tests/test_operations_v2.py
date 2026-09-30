import contextlib
import copy
import base64
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
import optimizer_lab
import routine_lab

ENDPOINT = "https://owned.services.ai.azure.com/api/projects/workshop"


class OperationalFiles(unittest.TestCase):
    def setUp(self):
        sdk_errors = patch.dict(sys.modules, {"azure.core.exceptions": SimpleNamespace(AzureError=RuntimeError)})
        sdk_errors.start()
        self.addCleanup(sdk_errors.stop)
        self.directory = ROOT / ".build" / ("operations-unit-" + uuid4().hex)
        self.directory.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, self.directory)
        self.evidence = SimpleNamespace(
            append=Mock(), failure=Mock(), run_id="contoso-optimizer-unit", path=self.directory / "evidence.jsonl",
        )
        self.environment = {
            "account_name": "owned", "project_name": "workshop", "project_endpoint": ENDPOINT,
            "subscription": "owned-subscription", "resource_group_id": "/subscriptions/owned/resourceGroups/owned",
        }
        (self.directory / "azure-environment.json").write_text(json.dumps(self.environment))

    def args(self, **changes):
        values = {
            "agent": "contoso-agent", "version": "2", "optimizer_deployment": "reflection",
            "suite": "automated-v2", "resume": None, "command": "scheduled-test",
            "max_seconds": 600,
            "prompt_file": optimizer_lab.DATA / "prompts/agent-v4.txt",
            "receipt": self.directory / "routine-v2.json", "delay_seconds": 120, "wait_seconds": 360,
        }
        return SimpleNamespace(**{**values, **changes})


def dev_case():
    return {
        "id": "v2-dev-unit", "split": "dev", "query": "Synthetic question",
        "ground_truth": "Synthetic answer", "expected_behavior": "Use the actual tool result.",
    }


def native_job(*, warnings=None, reflection=True):
    return {
        "id": "opt_unit", "status": "succeeded", "created_at": datetime.now(timezone.utc).timestamp(),
        "warnings": warnings or [],
        "result": {
            "baseline": "cand_baseline", "best": "cand_baseline",
            "candidates": [{
                "candidate_id": "cand_baseline", "name": "baseline", "avg_score": 0.8,
                "eval_id": "eval_unit", "eval_run_id": "evalrun_unit",
            }],
            "token_usage": [{"layer": "reflection", "total_tokens": 50}] if reflection else [],
        },
    }


def native_evaluation(**changes):
    return {
        "candidate_id": "cand_baseline", "status": "completed", "error": None,
        "result_counts": {"total": 20, "passed": 16, "failed": 4, "errored": 0},
        **changes,
    }


class OptimizerInputTests(OperationalFiles):
    def test_payload_loads_dev_directly_with_current_wire_contract(self):
        with patch.object(optimizer_lab, "load_cases", return_value=[dev_case()]) as load:
            request = optimizer_lab.payload("agent", "2", "judge", "reflection", "automated-v2")
        load.assert_called_once_with("automated-v2", split="dev")
        inputs = request["inputs"]
        self.assertNotIn("validation_dataset", inputs)
        self.assertNotIn("dataset_items", inputs["train_dataset"])
        self.assertEqual(len(inputs["train_dataset"]["items"]), 1)
        self.assertIsInstance(inputs["options"]["optimization_config"]["system_prompt"], str)
        self.assertEqual(inputs["options"]["max_candidates"], 2)
        self.assertEqual(inputs["options"]["max_stalls"], 1)

    def test_payload_default_tracks_the_current_suite(self):
        with patch.object(optimizer_lab, "load_cases", return_value=[dev_case()]) as load:
            optimizer_lab.payload("agent", "2", "judge", "reflection")
        load.assert_called_once_with(optimizer_lab.DEFAULT_SUITE, split="dev")

    def test_cli_default_tracks_the_current_suite(self):
        output = io.StringIO()
        with patch.object(sys, "argv", [
            "optimizer_lab.py", "--agent", "agent", "--version", "2", "--optimizer-deployment", "reflection",
        ]), patch.object(optimizer_lab, "load_cases", return_value=[dev_case()]) as load, \
                patch.object(optimizer_lab, "project_client") as client, contextlib.redirect_stdout(output):
            optimizer_lab.main()
        load.assert_called_once_with(optimizer_lab.DEFAULT_SUITE, split="dev")
        client.assert_not_called()
        self.assertEqual(json.loads(output.getvalue())["suite"], optimizer_lab.DEFAULT_SUITE)
        self.assertEqual(json.loads(output.getvalue())["max_seconds"], 600)

    def test_cli_exposes_explicit_bounded_budget(self):
        output = io.StringIO()
        with patch.object(sys, "argv", [
            "optimizer_lab.py", "--agent", "agent", "--version", "2", "--optimizer-deployment", "reflection",
            "--max-seconds", "1200",
        ]), patch.object(optimizer_lab, "load_cases", return_value=[dev_case()]), contextlib.redirect_stdout(output):
            optimizer_lab.main()
        self.assertEqual(json.loads(output.getvalue())["max_seconds"], 1200)

    def test_cli_rejects_invalid_budgets_before_reading_data(self):
        for value in ("59", "1801", "1200.5"):
            with patch.object(sys, "argv", [
                "optimizer_lab.py", "--agent", "agent", "--version", "2", "--optimizer-deployment", "reflection",
                "--max-seconds", value,
            ]), patch.object(optimizer_lab, "load_cases") as load, \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                optimizer_lab.main()
            self.assertEqual(raised.exception.code, 2)
            load.assert_not_called()

    def test_selected_prompt_is_passed_without_changing_the_dev_dataset(self):
        path = optimizer_lab.DATA / "prompts/current-approved.txt"
        with patch.object(optimizer_lab, "load_cases", return_value=[dev_case()]), \
                patch.object(optimizer_lab, "prompt_text", return_value="Matching deployed instructions") as prompt:
            request = optimizer_lab.payload("agent", "3", "judge", "reflection", prompt_path=path)
        prompt.assert_called_once_with(path)
        self.assertEqual(request["inputs"]["options"]["optimization_config"]["system_prompt"], "Matching deployed instructions")

    def test_prompt_argument_cannot_open_a_dataset(self):
        with patch.object(Path, "read_text") as read, self.assertRaisesRegex(ValueError, "never a dataset"):
            optimizer_lab.prompt_text(self.directory / "holdout.jsonl")
        read.assert_not_called()

    def test_holdout_and_duplicate_rows_are_rejected(self):
        for rows in ([{**dev_case(), "split": "holdout"}], [dev_case(), dev_case()], []):
            with patch.object(optimizer_lab, "load_cases", return_value=rows), self.assertRaises(ValueError):
                optimizer_lab.dev_cases("automated-v2")
        with self.assertRaises(ValueError):
            optimizer_lab.payload("a", "1", "j", "r", cases=[{**dev_case(), "split": "holdout"}])

    def test_new_legacy_submission_is_refused_before_loading_cases(self):
        with patch.object(optimizer_lab, "RESULTS", self.directory), \
                patch.object(optimizer_lab, "read_config", return_value=(ENDPOINT, "model")), \
                patch.object(optimizer_lab, "load_cases") as load, \
                self.assertRaisesRegex(ValueError, "diagnostic-only"):
            optimizer_lab.run(self.args(suite="legacy-v1"), self.evidence)
        load.assert_not_called()

    def test_new_live_job_requires_explicit_prompt_before_loading_cases(self):
        with patch.object(optimizer_lab, "RESULTS", self.directory), \
                patch.object(optimizer_lab, "read_config", return_value=(ENDPOINT, "model")), \
                patch.object(optimizer_lab, "load_cases") as load, \
                patch.object(optimizer_lab, "project_client") as client, \
                self.assertRaisesRegex(ValueError, "require --prompt-file"):
            optimizer_lab.run(self.args(prompt_file=None), self.evidence)
        load.assert_not_called()
        client.assert_not_called()

    def test_preflight_rejects_invocations_and_unsupported_reflection(self):
        project = Mock()
        project.agents.get_version.return_value.as_dict.return_value = {
            "name": "a", "version": "2",
            "definition": {"kind": "hosted", "protocol_versions": [{"protocol": "invocations"}]},
        }
        with self.assertRaisesRegex(ValueError, "Responses"):
            optimizer_lab.preflight(project, "a", "2", "reflection", self.evidence)
        project.deployments.get.assert_not_called()
        project.agents.get_version.return_value.as_dict.return_value["definition"]["protocol_versions"] = [
            {"protocol": "responses"},
        ]
        project.deployments.get.return_value.as_dict.return_value = {"modelName": "gpt-5-mini"}
        with self.assertRaisesRegex(ValueError, "not supported"):
            optimizer_lab.preflight(project, "a", "2", "reflection", self.evidence)

    def test_preflight_requires_the_exact_sdk_agent_and_version(self):
        for name, version in (("another-agent", "2"), ("a", "3")):
            project = Mock()
            project.agents.get_version.return_value.as_dict.return_value = {
                "name": name, "version": version,
                "definition": {"kind": "hosted", "protocol_versions": [{"protocol": "responses"}]},
            }
            with self.assertRaisesRegex(ValueError, "identity/version"):
                optimizer_lab.preflight(project, "a", "2", "reflection", self.evidence)
            project.deployments.get.assert_not_called()

    def test_scope_and_receipt_mismatches_are_rejected(self):
        with patch.object(optimizer_lab, "RESULTS", self.directory):
            with self.assertRaises(ValueError):
                optimizer_lab.owned_endpoint("https://other.services.ai.azure.com/api/projects/workshop")
            optimizer_lab.write_new(self.directory / "contoso-optimizer-unit-job.json", {
                "job_id": "opt_unit", "endpoint": ENDPOINT, "agent": "a", "version": "2",
            })
            with self.assertRaises(ValueError):
                optimizer_lab.recorded_job("opt_unit", ENDPOINT, "a", "3")
            with self.assertRaises(ValueError):
                optimizer_lab.recorded_job("opt_missing", ENDPOINT, "a", "2")

    def test_receipts_are_exclusive(self):
        path = self.directory / "receipt.json"
        optimizer_lab.write_new(path, {"original": True})
        with self.assertRaises(FileExistsError):
            optimizer_lab.write_new(path, {"original": False})
        self.assertTrue(json.loads(path.read_text())["original"])


class OptimizerProbeTests(OperationalFiles):
    def setup_probe(self, *, owned=True):
        self.environment.update({"tenant": "tenant", "oidc": {"principal_id": "ci-principal", "client_id": "ci-client"}})
        (self.directory / "azure-environment.json").write_text(json.dumps(self.environment))
        claims = {
            "oid": "ci-principal" if owned else "other-principal", "appid": "ci-client",
            "tid": "tenant", "aud": "https://ai.azure.com", "idtyp": "app", "nonce": "not-for-evidence",
        }
        encoded = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
        credential = Mock()
        credential.get_token.return_value = SimpleNamespace(token=f"unit.{encoded}.unit")
        response = SimpleNamespace(
            id="chatcmpl_unit", model="gpt-5.1-test", usage={"total_tokens": 20},
            choices=[SimpleNamespace(finish_reason="stop", message=SimpleNamespace(content="OK"))],
        )
        raw = SimpleNamespace(
            status_code=200, headers={"x-request-id": "request-unit", "apim-request-id": "apim-unit"},
            parse=Mock(return_value=response),
        )
        client = Mock()
        client.chat.completions.with_raw_response.create.return_value = raw
        project = Mock()
        project.deployments.get.return_value.as_dict.return_value = {"modelName": "gpt-5.1"}
        project.get_openai_client.return_value = contextlib.nullcontext(client)
        @contextlib.contextmanager
        def factory(_):
            yield project, credential, ENDPOINT, "model"
        return project, client, factory

    def test_probe_checks_identity_and_never_loads_data_or_submits_job(self):
        project, client, factory = self.setup_probe()
        with patch.object(optimizer_lab, "RESULTS", self.directory), \
                patch.object(optimizer_lab, "read_config", return_value=(ENDPOINT, "model")), \
                patch.object(optimizer_lab, "project_client", factory), \
                patch.object(optimizer_lab, "load_cases", side_effect=AssertionError("No dataset access")) as load:
            result = optimizer_lab.probe_reflection("reflection", self.evidence, require_oidc=True)
        load.assert_not_called()
        project.beta.agents.begin_create_optimization_job.assert_not_called()
        request = client.chat.completions.with_raw_response.create
        request.assert_called_once()
        self.assertEqual(request.call_args.kwargs["max_completion_tokens"], 256)
        project.get_openai_client.assert_called_once_with(timeout=45, max_retries=0)
        self.assertTrue(result["identity"]["owned_ci_principal"])
        self.assertEqual(result["optimizer_jobs_submitted"], 0)
        self.assertNotIn("token", result["identity"])
        self.assertNotIn("not-for-evidence", json.dumps(result))

    def test_wrong_oidc_principal_is_rejected_before_any_model_access(self):
        project, client, factory = self.setup_probe(owned=False)
        with patch.object(optimizer_lab, "RESULTS", self.directory), \
                patch.object(optimizer_lab, "read_config", return_value=(ENDPOINT, "model")), \
                patch.object(optimizer_lab, "project_client", factory), self.assertRaisesRegex(ValueError, "existing owned OIDC"):
            optimizer_lab.probe_reflection("reflection", self.evidence, require_oidc=True)
        project.deployments.get.assert_not_called()
        client.chat.completions.with_raw_response.create.assert_not_called()

    def test_probe_plan_requires_no_agent_and_opens_no_dataset(self):
        output = io.StringIO()
        with patch.object(sys, "argv", [
            "optimizer_lab.py", "--probe-reflection", "--optimizer-deployment", "reflection", "--require-oidc",
        ]), patch.object(optimizer_lab, "load_cases") as load, \
                patch.object(optimizer_lab, "project_client") as client, contextlib.redirect_stdout(output):
            optimizer_lab.main()
        load.assert_not_called()
        client.assert_not_called()
        plan = json.loads(output.getvalue())
        self.assertEqual(plan["model_requests"], 1)
        self.assertEqual(plan["dataset_rows_read"], 0)
        self.assertEqual(plan["optimizer_jobs_submitted"], 0)


class OptimizerOutcomeTests(unittest.TestCase):
    def test_succeeded_with_reflection_failures_is_operational_failure(self):
        job = native_job(warnings=[
            "Optimizer returned only the baseline; no optimized candidates were generated.",
            "Optimization stopped due to repeated reflection model failures (e.g., authentication failure or timeout).",
        ], reflection=False)
        report = optimizer_lab.outcome(job, [native_evaluation()], 20)
        self.assertEqual(report["outcome"], "operational_failure")
        self.assertFalse(report["quality_improvement_claimed"])
        self.assertFalse(report["human_review_completed"])
        self.assertFalse(report["promoted"])

    def test_normal_reflection_and_evaluation_without_improvement_is_not_failure(self):
        report = optimizer_lab.outcome(native_job(), [native_evaluation()], 20)
        self.assertEqual(report["outcome"], "executed_no_improvement")
        self.assertFalse(report["quality_improvement_claimed"])

    def test_baseline_only_with_no_reflection_evidence_stays_unverified(self):
        report = optimizer_lab.outcome(native_job(reflection=False), [native_evaluation()], 20)
        self.assertEqual(report["outcome"], "reflection_unverified")

    def test_evaluator_errors_missing_rows_and_skips_are_operational_failures(self):
        for counts in (
            {"total": 20, "errored": 1}, {"total": 19, "errored": 0},
            {"total": 20, "errored": 0, "skipped": 1},
        ):
            report = optimizer_lab.outcome(native_job(), [native_evaluation(result_counts=counts)], 20)
            self.assertEqual(report["outcome"], "operational_failure")
        self.assertEqual(optimizer_lab.outcome(native_job(), [], 20)["outcome"], "execution_evidence_incomplete")

    def test_full_changed_candidate_is_required(self):
        job = native_job()
        candidate = {**job["result"]["candidates"][0], "candidate_id": "cand_new", "avg_score": 0.9}
        job["result"]["candidates"].append(candidate)
        reports = [native_evaluation(), native_evaluation(candidate_id="cand_new")]
        self.assertEqual(optimizer_lab.outcome(job, reports, 20)["outcome"], "incomplete_candidate_evidence")
        candidate["mutations"] = {"system_prompt": "A real service mutation"}
        result = optimizer_lab.outcome(job, reports, 20)
        self.assertEqual(result["outcome"], "executed_candidate_available")
        self.assertEqual(result["new_candidates"], 1)
        self.assertFalse(result["promoted"])
        candidate["avg_score"] = 0.7
        self.assertEqual(optimizer_lab.outcome(job, reports, 20)["outcome"], "executed_no_improvement")

    def test_invalid_scores_do_not_claim_execution_quality(self):
        for score in (True, float("nan"), float("inf"), -1, 2):
            job = native_job()
            job["result"]["candidates"][0]["avg_score"] = score
            self.assertEqual(
                optimizer_lab.outcome(job, [native_evaluation()], 20)["outcome"],
                "execution_evidence_incomplete",
            )


class OptimizerLifecycleTests(OperationalFiles):
    def test_budget_bounds_and_legacy_receipt_default(self):
        for value in (60, 600, 1200, 1800):
            self.assertEqual(optimizer_lab.time_limit(value), value)
        for value in (59, 1801, True, 1200.5, "1200", None):
            with self.assertRaises(ValueError):
                optimizer_lab.time_limit(value)
        self.assertEqual(optimizer_lab.time_limit(600, {}), 600)
        with self.assertRaisesRegex(ValueError, "Recorded job budget is 600s"):
            optimizer_lab.time_limit(1200, {})

    def test_resume_rejects_budget_changes_before_cloud_access(self):
        optimizer_lab.write_new(self.directory / "contoso-optimizer-budget-job.json", {
            "job_id": "opt_unit", "endpoint": ENDPOINT, "agent": "contoso-agent", "version": "2",
            "max_seconds": 1200,
        })
        for value in (600, 1800):
            with patch.object(optimizer_lab, "RESULTS", self.directory), \
                    patch.object(optimizer_lab, "read_config", return_value=(ENDPOINT, "model")), \
                    patch.object(optimizer_lab, "load_cases") as load, \
                    patch.object(optimizer_lab, "project_client") as client, \
                    self.assertRaisesRegex(ValueError, "resume with --max-seconds 1200"):
                optimizer_lab.run(self.args(resume="opt_unit", max_seconds=value), self.evidence)
            load.assert_not_called()
            client.assert_not_called()

    def test_context_guard_retains_redacted_cli_reason_not_agent_secrets(self):
        output = json.dumps({"name": "a", "definition": {"environment_variables": {"API_KEY": "do-not-log"}}})
        result = SimpleNamespace(returncode=1, stdout=output,
                                 stderr="ERROR: azure.ai.projects context failed; Bearer unit-secret")
        with patch.object(optimizer_lab.subprocess, "run", return_value=result), \
                self.assertRaisesRegex(RuntimeError, "azd exit 1:.*azure.ai.projects") as raised:
            optimizer_lab.verify_session_context("a", ENDPOINT, self.evidence)
        event, diagnostic = self.evidence.append.call_args.args
        self.assertEqual(event, "session_management_probe")
        self.assertEqual(diagnostic["returncode"], 1)
        self.assertIn("azure.ai.projects", diagnostic["stderr"])
        self.assertNotIn("unit-secret", str(raised.exception))
        self.assertNotIn("do-not-log", json.dumps(diagnostic))

    def test_context_guard_accepts_only_the_exact_named_env_value(self):
        with patch.object(optimizer_lab.subprocess, "run", return_value=SimpleNamespace(
            returncode=0, stdout=ENDPOINT + "\n", stderr="",
        )) as cli:
            optimizer_lab.verify_session_context("a", ENDPOINT, self.evidence)
        self.assertEqual(cli.call_args.args[0], [
            "azd", "env", "get-value", "AZURE_AI_PROJECT_ENDPOINT", "--no-prompt",
        ])
        self.assertEqual(self.evidence.append.call_args.args[1]["endpoint"], ENDPOINT)

    def test_context_guard_rejects_unresolved_or_malformed_values(self):
        for value in ("", "not an endpoint", json.dumps({"endpoint": ENDPOINT})):
            with patch.object(optimizer_lab.subprocess, "run", return_value=SimpleNamespace(
                returncode=0, stdout=value, stderr="",
            )), self.assertRaisesRegex(ValueError, "unresolved or does not match"):
                optimizer_lab.verify_session_context("a", ENDPOINT, self.evidence)
            self.assertFalse(self.evidence.append.call_args.args[1]["matches_owned_endpoint"])

    def test_context_guard_still_rejects_another_project(self):
        with patch.object(optimizer_lab.subprocess, "run", return_value=SimpleNamespace(
            returncode=0, stdout="https://other.services.ai.azure.com/api/projects/other\n", stderr="",
        )), self.assertRaisesRegex(ValueError, "does not match the owned target"):
            optimizer_lab.verify_session_context("a", ENDPOINT, self.evidence)

    def test_monitor_uses_explicit_get_and_finishes(self):
        operations = Mock()
        job = native_job()
        operations.get_optimization_job.side_effect = [{**job, "status": "in_progress"}, job]
        with patch.object(optimizer_lab.time, "sleep"):
            actual = optimizer_lab.monitor(operations, "opt_unit", self.evidence)
        self.assertEqual(actual["status"], "succeeded")
        self.assertEqual(operations.get_optimization_job.call_count, 2)
        self.assertIn("read_timeout", operations.get_optimization_job.call_args.kwargs)

    def test_old_active_job_is_not_given_another_ten_minutes(self):
        operations = Mock()
        operations.get_optimization_job.return_value = {
            **native_job(), "status": "in_progress", "created_at": 1,
        }
        with self.assertRaises(TimeoutError):
            optimizer_lab.monitor(operations, "opt_unit", self.evidence)
        self.assertEqual(operations.get_optimization_job.call_count, 1)

    def test_extended_budget_can_poll_beyond_the_old_sixty_poll_limit(self):
        operations = Mock()
        job = native_job()
        operations.get_optimization_job.side_effect = [{**job, "status": "in_progress"}] * 65 + [job]
        clock = {"now": 0.0}
        def sleep(seconds):
            clock["now"] += seconds
        with patch.object(optimizer_lab.time, "monotonic", side_effect=lambda: clock["now"]), \
                patch.object(optimizer_lab.time, "sleep", side_effect=sleep):
            actual = optimizer_lab.monitor(operations, "opt_unit", self.evidence, max_seconds=1200)
        self.assertEqual(actual["status"], "succeeded")
        self.assertEqual(operations.get_optimization_job.call_count, 66)
        self.assertEqual(clock["now"], 650)

    def test_expired_extended_budget_does_not_restart_on_resume(self):
        operations = Mock()
        operations.get_optimization_job.return_value = {
            **native_job(), "status": "in_progress",
            "created_at": datetime.now(timezone.utc).timestamp() - 1201,
        }
        with patch.object(optimizer_lab.time, "sleep") as sleep, self.assertRaisesRegex(TimeoutError, "1200-second"):
            optimizer_lab.monitor(operations, "opt_unit", self.evidence, max_seconds=1200)
        operations.get_optimization_job.assert_called_once()
        sleep.assert_not_called()

    def test_cancellation_requires_terminal_readback(self):
        operations = Mock()
        operations.get_optimization_job.return_value = {"status": "in_progress"}
        with patch.object(optimizer_lab.time, "sleep"), self.assertRaisesRegex(RuntimeError, "not confirmed"):
            optimizer_lab.cancel_verified(operations, "opt_unit", self.evidence)
        self.assertEqual(operations.get_optimization_job.call_count, 6)
        operations.get_optimization_job.return_value = {"status": "cancelled"}
        self.assertEqual(optimizer_lab.cancel_verified(operations, "opt_unit", self.evidence)["status"], "cancelled")

    def test_poll_failure_cancels_new_job_and_stops_only_owned_new_sessions(self):
        project = Mock()
        project.beta.agents.begin_create_optimization_job.return_value.details = {"job_id": "opt_unit"}
        @contextlib.contextmanager
        def client(_):
            yield project, None, ENDPOINT, None
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(optimizer_lab, "RESULTS", self.directory))
            stack.enter_context(patch.object(optimizer_lab, "read_config", return_value=(ENDPOINT, "model")))
            stack.enter_context(patch.object(optimizer_lab, "config_values", return_value={"FOUNDRY_JUDGE_DEPLOYMENT_NAME": "judge"}))
            load = stack.enter_context(patch.object(optimizer_lab, "load_cases", return_value=[dev_case()]))
            stack.enter_context(patch.object(optimizer_lab, "project_client", client))
            stack.enter_context(patch.object(optimizer_lab, "preflight"))
            stack.enter_context(patch.object(optimizer_lab, "verify_session_context"))
            stack.enter_context(patch.object(optimizer_lab, "sessions", return_value=[{"agent_session_id": "prior"}]))
            monitor = stack.enter_context(patch.object(optimizer_lab, "monitor", side_effect=OSError("lost polling transport")))
            cancelled = {**native_job(), "status": "cancelled", "updated_at": datetime.now(timezone.utc).timestamp()}
            cancel = stack.enter_context(patch.object(optimizer_lab, "cancel_verified", return_value=cancelled))
            stop = stack.enter_context(patch.object(optimizer_lab, "reconcile_sessions"))
            with self.assertRaises(OSError):
                optimizer_lab.run(self.args(max_seconds=1200), self.evidence)
        load.assert_called_once_with("automated-v2", split="dev")
        create = project.beta.agents.begin_create_optimization_job
        create.assert_called_once()
        self.assertIs(create.call_args.kwargs["polling"], False)
        monitor.assert_called_once_with(project.beta.agents, "opt_unit", self.evidence, max_seconds=1200)
        cancel.assert_called_once_with(project.beta.agents, "opt_unit", self.evidence, max_seconds=1200)
        stop.assert_called_once()
        self.assertEqual(stop.call_args.args, (project, "contoso-agent", "2", {"prior"}, "opt_unit", cancelled, self.evidence))
        self.assertEqual(json.loads((self.directory / "contoso-optimizer-unit-terminal.json").read_text())["status"], "cancelled")
        outcome = json.loads((self.directory / "contoso-optimizer-unit-outcome.json").read_text())
        self.assertEqual(outcome["failure"]["type"], "OSError")
        self.assertFalse(outcome["quality_improvement_claimed"])
        receipt = json.loads((self.directory / "contoso-optimizer-unit-job.json").read_text())
        self.assertEqual(receipt["dev_items"], 1)
        self.assertEqual(receipt["max_seconds"], 1200)

    def test_resume_does_not_load_or_resubmit_any_dataset(self):
        optimizer_lab.write_new(self.directory / "contoso-optimizer-old-job.json", {
            "job_id": "opt_unit", "endpoint": ENDPOINT, "agent": "contoso-agent", "version": "2",
            "suite": "legacy-v1", "dev_items": 10, "max_seconds": 1200,
        })
        project = Mock()
        @contextlib.contextmanager
        def client(_):
            yield project, None, ENDPOINT, None
        with patch.object(optimizer_lab, "RESULTS", self.directory), \
                patch.object(optimizer_lab, "read_config", return_value=(ENDPOINT, "model")), \
                patch.object(optimizer_lab, "config_values", return_value={"FOUNDRY_JUDGE_DEPLOYMENT_NAME": "judge"}), \
                patch.object(optimizer_lab, "project_client", client), \
                patch.object(optimizer_lab, "load_cases", side_effect=AssertionError("dataset must stay closed")) as load, \
                patch.object(optimizer_lab, "monitor", return_value=native_job(reflection=False)) as monitor, \
                patch.object(optimizer_lab, "evaluation_evidence", return_value=[]):
            report = optimizer_lab.run(self.args(resume="opt_unit", max_seconds=1200), self.evidence)
        load.assert_not_called()
        project.beta.agents.begin_create_optimization_job.assert_not_called()
        self.assertEqual(report["suite"], "legacy-v1")
        self.assertTrue(report["diagnostic_only"])
        self.assertEqual(report["max_seconds"], 1200)
        monitor.assert_called_once_with(project.beta.agents, "opt_unit", self.evidence, max_seconds=1200)

    def test_cleanup_does_not_stop_prior_or_other_version_sessions(self):
        def row(name, version):
            return {"agent_session_id": name, "version_indicator": {"agent_version": version}}
        rows = [row("prior", "2"), row("other", "3"), row("owned-new", "2")]
        with patch.object(optimizer_lab, "sessions", return_value=rows), \
                patch.object(optimizer_lab, "session_command", side_effect=[
                    row("other", "3"), row("owned-new", "2"), None,
                    {"agent_session_id": "owned-new", "status": "idle"},
                ]) as cli:
            optimizer_lab.stop_new_sessions("a", "2", {"prior"}, "opt_unit", self.evidence)
        self.assertEqual(cli.call_count, 4)
        self.assertEqual(cli.call_args_list[2].args[2:], ("stop", "owned-new"))

    def test_cleanup_discovers_native_session_hidden_from_cli_listing(self):
        job = {"created_at": 100, "updated_at": 200}
        original = {
            "agent_session_id": "s-native", "version_indicator": {"agent_version": "2"}, "created_at": 150,
        }
        with patch.object(optimizer_lab, "sessions", return_value=[]), \
                patch.object(optimizer_lab, "job_session_ids", return_value={"s-native"}), \
                patch.object(optimizer_lab, "session_command", side_effect=[
                    original, None, {"agent_session_id": "s-native", "status": "idle"},
                ]) as cli:
            optimizer_lab.stop_new_sessions("a", "2", set(), "opt_unit", self.evidence, environment=self.environment, job=job)
        self.assertEqual(cli.call_args_list[1].args[2:], ("stop", "s-native"))
        proof = next(call.args[1] for call in self.evidence.append.call_args_list if call.args[0] == "optimizer_session_stopped")
        self.assertTrue(proof["stop_acknowledged"])
        self.assertFalse(proof["stopped_at_visible"])

    def test_cleanup_tries_other_sessions_even_after_one_stop_fails(self):
        def row(name):
            return {"agent_session_id": name, "version_indicator": {"agent_version": "2"}}
        with patch.object(optimizer_lab, "sessions", return_value=[row("s-a"), row("s-b")]), \
                patch.object(optimizer_lab, "session_command", side_effect=[
                    row("s-a"), RuntimeError("stop denied"), row("s-b"), None,
                    {"agent_session_id": "s-b", "status": "idle"},
                ]) as cli, self.assertRaisesRegex(RuntimeError, "cleanup is incomplete"):
            optimizer_lab.stop_new_sessions("a", "2", set(), "opt_unit", self.evidence)
        self.assertEqual(cli.call_args_list[-1].args[2:], ("show", "s-b"))

    def test_trace_cleanup_preserves_session_created_before_job(self):
        with patch.object(optimizer_lab, "sessions", return_value=[]), \
                patch.object(optimizer_lab, "job_session_ids", return_value={"s-prior"}), \
                patch.object(optimizer_lab, "session_command", return_value={
                    "agent_session_id": "s-prior", "version_indicator": {"agent_version": "2"}, "created_at": 50,
                }) as cli:
            optimizer_lab.stop_new_sessions("a", "2", set(), "opt_unit", self.evidence,
                                           environment=self.environment, job={"created_at": 100, "updated_at": 200})
        cli.assert_called_once()

    def test_session_trace_query_is_scoped_and_contains_no_dataset_content(self):
        environment = {**self.environment, "monitoring": {
            "appId": {"value": "owned-app"},
            "appInsightsId": {"value": self.environment["resource_group_id"] + "/providers/Microsoft.Insights/components/app"},
        }}
        response = {"tables": [{"columns": [{"name": "sessionId"}], "rows": [["s-native"]]}]}
        with patch.object(optimizer_lab.subprocess, "run", return_value=SimpleNamespace(
            returncode=0, stdout=json.dumps(response), stderr="",
        )) as cli, contextlib.redirect_stdout(io.StringIO()):
            found = optimizer_lab.job_session_ids(environment, "agent", "2", {"created_at": 100, "updated_at": 200}, self.evidence)
        self.assertEqual(found, {"s-native"})
        command = cli.call_args.args[0]
        self.assertIn("owned-subscription", command)
        query = command[command.index("--analytics-query") + 1]
        self.assertIn('gen_ai.agent.version', query)
        self.assertNotIn("gen_ai.input.messages", query)
        self.assertNotIn("gen_ai.output.messages", query)

    def test_missing_native_session_telemetry_is_not_all_stopped(self):
        environment = {**self.environment, "monitoring": {
            "appId": {"value": "owned-app"},
            "appInsightsId": {"value": self.environment["resource_group_id"] + "/providers/Microsoft.Insights/components/app"},
        }}
        job = {"created_at": 100, "updated_at": 200, "result": {"latency_usage": [{"layer": "agent", "call_count": 2}]}}
        with patch.object(optimizer_lab.subprocess, "run", return_value=SimpleNamespace(
            returncode=0, stdout='{"tables":[]}', stderr="",
        )), contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(RuntimeError, "unverified"):
            optimizer_lab.job_session_ids(environment, "a", "2", job, self.evidence)

    def test_foreign_monitoring_resource_is_rejected_before_a_query(self):
        environment = {**self.environment, "monitoring": {
            "appId": {"value": "foreign-app"},
            "appInsightsId": {"value": "/subscriptions/other/resourceGroups/other/providers/Microsoft.Insights/components/app"},
        }}
        with patch.object(optimizer_lab.subprocess, "run") as cli, self.assertRaises(ValueError):
            optimizer_lab.job_session_ids(environment, "a", "2", {"created_at": 100, "updated_at": 200}, self.evidence)
        cli.assert_not_called()

    def test_truncated_session_listing_is_not_a_stopped_claim(self):
        with patch.object(optimizer_lab, "session_command", return_value={"sessions": [], "next_page_token": "more"}):
            with self.assertRaises(RuntimeError):
                optimizer_lab.sessions("a", self.evidence)


def routine_state():
    return {
        "schema": "contoso-routine-v2", "name": "routine-unit", "endpoint": ENDPOINT,
        "agent": "contoso-agent", "input": "Synthetic policy summary. Marker: unit-marker",
        "marker": "unit-marker", "execution_kind": "scheduled", "verification_start": "2026-09-30T01:00:00+00:00",
    }


def routine_trace():
    return {
        "timestamp": "2026-09-30T01:00:01Z", "success": "True", "operation_Id": "unit-trace",
        "responseId": "resp_unit", "agent": "contoso-agent", "operation": "invoke_agent",
        "inputMessages": json.dumps([{"role": "user", "parts": [{"type": "text", "content": routine_state()["input"]}]}]),
        "outputMessages": json.dumps([{
            "role": "assistant", "parts": [{"type": "text", "content": "Synthetic completed summary."}],
            "finish_reason": "stop",
        }]),
    }


class RoutineEvidenceTests(unittest.TestCase):
    def test_history_supports_both_shapes_but_null_is_not_completion(self):
        self.assertEqual(routine_lab.history_rows({"value": None, "next_page_token": ""}), [])
        self.assertEqual(routine_lab.history_rows({"data": [{"id": "real"}]}), [{"id": "real"}])
        self.assertEqual(routine_lab.history_rows([{"id": "real"}]), [{"id": "real"}])
        for bad in ({}, {"data": "hidden"}, "ok"):
            with self.assertRaises(ValueError):
                routine_lab.history_rows(bad)

    def test_completed_run_requires_finished_action_and_real_response(self):
        row = {"status": "FINISHED", "phase": "completed", "response_id": "resp_unit", "dispatch_id": "dispatch_unit"}
        self.assertTrue(routine_lab.completed_run(row, dispatch_id="dispatch_unit"))
        for changes in (
            {"status": "RUNNING"}, {"phase": "failed"}, {"response_id": ""},
            {"error_status_code": 401}, {"error_message": "failure"}, {"dispatch_id": "another"},
        ):
            self.assertFalse(routine_lab.completed_run({**row, **changes}, dispatch_id="dispatch_unit"))

    def test_only_completed_correlated_action_trace_passes(self):
        report = routine_lab.completed_trace([routine_trace()], routine_state())
        self.assertEqual(report["verification"], "completed_action_trace")
        self.assertEqual(report["response_id"], "resp_unit")
        self.assertIsNone(report["routine_run_id"])
        self.assertFalse(report["human_review_completed"])

    def test_hidden_partial_failed_wrong_target_and_stale_traces_do_not_pass(self):
        base = routine_trace()
        for changes in (
            {"success": False}, {"success": 1}, {"responseId": ""}, {"operation_Id": ""},
            {"agent": "another-agent"}, {"operation": "chat"}, {"inputMessages": "hidden"},
            {"outputMessages": "hidden"}, {"timestamp": "2026-09-29T01:00:00Z"},
            {"timestamp": "2026-09-30T02:00:00Z"},
        ):
            self.assertIsNone(routine_lab.completed_trace([{**base, **changes}], routine_state()))
        for text, finish in (("[REDACTED]", "stop"), ("Partial output", "length"), ("", "stop")):
            row = copy.deepcopy(base)
            output = json.loads(row["outputMessages"])
            output[0]["parts"][0]["content"] = text
            output[0]["finish_reason"] = finish
            row["outputMessages"] = json.dumps(output)
            self.assertIsNone(routine_lab.completed_trace([row], routine_state()))


class RoutineLifecycleTests(OperationalFiles):
    def test_disable_is_verified_even_after_ambiguous_write_failure(self):
        with patch.object(routine_lab, "azd", side_effect=[
            RuntimeError("write timed out"), {"name": "r", "enabled": False},
        ]) as cli:
            routine_lab.stop_verified(ENDPOINT, "r", self.evidence)
        self.assertEqual(cli.call_args.args[2:], ("show", "r"))
        self.evidence.failure.assert_called_once()

    def test_disable_true_or_wrong_resource_does_not_pass(self):
        for status in ({"name": "r", "enabled": True}, {"name": "other", "enabled": False}):
            with patch.object(routine_lab, "azd", side_effect=[{}, status]), self.assertRaises(RuntimeError):
                routine_lab.stop_verified(ENDPOINT, "r", self.evidence)

    def test_existing_receipt_is_preserved_without_cloud_calls(self):
        args = self.args()
        args.receipt.write_text('{"original":true}')
        with patch.object(routine_lab, "RESULTS", self.directory), \
                patch.object(routine_lab, "read_config", return_value=(ENDPOINT, "model")), \
                patch.object(routine_lab, "azd") as cli, self.assertRaises(ValueError):
            routine_lab.run(args, self.evidence)
        cli.assert_not_called()
        self.assertTrue(json.loads(args.receipt.read_text())["original"])

    def test_scheduled_test_always_disables_on_failed_creation(self):
        with patch.object(routine_lab, "RESULTS", self.directory), \
                patch.object(routine_lab, "read_config", return_value=(ENDPOINT, "model")), \
                patch.object(routine_lab, "azd", side_effect=RuntimeError("ambiguous create")), \
                patch.object(routine_lab, "stop_verified") as stop, self.assertRaises(RuntimeError):
            routine_lab.run(self.args(), self.evidence)
        stop.assert_called_once()
        state = json.loads(self.args().receipt.read_text())
        self.assertEqual(state["execution_kind"], "scheduled")
        self.assertEqual(datetime.fromisoformat(state["trigger_at"]).microsecond, 0)

    def test_no_run_row_short_circuits_actual_response_verification(self):
        completed = {"status": "FINISHED", "phase": "completed", "response_id": "resp_unit"}
        with patch.object(routine_lab, "azd", return_value={"value": [completed]}), \
                patch.object(routine_lab, "query_traces", return_value=[]) as query, \
                patch.object(routine_lab.time, "monotonic", side_effect=[0, 1, 100]), \
                contextlib.redirect_stdout(io.StringIO()), self.assertRaises(RuntimeError):
            routine_lab.verify_execution(ENDPOINT, self.environment, routine_state(), self.evidence, 30)
        query.assert_called_once()

    def test_manual_dispatch_is_attempted_at_most_once_even_when_transport_fails(self):
        args = self.args(command="dispatch")
        state = {**routine_state(), "execution_kind": "manual"}
        args.receipt.write_text(json.dumps(state))
        show = {"enabled": False, "action": {"input": state["input"], "agent_name": state["agent"]}}
        with patch.object(routine_lab, "RESULTS", self.directory), \
                patch.object(routine_lab, "read_config", return_value=(ENDPOINT, "model")), \
                patch.object(routine_lab, "stop_verified") as stop, \
                patch.object(routine_lab, "azd", side_effect=[show, subprocess.TimeoutExpired("azd", 90)]) as cli:
            with self.assertRaises(subprocess.TimeoutExpired):
                routine_lab.run(args, self.evidence)
            cli.side_effect = [show]
            with self.assertRaises(FileExistsError):
                routine_lab.run(args, self.evidence)
        self.assertEqual(stop.call_count, 2)
        dispatches = [call for call in cli.call_args_list if call.args[2] == "dispatch"]
        self.assertEqual(len(dispatches), 1)

    def test_cli_timeout_preserves_partial_output_as_text(self):
        failure = subprocess.TimeoutExpired("azd", 90, output=b'{"partial":true}', stderr=b"timeout")
        with patch.object(routine_lab.subprocess, "run", side_effect=failure), self.assertRaises(subprocess.TimeoutExpired):
            routine_lab.azd(ENDPOINT, self.evidence, "show", "r")
        record = self.evidence.append.call_args.args[1]
        self.assertEqual(record["stdout"], '{"partial":true}')
        self.assertEqual(record["stderr"], "timeout")

    def test_history_timeout_does_not_extend_execution_deadline(self):
        with patch.object(routine_lab, "azd", return_value={"value": None}), \
                patch.object(routine_lab, "query_traces") as query, \
                patch.object(routine_lab.time, "monotonic", side_effect=[0, 31]), \
                contextlib.redirect_stdout(io.StringIO()), self.assertRaises(RuntimeError):
            routine_lab.verify_execution(ENDPOINT, self.environment, routine_state(), self.evidence, 30)
        query.assert_not_called()


if __name__ == "__main__":
    unittest.main()
