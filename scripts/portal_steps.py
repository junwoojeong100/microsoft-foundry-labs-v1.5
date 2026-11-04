"""Validate reviewed instructional stills derived from the genuine portal videos."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re
import struct

import portal_recordings

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "portal-steps.json"
DIRECTORY = Path("assets/portal/steps")


def regular_file(relative: Path) -> Path:
    path = ROOT / relative
    if not path.is_file() or any(
        part.is_symlink() for part in (path, *path.parents) if part.is_relative_to(ROOT)
    ):
        raise ValueError(f"Missing or nonregular portal step asset: {relative}")
    return path


def load_steps() -> list[dict]:
    manifest = json.loads(regular_file(Path("content") / MANIFEST).read_text(encoding="utf-8"))
    if (
        manifest.get("capture_method") != "ffmpeg-video-frame"
        or manifest.get("synthetic_ui") is not False
        or manifest.get("execution_language") != "ko"
        or manifest.get("recording_manifest") != "portal-recordings.json"
    ):
        raise ValueError("Portal steps must identify genuine Korean-run source footage.")
    frames = manifest["frames"]
    review = manifest.get("privacy_review", {})
    if (
        review.get("status") != "passed" or review.get("images") != len(frames)
        or review.get("ocr") != "passed" or review.get("visual") != "passed"
        or review.get("flags") != 0
    ):
        raise ValueError("Every portal step image needs completed OCR and visual privacy review.")
    recordings, _ = portal_recordings.load_recordings()
    clips = {clip["id"]: clip for clip in recordings["clips"]}
    identifiers = [frame["id"] for frame in frames]
    if not identifiers or len(identifiers) != len(set(identifiers)):
        raise ValueError("Portal step identifiers must be nonempty and distinct.")
    for frame in frames:
        identifier = frame["id"]
        relative = Path(frame["path"])
        if (
            not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", identifier)
            or relative != DIRECTORY / f"{identifier}.png"
        ):
            raise ValueError(f"Portal step must use a safe, scoped PNG path: {identifier}")
        clip = clips.get(frame["clip"])
        if clip is None or frame["source_sha256"] != clip["sha256"]["mp4"]:
            raise ValueError(f"Portal step source video/hash mismatch: {identifier}")
        seconds = frame["seconds"]
        if (
            type(seconds) not in (int, float) or not math.isfinite(seconds)
            or not 0 <= seconds < clip["seconds"]
            or abs(seconds * clip["fps"] - round(seconds * clip["fps"])) > 1e-6
        ):
            raise ValueError(f"Portal step needs an exact in-range source frame: {identifier}")
        crop = frame["crop_xywh"]
        if (
            not isinstance(crop, list) or len(crop) != 4
            or any(type(value) is not int for value in crop)
            or min(crop[:2]) < 0 or min(crop[2:]) <= 0
            or crop[0] + crop[2] > clip["width"]
            or crop[1] + crop[3] > clip["height"]
        ):
            raise ValueError(f"Portal step crop escapes its source frame: {identifier}")
        padding = frame["padding_ltrb"]
        if (
            not isinstance(padding, list) or len(padding) != 4
            or any(type(value) is not int or not 0 <= value <= 64 for value in padding)
        ):
            raise ValueError(f"Invalid portal step annotation padding: {identifier}")
        data = regular_file(relative).read_bytes()
        if (
            len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n"
            or hashlib.sha256(data).hexdigest() != frame["sha256"]
        ):
            raise ValueError(f"Portal step PNG signature/hash mismatch: {identifier}")
        width, height = struct.unpack(">II", data[16:24])
        if (
            width != crop[2] + padding[0] + padding[2]
            or height != crop[3] + padding[1] + padding[3]
        ):
            raise ValueError(f"Portal step dimensions differ from its crop: {identifier}")
        markers = frame["markers"]
        if (
            not 1 <= len(markers) <= 3
            or [marker["number"] for marker in markers] != list(range(1, len(markers) + 1))
            or any(
                type(marker[axis]) is not int or not 0 <= marker[axis] < maximum
                for marker in markers for axis, maximum in (("x", width), ("y", height))
            )
        ):
            raise ValueError(f"Portal step markers must be ordered and inside the image: {identifier}")
        frame.update(kind="video-frame", recorded_on=recordings["recorded_on"])
    return frames
