> **What you build:** A method for comparing v1/v2 answers under matched conditions and explaining differences, ties, or failures using scores and judge reasons.

<div class="lab-brief" markdown="1">

**Format:** Read instructions and questions first; collecting your own answers and running paid evaluation are optional.

**Start here:** Read both instruction files and the fixed questions, then identify what an answer must address.

**What to check:** Explain the comparison conditions and criteria. If you execute the optional path, connect your originals, scores, and reasons outside the guide.

</div>

## Objectives

**Distinguish differences in answers from the evaluator's judgment.** Version one is a role-and-goal starting instruction; version two specifies an answer procedure. The v2 label does not establish better quality.

## Concepts and lab map

**What you will try:** Compare two answers to the same question and interpret evaluation reasons.

**What is it, and why does it matter?** Evaluation compares expected behavior with actual answers. Keep the model, policy, questions, and rubric unchanged so instruction differences can be interpreted.

**How do you use it?** Read the instructions and questions first. If approved, collect and evaluate actual answers, preserving ties and regressions.

**Where do you run it?** Read the [questions and checklist](../../data/en/evaluation/instruction-comparison.json), [v1](../../data/en/prompts/agent-v1.txt), and [v2](../../data/en/prompts/agent-v2.txt). Optionally use the [collection](../../samples/instruction_prompt_agent_lab.py) and [evaluation](../../samples/instruction_evaluation.py) scripts.

## Prerequisites

**Reading the instructions and questions needs no account or model calls.** This guide does not contain the author's execution results or prewritten scores. Comparing actual answers requires your own collected originals or approved lab results provided separately by your instructor.

| Term | Plain-language meaning |
| --- | --- |
| v1 / v2 | Starting / improved instructions, not service-issued agent-version numbers |
| Judge / Native evaluation | The grading model / an evaluation performed by Foundry |
| Completeness / Relevance / Groundedness | Were all requests addressed / was the answer relevant / was it supported? |
| Dev / Holdout | Practice data exposed during improvement / a separate final test excluded from improvement |

<details class="optional-path" markdown="1">
<summary>Optional execution prerequisites: your project, deployments, and ownership receipt</summary>

Use L01's environment and L02's **`gpt-6-sol` / `2026-09-22`** model. Set the actual deployment name in `.env`. The administrator path uses `contoso-chat`; a manually chosen name such as `contoso-gpt-6-sol` must match your ownership receipt.

Native evaluation needs a separate **`gpt-4.1` / `2025-04-14`** judge and `FOUNDRY_JUDGE_DEPLOYMENT_NAME`. Verify both deployments' actual TPM/RPM in L02. Hosted redeployment, Search, Optimizer, and holdout are not prerequisites.

New execution uses **your own `results/azure-environment.json` and `.env`**. Both languages read back current RG ownership tags, project, deployments, and throughput. An author's old RG or historical validation files are not runtime dependencies. Each comparison creates a collision-resistant Prompt Agent name and pins v1/v2 versions.

Keep `FOUNDRY_LAB_LANGUAGE=en` selected in the separate English folder. Both instructions receive the same synthetic policy context; this is not live Search retrieval. Expected behavior and grading criteria are excluded from target-model input and supplied only to the judge.

</details>

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

### 2. Optional: collect and evaluate once in your environment

Execute only after confirming the project, language, request count, time, and cost scope.

<details class="optional-path" markdown="1">
<summary>New paid execution: inspect the plan → collect answers → evaluate originals</summary>

```bash
python samples/instruction_prompt_agent_lab.py
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `instruction_prompt_agent_lab.py` | Read the two instruction versions, twelve fixed questions, model, and request bound. | Plan only; no Azure calls. |

</div>

Run the first command only when the plan matches your scope. **Confirm collection completed successfully** before the second command. Do not execute both lines together.

```bash
python samples/instruction_prompt_agent_lab.py --live --output results/instruction-prompt-agent-en.json
python samples/instruction_evaluation.py --input results/instruction-prompt-agent-en.json --output results/instruction-native-prompt-agent-en.json --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. Collection with `--live` | Create a tool-free Prompt Agent and pinned instruction versions in your owned project, then collect matched answers. | At most 24 responses, 600 seconds, zero retries, and 2,048 output tokens per response for this language. Preserve originals and failures separately. |
| 2. Native evaluation with `--live` | Submit the 24 actual answers from `--input` to Foundry evaluation. | Zero target reinvocations. One native run per language, at most 600 seconds plus 90 seconds for cancellation confirmation. Write scores and reasons to `--output`. |

</div>

Keep Korean and English input/output paths distinct. Across both languages, collection is bounded to 48 target responses and 1,200 seconds. Do not overwrite existing files or resample until a score rises. On failure, inspect the original error and already completed request count.

When invoking with `agent_reference`, do not repeat the Agent definition's `reasoning` or `text` settings in the request. Keep results under your own `results/`; do not insert them into HTML, Markdown, PDF, or the kit.

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

Keep originals and evaluations outside the guide. Manage created agents and evaluation resources using your own ownership records and retention policy; do not delete without separate approval. Do not turn validation results into lab instructions or guaranteed scores.
