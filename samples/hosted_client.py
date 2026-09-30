"""Invoke the bundled local/remote agent and preserve evidence; never delete sessions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import time
from urllib.request import Request, urlopen
from urllib.parse import urlencode, urlparse

from cloud import Rest, credential
from evidence import Budget, Evidence, digest
from hosted_runtime import validate_request
from evaluation_data import DEFAULT_SUITE, SUITES, load_cases, suite_hash
from workshop import LANGUAGE, RESULTS, ROOT, read_config, save_json, validate_data


def parse_raw_http(text: str, *, allow_responses_stream: bool = False) -> tuple[dict, dict[str, str]]:
    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith("HTTP/"):
        raise ValueError("azd did not return a raw HTTP response; see original evidence.")
    header, separator, body = normalized.partition("\n\n")
    if not separator:
        raise ValueError("Raw response has no header/body boundary.")
    status = int(header.splitlines()[0].split()[1])
    headers = {}
    for line in header.splitlines()[1:]:
        key, sep, value = line.partition(":")
        if sep:
            headers[key.lower()] = value.strip()
    if status != 200:
        raise RuntimeError(f"Hosted HTTP {status}; response is not a success.")
    if allow_responses_stream and "text/event-stream" in headers.get("content-type", ""):
        completed = []
        for block in body.split("\n\n"):
            data = "\n".join(line[5:].lstrip() for line in block.splitlines() if line.startswith("data:"))
            if not data or data == "[DONE]":
                continue
            event = json.loads(data)
            if event.get("type") in {"response.failed", "response.incomplete", "error"}:
                raise RuntimeError("Responses stream terminated unsuccessfully; original events retained.")
            if event.get("type") == "response.completed":
                completed.append(event["response"])
        if len(completed) != 1 or completed[0].get("status") != "completed":
            raise ValueError("Stream must contain exactly one completed response; deltas alone cannot pass.")
        return completed[0], headers
    return json.loads(body), headers


def expected_contract() -> str:
    manifest = ROOT / ".build/contoso/package-manifest.json"
    return json.loads(manifest.read_text())["runtime_contract"]["sha256"]


def check_response(value: dict, payload: dict) -> None:
    if (
        value.get("status") != "completed" or not value.get("response", "").strip()
        or not value.get("response_id") or value.get("query") != payload["query"]
        or value.get("contract", {}).get("sha256") != expected_contract()
        or not isinstance(value.get("tool_calls"), list)
        or not isinstance(value.get("citations"), list)
    ):
        raise ValueError("Hosted result failed status, lineage, or deployed-package contract checks.")


def azd(*args: str, timeout: int = 360) -> str:
    result = subprocess.run(["azd", *args], cwd=ROOT, capture_output=True, text=True, timeout=timeout, check=False)
    if result.returncode:
        raise RuntimeError(f"azd failed ({result.returncode}): {result.stderr.strip()}\n{result.stdout.strip()}")
    return result.stdout


def remote_invoke(payload: dict, session_id: str, evidence: Evidence) -> dict:
    endpoint, _ = read_config()
    binding = json.loads(azd("ai", "agent", "show", "contoso-purchasing", "--output", "json"))
    target = urlparse(binding["agent_endpoints"]["invocations"])
    project = urlparse(endpoint)
    expected_path = project.path + "/agents/contoso-purchasing/endpoint/protocols/invocations"
    if target.scheme != "https" or target.netloc != project.netloc or target.path != expected_path or target.query != "api-version=v1":
        raise ValueError("Service-returned endpoint is outside the approved project/protocol.")
    path = target.path.removeprefix(project.path) + "?api-version=v1&" + urlencode({"agent_session_id": session_id})
    with credential() as cred:
        rest = Rest(endpoint, cred, "https://ai.azure.com/.default", evidence,
                    Budget(max_requests=1, max_seconds=300))
        return rest.request("POST", path, payload)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["invoke", "evaluate"])
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--live", action="store_true", help="Required even locally: the running agent calls paid Azure services.")
    parser.add_argument("--version", help="Exact remote agent version; never latest.")
    parser.add_argument("--query", default=(
        "Check policy and stock for NB-14, quantity 2, and prepare a purchase request draft only."
        if LANGUAGE == "en" else "NB-14 2대의 정책과 재고를 확인하고 구매 요청 초안만 만들어줘."
    ))
    parser.add_argument("--split", choices=["dev", "holdout"], default="dev")
    parser.add_argument("--case-delay", type=float, default=15.0)
    parser.add_argument("--suite", choices=SUITES, default=DEFAULT_SUITE)
    args = parser.parse_args()
    if not args.live:
        print(f"PLAN ONLY: Hosted {args.command}; local invocation also requires --live.")
        return
    if not args.local and (not args.version or not re.fullmatch(r"[1-9]\d*", args.version)):
        raise ValueError("Remote invocation requires an exact numeric --version.")
    if not 0 <= args.case_delay <= 60:
        raise ValueError("--case-delay must be 0..60 seconds.")
    endpoint, model = read_config()
    if not args.local:
        configured = azd("env", "get-value", "AZURE_AI_PROJECT_ENDPOINT").strip().rstrip("/")
        if configured != endpoint:
            raise ValueError("azd and .env target different projects; invocation refused.")
    environment_sha256 = digest(endpoint)
    evidence = Evidence("hosted-client")
    cases = load_cases(args.suite, args.split) if args.command == "evaluate" else [{"id": "manual-01", "query": args.query}]
    if args.command == "evaluate" and args.split == "holdout":
        marker = RESULTS / ("holdout-" + suite_hash(args.suite)[:16] + ".json")
        with marker.open("x", encoding="utf-8") as handle:
            json.dump({"run_id": evidence.run_id, "purpose": "sealed final holdout; not an optimizer input"}, handle)
    session_id = None
    configuration = None
    deadline = time.monotonic() + 1200
    try:
        if not args.local:
            session = json.loads(azd("ai", "agent", "sessions", "create", "contoso-purchasing", args.version, "--output", "json"))
            evidence.append("session_created", session)
            session_id = session["agent_session_id"]
            save_json(RESULTS / (evidence.run_id + "-session.json"), {"agent": "contoso-purchasing", "version": args.version, "session_id": session_id})
        path = RESULTS / (evidence.run_id + "-responses.jsonl")
        with path.open("x", encoding="utf-8") as output:
            for case in cases:
                if time.monotonic() >= deadline:
                    raise RuntimeError("Hosted evaluation time budget exceeded.")
                if args.command == "evaluate":
                    time.sleep(args.case_delay)
                payload = validate_request({"query": case["query"], "case_id": case["id"], "run_id": evidence.run_id})
                try:
                    if args.local:
                        request = Request("http://127.0.0.1:8088/invocations", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
                        with urlopen(request, timeout=310) as response:
                            value = json.load(response)
                    else:
                        value = remote_invoke(payload, session_id, evidence)
                    check_response(value, payload)
                    actual_configuration = (value["contract"]["sha256"], value["effective_prompt_sha256"], value["model_deployment"])
                    if configuration is not None and configuration != actual_configuration:
                        raise ValueError("Runtime configuration changed within a supposedly fixed evaluation.")
                    configuration = actual_configuration
                    if value["model_deployment"] != model:
                        raise ValueError("Hosted model deployment differs from the approved local configuration.")
                    value.update(
                        id=case["id"], hosted_version=args.version, hosted_session_id=session_id,
                        execution_location="local" if args.local else "azure", environment_sha256=environment_sha256,
                    )
                    if args.command == "evaluate":
                        value.update(evaluation_suite=args.suite, evaluation_suite_sha256=suite_hash(args.suite))
                    evidence.append("verified_response", value)
                    output.write(json.dumps(value, ensure_ascii=False) + "\n")
                    output.flush()
                    print(f"[{case['id']}] {value['response']}")
                except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
                    evidence.failure(exc)
                    output.write(json.dumps({"id": case["id"], "query": case["query"], "status": "failed", "response": "", "error": type(exc).__name__}) + "\n")
                    output.flush()
                    raise
        print(f"Responses: {path}")
    finally:
        if session_id:
            evidence.append("stop_requested", azd("ai", "agent", "sessions", "stop", session_id, "--agent-name", "contoso-purchasing"))
            status = json.loads(azd("ai", "agent", "sessions", "show", session_id, "--agent-name", "contoso-purchasing", "--output", "json"))
            evidence.append("stopped_session", status)
            if status.get("status") not in {"idle", "expired", "deleted"}:
                raise RuntimeError("Hosted compute stop is not confirmed; inspect the recorded session.")
        print(f"Evidence: {evidence.path}")


if __name__ == "__main__":
    main()
