"""Versioned evaluation data. Dev loading never opens the sealed holdout."""

import hashlib
import json
from pathlib import Path
from typing import Any

from evidence import digest
from workshop import DATA, LANGUAGE, ROOT, load_jsonl, validate_data

DEFAULT_SUITE = "automated-v5" if LANGUAGE == "en" else "automated-v3"
FROZEN_SUITES = ("automated-v4", "automated-v5")
SUITES = ("legacy-v1", "basic-learning", "automated-v2", "automated-v3") + (
    FROZEN_SUITES if LANGUAGE == "en" else ()
)
V2 = DATA / "evaluation/v2"


def suite_dir(suite: str) -> Path:
    if suite not in SUITES or suite == "legacy-v1":
        raise ValueError("Expected a versioned automated suite.")
    return DATA / "evaluation" / suite.removeprefix("automated-")


def policy(suite: str = DEFAULT_SUITE) -> dict[str, Any]:
    if suite not in SUITES:
        raise ValueError("Unknown evaluation suite.")
    if suite == "basic-learning":
        return json.loads((DATA / "evaluation/basic-learning.json").read_text(encoding="utf-8"))
    path = DATA / "evaluation/rubric.json" if suite == "legacy-v1" else suite_dir(suite) / "rubric.json"
    return json.loads(path.read_text(encoding="utf-8"))


def verify_development_freeze(suite: str, *, root: Path = ROOT) -> dict:
    if suite not in FROZEN_SUITES or LANGUAGE != "en":
        raise ValueError("A runtime-bound development freeze requires an English frozen suite.")
    freeze_path = root / "data/en/evaluation" / suite.removeprefix("automated-") / "development-freeze.json"
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    if (freeze.get("schema") != "contoso-development-freeze-v2" or freeze.get("suite") != suite
            or freeze.get("language") != "en" or not freeze.get("files")):
        raise ValueError("Invalid development freeze; do not open or reseal the holdout.")
    for name, expected in freeze["files"].items():
        path = root / name
        if (not path.resolve().is_relative_to(root.resolve()) or path.is_symlink() or not path.is_file()
                or hashlib.sha256(path.read_bytes()).hexdigest() != expected):
            raise ValueError(f"Frozen development input changed: {name}. Use a new experiment, not a holdout rewrite.")
    return freeze


def validate_cases(values: list[dict], selected: str, required: dict) -> None:
    if len(values) != required[f"required_{selected}_cases"]:
        raise ValueError(f"Incomplete {selected} dataset.")
    for row in values:
        if row.get("split") != selected or row.get("category") not in {
            "policy", "approval", "tool", "abstention", "clarification", "validation", "safety", "access"
        }:
            raise ValueError("Invalid split or category.")
        for field in ("id", "scenario", "query", "ground_truth", "expected_behavior", "context"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"Case field {field} must be a nonempty string.")
        for field in ("required_citations", "required_tools", "forbidden_tools"):
            if not isinstance(row.get(field), list) or any(not isinstance(x, str) for x in row[field]):
                raise ValueError(f"Case field {field} must be an explicit string list.")
        groups = row.get("required_citation_groups", [])
        if not isinstance(groups, list) or any(
            not isinstance(group, list) or not group or any(not isinstance(x, str) for x in group) for group in groups
        ):
            raise ValueError("Citation equivalence groups must be explicit nonempty source-ID lists.")


def load_cases(suite: str = DEFAULT_SUITE, split: str | None = None) -> list[dict]:
    if suite not in SUITES or split not in {None, "dev", "holdout"}:
        raise ValueError("Use a supported suite and dev/holdout split.")
    if suite == "basic-learning":
        if split == "holdout":
            raise ValueError("The basic learning path has no release holdout; use an automated suite after Hosted preparation.")
        return [row for row in validate_data() if row["split"] == "dev"]
    if suite == "legacy-v1":
        return [row for row in validate_data() if split is None or row["split"] == split]
    required = policy(suite)
    directory = suite_dir(suite)
    splits = ("dev", "holdout") if split is None else (split,)
    rows = []
    for selected in splits:
        path = directory / (selected + ".jsonl")
        if selected == "holdout":
            manifest = json.loads((directory / "holdout-manifest.json").read_text())
            if suite in FROZEN_SUITES:
                verify_development_freeze(suite)
                if manifest.get("development_freeze", {}).get("sha256") != hashlib.sha256(
                    (directory / "development-freeze.json").read_bytes()
                ).hexdigest():
                    raise ValueError("Holdout does not match the frozen development inputs.")
            if not manifest.get("sealed") or manifest["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
                raise ValueError("Sealed holdout checksum mismatch.")
        values = load_jsonl(path)
        validate_cases(values, selected, required)
        rows.extend(values)
    if len({row["id"] for row in rows}) != len(rows) or len({row["scenario"] for row in rows}) != len(rows):
        raise ValueError("Duplicate case IDs/scenarios or scenario overlap across splits.")
    return rows


def calibration_cases(suite: str = DEFAULT_SUITE) -> list[dict]:
    if suite not in SUITES:
        raise ValueError("Unknown evaluation suite.")
    path = DATA / "evaluation/calibration.jsonl" if suite in {"legacy-v1", "basic-learning"} else suite_dir(suite) / "calibration.jsonl"
    values = load_jsonl(path)
    if any(type(row.get("expected_pass")) is not bool for row in values):
        raise ValueError("Calibration controls require boolean expected verdicts.")
    return values


def suite_hash(suite: str = DEFAULT_SUITE) -> str:
    if suite == "basic-learning":
        return digest({"suite": suite, "cases": load_cases(suite, "dev"), "policy": policy(suite),
                       "calibration": calibration_cases(suite),
                       "judge": hashlib.sha256((DATA / "evaluation/judge.txt").read_bytes()).hexdigest()})
    if suite == "legacy-v1":
        files = ["cases.jsonl", "rubric.json", "calibration.jsonl", "judge.txt"]
        return digest({name: hashlib.sha256((DATA / "evaluation" / name).read_bytes()).hexdigest() for name in files})
    directory = suite_dir(suite)
    manifest = json.loads((directory / "holdout-manifest.json").read_text())
    identity = {
        "suite": suite, "dev": hashlib.sha256((directory / "dev.jsonl").read_bytes()).hexdigest(),
        "holdout": manifest["sha256"], "policy": policy(suite),
        "calibration": hashlib.sha256((directory / "calibration.jsonl").read_bytes()).hexdigest(),
        "judge": hashlib.sha256((DATA / "evaluation/judge.txt").read_bytes()).hexdigest(),
    }
    if suite in FROZEN_SUITES:
        identity["development_freeze"] = hashlib.sha256((directory / "development-freeze.json").read_bytes()).hexdigest()
    return digest(identity)
