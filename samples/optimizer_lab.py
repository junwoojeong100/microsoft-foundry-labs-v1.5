"""Bounded native Agent Optimizer job on dev only. Never auto-promotes a candidate."""

import argparse
import json
from pathlib import Path
import time

from cloud import project_client
from evidence import Evidence, digest
from evaluation_lab import settings_hash
from workshop import DATA, RESULTS, config_values, save_json, validate_data


def payload(agent: str, version: str, judge: str, optimizer: str) -> dict:
    dev = [case for case in validate_data() if case["split"] == "dev"]
    return {"inputs": {
        "agent": {"agent_name": agent, "agent_version": version},
        "train_dataset": {"type": "inline", "items": [{
            "query": case["query"], "ground_truth": case["ground_truth"],
            "criteria": [{"name": case["id"], "instruction": case["expected_behavior"]}],
        } for case in dev]},
        "evaluators": [{"name": "builtin.task_adherence"}],
        "options": {"max_candidates": 2, "max_stalls": 1, "eval_model": judge,
                    "optimization_model": optimizer},
    }}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--optimizer-deployment", required=True)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    judge = config_values()["FOUNDRY_JUDGE_DEPLOYMENT_NAME"]
    request = payload(args.agent, args.version, judge, args.optimizer_deployment)
    if not args.live:
        print(json.dumps({"plan_only": True, "dev_items": 10, "holdout_items": 0, "max_candidates": 2,
                          "max_stalls": 1, "auto_promote": False, "request": request}, ensure_ascii=False, indent=2))
        return
    if not judge:
        raise ValueError("Set an explicit judge deployment.")
    evidence = Evidence("optimizer")
    evidence.append("submitted_config", {"payload": request, "settings_hash": settings_hash(),
                                          "dev_ids": [c["id"] for c in validate_data() if c["split"] == "dev"],
                                          "prompt_sha256": digest((DATA / "prompts/agent-v4.txt").read_text()),
                                          "holdout_submitted": False})
    with project_client(evidence) as (project, _, _, _):
        poller = project.beta.agents.begin_create_optimization_job(job=request, polling_interval=10)
        job_id = poller.details["job_id"]
        evidence.append("job_submitted", {"job_id": job_id})
        save_json(RESULTS / (evidence.run_id + "-job.json"), {"job_id": job_id, "status": "submitted"})
        deadline = time.monotonic() + 600
        while not poller.done() and time.monotonic() < deadline:
            time.sleep(5)
        if not poller.done():
            evidence.append("cancel_requested", project.beta.agents.cancel_optimization_job(job_id))
            evidence.append("timeout", {"job_id": job_id, "must_inspect_active_jobs": True})
            raise RuntimeError("Optimizer time limit reached. Cancellation requested; verify the job's final state.")
        result = poller.result()
        evidence.append("optimizer_result", result)
        save_json(RESULTS / (evidence.run_id + ".json"), result.as_dict())
        candidates = getattr(result, "candidates", None)
        if candidates is None:
            candidates = getattr(getattr(result, "result", None), "candidates", [])
        changed = [c for c in candidates if c.mutations]
        print(json.dumps({"evidence": str(evidence.path), "new_candidates": len(changed), "promoted": False}))
        if not changed:
            raise RuntimeError("Optimizer returned no changed full candidate. Do not claim improvement.")


if __name__ == "__main__":
    main()
