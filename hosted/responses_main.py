"""Responses adapter for native optimization; delegates to the same bounded Contoso engine."""

import asyncio
import json
import os
from pathlib import Path
import sys

from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponseEventStream

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "samples"))
from hosted_runtime import invoke

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
        # Exceptions propagate to the protocol server as failure, never as completed text.
        result = await asyncio.to_thread(invoke, {"query": query})
    message = stream.add_output_item_message()
    yield message.emit_added()
    content = message.add_text_content()
    yield content.emit_added()
    yield content.emit_delta(json.dumps(result, ensure_ascii=False))
    yield content.emit_text_done()
    yield content.emit_done()
    yield message.emit_done()
    yield stream.emit_completed()


if __name__ == "__main__":
    remote = os.environ.get("FOUNDRY_AUTH_MODE") == "managed_identity"
    app.run(host="0.0.0.0" if remote else "127.0.0.1", port=8088 if remote else int(os.environ.get("CONTOSO_LOCAL_PORT", "8088")))
