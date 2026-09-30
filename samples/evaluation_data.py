"""Versioned evaluation data. Dev loading never opens the sealed holdout."""

import hashlib
import json
from pathlib import Path
from typing import Any

from evidence import digest
from workshop import DATA, load_jsonl, validate_data

DEFAULT_SUITE = "automated-v2"
SUITES = ("legacy-v1", DEFAULT_SUITE)
V2 = DATA / "evaluation/v2"


def policy(suite: str = DEFAULT_SUITE) -> dict[str, Any]:
    if suite not in SUITES:
        raise ValueError("Unknown evaluation suite.")
    path = DATA / "evaluation/rubric.json" if suite == "legacy-v1" else V2 / "rubric.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_cases(suite: str = DEFAULT_SUITE, split: str | None = None) -> list[dict]:
    if suite not in SUITES or split not in {None, "dev", "holdout"}:
        raise ValueError("Use a supported suite and dev/holdout split.")
    if suite == "legacy-v1":
        return [row for row in validate_data() if split is None or row["split"] == split]
    required = policy(suite)
    splits = ("dev", "holdout") if split is None else (split,)
    rows = []
    for selected in splits:
        path = V2 / (selected + ".jsonl")
        if selected == "holdout":
            manifest = json.loads((V2 / "holdout-manifest.json").read_text())
            if not manifest.get("sealed") or manifest["sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
                raise ValueError("Sealed holdout checksum mismatch.")
        values = load_jsonl(path)
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
        rows.extend(values)
    if len({row["id"] for row in rows}) != len(rows) or len({row["scenario"] for row in rows}) != len(rows):
        raise ValueError("Duplicate case IDs/scenarios or scenario overlap across splits.")
    return rows


def calibration_cases(suite: str = DEFAULT_SUITE) -> list[dict]:
    if suite not in SUITES:
        raise ValueError("Unknown evaluation suite.")
    path = DATA / "evaluation/calibration.jsonl" if suite == "legacy-v1" else V2 / "calibration.jsonl"
    values = load_jsonl(path)
    if any(type(row.get("expected_pass")) is not bool for row in values):
        raise ValueError("Calibration controls require boolean expected verdicts.")
    return values


def suite_hash(suite: str = DEFAULT_SUITE) -> str:
    if suite == "legacy-v1":
        files = ["cases.jsonl", "rubric.json", "calibration.jsonl", "judge.txt"]
        return digest({name: hashlib.sha256((DATA / "evaluation" / name).read_bytes()).hexdigest() for name in files})
    manifest = json.loads((V2 / "holdout-manifest.json").read_text())
    return digest({
        "suite": suite, "dev": hashlib.sha256((V2 / "dev.jsonl").read_bytes()).hexdigest(),
        "holdout": manifest["sha256"], "policy": policy(suite),
        "calibration": hashlib.sha256((V2 / "calibration.jsonl").read_bytes()).hexdigest(),
        "judge": hashlib.sha256((DATA / "evaluation/judge.txt").read_bytes()).hexdigest(),
    })
