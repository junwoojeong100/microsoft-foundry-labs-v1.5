"""Offline-first workshop exercises. Azure operations require --live."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

from evidence import Budget, Evidence, digest
from lab_profile import DATA, LANGUAGE

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
ENDPOINT_KEY = "FOUNDRY_PROJECT_ENDPOINT"
MODEL_KEY = "FOUNDRY_MODEL_DEPLOYMENT_NAME"
MAX_TOOL_CALLS = 8
MAX_ROUNDS = 5
RUN_BUDGET = {"max_requests": 60, "max_tokens": 150_000, "max_seconds": 900}


class ToolInputError(ValueError):
    pass


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            raise ValueError(f"{path.name}:{number}: blank JSONL line")
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}:{number}: invalid JSON") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path.name}:{number}: expected a JSON object")
        rows.append(row)
    if not rows:
        raise ValueError(f"{path.name}: empty dataset")
    return rows


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


ALLOWED_ENV_KEYS = frozenset({
    ENDPOINT_KEY, MODEL_KEY, "FOUNDRY_SEARCH_ENDPOINT", "FOUNDRY_SEARCH_INDEX",
    "FOUNDRY_KNOWLEDGE_BASE", "FOUNDRY_EMBEDDING_DEPLOYMENT_NAME",
    "FOUNDRY_JUDGE_DEPLOYMENT_NAME", "FOUNDRY_AUTH_MODE", "FOUNDRY_MANAGED_IDENTITY_CLIENT_ID",
    "FOUNDRY_EMBEDDING_ENDPOINT",
})


def env_pair(line: str) -> tuple[str, str] | None:
    """Parse one `.env` line; None for blank, comment, or non-assignment lines.

    Accepts a leading `export `, quoted values, and a trailing ` # comment`.
    """
    text = line.strip()
    if not text or text.startswith("#"):
        return None
    if text.startswith("export "):
        text = text[len("export "):].lstrip()
    if "=" not in text:
        return None
    key, value = text.split("=", 1)
    value = value.strip()
    if value[:1] in ("'", '"') and value.find(value[0], 1) > 0:
        value = value[1:value.find(value[0], 1)]
    else:
        value = re.split(r"\s+#", value, maxsplit=1)[0].strip().strip("'\"")
    return key.strip(), value


def config_values(path: Path = ROOT / ".env") -> dict[str, str]:
    values: dict[str, str] = {}
    if path.exists():
        for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
            if not line.strip() or line.strip().startswith("#"):
                continue
            pair = env_pair(line)
            if pair is None:
                raise ValueError(f".env:{number}: expected KEY=value")
            key, value = pair
            if key == "FOUNDRY_LAB_LANGUAGE":
                raise ValueError(
                    f".env:{number}: FOUNDRY_LAB_LANGUAGE is a shell setting, not a .env setting. "
                    "Run `export FOUNDRY_LAB_LANGUAGE=en` in each English terminal and delete this line."
                )
            if key not in ALLOWED_ENV_KEYS:
                raise ValueError(
                    f".env:{number}: unknown setting {key!r}. Allowed settings: {', '.join(sorted(ALLOWED_ENV_KEYS))}. "
                    "Credentials are never stored in .env."
                )
            values[key] = value
    return {key: os.environ.get(key, values.get(key, "")) for key in ALLOWED_ENV_KEYS}


def validate_endpoint(endpoint: str) -> str:
    endpoint = endpoint.rstrip("/")
    parsed = urlparse(endpoint)
    if "YOUR-" in endpoint.upper() or "ACTUAL-RESOURCE" in endpoint.upper() or "실제-" in endpoint:
        raise ValueError(
            "The project endpoint in .env is still the example text. Run `python scripts/azure_environment.py env --write` "
            "or copy project_endpoint from results/azure-environment.json."
        )
    if "/openai" in parsed.path:
        raise ValueError("Use the project endpoint (https://<resource>.services.ai.azure.com/api/projects/<name>), not a model /openai/v1 endpoint.")
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or not parsed.hostname.endswith(".services.ai.azure.com")
        or not re.fullmatch(r"/api/projects/[A-Za-z0-9._-]+", parsed.path)
        or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.port
    ):
        raise ValueError(
            "Set a public-cloud Foundry project endpoint in .env (https://<resource>.services.ai.azure.com/api/projects/<name>); "
            "do not use a model /openai/v1 endpoint."
        )
    return endpoint


def read_config(path: Path = ROOT / ".env") -> tuple[str, str]:
    values = config_values(path)
    endpoint = validate_endpoint(values[ENDPOINT_KEY])
    model = values[MODEL_KEY]
    if not model or "YOUR-" in model.upper() or not re.fullmatch(r"[A-Za-z0-9._-]+", model):
        raise ValueError("Set the actual model deployment name in .env.")
    return endpoint, model


def env_report(path: Path = ROOT / ".env", ledger: Path = RESULTS / "azure-environment.json") -> list[str]:
    """Offline `.env` check for `doctor`. Lines starting with PROBLEM mean a fix is needed."""
    if not path.exists():
        return [".env: not configured yet; L01 step 5 fills it in."]
    try:
        values = config_values(path)
    except ValueError as error:
        return [f"PROBLEM {error}"]
    lines: list[str] = []
    endpoint = values[ENDPOINT_KEY]
    if not endpoint or "YOUR-" in endpoint.upper():
        lines.append("project endpoint: not set yet (expected until L01 step 5)")
    else:
        try:
            validate_endpoint(endpoint)
            lines.append("project endpoint: format OK")
        except ValueError as error:
            lines.append(f"PROBLEM project endpoint: {error}")
    model = values[MODEL_KEY]
    if model and re.fullmatch(r"[A-Za-z0-9._-]+", model) and "YOUR-" not in model.upper():
        lines.append(f"chat deployment name: {model}")
    else:
        lines.append("PROBLEM chat deployment name: set FOUNDRY_MODEL_DEPLOYMENT_NAME to your deployment name (contoso-chat).")
    if ledger.exists():
        try:
            recorded = json.loads(ledger.read_text(encoding="utf-8"))
        except ValueError:
            return [*lines, "PROBLEM results/azure-environment.json is not valid JSON."]
        project = recorded.get("project_endpoint")
        chat = (recorded.get("model_deployments") or {}).get("chat")
        if project and endpoint and project.rstrip("/") != endpoint.rstrip("/"):
            lines.append("PROBLEM .env endpoint differs from results/azure-environment.json; run `python scripts/azure_environment.py env --write`.")
        elif chat and model and chat != model:
            lines.append("PROBLEM .env chat deployment differs from results/azure-environment.json; run `python scripts/azure_environment.py env --write`.")
        elif project and endpoint:
            lines.append("matches results/azure-environment.json")
    return lines


def inventory() -> dict[str, dict[str, Any]]:
    with (DATA / "inventory.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    result = {}
    for row in rows:
        sku = row["sku"]
        if sku in result:
            raise ValueError(f"Duplicate SKU: {sku}")
        result[sku] = {
            "sku": sku, "name": row["name"], "stock": int(row["stock"]),
            "unit_price_krw": int(row["unit_price_krw"]), "lead_days": int(row["lead_days"]),
            "currency": "KRW", "synthetic": True,
        }
    return result


def get_stock(sku: str) -> dict[str, Any]:
    if not isinstance(sku, str) or sku not in inventory():
        raise ToolInputError("Unknown SKU. Use NB-14, MON-27, or KB-01.")
    return inventory()[sku]


def required_approvals(total: int) -> list[str]:
    if type(total) is not int or total < 0:
        raise ToolInputError("Total must be a non-negative integer in KRW.")
    return ["team_lead", "procurement"] if total > 2_000_000 else ["team_lead"]


def prepare_purchase_request(sku: str, quantity: int) -> dict[str, Any]:
    item = get_stock(sku)
    if type(quantity) is not int or not 1 <= quantity <= 10:
        raise ToolInputError("Quantity must be an integer from 1 through 10.")
    if quantity > item["stock"]:
        raise ToolInputError(f"Insufficient stock: requested={quantity}, available={item['stock']}. No draft created.")
    total = quantity * item["unit_price_krw"]
    fingerprint = hashlib.sha256(f"{sku}:{quantity}:{total}".encode()).hexdigest()[:12]
    return {
        "draft_id": f"DEMO-{fingerprint}", "sku": sku, "quantity": quantity,
        "total_krw": total, "currency": "KRW", "status": "draft_requires_human_approval",
        "required_approvals": required_approvals(total),
        "order_submitted": False, "synthetic": True,
    }


def dispatch_tool(name: str, arguments: str) -> dict[str, Any]:
    try:
        payload = json.loads(arguments)
    except json.JSONDecodeError as exc:
        raise ToolInputError("Function arguments are not valid JSON.") from exc
    if not isinstance(payload, dict):
        raise ToolInputError("Function arguments must be an object.")
    if name == "get_stock" and set(payload) == {"sku"}:
        return get_stock(payload["sku"])
    if name == "prepare_purchase_request" and set(payload) == {"sku", "quantity"}:
        return prepare_purchase_request(payload["sku"], payload["quantity"])
    raise ToolInputError("Unknown function or unexpected argument keys.")


def function_schemas() -> list[dict[str, Any]]:
    sku = {"type": "string", "enum": ["NB-14", "MON-27", "KB-01"], "description": "Synthetic inventory SKU"}
    return [
        {
            "name": "get_stock", "description": "Read current synthetic stock and unit price; does not change inventory.",
            "parameters": {"type": "object", "properties": {"sku": sku}, "required": ["sku"], "additionalProperties": False},
            "strict": True,
        },
        {
            "name": "prepare_purchase_request",
            "description": "Prepare a synthetic purchase draft only. Never approves, orders, pays, or sends a message. Ask for missing quantity.",
            "parameters": {
                "type": "object",
                "properties": {"sku": sku, "quantity": {"type": "integer", "minimum": 1, "maximum": 10}},
                "required": ["sku", "quantity"], "additionalProperties": False,
            },
            "strict": True,
        },
    ]


def validate_data() -> list[dict[str, Any]]:
    cases = load_jsonl(DATA / "evaluation/cases.jsonl")
    ids: set[str] = set()
    scenarios: dict[str, str] = {}
    required = {"id", "split", "scenario", "category", "query", "ground_truth", "expected_behavior", "context"}
    for case in cases:
        if not required <= case.keys() or any(not isinstance(case[k], str) or not case[k].strip() for k in required):
            raise ValueError("Every evaluation case must have non-empty string fields.")
        if case["id"] in ids or case["split"] not in {"dev", "holdout"}:
            raise ValueError("Duplicate ID or invalid split.")
        ids.add(case["id"])
        old_split = scenarios.setdefault(case["scenario"], case["split"])
        if old_split != case["split"]:
            raise ValueError("Scenario leakage between dev and holdout.")
    if len(cases) != 20 or sum(c["split"] == "holdout" for c in cases) != 10:
        raise ValueError("Expected 10 dev cases and 10 held-out cases.")
    if len(inventory()) != 3:
        raise ValueError("Expected three synthetic inventory items.")
    return cases


def format_saved_responses(rows: list[dict[str, Any]]) -> str:
    if not rows:
        raise ValueError("No saved response records to read.")
    english = LANGUAGE == "en"
    labels = {
        "boundary": "LOCAL READ ONLY: no Azure calls; no automatic quality verdict." if english else "로컬 결과 읽기: Azure 호출 없음 · 품질 자동 판정 아님",
        "record": "Record" if english else "기록",
        "status": "Status" if english else "상태",
        "agent": "Agent / version" if english else "에이전트 / 버전",
        "model": "Model deployment" if english else "모델 배포",
        "question": "Question" if english else "질문",
        "answer": "Original answer" if english else "원문 답변",
        "tools": "Function calls" if english else "함수 호출",
        "inputs": "Inputs" if english else "입력값",
        "output": "Actual output" if english else "실제 결과",
        "citations": "Citations" if english else "인용",
        "missing": "Not recorded" if english else "미기록",
        "failed": "Execution failed" if english else "실행 실패",
        "completed": "completed means execution finished, not a quality pass" if english else "completed는 실행 완료이며 정답 판정이 아닙니다",
    }
    for number, row in enumerate(rows, 1):
        if any(not isinstance(row.get(key), str) or not row[key].strip() for key in ("id", "query", "status")):
            raise ValueError(f"Row {number}: use the SDK 'Responses:' JSONL, not a receipt or L08 evaluation file.")
        if row["status"] not in {"completed", "failed"}:
            raise ValueError(f"Row {number}: unsupported response status {row['status']!r}.")
        configuration = row.get("configuration")
        if not isinstance(configuration, dict) or configuration.get("language") != LANGUAGE:
            raise ValueError(f"Row {number}: configuration language must match FOUNDRY_LAB_LANGUAGE={LANGUAGE}.")
        for key in ("agent_name", "agent_version", "model_deployment"):
            if not isinstance(configuration.get(key), str) or not configuration[key].strip():
                raise ValueError(f"Row {number}: missing configuration.{key}.")
        for key in ("agent_name", "agent_version"):
            if key in row and row[key] != configuration[key]:
                raise ValueError(f"Row {number}: {key} differs from the recorded configuration.")
        if row["status"] == "failed":
            if not isinstance(row.get("error_type"), str) or not row["error_type"].strip():
                raise ValueError(f"Row {number}: failed record is missing error_type.")
            continue
        for key in ("response", "response_id"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f"Row {number}: completed record is missing {key}.")
        for key in ("tool_calls", "citations"):
            if not isinstance(row.get(key), list) or any(not isinstance(item, dict) for item in row[key]):
                raise ValueError(f"Row {number}: missing or invalid {key}; do not assume no calls or citations.")
        for call in row["tool_calls"]:
            if (
                any(not isinstance(call.get(key), str) or not call[key].strip()
                    for key in ("name", "call_id", "arguments"))
                or not isinstance(call.get("output"), dict)
            ):
                raise ValueError(f"Row {number}: incomplete function-call record.")
    lines = [labels["boundary"]]
    for number, row in enumerate(rows, 1):
        config = row["configuration"]
        lines += [
            "", f"--- {labels['record']} {number}: {row['id']} ---",
            f"{labels['status']}: {row['status']}",
            f"{labels['agent']}: {config['agent_name']} / {config['agent_version']}",
            f"{labels['model']}: {config['model_deployment']}",
            f"{labels['question']}:\n{row['query']}",
        ]
        if row["status"] == "failed":
            lines += [f"{labels['failed']}: {row['error_type']}", f"{labels['answer']}: {labels['missing']}"]
            continue
        lines += [
            labels["completed"], f"response_id: {row['response_id']}",
            f"\n{labels['answer']}:\n{row['response']}",
            f"\n{labels['tools']}: {len(row['tool_calls'])}",
        ]
        for call in row["tool_calls"]:
            lines += [
                f"- {call['name']} / call_id: {call['call_id']}",
                f"{labels['inputs']}: {call['arguments']}",
                f"{labels['output']}:\n{json.dumps(call['output'], ensure_ascii=False, indent=2)}",
            ]
        lines += [f"\n{labels['citations']}:\n{json.dumps(row['citations'], ensure_ascii=False, indent=2)}"]
    return "\n".join(lines)


def score_reviews(rows: list[dict[str, Any]], split: str = "all") -> dict[str, Any]:
    cases = [c for c in validate_data() if split == "all" or c["split"] == split]
    expected = {c["id"]: c for c in cases}
    if not rows or len(rows) != len(expected):
        raise ValueError(f"Expected exactly {len(expected)} reviewed rows; partial runs cannot pass.")
    seen: set[str] = set()
    for row in rows:
        case_id = row.get("id")
        if not isinstance(case_id, str) or case_id not in expected or case_id in seen:
            raise ValueError("Missing, unknown, or duplicated case ID.")
        seen.add(case_id)
        if type(row.get("manual_pass")) is not bool:
            raise ValueError(f"{case_id}: manual_pass must be true or false, not a score or an empty value.")
        for field in ("response", "review_note"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"{case_id}: {field} is required as review evidence.")
    rubric = json.loads((DATA / "evaluation/rubric.json").read_text(encoding="utf-8"))
    passed = sum(row["manual_pass"] for row in rows)
    blockers = [
        row["id"] for row in rows
        if not row["manual_pass"] and expected[row["id"]]["category"] in rubric["zero_tolerance_categories"]
    ]
    rate = passed / len(rows)
    return {
        "type": "human_review_gate", "split": split, "total": len(rows),
        "passed": passed, "pass_rate": rate, "critical_failures": blockers,
        "gate_passed": rate >= rubric["minimum_pass_rate"] and not blockers,
        "production_certification": False,
    }


class Receipt:
    def __init__(self, endpoint: str, mode: str) -> None:
        run_id = "contoso-lab-" + uuid4().hex[:12]
        self.path = RESULTS / f"{run_id}.json"
        self.data: dict[str, Any] = {
            "schema": "contoso-lab-resources-v1", "run_id": run_id,
            "endpoint": endpoint, "mode": mode, "resources": [],
        }
        self.persist()
        print(f"Resource receipt: {self.path.relative_to(ROOT)}")

    def persist(self) -> None:
        save_json(self.path, self.data)

    def add(self, kind: str, resource_id: str, **fields: str) -> None:
        self.data["resources"].append({"kind": kind, "id": resource_id, **fields})
        self.persist()


def read_receipt(path: Path, endpoint: str) -> dict[str, Any]:
    resolved = path.resolve()
    if resolved.parent != RESULTS.resolve():
        raise ValueError("Cleanup receipts must be direct children of this workshop's results directory.")
    data = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") not in {"contoso-lab-resources-v1", "hb-lab-resources-v1"}:
        raise ValueError("Unrecognized receipt schema.")
    run_id = data.get("run_id", "")
    prefix = "hb" if data["schema"] == "hb-lab-resources-v1" else "contoso"
    if not isinstance(run_id, str) or not re.fullmatch(rf"{prefix}-lab-[0-9a-f]{{12}}", run_id):
        raise ValueError("Invalid workshop run ID.")
    if resolved.stem != run_id or data.get("endpoint") != endpoint:
        raise ValueError("Receipt name or project endpoint mismatch; cleanup stopped.")
    resources = data.get("resources")
    if not isinstance(resources, list):
        raise ValueError("Invalid resource list.")
    for resource in resources:
        if not isinstance(resource, dict) or not isinstance(resource.get("id"), str) or not resource["id"]:
            raise ValueError("Invalid resource record.")
        if resource.get("kind") not in {"agent", "conversation", "vector_store", "file"}:
            raise ValueError("Unsupported resource kind; cleanup stopped.")
        if resource["kind"] == "agent" and resource["id"] != run_id:
            raise ValueError("Agent name is outside this workshop run.")
    return data


def ensure_response(response: Any) -> str:
    if response.status != "completed":
        raise RuntimeError(f"Response did not complete: {response.status}. Check quota, output limit, and trace; no success claimed.")
    if not response.output_text or not response.output_text.strip():
        raise RuntimeError("Completed response has no output text. Inspect refusal/tool results; no success claimed.")
    return response.output_text


def index_file(client: Any, file_id: str, vector_store_id: str, timeout_seconds: float = 180.0) -> None:
    if timeout_seconds <= 0:
        raise ValueError("Ingestion timeout must be positive.")
    deadline = time.monotonic() + timeout_seconds
    indexed = client.vector_stores.files.create(
        vector_store_id=vector_store_id, file_id=file_id, timeout=min(60.0, timeout_seconds),
    )
    while indexed.status == "in_progress":
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError(f"File ingestion timed out: {file_id}. Inspect the receipt and portal before retrying.")
        time.sleep(min(2.0, remaining))
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError(f"File ingestion timed out: {file_id}.")
        indexed = client.vector_stores.files.retrieve(
            file_id=file_id, vector_store_id=vector_store_id, timeout=min(60.0, remaining),
        )
    if indexed.status != "completed":
        raise RuntimeError(f"File ingestion did not complete: {file_id}, status={indexed.status}")


def run_turn(
    client: Any, agent_name: str, query: str, receipt: Receipt, *,
    version: str | None = None, budget: Budget | None = None, evidence: Evidence | None = None,
) -> dict[str, Any]:
    budget = budget or Budget(max_requests=MAX_ROUNDS + 1, max_seconds=360)
    budget.before_request()
    conversation = client.conversations.create()
    receipt.add("conversation", conversation.id)
    observed_calls: list[dict[str, Any]] = []
    citations: list[dict[str, Any]] = []
    retrieved: list[str] = []
    current_input: Any = query
    started = time.monotonic()
    total_calls = 0
    input_tokens = 0
    output_tokens = 0
    response_ids: list[str] = []
    request_ids: list[str] = []
    for _ in range(MAX_ROUNDS):
        budget.before_request(token_reservation=2048 + len(str(current_input)))
        reference = {"name": agent_name, "type": "agent_reference"}
        if version is not None:
            reference["version"] = version
        response = client.responses.create(
            conversation=conversation.id, input=current_input,
            extra_body={"agent_reference": reference},
            include=["file_search_call.results"], max_output_tokens=2048,
        )
        if evidence is not None:
            evidence.append("response", response)
        response_ids.append(response.id)
        request_id = getattr(response, "_request_id", None)
        if request_id:
            request_ids.append(request_id)
        if response.usage:
            input_tokens += response.usage.input_tokens
            output_tokens += response.usage.output_tokens
            budget.record_tokens(response.usage.input_tokens + response.usage.output_tokens)
        calls = []
        for item in response.output:
            if item.type == "function_call":
                calls.append(item)
            elif item.type == "file_search_call":
                for result in item.results or []:
                    if result.text:
                        retrieved.append(result.text)
            elif item.type == "message":
                for block in item.content:
                    if block.type == "output_text":
                        citations.extend(annotation.model_dump() for annotation in block.annotations)
        if response.status != "completed":
            ensure_response(response)
        if not calls:
            return {
                "query": query, "response": ensure_response(response), "context": "\n\n".join(retrieved),
                "response_id": response.id, "conversation_id": conversation.id,
                "response_ids": response_ids, "request_ids": request_ids,
                "trace_id": None, "trace_status": "not_yet_correlated",
                "agent_version": version, "model": getattr(response, "model", None),
                "tool_calls": observed_calls, "citations": citations,
                "latency_seconds": round(time.monotonic() - started, 3),
                "input_tokens": input_tokens, "output_tokens": output_tokens,
                "manual_pass": None, "review_note": "",
            }
        total_calls += len(calls)
        if total_calls > MAX_TOOL_CALLS:
            raise RuntimeError("Function-call budget exceeded; stopped before executing extra calls.")
        current_input = []
        for call in calls:
            try:
                value = {"ok": True, "result": dispatch_tool(call.name, call.arguments)}
            except ToolInputError as exc:
                print(f"TOOL_REJECTED {call.name}: {exc}", file=sys.stderr)
                value = {"ok": False, "error": {"code": "invalid_tool_request", "message": str(exc)}}
            observed_calls.append({"call_id": call.call_id, "name": call.name, "arguments": call.arguments, "output": value})
            if evidence is not None:
                evidence.append("tool_result", observed_calls[-1])
            current_input.append({
                "type": "function_call_output", "call_id": call.call_id,
                "output": json.dumps(value, ensure_ascii=False),
            })
    raise RuntimeError("Turn limit exceeded; stopped instead of claiming completion.")


def create_lab_agent(
    project: Any, client: Any, model: str, mode: str, receipt: Receipt,
    prompt: Path = DATA / "prompts/agent-v2.txt",
) -> str:
    from azure.ai.projects.models import FileSearchTool, FunctionTool, PromptAgentDefinition

    tools = []
    if mode in {"rag", "capstone", "evaluate"}:
        store = client.vector_stores.create(
            name=receipt.data["run_id"], expires_after={"anchor": "last_active_at", "days": 1},
        )
        receipt.add("vector_store", store.id)
        for path in sorted((DATA / "policies").glob("*.md")):
            with path.open("rb") as handle:
                uploaded = client.files.create(file=handle, purpose="assistants")
            receipt.add("file", uploaded.id)
            index_file(client, uploaded.id, store.id)
        tools.append(FileSearchTool(vector_store_ids=[store.id], max_num_results=4))
    if mode in {"capstone", "evaluate"}:
        tools.extend(FunctionTool(**schema) for schema in function_schemas())
    agent = project.agents.create_version(
        agent_name=receipt.data["run_id"],
        definition=PromptAgentDefinition(
            model=model,
            instructions=prompt.read_text(encoding="utf-8"),
            tools=tools,
        ),
        description="Synthetic workshop agent; never submit real orders.",
    )
    receipt.add("agent", agent.name, version=agent.version)
    return agent.name


def cleanup(project: Any, client: Any, path: Path, endpoint: str, confirmation: str | None) -> None:
    from azure.core.exceptions import ResourceNotFoundError
    from openai import NotFoundError

    data = read_receipt(path, endpoint)
    if confirmation != data["run_id"]:
        raise ValueError("Repeat the exact run_id using --confirm before deleting recorded resources.")
    ordered = sorted(data["resources"], key=lambda r: {"conversation": 0, "agent": 1, "vector_store": 2, "file": 3}[r["kind"]])
    for resource in ordered:
        if resource.get("cleanup_status") in {"deleted", "already_absent"}:
            continue
        resource_id = resource["id"]
        try:
            if resource["kind"] == "agent":
                project.agents.delete(agent_name=resource_id)
            elif resource["kind"] == "conversation":
                client.conversations.delete(conversation_id=resource_id)
            elif resource["kind"] == "vector_store":
                client.vector_stores.delete(vector_store_id=resource_id)
            elif resource["kind"] == "file":
                client.files.delete(file_id=resource_id)
            resource["cleanup_status"] = "deleted"
        except (ResourceNotFoundError, NotFoundError):
            resource["cleanup_status"] = "already_absent"
        save_json(path, data)
        print(f"{resource['kind']} {resource_id}: {resource['cleanup_status']}")


def run_live(args: argparse.Namespace) -> None:
    from azure.ai.projects import AIProjectClient
    from azure.core.exceptions import AzureError
    from azure.identity import AzureCliCredential
    from openai import OpenAIError

    endpoint, model = read_config()
    if args.command == "cleanup":
        if not args.receipt:
            raise ValueError("--receipt is required.")
        data = read_receipt(args.receipt, endpoint)
        if args.confirm != data["run_id"]:
            raise ValueError("--confirm must equal the run_id in the receipt.")
    receipt = None if args.command in {"model", "cleanup"} else Receipt(endpoint, args.command)
    evidence = Evidence(args.command)
    budget = Budget(**RUN_BUDGET)
    try:
        with (
            AzureCliCredential(process_timeout=30) as credential,
            AIProjectClient(endpoint=endpoint, credential=credential, retry_total=0) as project,
            project.get_openai_client(max_retries=0, timeout=60.0) as client,
        ):
            if args.command == "cleanup":
                cleanup(project, client, args.receipt, endpoint, args.confirm)
            elif args.command == "model":
                budget.before_request(token_reservation=4096)
                response = client.responses.create(
                    model=model, input=args.query or (
                        "How should you respond when no internal company policy has been provided?"
                        if LANGUAGE == "en" else "회사 내부 규정이 제공되지 않았을 때 어떻게 답해야 하나요?"
                    ),
                    max_output_tokens=2048, store=False,
                )
                evidence.append("response", response)
                print(ensure_response(response))
                print(f"response_id={response.id}")
            else:
                if receipt is None:
                    raise RuntimeError("Missing resource receipt.")
                agent_name = create_lab_agent(project, client, model, args.command, receipt, args.prompt)
                agent_version = next(r["version"] for r in receipt.data["resources"] if r["kind"] == "agent")
                cases = (
                    [c for c in validate_data() if args.split == "all" or c["split"] == args.split]
                    if args.command == "evaluate" else
                    [{"id": "manual-01", "query": args.query or (
                        ("Check the purchasing policy and inventory for NB-14, quantity 2, and prepare a purchase request draft."
                         if LANGUAGE == "en" else "노트북 2대의 구매 규정과 NB-14 재고를 확인하고 구매 요청 초안을 만들어줘.")
                        if args.command == "capstone" else (
                            "What is the standard laptop price ceiling? Cite the policy."
                            if LANGUAGE == "en" else "표준 노트북의 가격 상한과 근거를 알려줘."
                        )
                    )}]
                )
                path = RESULTS / f"{receipt.data['run_id']}-responses.jsonl"
                configuration = {
                    "language": LANGUAGE,
                    "agent_name": agent_name, "agent_version": agent_version, "model_deployment": model,
                    "prompt_sha256": hashlib.sha256(args.prompt.read_bytes()).hexdigest(),
                    "corpus_sha256": digest({p.name: p.read_text(encoding="utf-8") for p in sorted((DATA / "policies").glob("*.md"))}),
                    "dataset_sha256": hashlib.sha256((DATA / "evaluation/cases.jsonl").read_bytes()).hexdigest(),
                    "rubric_sha256": hashlib.sha256((DATA / "evaluation/rubric.json").read_bytes()).hexdigest(),
                }
                evidence.append("configuration", configuration)
                with path.open("x", encoding="utf-8") as output:
                    for case in cases:
                        if args.command == "evaluate":
                            time.sleep(args.case_delay)
                        try:
                            row = run_turn(
                                client, agent_name, case["query"], receipt, version=agent_version,
                                budget=budget, evidence=evidence,
                            )
                        except (AzureError, OpenAIError, RuntimeError) as exc:
                            evidence.failure(exc)
                            output.write(json.dumps({
                                "id": case["id"], "query": case["query"], "status": "failed",
                                "response": "", "manual_pass": None, "error_type": type(exc).__name__,
                                "configuration": configuration, "evidence_file": evidence.path.name,
                            }, ensure_ascii=False) + "\n")
                            output.flush()
                            raise
                        row["id"] = case["id"]
                        row["status"] = "completed"
                        row["agent_name"] = agent_name
                        row["configuration"] = configuration
                        row["evidence_file"] = evidence.path.name
                        output.write(json.dumps(row, ensure_ascii=False) + "\n")
                        output.flush()
                        print(f"[{case['id']}] {row['response']}\n")
                print(f"Responses: {path.relative_to(ROOT)}")
                print(f"Read again (local only): python samples/workshop.py read-result --input {path.relative_to(ROOT)}")
    except (AzureError, OpenAIError) as exc:
        evidence.failure(exc)
        status = getattr(exc, "status_code", None)
        raise RuntimeError(
            f"Azure call failed ({type(exc).__name__}, status={status}). "
            "See troubleshooting. Resources may remain; inspect the receipt and portal before retrying."
        ) from exc
    finally:
        print(f"Private evidence: {evidence.path.relative_to(ROOT)}")
        if receipt is not None:
            print("Resources are retained for inspection; vector stores expire after one inactive day, files do not.")
            print(
                f"Cleanup: python samples/workshop.py cleanup --receipt "
                f"{receipt.path.relative_to(ROOT)} --confirm {receipt.data['run_id']} --live"
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="Inspect local tools only; no Azure authentication.")
    sub.add_parser("validate-data", help="Check synthetic data and held-out split.")
    tools = sub.add_parser("tools", help="Run pure local functions; no orders or network.")
    tools.add_argument("--sku", default="NB-14")
    tools.add_argument("--quantity", type=int, default=2)
    score = sub.add_parser("score", help="Score complete human-reviewed records, not simulated success.")
    score.add_argument("--input", type=Path, required=True)
    score.add_argument("--split", choices=["all", "dev", "holdout"], default="all")
    read_result = sub.add_parser("read-result", help="Read saved SDK answers, tool results and citations locally; no Azure calls.")
    read_result.add_argument("--input", type=Path, required=True, help="The JSONL path printed after Responses: in L04/L05/L06.")
    for command in ("model", "agent", "rag", "capstone", "evaluate", "cleanup"):
        child = sub.add_parser(command, help="Plan only unless --live is set.")
        child.add_argument("--live", action="store_true", help="Allow billable Azure operations. Read the corresponding lab first.")
        child.add_argument("--query")
        child.add_argument("--split", choices=["all", "dev", "holdout"], default="dev")
        child.add_argument("--receipt", type=Path)
        child.add_argument("--confirm")
        child.add_argument("--prompt", type=Path, default=DATA / "prompts/agent-v2.txt")
        child.add_argument("--case-delay", type=float, default=10.0, help="Seconds between evaluation cases; 0..60.")
    args = parser.parse_args(argv)
    if args.command == "doctor":
        print(f"Python {sys.version.split()[0]} | Offline inspection only")
        print(f"Local .env: {'present (not printed)' if (ROOT / '.env').exists() else 'not configured'}")
        checks = env_report()
        for line in checks:
            print(f".env check: {line}")
        for package in ("azure-ai-projects", "azure-identity", "openai"):
            try:
                print(f"{package}: {importlib.metadata.version(package)}")
            except importlib.metadata.PackageNotFoundError:
                print(f"{package}: not installed (needed only for --live)")
        return 1 if any(line.startswith("PROBLEM") for line in checks) else 0
    if args.command == "validate-data":
        print(f"Validated {len(validate_data())} cases: dev=10, holdout=10; scenario overlap=0; inventory=3.")
        return 0
    if args.command == "tools":
        print(json.dumps({"stock": get_stock(args.sku), "draft": prepare_purchase_request(args.sku, args.quantity)}, ensure_ascii=False, indent=2))
        return 0
    if args.command == "read-result":
        rows = load_jsonl(args.input)
        print(format_saved_responses(rows))
        return 1 if any(row["status"] == "failed" for row in rows) else 0
    if args.command == "score":
        report = score_reviews(load_jsonl(args.input), args.split)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["gate_passed"] else 1
    if not args.live:
        print(f"PLAN ONLY: {args.command}. No Azure requests were made.")
        if args.command == "cleanup":
            print("With --live, only resources in --receipt are deleted, after an exact --confirm run ID.")
        else:
            print("With --live, synthetic prompts are sent to your configured Foundry project; charges may apply.")
            if args.command != "model":
                print("Creates an isolated agent/conversations and, for retrieval, uploads the three synthetic policy files.")
                print("Created IDs are saved in results/. Cleanup is explicit, not automatic.")
                print(
                    f"Limits per run: at most {RUN_BUDGET['max_requests']} requests, {RUN_BUDGET['max_tokens']:,} tokens "
                    f"and {RUN_BUDGET['max_seconds']} seconds; no automatic retries."
                    + (f" At most {MAX_ROUNDS} model rounds and {MAX_TOOL_CALLS} function calls." if args.command == "capstone" else "")
                )
            else:
                print("Limits per run: one model request with at most 2,048 output tokens; no automatic retries.")
        return 0
    if not 0 <= args.case_delay <= 60:
        raise ValueError("--case-delay must be 0..60 seconds.")
    run_live(args)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, OSError, ImportError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
