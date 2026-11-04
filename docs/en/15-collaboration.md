## Objectives

Manually compare writer → reviewer → revision with role routing in portal Chat. Do not report automated handoff, A2A, or human-approval workflow execution.

<div class="lab-brief" markdown="1">

**Format:** Manual Chat experiment: five baseline sends, at most seven with the optional change.

**Start here:** Reuse L13's two roles and identical synthetic context.

**What to check:** Three draft/review/revision originals and two classification/manual-transfer originals.

</div>

## Concepts and lab map

**What you will try:** Repeated review versus selecting a next role.

**What is it, and why does it matter?** Group chat supports review and revision; handoff changes who acts next. A sentence claiming delegation is not actual control transfer.

**How do you use it?** Copy and transfer answers manually, recording that fact and a bounded stopping condition.

**Where do you run it?** Microsoft Foundry role Chat and private comparison notes, without automatic orchestration.

## Prerequisites

Reuse `contoso-policy-review` and `contoso-budget-review`. Create `contoso-router` using L04 with the same model and no tools. Save Instructions: “Classify input as policy or budget and explain why. Do not claim actual delegation, approval, or ordering.”

## Steps

These are **control-location examples** from existing Prompt Agent footage, not recorded router, review-loop, or handoff execution. Inspect creation, input, and copy controls rather than another exercise's answer bodies.

### 1. Prepare a classification-only router

| Step | Click or enter | Expected screen or value | If it fails |
| --- | --- | --- | --- |
| 1 | Create a Prompt Agent as in L04 with Name `contoso-router` and `Text` mode. | A separate target from L13's two review roles. | Do not overwrite an existing role. |
| 2 | Use the same `contoso-chat`; save the classification-only Instructions from Prerequisites without tools/Memory. | Only policy/budget classification and reason are requested. | Do not instruct actual execution or invented approval. |

<div class="screen-step" markdown="1">

**Router name: separate it from review roles**

![Prompt creation form showing name, Text mode, and creation control locations.](../../assets/portal/steps/agent-create-form.png)

**1 Name:** Enter `contoso-router`, not the pictured generated name. **2 Text / 3 Create:** Create the Prompt target, then save its classification Instructions. Creation alone does not implement routing or handoff.

[Captioned video 04 · 00:01.5](../../downloads/portal/index.html?clip=04-native-evaluation&t=1.5&lang=en#04-native-evaluation)

</div>

<div class="screen-step" markdown="1">

**Instructions: save only the router's intended task**

![Baseline Prompt Agent Model and Instructions editing locations.](../../assets/portal/steps/agent-instructions.png)

**1 Model:** The same `contoso-chat` as L13. **2 Instructions:** Save Prerequisites' classification-only sentence. The pictured policy Instructions are not the router's actual saved content.

[Captioned video 02 · 02:04.5](../../downloads/portal/index.html?clip=02-model-agent&t=124.5&lang=en#02-model-agent)

</div>

<div class="practice-block" markdown="1">

### 2. Write, review, revise: stop after three sends

**Try it:** Keep this original request fixed and perform the five sends below.

```prompt
Synthetic review data: two NB-14 units, supplied total KRW 2,900,000. Briefly review policy caps, approvers, and unverified inventory/execution. Do not place an actual order.
```

| Step | Click or enter | Expected screen or value | If it fails |
| --- | --- | --- | --- |
| 1 | Send the original request once in a new policy-role Chat. | An initial draft appears. | Do not edit the answer before review. |
| 2 | Send original request plus draft to a new budget-role Chat, asking only for errors and missing evidence. | A review original appears. | Preserve any treatment of draft instructions as authority as a failure. |
| 3 | Paste the review into the writer's conversation and request one final revision. | You can compare which review points were incorporated. | Stop after three sends; no additional loop. |

<div class="screen-step" markdown="1">

**Copy drafts and reviews without rewriting the originals**

![Enlarged Traces and Copy controls beneath an answer.](../../assets/portal/steps/agent-answer-actions.png)

**1 Traces / 2 Copy:** Copy your draft to the reviewer and your review back to the writer. Request revision in the **original writer's same conversation**. The reviewer uses a new conversation; nothing transfers automatically.

[Captioned video 02 · 02:43](../../downloads/portal/index.html?clip=02-model-agent&t=163&lang=en#02-model-agent)

</div>

### 3. Classify, then manually select a role: stop after two sends

| Step | Click or enter | Expected screen or value | If it fails |
| --- | --- | --- | --- |
| 1 | Send the original request once to a new router Chat. | Only policy/budget classification and reason. | Claims of completed specialist execution lack tool evidence. |
| 2 | **Manually** open the selected role and send original request plus routing reason in a new Chat. | The selected role responds after human transfer. | Do not call this automatic handoff. |

<div class="screen-step" markdown="1">

**Type into the selected role: prior context is not inherited**

![Control-location example showing only the Chat input and Send button.](../../assets/portal/steps/agent-chat-controls.png)

**1 Input / 2 Send:** In the selected role's new conversation, label the original request separately from the router's reason. Do not send classification alone or assume earlier context transferred. This is not a recorded handoff result.

[Captioned video 02 · 02:43](../../downloads/portal/index.html?clip=02-model-agent&t=163&lang=en#02-model-agent)

</div>

**Change one thing:** If scope remains, ask the router about the regular laptop replacement interval and manually transfer once to the chosen role. Add only two sends.

**Explain the result:** Record original errors, review findings, actual revision, and routing reasons. A role emitting `approved` is not a real approval record.

</div>

### What automatic execution evidence is missing?

| Manual artifact | Additional evidence needed for actual execution |
| --- | --- |
| Copied writer/reviewer messages | One run's `GroupChatBuilder` routing and termination |
| Router classification text | `HandoffBuilder` control/tool call and next agent response |
| “Human review required” text | Authorized approver, event, wait/resume state in a HITL system |
| Two role names | Authenticated remote A2A endpoints and actual call results |

These code-first features are references only. No handoff tool, remote A2A server, or SDK execution exists in this path. Portal Workflows retire on 2026-12-01; do not use that designer as a workaround.

## Success criteria

Explain five actual messages and their manual transfer path. Explicitly mark automatic group chat, handoff, A2A, and business approval not run. Preserve missing or incorrectly routed results.

## Troubleshooting

Inspect Instructions and new-conversation state. Record nonclassification router actions as failures. Do not raise output/call bounds or repeat until success.

## Cleanup

No recursion, infinite conversation, or persistent execution was created. Keep drafts and final answers separately; include agents in L19's inventory.

<div class="lab-handoff" markdown="1">

**Keep:** Three draft/review/revision originals, two classification/manual-transfer originals, and automatic handoff not run.

**Continue:** [L15: inspect Memory and conditionally compare conversations](#l16).

</div>
