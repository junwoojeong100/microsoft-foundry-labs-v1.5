"""Two-agent Microsoft Agent Framework example; plan-only without --live."""

import argparse
import asyncio

from workshop import DATA, LANGUAGE, read_config


def build_workflow(client):
    from agent_framework import Agent, WorkflowBuilder

    policy = (DATA / "policies/procurement-policy.md").read_text(encoding="utf-8")
    drafter = Agent(
        client=client, name="drafter",
        instructions=(
            "Draft purchasing guidance in English using only the following synthetic policy. You have no tool or order authority.\n"
            if LANGUAGE == "en" else "다음 합성 정책만 사용해 구매 안내 초안을 작성한다. 도구·주문 권한은 없다.\n"
        ) + policy,
    )
    reviewer = Agent(
        client=client, name="reviewer",
        instructions=(
            "Compare the draft with the policy. Check the total and approval boundaries, then return corrected guidance in English. "
            "State explicitly that this is a review draft, not an approval or an order.\n"
            if LANGUAGE == "en" else
            "이전 초안을 정책과 대조하라. 총액과 승인 경계를 검사하고 수정한 최종 안내를 한국어로 답하라. "
            "실제 승인·주문이 아니라 검토 초안임을 명시하라.\n"
        ) + policy,
    )
    return WorkflowBuilder(
        start_executor=drafter, output_from=[reviewer], max_iterations=4,
    ).add_edge(drafter, reviewer).build()


async def run() -> None:
    from agent_framework import AgentResponse
    from agent_framework.foundry import FoundryChatClient
    from azure.ai.projects.aio import AIProjectClient
    from azure.identity.aio import AzureCliCredential

    endpoint, model = read_config()
    async with (
        AzureCliCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project,
    ):
        client = FoundryChatClient(project_client=project, model=model)
        async with client.client:
            workflow = build_workflow(client)
            events = await workflow.run(
                "I need two laptops at KRW 1,450,000 each. Explain the purchasing policy and approval process."
                if LANGUAGE == "en" else "단가 145만 원인 노트북 2대를 구매하려 한다. 정책과 승인 절차를 안내해줘."
            )
            outputs = events.get_outputs()
            responses = [item for item in outputs if isinstance(item, AgentResponse) and item.text.strip()]
            if not responses:
                raise RuntimeError("Workflow returned no final AgentResponse; inspect workflow events.")
            for response in responses:
                print(response.text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if args.live:
        asyncio.run(run())
    else:
        print("PLAN ONLY: drafter -> reviewer. Two model calls; no business actions or Azure provisioning.")
        print("Use the isolated .venv-advanced environment and --live to run.")
