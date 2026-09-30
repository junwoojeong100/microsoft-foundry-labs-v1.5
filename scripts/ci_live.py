"""Bound an explicitly approved OIDC job to one RG/project, then deploy and inspect a draft."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from evidence import Evidence, digest
from hosted_client import azd
from workshop import RESULTS, save_json


def required(name: str) -> str:
    value = os.environ.get(name, "")
    if not value or "YOUR-" in value:
        raise ValueError(f"Missing approved CI environment variable: {name}")
    return value


def run() -> None:
    if required("GITHUB_REPOSITORY") != "junwoojeong100/foundry-labs-v1.5":
        raise ValueError("Live workflow is restricted to repository A, not forks.")
    subscription, tenant = required("AZURE_SUBSCRIPTION_ID"), required("AZURE_TENANT_ID")
    project_id, rg = required("AZURE_AI_PROJECT_ID"), required("AZURE_RESOURCE_GROUP")
    expected = f"/subscriptions/{subscription}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/"
    if not project_id.lower().startswith(expected.lower()) or "/projects/" not in project_id:
        raise ValueError("Project ARM ID is outside the approved RG.")
    result = subprocess.run(["az", "account", "show", "--output", "json"], capture_output=True, text=True, check=True)
    account = json.loads(result.stdout)
    if account["id"] != subscription or account["tenantId"] != tenant or account["user"]["type"] != "servicePrincipal":
        raise ValueError("OIDC account/tenant/principal mismatch.")
    environment = "contoso-ci-" + required("GITHUB_RUN_ID")
    azd("env", "new", environment, "--no-prompt")
    for key in (
        "AZURE_SUBSCRIPTION_ID", "AZURE_TENANT_ID", "AZURE_RESOURCE_GROUP", "AZURE_LOCATION", "AZURE_AI_PROJECT_ID",
        "AZURE_AI_PROJECT_ENDPOINT", "FOUNDRY_PROJECT_ENDPOINT", "FOUNDRY_MODEL_DEPLOYMENT_NAME",
        "FOUNDRY_SEARCH_ENDPOINT", "FOUNDRY_SEARCH_INDEX", "FOUNDRY_KNOWLEDGE_BASE",
        "FOUNDRY_EMBEDDING_DEPLOYMENT_NAME",
        "FOUNDRY_EMBEDDING_ENDPOINT",
    ):
        azd("env", "set", key, required(key))
    evidence = Evidence("ci")
    summary = {"status": "started", "workflow_run_id": os.environ["GITHUB_RUN_ID"]}
    try:
        evidence.append("deploy", azd("deploy", "contoso-purchasing", "--no-prompt", timeout=1200))
        show = json.loads(azd("ai", "agent", "show", "contoso-purchasing", "--output", "json"))
        evidence.append("deployed_agent", show)
        values = json.loads(azd("env", "get-values", "--output", "json"))
        version = values.get("AGENT_CONTOSO_PURCHASING_VERSION", "")
        if not re.fullmatch(r"[1-9]\d*", version):
            raise ValueError("azd did not return an exact deployed version.")
        subprocess.run([
            sys.executable, "samples/hosted_client.py", "invoke", "--version", version, "--live",
            "--query", "NB-14 2대 구매 요청 초안을 만들어줘. 실제 주문은 하지 마.",
        ], cwd=ROOT, check=True, timeout=420)
        responses = sorted(RESULTS.glob("contoso-hosted-client-*-responses.jsonl"), key=lambda p: p.stat().st_mtime)
        row = json.loads(responses[-1].read_text())
        drafts = [call for call in row["tool_calls"] if call["name"] == "prepare_purchase_request" and call["output"]["ok"]]
        if len(drafts) != 1:
            raise ValueError("CI did not observe exactly one successful purchase-draft tool call.")
        draft = drafts[0]["output"]["result"]
        if draft["total_krw"] != 2_900_000 or draft["order_submitted"] or draft["required_approvals"] != ["team_lead", "procurement"]:
            raise ValueError("CI business contract failed.")
        summary = {
            "status": "business_smoke_passed", "hosted_version": version, "response_id": row["response_id"],
            "workflow_run_id": os.environ["GITHUB_RUN_ID"], "business_checks": "draft-only, 2900000 KRW, both approvals",
            "full_quality_gate": "not_claimed_by_smoke",
        }
        save_json(ROOT / "validation/current/ci.json", summary)
        calibration = subprocess.run([sys.executable, "samples/evaluation_lab.py", "calibrate", "--live"], cwd=ROOT, check=False, timeout=720)
        evidence.append("calibration_exit", {"returncode": calibration.returncode})
        summary["calibration"] = "passed" if calibration.returncode == 0 else "failed"
        save_json(ROOT / "validation/current/ci.json", summary)
        holdout = ROOT / "validation/current/holdout-responses.jsonl"
        if holdout.exists():
            held = [json.loads(line) for line in holdout.read_text(encoding="utf-8").splitlines()]
            if any(
                item.get("execution_location") != "azure"
                or item.get("environment_sha256") != digest(required("FOUNDRY_PROJECT_ENDPOINT").rstrip("/"))
                or item.get("contract", {}).get("sha256") != row["contract"]["sha256"]
                or item.get("model") != row["model"] for item in held
            ):
                raise ValueError("Recorded holdout does not match this approved environment, code, or model. Collect fresh evidence.")
            held_result = subprocess.run([sys.executable, "samples/evaluation_lab.py", "run", "--input", str(holdout),
                                         "--split", "holdout", "--live"], cwd=ROOT, check=False, timeout=720)
            evidence.append("holdout_exit", {"returncode": held_result.returncode})
            if held_result.returncode:
                summary["holdout"] = "failed_or_partial"
                raise RuntimeError("CI holdout evaluation failed or is partial; original service outputs are retained.")
            audits = sorted(RESULTS.glob("contoso-native-run-*-audit.json"), key=lambda p: p.stat().st_mtime)
            audit = json.loads(audits[-1].read_text())
            summary["holdout"] = {key: audit[key] for key in ("pass_rate", "critical_failures", "contradictions", "business_gate_passed")}
            summary["human_review_completed"] = False
            save_json(ROOT / "validation/current/ci.json", summary)
            if not audit["business_gate_passed"]:
                raise RuntimeError("CI holdout business gate failed; no threshold was changed.")
        if calibration.returncode:
            raise RuntimeError("Calibration failed. Any holdout scores are untrusted and cannot release the agent.")
        summary["status"] = "passed"
        save_json(ROOT / "validation/current/ci.json", summary)
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as exc:
        evidence.failure(exc)
        summary["status"] = "failed"
        summary["error_type"] = type(exc).__name__
        native = []
        for path in RESULTS.glob("contoso-native-*.json"):
            result = json.loads(path.read_text())
            if "items" not in result:
                continue
            valid, invalid = [], []
            for item in result["items"]:
                rows = [row for row in item.get("results", []) if row.get("name") == "contoso_business"]
                case_id = item.get("datasource_item", {}).get("id")
                if len(rows) == 1 and isinstance(rows[0].get("score"), (int, float)) and type(rows[0].get("passed")) is bool:
                    valid.append({"id": case_id, "score": rows[0]["score"], "passed": rows[0]["passed"]})
                else:
                    invalid.append(case_id)
            native.append({"eval_id": result["eval_id"], "run_id": result["run_id"],
                           "service_status": result["status"], "valid_judgments": valid, "invalid_or_missing": invalid})
        summary["native_runs"] = native
        save_json(ROOT / "validation/current/ci.json", summary)
        raise


if __name__ == "__main__":
    run()
