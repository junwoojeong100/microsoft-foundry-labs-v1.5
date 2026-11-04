"""Generate browser-uploadable learning files from unchanged canonical sources."""

import csv
import io
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from policy_documents import policy_chunks


def csv_bytes(fields, rows):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def inputs(language):
    data = ROOT / ("data/en" if language == "en" else "data")
    comparison = json.loads((data / "evaluation/instruction-comparison.json").read_text(encoding="utf-8"))
    cases = comparison["cases"]
    if len(cases) != 12 or len({row["id"] for row in cases}) != 12:
        raise ValueError("Portal comparison requires the twelve fixed, unique development questions.")
    files = {f"policies/{path.name}": path.read_bytes() for path in sorted((data / "policies").glob("*.md"))}
    context = json.dumps({
        "grounding_context": policy_chunks(data, language),
        "context_kind": "supplied_synthetic_documents_not_a_tool_execution",
        "available_tools": [],
    }, ensure_ascii=False, indent=2)
    boundary = (
        "The following synthetic documents are fixed context, not tool execution. Use only their citation IDs."
        if language == "en" else "다음 합성 문서는 고정 문맥이며 도구 실행 결과가 아닙니다. 제공된 인용 ID만 사용합니다."
    )
    for version in ("v1", "v2"):
        instructions = (data / f"prompts/agent-{version}.txt").read_text(encoding="utf-8")
        files[f"agent-{version}-with-context.txt"] = (instructions.rstrip() + "\n\n" + boundary + "\n" + context + "\n").encode("utf-8")
    evaluation_rows = [
        {"case_id": row["id"], "query": row["query"],
         "context": context,
         "ground_truth": "\n".join(check["requirement"] for check in row["checks"])}
        for row in cases
    ]
    files["evaluation-12.jsonl"] = "".join(
        json.dumps(row, ensure_ascii=False) + "\n" for row in evaluation_rows
    ).encode("utf-8")
    files["evaluation-12.csv"] = csv_bytes(("case_id", "query", "context", "ground_truth"), evaluation_rows)
    files["review-checklist.csv"] = csv_bytes(("case_id", "check_id", "requirement", "sources", "critical"), [
        {"case_id": row["id"], "check_id": check["id"], "requirement": check["requirement"],
         "sources": ";".join(check["sources"]), "critical": str(check["critical"]).lower()}
        for row in cases for check in row["checks"]
    ])
    return files


def build():
    directory = ROOT / "downloads/portal-inputs"
    archive_path = ROOT / "downloads/Contoso-Portal-Inputs.zip"
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for language in ("en", "ko"):
            for name, data in sorted(inputs(language).items()):
                path = directory / language / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                info = zipfile.ZipInfo(f"{language}/{name}", (2026, 11, 4, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o644 << 16
                archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


if __name__ == "__main__":
    build()
