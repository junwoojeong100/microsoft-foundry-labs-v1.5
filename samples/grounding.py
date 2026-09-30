"""Strict citation selection over actual retrieved sources, never guessed references."""

import json
import re
from typing import Any
from lab_profile import LANGUAGE


def answer_format(source_ids: list[str]) -> dict[str, Any]:
    if not source_ids:
        raise ValueError("No sources available for a grounded answer.")
    return {
        "format": {
            "type": "json_schema", "name": "contoso_grounded_answer", "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "citation_ids": {"type": "array", "items": {"type": "string", "enum": sorted(source_ids)}},
                    "answer": {"type": "string"},
                },
                "required": ["citation_ids", "answer"], "additionalProperties": False,
            },
        },
    }


def parse_answer(raw: str, sources: dict[str, dict]) -> tuple[str, list[dict]]:
    def unique_fields(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise RuntimeError("Duplicate JSON field in grounded answer.")
            result[key] = value
        return result

    try:
        value = json.loads(raw, object_pairs_hook=unique_fields)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Model did not return the required grounded-answer JSON.") from exc
    if not isinstance(value, dict) or set(value) != {"answer", "citation_ids"}:
        raise RuntimeError("Grounded answer has unexpected or missing fields.")
    answer, ids = value["answer"], value["citation_ids"]
    if not isinstance(answer, str) or not answer.strip():
        raise RuntimeError("Grounded answer text is empty.")
    if not isinstance(ids, list) or not ids or any(not isinstance(item, str) for item in ids):
        raise RuntimeError("At least one model-selected citation is required; no references are filled in automatically.")
    if len(ids) != len(set(ids)) or not set(ids) <= sources.keys():
        raise RuntimeError("Answer cited a source that was never retrieved, or duplicated a citation.")
    mentioned = set(re.findall(r"CONTOSO-(?:PROC|EXP|SEC)-\d{4}-\d{2}-s\d+", answer))
    if not mentioned <= set(ids):
        raise RuntimeError("Inline citations differ from the model's structured citation selection.")
    cited = [{**sources[key], "citation_kind": "model_selected_retrieved_source", "citation_text": key} for key in ids]
    files = set(re.findall(r"[A-Za-z0-9_-]+\.md", answer))
    if not files <= {item["filename"] for item in cited}:
        raise RuntimeError("Answer names a document outside its selected retrieval evidence.")
    english = LANGUAGE == "en"
    references = "; ".join(
        f"{item['filename']} section {item['section']} [{item['id']}]" if english
        else f"{item['filename']} {item['section']}절 [{item['id']}]"
        for item in cited
    )
    return answer.strip() + ("\n\nSources: " if english else "\n\n근거: ") + references, cited


def attribute_answer(raw_answer: str, raw_attribution: str, sources: dict[str, dict]) -> tuple[str, list[dict]]:
    parse_answer(raw_answer, sources)
    value = json.loads(raw_answer)
    attribution = json.loads(raw_attribution)
    if not isinstance(attribution, dict) or set(attribution) != {"citation_ids"}:
        raise RuntimeError("Citation attribution must return only citation_ids.")
    ids = attribution["citation_ids"]
    if not isinstance(ids, list) or any(not isinstance(key, str) for key in ids) or not set(ids) <= sources.keys():
        raise RuntimeError("Attribution selected a source outside actual retrieval.")
    value["citation_ids"] = list(dict.fromkeys([*value["citation_ids"], *ids]))
    return parse_answer(json.dumps(value, ensure_ascii=False), sources)
