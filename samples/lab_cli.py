"""Shared entry-point wrapper: expected learner errors become one `ERROR:` line, not a traceback."""

from __future__ import annotations

import os
import sys
from typing import Callable

EXPECTED = (ValueError, RuntimeError, OSError, TimeoutError, ImportError)


def leaf_exception(error: BaseException) -> BaseException:
    """Return the only real error inside nested ExceptionGroups (task groups wrap the real error)."""
    while isinstance(error, BaseExceptionGroup) and len(error.exceptions) == 1:
        error = error.exceptions[0]
    return error


def service_errors() -> tuple[type[BaseException], ...]:
    found: list[type[BaseException]] = []
    for module, name in (("azure.core.exceptions", "AzureError"), ("openai", "OpenAIError")):
        try:
            found.append(getattr(__import__(module, fromlist=[name]), name))
        except ImportError:
            continue
    return tuple(found)


def run(main: Callable[[], int | None]) -> None:
    """Run a lab entry point and exit. Set FOUNDRY_LAB_DEBUG=1 to see the full traceback."""
    try:
        code = main()
    except KeyboardInterrupt:
        print("Interrupted; no further requests were sent.", file=sys.stderr)
        raise SystemExit(130) from None
    except BaseException as error:
        leaf = leaf_exception(error)
        services = service_errors()
        if os.environ.get("FOUNDRY_LAB_DEBUG") or not isinstance(leaf, EXPECTED + services):
            raise
        print(f"ERROR: {leaf}", file=sys.stderr)
        if services and isinstance(leaf, services):
            print("Hint: the guide's troubleshooting table maps 401/403/404/429 to the first check to make.",
                  file=sys.stderr)
        raise SystemExit(2) from None
    raise SystemExit(code or 0)
