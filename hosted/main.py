"""Foundry Invocations entrypoint. A failed upstream operation remains an HTTP failure."""

import asyncio
import json
import os
from pathlib import Path
import sys

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.core.exceptions import AzureError
from openai import OpenAIError
from starlette.requests import Request
from starlette.responses import JSONResponse

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "samples"))
from evidence import Evidence
from hosted_runtime import invoke, validate_request

app = InvocationAgentServerHost(openapi_spec={
    "openapi": "3.0.3", "info": {"title": "Contoso purchasing", "version": "1.0.0"},
    "paths": {"/invocations": {"post": {
        "operationId": "contoso_purchase_assist",
        "requestBody": {"required": True, "content": {"application/json": {"schema": {
            "type": "object", "required": ["query"],
            "properties": {"query": {"type": "string", "maxLength": 4000},
                           "case_id": {"type": "string"}, "run_id": {"type": "string"}},
            "additionalProperties": False,
        }}}},
        "responses": {"200": {"description": "Evidence-bearing purchasing answer"},
                      "400": {"description": "Invalid synthetic request"}, "502": {"description": "Upstream failure"}},
    }}},
})
gate = asyncio.Semaphore(1)


@app.invoke_handler
async def handle(request: Request):
    raw = await request.body()
    if len(raw) > 32_000:
        return JSONResponse({"error": "request_too_large"}, status_code=413)
    try:
        payload = validate_request(json.loads(raw))
    except (ValueError, UnicodeDecodeError) as exc:
        return JSONResponse({"error": "invalid_request", "message": str(exc)}, status_code=400)
    async with gate:
        try:
            result = await asyncio.to_thread(invoke, payload)
            return JSONResponse(result)
        except (AzureError, OpenAIError, ValueError, RuntimeError, OSError) as exc:
            evidence = Evidence("hosted-failure")
            evidence.failure(exc)
            return JSONResponse({"error": type(exc).__name__, "run_id": evidence.run_id, "status": "failed"}, status_code=502)


if __name__ == "__main__":
    remote = os.environ.get("FOUNDRY_AUTH_MODE") == "managed_identity"
    app.run(host="0.0.0.0" if remote else "127.0.0.1", port=8088 if remote else int(os.environ.get("CONTOSO_LOCAL_PORT", "8088")))
