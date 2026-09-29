"""Export a minimal synthetic response set, excluding personal settings, headers and raw logs."""

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from evidence import redacted
from evaluation_lab import prepare_rows
from workshop import load_jsonl

FIELDS = {
    "id", "query", "status", "response", "response_id", "response_ids", "trace_id",
    "tool_calls", "citations", "retrieved_sources", "context", "model", "model_deployment",
    "input_tokens", "output_tokens", "latency_seconds", "hosted_version", "contract",
    "effective_prompt_sha256", "manual_pass", "review_note",
    "environment_sha256", "execution_location",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--split", choices=["dev", "holdout"], required=True)
    args = parser.parse_args()
    prepare_rows(args.input, args.split)
    target = ROOT / "validation/current" / (args.split + "-responses.jsonl")
    if target.exists():
        raise ValueError("Shared evidence already exists; preserve it instead of overwriting.")
    rows = [{key: value for key, value in row.items() if key in FIELDS} for row in load_jsonl(args.input)]
    text = "".join(json.dumps(redacted(row), ensure_ascii=False) + "\n" for row in rows)
    if re.search(r"[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text) or any(
        needle in text for needle in ("Bearer ", "InstrumentationKey=", "/Users/")
    ):
        raise ValueError("Evidence requires review before sharing: potential personal/credential text.")
    target.write_text(text, encoding="utf-8")
    print(f"Exported {len(rows)} synthetic {args.split} responses to {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
