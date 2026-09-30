> **What you will build:** An assistant that connects knowledge, tools, quality checks, and tracing, plus a process for deploying the version you validated.

## Objectives

Go beyond “It answered in the demo” to **selecting the version users receive and knowing how to roll back if it fails**.

## Concepts and lab map

**What you will try:** Integrating knowledge, functions, and evaluation results, and distinguishing agent versions from publishing channels.

**What is it, and why does it matter?** The latest development version may differ from the active version users call. A change to the model, knowledge, or tools can change the answer to the same question, so a release is a validated configuration bundle—not just one code file. An app appearing in Teams also does not guarantee invocation permissions or successful server-side tool execution.

**How do you use it?** Complete the same purchasing task end to end, then verify five facts in the final response against citations and function JSON. Record the validated version and decide how to return to a previously approved version. Publishing to Teams/Microsoft Copilot is a separate optional step requiring organizational approval.

**Where do you run it?** The [capstone code](../../samples/workshop.py) connects local functions with an Azure agent. Use the portal to inspect version and publishing settings. A remote channel cannot automatically run local functions, so actual publishing requires server-side tools or a Hosted runtime.

## Prerequisites

You need the L05–L10 results. Actual Teams/Microsoft Copilot publishing requires separate publish permissions, permission to create Bot Service resources, and an organizational-policy review. **You can complete the core course through local/Foundry integration without publishing.**

## Steps

### 1. Complete the final user task

```bash
python samples/workshop.py capstone --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `capstone --live` | Creates a new SDK experiment with 3 synthetic policies and 2 functions, then runs the default purchase task. It does not redisplay the L06 result. | Incurs model, retrieval, and storage costs and creates a new receipt/response. If reviewing an existing run is sufficient for the assignment, you do not need to call it again. |

</div>

Question: “Check the purchasing policy for two laptops and NB-14 inventory, then prepare a purchase request draft.” The executable sample keeps its original Korean synthetic question unchanged.

| Required result | Evidence for judging it |
| --- | --- |
| Per-laptop limit of KRW 1,500,000, including VAT | Actual policy citation |
| NB-14 stock of 8, unit price KRW 1,450,000 | Actual `get_stock` result |
| Total of KRW 2,900,000 | Tool calculation result |
| Team manager and purchasing representative approval required | Policy and `required_approvals` |
| A draft, not an order | `draft_requires_human_approval`, `order_submitted=false` |

Inspect JSONL `tool_calls`, `citations`, and `response_id`, not just the natural-language answer. A definite stock claim without an inventory result is a failure.

### 2. Record the release bundle

Bundle the model deployment/version, agent version, instructions file, tool schema, policy-document version, evaluation-data version, and evaluation results into one record. The SDK agents created by this guide are independent experiments; **do not treat them as production deployments as they stand**.

### 3. Select a stable endpoint and active version

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

## Success criteria

You have verified all five final-result items and have a release record and a rollback target version. If you did not publish, record “Ready to publish / actual publishing not performed” as separate states.

## Troubleshooting

If the app appears in Teams but does not respond, check the Bot channel, agent-endpoint authentication, active version, and server-side tool execution environment. If the app is not visible, start with its publishing scope and administrator approval.

## Cleanup

Withdraw experimental publications and connections according to administrator policy. Every learner who created resources **must complete L12**.
