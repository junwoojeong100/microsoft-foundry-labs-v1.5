"""Read-only closeout of the owned environment; no resource deletion or implicit cancellation."""

from datetime import datetime, timedelta, timezone
from itertools import islice
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from cloud import project_client
from evidence import Evidence
from routine_lab import azd
from lab_cli import run
from workshop import RESULTS, save_json
from azure_environment import owned


def routine_receipts(endpoint: str) -> list[dict]:
    receipts = {}
    for path in sorted(RESULTS.glob("*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict) or (
            value.get("schema") != "contoso-routine-v2" and path.name != "routine.json"
        ):
            continue
        if value.get("endpoint") != endpoint or not isinstance(value.get("name"), str):
            raise ValueError(f"Routine receipt endpoint/name mismatch: {path.name}.")
        if value["name"] in receipts:
            raise ValueError("Duplicate routine receipts; inspect their ownership before closeout.")
        receipts[value["name"]] = {**value, "receipt_file": path.name}
    if len(receipts) > 20:
        raise ValueError("Closeout supports at most 20 owned routines per bounded query.")
    return list(receipts.values())


def main():
    state = owned()
    evidence = Evidence("operations")
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(), "resource_group": state["resource_group"],
        "retention": "Keep Azure resources until explicit deletion approval; no expiry date authorized.",
        "next_check_by": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
        "resources_deleted": False, "hosted": [], "routine": None, "routines": [],
        "voice_sessions": "not_created",
        "quality_evaluation_performed": False, "not_deployed_agents": [],
    }
    with project_client(evidence) as (project, _, endpoint, _):
        if endpoint != state["project_endpoint"]:
            raise ValueError("Current project is not the owned validation environment.")
        inventory = list(islice(project.agents.list(limit=100), 101))
        if len(inventory) > 100:
            raise ValueError("Agent inventory exceeds the bounded workshop scope.")
        names = {agent.name for agent in inventory}
        evidence.append("agent_inventory", {"names": sorted(names)})
        for name in ("contoso-purchasing", "contoso-purchasing-responses"):
            if name not in names:
                report["not_deployed_agents"].append(name)
                continue
            agent = project.agents.get(name)
            sessions = list(project.agents.list_sessions(name))
            evidence.append("sessions", {"agent": name, "sessions": sessions})
            report["hosted"].append({
                "name": name, "latest_version": agent.versions.latest.version,
                "sessions": [{"id": s.agent_session_id, "status": s.status.value if hasattr(s.status, "value") else s.status,
                              "stopped_at": s.stopped_at.isoformat() if s.stopped_at else None} for s in sessions],
                "active_sessions": sum(s.status not in {"idle", "expired", "deleted"} for s in sessions),
            })
        jobs = list(project.beta.agents.list_optimization_jobs(limit=20))
        evidence.append("optimization_jobs", jobs)
        report["optimization_jobs"] = [{"id": job.id, "status": job.status.value if hasattr(job.status, "value") else job.status} for job in jobs]
        schedules = list(project.beta.schedules.list(enabled=True))
        monitors = list(project.beta.agent_insight_monitors.list(limit=20))
        evidence.append("enabled_schedules", schedules)
        evidence.append("insight_monitors", monitors)
        report["enabled_evaluation_schedules"] = len(schedules)
        report["insight_monitors"] = len(monitors)
        for routine in routine_receipts(endpoint):
            current = azd(endpoint, evidence, "show", routine["name"])
            if current.get("name") != routine["name"] or type(current.get("enabled")) is not bool:
                raise ValueError("Routine state readback is incomplete; closeout is unverified.")
            record = {
                "name": current["name"], "enabled": current["enabled"],
                "receipt_file": routine["receipt_file"],
                "execution_verification": "See the separate response/trace evidence; state is not execution proof.",
            }
            report["routines"].append(record)
            if routine["receipt_file"] == "routine.json":
                report["routine"] = record
    active = (
        any(item["active_sessions"] for item in report["hosted"])
        or any(item["status"] in {"queued", "in_progress"} for item in report["optimization_jobs"])
        or report["enabled_evaluation_schedules"] or report["insight_monitors"]
        or any(routine["enabled"] for routine in report["routines"])
    )
    report["active_work_observed"] = bool(active)
    save_json(RESULTS / "operations-status.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if active:
        raise RuntimeError("Active work remains; stop only the owned operations and recheck.")


if __name__ == "__main__":
    run(main)
