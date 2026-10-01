"""One v1/v2 learning comparison. No loop, optimizer, holdout, or predetermined scores."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import time

from cloud import project_client
from evidence import Budget, digest, redacted
from grounding import answer_format, parse_answer
from search_lab import policy_chunks
from workshop import DATA, LANGUAGE, RESULTS, ensure_response


def cases() -> list[dict]:
    rows = json.loads((DATA / "evaluation/instruction-comparison.json").read_text(encoding="utf-8"))["cases"]
    if len(rows) != 3 or len({row["id"] for row in rows}) != 3:
        raise ValueError("The learning comparison requires the same three fixed cases for both prompts.")
    for row in rows:
        if set(row) != {"id", "query", "checks"} or not row["query"] or len(row["checks"]) != 3:
            raise ValueError("Unexpected comparison case or checklist shape.")
        for check in row["checks"]:
            if set(check) != {"id", "pattern", "sources"} or not check["sources"]:
                raise ValueError("Checklist requirements cannot depend on the instruction version.")
            re.compile(check["pattern"])
    return rows


def score(raw: str, case: dict, sources: dict) -> dict:
    parse_answer(raw, sources)
    answer = json.loads(raw)
    selected = set(answer["citation_ids"])
    checks = {
        check["id"]: bool(re.search(check["pattern"], answer["answer"], re.I | re.S))
        and bool(selected & set(check["sources"]))
        for check in case["checks"]
    }
    return {"matched": sum(checks.values()), "total": len(checks), "checks": checks}


def summarize(rows: list[dict], expected: list[dict]) -> dict:
    ids = {case["id"] for case in expected}
    scores = {}
    for version in ("v1", "v2"):
        selected = [row for row in rows if row["instructions"] == version]
        if (len(selected) != len(ids) or {row["id"] for row in selected} != ids
                or any(row["status"] != "completed" for row in selected)):
            raise ValueError("A partial or failed comparison cannot show an improvement.")
        scores[version] = sum(row["checklist"]["matched"] for row in selected)
    if len({row["model"] for row in rows}) != 1:
        raise ValueError("Actual model versions changed; this is not a controlled comparison.")
    delta = scores["v2"] - scores["v1"]
    return {
        "scores": scores, "maximum": sum(len(case["checks"]) for case in expected), "delta": delta,
        "outcome": "improved" if delta > 0 else "unchanged" if delta == 0 else "regressed",
        "quality_release": False,
        "scope": "Mechanical fact/citation coverage for three teaching questions, not complete semantic quality or release evidence.",
    }


def compare(output: Path) -> dict:
    from openai import OpenAIError

    rows = cases()
    sources = {row["id"]: row for row in policy_chunks()}
    prompts = {f"v{version}": (DATA / f"prompts/agent-v{version}.txt").read_text(encoding="utf-8") for version in (1, 2)}
    if any(not set(check["sources"]) <= sources.keys() for row in rows for check in row["checks"]):
        raise ValueError("Comparison checklist cites an unknown source.")
    if not output.resolve().is_relative_to(RESULTS.resolve()):
        raise ValueError("Keep the one comparison result inside results/.")
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        report = {
            "schema": "contoso-instruction-comparison", "language": LANGUAGE, "status": "started",
            "instructions_sha256": {name: hashlib.sha256(text.encode()).hexdigest() for name, text in prompts.items()},
            "cases_sha256": digest(rows), "context_sha256": digest(sources), "rows": [],
            "model_calls_max": 6, "max_seconds": 360, "retries": 0, "holdout_cases": 0,
            "context_source": "Checked-in synthetic policy text, not a live Search retrieval.",
            "quality_release": False,
        }
        try:
            with project_client() as (project, _, endpoint, model), project.get_openai_client(max_retries=0, timeout=60) as client:
                receipt = RESULTS / "azure-environment.json"
                if receipt.exists():
                    owned = json.loads(receipt.read_text(encoding="utf-8"))
                    if owned.get("language", "ko") != LANGUAGE or owned.get("project_endpoint") != endpoint:
                        raise ValueError("The comparison profile/project differs from the owned environment receipt.")
                budget = Budget(max_requests=6, max_tokens=60000, max_seconds=360)
                deadline = time.monotonic() + 360
                for case in rows:
                    shared_input = json.dumps({
                        "query": case["query"], "grounding_context": list(sources.values()),
                        "context_kind": "supplied_synthetic_documents_not_a_tool_execution", "available_tools": [],
                    }, ensure_ascii=False)
                    for version in ("v1", "v2"):
                        budget.before_request(token_reservation=len(shared_input) + len(prompts[version]) + 2048)
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            raise TimeoutError("Single-comparison time budget exhausted.")
                        response = client.responses.create(
                            model=model, instructions=prompts[version], input=shared_input,
                            text=answer_format(list(sources)), tools=[], tool_choice="none",
                            max_output_tokens=2048, store=False, timeout=min(60, remaining),
                        )
                        row = {
                            "id": case["id"], "instructions": version, "query": case["query"],
                            "status": response.status, "response_id": response.id, "model": response.model,
                            "raw_answer": response.output_text, "input_sha256": digest(shared_input),
                        }
                        report["rows"].append(row)
                        raw = ensure_response(response)
                        row["checklist"] = score(raw, case, sources)
                        if response.usage:
                            budget.record_tokens(response.usage.input_tokens + response.usage.output_tokens)
                report.update(status="completed", comparison=summarize(report["rows"], rows))
        except (OpenAIError, OSError, ValueError, RuntimeError) as exc:
            report.update(status="failed", error={"type": type(exc).__name__, "message": str(exc)})
            raise
        finally:
            handle.write(json.dumps(redacted(report), ensure_ascii=False, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Explicitly allow six paid model calls once.")
    parser.add_argument("--output", type=Path, default=RESULTS / "instruction-comparison.json")
    args = parser.parse_args()
    if not args.live:
        print(json.dumps({
            "plan_only": True, "instructions": ["v1", "v2"], "same_cases_per_version": len(cases()),
            "model_calls": 0, "model_calls_if_approved": 6, "maximum_checklist_score": 9,
            "new_agent_deployments": 0, "optimizer_jobs": 0, "holdout_cases": 0,
            "output": str(args.output), "score_improvement_guaranteed": False,
        }, ensure_ascii=False, indent=2))
        return
    if args.output.exists():
        raise ValueError("A comparison already exists. Keep its actual result; do not resample until a better score appears.")
    result = compare(args.output)
    print(json.dumps(result["comparison"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
