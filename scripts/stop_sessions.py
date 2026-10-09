"""Stop only sessions recorded by this checkout; do not delete resources or session files."""

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from evidence import Evidence
from lab_cli import run


def stop_one(path: Path, evidence: Evidence) -> bool:
    """Stop one recorded session and read it back; return True only when it is confirmed stopped."""
    state = json.loads(path.read_text())
    if state["agent"] not in {"contoso-purchasing", "contoso-purchasing-responses"}:
        raise ValueError("Unexpected session owner.")
    command = ["azd", "ai", "agent", "sessions", "stop", state["session_id"], "--agent-name", state["agent"], "--no-prompt"]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=120, check=False)
    evidence.append("stop", {"session_id": state["session_id"], "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
    if result.returncode:
        return False
    check = subprocess.run(
        ["azd", "ai", "agent", "sessions", "show", state["session_id"], "--agent-name", state["agent"], "--output", "json"],
        cwd=ROOT, text=True, capture_output=True, timeout=60, check=True,
    )
    actual = json.loads(check.stdout)
    evidence.append("verified_state", actual)
    return actual.get("status") in {"idle", "expired", "deleted"}


def main():
    receipts = sorted((ROOT / "results").glob("contoso-hosted-client-*-session.json"))
    if not receipts:
        print("No recorded Hosted sessions; nothing to stop.")
        return
    evidence = Evidence("stop-sessions")
    failures = []
    for path in receipts:
        # One bad receipt, timeout or azd error must not leave the remaining sessions running.
        try:
            if not stop_one(path, evidence):
                failures.append(path.name)
        except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
            evidence.append("stop_error", {"receipt": path.name, "type": type(error).__name__, "message": str(error)})
            failures.append(path.name)
    if failures:
        raise RuntimeError(
            f"Session stop was not confirmed for {len(failures)} of {len(receipts)} recorded sessions ({', '.join(failures)}); "
            f"every recorded session was still attempted. Inspect the private evidence file {evidence.path.name}."
        )


if __name__ == "__main__":
    run(main)
