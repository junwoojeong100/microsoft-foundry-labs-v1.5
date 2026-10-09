"""Bounded azd Routines exercise. Disable is mandatory; no routine/RG deletion."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import signal
import subprocess
import time
from uuid import uuid4

from evidence import Evidence
from lab_cli import run as run_cli
from workshop import LANGUAGE, RESULTS, read_config

STATE = RESULTS / "routine.json"
HISTORY_LIMITATION = (
    "azd history is not authoritative: the service uses data/next_link, while affected "
    "routines extensions decode value/nextPageToken. An empty CLI page does not prove nonexecution."
)


def azd(endpoint: str, evidence: Evidence, *args: str):
    try:
        result = subprocess.run(
            ["azd", "ai", "routine", *args, "--project-endpoint", endpoint,
             "--output", "json", "--no-prompt", "--timeout", "30s"],
            text=True, capture_output=True, timeout=90, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        evidence.append("azd_routine_timeout", {
            "operation": list(args),
            "stdout": exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else exc.stdout,
            "stderr": exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else exc.stderr,
        })
        raise
    evidence.append("azd_routine", {"operation": list(args), "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
    if result.returncode:
        raise RuntimeError(f"Routine {args[0]} failed. Inspect the recorded name before retrying; it may already exist.")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Routine CLI did not return JSON; original output retained, no success assumed.") from exc


def stop_verified(endpoint: str, name: str, evidence: Evidence) -> None:
    try:
        azd(endpoint, evidence, "disable", name)
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        # A write may have succeeded before CLI decoding or the transport failed.
        evidence.failure(exc)
    status = azd(endpoint, evidence, "show", name)
    evidence.append("disabled_state", status)
    if status.get("name") != name or status.get("enabled") is not False:
        raise RuntimeError("Routine disable is not confirmed; do not declare operations stopped.")


def write_new(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def history_rows(history) -> list[dict]:
    if isinstance(history, list):
        rows = history
    elif isinstance(history, dict):
        key = next((key for key in ("data", "value", "runs") if key in history), None)
        if key is None:
            raise ValueError("Unrecognized Routine history response; no execution inferred.")
        rows = history[key]
        if rows is None:
            return []
    else:
        raise ValueError("Unrecognized Routine history response.")
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("Malformed Routine history rows.")
    return rows


def completed_run(row: dict, *, dispatch_id: str | None = None) -> bool:
    if dispatch_id and row.get("dispatch_id") != dispatch_id:
        return False
    return (
        str(row.get("status", "")).lower() in {"finished", "completed", "succeeded"}
        and str(row.get("phase", "")).lower() == "completed"
        and isinstance(row.get("response_id"), str) and bool(row["response_id"].strip())
        and not any(row.get(key) for key in ("error_type", "error_message", "error_status_code"))
    )


def owned_environment(endpoint: str) -> dict:
    state = json.loads((RESULTS / "azure-environment.json").read_text(encoding="utf-8"))
    expected = f"https://{state['account_name']}.services.ai.azure.com/api/projects/{state['project_name']}"
    if endpoint != state.get("project_endpoint") or endpoint != expected:
        raise ValueError("Routine endpoint does not match the owned environment ledger.")
    return state


def messages(value) -> list[dict]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return []
    return value if isinstance(value, list) and all(isinstance(v, dict) for v in value) else []


def message_text(message: dict) -> str:
    return "\n".join(
        part["content"] for part in message.get("parts", [])
        if isinstance(part, dict) and part.get("type") == "text" and isinstance(part.get("content"), str)
    )


def completed_trace(rows: list[dict], state: dict) -> dict | None:
    for row in rows:
        success = row.get("success")
        if (not (success is True or (isinstance(success, str) and success.lower() == "true"))
                or not isinstance(row.get("responseId"), str) or not row["responseId"].startswith("resp_")
                or not row.get("operation_Id") or row.get("agent") != state["agent"]
                or row.get("operation") != "invoke_agent"):
            continue
        inputs = messages(row.get("inputMessages"))
        if not any(m.get("role") == "user" and message_text(m) == state["input"] for m in inputs):
            continue
        outputs = messages(row.get("outputMessages"))
        finals = [m for m in outputs if m.get("role") == "assistant" and m.get("finish_reason") == "stop"]
        output = "\n".join(message_text(m) for m in finals).strip()
        if not output or re.search(r"\[(?:REDACTED|HIDDEN)\]|<redacted>", output, re.I):
            continue
        observed_at = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
        earliest = datetime.fromisoformat(state["verification_start"].replace("Z", "+00:00"))
        if observed_at < earliest or observed_at > earliest + timedelta(minutes=10):
            continue
        return {
            "verification": "completed_action_trace", "routine": state["name"],
            "execution_kind": state["execution_kind"], "trace_id": row["operation_Id"],
            "response_id": row["responseId"], "observed_at": row["timestamp"], "response": output,
            "routine_run_id": None, "history_limitation": HISTORY_LIMITATION,
            "human_review_completed": False,
        }
    return None


def trace_query(state: dict) -> str:
    agent, marker = json.dumps(state["agent"]), json.dumps(state["marker"])
    start = datetime.fromisoformat(state["verification_start"].replace("Z", "+00:00"))
    end = start + timedelta(minutes=10)
    return f"""dependencies
| where timestamp between (datetime({start.isoformat()}) .. datetime({end.isoformat()}))
| extend agent=tostring(customDimensions["gen_ai.agent.name"]),
    operation=tostring(customDimensions["gen_ai.operation.name"]),
    inputMessages=tostring(customDimensions["gen_ai.input.messages"]),
    outputMessages=tostring(customDimensions["gen_ai.output.messages"]),
    responseId=tostring(customDimensions["gen_ai.response.id"])
| where agent == {agent} and operation == "invoke_agent"
| where inputMessages contains {marker}
| project timestamp, success, operation_Id, agent, operation, responseId, inputMessages, outputMessages
| order by timestamp desc
| take 10"""


def query_traces(environment: dict, state: dict, evidence: Evidence, *, timeout: float = 90) -> list[dict]:
    monitoring = environment.get("monitoring", {})
    app_id = monitoring.get("appId", {}).get("value")
    resource_id = monitoring.get("appInsightsId", {}).get("value", "")
    if (not app_id or not resource_id.lower().startswith(environment["resource_group_id"].lower() + "/")):
        raise ValueError("No owned App Insights reference; hidden CLI history cannot prove execution.")
    query = trace_query(state)
    evidence.append("routine_trace_query", {"app_id": app_id, "query": query})
    result = subprocess.run(
        ["az", "monitor", "app-insights", "query", "--app", app_id,
         "--subscription", environment["subscription"], "--analytics-query", query,
         "--offset", "1d", "--output", "json", "--only-show-errors"],
        text=True, capture_output=True, timeout=timeout, check=False,
    )
    evidence.append("routine_trace_result", {
        "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr,
    })
    if result.returncode:
        raise RuntimeError("Owned trace query failed; execution is unverified, not successful.")
    data = json.loads(result.stdout)
    if data.get("error") or not isinstance(data.get("tables"), list):
        raise ValueError("Incomplete or invalid trace query result.")
    rows = []
    for table in data["tables"]:
        columns = [column["name"] for column in table["columns"]]
        rows.extend(dict(zip(columns, row, strict=True)) for row in table["rows"])
    return rows


def verify_execution(endpoint: str, environment: dict, state: dict,
                     evidence: Evidence, wait_seconds: int) -> dict:
    deadline = time.monotonic() + wait_seconds
    history = azd(endpoint, evidence, "run", "list", state["name"], "--top", "20")
    evidence.append("run_history", {"raw": history, "limitation": HISTORY_LIMITATION})
    # A run row, including a completed dispatch, is not proof of an actual final agent response.
    evidence.append("completed_history_rows", [
        row for row in history_rows(history) if completed_run(row, dispatch_id=state.get("dispatch_id"))
    ])
    query = trace_query(state)
    print(f"Owned Routine trace query:\n```kql\n{query}\n```", flush=True)
    for _ in range(40):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        proof = completed_trace(query_traces(environment, state, evidence, timeout=min(90, remaining)), state)
        if proof:
            evidence.append("verified_execution", proof)
            return proof
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(15, remaining))
    raise RuntimeError("No completed, correlated action response observed within the bound. " + HISTORY_LIMITATION)


def run(args: argparse.Namespace, evidence: Evidence) -> dict:
    endpoint, _ = read_config()
    environment = owned_environment(endpoint)
    receipt = Path(args.receipt).resolve()
    if receipt.parent != RESULTS.resolve():
        raise ValueError("--receipt must be a file directly inside this checkout's results directory.")
    if not 30 <= args.wait_seconds <= 600 or not 60 <= args.delay_seconds <= 300:
        raise ValueError("Wait must be 30–600 seconds and one-shot delay 60–300 seconds.")
    if args.command == "scheduled-test" and args.wait_seconds <= args.delay_seconds + 30:
        raise ValueError("Scheduled test must allow time after the one-shot timer fires.")
    if args.command in {"create", "scheduled-test"}:
        if receipt.exists() or not args.agent:
            raise ValueError("Provide --agent for a new routine; an existing receipt cannot be overwritten.")
        name = "contoso-policy-timer-v2-" + uuid4().hex[:8]
        now = datetime.now(timezone.utc)
        fire_at = (now + timedelta(
            seconds=args.delay_seconds if args.command == "scheduled-test" else 3600
        )).replace(microsecond=0)
        marker = evidence.run_id
        state = {
            "schema": "contoso-routine-v2", "name": name, "endpoint": endpoint, "agent": args.agent,
            "trigger_at": fire_at.isoformat(), "run_id": evidence.run_id, "marker": marker,
            "execution_kind": "scheduled" if args.command == "scheduled-test" else "manual",
            "verification_start": fire_at.isoformat(),
            "input": (
                f"Summarize the Contoso purchasing policy in three English sentences. Do not send, order, or approve anything. Verification marker: {marker}"
                if LANGUAGE == "en" else f"Contoso 구매 정책을 세 문장으로 요약해줘. 외부 발송·주문·승인은 하지 마. 검증 표식: {marker}"
            ),
        }
        write_new(receipt, state)
        manifest = RESULTS / (name + ".json")
        write_new(manifest, {
            "triggers": {"default": {"type": "timer", "at": fire_at.strftime("%Y-%m-%dT%H:%M:%SZ")}},
            "action": {"type": "invoke_agent_responses_api", "agent_name": args.agent,
                       "input": state["input"]},
        })
        try:
            created = azd(endpoint, evidence, "create", name, "--file", str(manifest),
                          "--enabled=" + ("true" if args.command == "scheduled-test" else "false"))
            if (created.get("name") != name or created.get("action", {}).get("input") != state["input"]
                    or created.get("action", {}).get("agent_name") != args.agent):
                raise RuntimeError("Created Routine action does not match its recorded target/input.")
            if args.command == "scheduled-test":
                return verify_execution(endpoint, environment, state, evidence, args.wait_seconds)
            return {"routine": name, "receipt": str(receipt), "execution_verified": False}
        except BaseException as exc:
            evidence.failure(exc)
            raise
        finally:
            stop_verified(endpoint, name, evidence)
    state = json.loads(receipt.read_text(encoding="utf-8"))
    if state["endpoint"] != endpoint:
        raise ValueError("Routine receipt belongs to another project.")
    name = state["name"]
    if args.command == "dispatch":
        if state.get("schema") != "contoso-routine-v2" or state.get("execution_kind") != "manual":
            raise ValueError("Dispatch requires a new disabled manual-test receipt; legacy/scheduled receipts are read-only.")
        try:
            status = azd(endpoint, evidence, "show", name)
            if (status.get("enabled") is not False or status.get("action", {}).get("input") != state["input"]
                    or status.get("action", {}).get("agent_name") != state["agent"]):
                raise ValueError("Manual routine must remain disabled with its original recorded action.")
            state["verification_start"] = datetime.now(timezone.utc).isoformat()
            # Create before dispatch: even an ambiguous network failure must not cause a second dispatch.
            write_new(receipt.with_suffix(".dispatch.json"), {
                "name": name, "endpoint": endpoint, "attempted_at": state["verification_start"],
                "run_id": evidence.run_id,
            })
            dispatched = azd(endpoint, evidence, "dispatch", name)
            evidence.append("manual_dispatch", dispatched)
            state["dispatch_id"] = dispatched.get("dispatch_id")
            return verify_execution(endpoint, environment, state, evidence, args.wait_seconds)
        except BaseException as exc:
            evidence.failure(exc)
            raise
        finally:
            stop_verified(endpoint, name, evidence)
    if args.command == "stop":
        stop_verified(endpoint, name, evidence)
    status = azd(endpoint, evidence, "show", name)
    evidence.append("routine_status", status)
    history = azd(endpoint, evidence, "run", "list", name, "--top", "20")
    evidence.append("run_history", {"raw": history, "limitation": HISTORY_LIMITATION})
    return {
        "routine": name, "enabled": status.get("enabled"), "history_rows": len(history_rows(history)),
        "execution_verified": False, "history_limitation": HISTORY_LIMITATION,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["create", "scheduled-test", "dispatch", "status", "stop"])
    parser.add_argument("--agent")
    parser.add_argument("--receipt", type=Path, default=STATE, help="New receipts never overwrite previous evidence.")
    parser.add_argument("--wait-seconds", type=int, default=360)
    parser.add_argument("--delay-seconds", type=int, default=120)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if not args.live:
        print(f"PLAN ONLY: Routine {args.command}. Timer is one-shot; no recurring background work.")
        return
    evidence = Evidence("routine")
    def interrupted(signum, frame):
        raise KeyboardInterrupt("Routine interrupted; disabling its recorded schedule.")
    signal.signal(signal.SIGTERM, interrupted)
    try:
        print(json.dumps(run(args, evidence), ensure_ascii=False, indent=2))
    except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        evidence.failure(exc)
        raise
    finally:
        print(f"Evidence: {evidence.path}")


if __name__ == "__main__":
    run_cli(main)
