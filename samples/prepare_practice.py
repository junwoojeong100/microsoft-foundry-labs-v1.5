"""Copy an intentionally flawed, Azure-free exercise into a new learner folder."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
LABS = ("governance", "delivery", "migration")


def prepare(lab: str, output: Path, *, root: Path = ROOT) -> Path:
    if lab not in LABS:
        raise ValueError("Choose governance, delivery, or migration.")
    root = root.resolve()
    destination = (root / output).resolve()
    if not any(destination.is_relative_to(root / name) and destination != root / name
               for name in ("results", "practice")):
        raise ValueError("Use a new subfolder under results/ or practice/; never the repository root.")
    if destination.exists():
        raise FileExistsError("The exercise folder already exists; preserve your work and choose another.")
    source = root / "data/exercises" / lab
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lab", choices=LABS)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    destination = prepare(args.lab, args.output)
    print(f"Prepared {args.lab}: {destination.relative_to(ROOT)}")
    print("LOCAL EXERCISE ONLY: the initial tests intentionally fail. Edit exercise.py, not the tests.")
    print("No Azure calls, permissions, deployments, or actual release approvals.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
