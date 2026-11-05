"""Real MAF builders with deterministic synthetic responses, never an Azure measurement."""

import asyncio
from contextlib import contextmanager
import re
from unittest.mock import patch

from agent_framework import (
    BaseChatClient, ChatMiddlewareLayer, ChatResponse, Content, FunctionInvocationLayer, Message,
)


@contextmanager
def without_network():
    with (
        patch("socket.socket.connect", side_effect=RuntimeError("Offline MAF fixtures forbid network access.")),
        patch("socket.socket.connect_ex", side_effect=RuntimeError("Offline MAF fixtures forbid network access.")),
        patch("socket.getaddrinfo", side_effect=RuntimeError("Offline MAF fixtures forbid DNS lookups.")),
    ):
        yield


class FixtureChatClient(FunctionInvocationLayer, ChatMiddlewareLayer, BaseChatClient):
    def __init__(self):
        super().__init__()
        self.calls = []
        self.active = 0
        self.maximum_active = 0

    async def _inner_get_response(self, *, messages, stream, options, **kwargs):
        if stream:
            raise ValueError("The offline fixture supports complete, non-streaming responses only.")
        instruction = str(options.get("instructions", "")) + "\n" + "\n".join(message.text for message in messages)
        roles = re.findall(r"Role: ([a-z-]+)\.", instruction)
        if not roles:
            raise ValueError("The fixture request has no role label.")
        role = roles[0]
        index = len(self.calls) + 1
        self.calls.append({
            "role": role, "messages": [message.to_dict() for message in messages],
            "instructions": options.get("instructions"),
        })
        self.active += 1
        self.maximum_active = max(self.maximum_active, self.active)
        try:
            await asyncio.sleep(0.01)
            if role == "coordinator":
                if "handoff_to_policy" not in [tool.name for tool in options.get("tools", [])]:
                    raise ValueError("HandoffBuilder did not expose the expected routing tool.")
                contents = [Content.from_function_call(
                    call_id=f"fixture-call-{index}", name="handoff_to_policy", arguments={},
                )]
                finish = "tool_calls"
            else:
                contents = [Content.from_text(f"Synthetic fixture from {role}, call {index}.")]
                finish = "stop"
            return ChatResponse(
                messages=[Message(role="assistant", contents=contents, author_name=role)],
                response_id=f"fixture-response-{index}", finish_reason=finish,
                usage_details={"input_token_count": 10, "output_token_count": 5},
            )
        finally:
            self.active -= 1


async def run_fixture(mode, case, evidence):
    from multi_agent import CALLS, LANGUAGE, MAX_SECONDS, QUESTIONS, CallAudit, compare_paths

    client = FixtureChatClient()
    audit = CallAudit(evidence, CALLS[mode], interval=0)
    with without_network():
        report = await asyncio.wait_for(compare_paths(
            client, mode, QUESTIONS[LANGUAGE][case], evidence, audit=audit,
        ), timeout=MAX_SECONDS)
    return {
        "schema": "contoso-maf-orchestrations-v1", "execution": "local_sdk_fixture",
        "language": LANGUAGE, "mode": mode, "case": case, "question": QUESTIONS[LANGUAGE][case],
        "azure_calls": 0, "max_model_calls": CALLS[mode], "fixture_calls": len(client.calls),
        "maximum_active_fixture_calls": client.maximum_active,
        "usage_source": "synthetic_fixture_not_billing",
        "routing_source": "fixed_policy_fixture_not_model_classification",
        **report,
    }
