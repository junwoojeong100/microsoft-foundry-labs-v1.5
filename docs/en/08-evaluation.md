> **What you will build:** An educational initial v1 → evaluate → analyze and improve → reevaluate v2 learning loop, grounded in actual answers and evaluation reasons.

## Objectives

**Explain how instruction changes affect the actual answer and evaluation.** A learning guide does not need an ever-growing sequence of release experiments.
V1 is a newly designed, simple educational starting instruction, held fixed within this one comparison; v2 adds an answer procedure. Further instruction edits stay in v2.

## Concepts and lab map

**What you will try:** Controlled inputs, a fixed checklist, source evidence, and interpretation of Foundry evaluation results.

**What is it, and why does it matter?** Scores must follow the actual answer, not the label “v2.”
Keep the model, policies, questions, output format, and checks identical; change only the instructions.

**How do you use it?** Ask the same 12 fixed composite questions once per version, inspect the original answers and individual checks, and calculate the difference.
Retain ties and regressions. Do not prewrite a winning result or keep sampling until a score increases.

**Where do you run it?** Use the [Prompt Agent comparison runner](../../samples/instruction_prompt_agent_lab.py), [fixed questions/checklist](../../data/en/evaluation/instruction-comparison.json),
[v1](../../data/en/prompts/agent-v1.txt), and [v2](../../data/en/prompts/agent-v2.txt).
In the portal's Evaluations area, distinguish service completion from scores, errors, and missing rows.

## Prerequisites

Use L01's environment and L02's **`gpt-6-sol` / `2026-09-22`** deployment. Set its actual deployment name, `contoso-gpt-6-sol`, in `.env`. Native evaluation also needs `FOUNDRY_JUDGE_DEPLOYMENT_NAME`; this measurement held the existing `contoso-judge` (GPT-4.1) fixed in both environments. No Hosted-agent redeployment, Search service, Optimizer, or holdout is required. The evaluation created one tool-free Prompt Agent with v1/v2 versions in each Foundry project.
Both prompts receive the same **checked-in synthetic policy context**; it is not described as a live Search retrieval.
The 12 questions use the same scenario IDs, expected behavior, and policy context in both languages. Expected behavior is not included in target-model inputs; it is supplied only to the native judge.
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
FOUNDRY_LAB_LANGUAGE=en python samples/instruction_prompt_agent_lab.py
FOUNDRY_LAB_LANGUAGE=en python samples/instruction_prompt_agent_lab.py --live --output results/instruction-prompt-agent-en.json
FOUNDRY_LAB_LANGUAGE=en python samples/instruction_evaluation.py --input results/instruction-prompt-agent-en.json --output results/instruction-native-prompt-agent-en.json --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `instruction_prompt_agent_lab.py` | Displays v1/v2, 12 fixed questions, target deployment, and the comparison plan. | Plan only; zero Azure response calls. |
| 2. `instruction_prompt_agent_lab.py --live` | In the approved existing project, invoke each pinned Prompt Agent version once per question with identical context and inputs. Create one Prompt Agent with v1/v2 in each language project. | At most 24 calls per language, 600 seconds, zero retries and 2,048 output tokens. Both languages together: at most 48 calls and 1,200 seconds. Agent definitions hold reasoning and JSON schema; do not resend them as request overrides when `agent_reference` is specified. Preserve originals, token/latency usage, and local checks in `results/`. |
| 3. `instruction_evaluation.py --live` | Submit those 24 originals to Foundry native completeness, relevance, and groundedness evaluation. The anonymous judge receives precommitted expected behavior, not the v1/v2 labels. | Zero target reinvocations. One 24-row native run per language, 600 seconds and 90-second cancellation verification; preserve scores and reasons separately. |

</div>

Run the same commands with the language and input/output paths set to `ko` or `en`. Response collection is bounded to 600 seconds per language (1,200 seconds total); one native run per language is bounded to 600 seconds. The two language comparisons cannot exceed 48 target calls. Never overwrite an existing result. This measurement's completed originals are `results/instruction-prompt-agent-{ko,en}-attempt-3.json`, with native originals at `results/instruction-native-prompt-agent-{ko,en}-attempt-1.json`.

If the result file exists, read it rather than invoking the target again. Do not increment instruction or experiment versions. The first ownership preflight and the subsequent request-shape error each produced zero target responses; those originals remain recorded, followed by one complete collection within the approved bounds. Do not substitute earlier or authored answers. With a Prompt Agent reference, keep reasoning and output schema in its definition rather than duplicate them in the Responses request. Foundry-issued evaluation IDs are retained for traceability.

### 3. Read the score and the underlying answers

The same 40 precommitted checks apply per instruction version, giving the local supporting checklist a score from **0 to 40**.
A check requires both an explicit fact/refusal/confirmation path and a relevant selected policy section.
This is a **mechanical text-and-citation checklist**, not comprehensive semantic evaluation or a business release gate.

| Result field | Interpretation |
| --- | --- |
| `local_checklist.scores.v1`, `.v2` | Actual matched checks under identical criteria |
| `local_checklist.delta`, `.outcome` | V2-v1 difference and actual `improved`, `unchanged`, or `regressed` result |
| `rows[].raw_answer`, `checklist` | Original answer, check-level judgments, and critical safety-check failures |
| `usage_latency` | Per-version tokens, mean/total latency, and v2-v1 deltas |
| `instructions_sha256`, `cases_sha256`, `context_sha256` | Exact input fingerprints, not increasing instruction versions |

**A higher v2 score is not guaranteed.** V1 may already answer every part correctly, and model variation can produce a regression.
Explain that result from the originals. Do not weaken v1 or change the checklist to manufacture improvement.

### 4. Question types and Foundry native evaluation

Before freezing the new suite, inspect the earlier three cases (`public-and-restricted`, `quote-and-policy`, `approval-and-draft`). The preserved [previous report](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/tree/39b2bd1a1c85cb18d3d46d8bf876a6e274d32958/validation) shows 5.0/5 on completeness, relevance, and groundedness for v1 and v2 in both languages. Both instructions answered these three composite cases well enough to reach the ceiling; with only three rows and saturated scores, that exercise could not distinguish the instructions. This does not prove equivalence or justify weakening v1. The new dev set was therefore fixed before measurement as 12 varied boundary, evidence, subquestion, and tool-limit cases; the earlier results were not replaced.

The fixed questions cover multiple item caps versus total approvals, exact thresholds, public facts versus restricted information, missing policy, uncertain contracts and currency conversion, quotes versus live inventory, tool-input constraints, untrusted approval claims, and compound requests. Both instructions receive the same context and no-tool boundary.

The Foundry native evaluator sees each question's precommitted expected behavior and returns a **1-5 ordinal** score with an English reason. Means use all 12 rows per instruction. This is not the binary `TaskAdherence` score. Native scores and reasons are the primary quality evidence; the mechanical local checklist is supporting evidence only.

![Foundry Evaluations. Separate completion status from individual scores, errors, and missing rows.](../../assets/portal/en/08-evaluations.png)

Explore the run state, evaluator, inputs, row-level judgments, and errors in Evaluations.
The first two commands collect real Azure model responses and calculate local checks. The third [native comparison runner](../../samples/instruction_evaluation.py) submits those exact responses to Foundry Evaluations. Relevance and groundedness use built-in evaluators; completeness uses one shared custom 1–5 rubric.
This is a development comparison on exposed teaching questions, not an independent holdout or generalization test. No separate judge calibration is performed.
The existing 90% overall and zero-safety/access-failure business gates are not replaced or relaxed by this small learning score.

### 5. Actual Korean and English measurements

The precommitted set of 12 composite development questions was invoked once for each instruction in each language using **Foundry Prompt Agents**, not Hosted agents. The Korean `contoso-instruction-eval-ko-20261001` and English `contoso-instruction-eval-en-20261001` each have pinned active v1/version `1` and v2/version `2`. The target was `gpt-6-sol` / `2026-09-22`, reasoning `low`, and a 2,048-token output limit; within each language, context, questions, schema, and criteria were held constant. There were **48 target responses**. Korean and English collection took 88.707 and 77.389 seconds (166.096 seconds total, within the 1,200-second combined limit). The separate judge was `contoso-judge` / GPT-4.1 `2025-04-14`; it was not told which instruction was expected to win. One native run per language submitted 24 rows; both completed with zero errors or missing rows.

| Language | Instructions | Supporting local checklist / 40 | Native completeness / 5 | Relevance / 5 | Groundedness / 5 |
| --- | --- | ---: | ---: | ---: | ---: |
| Korean | v1 | 33 | 5.0 | 4.9167 | 5.0 |
| Korean | v2 | 33 | 5.0 | 5.0 | 5.0 |
| English | v1 | 29 | 5.0 | 5.0 | 5.0 |
| English | v2 | 28 | 5.0 | 5.0 | 5.0 |

Native scores are 1–5 ordinal judgments. On Korean relevance, one `compound-request-no-tools` row changed from v1 score 4 to v2 score 5, moving the mean from 4.9167 to 5.0 (+0.0833). The judge reason said v1 addressed all four questions, cited policy, and explained the unavailable tools, while still assigning it 4. The other Korean metrics and all three English metrics tied at 5.0. **Only a limited Korean relevance improvement was observed in this small dev sample**; it does not establish a general, reproducible, or statistically significant improvement. `passed=24/24` is a separate binary summary for the threshold of 4 or higher, not the five-point score itself. No separate judge calibration was performed.

| Language | V1 input / output / total tokens | V2 input / output / total tokens | Total-token change | Mean response latency v1 → v2 |
| --- | ---: | ---: | ---: | ---: |
| Korean | 34,242 / 3,437 / 37,679 | 40,218 / 4,837 / 45,055 | +7,376 | 3.473 s → 3.900 s (+0.427 s) |
| English | 31,205 / 2,567 / 33,772 | 35,537 / 3,392 / 38,929 | +5,157 | 2.966 s → 3.462 s (+0.496 s) |

The local checklist is supporting evidence only: Korean tied at 33/40, while English changed from 29/40 to 28/40 (−1). Manually review every changed critical flag against the originals. In both languages, the v2 answer to `untrusted-contract-instruction` explicitly rejects the document as authority; Korean also provides the authorized access route. English v2 states that contract access is unverified and distinguishes the missing policy from restricted information. Its answers on replacement eligibility and draft/order/payment status also satisfy the intended boundaries, though the regex patterns missed some wording. Preserve both originals and flags; do not change checks after measurement or treat them as a calibrated safety evaluation.

Original answers, all three native metric scores, and the judge reasons for every question are available in [Korean responses](../../validation/current/ko/responses.json), [Korean native results](../../validation/current/ko/native.json), [English responses](../../validation/current/en/responses.json), and [English native results](../../validation/current/en/native.json). The summary links each case ID to answer hashes, Prompt Agent versions, metric-level scores/reasons, and v2-minus-v1 deltas. The Korean `compound-request-no-tools` case is the only sub-ceiling native result and the only nonzero mean delta.

**Conclusion:** Under the precommitted comparison, Korean native relevance rose slightly, every other required native metric tied, and manual review of changed critical checklist flags found no safety/access regression. Record this as a limited observed improvement only. The small, exposed dev sample is not statistical significance, generalization, operational approval, or a repeatable guarantee. Report increased token use/latency and the lower English supporting checklist as well.

**Optimizer and holdout:** Optimizer optionally generates candidates from dev data. A holdout is an independent final exam kept out of instruction development and optimization. These exposed development questions are not a holdout; the existing sealed holdout was neither opened nor run. The current Hosted agent for Optimizer uses a GPT-4.1-mini path, unlike the direct GPT-6 Sol comparison. No equivalent model path or new deployment was available, so no live Optimizer job was submitted; the manually written v2 is not an Optimizer candidate. Earlier instructions and measurements remain in [the preserved baseline commit](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/tree/39b2bd1a1c85cb18d3d46d8bf876a6e274d32958/validation).

## Success criteria

You can compare the actual v1/v2 answers under the same checklist and explain which instruction addresses which omission.
Claim a measured improvement only when the actual `delta` is positive. Repeated validation, holdout runs, and Optimizer are not prerequisites.

The [current instruction status](../../validation/current/instructions.json) and [latest Prompt Agent measurement](../../validation/current/report.json) link the bilingual originals, actual model and agent-version identities, per-question answer hashes, scores, reasons, and run IDs. Earlier direct Responses results remain distinct in Git history.

## Troubleshooting

First confirm that model, context, questions, and checks were identical. Distinguish JSON errors, missing citations, and omitted answers.
Do not overwrite an existing comparison. Never replace a model error with an “expected v2 answer.”

## Cleanup

This measurement created two evaluation-only Prompt Agents with two versions each. It created no Hosted sessions, Optimizer jobs, or model deployments. Both native runs are terminal; retain agents and model deployments unless their cleanup is separately approved.
