"""Validate installed SDK contracts without fetching credentials or using a network."""

import argparse
import asyncio
import importlib.metadata
import inspect
import json
from pathlib import Path
import sys
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "samples"))


class OfflineCredential:
    def get_token(self, *args, **kwargs):
        raise AssertionError("SDK contract checks must not acquire a token.")


async def check_workflow_execution():
    from agent_framework import BaseChatClient, ChatResponse, ChatResponseUpdate, Content, Message, ResponseStream
    from multi_agent import build_workflow, compare_paths

    class FixtureClient(BaseChatClient):
        def __init__(self):
            super().__init__()
            self.inputs = []

        def _inner_get_response(self, *, messages, stream, options, **kwargs):
            messages = list(messages)
            self.inputs.append([message.text for message in messages])
            reviewing = any(message.text == "fixture-draft" for message in messages)
            text = "fixture-reviewed" if reviewing else "fixture-draft"
            final = ChatResponse(
                messages=[Message("assistant", [text])], response_id=f"fixture-{len(self.inputs)}",
                finish_reason="stop",
                usage_details={"input_token_count": 10, "output_token_count": 5, "total_token_count": 15},
            )

            async def complete():
                return final

            async def updates():
                yield ChatResponseUpdate(contents=[Content.from_text(text)], role="assistant", response_id=final.response_id)

            return ResponseStream(updates(), finalizer=lambda _: final) if stream else complete()

    client = FixtureClient()
    events = await build_workflow(client).run("Offline synthetic workflow contract check.")
    outputs = events.get_outputs()
    assert len(client.inputs) == 2, "Both agent executors must run exactly once."
    assert any("fixture-draft" in message for message in client.inputs[1]), "Reviewer must receive the draft."
    assert any(getattr(output, "text", "") == "fixture-reviewed" for output in outputs), "Workflow must yield the reviewer's output."
    assert [item.text for item in events.get_intermediate_outputs()] == ["fixture-draft"]
    comparison_client = FixtureClient()
    report = await compare_paths(comparison_client, "compare", "Synthetic local fixture only.", Mock())
    assert len(comparison_client.inputs) == 3
    assert report["paths"]["single"]["total_tokens"] == 15
    assert report["paths"]["sequential"]["total_tokens"] == 30
    assert report["sequential_minus_single"]["total_tokens"] == 15
    assert [stage["role"] for stage in report["paths"]["sequential"]["stages"]] == ["drafter", "reviewer"]
    return {"executors_run": 2, "reviewer_received_draft": True, "final_output_verified": True,
            "intermediate_output_verified": True, "comparison_fixture_calls": 3,
            "fixture_usage_verified": True, "azure_measurement": False}


def main(advanced=False):
    packages = ["azure-ai-projects", "azure-identity", "openai"]
    if advanced:
        packages.append("agent-framework-foundry")
    try:
        versions = {package: importlib.metadata.version(package) for package in packages}
    except importlib.metadata.PackageNotFoundError as exc:
        requirements = "requirements-advanced.txt" if advanced else "requirements.txt"
        raise SystemExit(f"SDK dependencies missing: {exc.name}. In the intended virtual environment, run: python -m pip install -r {requirements}") from None
    workflow_result = None
    with patch("socket.socket.connect", side_effect=AssertionError("Network is forbidden in SDK contract checks.")):
        from azure.ai.projects import AIProjectClient
        from azure.ai.projects.models import FileSearchTool, FunctionTool, PromptAgentDefinition
        from workshop import function_schemas
        tools = [FileSearchTool(vector_store_ids=["vs_contract"])] + [FunctionTool(**schema) for schema in function_schemas()]
        payload = PromptAgentDefinition(model="contract-only", instructions="Synthetic contract check", tools=tools).as_dict()
        assert payload["kind"] == "prompt"
        assert payload["tools"][0]["type"] == "file_search"
        assert payload["tools"][1]["name"] == "get_stock"
        assert payload["tools"][2]["parameters"]["additionalProperties"] is False
        with (
            AIProjectClient(
                endpoint="https://contract.services.ai.azure.com/api/projects/contract",
                credential=OfflineCredential(), retry_total=0,
            ) as project,
            project.get_openai_client(max_retries=0, timeout=60.0) as client,
        ):
            assert "agent_name" in inspect.signature(project.agents.create_version).parameters
            assert "agent_name" in inspect.signature(project.agents.delete).parameters
            assert "file_id" in inspect.signature(client.vector_stores.files.create).parameters
            assert "file_id" in inspect.signature(client.vector_stores.files.retrieve).parameters
            assert "conversation" in inspect.signature(client.responses.create).parameters
            assert "extra_body" in inspect.signature(client.responses.create).parameters
        if advanced:
            from agent_framework.foundry import FoundryChatClient
            from multi_agent import build_workflow
            versions["agent-framework-foundry"] = importlib.metadata.version("agent-framework-foundry")
            chat = FoundryChatClient(
                project_endpoint="https://contract.services.ai.azure.com/api/projects/contract",
                model="contract-only", credential=OfflineCredential(),
            )
            workflow = build_workflow(chat)
            assert callable(workflow.run)
            assert callable(chat.client.__aenter__) and callable(chat.client.__aexit__)
            async def close_clients():
                await chat.client.close()
                await chat.project_client.close()
            asyncio.run(close_clients())
            workflow_result = asyncio.run(check_workflow_execution())
    print(json.dumps({"sdk_contracts": "passed", "azure_calls": 0, "versions": versions, "offline_workflow": workflow_result}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--advanced", action="store_true")
    args = parser.parse_args()
    main(args.advanced)
