"""Read-only closeout of the owned environment; no resource deletion or implicit cancellation."""

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from cloud import project_client
from evidence import Evidence
from lab_profile import validation_for
from routine_lab import azd
from workshop import save_json
from azure_environment import owned


def main():
    state = owned()
    evidence = Evidence("operations")
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(), "resource_group": state["resource_group"],
        "retention": "Keep Azure resources until explicit deletion approval; no expiry date authorized.",
        "next_check_by": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
        "resources_deleted": False, "hosted": [], "routine": None, "routines": [],
        "voice_sessions": "not_created",
        "quality_status_source": (validation_for(ROOT) / "automated-v3/quality.json").relative_to(ROOT).as_posix(),
    }
    with project_client(evidence) as (project, _, endpoint, _):
        if endpoint != state["project_endpoint"]:
            raise ValueError("Current project is not the owned validation environment.")
        for name in ("contoso-purchasing", "contoso-purchasing-responses"):
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
        receipt = ROOT / "results/routine.json"
        if receipt.exists():
            routine = json.loads(receipt.read_text())
            if routine["endpoint"] != endpoint:
                raise ValueError("Routine receipt endpoint mismatch.")
            current = azd(endpoint, evidence, "show", routine["name"])
            history = azd(endpoint, evidence, "run", "list", routine["name"], "--top", "10")
            report["routine"] = {
                "name": current["name"], "enabled": current["enabled"],
                "history_observed": bool(history.get("value")),
                "scheduled_execution_verified": False,
            }
            report["routines"].append(report["routine"])
        retained = validation_for(ROOT) / "current/routine.json"
        if retained.exists():
            proof = json.loads(retained.read_text())
            verified = (
                proof.get("verification") == "completed_action_trace"
                and bool(proof.get("response_id")) and bool(proof.get("trace_id"))
            )
            if report["routine"] and proof["name"] == report["routine"]["name"]:
                report["routine"].update(
                    scheduled_execution_verified=verified,
                    verification_source="retained actual completed action trace, not an invented run-history ID",
                    response_id=proof.get("response_id"), trace_id=proof.get("trace_id"),
                )
            else:
                current = azd(endpoint, evidence, "show", proof["name"])
                report["routines"].append({
                    "name": current["name"], "enabled": current["enabled"],
                    "scheduled_execution_verified": verified,
                    "verification_source": "retained actual completed action trace, not an invented run-history ID",
                    "response_id": proof.get("response_id"), "trace_id": proof.get("trace_id"),
                })
    active = (
        any(item["active_sessions"] for item in report["hosted"])
        or any(item["status"] in {"queued", "in_progress"} for item in report["optimization_jobs"])
        or report["enabled_evaluation_schedules"] or report["insight_monitors"]
        or any(routine["enabled"] for routine in report["routines"])
    )
    report["active_work_observed"] = bool(active)
    save_json(validation_for(ROOT) / "current/operations.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if active:
        raise RuntimeError("Active work remains; stop only the owned operations and recheck.")


if __name__ == "__main__":
    main()
