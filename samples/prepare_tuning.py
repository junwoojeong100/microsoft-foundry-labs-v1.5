"""Generate small synthetic SFT format exercises; never submits training jobs."""

import json
from pathlib import Path
from uuid import uuid4
from lab_profile import DATA, LANGUAGE

ROOT = Path(__file__).resolve().parents[1]
SYSTEM = (
    "Classify the request as exactly one of POLICY, STOCK, DRAFT, or CLARIFY."
    if LANGUAGE == "en" else "문의 유형을 POLICY, STOCK, DRAFT, CLARIFY 중 하나로만 분류한다."
)


def prepare(destination: Path) -> tuple[int, int]:
    examples = json.loads((DATA / "tuning/examples.json").read_text(encoding="utf-8"))
    seen: set[str] = set()
    grouped: dict[str, list[dict]] = {"train": [], "validation": []}
    for example in examples:
        query = example["query"].strip()
        if not query or query in seen:
            raise ValueError("Empty or duplicated tuning input.")
        seen.add(query)
        if example["label"] not in {"POLICY", "STOCK", "DRAFT", "CLARIFY"}:
            raise ValueError("Unrecognized training label.")
        if example["split"] not in grouped:
            raise ValueError("Unrecognized split.")
        grouped[example["split"]].append({"messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": query},
            {"role": "assistant", "content": example["label"]},
        ]})
    if len(grouped["train"]) < 10 or not grouped["validation"]:
        raise ValueError("Need at least 10 training examples and separate validation data.")
    destination.mkdir(parents=True, exist_ok=False)
    for split, rows in grouped.items():
        with (destination / f"{split}.jsonl").open("x", encoding="utf-8-sig") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return len(grouped["train"]), len(grouped["validation"])


if __name__ == "__main__":
    target = ROOT / "results" / f"tuning-{uuid4().hex[:12]}"
    counts = prepare(target)
    print(f"Prepared train={counts[0]}, validation={counts[1]} in {target.relative_to(ROOT)}.")
    print("Synthetic FORMAT EXERCISE ONLY. No training job or cloud request was made.")
