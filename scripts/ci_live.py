"""Bound an explicitly approved OIDC job to one RG/project, then deploy and inspect a draft."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))
from evidence import Evidence, digest, redacted
from hosted_client import azd
from evaluation_data import DEFAULT_SUITE, policy, suite_hash, verify_development_freeze
from business_checks import check_business_evidence
from lab_profile import active_prompt, validation_for
from workshop import DATA, LANGUAGE, RESULTS, save_json


def required(name: str) -> str:
    value = os.environ.get(name, "")
    if not value or "YOUR-" in value:
        raise ValueError(f"Missing approved CI environment variable: {name}")
    return value


def native_evidence() -> list[dict]:
    runs = []
    for path in sorted(RESULTS.glob("contoso-native-*.json")):
        result = json.loads(path.read_text())
        if "items" not in result:
            continue
        judgments = []
        for item in result["items"]:
            rows = [{
                key: value for key, value in row.items()
                if key in {"name", "metric", "score", "passed", "reason", "threshold", "status"}
            } for row in item.get("results", [])]
            judgments.append({"id": item.get("datasource_item", {}).get("id"), "results": rows})
        audit_path = path.with_name(path.stem + "-audit.json")
        audit = json.loads(audit_path.read_text()) if audit_path.exists() else None
        if audit:
            audit = {key: value for key, value in audit.items() if key != "judge_verdicts"}
        runs.append({
            "eval_id": result["eval_id"], "run_id": result["run_id"], "service_status": result["status"],
            "judgments": judgments, "audit": audit,
        })
    return redacted(runs)


def run(phase: str) -> None:
    if required("GITHUB_REPOSITORY_ID") != "1396573688":
        raise ValueError("Live workflow is restricted to repository A, not forks.")
    if LANGUAGE == "en" and phase in {"dev", "release", "optimizer"}:
        verify_development_freeze(DEFAULT_SUITE)
    dev_gate = None
    if DEFAULT_SUITE == "automated-v5" and phase == "release":
        from evaluation_lab import verify_gate
        dev_gate = verify_gate(DEFAULT_SUITE, "dev")
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
    if phase == "auth":
        from cloud import project_client
        with project_client() as (project, _, endpoint, _):
            agent = project.agents.get("contoso-purchasing")
        save_json(validation_for(ROOT) / DEFAULT_SUITE / "ci-auth.json", {
            "status": "passed", "phase": "auth", "repository_id": required("GITHUB_REPOSITORY_ID"),
            "repository": required("GITHUB_REPOSITORY"), "workflow_run_id": os.environ["GITHUB_RUN_ID"],
            "agent_read": agent.name, "environment_sha256": digest(endpoint),
            "model_calls": 0, "deployments": 0, "resource_changes": 0,
        })
        return
    if phase == "optimizer":
        baseline_version = required("FOUNDRY_OPTIMIZER_AGENT_VERSION") if LANGUAGE == "en" else "2"
        if not re.fullmatch(r"[1-9]\d*", baseline_version):
            raise ValueError("Optimizer CI requires an explicitly pinned numeric baseline version.")
        optimizer_suite = DEFAULT_SUITE if LANGUAGE == "en" else "automated-v2"
        optimizer_prompt = active_prompt() if LANGUAGE == "en" else DATA / "prompts/agent-v4.txt"
        from azure_environment import az
        group = az("group", "show", "--subscription", subscription, "--name", rg)
        project = az("rest", "--method", "get", "--url", project_id + "?api-version=2025-06-01")
        account_id = project_id.rsplit("/projects/", 1)[0]
        run_id = group.get("tags", {}).get("validationRun")
        if not run_id:
            raise ValueError("Optimizer may run only in the owned validation RG.")
        insights_id = group["id"] + "/providers/Microsoft.Insights/components/appi-" + run_id
        app_id = az("rest", "--method", "get", "--url", insights_id + "?api-version=2020-02-02",
                    "--query", "properties.AppId")
        identity = az("identity", "show", "--subscription", subscription, "--resource-group", rg,
                      "--name", "id-" + run_id)
        if identity["clientId"] != required("AZURE_CLIENT_ID"):
            raise ValueError("Optimizer CI identity is not the owned federated identity.")
        save_json(RESULTS / "azure-environment.json", {
            "schema": "contoso-environment-v1", "language": LANGUAGE, "subscription": subscription, "tenant": tenant,
            "repository": required("GITHUB_REPOSITORY"), "repository_id": "1396573688", "location": required("AZURE_LOCATION"),
            "resource_group": rg, "resource_group_id": group["id"], "run_id": run_id,
            "project_endpoint": required("FOUNDRY_PROJECT_ENDPOINT"),
            "account_name": account_id.rsplit("/", 1)[-1], "project_name": project_id.rsplit("/", 1)[-1],
            "foundation": {"accountId": {"value": account_id}, "projectId": {"value": project_id},
                           "projectPrincipalId": {"value": project["identity"]["principalId"]}},
            "monitoring": {"appId": {"value": app_id}, "appInsightsId": {"value": insights_id}},
            "oidc": {"client_id": identity["clientId"], "principal_id": identity["principalId"]},
        })
        probe = subprocess.run([
            sys.executable, "samples/optimizer_lab.py", "--probe-reflection",
            "--optimizer-deployment", "contoso-reflection", "--require-oidc", "--live",
        ], cwd=ROOT, check=False, timeout=90)
        if probe.returncode:
            raise RuntimeError("Same-principal reflection probe failed; no optimizer job submitted.")
        result = subprocess.run([
            sys.executable, "samples/optimizer_lab.py", "--agent", "contoso-purchasing-responses",
            "--version", baseline_version, "--optimizer-deployment", "contoso-reflection",
            "--suite", optimizer_suite, "--prompt-file", str(optimizer_prompt), "--require-oidc", "--live",
            "--max-seconds", "1200" if LANGUAGE == "en" else "600",
        ], cwd=ROOT, check=False, timeout=1560 if LANGUAGE == "en" else 960)
        terminal = []
        for path in RESULTS.glob("contoso-optimizer-*-terminal.json"):
            terminal.append(redacted(json.loads(path.read_text())))
        save_json(validation_for(ROOT) / "optimizer-oidc/result.json", {
            "workflow_run_id": os.environ["GITHUB_RUN_ID"], "returncode": result.returncode,
            "target_agent": "contoso-purchasing-responses", "target_version": baseline_version,
            "suite": optimizer_suite, "purpose": "dev-only OIDC optimization; not an independent release-quality claim",
            "terminal_results": terminal,
        })
        if result.returncode:
            raise RuntimeError("Native optimizer operational check failed; see preserved terminal result.")
        return
    evidence = Evidence("ci")
    output_dir = validation_for(ROOT) / DEFAULT_SUITE
    summary_path = output_dir / f"ci-{phase}.json"
    summary = {"status": "started", "phase": phase, "evaluation_suite": DEFAULT_SUITE,
               "evaluation_suite_sha256": suite_hash(), "workflow_run_id": os.environ["GITHUB_RUN_ID"],
               "human_review_required": False, "human_review_status": "optional_guidance_only"}
    try:
        if dev_gate is None:
            evidence.append("deploy", azd("deploy", "contoso-purchasing", "--no-prompt", timeout=1200))
            show = json.loads(azd("ai", "agent", "show", "contoso-purchasing", "--output", "json"))
            evidence.append("deployed_agent", show)
            values = json.loads(azd("env", "get-values", "--output", "json"))
            version = values.get("AGENT_CONTOSO_PURCHASING_VERSION", "")
        else:
            version = dev_gate["configuration"]["hosted_version"]
        if not re.fullmatch(r"[1-9]\d*", version):
            raise ValueError("azd did not return an exact deployed version.")
        subprocess.run([
            sys.executable, "samples/hosted_client.py", "invoke", "--version", version, "--live",
            "--query", (
                "Prepare a purchase request draft for NB-14, quantity 2. Do not place an order."
                if LANGUAGE == "en" else "NB-14 2대 구매 요청 초안을 만들어줘. 실제 주문은 하지 마."
            ),
        ], cwd=ROOT, check=True, timeout=420)
        responses = sorted(RESULTS.glob("contoso-hosted-client-*-responses.jsonl"), key=lambda p: p.stat().st_mtime)
        row = json.loads(responses[-1].read_text())
        proof = check_business_evidence(row, {"required_tools": ["prepare_purchase_request"]}, require_tool_definitions=True)
        if not proof["passed"]:
            raise ValueError(f"CI grounding/business proof failed: {proof['failures']}")
        drafts = [call for call in row["tool_calls"] if call["name"] == "prepare_purchase_request" and call["output"]["ok"]]
        if len(drafts) != 1:
            raise ValueError("CI did not observe exactly one successful purchase-draft tool call.")
        draft = drafts[0]["output"]["result"]
        if draft["total_krw"] != 2_900_000 or draft["order_submitted"] or draft["required_approvals"] != ["team_lead", "procurement"]:
            raise ValueError("CI business contract failed.")
        summary.update({
            "status": "business_smoke_passed", "hosted_version": version, "response_id": row["response_id"],
            "workflow_run_id": os.environ["GITHUB_RUN_ID"], "business_checks": "draft-only, 2900000 KRW, both approvals",
            "full_quality_gate": "not_claimed_by_smoke",
            "runtime_contract": row["contract"]["sha256"],
            "model": row["model"], "effective_prompt_sha256": row["effective_prompt_sha256"],
        })
        save_json(summary_path, summary)
        if phase == "release":
            dev_report_path = output_dir / "ci-dev.json"
            dev_responses_path = output_dir / "dev-responses.jsonl"
            if not dev_report_path.exists() or not dev_responses_path.exists():
                raise ValueError("Release requires the committed successful dev artifact; no holdout is opened.")
            dev_report = json.loads(dev_report_path.read_text())
            dev_responses = [json.loads(line) for line in dev_responses_path.read_text(encoding="utf-8").splitlines()]
            if (
                dev_report.get("status") != "passed" or dev_report.get("phase") != "dev"
                or dev_report.get("calibration") != "passed"
                or not dev_report.get("dev", {}).get("business_gate_passed")
                or dev_report.get("evaluation_suite_sha256") != suite_hash()
                or len(dev_responses) != policy()["required_dev_cases"]
                or any(
                    item.get("contract", {}).get("sha256") != row["contract"]["sha256"]
                    or item.get("model") != row["model"]
                    or item.get("effective_prompt_sha256") != row["effective_prompt_sha256"]
                    for item in dev_responses
                )
            ):
                raise ValueError("Dev artifact is not successful or its frozen runtime/model differs; holdout remains unopened.")
        calibration = (
            None if dev_gate is not None else
            subprocess.run([sys.executable, "samples/evaluation_lab.py", "calibrate", "--suite", DEFAULT_SUITE, "--live"],
                           cwd=ROOT, check=False, timeout=810)
        )
        calibrated = dev_gate is not None or calibration.returncode == 0
        evidence.append("calibration", {
            "source": "verified_preserved_native_gate" if dev_gate is not None else "new_native_run",
            "returncode": None if calibration is None else calibration.returncode,
        })
        summary["calibration"] = "passed" if calibrated else "failed"
        save_json(summary_path, summary)
        if not calibrated:
            raise RuntimeError("Calibration failed. No fresh development/holdout responses are collected with an unready judge.")
        if DEFAULT_SUITE == "automated-v5" and dev_gate is None:
            subprocess.run([sys.executable, "scripts/share_evidence.py", "--suite", DEFAULT_SUITE,
                            "--gate", "calibration"], cwd=ROOT, check=True, timeout=60)
        split = "dev" if phase == "dev" else "holdout"
        records = output_dir / (split + "-responses.jsonl")
        if not records.exists():
            subprocess.run([
                sys.executable, "samples/hosted_client.py", "evaluate", "--split", split, "--suite", DEFAULT_SUITE,
                "--version", version, "--case-delay", "3", "--live",
            ], cwd=ROOT, check=True, timeout=1380)
            candidates = sorted(RESULTS.glob("contoso-hosted-client-*-responses.jsonl"), key=lambda p: p.stat().st_mtime)
            subprocess.run([sys.executable, "scripts/share_evidence.py", "--input", str(candidates[-1]),
                            "--split", split, "--suite", DEFAULT_SUITE], cwd=ROOT, check=True, timeout=60)
        if records.exists():
            held = [json.loads(line) for line in records.read_text(encoding="utf-8").splitlines()]
            if any(
                item.get("execution_location") != "azure"
                or item.get("environment_sha256") != digest(required("FOUNDRY_PROJECT_ENDPOINT").rstrip("/"))
                or item.get("contract", {}).get("sha256") != row["contract"]["sha256"]
                or item.get("model") != row["model"] for item in held
            ):
                raise ValueError("Recorded responses differ from the approved environment, code, or model.")
            held_result = subprocess.run([sys.executable, "samples/evaluation_lab.py", "run", "--input", str(records),
                                         "--split", split, "--suite", DEFAULT_SUITE, "--live"], cwd=ROOT, check=False, timeout=810)
            evidence.append("evaluation_exit", {"split": split, "returncode": held_result.returncode})
            if held_result.returncode:
                summary[split] = "failed_or_partial"
                raise RuntimeError(f"CI {split} evaluation failed or is partial; original service outputs are retained.")
            audits = sorted(RESULTS.glob("contoso-native-run-*-audit.json"), key=lambda p: p.stat().st_mtime)
            audit = json.loads(audits[-1].read_text())
            summary[split] = {key: audit[key] for key in ("pass_rate", "critical_failures", "contradictions", "business_gate_passed")}
            summary["human_review_completed"] = False
            save_json(summary_path, summary)
            if not audit["business_gate_passed"]:
                raise RuntimeError("CI business gate failed; no threshold was changed.")
            if DEFAULT_SUITE == "automated-v5" and split == "dev":
                subprocess.run([sys.executable, "scripts/share_evidence.py", "--suite", DEFAULT_SUITE,
                                "--gate", "dev"], cwd=ROOT, check=True, timeout=60)
        else:
            raise RuntimeError("No complete response set; a smoke test alone cannot pass evaluation.")
        if not calibrated:
            raise RuntimeError("Calibration failed. Any holdout scores are untrusted and cannot release the agent.")
        summary["status"] = "passed"
        summary["quality_release"] = phase == "release"
        summary["native_runs"] = native_evidence()
        save_json(summary_path, summary)
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as exc:
        evidence.failure(exc)
        summary["status"] = "failed"
        summary["error_type"] = type(exc).__name__
        summary["native_runs"] = native_evidence()
        from share_evidence import FIELDS
        for path in RESULTS.glob("contoso-hosted-client-*-responses.jsonl"):
            values = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            if values and any(row.get("status") != "completed" for row in values):
                filtered = [{key: value for key, value in row.items() if key in FIELDS | {"error"}} for row in values]
                save_json(output_dir / (path.stem + "-partial.json"), redacted(filtered))
        save_json(summary_path, summary)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=["dev", "release", "optimizer", "auth"], default="release")
    run(parser.parse_args().phase)
