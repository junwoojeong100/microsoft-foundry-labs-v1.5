> **What you will build:** An educational initial v1 → evaluate → analyze and improve → reevaluate v2 learning loop, grounded in actual answers and evaluation reasons.

<div class="lab-brief" markdown="1">

**Format:** Read preserved actual results by default · a new paid evaluation is optional.

**Start here:** Read the v1/v2 answers to one question below. Mark whether both address the cap, stock, approval, and draft.

**What to check:** Explain a tie or difference using answers, scores, and reasons. Reading these originals is not your own Azure execution.

</div>

## Objectives

**Distinguish differences in the answers from the evaluator's judgment.** V1 is a role-and-goal starting instruction; v2 makes the answering procedure more explicit. Hold v1 fixed in this comparison. The label “v2” does not establish a better answer.

## Concepts and lab map

**What you will try:** Compare two answers to the same question, their scores, and the reasons.

**What is it, and why does it matter?** Evaluation compares expected behavior with the actual answer. Change only the instructions; keep the model, policies, questions, and scoring rules the same.

**How do you use it?** Read the two answers below before looking at their scores. Keep ties and regressions. No new paid evaluation is required.

**Where do you run it?** Read this page. Consult the [questions/checklist](../../data/en/evaluation/instruction-comparison.json), [v1](../../data/en/prompts/agent-v1.txt), [v2](../../data/en/prompts/agent-v2.txt), and [optional runner](../../samples/instruction_prompt_agent_lab.py) when needed.

## Prerequisites

**The default reading path needs no account or new model calls.** The [English response originals](../../validation/current/en/responses.json) and [English evaluation originals](../../validation/current/en/native.json) are also in the ZIP. The example below is generated from those records, not from newly authored ideal answers.

| Term to know | Plain-language meaning |
| --- | --- |
| v1 / v2 | Starting instructions / improved instructions; not the service's agent-version numbers |
| Judge / Native evaluation | The grading model / an evaluation run by Foundry's service |
| Completeness / Relevance / Groundedness | Did it address all requested parts / fit the question / stay supported by the supplied material? |
| Dev / Holdout | Practice data used while improving / a separate final exam excluded from improvement |

<details class="optional-path" markdown="1">
<summary>Optional execution prerequisites: collect and evaluate new responses</summary>

Use L01's environment and L02's **`gpt-6-sol` / `2026-09-22`** deployment. Set your actual deployment name in `.env`: the suggested name is `contoso-gpt-6-sol`, while L01's administrator path may use `contoso-chat`. Native evaluation also needs `FOUNDRY_JUDGE_DEPLOYMENT_NAME`; this measurement held the existing `contoso-judge` (GPT-4.1) fixed in both environments. No Hosted-agent redeployment, Search service, Optimizer, or holdout is required. The evaluation created one tool-free Prompt Agent with v1/v2 versions in each Foundry project.
Both prompts receive the same **checked-in synthetic policy context**; it is not described as a live Search retrieval.
The 12 questions use the same scenario IDs, expected behavior, and policy context in both languages. Expected behavior is not included in target-model inputs; it is supplied only to the native judge.
Keep `FOUNDRY_LAB_LANGUAGE=en` selected for the English inputs and instructions.

</details>

## Steps

### 1. Read and judge one question first

These are **actual English questions, answers, and native scores**. Locate **cap / current stock / approver / draft** in each answer. Unlike L06, this comparison has no tools: it must not claim a stock lookup or a created draft.

<!-- instruction-reading-example -->

**Interpretation:** Both answers address all four parts, and all three native scores tie at 5→5. The changed wording does not establish a measured English improvement. Read the expandable judge reasons critically; a maximum score on one exposed question is not proof of general quality.

Write one line each for **observed difference / supporting original text / remaining uncertainty**. Then read the full results below and the other questions in the originals.

### 2. Read what v2 changes

| General v1 guidance | More explicit v2 behavior | Difference to look for |
| --- | --- | --- |
| Do not guess missing information | Refuse restricted parts while still answering independently verifiable public parts | State the public cap's number, currency, and VAT basis |
| Cite actual documents | Match separate evidence to access, missing information, public facts, and next steps | Do not substitute a general introduction for a specific rule |
| Use policies and tools | Distinguish policy caps, quotes, actual prices, verified FX, and draft status | Do not confirm unavailable contract terms or exchange rates |
| Create drafts safely | Require explicit intent, exact quantity, no duplication, and actual results | No placeholder quantity or fabricated approval/order/payment |

V2 contains a reusable answer procedure, not question-specific answers or evaluation case IDs.

### 3. Optional: run a new comparison in your environment

Skip this step when reading existing results. Expand it only after approval of the project, language, request limits, and costs for new collection/evaluation. First select English in your separate lab folder as shown in L01; these commands then work without a shell-specific variable prefix.

<details class="optional-path" markdown="1">
<summary>New paid execution: inspect the plan → collect answers → evaluate those originals</summary>

```bash
python samples/instruction_prompt_agent_lab.py
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `instruction_prompt_agent_lab.py` | Displays v1/v2, 12 fixed questions, target deployment, and the comparison plan. | Plan only; zero Azure response calls. |

</div>

Run the first line below only if the plan matches your approved scope. Wait for a complete collection file before running the second. **Do not run both lines together.**

```bash
python samples/instruction_prompt_agent_lab.py --live --output results/instruction-prompt-agent-en.json
python samples/instruction_evaluation.py --input results/instruction-prompt-agent-en.json --output results/instruction-native-prompt-agent-en.json --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `instruction_prompt_agent_lab.py --live` | Creates one evaluation Agent with v1/v2 in the selected language's approved project, then collects answers under the same context and questions. | At most 24 calls, 600 seconds, zero retries, and 2,048 output tokens per language. If both languages are separately approved, the combined cap is 48 calls/1,200 seconds. Preserve originals, tokens, latency, and supporting checks in `results/`. |
| 2. `instruction_evaluation.py --live` | Submits the 24 collected Prompt Agent originals to Foundry native evaluation. | Zero target reinvocations. One native run per language, 600 seconds plus 90-second cancellation verification. Preserve scores and reasons separately. |

</div>

Run the same commands with the language and input/output paths set to `ko` or `en`. Response collection is bounded to 600 seconds per language (1,200 seconds total); one native run per language is bounded to 600 seconds. The two language comparisons cannot exceed 48 target calls. Never overwrite an existing result. This measurement's completed originals are `results/instruction-prompt-agent-{ko,en}-attempt-3.json`, with native originals at `results/instruction-native-prompt-agent-{ko,en}-attempt-1.json`.

If the result file exists, read it rather than invoking the target again. Do not increment instruction or experiment versions. The first ownership preflight and the subsequent request-shape error each produced zero target responses; those originals remain recorded, followed by one complete collection within the approved bounds. Do not substitute earlier or authored answers. With a Prompt Agent reference, keep reasoning and output schema in its definition rather than duplicate them in the Responses request. Foundry-issued evaluation IDs are retained for traceability.

The `results/` paths above belong to the person who executed the commands. Personal run files are excluded from the kit; read the linked `validation/current/en/` originals for the existing example.

</details>

### 4. Read the score and the underlying answers

The same 40 precommitted checks apply per instruction version, giving the local supporting checklist a score from **0 to 40**.
A check requires both an explicit fact/refusal/confirmation path and a relevant selected policy section.
This is a **mechanical text-and-citation checklist**, not comprehensive semantic evaluation or a business release gate.

<details markdown="1">
<summary>Finding other questions, scores, and hashes in the original JSON</summary>

| Result field | Interpretation |
| --- | --- |
| `comparison.local_checklist.scores.v1`, `.v2` | Actual matched checks in the response JSON under identical criteria |
| `comparison.local_checklist.delta`, `.outcome` | V2-v1 difference and actual `improved`, `unchanged`, or `regressed` result |
| `rows[].raw_answer`, `checklist` | Original answer, check-level judgments, and critical safety-check failures |
| `comparison.usage_latency` | Per-version tokens, mean/total latency, and v2-v1 deltas |
| `instructions_sha256`, `cases_sha256`, `context_sha256` | Exact input fingerprints, not increasing instruction versions |

Search for `compound-request-no-tools` in your editor to find v1/v2 under the response file's `rows`. In the native file, match `comparison.rows` by `case_id` and `instructions`, then read `metrics` for scores/reasons. `raw_answer` is a JSON-encoded string, so `\"` and `\n` are normal. The reading example above displays its decoded `answer` without editing the content.

</details>

**A higher v2 score is not guaranteed.** V1 may already answer every part correctly, and model variation can produce a regression.
Explain that result from the originals. Do not weaken v1 or change the checklist to manufacture improvement.

### 5. Question types and Foundry native evaluation

<details class="provenance-note" markdown="1">
<summary>Reference: why the earlier three questions became twelve</summary>

Before freezing the new suite, inspect the earlier three cases (`public-and-restricted`, `quote-and-policy`, `approval-and-draft`). The preserved [previous report](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/tree/39b2bd1a1c85cb18d3d46d8bf876a6e274d32958/validation) shows 5.0/5 on completeness, relevance, and groundedness for v1 and v2 in both languages. Both instructions answered these three composite cases well enough to reach the ceiling; with only three rows and saturated scores, that exercise could not distinguish the instructions. This does not prove equivalence or justify weakening v1. The new dev set was therefore fixed before measurement as 12 varied boundary, evidence, subquestion, and tool-limit cases; the earlier results were not replaced.

</details>

The fixed questions cover multiple item caps versus total approvals, exact thresholds, public facts versus restricted information, missing policy, uncertain contracts and currency conversion, quotes versus live inventory, tool-input constraints, untrusted approval claims, and compound requests. Both instructions receive the same context and no-tool boundary.

The Foundry native evaluator sees each question's precommitted expected behavior and returns a **1-5 ordinal** score with an English reason. Means use all 12 rows per instruction. This is not the binary `TaskAdherence` score. Native scores and reasons are the primary quality evidence; the mechanical local checklist is supporting evidence only.

![Foundry Evaluations. Separate completion status from individual scores, errors, and missing rows.](../../assets/portal/en/08-evaluations.png)

Explore the run state, evaluator, inputs, row-level judgments, and errors in Evaluations.
The optional collection command records real Azure responses and local checks; the [native comparison runner](../../samples/instruction_evaluation.py) submits those exact responses to Foundry Evaluations. Relevance and groundedness use built-in evaluators; completeness uses one shared custom 1–5 rubric.
This is a development comparison on exposed teaching questions, not an independent holdout or generalization test. No separate judge calibration is performed.
The existing 90% overall and zero-safety/access-failure business gates are not replaced or relaxed by this small learning score.

### 6. Full Korean and English measurements

These are actual results collected during guide production, not your own execution or guaranteed future scores. Read the score table first; expand the run configuration only when you need its reproduction conditions.

<details class="provenance-note" markdown="1">
<summary>Measurement configuration: model, agent versions, duration, and judge</summary>

The precommitted set of 12 composite development questions was invoked once for each instruction in each language using **Foundry Prompt Agents**, not Hosted agents. The Korean `contoso-instruction-eval-ko-20261001` and English `contoso-instruction-eval-en-20261001` each have pinned active v1/version `1` and v2/version `2`. The target was `gpt-6-sol` / `2026-09-22`, reasoning `low`, and a 2,048-token output limit; within each language, context, questions, schema, and criteria were held constant. There were **48 target responses**. Korean and English collection took 88.707 and 77.389 seconds (166.096 seconds total, within the 1,200-second combined limit). The separate judge was `contoso-judge` / GPT-4.1 `2025-04-14`; it was not told which instruction was expected to win. One native run per language submitted 24 rows; both completed with zero errors or missing rows.

</details>

| Language | Instructions | Supporting local checklist / 40 | Native completeness / 5 | Relevance / 5 | Groundedness / 5 |
| --- | --- | ---: | ---: | ---: | ---: |
| Korean | v1 | 33 | 5.0 | 4.9167 | 5.0 |
| Korean | v2 | 33 | 5.0 | 5.0 | 5.0 |
| English | v1 | 29 | 5.0 | 5.0 | 5.0 |
| English | v2 | 28 | 5.0 | 5.0 | 5.0 |

Native scores are 1–5 ordinal judgments. On Korean relevance, one `compound-request-no-tools` row changed from v1 score 4 to v2 score 5, moving the mean from 4.9167 to 5.0 (+0.0833). The judge reason said v1 addressed all four questions, cited policy, and explained the unavailable tools, while still assigning it 4. The other Korean metrics and all three English metrics tied at 5.0. **Only a limited Korean relevance improvement was observed in this small dev sample**; it does not establish a general, reproducible, or statistically significant improvement. `passed=24/24` is a separate binary summary for the threshold of 4 or higher, not the five-point score itself. No separate judge calibration was performed.

<details class="provenance-note" markdown="1">
<summary>Detailed analysis: tokens, latency, checklist differences, Optimizer, and holdout</summary>

| Language | V1 input / output / total tokens | V2 input / output / total tokens | Total-token change | Mean response latency v1 → v2 |
| --- | ---: | ---: | ---: | ---: |
| Korean | 34,242 / 3,437 / 37,679 | 40,218 / 4,837 / 45,055 | +7,376 | 3.473 s → 3.900 s (+0.427 s) |
| English | 31,205 / 2,567 / 33,772 | 35,537 / 3,392 / 38,929 | +5,157 | 2.966 s → 3.462 s (+0.496 s) |

The local checklist is supporting evidence only: Korean tied at 33/40, while English changed from 29/40 to 28/40 (−1). Manually review every changed critical flag against the originals. In both languages, the v2 answer to `untrusted-contract-instruction` explicitly rejects the document as authority; Korean also provides the authorized access route. English v2 states that contract access is unverified and distinguishes the missing policy from restricted information. Its answers on replacement eligibility and draft/order/payment status also satisfy the intended boundaries, though the regex patterns missed some wording. Preserve both originals and flags; do not change checks after measurement or treat them as a calibrated safety evaluation.

Original answers, all three native metric scores, and the judge reasons for every question are available in [Korean responses](../../validation/current/ko/responses.json), [Korean native results](../../validation/current/ko/native.json), [English responses](../../validation/current/en/responses.json), and [English native results](../../validation/current/en/native.json). The summary links each case ID to answer hashes, Prompt Agent versions, metric-level scores/reasons, and v2-minus-v1 deltas. The Korean `compound-request-no-tools` case is the only sub-ceiling native result and the only nonzero mean delta.

**Conclusion:** Under the precommitted comparison, Korean native relevance rose slightly, every other required native metric tied, and manual review of changed critical checklist flags found no safety/access regression. Record this as a limited observed improvement only. The small, exposed dev sample is not statistical significance, generalization, operational approval, or a repeatable guarantee. Report increased token use/latency and the lower English supporting checklist as well.

**Optimizer and holdout:** Optimizer optionally generates candidates from dev data. A holdout is an independent final exam kept out of instruction development and optimization. These exposed development questions are not a holdout; the existing sealed holdout was neither opened nor run. The current Hosted agent for Optimizer uses a GPT-4.1-mini path, unlike the direct GPT-6 Sol comparison. No equivalent model path or new deployment was available, so no live Optimizer job was submitted; the manually written v2 is not an Optimizer candidate. Earlier instructions and measurements remain in [the preserved baseline commit](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/tree/39b2bd1a1c85cb18d3d46d8bf876a6e274d32958/validation).

</details>

## Success criteria

You can compare the actual v1/v2 answers under the same criteria and explain a **difference or tie** using the original text.
Claim a measured improvement only when the actual `delta` is positive. Repeated validation, holdout runs, and Optimizer are not prerequisites.

The [current instruction status](../../validation/current/instructions.json) and [latest Prompt Agent measurement](../../validation/current/report.json) link the bilingual originals, actual model and agent-version identities, per-question answer hashes, scores, reasons, and run IDs. Earlier direct Responses results remain distinct in Git history.

## Troubleshooting

First confirm that model, context, questions, and checks were identical. Distinguish JSON errors, missing citations, and omitted answers.
Do not overwrite an existing comparison. Never replace a model error with an “expected v2 answer.”

## Cleanup

**Reading only creates no Azure resources in this module.** If you collected new responses, record only your own run's resources in L12.

<details class="provenance-note" markdown="1">
<summary>Reference: resources retained while creating the guide</summary>

This measurement created two evaluation-only Prompt Agents with two versions each. It created no Hosted sessions, Optimizer jobs, or model deployments. Both native runs are terminal; retain agents and model deployments unless their cleanup is separately approved.

</details>
