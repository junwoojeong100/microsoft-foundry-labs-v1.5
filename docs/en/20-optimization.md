> **What you will build:** Choose the right target for improvement and prepare training-ready data and a comparison process that guards against overfitting.

## Objectives

Start by considering **RAG for new facts, prompts for instruction problems, and fine-tuning for behavior that should be learned from repeated examples**. A current base model does not necessarily support every training method.

## Concepts and lab map

**What you will try:** Classifying failure causes, comparing prompt/Agent Optimizer candidates, preparing SFT data, and conditionally running fine-tuning.

**What is it, and why does it matter?** Prompt optimization changes the instructions, tool descriptions, and other guidance given to a model; fine-tuning teaches behavior through examples or rewards. Neither replaces RAG as a way to safely keep company facts current. An optimizer also generates and evaluates candidates repeatedly, so it usually costs more than a single question. Distinguishing a “successful job” from a “candidate better than the baseline” prevents unnecessary promotion.

**How do you use it?** First classify whether a failure involves retrieval, instructions, formatting, or repeated behavior. Compare the baseline and candidates using the same dev criteria, and send only candidates with demonstrated improvement to a separate independent test. Clearly separate learning the format from a small local fine-tuning seed file from submitting a real paid training job.

**Where do you run it?** The implementation is in [optimizer_lab.py](../../samples/optimizer_lab.py), the [optimizer-specific adapter](../../hosted/optimizer_responses.py), and [prepare_tuning.py](../../samples/prepare_tuning.py). Choose an English instruction source matching the deployed version. The approved v4 run deployed [agent-v7.txt](../../data/en/prompts/agent-v7.txt) as English Responses version 3; verify your own environment rather than copying that number. Use the portal for Optimize/Fine-tune settings, progress, and result comparisons.

## Prerequisites

You need the English baseline and failure cases from L08, separate dev/holdout data, and approval for training, evaluation, and deployment costs. Keep `FOUNDRY_LAB_LANGUAGE=en` selected and use only the English checkout's configuration and receipts. Submitting an actual training job is optional and may involve waiting tens of minutes to several hours or longer.

## Steps

### 1. Classify the cause first

| Failure cause | First approach |
| --- | --- |
| Does not know company policies | Document retrieval and knowledge connections |
| Cannot find the right document | Chunks, retrieval, permissions, and freshness |
| Tool selection/descriptions are ambiguous | Schemas, descriptions, and instructions |
| Only the output format is inconsistent | Structured outputs and validation |
| Repeated behavior needs enough examples | Compare fine-tuning |

### 2. Experiment with Prompt / Agent Optimizer

If the agent's **Optimize** experience is available, check the baseline version, dev data, evaluation criteria, judge/optimizer models, candidate count, and estimated cost. **Agent Optimizer is Limited preview in the GA status table.** If access is unavailable, record the path as blocked. A separate comparison loop that manually revises prompts based on dev failures is optional guidance.

For Prompt agents, optimization can target instructions, function descriptions, and model selection; for Hosted agents, it can target instructions, skills, tool descriptions, models, and more according to the optimizer-ready configuration. This differs from fine-tuning, which trains model weights.

Optimization/evaluation involving tools can call real tools repeatedly. Limit these to nonproduction read/draft tools. Optimizing a client-side function description does not mean that the quality of actual function execution was evaluated.

Do not automatically promote a candidate to the latest version. Inspect the change diff, quality, tokens, and latency, then reevaluate with an **unused holdout**.

The bundled native Agent Optimizer path:

```bash
python samples/optimizer_lab.py --agent ACTUAL_RESPONSES_AGENT --version ACTUAL_NUMERIC_VERSION --optimizer-deployment APPROVED_OPTIMIZER_DEPLOYMENT --prompt-file data/en/prompts/agent-v7.txt
AZURE_DEV_USER_AGENT=microsoft_foundry_skill python samples/optimizer_lab.py --agent ACTUAL_RESPONSES_AGENT --version ACTUAL_NUMERIC_VERSION --optimizer-deployment APPROVED_OPTIMIZER_DEPLOYMENT --prompt-file data/en/prompts/agent-v7.txt --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Submit a new optimization job only after separate approval for its execution costs.

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `optimizer_lab.py` | `--agent/--version` identify the English Responses baseline, `--optimizer-deployment` identifies the approved reflection deployment, and `--prompt-file` must match the deployed English instructions. Replace the agent/version/deployment placeholders; use `data/en/prompts/agent-v7.txt` only after that file has been deployed in the selected version. Without `--live`, read the submission plan. | No Azure job is created. Check the suite, dev count, candidate/time limits, and 0 holdout cases. |
| 2. The same command with `--live` | Submits a real native optimizer job with the reviewed settings and observes results for a bounded time. `AZURE_DEV_USER_AGENT` identifies the command process; it is not an authentication token. | Multiple model/agent/evaluator calls and Hosted charges may apply. Check results, warnings, cancellation, and session stopping; candidates are not automatically promoted. |

</div>

In the first command, check the **full dev count for the current suite and 0 holdout cases**, a maximum of 2 candidates, and at most 1 stall. English now defaults to `automated-v5` with **40** unchanged exposed v4 dev cases; the historical v3 job used 30.
`DEFAULT_SUITE` is the default; you can also select a suite explicitly with `--suite`. Verify the selected suite rather than substituting a smaller or easier sample.
The optimizer does not open or submit the newly sealed holdout.
It reads only the dev file through `load_cases(suite, split="dev")`, not all splits followed by filtering.
Record the suite, dev IDs/hashes, and actual submission settings in the raw evidence; do not claim a holdout-based quality pass.
Both `payload(...)` and the CLI follow `DEFAULT_SUITE`. Diagnosing legacy data requires
an explicit `suite="legacy-v1"`; do not submit new legacy jobs.

Hosted native optimization targets the **Responses adapter** prepared with
`AZURE_DEV_USER_AGENT=microsoft_foundry_skill azd deploy contoso-purchasing-responses --no-prompt`.
Submitting the Invocations agent as-is causes the service to reject it with 400.
Here, `contoso-purchasing-responses` is the separate service name in `azure.yaml`. `deploy` creates a real remote version, and `--no-prompt` only skips confirmation questions. If L14 already deployed the correct version, do not deploy it again.
The current optimizer-specific entry point is **`hosted/optimizer_responses.py`**, and its separate build path is
**`.build/contoso-responses`**. Build it with the English profile so that its `lab-profile.json` binds `en`; the primary Invocations build remains separate and needs separate validation.
Check the optimizer model family required by the service separately.
In the historical Korean run, this API did not accept `gpt-5-mini` as a reflection model; a `gpt-5.1` deployment was used separately
after checking the supported list. That is historical compatibility evidence, not a guaranteed English deployment choice. Support for inference models differs from support for optimizer reflection models.
The Hosted package includes `load_config()` from `azure-ai-agentserver-optimization==1.0.0b1`
and `.agent_configs/baseline/`. At packaging time, the baseline model is pinned to the approved deployment name;
an offline package built without the environment must be regenerated before execution.
The dedicated adapter passes credentials to the resolver and caches configuration in a writable location **under HOME**.
Model inheritance explicitly uses the packaged baseline model **only when a successfully resolved, instruction-only
optimizer overlay omits `model` or sets it to `null`**. It is not a fallback that copies baseline answers
or hides errors behind an arbitrary default model from the environment. Invalid explicit models, invalid configurations,
and resolver failures are rejected.
Do not target an agent whose client-side functions cannot be executed by the server.
The historical Korean experiment targeted `contoso-purchasing-responses` version `2`, which included `agent-v4.txt`.
Its later successful native execution used the dedicated Responses **version `3` / `agent-v6.txt`** combination.
Neither version number is a value to copy into a new English run. Use the actual English Responses version and **the same instruction file that was deployed**. V7 is a new local candidate, not the instructions of the historical English version 2.
New `--live` jobs require `--prompt-file`. The function/plan's v4 default exists for historical diagnostics;
you cannot omit this option and submit a job for a new version. The runner does not guess the latest instructions.
With the English profile selected, the prompt argument accepts only `data/en/prompts/*.txt`; it does not read a dataset as an instruction file or silently translate a Korean prompt.
The wire field for inline training data is `train_dataset.items`, not `dataset_items`.

The default time limit is **600 seconds (10 minutes), measured from job creation**. `--max-seconds` accepts only integers from 60–1800.
If measured full-model, three-stage execution takes longer, you can explicitly set `--max-seconds 1200` for a new job.
This is not unbounded waiting or automatic retry; candidate counts, scores, evaluation criteria, and the dev/holdout boundary remain unchanged.
The time limit is saved in the new job receipt. `--resume` must use **the same recorded** `--max-seconds`;
for example, a 1200-second job also requires `--max-seconds 1200` when resumed. Older receipts without the field use 600 seconds.
Resuming retains the deadline measured from the original creation time. It does not revive a canceled 600-second job with a larger budget
or silently extend an existing job's limit.
Rather than SDK automatic LRO polling, the runner submits with `polling=False` and queries through explicit GET requests containing the API version.
The original record of automatic polling failing because the service's `Operation-Location` lacked an API version is also preserved.
On timeout, query failure, or interruption, `finally` requests cancellation and verifies a terminal state within a separate **90-second cancellation bound**. It preserves terminal/outcome artifacts even when monitoring failed. Progress snapshots include the service's reported progress, candidate/evaluation IDs, warnings and observed stagnation; they do not invent a server-side root cause.
The new cleanup path uses the project SDK's paginated session list, not only the CLI list or baseline-filtered telemetry. It makes **six fresh sweeps**, at most **180 seconds**, at most **100 listed sessions per sweep**, and stops at most **10 distinct scoped sessions**. A reactivated session may need another stop in a later sweep, so the total stop-request bound is **60**; each stop has at most six readbacks, with no SDK retry. It requires two quiet final sweeps; a last-sweep arrival, error, truncated inventory, or unverified stop remains an explicit incomplete-cleanup result.
Native candidates can appear as `version_ref` sessions whose version is `draft-...`, not as a `cand_...` session indicator. For these, the runner reads only the exact version and verifies its optimizer candidate ID and resolver against the recorded job/project. It preserves unrelated versions, other jobs, and every session in the pre-job snapshot. Baseline sessions are bounded to the recorded version and the job window plus a **180-second creation tail** for post-cancellation arrivals; do not run concurrent work against that dedicated baseline.
A successful stop is followed by an inactive readback for the same ID. Already verified IDs remain tracked if the service changes `created_at` during stop/idle transitions; those timestamps are not used to forget a known session. The cleanup receipt states its bounded observation scope, not a guarantee that no future session can ever appear.
The Responses adapter also rechecks cancellation after waiting for its concurrency gate and after an in-flight call. A cancelled queued request does not start new inference. An already running synchronous model request still has its existing bound; cancellation is not instantaneous termination of that request.
If cancellation/stop verification fails, report that the job or session **may still be running**.
Do not overwrite existing jobs/receipts or delete resources. Candidates are not automatically deployed or promoted.

| Observation | Verdict to record |
| --- | --- |
| `succeeded` but with reflection failure/authentication/timeout warnings | **operational_failure** — do not reclassify it as success |
| Reflection/evaluation ran normally and ended without improvement according to `max_stalls` | **executed_no_improvement** — execution was valid, but no quality improvement is claimed |
| Only a baseline is present, without evidence of reflection execution | **reflection_unverified** |
| Missing candidate changes, missing/errored evaluation rows, or partial results | Incomplete evidence or operational failure — not completed improvement |

Also check the separate native evaluation's `completed` state, row count, and `errored=0`.
Do not judge successful optimization or a quality pass from service status or a single baseline score.
Human candidate review is optional guidance; keep `human_review_completed=false` truthful.

If service access is blocked, record **native optimizer blocked**. If you optionally author a separate candidate
based on actual dev failures, do not present it as a native optimizer result.
Keep the candidate file and reasons for the change, compare using the same dev criteria from L08, then check the holdout once.

azd's automatic suite generation may require at least 15 samples. Do not duplicate cases or include
the sealed holdout just to meet the count. The bundled SDK runner directly submits only the selected suite's full dev set;
distinguish that from the automatic-generation CLI's supported scope.
For existing legacy-v1 jobs, only query resumption with the original receipt is permitted; new legacy submissions are rejected.
Those historical Korean diagnostics belong in their original owner-controlled checkout and are not a step in this English lab. Do not copy their private settings or receipts into the English checkout. The English resumption example below uses only a job actually recorded in the English environment.

### 3. Prepare local SFT data

This additional exercise uses [data/en/tuning/examples.json](../../data/en/tuning/examples.json) to teach a simple behavior—classifying English inquiries as `POLICY`, `STOCK`, `DRAFT`, or `CLARIFY`—rather than memorizing answer content.

```bash
python samples/prepare_tuning.py
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `prepare_tuning.py` | Reads `data/en/tuning/examples.json` under the selected English profile and creates SFT-format files with 16 training and 8 validation examples in a new results directory. | Creates local files only. No Azure upload, training, model deployment, or training charges. |

</div>

This generates `results/tuning-.../train.jsonl` and `validation.jsonl`. The 16/8 examples are **seeds for learning the format**. Meeting the service's minimum of 10 examples is different from achieving meaningful quality improvement. For real training, review tens to hundreds or more representative, high-quality examples.

The basic SFT structure:

```json
{"messages":[{"role":"system","content":"Classify the inquiry using only POLICY, STOCK, DRAFT, or CLARIFY."},{"role":"user","content":"Tell me the laptop replacement policy."},{"role":"assistant","content":"POLICY"}]}
```

The English example preserves the literal output labels `POLICY`, `STOCK`, `DRAFT`, and `CLARIFY`; the user asks for the laptop replacement policy, so the label is `POLICY`.

The output includes a UTF-8 BOM to meet the encoding requirements in the current fine-tuning documentation. Before uploading through the portal, recheck file validation results and the target model's requirements. Do not upload evaluation query/response JSONL unchanged as SFT data.

### 4. Choose SFT / DPO / RFT

| Method | Required data | Suitable problem | Pitfall |
| --- | --- | --- | --- |
| SFT | Input + desired output | Formatting, classification, and repeated business behavior | Learning from poor-quality examples |
| DPO | Preferred/dispreferred outputs for the same input | Response preferences and style | Ambiguous preference criteria |
| RFT | Input + a verifiable grader | Complex behavior that can be judged through rewards | Reward hacking and grader errors |

For vision fine-tuning, tool calling, distillation, and open-model training, also check model-specific support, licenses, and data rights separately. SFT/DPO/RFT are not all supported on every model. Some GA training capabilities may still have restricted access.

### 5. Conditional: Run an actual training job

![Build → Fine-tune in the English Contoso project. Locate the training entry point and distinguish product illustrations from actual lab-job results.](../../assets/portal/en/14-fine-tuning.png)

**Read the screen:** Locate **Start fine-tuning** under **Build → Fine-tune**. English screenshot 14 shows a **product sample, not a Contoso training job**. Its prices, scores, or Clone training examples are not lab results or evidence of cost savings. The [English capture log](../../content/portal-screenshots.en.json) records the observation scope. Do not infer that a Contoso training job was submitted, completed, or deployed from that screenshot.

From **Start fine-tuning**, or **Fine-tune a model** in the applicable UI, choose a supported base model, method, and training tier. Upload train/validation files separately and leave auto-deploy off initially. After checking costs and data-processing location, the responsible operator selects Submit.

Check job status, training/validation curves, and checkpoints. The last checkpoint is not always the best. Deploy to an approved temporary deployment and compare with the baseline using the same held-out data and judge settings.

## Success criteria

You have validated the local data format and splits. If you ran actual training, compare **quality, latency, tokens, and total cost** with the baseline and record the reason for your selection. Preparing data alone is not completed training.

**Preserved English v3 Optimizer outcome:** The [single dev-only job](../../validation/english/current/optimizer.json), started before the holdout result was known, reached its explicit **1200-second limit** and was verified `cancelled`, with **no promotion or claimed improvement**. The runner initially stopped two baseline sessions; final project-wide closeout found three additional owned baseline/candidate sessions. After recording and stopping their exact identities, a fresh readback confirmed zero active sessions. See the [original report](../../validation/english/current/report.json). Cancellation alone is not proof that every child session stopped.

**Follow-up diagnosis, from preserved originals:** The job began at 13:34:45 UTC; the baseline first appeared in polling at 13:43:56 UTC, with a native score of 29/30. The last running snapshot had `candidate_generated=true` but `candidates_completed=0`; at cancellation at 13:54:45 UTC, the latest service-reported elapsed time was about 723 seconds. This locates the unfinished work after candidate generation, but no service error or reflection warning identified a precise latency or throttling cause. Two missed sessions used a `draft-...` version, and another baseline session was created 18 seconds after cancellation. The former one-shot listing, baseline-only trace filter and terminal timestamp cutoff were insufficient for those records. The [local follow-up record](../../validation/english/improvements-v4/report.json) made no new native execution claim.

**Latest v5 native run:** [Job `opt_7c6be680d37342dab3c41b2b06b52803`](../../validation/english/automated-v5/optimizer.json) used all 40 unchanged dev cases and zero holdout cases, with one job, at most two candidates, one stall and a 1200-second bound. It ended in **647 seconds** with service `succeeded` / `stopped_early`, but its 40 native rows contain **38 passed, 1 failed and 1 errored**. The outcome is **`operational_failure`**, not a quality pass or improvement. Baseline score **0.9453125** and “perfect scores” wording do not override those rows. No candidate was generated or promoted, and reflection execution was not established.

The [native originals](../../validation/english/automated-v5/optimizer-native.json) retain the empty engine response and evaluator error for `v5-dev-08`, without inventing a detailed cause. For `v5-dev-27`, the built-in task-adherence judge penalized refusal to confirm an unsupported deduction/FX conversion; its reason conflicts with the frozen Contoso oracle. The failed metric is preserved, not relabeled. All 39 parseable engine responses retain v2 authorization, actual tools, citations and runtime/prompt fingerprints. They are separate optimizer outputs, **not replacements for the Invocations dev failure**.

Six SDK cleanup sweeps completed in about **63.5 seconds**, stopping two new owned baseline sessions. A fresh [final readback](../../validation/english/automated-v5/operations.json) confirmed all five sessions created by v5 stopped and all recorded jobs terminal. The scoped Responses job list succeeded; this is not a global idle claim. No timeout or new draft candidate occurred, so cancellation and new-candidate cleanup were not exercised live in this run.

**Preserved v4 native run:** [Job `opt_d99483891d6a459087b2295d6410baaa`](../../validation/english/automated-v4/optimizer.json) used all 40 dev cases, zero holdout cases, at most two candidates and the unchanged 1200-second limit. It finished after **647 seconds** with service `succeeded` / `stopped_early`, but the native task-adherence evaluation had **37 passed and 3 errored**, including `v4-dev-14`, `v4-dev-37` and `v4-dev-40`. The runner correctly returned **`operational_failure`**. Its baseline score was **0.905625**, and the service's “perfect scores” warning is not accepted as a pass. No new candidate or promotion occurred.

Six fresh SDK sweeps stopped two new owned baseline sessions and observed five quiet subsequent sweeps. Final [closeout](../../validation/english/automated-v4/operations.json) verified all five sessions created by this live run inactive. Because no new draft candidate was generated and no timeout occurred, the new draft-version and timeout-cancellation branches remain locally covered but were **not exercised by this live run**. The Optimizer list API returned HTTP 500 through SDK and azd; exact recorded-job GET remained available, so the report makes no project-wide idle claim. This explicitly approved CLI run is not evidence that the optional OIDC workflow below ran.

The preserved v3 Invocations candidate's independent holdout passed only **7/10** with a critical safety citation-evidence failure. No threshold, data, or tested candidate was changed and no holdout rerun followed that result. Do not resume that canceled job with a longer budget, use it to override the failure, promote a candidate, or tune against the consumed holdout. The separate v4 holdout remains unexecuted because its dev attempt was incomplete.

### Historical Korean native result: Valid execution, no improvement

The final job in that **historical Korean run**, **`opt_428b84f689964bb793f83b93b8d34de5`**, completed with **`succeeded`**. The following record is unchanged; it is not an English execution or quality result.

| Item | Verified result |
| --- | --- |
| Target | `contoso-purchasing-responses` version `3`, `hosted/optimizer_responses.py` |
| Input | `agent-v6.txt`, 20 `automated-v2` dev cases, 0 holdout cases |
| Limits | `--max-seconds 1200`, maximum 2 candidates, `max_stalls=1` |
| Native baseline / best | **1.0 / 1.0** |
| Reflection | Actual execution verified |
| Reason for termination | Reached `max_stalls=1` without improvement — not an authentication/reflection failure |
| Newly adopted candidates / promotions | **0 / 0** |
| Verdict | **Valid execution completed (`executed_no_improvement`)**, with no improvement claimed |

Do not classify the absence of an adopted candidate as operational failure, or lower evaluation criteria to produce a successful status.
This 1.0 is the **native composite score on that v2 dev set**; it does not establish a quality pass
for a separate v3 holdout, the primary runtime, or the new English profile. No human review is claimed; human review remains optional guidance. New English evidence belongs under `validation/english/`; this historical result does not establish English Optimizer success.

<details markdown="1">
<summary>Preserved Korean-run failures and recovery — you may skip this on your first pass</summary>

### Preserved historical failures and recovery

**The earlier native optimizer job `opt_f732793c2d284a4f874966ed2caca4bf` had service status `succeeded` but returned only a baseline.**
It produced 0 new candidates and had warnings about reflection model errors/timeouts.
Its separate baseline score of 0.95 was not used as a holdout quality pass, and no candidate was promoted.
The improved v1→v4 instructions were **development changes based on dev failures**, not native optimizer output.
In a follow-up check, a Chat Completions call to `contoso-reflection` from the same local CLI user returned HTTP 200,
a `gpt-5.1-2025-11-13` response, and completion. The earlier baseline evaluation also completed 10 cases with 0 errors.
The broad reflection warning therefore was not treated as proof of a specific permission, token, or timeout cause,
and no Owner/broad roles were added. Successful direct model access is separate from successful internal calls by the native service.

A separate v2 local job, `opt_15ea242beb4e4e4f945fac6b5abfa868`, also ended within 5 minutes
with `succeeded`/`stopped_early`, but returned the same reflection warning and only a baseline.
Native evaluation `evalrun_da4f0442f71049ba868dd677b15e310d` had 19 passes and 1 error among 20 cases.
The evaluator status for output item `13` was `error`, but the service response did not include the detailed cause.
The original composite score of 0.91875 is not used as a quality pass.
It is also not directly compared for performance against the earlier 0.95 from a different suite.
Both native sessions were absent from the CLI list, so they were located through the job's traces and then verified through stop/idle readback.
The job, error, and session-stop records are preserved in `results/contoso-optimizer-ea97bd8ba694*.json*`
and `results/contoso-optimizer-3cf33582e7d6.jsonl`.

A later check of the owned resource's metrics found **3 reflection HTTP 429 responses**.
At that time, the 10k TPM limit on `contoso-reflection` was relaxed by setting capacity to 100 for the same GPT-5.1/version/SKU.
HTTP 200 from a small direct probe alone was not treated as evidence that native load handling or the entire authentication path was healthy.

Next, after a baseline of 0.928125, `opt_04988b29201c4eb79f79d2be1261f986` produced
3 empty outputs in each of two evaluation attempts for the same draft and failed with `AllEvaluatorsFailedError`.
The confirmed cause was **the previous runtime rejecting `model=null` in a successfully resolved candidate**.
It was not confirmed as a resolver 401 issue, and the SDK's disk-cache write `OSError` itself was not a fatal error preventing configuration return.
After applying the limited model inheritance described above in the dedicated adapter, **the same candidate**
returned nonempty responses in both local cache-present/cache-absent paths, and remote baseline version 3 also succeeded.

`opt_a78e46ee3f0b4e4a8c98c1fe64c28f13` had a baseline of 0.96875 and was progressing normally without warnings
when the existing 600-second limit canceled it before the full candidate evaluation. This record was not overwritten as a success,
and the existing job's budget was not extended. The separate final job with a 1200-second budget produced the valid execution result above.
Earlier errors, cancellations, and scores remain historical evidence; scores from different runs are not reframed as proof of improvement.

</details>

### Optional: Run and inspect a separately approved English OIDC comparison

First run a single-model probe that reads no datasets at all. A passing probe does not establish native optimizer success
or a quality pass for a new Invocations version. The comparison that follows targets the
**actual English Responses version** matching the supplied English instructions; do not submit an Invocations version to the optimizer.
The commands below explicitly select **English automated-v5 dev: 40 cases and 0 holdout cases**. Replace the version and reflection deployment placeholders with your verified values; use v7 instructions only if that file is in the deployed baseline. V5 permits one submission and at most 1200 seconds; the historical v4 freeze is not rewritten.
Do not submit the sealed holdout. A new live run is optional and permitted only in L22's approved `contoso-validation-en` OIDC CI environment, with separate cost approval and an English ownership ledger. Dispatch from the reviewed `docs/english-live-validation` branch with `language=en`; do not use the old Korean environment.

```bash
AZURE_DEV_USER_AGENT=microsoft_foundry_skill FOUNDRY_AUTH_MODE=cli \
python samples/optimizer_lab.py --probe-reflection --optimizer-deployment APPROVED_OPTIMIZER_DEPLOYMENT --require-oidc --live

AZURE_DEV_USER_AGENT=microsoft_foundry_skill FOUNDRY_AUTH_MODE=cli \
python samples/optimizer_lab.py --agent contoso-purchasing-responses --version ACTUAL_NUMERIC_VERSION \
  --suite automated-v5 --prompt-file data/en/prompts/agent-v7.txt \
  --optimizer-deployment APPROVED_OPTIMIZER_DEPLOYMENT --max-seconds 1200 --require-oidc --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Optional diagnostics in an OIDC CI environment, not an ordinary user login.

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `--probe-reflection` | A trailing `\` continues the same command on the next line. `FOUNDRY_AUTH_MODE=cli` selects CLI credentials, while `--require-oidc` verifies that they belong to the actual CI principal in the ownership ledger. | One reflection model request, at most 256 output tokens, 45 seconds, and 0 retries. Model charges apply, but no dataset or optimizer job is created. |
| 2. `--suite automated-v5 ... --max-seconds 1200` | Selects all 40 unchanged dev cases and the actual English Responses version with matching instructions. Replace the placeholders. The 1200 value bounds seconds from job creation; it does not change candidate limits or gates. | One paid job; no automatic apply/promotion. A personal CLI login alone cannot pass `--require-oidc`; do not bypass it. |

</div>

To inspect an already recorded English job, resume without creating a new job from **the same English checkout containing its original receipt**.
Replace the placeholders below with the exact recorded job, numeric version, and reflection deployment. This example applies only to a job whose receipt records 1200 seconds; otherwise use its exact original limit. Resumption neither rereads the dataset nor promotes candidates. Never substitute the historical Korean job ID.

```bash
AZURE_DEV_USER_AGENT=microsoft_foundry_skill FOUNDRY_AUTH_MODE=cli \
python samples/optimizer_lab.py --agent contoso-purchasing-responses --version RECORDED_NUMERIC_VERSION \
  --suite automated-v3 --optimizer-deployment RECORDED_OPTIMIZER_DEPLOYMENT \
  --resume RECORDED_ENGLISH_JOB_ID --max-seconds 1200 --require-oidc --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `--resume ... --max-seconds 1200` | Queries your recorded English job. Replace all placeholders from its receipt. `--max-seconds` must equal the original receipt's limit, and the deadline remains based on the original creation time. | No new job, holdout submission, or candidate promotion. Do not run it if your English checkout lacks that ownership receipt. Performs only remote queries and necessary termination checks. |

</div>

The probe makes 1 model request, with a maximum completion of 256 tokens, a model response timeout of 45 seconds, and 0 retries.
Before a model call or new job submission, `--require-oidc` compares the `tenant`,
`oidc.principal_id`, and `oidc.client_id` in `results/azure-environment.json` with safe principal metadata from the token.
Raw tokens, keys, and connection strings are neither printed nor saved.

The safe fields CI passes are the project endpoint, account/project names, subscription/RG IDs,
the OIDC identifiers above, `monitoring.appId.value`, and `monitoring.appInsightsId.value`.
General environment variables include `FOUNDRY_LAB_LANGUAGE=en`, `FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_MODEL_DEPLOYMENT_NAME=contoso-chat`,
and `FOUNDRY_JUDGE_DEPLOYMENT_NAME=contoso-judge`; use your actual deployment names, and azd must resolve to the same owned English project.
The project guard compares the value of `azd env get-value AZURE_AI_PROJECT_ENDPOINT` exactly with the owned endpoint.
A separate SDK query checks the agent name, version, and Responses protocol; unresolved values or values for another project are rejected.
In the probe evidence, check `identity.owned_ci_principal=true`, HTTP 200, actual response/request IDs,
the supported model name, and `finish_reason=stop`. Preserve job warnings/errors separately,
and do not replace or relax dev/calibration/release quality gates based on this optional diagnostic result.

## Troubleshooting

Models available for training differ from those available for inference. Check the training region/tier, file format, permissions, and minimum data count. If scores do not improve, first examine the data, evaluation contamination, and grader issues.

## Cleanup

Training jobs, checkpoints/models, inference deployments, and uploaded training files are separate objects. Pay particular attention to inference deployments and reserved/idle costs.
