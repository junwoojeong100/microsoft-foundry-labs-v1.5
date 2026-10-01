> **What you will build:** Connect the observed v1/v2 differences to the right improvement method, distinguishing instructions from model training.

## Objectives

Start with **RAG for new facts, instructions for procedure/omissions, and fine-tuning for repeated learned behavior**.
The current improved instructions are [v2](../../data/en/prompts/agent-v2.txt). Do not create v3/v4 files or growing evaluation numbers for each edit.

## Concepts and lab map

**What you will try:** Instruction improvements, controlled comparison, optional Agent Optimizer, and SFT data preparation.

**What is it, and why does it matter?** Instructions change how the model uses supplied information. Fine-tuning learns behavior from examples.
Neither establishes a missing contract, exchange rate, or permission.

**How do you use it?** Read the originals and per-row Foundry evaluation reasons from L08's single comparison and classify the cause.
Keep ties and regressions; repeatedly searching for a higher score is not the exercise.

**Where do you run it?** Use the [instruction comparison](../../samples/instruction_lab.py), [optional Optimizer code](../../samples/optimizer_lab.py),
and [training-data preparation](../../samples/prepare_tuning.py). Use Optimize/Fine-tune in the portal to understand inputs, limits, and outcomes.

## Prerequisites

Use L08's v1/v2 Prompt Agent originals from the 12 fixed questions, supporting checklist, native scores, and per-row reasons. Do not call the model again if that comparison already exists.
Optimizer and real training jobs require separate approval, supported models, and permissions; they are not core-course completion requirements.

## Steps

### 1. Select the right improvement

| Observed problem | First approach |
| --- | --- |
| Missing new policy facts | Check retrieval, documents, currency, and access scope |
| Omitted subquestions or evidence | V2's question separation, claim-specific sources, and final completeness check |
| Invalid arguments or excessive actions | Function schemas and server-side intent/quantity validation |
| Repeated format/style problems | Consider fine-tuning after preparing sufficient examples |

Do not weaken v1 or put question-specific answers into v2. Both receive the same context, model, questions, and criteria.
The educational v1 is a simple starting instruction focused on role and goal. V2 adds a reusable procedure based on the possible omissions being studied: decompose the request, separate verified facts from unknown or restricted information, select evidence for each claim, check thresholds and tool boundaries, and review for omissions. V1 is not intentionally wrong or constrained to lower its score.

### 2. Optional: Understand Agent Optimizer

Agent Optimizer is Limited preview; verify availability and supported models separately.
L08's one comparison is enough for the core exercise. Repeated jobs and automatic candidate promotion are unnecessary.
The existing Hosted Responses agent in this repository uses `contoso-chat` (GPT-4.1-mini), while L08 evaluated GPT-6 Sol Prompt Agent versions. The Hosted path cannot produce a same-model Optimizer candidate for that comparison. The two Prompt Agents created for L08 are evaluation-only; no Hosted agent was redeployed or changed. The manually authored v2 is not described as an Optimizer output.

```bash
python samples/optimizer_lab.py --agent ACTUAL_RESPONSES_AGENT --version ACTUAL_NUMERIC_VERSION --optimizer-deployment APPROVED_OPTIMIZER_DEPLOYMENT --prompt-file data/en/prompts/agent-v2.txt
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `optimizer_lab.py` | Inspect the plan for your actual Responses agent/version, reflection deployment, and current v2 instructions. Replace the placeholders with your own verified values. | Without `--live`, no Azure request occurs. Old deployment numbers or evaluations do not validate the edited v2. |

</div>

Only after separate live approval and verification of an equivalent model path, align the deployed instructions, input data, and evaluators.
The advanced runner retains source-freeze checks, dev-only input, at most two candidates/one stall, time limits, cancellation, and owned-session cleanup.
Do not bypass an old freeze that differs from current code or reuse a consumed exam.
Service `succeeded` is not proof of improvement. Inspect missing, errored, and failed rows and retain a no-improvement outcome.
Record service-generated, operator-edited, and manually authored instructions as different sources. A Korean translation/review of English dev instructions is not a Korean optimizer output, and Korean responses require separate measurement.
Preparing this advanced path is not a prerequisite for the v1/v2 learning comparison.

### 3. Learn the local SFT format

```bash
python samples/prepare_tuning.py
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `prepare_tuning.py` | Prepare training/validation JSONL from checked-in synthetic examples. | Local files only; no Azure upload, training, or deployment. |

</div>

These small seeds teach the format; they do not guarantee useful training results.
Never copy evaluation answer keys or holdout cases into training data.

### 4. Select a training approach

| Method | Data | Main concern |
| --- | --- | --- |
| SFT | Inputs and desired outputs | Avoid imitating incorrect answers |
| DPO | Preferred and rejected responses | Consistent preferences |
| RFT | Problems and a verifiable grader | Reward hacking and grader errors |

![Fine-tuning. Distinguish the product example from an actual workshop training job.](../../assets/portal/en/14-fine-tuning.png)

Real training requires separate approval after reviewing model/region support, data handling, and costs.
Completing a training job, deploying a model, and improving evaluation results are separate outcomes. Do not default to automatic deployment or promotion.

## Success criteria

Explain the intended v2 improvements and actual answer differences, then choose retrieval, instructions, tool constraints, or training appropriately.
Preparing files does not establish completed training or a score increase.

### Carry the measured L08 result into the next decision

| Language | Supporting checklist v1→v2 | Native completeness, relevance, groundedness |
| --- | ---: | --- |
| Korean | 33/40→33/40 (tie) | Completeness/groundedness 5.0→5.0; relevance 4.9167→5.0 (+0.0833) |
| English | 29/40→28/40 (−1) | All three metrics tied at 5.0→5.0 |

Only one Korean native relevance row, `compound-request-no-tools`, changed from 4 to 5; all other metrics tied. This is a limited gain observed on a small, exposed dev comparison, not statistical significance, generalization, or operational promotion. The supporting checklist tied in Korean and fell by one in English; every changed critical flag was manually checked against the original response. Some v2 answers explicitly state access, eligibility, and draft/order/payment boundaries that the regex missed. Do not alter the instructions or checks to fit the result; use the [per-question originals and native reasons](../../validation/current/report.json). V2 used 7,376 more tokens in Korean and 5,157 more in English, with mean latency increases of 0.427 and 0.496 seconds.

The [current Prompt Agent comparison](../../validation/current/report.json) records actual bilingual v1/v2 results on 12 questions each and pins agent names/versions. The Hosted Optimizer path uses GPT-4.1-mini, unlike the GPT-6 Sol Prompt Agents, so an equivalent model condition was unavailable and no live Optimizer job was submitted. Two evaluation-only Prompt Agents were created, but no Hosted agent or model deployment was deployed or changed. V2 was authored directly, not generated by Optimizer. The existing holdout stayed sealed. The [previous Optimizer original](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/blob/6fddd4642be0d0ac9dfee9b9b51e7b00b5cf1cde/validation/english/automated-v5/optimizer.json) preserves its actual execution and failed outcome; it is not relabeled as the current comparison.

## Troubleshooting

Distinguish model support, Preview access, deployed instructions, dev inputs, and evaluator failures.
When prerequisites are absent, record not executed and finish the learning objective with L08's single comparison.

## Cleanup

Local data preparation creates no cloud job. If you separately approved a job, confirm that exact owned job and its sessions have stopped.
Do not delete resources or change access without separate approval.
