"""Bounded, append-only execution evidence. No credentials or answer-key fallbacks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import time
from typing import Any
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def serializable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "as_dict"):
        return value.as_dict()
    if isinstance(value, dict):
        return {key: serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serializable(item) for item in value]
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def redacted(value: Any) -> Any:
    value = serializable(value)
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if re.search(
                r"^(authorization|access_token|refresh_token|api[_-]?key|client_secret|connection_string|headers)$", key, re.I
            ) else redacted(item) for key, item in value.items()
        }
    if isinstance(value, list):
        return [redacted(item) for item in value]
    if isinstance(value, str):
        value = re.sub(r"(?i)Bearer\s+[A-Za-z0-9._~+/-]+=*", "Bearer [REDACTED]", value)
        value = re.sub(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b", "[REDACTED JWT]", value)
        return re.sub(r"(?i)(InstrumentationKey|AccountKey|SharedAccessSignature)=[^;\s]+", r"\1=[REDACTED]", value)
    return value


def runtime_contract(prompt: Path | None = None, *, root: Path = ROOT) -> dict[str, Any]:
    prompt = prompt or root / "data/prompts/agent-v4.txt"
    files = [
        *sorted((root / "data/policies").glob("*.md")),
        root / "data/inventory.csv", prompt,
        *[root / "samples" / name for name in ("workshop.py", "evidence.py", "cloud.py", "search_lab.py", "hosted_runtime.py")],
    ]
    hashes = {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    entrypoint = root / "hosted/main.py" if (root / "hosted/main.py").exists() else root / "main.py"
    hashes["host_entrypoint"] = hashlib.sha256(entrypoint.read_bytes()).hexdigest()
    responses_entry = root / "hosted/responses_main.py" if (root / "hosted/responses_main.py").exists() else root / "responses_main.py"
    if responses_entry.exists():
        hashes["responses_entrypoint"] = hashlib.sha256(responses_entry.read_bytes()).hexdigest()
    baseline = root / ".agent_configs/baseline"
    if baseline.exists():
        for path in sorted(baseline.iterdir()):
            if path.is_file():
                hashes[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    pins = set()
    for name in ("requirements.txt", "requirements-hosted.txt"):
        pins.update(line.strip() for line in (root / name).read_text().splitlines() if "==" in line and not line.startswith("#"))
    hashes["dependency_pins"] = digest(sorted(pins))
    return {"schema": "contoso-runtime-v1", "sha256": digest(hashes), "files": hashes}


@dataclass
class Budget:
    max_requests: int = 60
    max_tokens: int = 150_000
    max_seconds: int = 900
    requests: int = 0
    tokens: int = 0
    started: float = 0.0

    def __post_init__(self) -> None:
        if any(type(v) is not int or v <= 0 for v in (self.max_requests, self.max_tokens, self.max_seconds)):
            raise ValueError("Budget limits must be positive integers.")
        self.started = time.monotonic()

    def before_request(self, token_reservation: int = 0) -> None:
        if (
            self.requests >= self.max_requests
            or self.tokens + token_reservation > self.max_tokens
            or time.monotonic() - self.started >= self.max_seconds
        ):
            raise RuntimeError("Execution budget exhausted; no further request was sent.")
        self.requests += 1

    def record_tokens(self, count: int) -> None:
        if type(count) is not int or count < 0:
            raise ValueError("Actual token usage must be a non-negative integer.")
        self.tokens += count


class Evidence:
    def __init__(self, operation: str, *, root: Path | None = None) -> None:
        if not re.fullmatch(r"[a-z0-9-]+", operation):
            raise ValueError("Invalid operation label.")
        if root is None:
            if os.environ.get("FOUNDRY_AUTH_MODE") == "managed_identity":
                root = Path.home() / ".contoso/evidence"
            else:
                root = Path(os.environ.get("CONTOSO_EVIDENCE_DIRECTORY", str(ROOT / "results")))
        self.run_id = f"contoso-{operation}-{uuid4().hex[:12]}"
        self.path = root / (self.run_id + ".jsonl")
        root.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(descriptor)
        self.append("started", {"operation": operation, "synthetic": True})

    def append(self, event: str, payload: Any) -> None:
        record = {
            "run_id": self.run_id, "at": datetime.now(timezone.utc).isoformat(),
            "event": event, "payload": redacted(payload),
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
            handle.flush()

    def failure(self, error: Exception) -> None:
        self.append("failed", {"type": type(error).__name__, "message": str(error)})
