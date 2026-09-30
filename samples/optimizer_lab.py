"""Bounded native Agent Optimizer job on dev only. Never auto-promotes a candidate."""

from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import signal
import subprocess
import time
from uuid import uuid4

from cloud import project_client
from evidence import Evidence, digest, redacted, serializable
from evaluation_data import DEFAULT_SUITE, SUITES, load_cases
from workshop import DATA, RESULTS, config_values, read_config

TERMINAL = {"succeeded", "failed", "cancelled"}
REFLECTION_MODELS = {
    "gpt-5", "gpt-5.1", "gpt-5.2", "gpt-5.4", "gpt-5.5", "deepseek-v4-pro", "deepseek-v-3.2",
}


def dev_cases(suite: str) -> list[dict]:
    # Do not load all splits and filter afterwards: the v2 holdout is sealed.
    cases = load_cases(suite, split="dev")
    if not cases or any(case.get("split") != "dev" for case in cases):
        raise ValueError("Optimizer accepts a nonempty dev split only.")
    if len({case["id"] for case in cases}) != len(cases):
        raise ValueError("Duplicate optimizer dev IDs.")
    return cases


def prompt_text(path: Path | None = None) -> str:
    path = (path or DATA / "prompts/agent-v4.txt").resolve()
    if path.parent != (DATA / "prompts").resolve() or path.suffix != ".txt":
        raise ValueError("Optimizer prompts must be .txt instructions inside data/prompts, never a dataset.")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("Optimizer system prompt cannot be empty.")
    return text


def payload(agent: str, version: str, judge: str, optimizer: str,
            suite: str = DEFAULT_SUITE, *, cases: list[dict] | None = None,
            prompt_path: Path | None = None) -> dict:
    dev = dev_cases(suite) if cases is None else cases
    if not dev or any(case.get("split") != "dev" for case in dev):
        raise ValueError("Holdout rows cannot enter an optimization request.")
    return {"inputs": {
        "agent": {"agent_name": agent, "agent_version": version},
        "train_dataset": {"type": "inline", "items": [{
            "query": case["query"], "ground_truth": case["ground_truth"],
            "criteria": [{"name": case["id"], "instruction": case["expected_behavior"]}],
        } for case in dev]},
        "evaluators": [{"name": "builtin.task_adherence"}],
        "options": {"max_candidates": 2, "max_stalls": 1, "eval_model": judge,
                    "optimization_model": optimizer,
                    "optimization_config": {"system_prompt": prompt_text(prompt_path)}},
    }}


def write_new(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def owned_endpoint(endpoint: str) -> dict:
    state = json.loads((RESULTS / "azure-environment.json").read_text(encoding="utf-8"))
    expected = f"https://{state['account_name']}.services.ai.azure.com/api/projects/{state['project_name']}"
    if endpoint != state.get("project_endpoint") or endpoint != expected:
        raise ValueError("Optimizer endpoint does not match the owned environment ledger.")
    return state


def principal_info(credential, environment: dict) -> dict:
    token = credential.get_token("https://ai.azure.com/.default")
    try:
        encoded = token.token.split(".")[1]
        claims = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
        if not isinstance(claims, dict):
            raise ValueError("Invalid claim object.")
    except (ValueError, IndexError, UnicodeDecodeError):
        raise ValueError("Cannot extract safe principal metadata from the credential.") from None
    identity = {
        "principal_id": claims.get("oid"), "tenant_id": claims.get("tid"),
        "application_id": claims.get("appid") or claims.get("azp"),
        "identity_type": claims.get("idtyp"), "audience": claims.get("aud"),
    }
    expected = environment.get("oidc") or {}
    identity["owned_ci_principal"] = bool(expected.get("principal_id") and expected.get("client_id")) and (
        identity["principal_id"] == expected["principal_id"]
        and identity["application_id"] == expected["client_id"]
        and identity["tenant_id"] == environment["tenant"]
    )
    return identity


def check_principal(credential, environment: dict, evidence: Evidence, *, require_oidc: bool) -> dict:
    identity = principal_info(credential, environment)
    evidence.append("caller_identity", identity)
    if require_oidc and not identity["owned_ci_principal"]:
        raise ValueError("Caller is not the existing owned OIDC principal; no model call or optimizer job submitted.")
    return identity


def probe_reflection(deployment_name: str, evidence: Evidence, *, require_oidc: bool = False) -> dict:
    endpoint, _ = read_config()
    environment = owned_endpoint(endpoint)
    with project_client(evidence) as (project, credential, actual_endpoint, _):
        if actual_endpoint != endpoint:
            raise ValueError("Reflection probe project changed after ownership validation.")
        identity = check_principal(credential, environment, evidence, require_oidc=require_oidc)
        deployment = project.deployments.get(deployment_name).as_dict()
        model = deployment.get("modelName", "").lower()
        if model not in REFLECTION_MODELS:
            raise ValueError("Probe requires a supported native reflection deployment.")
        parameters = {
            "model": deployment_name,
            "messages": [{"role": "user", "content": "For a bounded connectivity check, reply with OK only."}],
            "max_completion_tokens": 256,
        }
        if model.startswith("gpt-5"):
            parameters["reasoning_effort"] = "low"
        started = time.monotonic()
        with project.get_openai_client(timeout=45, max_retries=0) as client:
            raw = client.chat.completions.with_raw_response.create(**parameters)
            response = raw.parse()
            choice = response.choices[0] if response.choices else None
            completed = bool(choice and choice.finish_reason == "stop" and choice.message.content)
            summary = {
                "operation": "reflection_probe", "project_endpoint": endpoint, "identity": identity,
                "deployment": deployment_name, "model": response.model, "http_status": raw.status_code,
                "request_id": raw.headers.get("x-request-id"), "apim_request_id": raw.headers.get("apim-request-id"),
                "response_id": response.id, "finish_reason": choice.finish_reason if choice else None,
                "elapsed_seconds": round(time.monotonic() - started, 3), "usage": serializable(response.usage),
                "completed": completed, "max_completion_tokens": 256, "model_timeout_seconds": 45,
                "model_requests": 1, "optimizer_jobs_submitted": 0, "dataset_rows_read": 0,
                "holdout_submitted": False, "quality_improvement_claimed": False, "human_review_completed": False,
            }
            evidence.append("reflection_probe", summary)
            write_new(RESULTS / (evidence.run_id + "-probe.json"), summary)
            if raw.status_code != 200 or not completed:
                raise RuntimeError("Reflection probe did not produce a completed model response.")
            return summary


def recorded_job(job_id: str, endpoint: str, agent: str, version: str) -> dict:
    for path in RESULTS.glob("contoso-optimizer-*-job.json"):
        row = json.loads(path.read_text(encoding="utf-8"))
        if row.get("job_id") != job_id:
            continue
        if row.get("endpoint", endpoint) != endpoint:
            raise ValueError("Recorded optimizer job belongs to another project.")
        target = {"agent_name": row.get("agent"), "agent_version": row.get("version")}
        if not all(target.values()):
            # Legacy receipts lacked a target; use their original submission, not today's dataset.
            source = path.with_name(path.name.removesuffix("-job.json") + ".jsonl")
            for line in source.read_text(encoding="utf-8").splitlines():
                event = json.loads(line)
                if event.get("event") == "submitted_config":
                    target = event["payload"]["payload"]["inputs"]["agent"]
        if target != {"agent_name": agent, "agent_version": version}:
            raise ValueError("Recorded optimizer job does not match the selected target version.")
        return row
    raise ValueError("Unknown job: monitoring/cancellation is limited to recorded runs.")


def preflight(project, agent: str, version: str, optimizer: str, evidence: Evidence) -> None:
    target = project.agents.get_version(agent, version).as_dict()
    if target.get("name") != agent or str(target.get("version")) != version:
        raise ValueError("SDK agent identity/version does not match the requested owned target.")
    definition = target.get("definition", {})
    protocols = definition.get("protocol_versions", definition.get("container_protocol_versions", []))
    if definition.get("kind") != "hosted" or not any(p.get("protocol") == "responses" for p in protocols):
        raise ValueError("Native hosted optimization requires a Responses-protocol agent version.")
    deployment = project.deployments.get(optimizer).as_dict()
    evidence.append("preflight", {
        "agent": agent, "version": version, "protocols": protocols,
        "reflection_deployment": deployment,
    })
    if deployment.get("modelName", "").lower() not in REFLECTION_MODELS:
        raise ValueError("Deployment is not an allowed reflection model; gpt-5-mini is not supported.")


def session_command(agent: str, evidence: Evidence, *args: str, json_output: bool = True):
    command = ["azd", "ai", "agent", "sessions", *args, "--agent-name", agent, "--no-prompt"]
    if json_output:
        command += ["--output", "json"]
    result = subprocess.run(command, text=True, capture_output=True, timeout=90, check=False)
    evidence.append("optimizer_session_cli", {
        "operation": list(args), "agent": agent, "returncode": result.returncode,
        "stdout": result.stdout, "stderr": result.stderr,
    })
    if result.returncode:
        raise RuntimeError("Optimizer session operation failed; stop state is not confirmed.")
    return json.loads(result.stdout) if json_output else None


def verify_session_context(agent: str, endpoint: str, evidence: Evidence) -> None:
    command = ["azd", "env", "get-value", "AZURE_AI_PROJECT_ENDPOINT", "--no-prompt"]
    result = subprocess.run(
        command, text=True, capture_output=True, timeout=90, check=False,
    )
    actual = result.stdout.strip()
    matches = bool(actual) and actual == endpoint
    diagnostic = {
        "command": command, "expected_project_endpoint": endpoint, "returncode": result.returncode,
        "stderr": redacted(result.stderr), "stdout_digest": digest(result.stdout),
        "stdout_length": len(result.stdout), "value_present": bool(actual),
        "matches_owned_endpoint": matches, "resolved_project_endpoint": actual if matches else None,
    }
    # Read only the named endpoint, without an agent-status command or a fallback to another context.
    evidence.append("session_management_probe", diagnostic)
    if result.returncode:
        detail = diagnostic["stderr"].strip()[:1600] or "No stderr; inspect the recorded context probe."
        raise RuntimeError(
            f"Cannot confirm the azd session-management project; no optimizer job submitted. "
            f"azd exit {result.returncode}: {detail}"
        )
    if not matches:
        raise ValueError("azd AZURE_AI_PROJECT_ENDPOINT is unresolved or does not match the owned target project.")
    evidence.append("session_management_scope", {
        "agent": agent, "endpoint": actual, "source": "azd env get-value AZURE_AI_PROJECT_ENDPOINT",
    })


def sessions(agent: str, evidence: Evidence) -> list[dict]:
    page = session_command(agent, evidence, "list", "--limit", "100")
    if isinstance(page, list):
        return page
    if any(page.get(key) for key in (
        "continuation_token", "next_page_token", "pagination_token", "next_link", "nextLink",
    )):
        raise RuntimeError("Session listing is truncated; do not assume all optimizer compute is stopped.")
    rows = page.get("sessions", page.get("value", page.get("data")))
    if not isinstance(rows, list):
        raise ValueError("Unrecognized hosted-session list response.")
    return rows


def job_session_ids(environment: dict, agent: str, version: str, job: dict, evidence: Evidence) -> set[str]:
    monitoring = environment.get("monitoring", {})
    app_id = monitoring.get("appId", {}).get("value")
    resource_id = monitoring.get("appInsightsId", {}).get("value", "")
    if not app_id or not resource_id.lower().startswith(environment["resource_group_id"].lower() + "/"):
        raise ValueError("Owned App Insights is required to discover native sessions omitted by azd list.")
    start = datetime.fromtimestamp(job["created_at"], timezone.utc)
    end = datetime.fromtimestamp(job["updated_at"], timezone.utc)
    query = f"""traces
| where timestamp between (datetime({start.isoformat()}) .. datetime({end.isoformat()}))
| where tostring(customDimensions["gen_ai.agent.name"]) == {json.dumps(agent)}
    and tostring(customDimensions["gen_ai.agent.version"]) == {json.dumps(version)}
| extend sessionId=tostring(customDimensions["azure.ai.agentserver.session_id"])
| where isnotempty(sessionId)
| summarize first_seen=min(timestamp), last_seen=max(timestamp) by sessionId
| take 11"""
    print(f"Owned Optimizer session query:\n```kql\n{query}\n```", flush=True)
    result = subprocess.run(
        ["az", "monitor", "app-insights", "query", "--app", app_id,
         "--subscription", environment["subscription"], "--analytics-query", query,
         "--start-time", start.isoformat(), "--end-time", end.isoformat(),
         "--output", "json", "--only-show-errors"],
        text=True, capture_output=True, timeout=90, check=False,
    )
    evidence.append("native_session_trace_discovery", {
        "app_id": app_id, "query": query, "returncode": result.returncode,
        "stdout": result.stdout, "stderr": result.stderr,
    })
    if result.returncode:
        raise RuntimeError("Native session discovery failed; azd list alone cannot confirm all compute stopped.")
    page = json.loads(result.stdout)
    if page.get("error") or not isinstance(page.get("tables"), list):
        raise ValueError("Invalid native session trace response.")
    found = set()
    for table in page["tables"]:
        columns = [column["name"] for column in table["columns"]]
        for values in table["rows"]:
            row = dict(zip(columns, values, strict=True))
            if not isinstance(row.get("sessionId"), str) or not row["sessionId"]:
                raise ValueError("Invalid session identifier in native trace.")
            found.add(row["sessionId"])
    if len(found) > 10:
        raise RuntimeError("Native session discovery exceeded the bounded cleanup limit.")
    if not found and any(
        item.get("layer") == "agent" and item.get("call_count", 0) > 0
        for item in (job.get("result") or {}).get("latency_usage", [])
    ):
        raise RuntimeError("The job invoked the agent but no session telemetry is visible; cleanup is unverified.")
    return found


def stop_new_sessions(agent: str, version: str, before: set[str], job_id: str,
                      evidence: Evidence, *, environment: dict | None = None, job: dict | None = None) -> None:
    errors = []
    found = set()
    try:
        found.update(row["agent_session_id"] for row in sessions(agent, evidence))
    except Exception as exc:
        evidence.failure(exc)
        errors.append(str(exc))
    if environment is not None:
        try:
            if not job:
                raise ValueError("No final job timestamps; native session ownership cannot be established.")
            found.update(job_session_ids(environment, agent, version, job, evidence))
        except Exception as exc:
            evidence.failure(exc)
            errors.append(str(exc))
    for session_id in sorted(found - before):
        try:
            original = session_command(agent, evidence, "show", session_id)
            indicator = original.get("version_indicator", {})
            related = indicator.get("agent_version") == version or any(
                isinstance(value, str) and value.startswith("cand_" + job_id + "_") for value in indicator.values()
            )
            if original.get("agent_session_id") != session_id or not related:
                continue
            if job and not (job["created_at"] <= original.get("created_at", 0) <= job["updated_at"]):
                evidence.append("preexisting_session_preserved", {"session_id": session_id})
                continue
            session_command(agent, evidence, "stop", session_id, json_output=False)
            for attempt in range(6):
                status = session_command(agent, evidence, "show", session_id)
                if status.get("agent_session_id") == session_id and status.get("status") in {"idle", "stopped"}:
                    break
                if attempt < 5:
                    time.sleep(2)
            if status.get("agent_session_id") != session_id or status.get("status") not in {"idle", "stopped"}:
                raise RuntimeError(f"Optimizer session {session_id} has no verified stopped state.")
            # The extension omits stopped_at; successful stop + idle readback is the supported CLI evidence.
            evidence.append("optimizer_session_stopped", {
                "session": status, "stop_acknowledged": True, "stopped_at_visible": "stopped_at" in status,
            })
        except Exception as exc:
            evidence.failure(exc)
            errors.append(f"{session_id}: {exc}")
    if errors:
        raise RuntimeError("Optimizer cleanup is incomplete: " + "; ".join(errors))


def cancel_verified(operations, job_id: str, evidence: Evidence) -> dict:
    try:
        evidence.append("cancel_requested", operations.cancel_optimization_job(job_id))
    except Exception as exc:
        evidence.failure(exc)
    for attempt in range(6):
        job = serializable(operations.get_optimization_job(job_id))
        evidence.append("cancel_status", job)
        if job.get("status") in TERMINAL:
            return job
        if attempt < 5:
            time.sleep(5)
    raise RuntimeError(f"Optimizer {job_id} cancellation is not confirmed; operations may still be active.")


def monitor(operations, job_id: str, evidence: Evidence) -> dict:
    job = serializable(operations.get_optimization_job(job_id))
    created = job.get("created_at")
    if isinstance(created, str):
        created = datetime.fromisoformat(created.replace("Z", "+00:00")).timestamp()
    if not isinstance(created, (int, float)):
        raise ValueError("Missing optimizer creation time; cannot enforce the ten-minute bound.")
    remaining = max(0, min(600, 600 - (datetime.now(timezone.utc).timestamp() - created)))
    deadline = time.monotonic() + remaining
    for _ in range(60):
        evidence.append("job_status", job)
        if job.get("status") in TERMINAL:
            return job
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(10, remaining))
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        # Explicit GET carries api-version; do not follow the service's unversioned Operation-Location.
        job = serializable(operations.get_optimization_job(
            job_id, read_timeout=min(60, remaining), connection_timeout=min(15, remaining),
        ))
    raise TimeoutError("Optimizer ten-minute limit reached; cancellation is required.")


def evaluation_evidence(client, result: dict, evidence: Evidence) -> list[dict]:
    reports = []
    candidates = result.get("candidates") or []
    if len(candidates) > 3:
        raise ValueError("Unexpected candidate count exceeds this lab's evaluation-query bound.")
    for candidate in candidates:
        if not candidate.get("eval_id") or not candidate.get("eval_run_id"):
            continue
        run = client.evals.runs.retrieve(candidate["eval_run_id"], eval_id=candidate["eval_id"])
        report = {
            "candidate_id": candidate.get("candidate_id"), "eval_id": candidate["eval_id"],
            "eval_run_id": run.id, "status": run.status,
            "result_counts": serializable(run.result_counts), "error": serializable(run.error),
        }
        if report["result_counts"].get("errored", 0):
            page = client.evals.runs.output_items.list(
                candidate["eval_run_id"], eval_id=candidate["eval_id"], limit=100,
            )
            errors = []
            for row in page.data:
                data = row.model_dump(mode="json", warnings=False)
                for metric in data.get("results", []):
                    if metric.get("status") in {"error", "errored", "failed"}:
                        errors.append({
                            "output_item_id": data.get("id"), "datasource_item_id": data.get("datasource_item_id"),
                            "evaluator": metric.get("name"), "status": metric.get("status"),
                            "error": metric.get("error"), "reason": metric.get("reason"),
                        })
            report["error_items"] = errors
            report["error_details_truncated"] = page.has_more
        evidence.append("native_evaluation_status", report)
        reports.append(report)
    return reports


def outcome(job: dict, evaluations: list[dict], expected_items: int | None) -> dict:
    result = job.get("result") or {}
    candidates = result.get("candidates") or []
    warnings = job.get("warnings") or []
    faults = [warning for warning in warnings if any(
        word in warning.lower() for word in ("failure", "failed", "timeout", "authentication", "error")
    )]
    baseline = next((c for c in candidates if c.get("candidate_id") == result.get("baseline")), None)
    changed = [c for c in candidates if c.get("candidate_id") != result.get("baseline") and c.get("mutations")]
    summary = {
        "job_id": job.get("id"), "service_status": job.get("status"),
        "completion_status": job.get("completion_status"), "warnings": warnings,
        "new_candidates": len(changed), "promoted": False, "holdout_submitted": False,
        "quality_improvement_claimed": False, "human_review_completed": False,
    }
    if job.get("status") != "succeeded" or job.get("error") or faults:
        return {**summary, "outcome": "operational_failure", "operational_faults": faults}
    if not candidates or not baseline or len(evaluations) != len(candidates):
        return {**summary, "outcome": "execution_evidence_incomplete"}
    for report in evaluations:
        counts = report.get("result_counts") or {}
        if (report.get("status") != "completed" or report.get("error") or counts.get("errored") != 0
                or counts.get("skipped", 0) != 0 or not counts.get("total")
                or (expected_items is not None and counts["total"] != expected_items)):
            return {**summary, "outcome": "operational_failure"}
    for candidate in candidates:
        score = candidate.get("avg_score")
        if type(score) not in (int, float) or not math.isfinite(score) or not 0 <= score <= 1:
            return {**summary, "outcome": "execution_evidence_incomplete"}
    reflection_observed = any(
        row.get("layer", "").lower() in {"reflection", "optimizer", "optimization"}
        and isinstance(row.get("total_tokens"), (int, float)) and row["total_tokens"] > 0
        for row in result.get("token_usage", [])
    )
    if any(c.get("candidate_id") != result.get("baseline") and not c.get("mutations") for c in candidates):
        return {**summary, "outcome": "incomplete_candidate_evidence"}
    if not changed and not reflection_observed:
        return {**summary, "outcome": "reflection_unverified"}
    improved = [c for c in changed if c["avg_score"] > baseline["avg_score"]]
    return {
        **summary, "outcome": "executed_candidate_available" if improved else "executed_no_improvement",
        "baseline_dev_score": baseline["avg_score"],
        "best_dev_score": max(c["avg_score"] for c in candidates),
        "reflection_observed": reflection_observed or bool(changed),
    }


def run(args: argparse.Namespace, evidence: Evidence) -> dict:
    endpoint, _ = read_config()
    environment = owned_endpoint(endpoint)
    receipt = recorded_job(args.resume, endpoint, args.agent, args.version) if args.resume else None
    if not args.resume and args.suite == "legacy-v1":
        raise ValueError("Legacy suites are diagnostic-only; use --resume for an existing legacy job.")
    if not args.resume and getattr(args, "prompt_file", None) is None:
        raise ValueError("New live jobs require --prompt-file matching the selected deployed Responses version.")
    cases = None if args.resume else dev_cases(args.suite)
    judge = config_values()["FOUNDRY_JUDGE_DEPLOYMENT_NAME"]
    if not args.resume and not judge:
        raise ValueError("Set an explicit judge deployment.")
    with project_client(evidence) as (project, credential, actual_endpoint, _):
        if actual_endpoint != endpoint:
            raise ValueError("Optimizer project changed after ownership validation.")
        if getattr(args, "require_oidc", False):
            check_principal(credential, environment, evidence, require_oidc=True)
        job_id = args.resume
        before = set(receipt.get("session_ids_before", [])) if receipt else None
        job = None
        cleanup_needed = False
        try:
            if not args.resume:
                preflight(project, args.agent, args.version, args.optimizer_deployment, evidence)
                verify_session_context(args.agent, endpoint, evidence)
                before = {row["agent_session_id"] for row in sessions(args.agent, evidence)}
                request = payload(
                    args.agent, args.version, judge, args.optimizer_deployment, args.suite, cases=cases,
                    prompt_path=getattr(args, "prompt_file", None),
                )
                evidence.append("submitted_config", {
                    "payload": request, "suite": args.suite, "dev_ids": [c["id"] for c in cases],
                    "dev_sha256": digest(cases), "configuration_sha256": digest(request),
                    "holdout_submitted": False, "human_review_completed": False,
                })
                operation_id = str(uuid4())
                evidence.append("submission_intent", {"operation_id": operation_id, "endpoint": endpoint})
                poller = project.beta.agents.begin_create_optimization_job(
                    job=request, operation_id=operation_id, polling=False,
                )
                job_id = poller.details["job_id"]
                cleanup_needed = True
                evidence.append("job_submitted", {"job_id": job_id, "poller_details": poller.details})
                print(json.dumps({"job_id": job_id, "max_seconds": 600, "evidence": str(evidence.path)}), flush=True)
                receipt = {
                    "job_id": job_id, "status": "submitted", "endpoint": endpoint,
                    "agent": args.agent, "version": args.version, "suite": args.suite,
                    "dev_items": len(cases), "session_ids_before": sorted(before),
                    "operation_id": operation_id, "configuration_sha256": digest(request),
                }
                write_new(RESULTS / (evidence.run_id + "-job.json"), receipt)
            else:
                cleanup_needed = True
            job = monitor(project.beta.agents, job_id, evidence)
            target = (job.get("inputs") or {}).get("agent")
            if target and (target.get("agent_name") != args.agent or target.get("agent_version") != args.version):
                raise ValueError("Service job inputs do not match the recorded target version.")
            evidence.append("terminal_job", job)
            write_new(RESULTS / (evidence.run_id + "-terminal.json"), job)
            reports = []
            if job.get("status") == "succeeded" and job.get("result"):
                try:
                    with project.get_openai_client(timeout=45, max_retries=0) as client:
                        reports = evaluation_evidence(client, job["result"], evidence)
                except Exception as exc:
                    evidence.failure(exc)
            summary = outcome(job, reports, receipt.get("dev_items"))
            summary["suite"] = receipt.get("suite", "legacy-v1")
            summary["diagnostic_only"] = bool(args.resume)
            evidence.append("optimizer_outcome", summary)
            write_new(RESULTS / (evidence.run_id + "-outcome.json"), summary)
            return summary
        except BaseException as exc:
            evidence.failure(exc)
            raise
        finally:
            try:
                if cleanup_needed and job_id and (job is None or job.get("status") not in TERMINAL):
                    job = cancel_verified(project.beta.agents, job_id, evidence)
            finally:
                if cleanup_needed and before is not None and (not args.resume or "session_ids_before" in receipt):
                    verify_session_context(args.agent, endpoint, evidence)
                    stop_new_sessions(
                        args.agent, args.version, before, job_id, evidence, environment=environment, job=job,
                    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent")
    parser.add_argument("--version")
    parser.add_argument("--optimizer-deployment", required=True)
    parser.add_argument("--suite", choices=SUITES, default=DEFAULT_SUITE)
    parser.add_argument("--prompt-file", type=Path, help="Required for new live jobs: matching baseline in data/prompts/*.txt.")
    parser.add_argument("--require-oidc", action="store_true", help="Require the existing CI identity in the ownership ledger.")
    parser.add_argument("--live", action="store_true")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--resume", help="Resume monitoring only an optimization job recorded in this checkout.")
    mode.add_argument("--probe-reflection", action="store_true", help="One bounded model call; no dataset or optimization job.")
    args = parser.parse_args()
    if not args.probe_reflection and (not args.agent or not args.version):
        parser.error("--agent and --version are required for an optimizer job.")
    if not args.live:
        if args.probe_reflection:
            print(json.dumps({
                "plan_only": True, "operation": "reflection_probe", "deployment": args.optimizer_deployment,
                "require_owned_oidc": args.require_oidc, "model_requests": 1, "max_completion_tokens": 256,
                "model_timeout_seconds": 45, "optimizer_jobs_submitted": 0, "dataset_rows_read": 0,
            }, indent=2))
            return
        cases = [] if args.resume or args.probe_reflection else dev_cases(args.suite)
        print(json.dumps({
            "plan_only": True, "suite": args.suite, "resume": args.resume,
            "reflection_probe": args.probe_reflection, "require_owned_oidc": args.require_oidc,
            "dev_items": len(cases), "holdout_items": 0, "max_candidates": 2,
            "max_stalls": 1, "max_seconds": 600, "auto_promote": False,
            "prompt_file": str(args.prompt_file or DATA / "prompts/agent-v4.txt"),
            "prompt_selection_required": args.prompt_file is None and not args.resume,
            "dev_ids": [case["id"] for case in cases],
        }, ensure_ascii=False, indent=2))
        return
    evidence = Evidence("optimizer")
    def interrupted(signum, frame):
        raise KeyboardInterrupt("Optimizer interrupted; cancelling the recorded job.")
    signal.signal(signal.SIGTERM, interrupted)
    try:
        if args.probe_reflection:
            print(json.dumps(probe_reflection(
                args.optimizer_deployment, evidence, require_oidc=args.require_oidc,
            ), ensure_ascii=False, indent=2))
            return
        summary = run(args, evidence)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        if summary["outcome"] not in {"executed_candidate_available", "executed_no_improvement"}:
            raise RuntimeError(f"Optimizer outcome: {summary['outcome']}. Original evidence retained; no promotion.")
    except Exception as exc:
        evidence.failure(exc)
        raise
    finally:
        print(f"Evidence: {evidence.path}")


if __name__ == "__main__":
    main()
