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

Use the environment from L01 and a callable model from L02. This comparison needs no Hosted deployment, Search service, Optimizer, or holdout.
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
python samples/instruction_lab.py
python samples/instruction_lab.py --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `instruction_lab.py` | Displays v1/v2, the three shared questions, fixed checks, and limits. | Plan only; zero Azure calls. |
| 2. `instruction_lab.py --live` | Run only after separate cost approval. Invokes each prompt once per question with the same model and context. | At most six model calls, 360 seconds, and zero retries. Saves actual answers and scores in one `results/instruction-comparison.json` file. |

</div>

If the result file exists, read it rather than running again. No new agent version or evaluation-run sequence is created.
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
The comparison above uses SDK model calls and a local checklist; it does not create a native evaluation job in that screen.
Use the separately approved [native evaluation runner](../../samples/evaluation_lab.py) only when that additional exercise is needed.
The existing 90% overall and zero-safety/access-failure business gates are not replaced or relaxed by this small learning score.

## Success criteria

You can compare the actual v1/v2 answers under the same checklist and explain which instruction addresses which omission.
Claim a measured improvement only when the actual `delta` is positive. Repeated validation, holdout runs, and Optimizer are not prerequisites.

The [current instruction status](../../validation/current/instructions.json) distinguishes the edited v2 from the [latest preserved Azure originals](../../validation/current/report.json).
Those originals predate this instruction edit; they do not establish its improvement. Older records remain in Git history, not the current reader.

## Troubleshooting

First confirm that model, context, questions, and checks were identical. Distinguish JSON errors, missing citations, and omitted answers.
Do not overwrite an existing comparison. Never replace a model error with an “expected v2 answer.”

## Cleanup

This exercise creates no agents, Hosted sessions, or Optimizer jobs. Inspect the one response file, then continue to L09.
