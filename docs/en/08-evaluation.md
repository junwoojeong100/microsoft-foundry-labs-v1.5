> **What you will build:** One comparison of the unchanged v1 baseline and improved v2, connecting instruction changes to observable differences in answers.

## Objectives

**Explain why an instruction change improves an answer.** A learning guide does not need an ever-growing sequence of release experiments.
Keep v1 as the unchanged baseline and v2 as the current improved instructions. Further instruction edits stay in v2.

## Concepts and lab map

**What you will try:** Controlled inputs, a fixed checklist, source evidence, and interpretation of Foundry evaluation results.

**What is it, and why does it matter?** Scores must follow the actual answer, not the label “v2.”
Keep the model, policies, questions, output format, and checks identical; change only the instructions.

**How do you use it?** Ask the same three questions once per version, inspect the original answers and individual checks, and calculate the difference.
Retain ties and regressions. Do not prewrite a winning result or keep sampling until a score increases.

**Where do you run it?** Use the [comparison runner](../../samples/instruction_lab.py), [fixed questions/checklist](../../data/en/evaluation/instruction-comparison.json),
[v1](../../data/en/prompts/agent-v1.txt), and [v2](../../data/en/prompts/agent-v2.txt).
In the portal's Evaluations area, distinguish service completion from scores, errors, and missing rows.

## Prerequisites

Use L01's environment and L02's **`gpt-6-sol` / `2026-09-22`** deployment. Set its actual deployment name, `contoso-gpt-6-sol`, in `.env`. Native evaluation also needs `FOUNDRY_JUDGE_DEPLOYMENT_NAME`; this measurement held the existing `contoso-judge` (GPT-4.1) fixed in both environments. No Hosted redeployment, Search service, Optimizer, or holdout is required.
Both prompts receive the same **checked-in synthetic policy context**; it is not described as a live Search retrieval.
Keep `FOUNDRY_LAB_LANGUAGE=en` selected for the English inputs and instructions.

## Steps

### 1. Read what v2 changes

| General v1 guidance | More explicit v2 behavior | Difference to look for |
| --- | --- | --- |
| Do not guess missing information | Refuse restricted parts while still answering independently verifiable public parts | State the public cap's number, currency, and VAT basis |
| Cite actual documents | Match separate evidence to access, missing information, public facts, and next steps | Do not substitute a general introduction for a specific rule |
| Use policies and tools | Distinguish policy caps, quotes, actual prices, verified FX, and draft status | Do not confirm unavailable contract terms or exchange rates |
| Create drafts safely | Require explicit intent, exact quantity, no duplication, and actual results | No placeholder quantity or fabricated approval/order/payment |

V2 contains a reusable answer procedure, not question-specific answers or evaluation case IDs.

### 2. Inspect the plan, then compare once

```bash
python samples/instruction_lab.py --reasoning-effort low
python samples/instruction_lab.py --reasoning-effort low --live
python samples/instruction_evaluation.py --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `instruction_lab.py --reasoning-effort low` | Displays v1/v2, three shared questions and the reasoning setting applied equally to both. | Plan only; zero Azure calls. |
| 2. `instruction_lab.py ... --live` | After cost approval, invoke each prompt once per question using the same GPT-6 Sol deployment and context. | At most six calls, 360 seconds, zero retries and 2048 output tokens. Retain originals and local checks in `results/instruction-comparison.json`. |
| 3. `instruction_evaluation.py --live` | Submit those six originals to Foundry native completeness, relevance and groundedness evaluation. The judge is not given the v1/v2 labels. | Zero target reinvocations. One native run, 600 seconds and 90-second cancellation verification; retain per-row outputs in `results/instruction-native.json`. |

</div>

If the result file exists, read it rather than running again. Do not increment instruction or experiment versions. Foundry-issued evaluation IDs are retained only for original-result traceability.
Errors and incomplete responses remain recorded; no earlier answer or authored example is substituted.

### 3. Read the score and the underlying answers

The same three checks apply to each answer, giving each instruction version a score from **0 to 9**.
A check requires both an explicit fact/refusal/confirmation path and a relevant selected policy section.
This is a **limited mechanical completeness/citation checklist**, not comprehensive semantic evaluation or a business release gate.

| Result field | Interpretation |
| --- | --- |
| `scores.v1`, `scores.v2` | Actual matched checks under identical criteria |
| `delta` | V2 score minus v1 score |
| `outcome` | Actual `improved`, `unchanged`, or `regressed` result |
| `rows[].raw_answer`, `checklist` | Original answer and check-level reasons behind its score |
| `instructions_sha256`, `context_sha256` | Exact input fingerprints, not increasing instruction versions |

**A higher v2 score is not guaranteed.** V1 may already answer every part correctly, and model variation can produce a regression.
Explain that result from the originals. Do not weaken v1 or change the checklist to manufacture improvement.

### 4. Connect this to Foundry evaluation

![Foundry Evaluations. Separate completion status from individual scores, errors, and missing rows.](../../assets/portal/en/08-evaluations.png)

Explore the run state, evaluator, inputs, row-level judgments, and errors in Evaluations.
The first two commands collect real Azure model responses and calculate local checks. The third [native comparison runner](../../samples/instruction_evaluation.py) submits those exact responses to Foundry Evaluations. Relevance and groundedness use built-in evaluators; completeness uses one shared custom 1–5 rubric.
This is a small learning evaluation without a separate judge-control calibration.
The existing 90% overall and zero-safety/access-failure business gates are not replaced or relaxed by this small learning score.

### 5. Actual Korean and English measurements

All target calls used `gpt-6-sol` version `2026-09-22`, reasoning `low`, and identical questions/context/criteria within each language.

| Language | Instructions | Local checklist / 9 | Native completeness / 5 | Relevance / 5 | Groundedness / 5 |
| --- | --- | --- | --- | --- | --- |
| Korean | v1 | 9 | 5.0 | 5.0 | 5.0 |
| Korean | v2 | 9 | 5.0 | 5.0 | 5.0 |
| English | v1 | 8 | 5.0 | 5.0 | 5.0 |
| English | v2 | 8 | 5.0 | 5.0 | 5.0 |

**No v2 score improvement was observed on these three questions.** V1 also reached the native ceiling. The English regex checklist missed “ask the responsible department” in both answers; the native semantic evaluation correctly recognized that confirmation path. The fixed checklist was not changed after measurement.

The original custom evaluator omitted its numeric-output contract, producing `null` completeness scores; that failure and a Korean polling timeout remain preserved. After correcting only the output format, **completeness alone was evaluated once on the same original answers**. There were 12 target responses and four native runs: two original runs and two completeness-only corrections. No target answer or valid built-in metric was resampled. All four runs were verified terminal.

**Optimizer and holdout:** Optimizer optionally generates candidates from dev data. A holdout is an independent final exam kept out of instruction development and optimization. These exposed teaching questions are not a holdout, and neither operation was newly run here. The earlier Optimizer actually ran and failed with evaluator errors; its holdout stayed sealed because the full dev gate failed.

## Success criteria

You can compare the actual v1/v2 answers under the same checklist and explain which instruction addresses which omission.
Claim a measured improvement only when the actual `delta` is positive. Repeated validation, holdout runs, and Optimizer are not prerequisites.

The [current instruction status](../../validation/current/instructions.json) and [latest real measurement](../../validation/current/report.json) link the bilingual originals, actual model identities, per-row scores and preserved errors. Older records stay in Git history; this tie is not relabeled as improvement.

## Troubleshooting

First confirm that model, context, questions, and checks were identical. Distinguish JSON errors, missing citations, and omitted answers.
Do not overwrite an existing comparison. Never replace a model error with an “expected v2 answer.”

## Cleanup

This exercise creates no agents, Hosted sessions, or Optimizer jobs. Inspect the original responses and confirm native runs are terminal, then continue to L09. Retain model deployments until deletion is separately approved.
