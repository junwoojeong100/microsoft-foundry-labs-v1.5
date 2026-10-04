> **What you will build:** Run the same Contoso purchasing question through sequential, concurrent, group-chat, and handoff orchestration, then explain how roles exchange control and results.

<div class="lab-brief" markdown="1">

**Format:** Run Agent Framework orchestration locally against an approved Foundry model. No Hosted deployment is performed.

**Start here:** Prepare the separate advanced environment, finish L02's TPM/RPM check, and read the plan for one selected pattern.

**What to check:** Compare actual roles, message flow, model-call counts, answers, tokens, and time. An agent's answer is not business approval.

</div>

## Objectives

**Experience how the same roles behave under different coordination patterns.** More agents do not automatically make an answer faster or more accurate.
This module uses the official Builders in `agent_framework.orchestrations`. It is separate from the Foundry portal Workflows feature, scheduled to retire on **2026-12-01**.

## Concepts and lab map

**What you will try:** Sequential, concurrent, group-chat, and handoff orchestration.

**What is it, and why does it matter?** Orchestration chooses who acts next and which conversation/results are passed along. Sequential chains work, concurrent divides work, group chat refines work, and handoff changes the responsible agent.

**How do you use it?** Change only `--mode` under the same policy and question. Compare role order and actual outputs while retaining request limits and termination conditions.

**Where do you run it?** Run [multi_agent.py](../../samples/multi_agent.py) in a separate Python environment. Only the model is in Azure; this is not a remote A2A or business-approval exercise.

## Prerequisites

Use L01's project, deployment, `.env`, and administrator-provided `results/azure-environment.json`. Stop if the project, language, or deployment name differs.
L15 itself uses **only the chat deployment**. The per-learner starting minimum is **100,000 TPM / 60 RPM**; see [L02](#l02-capacity) for sizing assumptions and configuration.

Keep the advanced SDK in `requirements-advanced.txt` separate. `agent-framework-foundry==1.13.1` requires `azure-ai-projects<2.7.0`, unlike the core environment. Install `agent-framework-orchestrations==1.2.0` with it.

## Steps

### 1. Prepare the separate SDK environment

```bash
python3.13 -m venv .venv-advanced
.venv-advanced/bin/python -m pip install -r requirements-advanced.txt
.venv-advanced/bin/python -m pip check
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `python3.13 -m venv` | Create the advanced environment separately from the core SDK. | Local environment creation; do not overwrite an existing environment. |
| 2. `pip install -r requirements-advanced.txt` | Install compatible Foundry integration and orchestration Builders. | Package downloads only; no Azure request. |
| 3. `pip check` | Check dependencies in that same environment. | Resolve conflicts before executing. |

</div>

On Windows use `.venv-advanced\Scripts\python.exe`. If an existing advanced environment uses another Python version, create a new environment folder.

### 2. Check model throughput

```bash
.venv-advanced/bin/python samples/model_capacity.py plan --roles chat
.venv-advanced/bin/python samples/model_capacity.py check --roles chat --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `model_capacity.py plan --roles chat` | Read the chat TPM/RPM plan for one learner running one lab. | Local calculation; no Azure request. |
| 2. `check --roles chat --live` | Read the owned resource group and deployment's actual `rateLimits`. | Read-only. Below-minimum capacity fails without a model call. |

</div>

If insufficient, the administrator uses L02's `apply` path first. Sufficient capacity is not reduced. Each live orchestration also rechecks readiness instead of trusting an old confirmation file.

### 3. Read the four execution plans

```bash
python samples/multi_agent.py --mode concurrent
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `multi_agent.py --mode concurrent` | Read the selected pattern's roles and call limit. Use the other modes below to inspect their plans. | Without `--live`, no SDK initialization, Azure request, or execution evidence is created. |

</div>

| Mode | Actual Builder | Flow | Maximum model calls |
| --- | --- | --- | ---: |
| `sequential` | `SequentialBuilder` | Drafter → reviewer | 2 |
| `concurrent` | `ConcurrentBuilder` | Policy, budget, and risk work independently → collected outputs | 3 |
| `group-chat` | `GroupChatBuilder` | Drafter → reviewer → revised draft | 3 |
| `handoff` | `HandoffBuilder` | Coordinator transfers control to policy or budget | 4 |

Every pattern is bounded to **180 seconds, 2,048 output tokens per response, and zero retries**. Do not run multiple terminals against the same deployment.
Within one execution, request starts are spaced by at least one second and capped at six per minute. Start the next pattern **at least one minute after the previous execution began**. Size shared deployments for all simultaneous learners in L02.

### 4. Run one pattern at a time

Each command makes new model calls. Read its outputs before choosing the next pattern. Running all four has a combined maximum of **12 model calls**.

**Sequential:** Confirm that the reviewer's input contains the drafter's actual answer.

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode sequential --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `--mode sequential --live` | Pass the same policy and conversation through the drafter and reviewer in order. | At most two model calls; preserve actual intermediate and final answers. |

</div>

**Concurrent:** The three roles do not first read one another's answers. Collecting outputs is not automatic consensus or a verified single answer.

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode concurrent --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `--mode concurrent --live` | Policy, budget, and risk independently handle the same question. | At most three calls. Starts are paced, while in-flight work can overlap. |

</div>

**Group chat:** Speaker selection is deterministic round-robin. No extra model-based moderator call is made; the conversation stops after three contributions.

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode group-chat --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `--mode group-chat --live` | Run three contributions so the drafter receives the review and replies again. | At most three calls. Do not increase termination or call limits. |

</div>

**Handoff:** The coordinator uses an actual `handoff_to_…` tool. Saying “delegated” is not sufficient. Specialists terminate after answering and do not hand off again in this exercise.

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode handoff --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `--mode handoff --live` | Transfer conversation control to an allowed policy or budget specialist. | At most four calls. Missing tool/specialist evidence fails. No business approval or A2A server invocation occurs. |

</div>

Handoff agents require `require_per_service_call_history_persistence=True`. The sample sets it so tool-call control changes retain the local conversation.
Read `build_workflow` in `samples/multi_agent.py` to compare all four Builders. The official [group-chat](https://learn.microsoft.com/agent-framework/workflows/orchestrations/group-chat?pivots=programming-language-python) and [handoff](https://learn.microsoft.com/agent-framework/workflows/orchestrations/handoff?pivots=programming-language-python) documentation explains their contracts.

### 5. Compare message flow, termination, and cost

<div class="practice-block" markdown="1">

**Try it:** Find these fields under `paths` and in the `Evidence:` file. Record your actual values, not example numbers.

| Field | What to inspect |
| --- | --- |
| `paths.<mode>.stages` | Actual per-call roles, answers, response IDs, and tokens |
| `input_authors`, `input_sha256` | Clues linking the conversation passed to the next role |
| `payload.input` in `model_call_completed` events | Actual messages and instructions; check prior-answer propagation in sequential/group chat |
| `handoff_calls` | The actual requested handoff tool names |
| `elapsed_seconds`, `total_tokens` | Elapsed time and token sum; `null` usage is not zero |
| `final_messages`, `workflow_state` | Final messages and state for concurrent, group-chat, and handoff execution |

**Change one thing:** With approval for additional calls, add only `--case boundary` to the same mode. Compare approval rules for exactly KRW 2,000,000 and KRW 2,000,001. Keep model, policy, and role instructions fixed.

**Explain the result:** Record `pattern / message order / omissions / termination / extra tokens and time / reason to use this pattern`. Compare amounts, approvals, and unperformed-action claims with the policy. More agents alone do not establish better quality.

</div>

<details class="optional-path" markdown="1">
<summary>Optional: compare one drafter with the sequential workflow</summary>

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode compare --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `--mode compare --live` | Use the same drafting instruction, policy, and question for one direct answer and two sequential calls. | At most three additional calls. `sequential_minus_single` measures time/tokens, not quality. |

</div>

The single path runs first, so authentication, caching, and startup latency can differ. One timing difference does not establish general performance superiority.

</details>

## Success criteria

Distinguish the four patterns' message flow and termination, and explain actual responses from the patterns you chose to run.
Check real control transfer for handoff, three contributions for group chat, and three independent perspectives for concurrent execution. Do not claim a business approval or remote A2A run.

## Troubleshooting

For `agent_framework_orchestrations` import errors, check the advanced environment's installation path. If TPM/RPM is insufficient, return to L02. On 429, do not keep sending requests; inspect the error, limits, and other simultaneous users.
An oversized input or truncated response is a failure. Inspect context length and actual output rather than fabricating results or blindly increasing limits.

## Cleanup

This module performs local orchestration and model calls only. Hosted sessions and schedules created in other labs are separate; handle those in L12. Keep your own results under `results/` and do not share user or authentication information.
