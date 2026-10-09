"""Actual remote A2A delegation, separate from the in-process MAF example."""

from __future__ import annotations

import argparse
import json
import subprocess
from uuid import uuid4

from cloud import Rest, project_client
from evidence import Budget, Evidence
from lab_cli import run
from workshop import DATA, LANGUAGE, RESULTS, ensure_response, save_json

STATE = RESULTS / "a2a.json"


def run(command: str, evidence: Evidence) -> None:
    from azure.ai.projects.models import (
        A2AProtocolConfiguration, A2ATool, AgentCard, AgentCardSkill,
        AgentEndpointConfig, PromptAgentDefinition, ProtocolConfiguration, ResponsesProtocolConfiguration,
    )

    with project_client(evidence) as (project, cred, endpoint, model), project.get_openai_client(max_retries=0, timeout=90) as client:
        if command == "create":
            if STATE.exists():
                raise ValueError("A2A receipt exists; keep existing versions and inspect them.")
            suffix = uuid4().hex[:8]
            worker_name, caller_name = "contoso-policy-worker-" + suffix, "contoso-coordinator-" + suffix
            state = {"endpoint": endpoint, "worker": worker_name, "caller": caller_name, "connection": "contoso-a2a-" + suffix}
            save_json(STATE, state)
            worker = project.agents.create_version(
                agent_name=worker_name, definition=PromptAgentDefinition(
                    model=model,
                    instructions=(
                        ("You review Contoso purchasing policies. Use only the following synthetic policy. "
                         "Explain the rules in English; never approve a purchase or place an order. Cite the document ID and section.\n"
                         if LANGUAGE == "en" else
                         "너는 Contoso 구매 정책 검토 담당이다. 다음 합성 정책만 사용한다. "
                         "규칙을 설명할 뿐 실제 승인·주문을 하지 않는다. 문서 ID와 절을 명시한다.\n")
                        + (DATA / "policies/procurement-policy.md").read_text(encoding="utf-8")
                    ),
                ),
            )
            state["worker_version"] = worker.version
            save_json(STATE, state)
            evidence.append("worker_created", worker)
            enabled = project.agents.update_details(
                agent_name=worker.name,
                agent_endpoint=AgentEndpointConfig(protocol_configuration=ProtocolConfiguration(
                    responses=ResponsesProtocolConfiguration(), a2a=A2AProtocolConfiguration(),
                )),
                agent_card=AgentCard(
                    version="1.0", description="Contoso purchase policy review; no order or approval execution",
                    skills=[AgentCardSkill(id="policy-review", name="Contoso policy review", description="Review purchasing limits and approval roles")],
                ),
            )
            evidence.append("incoming_a2a_enabled", enabled)
            target = f"{endpoint}/agents/{worker.name}/endpoint/protocols/a2a"
            result = subprocess.run([
                "azd", "ai", "connection", "create", state["connection"], "--kind", "remote-a2a",
                "--target", target, "--auth-type", "agentic-identity", "--audience", "https://ai.azure.com",
                "--project-endpoint", endpoint, "--no-prompt",
            ], capture_output=True, text=True, timeout=120, check=False)
            evidence.append("connection_create", {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
            if result.returncode:
                raise RuntimeError("A2A connection creation failed; inspect the receipt, do not blindly recreate.")
            connection = project.connections.get(state["connection"], include_credentials=False)
            caller = project.agents.create_version(
                agent_name=caller_name, definition=PromptAgentDefinition(
                    model=model, instructions=(
                        "You are the Contoso coordinator. Delegate purchasing-policy questions to the remote policy-review agent "
                        "and answer in English using its actual result. Report delegation failures explicitly. Never approve or order."
                        if LANGUAGE == "en" else
                        "너는 Contoso 조정자다. 구매 정책 질문은 반드시 원격 policy-review agent에 위임하고 "
                        "그 실제 결과로 한국어 답변한다. 위임 실패는 실패로 알린다. 실제 승인·주문을 하지 않는다."
                    ),
                    tools=[A2ATool(
                        a2a_version="1.0", project_connection_id=connection.id, base_url=target,
                        send_credentials_for_agent_card=True,
                    )],
                ),
            )
            evidence.append("caller_created", caller)
            state.update(caller_version=caller.version, target=target, connection_id=connection.id)
            save_json(STATE, state)
            return
        state = json.loads(STATE.read_text(encoding="utf-8"))
        if state["endpoint"] != endpoint:
            raise ValueError("A2A receipt belongs to another project.")
        if command == "rebind":
            previous = project.agents.get_version(state["caller"], state["caller_version"])
            caller = project.agents.create_version(
                agent_name=state["caller"], definition=PromptAgentDefinition(
                    model=model, instructions=previous.definition.instructions,
                    tools=[A2ATool(
                        a2a_version="1.0", project_connection_id=state["connection_id"],
                        base_url=state["target"],
                        send_credentials_for_agent_card=True,
                    )],
                ),
            )
            evidence.append("caller_rebound", caller)
            state.setdefault("previous_caller_versions", []).append(state["caller_version"])
            state["caller_version"] = caller.version
            save_json(STATE, state)
            return
        if command == "card":
            rest = Rest(endpoint, cred, "https://ai.azure.com/.default", evidence, Budget(max_requests=1))
            card = rest.request("GET", f"/agents/{state['worker']}/endpoint/protocols/a2a/agentCard/v1.0")
            evidence.append("agent_card", card)
            print(json.dumps(card, ensure_ascii=False, indent=2))
            return
        response = client.responses.create(
            input=(
                "Ask the policy-review agent which roles must approve two laptops totaling KRW 2,900,000."
                if LANGUAGE == "en" else "총액 290만 원인 노트북 2대의 구매 승인 역할을 정책 검토 agent에게 확인해줘."
            ),
            extra_body={"agent_reference": {"type": "agent_reference", "name": state["caller"], "version": state["caller_version"]}},
            max_output_tokens=2048,
        )
        evidence.append("delegation_response", response)
        text = ensure_response(response)
        calls = [item for item in response.output if "a2a" in item.type]
        if not calls:
            raise RuntimeError("No actual A2A output item: a natural-language delegation claim is not proof.")
        evidence.append("verified", {"response_id": response.id, "caller_version": state["caller_version"], "worker_version": state["worker_version"], "a2a_items": calls})
        print(text)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["create", "card", "invoke", "rebind"])
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if not args.live:
        print(f"PLAN ONLY: A2A {args.command}; no remote operations.")
        return
    evidence = Evidence("a2a")
    try:
        run(args.command, evidence)
    except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        evidence.failure(exc)
        raise
    finally:
        print(f"Evidence: {evidence.path}")


if __name__ == "__main__":
    run(main)
