> **What you will build:** Connect the observed v1/v2 differences to the right improvement method, distinguishing instructions from model training.

<div class="lab-brief" markdown="1">

**Format:** Advanced elective · begin with existing evaluation results and local training-file preparation.

**Start here:** Read one English answer pair from L08 and identify whether instructions, retrieval, or tools need attention.

**What to check:** Explain the chosen improvement and the 16 training/8 validation rows. Optimizer submission and real training are optional.

</div>

## Objectives

Start with **RAG for new facts, instructions for procedure/omissions, and fine-tuning for repeated learned behavior**.
The current improved instructions are [v2](../../data/en/prompts/agent-v2.txt). Do not create v3/v4 files or growing evaluation numbers for each edit.

## Concepts and lab map

**What you will try:** Choose an improvement method and prepare training files.

**What is it, and why does it matter?** Instructions change the answering procedure; fine-tuning learns behavior from examples. SFT trains on input/answer pairs. Neither creates missing facts or permissions.

**How do you use it?** Identify a cause in L08's answers, then repair a label in a local training example. Distinguish file generation from actual model training and score improvement.

**Where do you run it?** Start with [L08 comparison](../../samples/instruction_prompt_agent_lab.py) reading and [local data preparation](../../samples/prepare_tuning.py). [Optimizer](../../samples/optimizer_lab.py) and portal training are separate options.

## Prerequisites

Use L08's v1/v2 Prompt Agent originals from the 12 fixed questions, supporting checklist, native scores, and per-row reasons. Do not call the model again if that comparison already exists.
Optimizer and real training jobs require separate approval, supported models, and permissions; they are not core-course completion requirements.

## Steps

### 1. Select the right improvement

| Observed problem | First approach |
| --- | --- |
| Missing new policy facts | Check retrieval, documents, freshness, and access scope |
| Omitted subquestions or evidence | V2's question separation, claim-specific sources, and final completeness check |
| Invalid arguments or excessive actions | Function schemas and server-side intent/quantity validation |
| Repeated format/style problems | Consider fine-tuning after preparing sufficient examples |

Do not weaken v1 or put question-specific answers into v2. Both receive the same context, model, questions, and criteria.
The educational v1 is a simple starting instruction focused on role and goal. V2 adds a reusable procedure based on the possible omissions being studied: decompose the request, separate verified facts from unknown or restricted information, select evidence for each claim, check thresholds and tool boundaries, and review for omissions. V1 is not intentionally wrong or constrained to lower its score.

**Make a decision from one row:** Read the **English** `compound-request-no-tools` pair displayed in L08 and its native reasons. Both answers cover the four requests, and all three metrics tie at 5→5. Identify the wording changes without calling them a measured quality gain, then write one line each for **observation → possible cause → next method → remaining uncertainty**. The Korean relevance change from 4→5 is a separate result, not a conclusion to transfer to English. This analysis requires no new measurement or Korean reading.

### 2. Optional: Understand Agent Optimizer

Go straight to **step 3** if your goal is local training-data preparation. You do not need to run this optional feature to use v2.

<details class="optional-path" markdown="1">
<summary>Optional reference: Optimizer prerequisites and submission plan</summary>

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

</details>

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

Open the terminal's `Prepared train=16, validation=8 in results/tuning-…` directory in an editor. The source is [tuning/examples.json](../../data/en/tuning/examples.json); outputs are `train.jsonl` and `validation.jsonl`. **One line is one training example.** The first generated line is shown below. It transforms a checked-in example; it is not a measured model response.

```json
{"messages":[{"role":"system","content":"Classify the request as exactly one of POLICY, STOCK, DRAFT, or CLARIFY."},{"role":"user","content":"What is the regular replacement period for a laptop?"},{"role":"assistant","content":"POLICY"}]}
```

| What to inspect | How to judge it | Next action on failure |
| --- | --- | --- |
| `system` / `user` / `assistant` | Classification rule / request / desired label | Compare role order and label with the source example |
| Four labels | `POLICY` policy, `STOCK` lookup, `DRAFT` draft request, `CLARIFY` ambiguous request | Check for conflicting labels on equivalent requests |
| 16 train / 8 validation rows | Separate training and checking examples without duplicate inputs | Preserve generator errors; inspect empty/duplicate input and split/label typos |
| A `DRAFT` example versus execution | **Intent classification**, not successful stock allocation or draft creation | An out-of-stock request can still have DRAFT intent; L06 functions decide whether execution is allowed |

`validation.jsonl` checks training behavior; it is distinct from L08's dev comparison and the sealed release holdout. This small seed teaches format, not useful training performance. Never expand it by copying answer keys or holdout cases.

<div class="practice-block" markdown="1">

**Try it:** In VS Code, copy `data/en/tuning/examples.json` to **`results/l20-examples.json`**. Create `results` if absent; do not edit the original. In the copy's first training row, deliberately change `POLICY` to `POLCIY` and save.

```bash
python samples/prepare_tuning.py --input results/l20-examples.json --output results/l20-tuning
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `--input ... --output ...` | Checks labels, duplicates, and splits in the synthetic copy before creating a new output folder. | Initially raises `Unrecognized training label` without writing training files. No Azure requests. |

</div>

**Change one thing:** Correct only the typo to `POLICY` and rerun **the same command**. Expect 16 rows in `train.jsonl` and eight in `validation.jsonl`. Existing output folders are not overwritten; use another name for a subsequent experiment. Files use UTF-8 BOM, and their first example matches the JSON above.

**Explain the result:** Why can valid JSON still be rejected as training data? Why does the DRAFT classification not establish an order when quantity/stock are unknown? Separate data format, label meaning, and model performance. Completing only this local exercise means **data preparation complete / model training not executed**.

</div>

### 4. Select a training approach

| Method | Data | Main concern |
| --- | --- | --- |
| SFT | Inputs and desired outputs | Avoid imitating incorrect answers |
| DPO | Preferred and rejected responses | Consistent preferences |
| RFT | Problems and a verifiable grader | Reward hacking and grader errors |

![Fine-tuning. Distinguish the product example from an actual workshop training job.](../../assets/portal/en/14-fine-tuning.png)

Real training requires separate approval after reviewing model/region support, data handling, and costs.
Completing a training job, deploying a model, and improving evaluation results are separate outcomes. Do not default to automatic deployment or promotion.

### 5. Optional execution: train and compare one SFT model end to end

This complete path applies the [official fine-tuning portal procedure](https://learn.microsoft.com/azure/foundry/openai/how-to/fine-tuning) to synthetic **request-intent classification**. It is separate from L08's GPT-6 Sol instruction comparison and was not executed as part of this documentation update.

<details class="optional-path" markdown="1">
<summary>After separate cost approval: baseline → files → training → checkpoint → deployment → identical questions</summary>

#### 5-1. Record the execution scope first

Obtain the **training-capable resource/region, base deployment name, training permission, separate deployment permission, maximum budget/wait deadline, and stop owner** from the administrator. Without them, do not submit. Training can take hours; that wait is not included in the 45-minute hands-on estimate.

| Item | Teaching configuration |
| --- | --- |
| Task | Four labels: POLICY / STOCK / DRAFT / CLARIFY |
| Base model | `gpt-4.1-mini`, version `2025-04-14`; verify current support |
| Region / training type | For example, supported **Standard** training in Sweden Central; first approve the processing location |
| Training / validation | Your `results/l20-tuning/train.jsonl` / `validation.jsonl` |
| Method | Supervised fine-tuning (SFT) |
| `n_epochs` | 2 |
| `batch_size` / `learning_rate_multiplier` | Service default / 0.1 |
| Seed / Suffix | 42 / `contoso-intent` |
| Automatic deployment | **Off** |
| Run count | One training job; eight base answers plus eight candidate answers; no automatic retries |

This small-data configuration teaches the procedure, not guaranteed improvement or minimum cost. **Sixteen training examples are a format exercise**; useful improvements generally need more diverse reviewed examples. Do not change or overwrite L02's base deployment.

#### 5-2. Preserve eight baseline answers before training

Open the base `gpt-4.1-mini` deployment's Playground. Use **the same classification rule as `messages[0].content` (system) in the generated JSONL** for Instructions. Connect no tools; where supported, fix temperature=0 and maximum output=64 tokens.

Send only **`messages[1].content` (user)** from each of the eight validation rows once, in a new conversation. Do not append the expected `messages[2].content` (assistant). Record `row / question / expected label / actual answer / response ID / tokens / latency`. Missing tokens are uncollected; self-timed latency is a manual measurement.

#### 5-3. Select files and submit one job

Open **Build → Fine-tune → Fine-tune**. Select base model/version → SFT → Standard training → **Upload new dataset**. Do not swap training and validation files. Wait for upload validation and compare existing datasets with your actual files rather than their names alone.

Enter the table's parameters, keep automatic deployment off, review scope, and select **Submit once**. Privately record the job ID, resource, input-file IDs, and parameters. Do not resubmit because the screen takes time to update.

#### 5-4. Read metrics and checkpoints

Open that job's **Job details → Monitor / Checkpoints**. `queued` and `running` are not completion; preserve original errors for `failed`. At the approved deadline, the owner uses the supported stop operation for that job and confirms its state. Closing the browser does not stop training.

| Observation | Interpretation |
| --- | --- |
| `train_loss` | Fit to training data, not evidence of performance on new questions |
| `full_valid_loss` | Validation loss during training; falling train loss with rising validation loss suggests possible overfitting |
| `full_valid_mean_token_accuracy` | Validation token prediction, not the four-label per-question accuracy |
| Checkpoints | Compare epoch-level validation metrics and available model IDs; do not blindly select the last |

Do not estimate missing values. Record service completion, checkpoint creation, and quality improvement separately.

#### 5-5. Deploy only an approved candidate under a separate name and compare

On the selected checkpoint/model details, select **Deploy**, an approved nonproduction deployment type, and a distinct name such as `contoso-intent-ft`. Use a short-lived Developer evaluation type only when its support and terms are approved. Training approval does not automatically cover deployment/retention costs.

After readiness, apply **the identical system rule, no tools, and the same parameters** in the candidate Playground. Send the same eight user questions once each. Record both models' actual versions and conditions.

| Result to retain | Calculation/interpretation |
| --- | --- |
| Per-question correctness | Output must be exactly the expected single label; added explanation fails the output contract |
| Accuracy for all eight completed questions | Correct ÷ 8. Missing/errored rows leave the comparison incomplete; do not calculate 100% from successful rows only |
| Token/latency difference | Compare totals/means over the same eight questions; do not replace missing measurements with zero |
| Adoption decision | Retain ties/regressions; training alone does not justify promotion |

This validation set was used during training, so it is **not an independent holdout**. Preserve the existing sealed exam and business release gates. Record owners/deadlines for uploaded files, trained models, and deployments; delete only after separate approval.

</details>

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

If the Optimizer plan is blocked, first check Preview access, Responses protocol, and matching model/deployed instructions. If the supporting checklist and native scores disagree, compare the original, check condition, and judge reason rather than treating one score as ground truth. For SFT generation errors, inspect inputs/labels/splits in the table above. Leave cloud tasks not executed when their prerequisites are absent.

## Cleanup

Local data preparation creates no cloud job. If you separately approved a job, confirm that exact owned job and its sessions have stopped.
Do not delete resources or change access without separate approval.
