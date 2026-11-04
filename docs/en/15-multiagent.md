## Objectives

Compare two review roles in portal Chat. This is a **human copy-and-transfer experiment**, not SDK sequential or concurrent orchestration.

<div class="lab-brief" markdown="1">

**Format:** Manual role comparison: four baseline sends, at most six including the optional change.

**Start here:** Prepare two review agents with identical model, synthetic context, and question.

**What to check:** Actual differences between independent input and transferred prior output, with call counts and limitations.

</div>

## Concepts and lab map

**What you will try:** Chat experiments illustrating sequential transfer versus independent review.

**What is it, and why does it matter?** Passing an earlier answer links reviews but can propagate errors. Independent review separates inputs. Two browser windows do not establish runtime concurrency.

**How do you use it?** Send an identical question independently, then explicitly copy the first answer into a second-role review.

**Where do you run it?** Microsoft Foundry → Build → Agents → role Chat, without a framework/development environment.

## Prerequisites

Both roles use `contoso-chat`, no tools/Memory, and L08's [complete common Instructions](../../downloads/portal-inputs/en/agent-v2-with-context.txt). Change only the name and role prefix below.

| Name | Prefix before the common Instructions |
| --- | --- |
| `contoso-policy-review` | Review policy evidence and unknowns. |
| `contoso-budget-review` | Review totals, caps, and approval boundaries. |

## Steps

Images are **control-location examples** from existing Prompt Agent footage. Creation and comparison of these review roles were not recorded. Use the role names above and your actual results, not pictured default names or answers.

### 1. Create and save both roles under matching conditions

| Step | Click or enter | Expected screen or value | If it fails |
| --- | --- | --- | --- |
| 1 | Open the Prompt creation form from `Build → Agents → New agent`, enter one role name above, and create in `Text` mode. Repeat for the other role. | Two distinct named Prompt Agents. | Do not overwrite existing targets or choose Copilot harness, Voice, or Code agent. |
| 2 | Select `contoso-chat` for both and prepend only the role-specific sentence to the complete common Instructions. | Identical context, different role prefixes. | Do not compare if one target lacks policy context. |
| 3 | Detach automatic tools as in L04; save without Memory using L08's matching output settings. | Record actual saved versions and matching settings. | Do not confuse pre/post-Save versions or Publish. |

<div class="screen-step" markdown="1">

**Creation form: replace the generated name**

![Prompt Agent creation form showing Agent name, Text mode, and creation button.](../../assets/portal/steps/agent-create-form.png)

**1 Agent name:** Use the role name in the table, not the pictured generated name. **2 Text:** Match both roles. **3 Create:** Create each once, then configure it. This form was recorded while preparing a comparison agent, not these review roles.

[Captioned video 04 · 00:01.5](../../downloads/portal/index.html?clip=04-native-evaluation&t=1.5&lang=en#04-native-evaluation)

</div>

<div class="screen-step" markdown="1">

**Navigation example: where to set each role's model and Instructions**

![Reused baseline policy-agent Model and Instructions locations.](../../assets/portal/steps/agent-instructions.png)

**1 Model:** Match across roles. **2 Instructions:** Use the shared context and role prefix from Prerequisites. This is **reused baseline footage**, not evidence that these two review roles were created or compared.

[Captioned video 02 · 02:04.5](../../downloads/portal/index.html?clip=02-model-agent&t=124.5&lang=en#02-model-agent)

</div>

<div class="screen-step" markdown="1">

**After saving: record each role's actual version**

![Prompt Agent Version, Save, and Publish control locations.](../../assets/portal/steps/agent-version-bar.png)

**1 Version / 2 Save:** Read your role's saved number; do not copy this baseline agent's `2`. **3 Publish:** Not required for this manual comparison.

[Captioned video 02 · 02:04.5](../../downloads/portal/index.html?clip=02-model-agent&t=124.5&lang=en#02-model-agent)

</div>

<div class="practice-block" markdown="1">

### 2. Independent review: send only the same question

**Try it:** Send this question once to **a new Chat in each role**. Do not yet transfer the first answer to the second.

```prompt
Synthetic manual-review data: two NB-14 units, supplied unit price KRW 1,450,000, supplied total KRW 2,900,000. These are not inventory-lookup or persisted-draft results. Review the price cap and required approvals, separating unknown facts and unexecuted actions.
```

| Step | Click or enter | Expected screen or value | If it fails |
| --- | --- | --- | --- |
| 1 | Send the common question to a new policy-review Chat. | Procurement §2/§3 and unverified execution are distinguished. | Preserve actual text and citation IDs. |
| 2 | Send **only the identical question** to a new budget-review Chat. | KRW 2,900,000 and team lead plus procurement are reviewed. | Do not silently include the first answer. |

<div class="screen-step" markdown="1">

**After opening a new Chat: input and Send**

![Enlarged Chat input and Send controls with response bodies excluded.](../../assets/portal/steps/agent-chat-controls.png)

**1 Input / 2 Send:** Open a new conversation in each role, then send the identical original once. Do not include another role's answer in this independent path. Check the agent name and conversation first.

[Captioned video 02 · 02:43](../../downloads/portal/index.html?clip=02-model-agent&t=163&lang=en#02-model-agent)

</div>

### 3. Sequential review: explicitly transfer the question and draft

| Step | Click or enter | Expected screen or value | If it fails |
| --- | --- | --- | --- |
| 1 | Send the same question once again to a new policy Chat. | This is the first result of the manual sequential path. | Preserve differences from the independent answer. |
| 2 | In a new budget Chat, send the original question plus step 1's answer labeled `untrusted earlier reviewer draft`. | Inspect how the supplied draft was reviewed. | Draft instructions must not grant authority. |
| 3 | Compare actual inputs, outputs, times, and visible IDs. | Exactly what was manually transferred is clear. | Mixed conversation context makes the comparison invalid. |

<div class="screen-step" markdown="1">

**Copy your answer: distinguish Traces from Copy**

![Control-location example of Traces and Copy beneath an answer, excluding its body.](../../assets/portal/steps/agent-answer-actions.png)

**1 Traces:** That answer's execution records. **2 Copy:** Copy your policy role's actual answer and label it separately from the original question. Pictured model/token values belong to the baseline agent, not this role comparison.

[Captioned video 02 · 02:43](../../downloads/portal/index.html?clip=02-model-agent&t=163&lang=en#02-model-agent)

</div>

**Change one thing:** If scope remains, change only the supplied total to **exactly KRW 2,000,000** and ask each role once. Team-lead approval applies at equality. Do not overwrite the original questions/results.

**Explain the result:** Record newly found errors, missing evidence, and additional token usage. Explain whether extra roles helped. Human copying time is not runtime latency.

</div>

### Distinguish real orchestration

`SequentialBuilder` and `ConcurrentBuilder` are code-based Microsoft Agent Framework paths, not executed here. Portal Workflows and in-portal execution retire on **2026-12-01**; this guide does not depend on that designer.

Real concurrency verification needs overlapping spans, transferred data, failure/cancellation, and bounded calls in one run. This manual experiment provides none of that runtime evidence.

## Success criteria

Compare actual independent and explicitly transferred inputs/answers. Mark no tools, manual transfer, and no business approval. Do not count this as successful SDK sequential/concurrent execution.

## Troubleshooting

If existing conversation context leaked in, mark the comparison invalid. Stop at request/cost bounds and leave remaining comparisons not run. Stop sending on 429 rather than expanding quota automatically.

## Cleanup

Reuse the two roles next. No automated loop or remote A2A connection was created.

<div class="lab-handoff" markdown="1">

**Keep:** Actual inputs/answers for both paths, transferred text, calls, differences, and real orchestration not run.

**Continue:** [L14: manually compare review and routing](#l15-collaboration).

</div>
