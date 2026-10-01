"""Bounded native Agent Optimizer job on dev only. Never auto-promotes a candidate."""

from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import json
from itertools import islice
import math
from pathlib import Path
import re
import signal
import subprocess
import time
from uuid import uuid4
from urllib.parse import urlparse

from cloud import project_client
from evidence import Evidence, digest, redacted, serializable
from evaluation_data import DEFAULT_SUITE, FROZEN_SUITES, SUITES, load_cases, suite_hash, verify_development_freeze
from lab_profile import active_prompt
from workshop import DATA, LANGUAGE, RESULTS, config_values, read_config

TERMINAL = {"succeeded", "failed", "cancelled"}
INACTIVE_SESSIONS = {"idle", "stopped", "expired", "deleted"}
CLEANUP_MAX_SECONDS = 180
CLEANUP_PASSES = 6
CLEANUP_INTERVAL_SECONDS = 10
MAX_CLEANUP_SESSIONS = 10
CANCELLATION_MAX_SECONDS = 90
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
    path = (path or active_prompt()).resolve()
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
    if state.get("language", "ko") != LANGUAGE:
        raise ValueError("Optimizer language does not match the owned environment ledger.")
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


def session_command(agent: str, evidence: Evidence, *args: str, json_output: bool = True, timeout_seconds: float = 90):
    command = ["azd", "ai", "agent", "sessions", *args, "--agent-name", agent, "--no-prompt"]
    if json_output:
        command += ["--output", "json"]
    result = subprocess.run(command, text=True, capture_output=True, timeout=timeout_seconds, check=False)
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


def sessions(agent: str, evidence: Evidence, *, project=None, timeout_seconds: float = 60) -> list[dict]:
    if project is not None:
        from azure.core.exceptions import AzureError
        try:
            rows = [serializable(row) for row in islice(project.agents.list_sessions(
                agent, limit=100, read_timeout=timeout_seconds, connection_timeout=min(15, timeout_seconds),
            ), 101)]
        except AzureError as exc:
            raise RuntimeError("SDK session discovery failed; cleanup is unverified.") from exc
        if len(rows) > 100:
            raise RuntimeError("SDK session discovery exceeded 100 sessions; cleanup is unverified.")
        if any(not isinstance(row, dict) or not row.get("agent_session_id") for row in rows):
            raise ValueError("Invalid SDK session identity; cleanup is unverified.")
        evidence.append("optimizer_session_sdk_list", {"agent": agent, "sessions": rows})
        return rows
    page = session_command(agent, evidence, "list", "--limit", "100", timeout_seconds=timeout_seconds)
    if isinstance(page, list):
        if len(page) >= 100:
            raise RuntimeError("CLI session listing may be truncated; cleanup is unverified.")
        return page
    if any(page.get(key) for key in (
        "continuation_token", "next_page_token", "pagination_token", "next_link", "nextLink",
    )):
        raise RuntimeError("Session listing is truncated; do not assume all optimizer compute is stopped.")
    rows = page.get("sessions", page.get("value", page.get("data")))
    if not isinstance(rows, list):
        raise ValueError("Unrecognized hosted-session list response.")
    if len(rows) >= 100:
        raise RuntimeError("CLI session listing may be truncated; cleanup is unverified.")
    return rows


def timestamp(value, label: str) -> float:
    if isinstance(value, datetime):
        value = value.timestamp()
    elif isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"Invalid {label}; session ownership/time bounds cannot be established.")
    return value


def remaining_timeout(deadline: float | None, limit: float = 60) -> float:
    remaining = limit if deadline is None else min(limit, deadline - time.monotonic())
    if remaining <= 0:
        raise TimeoutError("Optimizer cleanup budget exhausted; remaining sessions are unverified.")
    return remaining


def session_action(agent: str, session_id: str, operation: str, evidence: Evidence, *, project=None, deadline=None):
    timeout = remaining_timeout(deadline)
    if project is None:
        return session_command(
            agent, evidence, operation, session_id, json_output=operation == "show", timeout_seconds=timeout,
        )
    from azure.core.exceptions import AzureError
    try:
        method = project.agents.get_session if operation == "show" else project.agents.stop_session
        result = serializable(method(
            agent, session_id, read_timeout=timeout, connection_timeout=min(15, timeout),
        ))
    except AzureError as exc:
        raise RuntimeError(f"SDK {operation} failed for recorded session {session_id}; stop is unverified.") from exc
    evidence.append("optimizer_session_sdk_" + operation, {
        "agent": agent, "session_id": session_id, "result": result,
    })
    return result


def owned_draft_version(project, agent: str, version: str, job_id: str, endpoint: str,
                        evidence: Evidence, deadline: float) -> bool:
    from azure.core.exceptions import AzureError
    timeout = remaining_timeout(deadline)
    try:
        details = serializable(project.agents.get_version(
            agent, version, read_timeout=timeout, connection_timeout=min(15, timeout),
        ))
    except AzureError as exc:
        raise RuntimeError("Cannot verify optimizer draft-version ownership; no session was stopped.") from exc
    if details.get("name") != agent or str(details.get("version")) != version:
        raise ValueError("Optimizer draft-version identity mismatch.")
    definition = details.get("definition") or {}
    variables = definition.get("environment_variables") or {}
    candidate = variables.get("OPTIMIZATION_CANDIDATE_ID", "")
    if not isinstance(candidate, str) or not candidate.startswith("cand_opt_"):
        raise ValueError("Draft version has no verifiable optimizer job identity; cleanup remains unverified.")
    resolver = urlparse(variables.get("OPTIMIZATION_RESOLVE_ENDPOINT", ""))
    target = urlparse(endpoint)
    matches = (
        definition.get("kind") == "hosted" and isinstance(candidate, str)
        and candidate.startswith("cand_" + job_id + "_")
        and target.scheme == "https" and resolver.scheme == "https" and resolver.netloc == target.netloc
        and resolver.path.startswith(target.path.rstrip("/") + "/")
    )
    evidence.append("optimizer_draft_version_ownership", {
        "agent": agent, "version": version, "candidate_id": candidate, "matches_recorded_job_and_project": matches,
    })
    if candidate.startswith("cand_" + job_id + "_") and not matches:
        raise ValueError("Recorded job candidate has an unverified definition/resolver; no session was stopped.")
    return matches


def job_session_ids(environment: dict, agent: str, version: str, job: dict, evidence: Evidence) -> set[str]:
    monitoring = environment.get("monitoring", {})
    app_id = monitoring.get("appId", {}).get("value")
    resource_id = monitoring.get("appInsightsId", {}).get("value", "")
    if not app_id or not resource_id.lower().startswith(environment["resource_group_id"].lower() + "/"):
        raise ValueError("Owned App Insights is required to discover native sessions omitted by azd list.")
    start = datetime.fromtimestamp(timestamp(job["created_at"], "job creation time"), timezone.utc)
    end = datetime.fromtimestamp(timestamp(job["updated_at"], "job update time"), timezone.utc)
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
                      evidence: Evidence, *, environment: dict | None = None, job: dict | None = None,
                      project=None, deadline=None, verified: set[str] | None = None,
                      endpoint: str | None = None, version_ownership: dict[str, bool] | None = None,
                      allow_terminal_tail: bool = False) -> dict:
    verified = set() if verified is None else verified
    version_ownership = {} if version_ownership is None else version_ownership
    errors = []
    found = set()
    owned = set()
    stopped = set()
    try:
        found.update(row["agent_session_id"] for row in sessions(
            agent, evidence, project=project, timeout_seconds=remaining_timeout(deadline),
        ))
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        evidence.failure(exc)
        errors.append(str(exc))
    if environment is not None and project is None:
        try:
            if not job:
                raise ValueError("No final job timestamps; native session ownership cannot be established.")
            found.update(job_session_ids(environment, agent, version, job, evidence))
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
            evidence.failure(exc)
            errors.append(str(exc))
    for session_id in sorted(found - before):
        try:
            original = session_action(agent, session_id, "show", evidence, project=project, deadline=deadline)
            indicator = original.get("version_indicator", {})
            candidate_ids = {
                candidate["candidate_id"] for candidate in ((job or {}).get("result") or {}).get("candidates", [])
                if isinstance(candidate.get("candidate_id"), str)
            }
            candidate = any(
                isinstance(value, str) and (value.startswith("cand_" + job_id + "_") or value in candidate_ids)
                for key, value in indicator.items() if key in {"agent_version", "candidate_id", "optimization_candidate_id"}
            )
            candidate_reference = any(
                key in {"candidate_id", "optimization_candidate_id"}
                or (key == "agent_version" and isinstance(value, str) and value.startswith("cand_"))
                for key, value in indicator.items()
            )
            related = candidate if candidate_reference else indicator.get("agent_version") == version
            observed_version = indicator.get("agent_version", "")
            if project is not None and isinstance(observed_version, str) and re.fullmatch(r"draft-\d+", observed_version):
                if not endpoint or deadline is None:
                    raise ValueError("The owned project and cleanup deadline are required for draft-version discovery.")
                if observed_version not in version_ownership:
                    if len(version_ownership) >= MAX_CLEANUP_SESSIONS:
                        raise RuntimeError("Draft-version discovery exceeded the bounded ownership lookup limit.")
                    version_ownership[observed_version] = owned_draft_version(
                        project, agent, observed_version, job_id, endpoint, evidence, deadline,
                    )
                related = candidate = version_ownership[observed_version]
            if original.get("agent_session_id") != session_id or not related:
                evidence.append("unrelated_session_preserved", {"session_id": session_id})
                continue
            if job and session_id not in verified:
                created = timestamp(original.get("created_at"), "session creation time")
                start = timestamp(job.get("created_at"), "job creation time")
                end = timestamp(job.get("updated_at"), "job update time")
                upper = end + (CLEANUP_MAX_SECONDS if allow_terminal_tail else 0)
                if created < start or created > upper:
                    evidence.append("outside_job_window_session_preserved", {"session_id": session_id})
                    continue
                if created > datetime.now(timezone.utc).timestamp():
                    raise ValueError("Session creation time is in the future; ownership is unverified.")
            owned.add(session_id)
            if len(owned | verified) > MAX_CLEANUP_SESSIONS:
                raise RuntimeError("Optimizer sessions exceed the bounded cleanup limit.")
            if original.get("status") in INACTIVE_SESSIONS and (
                session_id in verified or original.get("stopped_at") or original.get("status") in {"expired", "deleted"}
            ):
                continue
            session_action(agent, session_id, "stop", evidence, project=project, deadline=deadline)
            for attempt in range(6):
                status = session_action(agent, session_id, "show", evidence, project=project, deadline=deadline)
                if status.get("agent_session_id") == session_id and status.get("status") in INACTIVE_SESSIONS:
                    break
                if attempt < 5:
                    time.sleep(remaining_timeout(deadline, 2))
            if status.get("agent_session_id") != session_id or status.get("status") not in INACTIVE_SESSIONS:
                raise RuntimeError(f"Optimizer session {session_id} has no verified stopped state.")
            stopped.add(session_id)
            verified.add(session_id)
            evidence.append("optimizer_session_stopped", {
                "session": status, "stop_acknowledged": True, "stopped_at_visible": "stopped_at" in status,
            })
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
            evidence.failure(exc)
            errors.append(f"{session_id}: {exc}")
    snapshot = {"observed_owned": sorted(owned), "stopped": sorted(stopped), "errors": errors}
    evidence.append("optimizer_cleanup_snapshot", snapshot)
    if errors:
        raise RuntimeError("Optimizer cleanup is incomplete: " + "; ".join(errors))
    return snapshot


def reconcile_sessions(project, agent: str, version: str, before: set[str], job_id: str,
                       job: dict, evidence: Evidence, *, endpoint: str) -> dict:
    deadline = time.monotonic() + CLEANUP_MAX_SECONDS
    observed, verified = set(), set()
    version_ownership = {}
    quiet = 0
    summary = {
        "job_id": job_id, "agent": agent, "version": version,
        "status": "unverified", "max_seconds": CLEANUP_MAX_SECONDS,
        "max_passes": CLEANUP_PASSES, "max_sessions": MAX_CLEANUP_SESSIONS,
        "max_stop_requests": CLEANUP_PASSES * MAX_CLEANUP_SESSIONS,
        "session_creation_tail_seconds": CLEANUP_MAX_SECONDS,
        "passes": 0, "stopped_session_ids": [], "resources_deleted": False,
        "scope": "Recorded baseline version and verified job candidate versions, excluding the pre-job snapshot; bounded observation only.",
    }
    try:
        if not job or job.get("id") != job_id or job.get("status") not in TERMINAL:
            raise RuntimeError("A terminal owned job is required before claiming session cleanup.")
        start = timestamp(job.get("created_at"), "job creation time")
        if timestamp(job.get("updated_at"), "job update time") < start:
            raise ValueError("Optimizer job timestamps are out of order.")
        for sweep in range(CLEANUP_PASSES):
            snapshot = stop_new_sessions(
                agent, version, before, job_id, evidence, project=project, job=job,
                deadline=deadline, verified=verified,
                endpoint=endpoint, version_ownership=version_ownership, allow_terminal_tail=True,
            )
            current = set(snapshot["observed_owned"])
            quiet = quiet + 1 if current <= observed and not snapshot["stopped"] else 0
            observed.update(current)
            summary.update(passes=sweep + 1, stopped_session_ids=sorted(verified), quiet_passes=quiet)
            evidence.append("optimizer_cleanup_progress", summary)
            if sweep < CLEANUP_PASSES - 1:
                time.sleep(remaining_timeout(deadline, CLEANUP_INTERVAL_SECONDS))
        if quiet < 2:
            raise RuntimeError("Late sessions have not settled for two readbacks; cleanup remains unverified.")
        summary["status"] = "observed_quiescence"
        return summary
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        summary["error"] = {"type": type(exc).__name__, "message": str(exc)}
        evidence.failure(exc)
        raise
    finally:
        summary["stopped_session_ids"] = sorted(verified)
        evidence.append("optimizer_cleanup", summary)
        write_new(RESULTS / (evidence.run_id + "-cleanup.json"), summary)


def time_limit(value: int = 600, receipt: dict | None = None) -> int:
    if type(value) is not int or not 60 <= value <= 1800:
        raise ValueError("--max-seconds must be an integer between 60 and 1800.")
    if receipt is not None:
        recorded = receipt.get("max_seconds", 600)
        if type(recorded) is not int or not 60 <= recorded <= 1800:
            raise ValueError("Recorded optimizer time budget is invalid; preserve the receipt.")
        if value != recorded:
            raise ValueError(
                f"Recorded job budget is {recorded}s; resume with --max-seconds {recorded}. "
                "An existing job's budget cannot be changed."
            )
    return value


def cancel_verified(operations, job_id: str, evidence: Evidence, *, max_seconds: int = 600) -> dict:
    from azure.core.exceptions import AzureError
    deadline = time.monotonic() + CANCELLATION_MAX_SECONDS
    evidence.append("cancellation_budget", {
        "job_id": job_id, "max_seconds": time_limit(max_seconds),
        "cancellation_max_seconds": CANCELLATION_MAX_SECONDS,
    })
    try:
        timeout = remaining_timeout(deadline)
        evidence.append("cancel_requested", operations.cancel_optimization_job(
            job_id, read_timeout=timeout, connection_timeout=min(15, timeout),
        ))
    except (AzureError, OSError, RuntimeError) as exc:
        evidence.failure(exc)
    for attempt in range(6):
        timeout = remaining_timeout(deadline)
        job = serializable(operations.get_optimization_job(
            job_id, read_timeout=timeout, connection_timeout=min(15, timeout),
        ))
        evidence.append("cancel_status", job)
        if job.get("status") in TERMINAL:
            return job
        if attempt < 5:
            time.sleep(remaining_timeout(deadline, 5))
    raise RuntimeError(f"Optimizer {job_id} cancellation is not confirmed; operations may still be active.")


def monitor(operations, job_id: str, evidence: Evidence, *, max_seconds: int = 600) -> dict:
    max_seconds = time_limit(max_seconds)
    job = serializable(operations.get_optimization_job(job_id, read_timeout=60, connection_timeout=15))
    created = timestamp(job.get("created_at"), "optimizer creation time")
    if created > datetime.now(timezone.utc).timestamp() + 30:
        raise ValueError("Optimizer creation time is in the future; refusing to reset its budget.")
    remaining = max(0, min(max_seconds, max_seconds - (datetime.now(timezone.utc).timestamp() - created)))
    deadline = time.monotonic() + remaining
    evidence.append("monitor_budget", {
        "job_id": job_id, "max_seconds": max_seconds, "created_at": created,
        "deadline_at": created + max_seconds, "remaining_seconds": remaining,
    })
    previous = None
    last_change = time.monotonic()
    progress = {}
    for poll in range(math.ceil(max_seconds / 10)):
        evidence.append("job_status", job)
        result = job.get("result") or {}
        progress = {
            "job_id": job_id, "status": job.get("status"), "completion_status": job.get("completion_status"),
            "candidates": [{key: candidate.get(key) for key in (
                "candidate_id", "eval_id", "eval_run_id", "avg_score",
            )} for candidate in result.get("candidates", [])],
            "latency_usage": result.get("latency_usage", []), "token_usage": result.get("token_usage", []),
            "warnings": job.get("warnings", []), "error": job.get("error"),
            "service_progress": job.get("progress"),
        }
        fingerprint = digest(progress)
        if fingerprint != previous:
            previous, last_change = fingerprint, time.monotonic()
        evidence.append("optimizer_progress", {
            **progress, "polls": poll + 1,
            "unchanged_seconds": round(time.monotonic() - last_change, 3),
        })
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
    evidence.append("optimizer_timeout", {
        **progress, "max_seconds": max_seconds, "created_at": created, "deadline_at": created + max_seconds,
        "unchanged_seconds": round(time.monotonic() - last_change, 3),
        "cause": "The recorded job deadline expired; service latency/throttling cause is not established by polling alone.",
        "deadline_extended": False, "new_job_submitted": False,
    })
    raise TimeoutError(f"Optimizer {max_seconds}-second limit reached; cancellation is required.")


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
    max_seconds = time_limit(getattr(args, "max_seconds", 600))
    if LANGUAGE == "en" and not args.resume and args.suite in FROZEN_SUITES:
        verify_development_freeze(args.suite)
    if not args.resume and args.suite == "automated-v5" and max_seconds > 1200:
        raise ValueError("The v5 optimizer budget cannot exceed 1200 seconds.")
    endpoint, _ = read_config()
    environment = owned_endpoint(endpoint)
    receipt = recorded_job(args.resume, endpoint, args.agent, args.version) if args.resume else None
    max_seconds = time_limit(max_seconds, receipt)
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
        terminal_saved = False
        failure = None
        try:
            if not args.resume:
                preflight(project, args.agent, args.version, args.optimizer_deployment, evidence)
                verify_session_context(args.agent, endpoint, evidence)
                before = {row["agent_session_id"] for row in sessions(args.agent, evidence, project=project)}
                if args.suite == "automated-v5":
                    write_new(RESULTS / f"optimizer-{suite_hash(args.suite)[:16]}-attempt.json", {
                        "run_id": evidence.run_id, "suite": args.suite, "agent": args.agent,
                        "version": args.version, "max_seconds": max_seconds,
                        "purpose": "one dev-only optimizer submission; never automatically retry or promote",
                    })
                request = payload(
                    args.agent, args.version, judge, args.optimizer_deployment, args.suite, cases=cases,
                    prompt_path=getattr(args, "prompt_file", None),
                )
                evidence.append("submitted_config", {
                    "payload": request, "suite": args.suite, "dev_ids": [c["id"] for c in cases],
                    "dev_sha256": digest(cases), "configuration_sha256": digest(request),
                    "max_seconds": max_seconds,
                    "holdout_submitted": False, "human_review_completed": False,
                })
                operation_id = str(uuid4())
                evidence.append("submission_intent", {
                    "operation_id": operation_id, "endpoint": endpoint, "max_seconds": max_seconds,
                })
                poller = project.beta.agents.begin_create_optimization_job(
                    job=request, operation_id=operation_id, polling=False,
                )
                job_id = poller.details["job_id"]
                cleanup_needed = True
                evidence.append("job_submitted", {"job_id": job_id, "poller_details": poller.details})
                print(json.dumps({"job_id": job_id, "max_seconds": max_seconds, "evidence": str(evidence.path)}), flush=True)
                receipt = {
                    "job_id": job_id, "status": "submitted", "endpoint": endpoint,
                    "agent": args.agent, "version": args.version, "suite": args.suite,
                    "dev_items": len(cases), "session_ids_before": sorted(before),
                    "operation_id": operation_id, "configuration_sha256": digest(request),
                    "max_seconds": max_seconds,
                }
                write_new(RESULTS / (evidence.run_id + "-job.json"), receipt)
            else:
                cleanup_needed = True
            job = monitor(project.beta.agents, job_id, evidence, max_seconds=max_seconds)
            target = (job.get("inputs") or {}).get("agent")
            if target and (target.get("agent_name") != args.agent or target.get("agent_version") != args.version):
                raise ValueError("Service job inputs do not match the recorded target version.")
            evidence.append("terminal_job", job)
            write_new(RESULTS / (evidence.run_id + "-terminal.json"), job)
            terminal_saved = True
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
            summary["max_seconds"] = max_seconds
            evidence.append("optimizer_outcome", summary)
            write_new(RESULTS / (evidence.run_id + "-outcome.json"), summary)
            return summary
        except BaseException as exc:
            failure = exc
            evidence.failure(exc)
            raise
        finally:
            try:
                if cleanup_needed and job_id and (job is None or job.get("status") not in TERMINAL):
                    job = cancel_verified(project.beta.agents, job_id, evidence, max_seconds=max_seconds)
                if job and job.get("status") in TERMINAL and not terminal_saved:
                    evidence.append("terminal_job", job)
                    write_new(RESULTS / (evidence.run_id + "-terminal.json"), job)
                    summary = {
                        **outcome(job, [], (receipt or {}).get("dev_items")),
                        "suite": (receipt or {}).get("suite", args.suite),
                        "max_seconds": max_seconds,
                        "failure": {"type": type(failure).__name__, "message": str(failure)} if failure else None,
                    }
                    evidence.append("optimizer_outcome", summary)
                    write_new(RESULTS / (evidence.run_id + "-outcome.json"), summary)
            finally:
                if cleanup_needed and before is not None and (not args.resume or "session_ids_before" in receipt):
                    reconcile_sessions(project, args.agent, args.version, before, job_id, job, evidence, endpoint=endpoint)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent")
    parser.add_argument("--version")
    parser.add_argument("--optimizer-deployment", required=True)
    parser.add_argument("--suite", choices=SUITES, default=DEFAULT_SUITE)
    parser.add_argument(
        "--max-seconds", type=int, default=600,
        help="Job budget from creation, 60..1800 seconds (default: 600). Resume must match the recorded budget.",
    )
    parser.add_argument("--prompt-file", type=Path, help="Required for new live jobs: matching baseline in data/prompts/*.txt.")
    parser.add_argument("--require-oidc", action="store_true", help="Require the existing CI identity in the ownership ledger.")
    parser.add_argument("--live", action="store_true")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--resume", help="Resume monitoring only an optimization job recorded in this checkout.")
    mode.add_argument("--probe-reflection", action="store_true", help="One bounded model call; no dataset or optimization job.")
    args = parser.parse_args()
    try:
        time_limit(args.max_seconds)
    except ValueError as exc:
        parser.error(str(exc))
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
            "max_stalls": 1, "max_seconds": args.max_seconds, "auto_promote": False,
            "cancellation_max_seconds": CANCELLATION_MAX_SECONDS,
            "cleanup_max_seconds": CLEANUP_MAX_SECONDS, "cleanup_passes": CLEANUP_PASSES,
            "cleanup_max_sessions": MAX_CLEANUP_SESSIONS,
            "cleanup_max_stop_requests": CLEANUP_PASSES * MAX_CLEANUP_SESSIONS,
            "prompt_file": str(args.prompt_file or active_prompt()),
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
