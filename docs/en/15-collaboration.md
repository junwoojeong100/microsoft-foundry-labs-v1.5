> **What you will build:** Distinguish a drafter revising after review from transferring control to a specialist.

<div class="lab-brief" markdown="1">

**Format:** Advanced elective · reuse L13's environment and run two patterns one at a time.

**Start here:** Read both plans below and predict whether the task needs revision or a change of owner.

**What to check:** Find group chat's three contributions and handoff's actual tool call and specialist answer. Distinguish a termination message from the business answer.

</div>

## Objectives

**“Discuss together” and “change the responsible agent” are different.** Group chat returns a review to the same drafter; handoff lets a specialist take over. Neither replaces human purchasing approval.

## Concepts and lab map

**What you will try:** Message and control transfer with `GroupChatBuilder` and `HandoffBuilder`.

**What is it, and why does it matter?** Group chat supports iterative team review; handoff changes ownership. Saying “I delegated” does not prove control transferred.

**How do you use it?** Run both patterns against the same policy and question. Inspect intermediate answers and actual delegation calls without increasing iteration or cost limits.

**Where do you run it?** Run [multi_agent.py](../../samples/multi_agent.py) in `.venv-advanced`. Only the model is in Azure; no Hosted or remote A2A server is created.

## Prerequisites

Reuse [L13's environment setup](#l15): `.venv-advanced`, `.env`, administrator-provided `results/azure-environment.json`, and the chat deployment's **100,000 TPM / 60 RPM** check. L13's paid pattern runs are not prerequisites. On Windows use `.venv-advanced\Scripts\python.exe`. Keep `FOUNDRY_LAB_LANGUAGE=en` selected.

### Choose your starting path

| Current state | Steps to follow | What to retain |
| --- | --- | --- |
| No Azure approval | Read both plans in step 1 | Explain differences and call limits; actual execution remains not performed |
| Model, receipt, and cost approval ready | Plan → group chat → inspect → handoff → compare | Two original files and a revision/delegation comparison |

No additional resources need deployment. Both patterns together use **at most seven model calls**. Preserve **180 seconds per run, 2,048 output tokens per response, and zero retries**. Start the next pattern **at least one minute** after the previous start.

## Steps

### 1. Predict both flows before execution

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode group-chat
.venv-advanced/bin/python samples/multi_agent.py --mode handoff
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `--mode group-chat` | Read the drafter → reviewer → revised draft plan. | No SDK initialization, Azure call, or execution evidence. Plans at most three calls. |
| 2. `--mode handoff` | Read the coordinator → policy or budget specialist plan. | No actual delegation. Plans at most four calls. |

</div>

Predict group chat for “review and improve advice on a KRW 2,900,000 purchase,” and handoff for “choose the policy or budget specialist.” **A prediction is not a result.** Inspect actual transfer in the next steps.

### 2. Group chat: read the final revision

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode group-chat --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `--mode group-chat --live` | Run three contributions, returning the review to the drafter. Code chooses speakers round-robin; no model moderator is added. | At most three actual model calls. Inspect output and the original `Evidence:` file. |

</div>

Open the `Evidence:` file in an editor and find `paths.group-chat.stages`. Read first draft → review → final draft side by side. Use `payload.input` from `model_call_completed` events and `input_authors` to verify that the review was passed into the next request.

| What to inspect | Decision |
| --- | --- |
| Each of the three stages' `role` | Are they drafter, reviewer, drafter in order? |
| First and last `answer` | Were identified omissions addressed? Record unchanged output honestly |
| `final_messages`, `workflow_state` | Did execution terminate? An orchestrator's termination notice is not purchasing advice |

### 3. Handoff: find actual control transfer

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode handoff --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `--mode handoff --live` | Transfer control to an allowed policy or budget specialist. The specialist answers and terminates without delegating again. | At most four model calls. Missing tool/specialist evidence fails. No order or human approval. |

</div>

Under `paths.handoff.stages`, find the coordinator's `handoff_calls` followed by the specialist's response. Check that a `handoff_to_…` tool was recorded and the chosen specialist actually answered. A natural-language delegation claim without a tool call does not pass.

The sample sets `require_per_service_call_history_persistence=True` to retain conversation history across control changes. Do not remove it and hide the resulting error behind retries.

### 4. Change one condition and compare

<div class="practice-block" markdown="1">

**Try it:** Record `role order / input transfer / revised sentence / delegation tool / termination / total_tokens / elapsed_seconds` from both files. Missing usage (`null`) is not zero.

**Change one thing:** If additional calls are approved, add only `--case boundary` to one chosen pattern. Compare exactly KRW 2,000,000 with KRW 2,000,001, leaving the model, policy, and role instructions unchanged. If you only read plans, mark the actual comparison not performed.

**Explain the result:** Choose “group chat because revision is needed” or “handoff because ownership must change” for your task, citing actual inputs and responses. Extra calls alone do not prove better quality.

</div>

### 5. Identify what this exercise does not implement

Handoff between local roles is **not a remote Agent2Agent (A2A) connection**. Human-in-the-loop approval, incoming A2A endpoints, and organizational delegation are also outside this implementation. Start with separate authentication, protocol, and user-permission design before connecting external agents.

Compare the Builder responsibilities using the official [group-chat](https://learn.microsoft.com/agent-framework/workflows/orchestrations/group-chat?pivots=programming-language-python) and [handoff](https://learn.microsoft.com/agent-framework/workflows/orchestrations/handoff?pivots=programming-language-python) documentation.

## Success criteria

Within the patterns you ran, identify group chat's three contributions and final revision, and handoff's actual delegation call, specialist answer, and terminal state. Do not report review/delegation as human approval or remote A2A success.

## Troubleshooting

| Symptom | Inspect first | Next action |
| --- | --- | --- |
| SDK import fails | L13's Python environment and `pip check` | Return to the dedicated environment instead of mixing core SDKs |
| Group chat ends with only a termination notice | Whether `final_messages` was mistaken for `stages` | Read `answer` from the last drafter stage |
| No delegation tool or specialist response | `handoff_calls`, actual inputs, termination reason | Preserve the failure; do not repeat until a preferred result appears |
| 429, truncated response, or timeout | L02 throughput, request times, and bounds | Stop new calls, inspect the original error, and rerun only with approval |

## Cleanup

These executions call the owned model without creating Hosted deployments or recurring schedules. Keep originals under `results/`; after all selected labs, go to [L19 shared wrap-up](#l12).
