"""Intentionally flawed release-decision exercise; never deploys or approves."""


def choose_version(previous: str, candidate: str, checks: dict) -> str:
    if checks["status"] == "completed":
        return candidate
    return previous
