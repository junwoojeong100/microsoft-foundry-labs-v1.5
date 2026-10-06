> **What you build:** A method for comparing v1/v2 answers under matched conditions and explaining differences, ties, or failures using scores and judge reasons.

<div class="lab-brief" markdown="1">

**Format:** Compare inputs → collect your answers → evaluate the same originals in Foundry → analyze reasons.

**Start here:** Read both instruction files and the fixed questions, then identify what an answer must address.

**What to check:** Connect your v1/v2 originals, scores, and reasons for the same question. With missing prerequisites, record reading only.

</div>

## Objectives

**Distinguish differences in answers from the evaluator's judgment.** Version one is a role-and-goal starting instruction; version two specifies an answer procedure. The v2 label does not establish better quality.

## Concepts and lab map

**What you will try:** Compare two answers to the same question and interpret evaluation reasons.

**What is it, and why does it matter?** Evaluation compares expected behavior with actual answers. Keep the model, policy, questions, and rubric unchanged so instruction differences can be interpreted.

**How do you use it?** Read fixed inputs and verify the request budget. Collect your originals once, evaluate them, and preserve ties/regressions.

**Where do you run it?** Read the [questions](../../data/en/evaluation/instruction-comparison.json) and [v1](../../data/en/prompts/agent-v1.txt)/[v2](../../data/en/prompts/agent-v2.txt), then use the [collector](../../samples/instruction_prompt_agent_lab.py) and [evaluator](../../samples/instruction_evaluation.py). Inspect results in Foundry Evaluations.

## Prerequisites

Use **your L01 project, chat/judge deployments, and ownership receipt**. Do not count another person's results as your execution. Without live prerequisites, read inputs/rubric and record actual evaluation not performed.

| Term | Plain-language meaning |
| --- | --- |
| v1 / v2 | Starting / improved instructions, not service-issued agent-version numbers |
| Judge / Native evaluation | The grading model / an evaluation performed by Foundry |
| Completeness / Relevance / Groundedness | Were all requests addressed / was the answer relevant / was it supported? |
| Dev / Holdout | Practice data exposed during improvement / a separate final test excluded from improvement |

Use L01's environment and L02's **`gpt-6-sol / 2026-09-22`**, deployment `contoso-chat`. `.env` and the ownership record must agree.

Native evaluation uses L01's distinct **`gpt-4.1 / 2025-04-14`** judge, `FOUNDRY_JUDGE_DEPLOYMENT_NAME=contoso-judge`. Check chat/judge limits in L02. Search, Hosted, Optimizer, and holdout are unnecessary.

New execution uses **your own `results/azure-environment.json` and `.env`**. The collection code reads back current RG ownership tags, project, deployments, and throughput, creates a collision-resistant Prompt Agent name, and pins v1/v2 versions.

Keep `FOUNDRY_LAB_LANGUAGE=en` selected in the separate English folder. Both instructions receive the same synthetic policy context; this is not live Search retrieval. Expected behavior and grading criteria are excluded from target-model input and supplied only to the judge.

## Steps

### 1. Compare the question and instructions first

Find `compound-request-no-tools` in the question file and separate **cap / current stock / approver / draft** requests. Read the answer procedure each instruction requires. No tools are available in this comparison, so neither stock lookup nor draft creation may be claimed as executed.

| General v1 instruction | Procedure specified in v2 | What to inspect in answers |
| --- | --- | --- |
| Do not guess unknown information | Answer available public parts even when restricted parts cannot be answered | Numbers, currency, and VAT basis |
| Cite actual documents | Link each claim to its relevant section | Do not reuse a general introduction as evidence for unrelated judgments |
| Use policy and tools | Distinguish caps, quotes, actual prices, exchange rates, and draft state | Keep unverified conditions unconfirmed |
| Prepare drafts safely | Check explicit intent, quantity, and actual tool output | Never fabricate approval, ordering, or payment |

Do not put case IDs or question-specific answers into instructions. Without an account, record **conditions to hold fixed / evidence to inspect / unexecuted scope**. Do not assign scores or claim a winner before collecting answers.

### 2. Collect and evaluate your own answers once

Verify your project, language, request count, time, and cost scope. With prerequisites met, the default is **plan → collect → evaluate**.

```bash
python samples/instruction_prompt_agent_lab.py
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `instruction_prompt_agent_lab.py` | Read the two instruction versions, twelve fixed questions, model, and request bound. | Plan only; no Azure calls. |

</div>

When the plan matches your scope, run **collection only**.

```bash
python samples/instruction_prompt_agent_lab.py --live --output results/instruction-prompt-agent-en.json
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. Collection with `--live` | Create a tool-free Prompt Agent and pinned instruction versions in your owned project, then collect matched answers. | At most 24 responses, 600 seconds, zero retries, and 2,048 output tokens per response for this language. Preserve originals and failures separately. |

</div>

**Stop and check:** Open `results/instruction-prompt-agent-en.json` in VS Code. Top-level `status` must be `completed`, `target_calls` must be 24, and `rows` must contain both instruction versions for all twelve questions. Inspect each row's `status`, `response_id`, and `raw_answer`. On errors or omissions, use **Troubleshooting** instead of submitting evaluation. Do not edit originals to mark them complete.

Only after collection completes and judge/cost conditions are ready, evaluate **that same file**:

```bash
python samples/instruction_evaluation.py --input results/instruction-prompt-agent-en.json --output results/instruction-native-prompt-agent-en.json --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. Native evaluation with `--live` | Submits the 24 actual originals in `--input`, not an L06 response JSONL or ownership receipt. | Zero target reinvocations. One native run per language, at most 600 seconds plus 90 seconds for cancellation confirmation. Write scores/reasons to `--output`. |

</div>

Keep Korean and English input/output paths distinct. Across both languages, collection is bounded to 48 target responses and 1,200 seconds. Do not overwrite existing files or resample until a score rises. On failure, inspect the original error and already completed request count.

When invoking with `agent_reference`, do not repeat the Agent definition's `reasoning` or `text` settings in the request.

<details class="implementation-detail" markdown="1">
<summary>Implementation reference: collection and evaluation use different APIs — read only</summary>

#### Portal Evaluations and the actual SDK calls

Collection and evaluation are separate. The collector invokes pinned v1/v2 versions; evaluation submits 24 saved originals. In this call excerpt, `shared_input` is a question plus matched policy context, `criteria` configures completeness/relevance/groundedness, and `rows` contains actual answers. `data_source_config` defines required row fields. Do not execute the excerpt alone.

```python
# instruction_prompt_agent_lab.py: one row in the fixed v1/v2 collection
response = client.responses.create(
    input=shared_input,
    extra_body={"agent_reference": {
        "type": "agent_reference",
        "name": agent_name,
        "version": versions[label],
    }},
    max_output_tokens=MAX_OUTPUT_TOKENS,
    store=False,
)

# instruction_evaluation.py: evaluate saved rows; do not call the target again
group = client.evals.create(
    name=f"Contoso {LANGUAGE} instruction comparison",
    data_source_config=data_source_config,
    testing_criteria=criteria,
)
native = client.evals.runs.create(
    eval_id=group.id,
    name=f"Contoso {LANGUAGE} v1-v2 one comparison",
    data_source={"type": "jsonl", "source": {"type": "file_content", "content": [{"item": row} for row in rows]}},
)
```

| Foundry portal | Value to inspect in the source |
| --- | --- |
| Agents → Versions | `agent_reference.name/version` identifies the instruction version used for each answer |
| Evaluations → Criteria | `testing_criteria=criteria` and the fixed judge deployment |
| Evaluations → Run | `client.evals.runs.create(...)` consumes the saved JSONL rows |
| Results | Actual answer/score/reason for the same `case_id`; `completed` alone is not a quality pass |

Execute through the `--live` path above. Reading this excerpt or portal results makes no additional target call. Preserve the fixed questions, rubric, and threshold.

</details>

### 3. Connect each answer with its score and reason

In the collection file, find the v1/v2 rows sharing an `id`. In the evaluation file, join `comparison.rows` by `case_id` and `instructions`.

| Field | How to read it |
| --- | --- |
| `rows[].raw_answer`, `response_id` | The actual answer and its identifier |
| `prompt_agent_versions` | Agent name and pinned versions |
| `comparison.rows[].metrics` | Per-case native scores, verdicts, and reasons |
| `comparison.local_checklist` | Supporting text-and-citation checks in the collection file |
| `comparison.usage_latency` | Token and latency totals and differences |
| `instructions_sha256`, `cases_sha256`, `context_sha256` | Input hashes for checking matched conditions |

Record **the request / both actual answers / relevant policy sections / the judge's reason / whether you agree**. `raw_answer` contains a JSON string; inspect its `answer` and `citation_ids` separately.

**Start with one question.** Search both files for `compound-request-no-tools`. Read its collection rows for `instructions=v1` and `v2`, then the evaluation rows with matching `case_id`/`instructions`. Within `metrics`, read **score → passed → reason**. Separate the price limit, stock, approvers, and draft parts actually answered from those not executable without tools. Apply the same method to the other eleven questions. You need not understand every SDK line or hash first.

### 4. Distinguish scores from completed execution

Native completeness, relevance, and groundedness use **1–5 ordinal** scores. Relevance and groundedness use built-in evaluators; completeness uses the same custom rubric for both instructions. The binary summary of scores at least four is not the five-point scale itself.

The local checklist checks forty criteria across twelve questions using **mechanical text-and-citation matching**. It can miss paraphrases and is not a semantic evaluator or a business safety/access gate.

![Foundry evaluation view. Locate execution status and per-row scores, errors, and omissions.](../../assets/portal/en/08-evaluations.png)

Find your run under **Build → Evaluations** and inspect status, evaluator identity, and row-level results. `completed` does not establish that every score is valid. Errors, omissions, and missing numeric scores remain failures; never fill them with zero or a passing verdict.

### 5. Explain improvements, ties, or regressions

Version one may already answer sufficiently, producing a tie; generation variability can also make version two worse. Inspect originals and reasons without weakening v1 or changing the rubric after observing results.

These are exposed **dev** questions, not an independent **holdout** or a generalization test. **Optimizer** candidate generation is a separate activity. Existing business gates, such as at least 90% overall and zero safety/access failures, must not be replaced or lowered by this small teaching comparison.

## Success criteria

For reading only, explain the comparison conditions and evidence to inspect, and record **actual evaluation not run**.
For live execution, connect all twelve v1/v2 pairs with pinned versions, native scores, judge reasons, errors, and missing rows. Explain differences, ties, or regressions from evidence; never promise an improvement beforehand.

## Troubleshooting

For 401/403, check your project, caller identity, and roles. For 404, check the actual deployment name and endpoint. For 429, inspect TPM/RPM and shared traffic rather than retrying indefinitely. Do not submit a failed or partial collection to evaluation, or silently change the target or judge model.

## Cleanup

Keep the response file `results/instruction-prompt-agent-en.json` and evaluation file `results/instruction-native-prompt-agent-en.json` together. Manage created agents and evaluation resources using your own ownership records and retention policy; do not delete without separate approval.

<div class="lab-handoff" markdown="1">

**Keep:** Collection/evaluation JSON files, evaluation-agent name/versions, matched originals/scores/reasons, errors, and omissions. Reading only means actual evaluation not run.

**Continue:** [L09 boundary questions](#l09), returning to **L05's policy agent**, not the evaluation agent.

</div>
