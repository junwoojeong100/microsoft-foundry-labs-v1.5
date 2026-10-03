> **What you will build:** Compare local execution and business-data integration options, and select only the extensions your project needs.

## Objectives

**Foundry cloud, Foundry Local, and Foundry Local on Azure Local are not the same deployment approach.** Fabric IQ, Work IQ, and Foundry IQ also provide different knowledge contexts.

## Concepts and lab map

**What you will try:** Comparing on-device inference, Fabric's business semantics layer, and Microsoft 365 knowledge integration.

**What is it, and why does it matter?** Foundry Local is a runtime/SDK for running models on a device; Fabric IQ and Work IQ connect to data and context in their respective business products. Choosing Local to reduce cloud costs means managing device memory and model deployment, while adding business integrations means managing source-data permissions and licenses. Assuming the same environment support just because products share “IQ” or the “Foundry” brand leads to flawed designs.

**How do you use it?** First decide whether you need a short on-device inference, a query for analytical measures, or authorized retrieval of business documents. Execute only one path allowed in your environment, and record the support conditions and selection rationale for the others. This chapter does not ask you to install every additional product.

**Where do you run it?** Local requires a supported device and the official SDK; Fabric/M365 requires an approved test environment in the relevant product. Use this repository's English [synthetic monthly expenses](../../data/en/monthly-spend.csv) and [purchasing policy](../../data/en/policies/procurement-policy.md) as inputs, but do not assume that executors for every separate product are bundled.

## Prerequisites

This module consists of **optional mini-labs**. Perform one that fits your available environment and leave the others as selection/design records. Check additional licenses, administrator consent, model downloads, and hardware requirements beforehand.

**Selection example:** Choose Fabric with the synthetic CSV for “exact monthly equipment totals,” Local for “brief guidance on a disconnected device,” or Work IQ for “authorized M365 document retrieval.” Success in one capability does not establish success in another.

Before starting, record the selected path's **purpose, prepared runtime/resource, input, expected output, unsupported conditions, and shutdown action**. Without resources, use the worked examples to deliver a design, not a claim of execution.

## Steps

### 1. Option A: Foundry Local

In the [Foundry Local quickstart](https://learn.microsoft.com/azure/foundry-local/get-started), choose a **current SDK sample** for your device and language. Proceed in this order: inspect the model list → download a supported model → run a short inference → unload the model.

| What to inspect | How to judge it | Next action on failure |
| --- | --- | --- |
| Official sample's OS/SDK/device memory requirements | Your environment meets the chosen model's requirements | Stop or use another supported device; a cloud model is not Local execution |
| Model ID and completed download state | The selected model is actually available on the device | Separate download failures from inference failures; inspect approved storage/network access |
| Sample's single generation call with the input below | A draft prepares a request; an order requires separate approval/system execution | Check response language, truncation, and model support; do not conflate inference with a business API call |
| State after unload | The running model is unloaded from memory | Inspect process/model state; distinguish unloading from deleting the cache |

```text
Input: "Explain the difference between a purchase request draft and an actual order in one sentence."
```

Distinguish the initial download time from subsequent inference time, and record model/version, memory use, hardware acceleration, and the response. After preparing the model and runtime, check whether the same inference also works in an approved offline test environment.

The core of current Foundry Local is a **runtime/SDK** embedded in an application. An optional server/CLI is also available, but this does not mean “installing the cloud Agent Service locally.” On-device inference does not require an Azure subscription or cloud token charges, but initial model/component downloads, licensing, and optional diagnostics conditions still apply.

### 2. Option B: Fabric IQ

Start with an approved workspace and data agent/semantic model supplied by an administrator. Check support and caller identity in the [Fabric IQ connection documentation](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/fabric-iq). Without that setup, write the specification below rather than creating every Fabric component.

**Contoso specification example — not an actual Fabric result.**

| Step | Input/choice | Result to judge |
| --- | --- | --- |
| Source preparation | English `monthly-spend.csv`, 9 rows excluding the header | `month`, `category`, numeric `amount_krw` |
| Aggregation | Sum `amount_krw` by `month`, with no filters | July 3,718,000 / August 2,677,000 / September 4,759,000 KRW |
| Source-product check | Run that aggregation in Fabric first | Verify overall 11,154,000 and 9 rows before connecting Foundry |
| Connection | Supply the approved item and read identity to a supported Fabric IQ tool | Same item/identity as the source check |
| Question | “Give the monthly equipment expense totals and the overall total.” | Actual tool results and final answer match the source aggregation |

For mismatches, inspect **source types/duplicates → measure and filters → connected item/identity → answer synthesis**. Do not change the prompt when the source aggregation is already wrong. Correct numbers without tool evidence leave the connection unverified.

### 3. Option C: Work IQ / SharePoint

Use only an approved test tenant and **administrator-provided test accounts A/B**. Check delegation, administrator consent, and licensing in the [Work IQ connection documentation](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/work-iq). Do not create accounts or change permissions arbitrarily during the lab.

Prepare an **approved test configuration** allowing A, but not B, to read one synthetic purchasing-policy document. First confirm access/denial directly in SharePoint. Then send the same policy question from separate logins and new conversations. Expect authorized document evidence for A and no restricted content, title, or URL for B. If B answers from separate public facts, verify that their evidence is a different authorized source.

If B sees restricted evidence, inspect source ACLs, delegated identity, and conversation/cache mixing before repeating queries. Two conversations under one account do not test user isolation.

Do not treat Work IQ Preview, remote SharePoint search, the direct SharePoint tool, and a Foundry IQ knowledge source as the same feature. Record the search protocol and where source permissions are enforced.

### 4. Summarize product boundaries on one page

| Need | Option | Conditions beyond the core course |
| --- | --- | --- |
| Inference on an application user's device | Foundry Local | Model size, hardware, and SDK |
| Inference on enterprise on-premises infrastructure | Foundry Local on Azure Local | Separate Preview access, Kubernetes/Arc, and operational infrastructure |
| Knowledge retrieval over organizational documents | Foundry IQ | Search, knowledge sources, and permissions |
| Analytics/business semantics layer | Fabric IQ | Fabric items and semantic context |
| M365 work context | Work IQ | M365 permissions, delegation, and licenses |
| Use from Copilot Studio | Foundry agent/knowledge connection | The connector's support and Preview conditions |

### 5. Optional specialized model and framework exercises

When considering community/Hugging Face models, Fireworks integration, healthcare models, or image/video/audio models, record **licenses, responsibilities, supported deployment options, and evaluation methods rather than focusing on names**. This is not an exercise in directly using healthcare-specific models for clinical judgment or diagnosis.

Teams already using LangGraph/LangChain or Semantic Kernel should first consider integration with Foundry endpoints, Toolbox, tracing, and hosted runtime rather than a complete rewrite. Bringing existing code does not automatically make its state, retry, and security contracts compatible.

## Success criteria

Record one selected path's **input, runtime/identity, expected and actual values, next action on failure, and shutdown state**. If access is unavailable, retain the reason and completed design specification. Mark other paths not executed; Local inference does not count as Fabric/M365 authorization testing.

## Troubleshooting

Foundry project roles alone do not resolve other products' license, permission, region, or hardware requirements. If the required Preview access is missing, do not work around it using information from another tenant.

## Cleanup

Unload local models and decide whether to retain the model cache. Work with each product's owner to remove test connections, revoke permissions, and disconnect external sources.
