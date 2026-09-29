"""Small keyless Azure transport shared by the optional live labs."""

from __future__ import annotations

from contextlib import contextmanager
import json
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from evidence import Budget, Evidence
from workshop import config_values, read_config


def credential():
    from azure.identity import AzureCliCredential, ManagedIdentityCredential

    values = config_values()
    mode = values["FOUNDRY_AUTH_MODE"] or "cli"
    if mode == "cli":
        return AzureCliCredential(process_timeout=30)
    if mode == "managed_identity":
        client_id = values["FOUNDRY_MANAGED_IDENTITY_CLIENT_ID"]
        return ManagedIdentityCredential(**({"client_id": client_id} if client_id else {}))
    raise ValueError("FOUNDRY_AUTH_MODE must be cli or managed_identity.")


@contextmanager
def project_client(evidence: Evidence | None = None):
    from azure.ai.projects import AIProjectClient
    from azure.core.exceptions import AzureError
    from openai import OpenAIError

    endpoint, model = read_config()
    try:
        with credential() as cred, AIProjectClient(
            endpoint=endpoint, credential=cred, retry_total=0,
            connection_timeout=15, read_timeout=60,
        ) as project:
            yield project, cred, endpoint, model
    except (AzureError, OpenAIError) as exc:
        if evidence is not None:
            evidence.failure(exc)
        raise


def azure_url(value: str, suffix: str) -> str:
    parsed = urlparse(value)
    if (
        parsed.scheme != "https" or not parsed.hostname or not parsed.hostname.endswith(suffix)
        or parsed.username or parsed.password or parsed.port or parsed.query or parsed.fragment
    ):
        raise ValueError(f"Expected a credential-free HTTPS Azure endpoint ending in {suffix}.")
    return value.rstrip("/")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError("Redirect refused: never forward Azure bearer credentials to another endpoint.")


class Rest:
    def __init__(self, endpoint: str, cred: Any, audience: str, evidence: Evidence, budget: Budget):
        self.endpoint, self.cred, self.audience = endpoint.rstrip("/"), cred, audience
        self.evidence, self.budget = evidence, budget
        self.opener = build_opener(NoRedirect)

    def request(self, method: str, path: str, body: Any = None, *, create_only: bool = False) -> Any:
        if not path.startswith("/") or path.startswith("//") or ".." in path:
            raise ValueError("REST path must be relative and cannot traverse endpoints.")
        self.budget.before_request()
        data = None if body is None else json.dumps(body, ensure_ascii=False, allow_nan=False).encode()
        headers = {
            "Authorization": f"Bearer {self.cred.get_token(self.audience).token}",
            "Content-Type": "application/json", "Accept": "application/json",
        }
        if create_only:
            headers["If-None-Match"] = "*"
        req = Request(self.endpoint + path, data=data, headers=headers, method=method)
        try:
            with self.opener.open(req, timeout=60) as response:
                raw = response.read(4_000_001)
                if len(raw) > 4_000_000:
                    raise RuntimeError("Response exceeded the four-megabyte evidence limit.")
                value = json.loads(raw) if raw else None
                self.evidence.append("http", {
                    "method": method, "path": path, "status": response.status,
                    "request_id": response.headers.get("x-ms-request-id") or response.headers.get("apim-request-id"),
                    "body": value,
                })
                return value
        except HTTPError as exc:
            raw = exc.read(4_000_000).decode("utf-8", errors="replace")
            self.evidence.append("http_failed", {"method": method, "path": path, "status": exc.code, "body": raw})
            raise RuntimeError(f"HTTP {exc.code} from {urlparse(self.endpoint).hostname}; see {self.evidence.path.name}") from exc
