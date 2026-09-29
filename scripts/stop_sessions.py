"""Stop only sessions recorded by this checkout; do not delete resources or session files."""

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from evidence import Evidence


def main():
    receipts = list((ROOT / "results").glob("contoso-hosted-client-*-session.json"))
    if not receipts:
        print("No recorded Hosted sessions; nothing to stop.")
        return
    evidence = Evidence("stop-sessions")
    failures = []
    for path in receipts:
        state = json.loads(path.read_text())
        if state["agent"] not in {"contoso-purchasing", "contoso-purchasing-responses"}:
            raise ValueError("Unexpected session owner.")
        command = ["azd", "ai", "agent", "sessions", "stop", state["session_id"], "--agent-name", state["agent"], "--no-prompt"]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=120, check=False)
        evidence.append("stop", {"session_id": state["session_id"], "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
        if result.returncode:
            failures.append(state["session_id"])
            continue
        check = subprocess.run(
            ["azd", "ai", "agent", "sessions", "show", state["session_id"], "--agent-name", state["agent"], "--output", "json"],
            cwd=ROOT, text=True, capture_output=True, timeout=60, check=True,
        )
        actual = json.loads(check.stdout)
        evidence.append("verified_state", actual)
        if actual.get("status") not in {"idle", "expired", "deleted"}:
            failures.append(state["session_id"])
    if failures:
        raise RuntimeError(f"Session stop failed for {len(failures)} recorded sessions; inspect private evidence.")


if __name__ == "__main__":
    main()
