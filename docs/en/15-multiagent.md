> **What you will build:** A two-stage flow that separates drafting and review without letting the model perform real approval.

## Objectives

**Adding more agents is not the goal.** Add orchestration only when roles, tools, and evaluation criteria are genuinely separate.

**Important:** Foundry portal Workflows is in Preview and **scheduled to retire on 2026-12-01**. This module uses **Microsoft Agent Framework** for new implementation.

## Concepts and lab map

**What you will try:** Sequential orchestration in Microsoft Agent Framework, remote A2A delegation, and human approval boundaries.

**What is it, and why does it matter?** Orchestration is code that defines the order of tasks and how results are passed between them. A drafter→reviewer flow in the same process has different failure and authentication boundaries from A2A requests to another service. Separating roles can separate expertise, but it also increases call counts, latency, and permission-management work. Do not mistake the reviewer's wording for real business approval or independent quality validation.

**How do you use it?** Read the local plan first, inspect the inputs and outputs of both stages, and compare them with a single agent. For A2A, verify the agent card's capabilities separately from the actual delegation result. The model saying “I delegated it” does not establish that a downstream network call occurred.

**Where do you run it?** [multi_agent.py](../../samples/multi_agent.py) uses a separate MAF environment; [a2a_lab.py](../../samples/a2a_lab.py) uses the core SDK environment. Be sure to distinguish the Python environments between these command groups. Do not introduce portal Workflows as a new dependency.

## Prerequisites

You need the project, model, and `.env` from L01, plus a separate Python environment. Do not overwrite the core-course environment.

As checked on 2026-09-29, `agent-framework-foundry==1.13.1` requires `azure-ai-projects<2.7.0`. The core course uses 2.7.0. **Separate environments with compatible dependencies** are provided.

## Steps

### 1. Inspect the local plan

```bash
python samples/multi_agent.py
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `multi_agent.py` | Prints only the sequential flow of the two roles. Without `--live`, it does not call a Foundry model. | Inspect the `drafter → reviewer` structure. No deployment or Azure charges. |

</div>

This prints only the `drafter → reviewer` plan and makes no Azure calls.

### 2. Install the advanced environment

```bash
python3 -m venv .venv-advanced
.venv-advanced/bin/python -m pip install -r requirements-advanced.txt
.venv-advanced/bin/python -m pip check
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `python3 -m venv .venv-advanced` | Creates a MAF environment separate from the core SDK. Also check the installed Python version against the requirements. | Creates a local environment without changing the core `.venv`. |
| 2. `.venv-advanced/bin/python -m pip install` | Explicitly uses the advanced environment's Python to install the compatible combination in `-r requirements-advanced.txt`. | Downloads packages and changes the advanced environment. No Azure calls. |
| 3. `.venv-advanced/bin/python -m pip check` | Checks that specific advanced environment for dependency conflicts. | If it fails, inspect the installed combination instead of indiscriminately mixing in core-environment packages. |

</div>

On Windows, use `.venv-advanced\Scripts\python.exe`. Use a package repository allowed by your administration policy.

### 3. Run both agents live

```bash
.venv-advanced/bin/python samples/multi_agent.py --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `multi_agent.py --live` | Runs the drafter and reviewer sequentially in the MAF environment, calling Foundry models. | Model inference charges apply. Orchestration is local; this is neither a Hosted deployment nor completed real approval. Compare each role's output and the added latency. |

</div>

This example runs Microsoft Agent Framework locally and calls Foundry models. **It does not deploy a Hosted Agent.** Both roles explicitly receive the same synthetic policies; this is not a RAG example for evaluating retrieval quality.

| Role | Input | Result | Not allowed |
| --- | --- | --- | --- |
| drafter | Request and policies | Draft purchasing guidance | Claiming an order was completed when it was not |
| reviewer | Draft and policies | Final guidance after reviewing boundary values and approval rules | Real business approval |

The core flow is:

```python
workflow = WorkflowBuilder(
    start_executor=drafter,
    output_from=[reviewer],
    max_iterations=4,
).add_edge(drafter, reviewer).build()
```

### 4. Compare with a single agent

Record accuracy, tokens, and total latency for the same question. If the two-agent result is merely longer, return to a single agent. Calling a role “reviewer” does not create independent validation or a security boundary.

<details markdown="1">
<summary>When to choose other orchestration patterns</summary>

| Pattern | When to choose it | Cost/failure considerations |
| --- | --- | --- |
| Sequential | The next stage reviews the previous stage's result | Total latency accumulates |
| Concurrent | Independent research or evaluation | Parallel token costs and conflicting results |
| Handoff | Transfer conversation control to a specialist | Permission and history scope |
| Group/Magentic | Complex work requiring planning and role coordination | Iteration limits and stop conditions |
| Explicit workflow graph | Conditional branches, checkpoints, and human input | Managing failure/resume state |

</details>

### 5. Perform real A2A delegation

A2A integrates an agent from another service or vendor. It differs from the in-process MAF flow above.
Run this path in the **core/`.venv-live` SDK environment**. Do not mix A2A 1.0 GA with 0.3 Preview.

```bash
python samples/a2a_lab.py create
python samples/a2a_lab.py create --live
python scripts/runtime_roles.py --agent results/a2a.json의-caller --live
python samples/a2a_lab.py card --live
python samples/a2a_lab.py invoke --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Return to the core/`.venv-live` SDK environment first.

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `a2a_lab.py create` | Reads the creation plan for the worker, coordinator, and connection. | No Azure requests. |
| 2. `create --live` | Actually configures a new policy worker, coordinator, and A2A connection. | Creates remote objects and `results/a2a.json`. Do not assume it reuses an existing agent. |
| 3. `runtime_roles.py --agent ... --live` | Replace `results/a2a.json의-caller` with the `caller` value in that JSON. Grants the project-scoped invocation role to the owned caller's runtime identity. | An administrator task because it changes real permissions. The JSON file path itself is not the agent name. |
| 4. `card --live` | Reads the owned worker's actual incoming agent card to check the connection contract. | Reads remote metadata. This is separate from successfully answering a business question. |
| 5. `invoke --live` | Sends a synthetic request to the coordinator and checks delegation to the remote worker and the returned items. | Real model/agent invocation charges. Do not mark delegation as successful without evidence of an A2A call. |

</div>

The bundled code creates a new Contoso policy worker and coordinator, connecting an incoming A2A agent card
and an `agentic-identity` connection. The worker/caller versions in `results/a2a.json` are pinned.
The administrator must grant the new caller identity the minimum project role needed to invoke that worker.
When reading a card directly, the Foundry 1.0 path is `agentCard/v1.0`. Do not confuse it with the general `.well-known/agent-card.json` path.
By contrast, an `A2ATool` pointing to Foundry omits `agent_card_path` to use the service's default resolution.
If an existing lab caller's connection needs correction, `rebind --live` creates a new version while preserving the previous one.
If the actual returned items contain no A2A call, a sentence saying “I delegated it” is not enough to count as success.
Do not infer downstream responses hidden by the service; record response/task IDs only to the extent that they are actually exposed.

At the approval stage, store an actual approval request ID and the human's decision instead of **a model-generated “I approve”**, and verify that the approved content has not changed. The L06 sample performs no real business action, so do not pretend it completed an approval process.

## Success criteria

Verify execution evidence separately for both MAF stages and for remote A2A delegation.
You can explain whether the added cost over a single agent is justified.
HITL remains a design exercise; do not mark real business approval as completed.

## Troubleshooting

For SDK import errors, first check for mixed environments. This sample uses the core `WorkflowBuilder` and does not require a separate `agent-framework-orchestrations` package. Other documentation examples using `SequentialBuilder` may require an additional package.

## Cleanup

Record model invocation costs. For production use, apply L14's hosted runtime and L22's release gates.
