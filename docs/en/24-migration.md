> **What you will build:** A migration table that distinguishes what to move to the new Foundry and the order of validation, while preserving existing resources.

<div class="lab-brief" markdown="1">

**Format:** Local contract transformation plus optional design · no existing Classic environment needed.

**Start here:** Repair three errors in a synthetic request transform, then distinguish definitions, user state, and operational state.

**What to check:** Produce a migration/check/recovery/retention table with owners. This design does not move or delete real resources.

</div>

## Objectives

**A brand rename, portal transition, resource upgrade, and SDK/API migration are different tasks.**

## Concepts and lab map

**What you will try:** Repair a new API request conversion and plan a service migration.

**What is it, and why does it matter?** Classic is the earlier Foundry environment. Moving from Threads/Runs to Conversations/Responses can change conversations, function-result handling, permissions, and retention—not just names.

**How do you use it?** Repair three errors in a synthetic request. Then list the settings, user data, operational state, verification, and recovery steps to migrate.

**Where do you run it?** Work on your PC without a Classic account. The [SDK dependencies](../../requirements.txt), [Responses example](../../samples/workshop.py), and [deployment settings](../../azure.yaml) are comparisons. No actual migration or deletion is performed.

## Prerequisites

If an existing system is available, inventory it read-only within the approved scope. Otherwise use the **fictional Contoso Classic scenario** below. Do not create Classic resources just for this exercise. This chapter does not automatically upgrade resources or move data.

## Steps

### 0. Fix it: identifiers and output contracts in the new API

<div class="practice-block" markdown="1">

**Try it:** Transform a small fragment of a Responses request without creating a Classic environment. Unlike the old Threads/Runs `tool_call_id` field, a Responses output item's `id` and the `call_id` needed for its function result are different. Every ID here is synthetic.

```bash
python samples/prepare_practice.py migration --output practice/migration
python -m unittest discover -s practice/migration -p "test_exercise.py" -v
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `prepare_practice.py migration` | Copies the transform function and fixed contract tests into a new folder. | Local files only; no old SDK installation, Azure calls, or real migration. |
| 2. `unittest discover` | Checks conversation ID, function correlation ID, JSON string, and output-item count. | Initially **three of four tests fail**. The checks correctly detect a bad transform. |

</div>

| Input/output | Synthetic value | Meaning to preserve |
| --- | --- | --- |
| New conversation | `conv_new_demo` | The same conversation receiving the function result |
| Function-call item's `id` | `fc_item_demo` | Identifies an item in the response |
| Function call's `call_id` | `call_demo_1` | Correlates the result with its request |
| Actual function result | `{"sku":"NB-14","stock":8}` | Send this object's JSON **string** in `output` |

**Change one thing:** Repair the transform contract in `practice/migration/exercise.py`: use the supplied `conversation_id`, `function_call["call_id"]`, and `json.dumps`. Fix one field at a time and rerun the same tests to identify which failure disappears.

<details markdown="1">
<summary>Completed transform fragment — part of a new API request, not a full migration tool</summary>

<!-- solution:migration -->
```python
import json

def continuation(conversation_id: str, function_call: dict, result: dict) -> dict:
    return {
        "conversation": conversation_id,
        "input": [{
            "type": "function_call_output",
            "call_id": function_call["call_id"],
            "output": json.dumps(result, ensure_ascii=False),
        }],
    }
```

</details>

**Explain the result:** After four passes, explain each field and place it under **definitions / user state / operational state** in the migration table below. Real calls use IDs issued by the new service and the same agent/version binding. This exercise neither reuses old Thread/Run IDs nor moves user history. Compare the complete invocation/tool loop with `run_turn` in the bundled `samples/workshop.py`.

</div>

### 1. Identify what is currently in use

| Earlier/existing approach | New path | Caution |
| --- | --- | --- |
| Azure AI Studio / Azure AI Foundry | Microsoft Foundry | A name change alone does not change the API |
| Hub-based project | Project under a Foundry resource | Some Classic experiences remain separate |
| Assistants / Threads / Runs | Agent Versions / Conversations / Responses | Calls, state, and tool loops change |
| `azure-ai-projects` 1.x | 2.x project client | More than changing imports |
| Multiple inference endpoints | Project/OpenAI-compatible surface | Check support by provider and API |
| Role names such as Azure AI User | Foundry User and others | Check role IDs, scopes, and actual permissions |

Standalone Azure OpenAI resources and Classic hub-based projects do not directly enter every path in the new portal. Follow the official upgrade/migration procedures.

Sovereign clouds such as Azure Government have separate endpoints, authentication audiences, and service/model support. Do not reuse this public-cloud guide's environment files by changing only some addresses; base the migration plan on the official support documentation for that cloud.

### 2. Plan migration for three kinds of state separately

**Definitions:** instructions, models, tools, and connections.<br>
**User state:** conversations, memory, files, and vector stores.<br>
**Operational state:** endpoints, identities, permissions, monitoring, evaluation results, and publishing channels.

Do not assume that an API migration tool moving definitions has also moved all user conversations or business approval state.

**Worked example — a fictional purchasing assistant, not an actual migration result.**

| Existing state/item | New-path decision | Inspect / next action on failure |
| --- | --- | --- |
| Definition: instructions/function schema | Map separately to current v2 and L06 contracts; do not merely rename | Compare quantity 1–10 and not-ordered boundaries; correct/review functions or contracts if different |
| Knowledge: 3 policy files/vector store | After approval, upload originals into the new environment and record new file/store IDs | L05 citations must identify new files and the same sections; inspect file→store→agent bindings on failure |
| User state: Thread/Run | Test with a new conversation; do not reuse old IDs | Verify only intended context is passed; historical user-state migration needs separate scope/retention planning |
| Operations: identity/endpoint/model | Bind each new environment and specify minimum permissions | Correlate L03 responses with L10 traces; separate permissions, addresses, and versions for 403/404 |
| Publishing/recovery | Keep the old endpoint; route only test users to the new path | Confirm a return to L22's previous configuration bundle; separate deletion from cutover |

Add **source location, owner, retention decision, evidence file/ID, and unresolved items** to your own table. Check current migration support before applying an example decision to a real system.

### 3. Check regressions in the new environment

Only after approval for an actual migration, compare identical English synthetic inputs in the new nonproduction environment with L01's English profile. The default design exercise records the inputs and evidence locations below without executing them. Never reuse Korean private settings or receipts.

| What to inspect | How to judge it | Next action on failure |
| --- | --- | --- |
| L03 model call | Completed response, actual deployment name/response ID | Check endpoint/token audience and model support |
| L05 policy question | KRW 1,500,000 including VAT, 36 months, and actual new citations | Inspect originals, indexing, and store bindings |
| L06 normal/failure inputs | NB-14 quantity 2 totals KRW 2,900,000 and remains not ordered; out-of-stock/negative inputs error | Inspect schema, dispatcher, and tool-result return loop |
| L08 instruction comparison | Actual differences with the same language/context/model/questions/criteria | Do not claim superiority across changed conditions; never overwrite results or reuse sealed holdout data |
| L10 tracing | New response correlated with the new environment's trace | Check connection/time/permissions rather than attaching an old environment's logs |

L08's tool-free comparison does not replace integrated retrieval/function checks above. Record endpoint/schema/retry/retention differences separately, and mark unexecuted checks not executed rather than leaving a success-shaped blank.

### 4. Remove dependencies on retiring features first

Include portal Workflows' **scheduled retirement on 2026-12-01** in your timeline, and do not introduce new dependencies on it. Move required orchestration to currently supported paths such as Microsoft Agent Framework, then revalidate checkpoints, human approval, and resumption after failure.

AI Search agentic retrieval differs in capabilities and payloads between stable `2026-04-01` and the latest preview. Compare changes in knowledge sources, client names, pagination, Work IQ authentication, and response handling with the official migration tables.

### 5. Define staged cutover and recovery criteria

Proceed from test users → limited traffic → approved expansion. In this scenario, **a candidate that gives an uncited answer or falsely claims order completion blocks expansion**. Preserve its failed original first; the owner then selects the approved earlier endpoint/version/configuration. Verify state compatibility and separately check the actual recovery invocation.

If any quality, access, or recovery item remains unverified, record **cutover on hold / required next check**, not “migration complete.” Do not prematurely delete the earlier endpoint or user state.

## Success criteria

Explain the three synthetic transform errors and obtain four passes without changing the tests. This verifies a local wire-shape transform, not a completed service migration.
You have identified migration targets, Classic features to retain, handling of user state, retirement schedules, evaluation results, and a rollback method. “It appears in the new portal” is not enough to declare migration complete.

## Troubleshooting

Even under the same brand, older documentation URLs/SDK examples may use a different resource model. First check for `foundry-classic`, `azure-ai-projects 1.x`, and Threads/Runs.

## Cleanup

After the new path passes actual usage and evaluation and the recovery period has ended, the responsible owner approves retention or deletion of the old resources.
