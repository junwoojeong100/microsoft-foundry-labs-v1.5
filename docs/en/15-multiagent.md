> **What you will build:** A two-stage flow that separates drafting and review without letting the model perform real approval.

<div class="lab-brief" markdown="1">

**Format:** Advanced elective · two local roles and remote A2A are separate experiments.

**Start here:** Run `python samples/multi_agent.py --mode compare` to inspect the single baseline and drafter → reviewer plan, at most three calls.

**What to check:** If executed, record role outputs/additional latency separately from A2A delegation evidence. A reviewer's answer is not purchase approval.

</div>

## Objectives

**Adding more agents is not the goal.** Add orchestration only when roles, tools, and evaluation criteria are genuinely separate.

**Important:** Foundry portal Workflows is in Preview and **scheduled to retire on 2026-12-01**. This module uses **Microsoft Agent Framework** for new implementation.

## Concepts and lab map

**What you will try:** Compare a drafter → reviewer flow with one agent.

**What is it, and why does it matter?** Orchestration controls task order and result handoff. A2A separately communicates with an agent in another service. More roles add calls and time; the reviewer's words are not purchasing approval.

**How do you use it?** Read the single answer, drafter's intermediate answer, and reviewer's answer for the same question. Compare added tokens and time. Verify A2A separately with actual downstream-call evidence.

**Where do you run it?** [multi_agent.py](../../samples/multi_agent.py) uses a separate MAF environment; [a2a_lab.py](../../samples/a2a_lab.py) uses the core SDK environment. Do not mix them.

## Prerequisites

You need the English project, model, and separate checkout's `.env` from L01, plus a separate Python environment. Keep `FOUNDRY_LAB_LANGUAGE=en` selected when switching Python environments. Do not overwrite the core-course environment.
Live calls also require the administrator-supplied `results/azure-environment.json` ownership record. Execution stops if its project endpoint/language differs from `.env`. Obtain the record from the administrator rather than inventing one; without it, stop at plan/code inspection.

As checked on 2026-09-29, `agent-framework-foundry==1.13.1` requires `azure-ai-projects<2.7.0`. The core course uses 2.7.0. **Separate environments with compatible dependencies** are provided.

## Steps

### 1. Inspect the local plan

```bash
python samples/multi_agent.py --mode compare
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `multi_agent.py --mode compare` | Plans one single-agent baseline plus two calls for drafter→reviewer: at most three calls total. | Without `--live`, no SDK initialization or Azure calls. |

</div>

Check `mode=compare`, `model_calls_if_approved=3`, 180 seconds, 2,048 output tokens per response, and zero retries. The default `--mode sequential` preserves the original two-role path; it has a different call count.

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

### 3. Compare one and two agents with the same question

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode compare --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `multi_agent.py --mode compare --live` | Uses the same purchase question, model, and policy for one baseline and one drafter→reviewer workflow. | At most three model calls/180 seconds. Prints intermediate/final answers, actual token usage, and elapsed time; preserves them in a unique `Evidence:` JSONL. No Hosted deployment or real approval. |

</div>

This example runs Microsoft Agent Framework locally and calls Foundry models. **It does not deploy a Hosted Agent.** Both roles explicitly receive the same English synthetic policies from `data/en/policies/`; this is not a RAG example for evaluating retrieval quality.

| Role | Input | Result | Not allowed |
| --- | --- | --- | --- |
| drafter | Request and policies | Draft purchasing guidance | Claiming an order was completed when it was not |
| reviewer | Draft and policies | Final guidance after reviewing boundary values and approval rules | Real business approval |

The core flow is:

```python
workflow = WorkflowBuilder(
    start_executor=drafter,
    output_from=[reviewer],
    intermediate_output_from=[drafter],
    max_iterations=4,
).add_edge(drafter, reviewer).build()
```

### 4. Read the intermediate answer and change one question

<div class="practice-block" markdown="1">

**Try it:** Inspect the terminal's `paths`. In the `Evidence:` file, open `payload.paths` in the final `event=completed` row. Record your returned values, not invented example measurements.

| Result path | What to read |
| --- | --- |
| `single.stages[0].answer` | Single-agent baseline using the drafter's instructions and policy |
| `sequential.stages[0].answer` | Actual intermediate draft, not a later summary or reconstruction |
| `sequential.stages[1].answer` | Reviewer's final guidance after receiving that draft |
| Each stage's `response_id`, `input_tokens`, `output_tokens` | That call's identifier and actual SDK usage |
| Each path's `elapsed_seconds`, `total_tokens` | Whole-path elapsed time and summed call tokens |
| `sequential_minus_single` | Two-stage minus single time/tokens, not a correctness-improvement score |

Compare with **policy section 3**: did the drafter omit an approver for KRW 2,900,000, and did the reviewer fix it? If both answers are correct, “no additional quality benefit observed” is valid. Token `null` means uncollected, not zero. Do not add individual operation times to the whole-path duration again.
Timing covers each path's execution after object construction. The single path runs first, so authentication, caching, and startup latency can affect the observation. One duration difference does not establish a difference in the model's intrinsic speed.

**Change one thing:** Optionally approve a second run changing only the question to the boundary case. Keep model, policy, and instructions unchanged. This makes up to three **additional calls**, not a replay.

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode compare --case boundary --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `--case boundary` | Compares approvals for KRW 2,000,000 and KRW 2,000,001 through the same two paths. | At most three new model calls and new evidence. Running both cases totals at most six calls, each within its approved scope. |

</div>

**Explain the result:** Record `case / baseline errors / drafter errors / errors remaining after review / extra tokens and time / reason to keep two roles`. Exactly KRW 2,000,000 needs team-lead approval; KRW 2,000,001 also needs procurement approval. Single runs are variable observations, not statistical superiority. They do not establish human approval or A2A delegation.

</div>

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
python scripts/runtime_roles.py --agent ACTUAL_CALLER_AGENT --live
python samples/a2a_lab.py card --live
python samples/a2a_lab.py invoke --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Return to the core/`.venv-live` SDK environment first.

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `a2a_lab.py create` | Reads the creation plan for the worker, coordinator, and connection. | No Azure requests. |
| 2. `create --live` | Actually configures a new policy worker, coordinator, and A2A connection. | Creates remote objects and `results/a2a.json`. Do not assume it reuses an existing agent. |
| 3. `runtime_roles.py --agent ... --live` | Replace `ACTUAL_CALLER_AGENT` with the `caller` value in your English checkout's `results/a2a.json`. Grants the project-scoped invocation role to the owned caller's runtime identity. | An administrator task because it changes real permissions. The JSON file path itself is not the agent name. |
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
