"""Add every exposed v2 holdout case to development; preserve all prior datasets."""

import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from workshop import DATA, load_jsonl
from prepare_eval_v2 import write_new


def main():
    v2 = DATA / "evaluation/v2"
    v3 = DATA / "evaluation/v3"
    source = load_jsonl(v2 / "dev.jsonl") + load_jsonl(v2 / "holdout.jsonl")
    rows = []
    for number, row in enumerate(source, 1):
        rows.append({**row, "id": f"v3-dev-{number:02}", "split": "dev",
                     "origin": {"suite": "automated-v2", "id": row["id"], "original_split": row["split"]}})
    write_new(v3 / "dev.jsonl", rows)
    target = v3 / "calibration.jsonl"
    if target.exists() and target.read_bytes() != (v2 / "calibration.jsonl").read_bytes():
        raise ValueError("Existing v3 calibration differs; no overwrite.")
    if not target.exists():
        shutil.copy2(v2 / "calibration.jsonl", target)
    print("Prepared all 30 exposed cases as dev; no v3 holdout content was read.")


if __name__ == "__main__":
    main()
