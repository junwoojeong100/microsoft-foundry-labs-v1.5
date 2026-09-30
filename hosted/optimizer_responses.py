"""Responses profile with explicit instruction-only optimizer model inheritance."""

import asyncio
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
if not (ROOT / "samples").is_dir():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "samples"))


def resolved_model(model, baseline_model: str, *, optimizer_overlay: bool) -> tuple[str, str]:
    if not isinstance(baseline_model, str) or not baseline_model or baseline_model == "CONFIGURE-MODEL-BEFORE-DEPLOY":
        raise ValueError("The packaged baseline must contain an explicit model deployment.")
    if model is None and optimizer_overlay:
        return baseline_model, "explicit_baseline_inheritance"
    if not isinstance(model, str) or not model.strip():
        raise ValueError("Missing or invalid model configuration; no default was substituted.")
    return model, "candidate" if optimizer_overlay else "baseline"


def invoke_configured(payload):
    import yaml
    from azure.ai.agentserver.optimization import load_config
    from cloud import project_client
    from evidence import Budget, Evidence
    from hosted_runtime import execute_turn, validate_request
    from search_lab import Search

    payload = validate_request(payload)
    evidence = Evidence("optimizer-ready-turn")
    baseline_dir = ROOT / ".agent_configs"
    baseline = yaml.safe_load((baseline_dir / "baseline/metadata.yaml").read_text())
    candidate_id = os.environ.get("OPTIMIZATION_CANDIDATE_ID", "")
    resolver = os.environ.get("OPTIMIZATION_RESOLVE_ENDPOINT", "")
    inline = bool(os.environ.get("OPTIMIZATION_CONFIG", "").strip())
    overlay = bool(candidate_id or inline)
    with project_client(evidence) as (project, cred, endpoint, _):
        if candidate_id:
            if not re.fullmatch(r"[A-Za-z0-9_-]{1,256}", candidate_id):
                raise ValueError("Invalid optimizer candidate identifier.")
            target, owned = urlparse(resolver), urlparse(endpoint)
            if target.scheme != "https" or target.netloc != owned.netloc or not target.path.startswith(owned.path + "/"):
                raise ValueError("Optimizer resolver must belong to this exact Foundry project.")
        cache_root = (
            Path.home() / ".contoso" if os.environ.get("FOUNDRY_AUTH_MODE") == "managed_identity"
            else Path(os.environ.get("CONTOSO_EVIDENCE_DIRECTORY", str(ROOT / "results")))
        )
        config_dir = cache_root / "optimization-configs" if overlay else baseline_dir
        if overlay:
            config_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        config = load_config(config_dir=config_dir, credential=cred)
        if config is None or not config.compose_instructions().strip():
            raise ValueError("Optimizer/baseline instructions are missing; no fallback answer.")
        if candidate_id and not inline and config.candidate_id != candidate_id:
            raise ValueError("Requested optimizer candidate was not resolved; refusing baseline fallback.")
        model, source = resolved_model(config.model, baseline.get("model"), optimizer_overlay=overlay)
        resolution = {
            "candidate_id": candidate_id or None, "configuration_source": config.source,
            "model_deployment": model, "model_resolution": source,
        }
        evidence.append("optimization_model_resolution", resolution)
        with project.get_openai_client(max_retries=0, timeout=60) as client:
            budget = Budget(max_requests=12, max_tokens=60000, max_seconds=300)
            result = execute_turn(client, Search(cred, client, evidence, budget), model, payload, evidence, budget,
                                  instructions=config.compose_instructions())
            result["optimization"] = resolution
            return result


def create_app():
    from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponseEventStream

    app = ResponsesAgentServerHost()
    gate = asyncio.Semaphore(1)

    @app.response_handler
    async def handle(request, context, cancellation_signal):
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        yield stream.emit_created()
        yield stream.emit_in_progress()
        query = await context.get_input_text()
        if cancellation_signal.is_set():
            yield stream.emit_incomplete("cancelled")
            return
        async with gate:
            result = await asyncio.to_thread(invoke_configured, {"query": query})
        message = stream.add_output_item_message()
        yield message.emit_added()
        content = message.add_text_content()
        yield content.emit_added()
        yield content.emit_delta(json.dumps(result, ensure_ascii=False))
        yield content.emit_text_done()
        yield content.emit_done()
        yield message.emit_done()
        yield stream.emit_completed()

    return app


if __name__ == "__main__":
    remote = os.environ.get("FOUNDRY_AUTH_MODE") == "managed_identity"
    create_app().run(host="0.0.0.0" if remote else "127.0.0.1",
                     port=8088 if remote else int(os.environ.get("CONTOSO_LOCAL_PORT", "8089")))
