> **What you will build:** An assistant that connects knowledge, tools, quality checks, and tracing, plus a process for deploying the version you validated.

<div class="lab-brief" markdown="1">

**Format:** Review L06's integrated result and design a release · Teams publishing is not required.

**Start here:** Use L06's `Read again` command to read the saved answer, then check the five items below. No new Azure call is needed.

**What to check:** Record citations, function results, the not-ordered state, and configuration bundle. Production approval and publishing remain separate.

</div>

## Objectives

Go beyond “It answered in the demo” to **selecting the version users receive and knowing how to roll back if it fails**.

## Concepts and lab map

**What you will try:** Review L06's purchasing assistant against five required results.

**What is it, and why does it matter?** Completion means correct evidence, calculations, and pending approval—not merely receiving an answer. Choose the version users will call separately from the latest development version.

**How do you use it?** Reread the saved response and compare its policy citations and function results. Record the configuration and recovery plan. Teams publishing is not required.

**Where do you run it?** Read the [capstone's saved result](../../samples/workshop.py) in the terminal. Portal version and publishing settings are optional references. Remote channels do not automatically execute L06's local functions.

## Prerequisites

You need the L05–L10 results. Actual Teams/Microsoft Copilot publishing requires separate publish permissions, permission to create Bot Service resources, and an organizational-policy review. **You can complete the core course through local/Foundry integration without publishing.**

## Steps

### 1. Complete the final user task

**Reuse the L06 result first.** Use that run's `Read again` command or replace `ACTUAL_ID` below with your own response-file path.

```bash
python samples/workshop.py read-result --input results/contoso-lab-ACTUAL_ID-responses.jsonl
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `read-result --input` | Displays saved questions, answers, function results, and citations. | Local reading; zero Azure calls. It does not change records or issue a pass. Compare the five items yourself. |

</div>

If missing, check L06's folder and ownership record first. **Without an L06 Azure integration run, there is no actual integrated result to review.** Do not substitute local function output or L08 evaluation results and claim integration success. Keep the English profile selected.

<details class="optional-path" markdown="1">
<summary>Optional: only if no integrated result exists and a new collection is approved</summary>

```bash
python samples/workshop.py capstone --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `capstone --live` | Creates a new SDK experiment with 3 synthetic policies and 2 functions, then runs the default purchase task. It does not redisplay the L06 result. | Incurs model, retrieval, and storage costs and creates a new receipt/response. If reviewing an existing run is sufficient for the assignment, you do not need to call it again. |

</div>

</details>

Question: “Check the purchasing policy for two laptops and NB-14 inventory, then prepare a purchase request draft.” With `FOUNDRY_LAB_LANGUAGE=en` selected, the executable sample uses an English synthetic request, English instructions, and the policies in `data/en/policies/`.

| Required result | Evidence for judging it |
| --- | --- |
| Per-laptop limit of KRW 1,500,000, including VAT | Actual policy citation |
| NB-14 stock of 8, unit price KRW 1,450,000 | Actual `get_stock` result |
| Total of KRW 2,900,000 | Tool calculation result |
| Team manager and purchasing representative approval required | Policy and `required_approvals` |
| A draft, not an order | `draft_requires_human_approval`, `order_submitted=false` |

The reader's **Function calls / Citations / response_id** come from the original JSONL `tool_calls`, `citations`, and `response_id`. Check these alongside the answer. A definite stock claim without an inventory result is a failure.

### 2. Record the release bundle

Bundle the model deployment/version, agent version, instructions file, tool schema, policy-document version, evaluation-data version, and evaluation results into one record. The SDK agents created by this guide are independent experiments; **do not treat them as production deployments as they stand**.

Link your results into [L22's release-manifest example](../../docs/en/22-delivery.md). L08's tool-free instruction comparison differs from this `capstone` in model/tool/policy conditions; do not transfer its score into integrated-agent release approval. If operational checks are incomplete, record “integration lab complete / release on hold.”

### 3. Select a stable endpoint and active version

Steps 3–5 are **only for the optional publishing/production-transition path**. The default exercise reads the settings and writes a recovery plan.

<details class="optional-path" markdown="1">
<summary>Optional: switch production versions and publish to Teams — separate access and approval required</summary>

Review how to select a specific version under the portal agent's **Details → Agent configuration → Active version**. `Always use latest` can automatically expose new versions to users; do not select it without an actual production policy.

Test a new version, then select the earlier version again and send the same question. The URL can stay the same while behavior and version change.

### 4. Conditional: Publish to Teams/Microsoft Copilot

For an agent that needs actual functions, first move to a **Hosted Agent or tools executable on a server**. The local Python process from L06 does not automatically handle Teams users' requests.

An administrator checks the following.

| Area | What to verify |
| --- | --- |
| Foundry | Project/resource roles required for the actual publishing operation |
| Bot Service | Separate permissions such as `botServices/write` and `channels/write` |
| Organization | App-allow policies, audience, and administrator approval |
| Data | Processing terms for publishing metadata and responses flowing into M365/Teams |
| Network | A separate publishing path for private projects |

In the portal's **Publish → Teams and Microsoft Copilot**, enter the name, description, and version to publish. Test with **Just you** first. **People in your organization** is a separate rollout subject to organizational administrator approval and policy.

Current public documentation describes `Foundry User` project permissions and publishing management permissions differently across pages. Do not assume one role name is sufficient. **Verify both the permissions required for the specific publishing operation and the Bot Service permissions in advance.**

The standard portal publishing flow may not support projects with public network access disabled. Use the separate Activity route and authentication requirements in the official REST path. Do not bypass this by disabling private-network settings.

### 5. Recheck from user and operations perspectives

Compare access for 1 permitted user and 1 unauthorized user. Successful publishing, discoverability, invocation permissions, and successful tool execution are separate checks. Do not stop at a “published successfully” message.

</details>

## Success criteria

Record all five final-result items, the configuration bundle, and the recovery plan. If no previously approved version exists, write “no recovery target / release on hold”; do not invent an approved version. If you did not publish, record **“integration lab complete / publishing not performed.”** This does not establish production readiness.

## Troubleshooting

If the app appears in Teams but does not respond, check the Bot channel, agent-endpoint authentication, active version, and server-side tool execution environment. If the app is not visible, start with its publishing scope and administrator approval.

## Cleanup

Withdraw experimental publications and connections according to administrator policy. Every learner who created resources **must complete L12**.
