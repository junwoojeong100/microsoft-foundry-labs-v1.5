## Objectives

Execute real MAF **GroupChatBuilder and HandoffBuilder**. Locate draft → review → revision transfer, the actual handoff tool, the specialist response, and termination.

<div class="lab-brief" markdown="1">

**Format:** Terminal SDK exercise. Offline defaults use three group-chat and two handoff fixture responses; optional live ceilings are three and four calls respectively.

**Start here:** Reselect L13's `.venv-maf` and language. Do not create another portal agent, router, or Hosted deployment.

**What to check:** Three draft/review/revision originals, plus `handoff_to_policy` or `handoff_to_budget` followed by an actual specialist response.

</div>

## Concepts and lab map

**What you will try:** Bounded group chat and tool-based control transfer.

**What is it, and why does it matter?** Group chat returns review to the writer; handoff transfers control to another role. A sentence saying “delegated” is not transfer evidence.

**How do you use it?** Run both builders with the same question/policy, then inspect roles, tool calls, the next response, and termination.

**Where do you run it?** Local Python SDK; only separately approved `--live` runs call the existing Microsoft Foundry model.

[![MAF three-turn group-chat termination and actual coordinator-to-specialist handoff flow.](../../assets/maf-collaboration.svg)](../../assets/maf-collaboration.svg)

Select the flow diagram to enlarge it. Existing footage contains no SDK execution; another agent's answer/Copy control is not reused as an execution example.

## Prerequisites

Complete [L13 environment setup](#l15). In a new terminal, repeat only MAF activation/language selection. Offline execution needs no login, `.env`, or ownership receipt. Live execution reuses [L13's model/scope checks](#maf-live-setup), without Hosted, Search, or a judge.

## Steps

### 1. Read execution and termination first

Open [`build_workflow` in multi_agent.py](../../samples/multi_agent.py). These are **read-only excerpts** with role definitions omitted; do not run the fragments independently.

```python
def select_speaker(state):
    names = list(state.participants)
    return names[state.current_round % len(names)]

group_chat = GroupChatBuilder(
    participants=[drafter, reviewer], selection_func=select_speaker, max_rounds=3,
    termination_condition=lambda messages: sum(message.role == "assistant" for message in messages) >= 3,
    intermediate_output_from=[drafter, reviewer],
).build()
```

Speakers are drafter → reviewer → drafter, stopping after three assistant messages. Handoff depends on this actual SDK connection, not classification prose:

```python
handoff = (
    HandoffBuilder(
        participants=[coordinator, policy_agent, budget_agent],
        termination_condition=lambda messages: any(
            message.role == "assistant" and message.author_name in {"policy", "budget"} and message.text.strip()
            for message in messages
        ),
    )
    .with_start_agent(coordinator)
    .add_handoff(coordinator, [policy_agent, budget_agent])
    .build()
)
```

`CallAudit` enforces the overall call ceiling; the specialist's nonempty answer terminates handoff. A direct coordinator answer without a handoff tool is not substituted for success.

<div class="practice-block" markdown="1">

### 2. Execute draft, review, and revision through the SDK

**Try it:** Keep L13's default purchase question and run:

```bash
python samples/multi_agent.py --mode group-chat --offline
```
<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Operation and options | Result, cost, or change |
| --- | --- | --- |
| 1. `--mode group-chat --offline` | Connect a fixed-response client to the real `GroupChatBuilder` for three turns. | `fixture_calls: 3`, blocked network/DNS, private `results/contoso-maf-fixture-....jsonl`, zero Microsoft Azure calls. |

</div>

| Inspect | Actual check |
| --- | --- |
| `paths.group-chat.stages` | Role order: `drafter`, `reviewer`, `drafter` |
| Reviewer's `model_call_completed` input | Original `Synthetic fixture from drafter, call 1.` |
| Final drafter's input | Original `Synthetic fixture from reviewer, call 2.` |
| `workflow_state` and `final_messages` | Termination after three turns, with originals retained |

Fixed fixture strings **do not establish that review found or corrected policy mistakes**. This checks message transfer, turn-taking, and termination.

### 3. Verify the actual handoff tool and next role's response

```bash
python samples/multi_agent.py --mode handoff --offline
```
<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Operation and options | Result, cost, or change |
| --- | --- | --- |
| 1. `--mode handoff --offline` | The fixture calls the tool exposed by the real `HandoffBuilder`, then executes the policy response. | Two calls, coordinator → policy. Routing is a **fixed policy fixture**, not model classification. |

</div>

Find this combination of fields. This is an inspection excerpt, not the complete JSON:

```output
"execution": "local_sdk_fixture"
"fixture_calls": 2
"routing_source": "fixed_policy_fixture_not_model_classification"
"handoff_calls": ["handoff_to_policy"]
"human_approval_performed": false
"quality_release": false
```

`handoff_calls` belongs to the coordinator stage; the next stage's `role` must be `policy`. Also locate the policy answer in `final_messages`. A tool name without the subsequent response is not success.

**Change one thing:** Keep execution mode, policy, and bounds fixed; change only `case` to the approval-boundary question.

```bash
python samples/multi_agent.py --mode group-chat --case boundary --offline
python samples/multi_agent.py --mode handoff --case boundary --offline
```
<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Operation and options | Result, cost, or change |
| --- | --- | --- |
| 1. `group-chat --case boundary --offline` | Inspect transfer of the exactly KRW 2,000,000 versus KRW 2,000,001 question across three turns. | Three fixture calls. A changed question does not make the fixed responses policy reasoning. |
| 2. `handoff --case boundary --offline` | Inspect transfer of that boundary question to the specialist. | Two fixture calls; fixed policy routing remains unchanged, not a classification-accuracy test. |

</div>

**Explain the result:** Identify which original reached the next role, which tool transferred control, and what ended execution. Do not claim business approval, remote A2A, or HITL execution.

</div>

### 4. Compare with a real model — separate approval

Reuse L13's live configuration, ownership, and capacity checks. These two baseline commands permit **at most seven paid model calls**: 180 seconds/execution, 2048 output tokens/call, six starts/minute, and zero retries. Live boundary-case repetitions need an additional approved budget.

```bash
python samples/multi_agent.py --mode group-chat --live
python samples/multi_agent.py --mode handoff --live
```
<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Operation and options | Result, cost, or change |
| --- | --- | --- |
| 1. `--mode group-chat --live` | Execute drafter → reviewer → drafter on the existing model. | At most three paid calls; compare actual findings, revisions, and unaddressed review points. |
| 2. `--mode handoff --live` | Require the model to select policy or budget using a real handoff tool. | At most four paid calls; preserve absent tool/next responses or exhausted bounds as failures. |

</div>

Check `execution=local_maf_with_azure_model`. Actual `response_id`, `handoff_calls`, specialist original, times, and usage must belong to the same run. Do not confuse model-selected routing with the fixture's fixed path.

| Executed here | Still not executed |
| --- | --- |
| Actual SDK group message transfer/termination | Persistent service or portal-hosted workflow |
| Actual SDK handoff tool and specialist response | Authenticated remote A2A endpoint/agent invocation |
| `human_approval_performed: false` | Authorized approver, events, and wait/resume in a HITL system |
| Synthetic-policy purchasing guidance | Real ordering, payment, or business approval |

Portal Workflows retire on **2026-12-01**; do not use that designer as a workaround.

## Success criteria

Locate the three group originals/transferred review, handoff tool, and actual specialist response. Separate offline from real-model execution and respect termination/call ceilings. Do not count this as passing a quality gate, business approval, remote A2A, or HITL.

## Troubleshooting

`PLAN ONLY` means not executed. Missing SDKs require L13's environment. A direct model answer instead of handoff is a failure, not an automatic fallback. Preserve empty specialist output, partial results, 429s, and exhausted bounds without raising recursion, retry, or output limits to pass.

## Cleanup

Only the one-shot local process ends. No recursion, remote server, or persistent router is created. Hand private evidence and remaining model/logging costs to L19.

<div class="lab-handoff" markdown="1">

**Keep:** Draft/review/revision originals, tool/specialist/termination records, execution kind, and unexecuted A2A, HITL, and business approval.

**Continue:** [L15: inspect Memory and conditionally compare conversations](#l16).

</div>
