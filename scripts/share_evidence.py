"""Export a minimal synthetic response set, excluding personal settings, headers and raw logs."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from evidence import digest, redacted
from evaluation_lab import prepare_rows, verify_gate
from evaluation_data import DEFAULT_SUITE, SUITES
from lab_profile import validation_for
from workshop import load_jsonl

FIELDS = {
    "id", "query", "status", "response", "response_id", "response_ids", "trace_id",
    "tool_calls", "citations", "retrieved_sources", "context", "model", "model_deployment",
    "input_tokens", "output_tokens", "latency_seconds", "hosted_version", "contract",
    "effective_prompt_sha256", "manual_pass", "review_note",
    "environment_sha256", "execution_location",
    "raw_answer", "grounding_contract", "human_review_status", "evaluation_suite", "evaluation_suite_sha256",
    "tool_definitions",
    "raw_attribution", "attribution_response_id",
    "tool_authorization_contract", "request_permissions", "required_policy_citations",
}


def write_shared(target: Path, value: dict) -> None:
    text = json.dumps(redacted(value), ensure_ascii=False, indent=2) + "\n"
    if re.search(r"[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text) or any(
        needle in text for needle in ("Bearer ", "InstrumentationKey=", "/Users/")
    ):
        raise ValueError("Gate evidence contains potential personal/credential text; no export was written.")
    with target.open("x", encoding="utf-8") as handle:
        handle.write(text)


def export_gate(suite: str, stage: str) -> None:
    receipt = verify_gate(suite, stage)
    folder = validation_for(ROOT) / suite
    folder.mkdir(parents=True, exist_ok=True)
    native = json.loads((ROOT / receipt["native_path"]).read_text(encoding="utf-8"))
    shared = redacted({
        **{key: native[key] for key in ("eval_id", "run_id", "status", "result_counts", "error", "timed_out")},
        "items": [{key: item[key] for key in ("datasource_item", "results") if key in item}
                  for item in native["items"]],
    })
    native_path = folder / f"native-{stage}.json"
    gate = {**receipt, "native_path": native_path.relative_to(ROOT).as_posix(), "native_sha256": digest(shared)}
    if stage == "dev":
        source = folder / "dev-responses.jsonl"
        prepare_rows(source, "dev", suite)
        gate.update(input_path=source.relative_to(ROOT).as_posix(),
                    input_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    write_shared(native_path, shared)
    write_shared(folder / f"{stage}-gate.json", gate)
    if stage == "calibration":
        state = json.loads((ROOT / "results" / f"native-evaluation-{suite}.json").read_text())
        binding = {key: state[key] for key in (
            "judge", "suite", "settings_hash", "evaluator_name", "evaluator_version", "definition_hash", "eval_id", "criteria",
        )}
        write_shared(folder / "evaluation-binding.json", {**binding, "environment_sha256": receipt["environment_sha256"]})
    print(f"Exported verified {stage} originals and gate to {folder.relative_to(ROOT)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--split", choices=["dev", "holdout"])
    parser.add_argument("--suite", choices=SUITES, default=DEFAULT_SUITE)
    parser.add_argument("--gate", choices=["calibration", "dev"], help="Export a verified v5 gate and its native originals.")
    args = parser.parse_args()
    if args.gate:
        if args.input or args.split:
            parser.error("--gate cannot be combined with --input or --split.")
        export_gate(args.suite, args.gate)
        return
    if not args.input or not args.split:
        parser.error("Response export requires --input and --split.")
    prepare_rows(args.input, args.split, args.suite)
    folder = validation_for(ROOT) / ("current" if args.suite == "legacy-v1" else args.suite)
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / (args.split + "-responses.jsonl")
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
