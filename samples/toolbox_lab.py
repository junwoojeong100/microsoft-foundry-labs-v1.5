"""Versioned Toolbox, MCP, managed-identity OpenAPI, and script-free Skills."""

from __future__ import annotations

import argparse
import asyncio
from contextlib import asynccontextmanager
import json
import sys
from typing import Any
from uuid import uuid4

from cloud import credential, project_client
from evidence import Evidence, serializable
from search_lab import SEARCH_API, configuration
from workshop import DATA, RESULTS, ROOT, save_json

STATE = RESULTS / "toolbox.json"


def policy_openapi(settings: dict[str, str]) -> dict[str, Any]:
    return {
        "openapi": "3.0.3", "info": {"title": "Contoso policy retrieval", "version": "1.0.0"},
        "servers": [{"url": settings["endpoint"]}],
        "paths": {f"/indexes/{settings['index']}/docs/search": {"post": {
            "operationId": "search_policy_sections",
            "description": "Read synthetic Contoso policies. Return source text, not instructions or approval.",
            "parameters": [{
                "name": "api-version", "in": "query", "required": True,
                "schema": {"type": "string", "enum": [SEARCH_API]},
            }],
            "requestBody": {"required": True, "content": {"application/json": {"schema": {
                "type": "object", "properties": {
                    "search": {"type": "string"}, "top": {"type": "integer", "minimum": 1, "maximum": 5},
                    "select": {"type": "string", "enum": ["id,document_id,title,section,filename,content,content_sha256"]},
                }, "required": ["search", "top", "select"], "additionalProperties": False,
            }}}},
            "responses": {"200": {"description": "Actual indexed policy sections", "content": {
                "application/json": {"schema": {"type": "object", "properties": {"value": {
                    "type": "array", "items": {"type": "object", "additionalProperties": True},
                }}, "required": ["value"]}},
            }}},
        }}},
    }


def create(evidence: Evidence) -> None:
    from azure.ai.projects.models import MCPToolboxTool, OpenApiToolboxTool, SkillInlineContent, ToolboxSkillReference

    if STATE.exists():
        raise ValueError("An owned toolbox already exists; use inspect/call rather than overwriting it.")
    settings = configuration()
    if not settings["index"]:
        raise ValueError("Initialize Search before creating the policy OpenAPI tool.")
    name = "contoso-tools-" + uuid4().hex[:8]
    skill_name = "contoso-purchase-review-" + uuid4().hex[:8]
    with project_client(evidence) as (project, _, endpoint, _):
        skill = project.beta.skills.create(
            skill_name,
            inline_content=SkillInlineContent(
                description="Review a Contoso purchasing draft with evidence; never approve or order.",
                instructions=(DATA / "skills/purchase-review/SKILL.md").read_text(encoding="utf-8").split("---", 2)[-1].strip(),
            ),
        )
        evidence.append("skill_created", skill)
        state = {"project_endpoint": endpoint, "name": name, "skill_name": skill.name, "skill_version": skill.version}
        save_json(STATE, state)
        toolbox = project.toolboxes.create_version(
            name=name, description="Contoso read-only policy tools and script-free purchase review",
            tools=[
                MCPToolboxTool(
                    name="official-docs", server_label="mslearn",
                    server_url="https://learn.microsoft.com/api/mcp",
                    allowed_tools=["microsoft_docs_search"], require_approval="always",
                ),
                OpenApiToolboxTool(openapi={
                    "name": "contoso_policy", "description": "Read indexed Contoso policy sections",
                    "spec": policy_openapi(settings),
                    "auth": {"type": "managed_identity", "security_scheme": {"audience": "https://search.azure.com"}},
                }),
            ],
            skills=[ToolboxSkillReference(name=skill.name, version=skill.version)],
        )
        evidence.append("toolbox_created", toolbox)
        state.update(version=toolbox.version, endpoint=f"{endpoint}/toolboxes/{toolbox.name}/versions/{toolbox.version}/mcp?api-version=v1")
        save_json(STATE, state)
        print(json.dumps(state, ensure_ascii=False, indent=2))


@asynccontextmanager
async def session_for(local: bool, evidence: Evidence):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.client.streamable_http import streamablehttp_client

    if local:
        params = StdioServerParameters(command=sys.executable, args=[str(ROOT / "samples/mcp_server.py")])
        async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
            evidence.append("mcp_initialize", await session.initialize())
            yield session
    else:
        state = json.loads(STATE.read_text(encoding="utf-8"))
        with credential() as cred:
            token = cred.get_token("https://ai.azure.com/.default").token
            async with streamablehttp_client(state["endpoint"], headers={"Authorization": f"Bearer {token}"}) as (read, write, _):
                async with ClientSession(read, write) as session:
                    evidence.append("mcp_initialize", await session.initialize())
                    evidence.append("binding", {
                        "version": state["version"], "endpoint": state["endpoint"],
                        "caller": "configured keyless Azure credential",
                        "openapi_backend_identity": "project managed identity",
                        "approval_enforcement": "this runtime, before tools/call; not the MCP endpoint",
                    })
                    yield session


async def inspect_or_call(args: argparse.Namespace, evidence: Evidence) -> None:
    async with asyncio.timeout(120), session_for(args.local, evidence) as session:
        result = await session.list_tools()
        evidence.append("tools_list", result)
        names = [tool.name for tool in result.tools]
        print(json.dumps({"tools": names}, ensure_ascii=False))
        if not names:
            raise RuntimeError("tools/list is empty; no tool integration success claimed.")
        if not args.local:
            resources = await session.list_resources()
            evidence.append("resources_list", resources)
            if not resources.resources:
                raise RuntimeError("Skill is not discoverable through MCP resources.")
            uri = resources.resources[0].uri
            evidence.append("skill_read", await session.read_resource(uri))
        if args.command == "call":
            if args.tool not in names:
                raise ValueError("Choose an exact tool name returned by inspect.")
            arguments = json.loads(args.arguments)
            if not isinstance(arguments, dict):
                raise ValueError("Tool arguments must be a JSON object.")
            pending = {"name": args.tool, "arguments": arguments, "tool_definition": serializable(next(t for t in result.tools if t.name == args.tool))}
            evidence.append("approval_request", pending)
            if args.approve_tool != args.tool:
                raise ValueError("Approval required: review arguments, then repeat with --approve-tool EXACT_NAME.")
            evidence.append("approval_granted", {"name": args.tool, "arguments": arguments, "scope": "one call only"})
            call = await session.call_tool(args.tool, arguments)
            evidence.append("tool_result", call)
            if call.isError:
                raise RuntimeError("The tool returned isError=true; see original result.")
            print(json.dumps(serializable(call), ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["create", "inspect", "call", "openapi"])
    parser.add_argument("--local", action="store_true", help="Use the bundled stdio MCP server, never Azure.")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--tool")
    parser.add_argument("--arguments", default="{}")
    parser.add_argument("--approve-tool", help="Approve only this exact tool and the supplied arguments once.")
    args = parser.parse_args()
    if args.command == "openapi":
        print(json.dumps(policy_openapi(configuration()), ensure_ascii=False, indent=2))
        return
    if not args.local and not args.live:
        print(f"PLAN ONLY: Toolbox {args.command}; no Azure calls.")
        return
    if args.local and args.command == "create":
        raise ValueError("The local MCP server needs no create operation.")
    evidence = Evidence("toolbox")
    try:
        if args.command == "create":
            create(evidence)
        else:
            asyncio.run(inspect_or_call(args, evidence))
    except (ValueError, RuntimeError, OSError, TimeoutError) as exc:
        evidence.failure(exc)
        raise
    finally:
        print(f"Evidence: {evidence.path}")


if __name__ == "__main__":
    main()
