> **What you will build:** Run one Contoso purchasing question sequentially and concurrently, then explain passing a prior answer versus dividing independent work.

<div class="lab-brief" markdown="1">

**Format:** Run Agent Framework orchestration locally against an approved Foundry model. No Hosted deployment is performed.

**Start here:** Prepare the separate advanced environment, finish L02's TPM/RPM check, and read the plan for one selected pattern.

**What to check:** Compare actual roles, message flow, model-call counts, answers, tokens, and time. An agent's answer is not business approval.

</div>

## Objectives

**Experience how the same roles behave under different coordination patterns.** More agents do not automatically make an answer faster or more accurate.
This module uses the official Builders in `agent_framework.orchestrations`. It is separate from the Foundry portal Workflows feature, scheduled to retire on **2026-12-01**.

## Concepts and lab map

**What you will try:** Sequential and concurrent execution with `SequentialBuilder` and `ConcurrentBuilder`.

**What is it, and why does it matter?** Orchestration chooses who acts next and which conversation/results are passed along. Sequential chains work, concurrent divides work, group chat refines work, and handoff changes the responsible agent.

**How do you use it?** Change only `--mode` under the same policy and question. Compare role order and actual outputs. Revision after review and specialist delegation have their own [L14 exercise](#l15-collaboration).

**Where do you run it?** Run [multi_agent.py](../../samples/multi_agent.py) in a separate Python environment. Only the model is in Azure; this is not a remote A2A or business-approval exercise.

## Prerequisites

Use the project/model, `.env`, and `results/azure-environment.json` you created in L01. Stop if the project, language, or deployment differs.
L13/L14 use **only the chat deployment**. The per-learner starting minimum is **100,000 TPM / 60 RPM**; see [L02](#l02-capacity) for sizing assumptions and configuration.

Keep the advanced SDK in `requirements-advanced.txt` separate. `agent-framework-foundry==1.13.1` requires `azure-ai-projects<2.7.0`, unlike the core environment. Install `agent-framework-orchestrations==1.2.0` with it.

### Choose your starting path

| Current state | Steps to follow | What to retain |
| --- | --- | --- |
| No Azure approval | Step 1 environment → step 3 plan | Explain roles and call limits; model execution remains not performed |
| Model, ownership receipt, and cost approval ready | 1 → 2 → 3 → 4 → 5 | Sequential/concurrent answers to one question and a comparison |

Reuse L01/L02's `.env` and your receipt; Hosted/Search are unnecessary. **Unlike L06, these SDK roles review policy/questions without a stock function.** Keep the English profile selected.

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

If insufficient, verify your update permissions/quota/cost scope, then use L02's `apply`. Sufficient capacity is not reduced. Live execution rechecks actual limits rather than trusting an old file.

### 3. Read the sequential and concurrent plans

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode concurrent
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

This module covers those two patterns only. **GroupChatBuilder and HandoffBuilder belong to L14**, which reuses the same environment; do not run them yet.

Every pattern is bounded to **180 seconds, 2,048 output tokens per response, and zero retries**. Do not run multiple terminals against the same deployment.
Within one execution, request starts are spaced by at least one second and capped at six per minute. Start the next pattern **at least one minute after the previous execution began**. Size shared deployments for all simultaneous learners in L02.

### 4. Run one pattern at a time

Each command makes new model calls. Read its outputs before choosing the next pattern. These two patterns total **at most five calls**, or **12 calls** if you also choose both L14 patterns.

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

Open each command's **`Evidence:` file in an editor**. Under `paths.sequential.stages`, connect the drafter's answer to the reviewer's actual input. Under `paths.concurrent.stages`, use `input_authors` and the original inputs to check that the three roles did not wait for one another's answers. The implementation is `build_workflow` in `samples/multi_agent.py`.

### 5. Compare message flow, termination, and cost

<div class="practice-block" markdown="1">

**Try it:** Find these fields under `paths` and in the `Evidence:` file. Record your actual values, not example numbers.

| Field | What to inspect |
| --- | --- |
| `paths.<mode>.stages` | Actual per-call roles, answers, response IDs, and tokens |
| `input_authors`, `input_sha256` | Clues linking the conversation passed to the next role |
| `payload.input` in `model_call_completed` events | Actual messages and instructions; sequential passes the draft to the reviewer |
| `elapsed_seconds`, `total_tokens` | Elapsed time and token sum; `null` usage is not zero |
| `final_messages`, `workflow_state` | Collected concurrent results and termination state |

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

<details class="implementation-detail" markdown="1">
<summary>Implementation reference: sequential and concurrent Builder settings — read only</summary>

#### Portal deployment versus Python orchestration

The portal supplies the **model deployment**, but it does not configure L13's sequential/concurrent workflow graph. Python Agent Framework code constructs that order:

```python
from agent_framework.orchestrations import SequentialBuilder, ConcurrentBuilder

sequential = SequentialBuilder(
    participants=[drafter, reviewer],
    intermediate_output_from=[drafter],
).build()

concurrent = ConcurrentBuilder(
    participants=[policy_agent, budget_agent, risk],
    intermediate_output_from=[policy_agent, budget_agent, risk],
).build()
```

| Foundry/code location | What it controls |
| --- | --- |
| Portal → Models → Deployments | Model deployment called by the Python client |
| `build_role(...)` | Each SDK agent's instructions and role |
| `SequentialBuilder` | Sends the drafter's output to the reviewer |
| `ConcurrentBuilder` | Runs independent roles together and collects per-stage output |
| `multi_agent.py` in `.venv-advanced` | Builds orchestration locally; only approved model requests go to Foundry |

`drafter`, `reviewer`, `policy_agent`, `budget_agent`, and `risk` are SDK agents configured by `build_role()` with instructions/model client. `multi_agent.py` executes only the selected Builder. This is local code, not a portal workflow; verify actual inputs/stages/output in `Evidence:`.

</details>

## Success criteria

Distinguish actual draft propagation in sequential execution from the three independent concurrent results. Explain the responses, elapsed time, and tokens for the patterns you ran.
A reviewer's agreement is neither human approval nor an automatic quality pass. If you only read plans, model execution remains not performed.

## Troubleshooting

For `agent_framework_orchestrations` import errors, check the advanced environment's installation path. If TPM/RPM is insufficient, return to L02. On 429, do not keep sending requests; inspect the error, limits, and other simultaneous users.
An oversized input or truncated response is a failure. Inspect context length and actual output rather than fabricating results or blindly increasing limits.

## Cleanup

This module performs local orchestration and model calls only. Hosted sessions and schedules created in other labs are separate; handle those in L19. Keep your own results under `results/` and do not share user or authentication information.

<div class="lab-handoff" markdown="1">

**Keep:** Sequential/concurrent `Evidence:` files and role inputs/answers, call counts, token totals, and timing comparisons. Plan-only means model execution not run.

**Continue:** [L14 group chat/handoff](#l15-collaboration) reuses **the same `.venv-advanced`**. If this was your only elective, go to [L19](#l12).

</div>
