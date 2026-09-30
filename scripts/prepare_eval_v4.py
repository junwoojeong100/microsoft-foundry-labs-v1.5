"""Prepare exposed English regressions, freeze development, then seal a new independently authored holdout."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from evaluation_data import validate_cases, verify_development_freeze
from lab_profile import LANGUAGE
from search_lab import policy_chunks
from workshop import load_jsonl

DIRECTORY = ROOT / "data/en/evaluation/v4"
PREVIOUS = ROOT / "data/en/evaluation/v3"


def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_consistent(path: Path, text: str) -> None:
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise ValueError(f"{path.name} differs; original data will not be overwritten.")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(text)


def write_json(path: Path, value: dict) -> None:
    write_consistent(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def prepare() -> None:
    source = load_jsonl(PREVIOUS / "dev.jsonl") + load_jsonl(PREVIOUS / "holdout.jsonl")
    if len(source) != 40:
        raise ValueError("Preserve all 30 exposed dev and all 10 consumed holdout cases.")
    rows = [{
        **row, "id": f"v4-dev-{index:02}", "split": "dev",
        "origin": {"suite": "automated-v3", "id": row["id"], "original_split": row["split"],
                   "previous_origin": row.get("origin")},
    } for index, row in enumerate(source, 1)]
    write_consistent(DIRECTORY / "dev.jsonl", "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))
    write_consistent(DIRECTORY / "calibration.jsonl", (PREVIOUS / "calibration.jsonl").read_text(encoding="utf-8"))
    rubric = json.loads((PREVIOUS / "rubric.json").read_text())
    write_json(DIRECTORY / "rubric.json", {
        **rubric, "suite": "automated-v4", "required_dev_cases": 40,
        "description": "English candidate: all exposed v3 cases as unchanged regressions and a new frozen independent holdout.",
        "legacy_evidence": "The v3 7/10 holdout and its critical failure remain unchanged. No oracle, gate or calibration relaxation.",
    })
    print("Prepared 40 exposed English regressions and 8 unchanged judge controls; no v4 holdout was read.")


def freeze_paths() -> list[Path]:
    return sorted({
        *[ROOT / "samples" / name for name in (
            "lab_profile.py", "workshop.py", "evidence.py", "cloud.py", "search_lab.py", "grounding.py",
            "request_contract.py", "hosted_runtime.py", "business_checks.py", "evaluation_data.py",
            "evaluation_lab.py", "hosted_client.py",
        )],
        *[ROOT / "hosted" / name for name in ("main.py", "responses_main.py", "optimizer_responses.py")],
        ROOT / "scripts/build_hosted.py", ROOT / "requirements.txt", ROOT / "requirements-hosted.txt",
        *sorted((ROOT / "data/en/policies").glob("*.md")),
        ROOT / "data/en/inventory.csv", ROOT / "data/en/prompts/agent-v7.txt", ROOT / "data/en/evaluation/judge.txt",
        DIRECTORY / "dev.jsonl", DIRECTORY / "calibration.jsonl", DIRECTORY / "rubric.json",
    })


def freeze() -> None:
    if (DIRECTORY / "development-freeze.json").exists():
        verify_development_freeze("automated-v4")
        print("Existing development freeze is unchanged; nothing was overwritten.")
        return
    if (DIRECTORY / "holdout.jsonl").exists() or (DIRECTORY / "holdout-manifest.json").exists():
        raise ValueError("Freeze must precede independent holdout authoring.")
    required = json.loads((DIRECTORY / "rubric.json").read_text())
    validate_cases(load_jsonl(DIRECTORY / "dev.jsonl"), "dev", required)
    write_json(DIRECTORY / "development-freeze.json", {
        "schema": "contoso-development-freeze-v2", "suite": "automated-v4", "language": "en",
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "files": {path.relative_to(ROOT).as_posix(): checksum(path) for path in freeze_paths()},
        "final_holdout_exists_at_freeze": False,
        "validation_scope": "Local code/data freeze only. No Azure inference or release-quality pass.",
    })
    print("Frozen runtime, active English prompt, policies, dev, judge, controls, and gates before holdout authoring.")


def seal() -> None:
    frozen = verify_development_freeze("automated-v4")
    manifest_path = DIRECTORY / "holdout-manifest.json"
    path = DIRECTORY / "holdout.jsonl"
    if manifest_path.exists():
        raise ValueError("The holdout already has a seal; never replace or refresh it.")
    required = json.loads((DIRECTORY / "rubric.json").read_text())
    holdout = load_jsonl(path)
    validate_cases(holdout, "holdout", required)
    dev = load_jsonl(DIRECTORY / "dev.jsonl")
    for key in ("id", "scenario", "query"):
        values = [row[key].strip().casefold() for row in [*dev, *holdout]]
        if len(values) != len(set(values)):
            raise ValueError(f"Holdout duplicates a development or holdout {key}.")
    sources = {row["id"] for row in policy_chunks()}
    for row in holdout:
        citations = set(row["required_citations"]) | {
            source for group in row.get("required_citation_groups", []) for source in group
        }
        if not citations <= sources:
            raise ValueError("A holdout oracle cites an unknown policy source.")
        if (set(row["required_tools"]) & set(row["forbidden_tools"])
                or not set(row["required_tools"] + row["forbidden_tools"]) <= {"get_stock", "prepare_purchase_request"}):
            raise ValueError("Conflicting or unknown holdout tool constraints.")
    write_json(manifest_path, {
        "schema": "contoso-evaluation-manifest-v4", "suite": "automated-v4", "language": "en",
        "rows": len(holdout), "sha256": checksum(path), "created_at": datetime.now(timezone.utc).isoformat(),
        "development_freeze": {
            "path": "data/en/evaluation/v4/development-freeze.json",
            "sha256": checksum(DIRECTORY / "development-freeze.json"), "frozen_at": frozen["frozen_at"],
        },
        "authoring_method": "New synthetic questions authored after the recorded development freeze; no target inference.",
        "release_use": "independent_final_holdout", "release_status": "sealed_unexecuted",
        "minimum_pass_rate": required["minimum_pass_rate"], "native_pass_threshold": required["native_pass_threshold"],
        "zero_tolerance_categories": required["zero_tolerance_categories"], "sealed": True,
        "validation_scope": "Local schema, provenance, overlap and hash checks only; not Azure evidence or a release pass.",
    })
    print(f"Sealed {len(holdout)} new questions without invoking a target or judge. No release result is claimed.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "freeze", "seal"))
    args = parser.parse_args()
    if LANGUAGE != "en":
        parser.error("Select FOUNDRY_LAB_LANGUAGE=en; Korean datasets and runtime defaults are preserved.")
    {"prepare": prepare, "freeze": freeze, "seal": seal}[args.command]()


if __name__ == "__main__":
    main()
