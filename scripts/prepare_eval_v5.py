"""Inherit unchanged exposed v4 dev, freeze v5, then seal a separately authored exam."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from evaluation_data import validate_cases, verify_development_freeze
from lab_profile import LANGUAGE
from prepare_eval_v4 import checksum, freeze_paths as previous_freeze_paths, write_consistent, write_json
from search_lab import policy_chunks
from workshop import load_jsonl

SUITE = "automated-v5"
DIRECTORY = ROOT / "data/en/evaluation/v5"
PREVIOUS = ROOT / "data/en/evaluation/v4"


def prepare() -> None:
    source = load_jsonl(PREVIOUS / "dev.jsonl")
    if len(source) != 40 or any(row["split"] != "dev" for row in source):
        raise ValueError("Inherit all 40 exposed v4 dev cases, never its unused holdout.")
    rows = [{
        **row, "id": f"v5-dev-{index:02}", "split": "dev",
        "origin": {"suite": "automated-v4", "id": row["id"], "original_split": "dev",
                   "previous_origin": row.get("origin")},
    } for index, row in enumerate(source, 1)]
    write_consistent(DIRECTORY / "dev.jsonl", "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))
    write_consistent(DIRECTORY / "calibration.jsonl", (PREVIOUS / "calibration.jsonl").read_text(encoding="utf-8"))
    rubric = json.loads((PREVIOUS / "rubric.json").read_text())
    write_json(DIRECTORY / "rubric.json", {
        **rubric, "suite": SUITE,
        "description": "English explicit-request-v2 candidate: unchanged exposed v4 dev and a new independent final holdout.",
        "legacy_evidence": "All v3/v4 failures, original freezes, gates and judge controls remain unchanged.",
    })
    print("Prepared 40 unchanged v4 dev regressions and 8 unchanged controls; no unused holdout was opened.")


def freeze_paths() -> list[Path]:
    return sorted({
        *[path for path in previous_freeze_paths() if not path.is_relative_to(PREVIOUS)],
        *[DIRECTORY / name for name in ("dev.jsonl", "calibration.jsonl", "rubric.json")],
        ROOT / "samples/optimizer_lab.py", ROOT / "scripts/prepare_eval_v5.py",
        ROOT / "scripts/prepare_eval_v4.py", ROOT / "scripts/share_evidence.py",
        ROOT / "scripts/ci_live.py", ROOT / "azure.yaml",
        ROOT / ".github/workflows/azure-validation.yml",
    })


def freeze() -> None:
    if (DIRECTORY / "development-freeze.json").exists():
        verify_development_freeze(SUITE)
        print("Existing v5 freeze verified; nothing was overwritten.")
        return
    if any((DIRECTORY / name).exists() for name in ("holdout.jsonl", "holdout-manifest.json")):
        raise ValueError("Development must freeze before independent holdout authoring.")
    validate_cases(load_jsonl(DIRECTORY / "dev.jsonl"), "dev", json.loads((DIRECTORY / "rubric.json").read_text()))
    frozen = {
        "schema": "contoso-development-freeze-v2", "suite": SUITE, "language": "en",
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "tool_authorization_contract": "explicit-request-v2",
        "files": {path.relative_to(ROOT).as_posix(): checksum(path) for path in freeze_paths()},
        "final_holdout_exists_at_freeze": False,
        "validation_scope": "Local source freeze only; not Azure quality evidence.",
    }
    write_json(DIRECTORY / "development-freeze.json", frozen)
    target = ROOT / "validation/english/automated-v5/source-snapshot.zip"
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "x", zipfile.ZIP_DEFLATED) as archive:
        for name in [*frozen["files"], "data/en/evaluation/v5/development-freeze.json"]:
            archive.write(ROOT / name, name)
    print(f"Frozen {len(frozen['files'])} v5 inputs before independent exam authoring; archive {checksum(target)}.")


def seal() -> None:
    frozen = verify_development_freeze(SUITE)
    manifest = DIRECTORY / "holdout-manifest.json"
    if manifest.exists():
        raise ValueError("The independent holdout is already sealed; never reseal or replace it.")
    required = json.loads((DIRECTORY / "rubric.json").read_text())
    holdout = load_jsonl(DIRECTORY / "holdout.jsonl")
    validate_cases(holdout, "holdout", required)
    dev = load_jsonl(DIRECTORY / "dev.jsonl")
    for key in ("id", "scenario", "query"):
        values = [row[key].strip().casefold() for row in [*dev, *holdout]]
        if len(values) != len(set(values)):
            raise ValueError(f"Independent holdout duplicates a {key}.")
    sources = {row["id"] for row in policy_chunks()}
    for row in holdout:
        citations = set(row["required_citations"]) | {
            source for group in row.get("required_citation_groups", []) for source in group
        }
        if not citations <= sources:
            raise ValueError("Independent holdout cites an unknown policy source.")
        tools = set(row["required_tools"] + row["forbidden_tools"])
        if (set(row["required_tools"]) & set(row["forbidden_tools"])
                or not tools <= {"get_stock", "prepare_purchase_request"}):
            raise ValueError("Conflicting or unknown holdout tool constraints.")
    write_json(manifest, {
        "schema": "contoso-evaluation-manifest-v5", "suite": SUITE, "language": "en",
        "rows": len(holdout), "sha256": checksum(DIRECTORY / "holdout.jsonl"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "development_freeze": {
            "path": "data/en/evaluation/v5/development-freeze.json",
            "sha256": checksum(DIRECTORY / "development-freeze.json"), "frozen_at": frozen["frozen_at"],
        },
        "authoring_method": "Separate authoring context after development freeze; synthetic policy/inventory only; no v4 holdout or target inference.",
        "release_use": "independent_final_holdout", "release_status": "sealed_unexecuted",
        "minimum_pass_rate": required["minimum_pass_rate"],
        "native_pass_threshold": required["native_pass_threshold"],
        "zero_tolerance_categories": required["zero_tolerance_categories"], "sealed": True,
        "validation_scope": "Local schema, source, overlap and seal checks; not Azure evidence.",
    })
    print(f"Sealed {len(holdout)} independent v5 cases; questions are not printed or submitted.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "freeze", "seal"))
    args = parser.parse_args()
    if LANGUAGE != "en":
        parser.error("Select FOUNDRY_LAB_LANGUAGE=en; Korean defaults remain unchanged.")
    {"prepare": prepare, "freeze": freeze, "seal": seal}[args.command]()
