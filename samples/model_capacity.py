"""Plan model throughput; check/apply/test only with explicit --live and owned scope."""

from __future__ import annotations

import argparse
import asyncio
from collections import defaultdict
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Callable
from uuid import UUID

from evidence import Evidence, digest
from lab_profile import LANGUAGE

ROOT = Path(__file__).resolve().parents[1]
API_VERSION = "2025-06-01"
ROLES = ("chat", "judge", "embedding")
ONLINE_SKUS = {"Standard", "GlobalStandard", "DataZoneStandard"}
MAX_SECONDS = 180
MAX_MANAGEMENT_REQUESTS = 24
INPUT_BUDGET = 8192
OUTPUT_BUDGET = 2048
STARTS_PER_MINUTE = 6
MIN_START_INTERVAL = 1.0


def requirements(learners: int = 1) -> dict:
    if type(learners) is not int or not 1 <= learners <= 20:
        raise ValueError("Choose 1..20 simultaneous learners; shared deployments need the combined budget.")
    profiles = {}
    for role in ROLES:
        output = 0 if role == "embedding" else OUTPUT_BUDGET
        rate = 1 if role == "embedding" else STARTS_PER_MINUTE
        margin = 1.2 if role == "embedding" else 1.5
        quantum = 1000 if role == "embedding" else 10_000
        per_learner = math.ceil((INPUT_BUDGET + output) * rate * margin / quantum) * quantum
        profiles[role] = {
            "estimated_input_tokens_per_request": INPUT_BUDGET,
            "reserved_output_tokens_per_request": output,
            "planned_requests_per_minute": rate,
            "headroom_factor": margin,
            "minimum_tpm": per_learner * learners,
            "minimum_rpm": (6 if role == "embedding" else 60) * learners,
        }
    return {
        "schema": "contoso-model-capacity-plan-v1", "learners": learners,
        "roles": profiles,
        "assumptions": [
            "Each learner runs one lab at a time; L13 permits up to three overlapping agents.",
            "Chat/judge sizing assumes at most six request starts per minute and an 8192-token input estimate.",
            "TPM admission uses provider estimates plus the output reservation, not billed token counts.",
            "These are conservative starting minimums, not a universal no-429 guarantee.",
            "Longer context, managed retrieval/evaluation, other users, or faster dispatch need a new budget.",
            "TPM and RPM must both pass; capacity units vary by model and SKU and are not a spending cap.",
        ],
        "azure_calls": 0,
    }


def estimate_tokens(text: str) -> int:
    """Conservative planning estimate, not the provider's admission or billing tokenizer."""
    return math.ceil(len(text.encode("utf-8")) / 3) + 512


def load_scope(receipt: Path, language: str = LANGUAGE, roles: tuple[str, ...] | list[str] = ROLES) -> dict:
    state = json.loads(receipt.read_text(encoding="utf-8"))
    required = {
        "repository_id", "language", "subscription", "resource_group", "resource_group_id",
        "account_name", "project_name", "project_endpoint", "run_id", "model_deployments", "location",
    }
    if not isinstance(state, dict) or not required <= state.keys():
        raise ValueError("Ownership receipt is missing required environment fields.")
    if state.get("repository_id") != 1396573688 or state.get("language") != language:
        raise ValueError("Receipt repository/language does not match this lab.")
    if not isinstance(state["subscription"], str):
        raise ValueError("The receipt must contain a subscription UUID.")
    subscription = str(UUID(state["subscription"]))
    names = [state[key] for key in ("resource_group", "account_name", "project_name", "run_id")]
    if any(not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,90}", name) for name in names):
        raise ValueError("Invalid resource names in ownership receipt.")
    if not isinstance(state["location"], str) or not re.fullmatch(r"[A-Za-z0-9]+", state["location"]):
        raise ValueError("Use an Azure region identifier in the ownership receipt.")
    group_id = f"/subscriptions/{subscription}/resourceGroups/{state['resource_group']}"
    if state.get("resource_group_id", "").lower() != group_id.lower():
        raise ValueError("Receipt resource group is outside the recorded subscription.")
    endpoint = f"https://{state['account_name']}.services.ai.azure.com/api/projects/{state['project_name']}"
    if state.get("project_endpoint", "").rstrip("/") != endpoint:
        raise ValueError("Receipt project endpoint is outside the owned Foundry account.")
    deployments = state["model_deployments"]
    if not roles or len(roles) != len(set(roles)) or not set(roles) <= set(ROLES):
        raise ValueError("Select distinct supported model roles.")
    if not isinstance(deployments, dict) or any(
        role not in deployments or not isinstance(deployments[role], str)
        or not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", deployments[role]) for role in roles
    ):
        raise ValueError("The receipt must identify the selected role deployments.")
    if len(set(deployments[role] for role in roles)) != len(roles):
        raise ValueError("Use separate role deployments; this plan does not size shared chat/judge deployments.")
    return state


class Management:
    def __init__(self, az_call: Callable | None = None):
        if az_call is None:
            sys.path.insert(0, str(ROOT / "scripts"))
            from azure_environment import az
            az_call = az
        self.az_call = az_call
        self.started = time.monotonic()
        self.calls = 0

    def remaining(self) -> float:
        remaining = MAX_SECONDS - (time.monotonic() - self.started)
        if remaining <= 0:
            raise RuntimeError("Capacity operation deadline exceeded; no further request was sent.")
        return remaining

    def call(self, *args):
        if self.calls >= MAX_MANAGEMENT_REQUESTS:
            raise RuntimeError("Capacity management request limit exceeded.")
        timeout = max(1, min(30, math.ceil(self.remaining())))
        self.calls += 1
        return self.az_call(*args, timeout=timeout)


def model_catalog(state: dict, management: Management) -> list[dict]:
    scope = (
        f"/subscriptions/{state['subscription']}/providers/Microsoft.CognitiveServices/"
        f"locations/{state['location']}"
    )
    result = management.call(
        "rest", "--method", "get", "--url", scope + f"/models?api-version={API_VERSION}",
        "--subscription", state["subscription"],
    )
    if (
        not isinstance(result, dict) or not isinstance(result.get("value"), list)
        or result.get("nextLink")
    ):
        raise ValueError("A complete raw ARM model catalog is required; no deployment was sent.")
    return result["value"]


def model_sku(catalog: list[dict], selected: dict, sku_name: str) -> dict:
    candidates = []
    for item in catalog:
        if not isinstance(item, dict) or (item.get("kind"), item.get("skuName")) != ("AIServices", "S0"):
            continue
        model = item.get("model")
        if not isinstance(model, dict) or (
            model.get("name"), model.get("version"), model.get("format")
        ) != (selected["name"], selected["version"], "OpenAI"):
            continue
        skus = model.get("skus")
        if not isinstance(skus, list):
            raise ValueError("Supported SKU metadata is missing.")
        for sku in skus:
            if not isinstance(sku, dict) or sku.get("name") != sku_name:
                continue
            usage = sku.get("usageName")
            if not isinstance(usage, str) or not usage:
                raise ValueError("SKU quota usageName is missing.")
            if not usage.endswith("-finetune"):
                candidates.append(sku)
    if len(candidates) != 1:
        raise ValueError("No unique AIServices/S0 base-model version/SKU in this region.")
    return candidates[0]


def rate_limits(deployment: dict) -> dict:
    values = defaultdict(list)
    rules = deployment.get("properties", {}).get("rateLimits")
    if not isinstance(rules, list) or any(not isinstance(rule, dict) for rule in rules):
        raise ValueError("Deployment returned no valid rateLimits list.")
    for rule in rules:
        key = rule.get("key")
        if key not in {"token", "request"}:
            continue
        count, period = rule.get("count"), rule.get("renewalPeriod")
        if (
            type(count) not in (int, float) or type(period) not in (int, float)
            or not math.isfinite(count) or not math.isfinite(period) or count <= 0 or period <= 0
        ):
            raise ValueError("Deployment returned invalid rateLimits.")
        values[key].append(math.floor(60 * count / period))
    if not values["token"] or not values["request"]:
        raise ValueError("Both actual token and request rateLimits are required; capacity is not assumed to equal TPM.")
    return {"tpm": min(values["token"]), "rpm": min(values["request"])}


def verify_quota(usages: list[dict], needed: dict[str, int]) -> None:
    if not isinstance(usages, list):
        raise ValueError("No valid regional quota inventory was returned; no changes were sent.")
    for name, additional in needed.items():
        if additional == 0:
            continue
        matches = [item for item in usages if isinstance(item, dict)
                   and isinstance(item.get("name"), dict) and item["name"].get("value") == name]
        if len(matches) != 1:
            raise ValueError(f"No unique verified quota capacity for {name}; no changes were sent.")
        limit, used = matches[0].get("limit"), matches[0].get("currentValue")
        if (
            type(limit) not in (int, float) or type(used) not in (int, float)
            or not math.isfinite(limit) or not math.isfinite(used) or used < 0 or limit - used < additional
        ):
            raise ValueError(f"Insufficient verified quota capacity for {name}; no changes were sent.")


def catalog_unit_rates(sku: dict) -> dict:
    limits = sku.get("rateLimits")
    if not isinstance(limits, list):
        raise ValueError("SKU unit rateLimits are unavailable; initial capacity cannot be guessed.")
    rules = []
    for limit in limits:
        if not isinstance(limit, dict):
            raise ValueError("SKU returned an invalid rate limit.")
        if "key" in limit:
            rules.append(limit)
            continue
        if limit.get("count") is not None:
            rules.append({"key": "request", "count": limit["count"], "renewalPeriod": limit.get("renewalPeriod")})
        nested = limit.get("rules", [])
        if not isinstance(nested, list):
            raise ValueError("SKU returned invalid nested throttling rules.")
        rules.extend(nested)
    return rate_limits({"properties": {"rateLimits": rules}})


def aligned_capacity(required: int, configuration: dict) -> int:
    if not isinstance(configuration, dict):
        raise ValueError("Model SKU capacity constraints are missing.")
    allowed = configuration.get("allowedValues")
    if allowed:
        if not isinstance(allowed, list) or any(type(value) is not int or value < 0 for value in allowed):
            raise ValueError("Invalid SKU allowed capacity values.")
        candidates = [value for value in allowed if value >= required]
        if not candidates:
            raise ValueError("The SKU has no allowed capacity large enough for the recommendation.")
        return min(candidates)
    # Online SKUs may omit these optional restrictions; capacity is still an integer.
    minimum = configuration.get("minimum", 1)
    maximum = configuration.get("maximum")
    step = configuration.get("step", 1)
    if (
        any(type(value) is not int for value in (minimum, maximum, step))
        or minimum < 0 or step <= 0 or maximum < minimum
    ):
        raise ValueError("Invalid SKU minimum/maximum/step constraints.")
    result = minimum + max(0, math.ceil((required - minimum) / step)) * step
    if result > maximum:
        raise ValueError("Recommended capacity exceeds the model SKU maximum.")
    return result


def initial_capacity_plan(catalog: list[dict], usages: list[dict], models: dict, sku_name: str,
                          *, learners: int = 1, max_capacity: int = 100,
                          existing: dict | None = None) -> dict:
    if sku_name not in ONLINE_SKUS or set(models) != set(ROLES):
        raise ValueError("Select all three model roles and an approved online SKU.")
    if type(max_capacity) is not int or not 1 <= max_capacity <= 10000:
        raise ValueError("The capacity ceiling must be 1..10000 units per deployment.")
    if not isinstance(catalog, list):
        raise ValueError("No valid regional model catalog was returned.")
    budget = requirements(learners)
    if existing is None:
        existing = {}
    if not isinstance(existing, dict) or not set(existing) <= set(ROLES):
        raise ValueError("Existing allocations must be keyed by supported model role.")
    planned, preserved = {}, {}
    needed = defaultdict(int)
    for role in ROLES:
        selected = models[role]
        if not isinstance(selected, dict) or any(
            not isinstance(selected.get(key), str) or not selected[key] for key in ("name", "version")
        ):
            raise ValueError(f"{role}: specify an explicit model name and version.")
        sku = model_sku(catalog, selected, sku_name)
        usage_name = sku["usageName"]
        rates = catalog_unit_rates(sku)
        minimum = budget["roles"][role]
        required = max(
            math.ceil(minimum["minimum_tpm"] / rates["tpm"]),
            math.ceil(minimum["minimum_rpm"] / rates["rpm"]),
        )
        current = existing.get(role)
        allocated = 0
        settings = {"properties": {}, "sku": {}, "tags": {}}
        if current is not None:
            properties = current["properties"]
            if (
                (properties["model"].get("name"), properties["model"].get("version"),
                 properties["model"].get("format")) != (selected["name"], selected["version"], "OpenAI")
                or current["sku"]["name"] != sku_name
                or properties.get("versionUpgradeOption") != "NoAutoUpgrade"
            ):
                raise ValueError(f"{role}: resume would change the existing model, SKU, or upgrade policy.")
            allocated = current["sku"]["capacity"]
            if type(allocated) is not int or allocated < 1:
                raise ValueError(f"{role}: existing capacity is invalid.")
            required = max(required, allocated)
            settings = {
                "sku": dict(current["sku"]), "tags": dict(current.get("tags") or {}),
                "properties": {
                    key: properties[key] for key in (
                        "raiPolicyName", "scaleSettings", "capacitySettings",
                        "parentDeploymentName", "spilloverDeploymentName",
                    ) if properties.get(key) is not None
                },
            }
        units = aligned_capacity(required, sku.get("capacity"))
        if units > max_capacity and units > allocated:
            raise ValueError(f"{role}: required capacity exceeds --max-capacity; no deployment was sent.")
        needed[usage_name] += units - allocated
        preserved[role] = settings
        planned[role] = {
            "model": selected["name"], "version": selected["version"], "sku": sku_name,
            "capacity": units, "already_allocated": allocated, "additional_capacity": units - allocated,
            "usage_name": usage_name, "catalog_tpm_per_unit": rates["tpm"],
            "catalog_rpm_per_unit": rates["rpm"], "planned_tpm": units * rates["tpm"],
            "planned_rpm": units * rates["rpm"], **minimum,
        }
    verify_quota(usages, needed)
    return {
        "schema": "contoso-initial-model-capacity-v1", "learners": learners,
        "roles": planned, "preserved_deployments": preserved,
        "source": "Regional model/SKU catalog and quota preflight; not an execution measurement.",
    }


def deployment_id(state: dict, role: str) -> str:
    return (
        f"{state['resource_group_id']}/providers/Microsoft.CognitiveServices/accounts/"
        f"{state['account_name']}/deployments/{state['model_deployments'][role]}"
    )


def validate_deployment(current: dict, expected_id: str) -> None:
    if (
        not isinstance(current, dict) or not isinstance(current.get("id"), str)
        or not isinstance(current.get("sku"), dict) or not isinstance(current.get("properties"), dict)
        or not isinstance(current["properties"].get("model"), dict)
        or not isinstance(current["sku"].get("name"), str)
        or type(current["sku"].get("capacity")) is not int or current["sku"]["capacity"] < 1
        or not isinstance(current["properties"]["model"].get("name"), str)
        or not isinstance(current["properties"]["model"].get("version"), str)
        or not current["properties"]["model"]["name"] or not current["properties"]["model"]["version"]
        or "provisioningState" not in current["properties"]
    ):
        raise ValueError("Deployment readback is missing identity, SKU, or model properties.")
    if current["id"].lower() != expected_id.lower():
        raise ValueError("Deployment readback is outside owned scope.")


def inspect_deployments(state: dict, plan: dict, roles: list[str] | tuple[str, ...],
                        management: Management) -> tuple[dict, dict]:
    if not roles or len(roles) != len(set(roles)) or not set(roles) <= set(ROLES):
        raise ValueError("Select distinct supported model roles.")
    group = management.call("group", "show", "--subscription", state["subscription"],
                            "--name", state["resource_group"])
    if (
        not isinstance(group, dict) or not isinstance(group.get("tags"), dict)
        or str(group.get("id", "")).lower() != state["resource_group_id"].lower()
        or group["tags"].get("validationRun") != state["run_id"]
        or group["tags"].get("repository") != "microsoft-foundry-labs-v1.5"
    ):
        raise ValueError("Live resource group ownership does not match the receipt.")
    account = management.call(
        "cognitiveservices", "account", "show", "--subscription", state["subscription"],
        "--resource-group", state["resource_group"], "--name", state["account_name"],
    )
    account_id = state["resource_group_id"] + "/providers/Microsoft.CognitiveServices/accounts/" + state["account_name"]
    if (
        not isinstance(account, dict) or str(account.get("id", "")).lower() != account_id.lower()
        or str(account.get("location", "")).lower() != state["location"].lower()
    ):
        raise ValueError("Account identity/region differs from the receipt; quota scope is not verified.")
    report, originals = {}, {}
    for role in roles:
        current = management.call(
            "rest", "--method", "get", "--url", deployment_id(state, role) + f"?api-version={API_VERSION}",
            "--subscription", state["subscription"],
        )
        validate_deployment(current, deployment_id(state, role))
        if current["properties"]["provisioningState"] != "Succeeded":
            raise ValueError(f"{role}: deployment is not ready.")
        sku = current["sku"]
        if sku["name"] not in ONLINE_SKUS or type(sku.get("capacity")) is not int or sku["capacity"] < 1:
            raise ValueError("Only existing usage-based online deployments can be sized; no PTU changes.")
        model = current["properties"]["model"]
        if model.get("format") != "OpenAI":
            raise ValueError("This course capacity path supports OpenAI-format deployments only.")
        expected = state.get("model_configuration", {})
        for field, suffix in (("name", "Model"), ("version", "Version")):
            if role + suffix in expected and expected[role + suffix] != model.get(field):
                raise ValueError(f"{role}: deployed model identity differs from the ownership receipt.")
        rates = rate_limits(current)
        minimum = plan["roles"][role]
        required = max(
            sku["capacity"],
            math.ceil(sku["capacity"] * minimum["minimum_tpm"] / rates["tpm"]),
            math.ceil(sku["capacity"] * minimum["minimum_rpm"] / rates["rpm"]),
        )
        report[role] = {
            "deployment": state["model_deployments"][role], "model": model["name"],
            "subscription": state["subscription"],
            "version": model["version"], "sku": sku["name"], "capacity": sku["capacity"],
            **rates, **minimum, "proposed_capacity": required,
            "ready": rates["tpm"] >= minimum["minimum_tpm"] and rates["rpm"] >= minimum["minimum_rpm"],
        }
        originals[role] = current
    return report, originals


def require_ready(report: dict) -> None:
    if not report or any(not isinstance(item, dict) or type(item.get("ready")) is not bool for item in report.values()):
        raise ValueError("No valid deployment readiness results were provided.")
    insufficient = [role for role, item in report.items() if not item["ready"]]
    if insufficient:
        raise ValueError(f"TPM/RPM below the lab minimum for {', '.join(insufficient)}. Configure first; no model test was sent.")


def check_ready(receipt: Path, roles: tuple[str, ...] = ("chat",), learners: int = 1,
                az_call: Callable | None = None, *, expected_endpoint: str | None = None,
                expected_deployment: str | None = None) -> dict:
    state = load_scope(receipt, roles=roles)
    if expected_endpoint is not None and state["project_endpoint"].rstrip("/") != expected_endpoint.rstrip("/"):
        raise ValueError("Capacity receipt and execution endpoint differ; no model call was sent.")
    if expected_deployment is not None and state["model_deployments"]["chat"] != expected_deployment:
        raise ValueError("Capacity receipt and execution deployment differ; no model call was sent.")
    report, _ = inspect_deployments(state, requirements(learners), roles, Management(az_call))
    require_ready(report)
    return report


def apply_capacity(state: dict, report: dict, originals: dict, management: Management,
                   evidence: Evidence, max_capacity: int) -> dict:
    if type(max_capacity) is not int or not 1 <= max_capacity <= 10000:
        raise ValueError("The explicit capacity ceiling must be 1..10000 units per deployment.")
    changes = {role: item for role, item in report.items() if not item["ready"]}
    if not changes:
        return report
    if any(item["proposed_capacity"] > max_capacity for item in changes.values()):
        raise ValueError("Required capacity exceeds --max-capacity; no changes were sent.")
    catalog = model_catalog(state, management)
    needed = defaultdict(int)
    for item in changes.values():
        sku = model_sku(catalog, {"name": item["model"], "version": item["version"]}, item["sku"])
        item["proposed_capacity"] = aligned_capacity(item["proposed_capacity"], sku.get("capacity"))
        if item["proposed_capacity"] > max_capacity:
            raise ValueError("Required SKU increment exceeds --max-capacity; no changes were sent.")
        needed[sku["usageName"]] += item["proposed_capacity"] - item["capacity"]
    usages = management.call("cognitiveservices", "usage", "list", "--subscription", state["subscription"],
                             "--location", state["location"])
    verify_quota(usages, needed)
    for role, item in changes.items():
        before = originals[role]
        sku = {**before["sku"], "capacity": item["proposed_capacity"]}
        args = [
            "rest", "--method", "patch", "--url", before["id"] + f"?api-version={API_VERSION}",
            "--subscription", state["subscription"], "--body", json.dumps({"sku": sku}),
        ]
        if before.get("etag"):
            args += ["--headers", "If-Match=" + before["etag"]]
        evidence.append("capacity_change_requested", {"role": role, "before": item, "target_sku": sku})
        management.call(*args)
        for attempt in range(4):
            current = management.call("rest", "--method", "get",
                                      "--url", before["id"] + f"?api-version={API_VERSION}",
                                      "--subscription", state["subscription"])
            validate_deployment(current, before["id"])
            for field in ("model", "raiPolicyName", "versionUpgradeOption", "spilloverDeploymentName"):
                if current["properties"].get(field) != before["properties"].get(field):
                    raise RuntimeError(f"{role}: {field} changed; stop and inspect, do not test.")
            if current["properties"]["provisioningState"] == "Succeeded":
                rates = rate_limits(current)
                if (
                    current["sku"]["name"] == before["sku"]["name"]
                    and current["sku"]["capacity"] >= item["proposed_capacity"]
                    and rates["tpm"] >= item["minimum_tpm"] and rates["rpm"] >= item["minimum_rpm"]
                ):
                    report[role] = {**item, **rates, "capacity": current["sku"]["capacity"], "ready": True}
                    evidence.append("capacity_change_verified", {"role": role, **report[role]})
                    break
            if current["properties"]["provisioningState"] in {"Failed", "Canceled"}:
                raise RuntimeError(f"{role}: capacity update failed; preserve the partial-change receipt.")
            if attempt == 3:
                raise RuntimeError(f"{role}: capacity update not verified within the bounded readback.")
            time.sleep(min(10, management.remaining()))
    return report


async def smoke_test(state: dict, report: dict, management: Management, evidence: Evidence) -> list[dict]:
    require_ready(report)
    if not report or not set(report) <= set(ROLES):
        raise ValueError("Smoke tests require distinct supported roles.")
    from azure.ai.projects.aio import AIProjectClient
    from azure.identity.aio import AzureCliCredential, get_bearer_token_provider
    from openai import AsyncOpenAI

    results = []
    data = ROOT / "data" / ("en" if LANGUAGE == "en" else "")
    policy = (data / "policies/procurement-policy.md").read_text(encoding="utf-8")
    question = (
        "Using only this synthetic Contoso policy, name the approver for exactly KRW 2,000,000. Do not perform actions."
        if LANGUAGE == "en" else
        "이 합성 Contoso 정책만 보고 정확히 200만 원 구매에 필요한 승인자를 짧게 답하세요. 업무를 실행하지 마세요."
    )
    if estimate_tokens(question + "\n\n" + policy) > INPUT_BUDGET:
        raise ValueError("Smoke input exceeds the assumed input budget; resize the plan rather than sending it.")
    async with AzureCliCredential(subscription=state["subscription"], process_timeout=30) as credential:
        async with AIProjectClient(endpoint=state["project_endpoint"], credential=credential,
                                   retry_total=0, connection_timeout=15, read_timeout=30) as project:
            async with project.get_openai_client(max_retries=0, timeout=30) as client:
                for role in report:
                    for index in range(3 if role == "chat" else 1):
                        if results:
                            await asyncio.sleep(min(MIN_START_INTERVAL, management.remaining()))
                        if role == "embedding":
                            async with AsyncOpenAI(
                                base_url=f"https://{state['account_name']}.openai.azure.com/openai/v1/",
                                api_key=get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default"),
                                max_retries=0, timeout=30,
                            ) as embedding_client:
                                response = await embedding_client.embeddings.create(
                                    model=report[role]["deployment"], input=[policy[:4000]],
                                    timeout=min(30, management.remaining()),
                                )
                            if not response.data or not response.data[0].embedding:
                                raise RuntimeError("Embedding smoke test returned no vector.")
                            record = {"role": role, "dimensions": len(response.data[0].embedding),
                                      "input_tokens": response.usage.prompt_tokens}
                        else:
                            response = await client.responses.create(
                                model=report[role]["deployment"], input=question + "\n\n" + policy,
                                max_output_tokens=OUTPUT_BUDGET, store=False,
                                timeout=min(30, management.remaining()),
                            )
                            if response.status != "completed" or not response.output_text.strip() or not response.id:
                                raise RuntimeError(f"{role}: incomplete smoke response; no retry.")
                            record = {"role": role, "response_id": response.id, "answer": response.output_text,
                                      "usage": response.usage.model_dump() if response.usage else None}
                        record["index"] = index + 1
                        results.append(record)
                        evidence.append("model_smoke_completed", record)
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "check", "apply", "test"))
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--receipt", type=Path, default=ROOT / "results/azure-environment.json")
    parser.add_argument("--learners", type=int, default=1)
    parser.add_argument("--roles", choices=ROLES, nargs="+", default=list(ROLES))
    parser.add_argument("--confirm", help="Exact owned run_id; required for capacity changes and model tests.")
    parser.add_argument("--max-capacity", type=int, default=100)
    args = parser.parse_args(argv)
    plan = requirements(args.learners)
    if args.action == "apply" and not 1 <= args.max_capacity <= 10000:
        raise ValueError("The capacity ceiling must be 1..10000 units per deployment.")
    if len(args.roles) != len(set(args.roles)):
        raise ValueError("Specify each model role only once.")
    plan["roles"] = {role: plan["roles"][role] for role in args.roles}
    if args.action == "plan" or not args.live:
        print(json.dumps({"action": args.action, "mode": "plan_only", **plan}, ensure_ascii=False, indent=2))
        return 0
    state = load_scope(args.receipt, roles=args.roles)
    if args.action in {"apply", "test"} and args.confirm != state["run_id"]:
        raise ValueError("Explicit --confirm matching the owned run_id is required; no request was sent.")
    from azure.core.exceptions import AzureError
    from openai import OpenAIError

    evidence = Evidence("model-capacity")
    management = Management()
    try:
        report, originals = inspect_deployments(state, plan, args.roles, management)
        evidence.append("capacity_observed", {"plan": plan, "deployments": report})
        if args.action == "apply":
            report = apply_capacity(state, report, originals, management, evidence, args.max_capacity)
        require_ready(report)
        tests = asyncio.run(asyncio.wait_for(
            smoke_test(state, report, management, evidence), timeout=management.remaining(),
        )) if args.action == "test" else []
        result = {
            "checked_at": datetime.now(timezone.utc).isoformat(), "action": args.action,
            "language": LANGUAGE, "resource_group": state["resource_group"],
            "project_endpoint_sha256": digest(state["project_endpoint"]),
            "deployments": report, "model_test_requests": len(tests),
            "scope": "Capacity/readiness and bounded connectivity smoke only; not full course or quality validation.",
            "quality_release": False, "max_seconds": MAX_SECONDS, "model_retries": 0,
        }
        evidence.append("completed", result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired, AzureError, OpenAIError) as error:
        evidence.failure(error)
        raise
    finally:
        print(f"Evidence: {evidence.path}")


if __name__ == "__main__":
    raise SystemExit(main())
