## Objectives

Combine actual evaluation, agent version, and sharing scope in a release decision. The default path **does not publish, switch Active version, or deploy channels**.

<div class="lab-brief" markdown="1">

**Format:** Read-only release inspection and failed-gate exercise. No CI execution, SDK deployment, or Hosted prerequisite installation.

**Start here:** Find L08's actual run and evaluated agent version.

**What to check:** Matching candidate/evaluated versions, gates, safety, retention, recovery evidence, and hold reasons.

</div>

## Concepts and lab map

**What you will try:** Evaluation, Versions, sharing/publishing boundaries.

**What is it, and why does it matter?** One good Chat answer is not a release gate. Results cannot automatically apply to a different candidate version.

**How do you use it?** Gather results, target, access, and recovery plans and decide hold/separate approval required.

**Where do you run it?** Evaluations in the Foundry portal and Agent Details/Versions/publishing information, without publishing.

## Prerequisites

Use actual fixed twelve-question v1/v2 results from L08. Tool-free Prompt Agent comparison does not require L12 Hosted deployment. Existing SDK collections are separate historical evidence, not a new SDK validation run.

## Steps

### 1. Inspect the existing run's target, denominator, and rows

Do not create or resubmit an evaluation. Below is the actual `contoso-compare-v2` run. Its name's `v2` is the instruction variant, distinct from saved numeric version `2`.

<div class="practice-block" markdown="1">

**Try it:** Inspect the portal and enter actual values or `unverified` in the checklist.

| Step | Click or enter | Expected screen or value | If it fails |
| --- | --- | --- | --- |
| 1 | Open `Evaluations → actual L08 run`. | Twelve dataset rows, target agent/version/model, state. | Never exclude Partial/Failed, missing/duplicate/error rows to inflate success. |
| 2 | Read every row's checklist and safety/access outcomes. | Quality ≥90% and zero safety/access failures remain unchanged. | Do not lower gates or edit requirements/questions after results. |

<div class="screen-step" markdown="1">

**Run details: read the actual evaluated target**

![Actual v2 run's Agent ID contoso-compare-v2:2 and Download results.](../../assets/portal/steps/eval-run-target.png)

**1 Agent ID:** Match the final number in `contoso-compare-v2:2` to the candidate. **2 Download results:** Read originals including missing/errors/nulls. Do not select Make recurring or Delete.

[Captioned video 04 · 04:06](../../downloads/portal/index.html?clip=04-native-evaluation&t=246&lang=en#04-native-evaluation)

</div>

<div class="screen-step" markdown="1">

**Actual hold example: 100% still has denominator 11/11**

![Actual v2 Completed result with Relevance 100 percent and 11/11.](../../assets/portal/steps/eval-v2-result.png)

**1 Completed / 2 Relevance:** Neither status nor percentage alone passes the gate. **3 Download results:** Include the missing judgment's error and nulls. This comparison is incomplete; publishing, activation, and rollback were not run.

[Captioned video 04 · 04:06](../../downloads/portal/index.html?clip=04-native-evaluation&t=246&lang=en#04-native-evaluation)

</div>

<div class="screen-step" markdown="1">

**Detailed rows: one page is not the whole dataset**

![Actual Detailed metrics result last page showing Index 10 and 11 and query.](../../assets/portal/steps/eval-detail-rows.png)

**1 Index / 2 query:** Zero-based `10` and `11` are the final two rows, not a two-question dataset. Reconcile all twelve rows and evaluator errors against exported originals. Error details are not visible in this image.

[Captioned video 04 · 04:15](../../downloads/portal/index.html?clip=04-native-evaluation&t=255&lang=en#04-native-evaluation)

</div>

### 2. Read that candidate's saved configuration and publishing boundary

| Step | Click or enter | Expected screen or value | If it fails |
| --- | --- | --- | --- |
| 1 | Open candidate `Build → Agents → Versions/Details`. | Model, Instructions, tools, version match evaluation. | Mismatch requires reevaluation/hold. |
| 2 | If exposed, **read only** `Publish version`, `Active version`, and audience information. | Publishing and active-target switching are distinct. | No button submission, audience, or permission creation. |
| 3 | Record sharing such as `Just you`. | Chat success is not Teams/business-channel deployment. | Add no channel permissions/consent. |

<div class="screen-step" markdown="1">

**Candidate configuration: the same v2 agent's actual settings**

![Actual contoso-compare-v2 showing Version 2, contoso-chat, and empty Tools.](../../assets/portal/steps/eval-v2-candidate.png)

**1 Version / 2 Model / 3 Tools:** Match the exact candidate to the run above. Reconcile partially visible Instructions with the complete original. Do not select Publish. Active version and sharing audience are absent in this scene and remain unverified.

[Captioned video 04 · 00:53](../../downloads/portal/index.html?clip=04-native-evaluation&t=53&lang=en#04-native-evaluation)

</div>

<div class="screen-step" markdown="1">

**List reconciliation: v1 and v2 both have numeric version 2**

![Actual comparison agents v1 and v2 with Version 2 and Prompt Type.](../../assets/portal/steps/agents-type-list.png)

**1 Version / 2 Type:** Do not confuse the two differently named candidates. **3 New agent:** This chapter reads existing targets only; create nothing. Running does not establish publishing or business-channel deployment.

[Captioned video 05 · 02:23](../../downloads/portal/index.html?clip=05-inspection-retention&t=143&lang=en#05-inspection-retention)

</div>

### 3. Gather evidence and decide hold

| Step | Click or enter | Expected screen or value | If it fails |
| --- | --- | --- | --- |
| 1 | Connect L10 traces, L17 boundaries, and L19 cost/retention. | Only actually available evidence is included. | Do not mark untested CRUD, ACL, HITL, or ordering complete. |
| 2 | Apply the hypothetical failure condition below. | Unmet gates hold release. | Average quality cannot offset a safety failure. |

| Check | Required evidence | Current result |
| --- | --- | --- |
| Pinned target | Exact evaluated/candidate version, model, tools | Actual value/unverified |
| Quality/safety | Quality ≥90%, zero safety/access failures, preserved missing/errors | Actual value/unverified |
| Evaluation limits | Fixed twelve questions, **no holdout**, behavioral requirements/manual review | Learning comparison, not production release evidence |
| Execution | Separate evidence for tools, citations, persisted draft, human approval | Actual operations only |
| Costs/resources | Dedicated scope, request limits, retained resources, retention owner | Actual value/unverified |
| Recovery | Actual prior version, restore target, RTO/RPO, owner | Distinguish plan from performed restore test |

**Change one thing:** Apply the **hypothetical decision condition** “one safety/access failure.” Do not edit actual runs. Even 100% average quality does not permit publication.

**Explain the result:** Saving `Publish version`, switching `Active version`, and the caller's actually used version differ. Reading versions does not validate deployment, rollback, or RTO/RPO.

</div>

### Delivery outside this path

GitHub Actions, OIDC, and CI/CD are references. No workflow execution, role grants, merges, or publishing here. Preserve existing `repository_id`, `acknowledge_cost`, ownership receipts, and request bounds.

The reviewed [local validation workflow](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/blob/8fb85c0eb837ceac30a634d9017ef3e3bcca081e/.github/workflows/validate.yml) and [Microsoft Azure validation workflow](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/blob/8fb85c0eb837ceac30a634d9017ef3e3bcca081e/.github/workflows/azure-validation.yml) are **read-only references**. Reading them is not execution or deployment evidence.

Teams/Microsoft 365 channels can require separate permissions/consent, `botServices/write`, `channels/write`, and actual path verification. Chat success does not establish those deployments.

## Success criteria

Verify target/candidate versions and hold on unknowns, mismatches, or safety failures. Fixed questions/manual review are not production or historical SDK gates.

## Troubleshooting

Without exposed version identity, target pinning is unverified. Without an actual run, produce no release score. Never copy old passes or lower gates.

## Cleanup

Finish read-only. Publishing, activation, rollback, and recovery tests need separate scope/permission/cost approval. No GitHub release, Pages publication, or main merge is included.

<div class="lab-handoff" markdown="1">

**Keep:** Actual version/run links, gates/unknowns/recovery plan, and publishing/activation/rollback not run.

**Continue:** [L19: costs, retention, and approved cleanup](#l12).

</div>
