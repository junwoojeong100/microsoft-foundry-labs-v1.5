> **What you will build:** A Prompt Agent with a clear role and clear limits—a baseline version before adding knowledge and tools.

<div class="lab-brief" markdown="1">

**Format:** Create and test the agent in the Foundry portal, then trace the same settings in raw SDK code.

**Start here:** Create a Text agent with L02's model and the bundled English instructions.

**What to check:** No invented policies or stock values; compare the same conversation with a new one. Keep this agent for L05.

</div>

## Objectives

A Prompt Agent is a managed agent declared through **model + instructions + tools**. You do not operate a separate server or container yourself. L12 explains how it differs from a Hosted Agent.

## Concepts and lab map

**What you will try:** Create a Prompt Agent with a role and continue a conversation.

**What is it, and why does it matter?** Instructions tell the agent how to behave. Calling it an “inventory assistant” does not provide inventory access. Starting without documents or tools makes the additions in L05 and L06 visible.

**How do you use it?** Save the model and instructions, then ask the questions. Check that the same conversation retains context and a new conversation starts separately.

**Where do you run it?** Paste the [English instructions](../../data/en/prompts/agent-v2.txt) into the portal, then match Model, Instructions, and Tools to the Python values below. `workshop.py` is the separate receipt- and call-bounded SDK runner.

## Prerequisites

You need project `Foundry User` access, a callable model, and `data/en/prompts/agent-v2.txt`. Keep L01's English profile selected for the SDK path.

## Steps

### 1. Create the agent in the portal

1. Select **Build → Agents → New agent → Build an agent**. Some UI versions show **Build an agent** directly.
2. Choose your own unique name, such as `contoso-procurement-en-your-unique-suffix`, and **Text** mode. If a goal is required, enter “Explain synthetic Contoso purchasing policies without placing real orders.” For an existing name, verify it belongs to your prior lab; do not modify another person's agent.
3. In the editor that opens, select L02's deployment under **Model**. Open `data/en/prompts/agent-v2.txt` in VS Code and paste **the complete file contents** into Instructions, not the file path. Do not reuse Korean instructions.
4. Select **Save** and record the agent name and displayed version. Confirm **the model matches, instructions are saved, and no knowledge or function tools are attached yet**, then move to Chat on the right.

Reuse this agent in L05. It **must not claim to have used unavailable tools**. The exercise sends five inputs: two boundary questions, two in the same conversation, and one in a new conversation. Send each only once within the approved scope.

![Prompt Agent configuration example, with English instructions, model/tools settings, conversation input, and version controls.](../../assets/portal/en/04-prompt-playground.png)

**Reading the screen:** Check the deployment name under **Model** and the prompt under **Instructions** on the left, then enter test questions in **Chat** on the right. **Version** at the top identifies the configuration version; **New chat** separates conversation contexts. **Save** changes configuration, while **Send** submits a billable request. Confirm your purpose before clicking either.

The image is a configuration example with later integrations. **Save only the instructions in L04.** File search belongs to L05 and function tools to L06, so you do not need to match those connections yet.

| Portal action | Matching SDK value or operation |
| --- | --- |
| Select the L02 deployment under **Model** | `model=deployment_name` |
| Paste the full instruction text | `Path("data/en/prompts/agent-v2.txt").read_text(...)` |
| Leave **Tools** empty | `tools=[]` |
| Save the configuration | `project.agents.create_version(...)` |
| Start **New chat** | `client.conversations.create()` |
| Enter a question and select **Send** | `client.responses.create(..., extra_body={"agent_reference": ...})` |

The portal expresses the same configuration through fields; the SDK expresses it through arguments. Create and test the agent in the portal for L04. The code below makes the API operations behind those controls visible.

### 2. Check the limits with baseline questions

```prompt
What is the price limit for our company's standard laptop?
```

Without a policy file, the agent must not act as though it knows the KRW 1,500,000 limit. At this stage, the correct behavior is to say that it needs the policy or a knowledge connection.

```prompt
Check the real-time inventory for NB-14.
```

With no tool connected, a claim of a successful lookup is a failure. **“I don't know” can be the correct answer.**

### 3. Experiment with conversation state

Send these two inputs in order within the same conversation.

```prompt
In this conversation, I am considering buying a monitor.
```

```prompt
Tell me the item I am considering, in one word.
```

Check that the answer is “monitor.” Start a new conversation and send only the second question. The item from the previous conversation should not carry over automatically. **Conversation continuity and long-term Memory are separate capabilities.**

### 4. Distinguish names, versions, conversations, and responses

| Unit | What it identifies or when it changes |
| --- | --- |
| Agent name | Identifies one logical agent |
| Agent version | Saves changes to the instructions, model, or tools as a configuration version |
| Conversation | Starts an independent conversation context |
| Response | Represents one model/agent execution within a conversation |

Record the saved name/version separately from each response ID. Do not change instructions merely to increment a version. When you later change configuration, check the new version; “latest” does not mean “approved for production.”

<details class="implementation-detail" markdown="1">
<summary>Implementation reference: portal Model, Instructions, and Save in SDK code — read only</summary>

### 5. Read the same configuration in raw Python SDK code

This teaching excerpt connects the SDK calls used by `create_lab_agent()` and `run_turn()` in `workshop.py`. The endpoint is your own; the deployment is `contoso-chat`. **Read the block**, then choose either portal creation or the receipt-tracked SDK path below for execution.

```python
from pathlib import Path
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import AzureCliCredential

project_endpoint = "<Project endpoint from L01>"
deployment_name = "<deployment name from L02>"
agent_name = "<unique-sdk-agent-name>"
instructions = Path("data/en/prompts/agent-v2.txt").read_text(encoding="utf-8")

with (
    AzureCliCredential(process_timeout=30) as credential,
    AIProjectClient(
        endpoint=project_endpoint,
        credential=credential,
        retry_total=0,
    ) as project,
    project.get_openai_client(max_retries=0, timeout=60.0) as client,
):
    agent = project.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=deployment_name,
            instructions=instructions,
            tools=[],
        ),
        description="Synthetic workshop agent; never submit real orders.",
    )
    conversation = client.conversations.create()
    response = client.responses.create(
        conversation=conversation.id,
        input="What is the price limit for our company's standard laptop?",
        extra_body={
            "agent_reference": {
                "name": agent.name,
                "type": "agent_reference",
                "version": agent.version,
            }
        },
        max_output_tokens=2048,
    )
    if response.status != "completed" or not response.output_text or not response.output_text.strip():
        raise RuntimeError(f"Response not complete: {response.status}")
    print(response.output_text)
    print(f"response_id={response.id}")
```

`conversation.id` is the new chat context; `agent_reference` points to the exact version above. With no policy file attached, withholding an unsupported limit is correct.

Executing this raw code creates a separate agent and conversation and incurs model costs. For live SDK work, use the runner below, which adds an owned-scope receipt, bounded calls, and a `--live` opt-in. Do not run both portal and SDK paths.

</details>

<details class="optional-path" markdown="1">
<summary>Optional: run the complete receipt- and call-bounded SDK runner</summary>

```bash
python samples/workshop.py agent
python samples/workshop.py agent --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Use this only if SDK is your execution path.

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `agent` | Prints the plan for creating and invoking a Prompt Agent. With the English profile selected, the default instruction file is `data/en/prompts/agent-v2.txt`. | No Azure requests. First distinguish capabilities described in the instructions from tools that will actually be connected. |
| 2. `agent --live` | Creates a uniquely named `contoso-lab-...` agent and conversation, then obtains a real model response. It does not modify the agent created in the portal. | Incurs inference/service costs and creates new lab objects. Keep the printed receipt path for cleanup in L19. |

</div>

`workshop.py` adds plan-only behavior, a unique receipt, error handling, and call limits around the raw operations above. It creates a **new agent** named `contoso-lab-...` to avoid collisions; it does not modify your portal agent. Created IDs are saved in `results/contoso-lab-....json`.

The default input is **one price-limit question**, not the five portal questions or the same/new-conversation comparison. To continue that comparison, open the receipt's agent name in the portal and perform the relevant questions; otherwise record **conversation comparison not run**. The L05 SDK path creates another agent rather than attaching files to this one.

</details>

## Success criteria

The instructions define the role, grounding requirements, handling of missing information and tool failures, and prohibited actions. The agent retains context within the same conversation and does not pretend that unavailable knowledge or tools produced a successful result.

## Troubleshooting

Earlier conversation context can mask an instruction change. After selecting the new version, also test in a **new conversation**. Do not mix SDK 1.x Threads/Runs code into the 2.x sample.

## Cleanup

Reuse the portal agent in L05. If you chose SDK, distinguish the new agent created by L05's SDK File search path and keep each receipt. Delete only the exact approved resources in L19.

<div class="lab-handoff" markdown="1">

**Keep:** Your agent name/version, the five answers, and conversation distinctions. A portal-created agent has no automatic SDK receipt, so record its name yourself.

**Continue:** [L05 company documents](#l05). The default path reuses **this same portal agent**.

</div>
