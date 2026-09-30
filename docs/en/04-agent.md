> **What you will build:** A Prompt Agent with a clear role and clear limits—a baseline version before adding knowledge and tools.

## Objectives

A Prompt Agent is a managed agent declared through **model + instructions + tools**. You do not operate a separate server or container yourself. L14 explains how it differs from a Hosted Agent.

## Concepts and lab map

**What you will try:** Prompt Agent instructions, models, versions, and conversations.

**What is it, and why does it matter?** A Prompt Agent is a managed execution unit whose role and rules are defined on the service and reused across requests. Instructions guide behavior; they do not automatically provide private company knowledge or permission to act. Naming an agent “inventory assistant” does not let it check inventory without an inventory tool. This chapter deliberately starts without knowledge or tools so that you can compare the actual difference those additions make in later chapters.

**How do you use it?** Set the model and instructions in the portal, then test missing knowledge, missing tools, the same conversation, and a new conversation in turn. Record the instruction version separately from conversation context. Observe whether the agent respects the limits of its provided capabilities, not merely whether it produces plausible text.

**Where do you run it?** The portal is the main path; the SDK provides an optional comparison. Read the [English instruction source](../../data/en/prompts/agent-v4.txt) first, then compare it with the [SDK implementation](../../samples/workshop.py). The two paths create separate agents; they do not automatically synchronize the same object.

## Prerequisites

You need project `Foundry User` access, a callable model, and `data/en/prompts/agent-v4.txt`. Keep L01's English profile selected for the SDK path.

## Steps

### 1. Create the agent in the portal

Select **Build → Agents → New agent → Build an agent**. Depending on the UI version, **New agent** may open a menu of Build, Code, template, and other paths, or the page may show **Build an agent** directly. Set the name to `contoso-procurement`, the mode to **Text**, and the model to the deployment from L02.

Paste the contents of `data/en/prompts/agent-v4.txt` into Instructions in your English project. Do not reuse a Korean agent's instructions. You have not yet attached File search or function tools, so the agent **must not claim to have used tools it does not have**.

![The Prompt Agent Playground in contoso-workshop-en, with English instructions, model/tools settings, conversation input, and version controls.](../../assets/portal/en/04-prompt-playground.png)

**Reading the screen:** Check the deployment name under **Model** and the prompt under **Instructions** on the left, then enter test questions in **Chat** on the right. **Version** at the top identifies the configuration version; **New chat** separates conversation contexts. **Save** changes configuration, while **Send** submits a billable request. Confirm your purpose before clicking either.

The screenshot concerns the English lab project; its exact agent state and capture actions are recorded in the [English capture log](../../content/portal-screenshots.en.json). If it shows File search or functions already connected, those belong to later integration steps, not the L04 baseline. A visible configuration is not proof that the agent used its tools successfully.

### 2. Check the limits with baseline questions

```text
What is the price limit for our company's standard laptop?
```

Without a policy file, the agent must not act as though it knows the KRW 1,500,000 limit. At this stage, the correct behavior is to say that it needs the policy or a knowledge connection.

```text
Check the real-time inventory for NB-14.
```

With no tool connected, a claim of a successful lookup is a failure. **“I don't know” can be the correct answer.**

### 3. Experiment with conversation state

Send these two inputs in order within the same conversation.

```text
In this conversation, I am considering buying a monitor.
```

```text
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

Edit and save an instruction, then check that a new version is created. The “latest version” is not necessarily the “version approved for production.”

### 5. Optional: Explore the same concepts with the SDK

```bash
python samples/workshop.py agent
python samples/workshop.py agent --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — An optional comparison after completing the portal exercise.

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `agent` | Prints the plan for creating and invoking a Prompt Agent. With the English profile selected, the default instruction file is `data/en/prompts/agent-v4.txt`. | No Azure requests. First distinguish capabilities described in the instructions from tools that will actually be connected. |
| 2. `agent --live` | Creates a uniquely named `contoso-lab-...` agent and conversation, then obtains a real model response. It does not modify the agent created in the portal. | Incurs inference/service costs and creates new lab objects. Keep the printed receipt path for cleanup in L12. |

</div>

To avoid name collisions, the SDK sample creates a **new agent** named `contoso-lab-...`. It does not modify the portal-created `contoso-procurement`. Created IDs are saved in `results/contoso-lab-....json`.

## Success criteria

The instructions define the role, grounding requirements, handling of missing information and tool failures, and prohibited actions. The agent retains context within the same conversation and does not pretend that unavailable knowledge or tools produced a successful result.

## Troubleshooting

Earlier conversation context can mask an instruction change. After selecting the new version, also test in a **new conversation**. Do not mix SDK 1.x Threads/Runs code into the 2.x sample.

## Cleanup

Reuse the portal agent in the next lab. Keep the receipt for the separate SDK-created agent and clean it up in L12.
