"""One-shot result originals that stay retryable when the run failed before any Azure change."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import os
from pathlib import Path
import sys


class Attempt:
    """Tracks whether this call created the original and whether Azure was already changed."""

    def __init__(self) -> None:
        self.created = False
        self.side_effects = False


def open_original(output: Path, attempt: Attempt) -> int:
    """Create the original exclusively (never overwrite) and remember that this call created it."""
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    attempt.created = True
    return descriptor


def archive_unused(output: Path) -> Path:
    """Keep the failed attempt as evidence, but free the canonical path for a clean rerun."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = output.with_name(f"{output.stem}.failed-{stamp}{output.suffix}")
    output.rename(target)
    return target


@contextmanager
def retryable_original(output: Path):
    """Archive the original when this call created it and failed before any Azure change.

    Set `attempt.side_effects = True` immediately before the first operation that changes Azure.
    After that point the original stays in place: inspect it instead of rerunning.
    """
    attempt = Attempt()
    try:
        yield attempt
    except BaseException:
        if attempt.created and not attempt.side_effects and output.exists():
            archived = archive_unused(output)
            print(
                f"No Azure change was made. The failed attempt was kept as {archived.name}; "
                "fix the cause and run the same command again.",
                file=sys.stderr,
            )
        raise
