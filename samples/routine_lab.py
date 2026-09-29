"""Bounded azd Routines exercise. Disable is mandatory; no routine/RG deletion."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import subprocess
import time
from uuid import uuid4

from evidence import Evidence
from workshop import RESULTS, read_config, save_json

STATE = RESULTS / "routine.json"


def azd(endpoint: str, evidence: Evidence, *args: str):
    result = subprocess.run(
        ["azd", "ai", "routine", *args, "--project-endpoint", endpoint, "--output", "json", "--no-prompt"],
        text=True, capture_output=True, timeout=90, check=False,
    )
    evidence.append("azd_routine", {"operation": list(args), "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
    if result.returncode:
        raise RuntimeError(f"Routine {args[0]} failed. Inspect the recorded name before retrying; it may already exist.")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Routine CLI did not return JSON; original output retained, no success assumed.") from exc


def stop_verified(endpoint: str, name: str, evidence: Evidence) -> None:
    azd(endpoint, evidence, "disable", name)
    status = azd(endpoint, evidence, "show", name)
    evidence.append("disabled_state", status)
    if status.get("enabled") is not False:
        raise RuntimeError("Routine disable is not confirmed; do not declare operations stopped.")


def run(args: argparse.Namespace, evidence: Evidence) -> None:
    endpoint, _ = read_config()
    if args.command in {"create", "scheduled-test"}:
        if STATE.exists() or not args.agent:
            raise ValueError("Provide --agent for a new routine; an existing receipt cannot be overwritten.")
        name = "contoso-policy-timer-" + uuid4().hex[:8]
        fire_at = datetime.now(timezone.utc) + timedelta(minutes=3 if args.command == "scheduled-test" else 60)
        state = {"name": name, "endpoint": endpoint, "agent": args.agent, "trigger_at": fire_at.isoformat(), "run_id": evidence.run_id}
        save_json(STATE, state)
        manifest = RESULTS / (name + ".json")
        save_json(manifest, {
            "triggers": {"default": {"type": "timer", "at": fire_at.strftime("%Y-%m-%dT%H:%M:%SZ")}},
            "action": {"type": "invoke_agent_responses_api", "agent_name": args.agent,
                       "input": "Contoso 구매 정책을 세 문장으로 요약해줘. 외부 발송·주문·승인은 하지 마."},
        })
        try:
            azd(endpoint, evidence, "create", name, "--file", str(manifest),
                "--enabled=" + ("true" if args.command == "scheduled-test" else "false"))
            if args.command == "scheduled-test":
                deadline = time.monotonic() + 360
                while time.monotonic() < deadline:
                    history = azd(endpoint, evidence, "run", "list", name, "--top", "5")
                    rows = history if isinstance(history, list) else history.get("value", history.get("runs", []))
                    if rows:
                        evidence.append("scheduled_run_observed", rows)
                        # The raw status/output is judged separately; any run is not automatically successful.
                        return
                    time.sleep(15)
                raise RuntimeError("No scheduled run observed within six minutes.")
        finally:
            stop_verified(endpoint, name, evidence)
        return
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if state["endpoint"] != endpoint:
        raise ValueError("Routine receipt belongs to another project.")
    name = state["name"]
    if args.command == "dispatch":
        try:
            evidence.append("manual_dispatch", azd(endpoint, evidence, "dispatch", name))
        finally:
            stop_verified(endpoint, name, evidence)
    elif args.command == "stop":
        stop_verified(endpoint, name, evidence)
    evidence.append("run_history", azd(endpoint, evidence, "run", "list", name, "--top", "5"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["create", "scheduled-test", "dispatch", "status", "stop"])
    parser.add_argument("--agent")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if not args.live:
        print(f"PLAN ONLY: Routine {args.command}. Timer is one-shot; no recurring background work.")
        return
    evidence = Evidence("routine")
    try:
        run(args, evidence)
    except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        evidence.failure(exc)
        raise
    finally:
        print(f"Evidence: {evidence.path}")


if __name__ == "__main__":
    main()
