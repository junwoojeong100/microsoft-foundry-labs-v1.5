"""Intentionally flawed local Responses payload exercise. Never calls Azure."""

import json


def continuation(conversation_id: str, function_call: dict, result: dict) -> dict:
    return {
        "conversation": function_call["id"],
        "input": [{
            "type": "function_call_output",
            "call_id": function_call["id"],
            "output": result,
        }],
    }
