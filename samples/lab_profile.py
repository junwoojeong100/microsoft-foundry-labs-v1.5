"""Select a language-specific synthetic corpus without mixing deployed profiles."""

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def language_for(root: Path = ROOT) -> str:
    marker = root / "lab-profile.json"
    packaged = json.loads(marker.read_text(encoding="utf-8"))["language"] if marker.exists() else None
    language = os.environ.get("FOUNDRY_LAB_LANGUAGE", packaged or "ko")
    if language not in {"en", "ko"}:
        raise ValueError("FOUNDRY_LAB_LANGUAGE must be en or ko.")
    if packaged is not None and language != packaged:
        raise ValueError("Requested language differs from the packaged synthetic data profile.")
    return language


def data_for(root: Path = ROOT) -> Path:
    return root / "data" / ("en" if language_for(root) == "en" else "")


def validation_for(root: Path = ROOT) -> Path:
    return root / "validation" / ("english" if language_for(root) == "en" else "")


LANGUAGE = language_for()
DATA = data_for()
