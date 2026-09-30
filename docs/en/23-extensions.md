> **What you will build:** Compare local execution and business-data integration options, and select only the extensions your project needs.

## Objectives

**Foundry cloud, Foundry Local, and Foundry Local on Azure Local are not the same deployment approach.** Fabric IQ, Work IQ, and Foundry IQ also provide different knowledge contexts.

## Concepts and lab map

**What you will try:** Comparing on-device inference, Fabric's business semantics layer, and Microsoft 365 knowledge integration.

**What is it, and why does it matter?** Foundry Local is a runtime/SDK for running models on a device; Fabric IQ and Work IQ connect to data and context in their respective business products. Choosing Local to reduce cloud costs means managing device memory and model deployment, while adding business integrations means managing source-data permissions and licenses. Assuming the same environment support just because products share “IQ” or the “Foundry” brand leads to flawed designs.

**How do you use it?** First decide whether you need a short on-device inference, a query for analytical measures, or authorized retrieval of business documents. Execute only one path allowed in your environment, and record the support conditions and selection rationale for the others. This chapter does not ask you to install every additional product.

**Where do you run it?** Local requires a supported device and the official SDK; Fabric/M365 requires an approved test environment in the relevant product. Use this repository's [synthetic monthly expenses](../../data/monthly-spend.csv) and [purchasing policy](../../data/policies/procurement-policy.md) as inputs, but do not assume that executors for every separate product are bundled.

## Prerequisites

This module consists of **optional mini-labs**. Perform one that fits your available environment and leave the others as selection/design records. Check additional licenses, administrator consent, model downloads, and hardware requirements beforehand.

## Steps

### 1. Option A: Foundry Local

In the [Foundry Local quickstart](https://learn.microsoft.com/azure/foundry-local/get-started), choose a **current SDK sample** for your device and language. Proceed in this order: inspect the model list → download a supported model → run a short inference → unload the model.

```text
Input: "Explain the difference between a purchase request draft and an actual order in one sentence."
```

Distinguish the initial download time from subsequent inference time, and record model/version, memory use, hardware acceleration, and the response. After preparing the model and runtime, check whether the same inference also works in an approved offline test environment.

The core of current Foundry Local is a **runtime/SDK** embedded in an application. An optional server/CLI is also available, but this does not mean “installing the cloud Agent Service locally.” On-device inference does not require an Azure subscription or cloud token charges, but initial model/component downloads, licensing, and optional diagnostics conditions still apply.

### 2. Option B: Fabric IQ

Using **synthetic data** in an approved Fabric workspace, prepare a supported semantic model, data agent, or ontology. Follow the Foundry Fabric IQ tool-connection procedure to configure read permissions.

Ask: “What are the monthly equipment expense totals?” Compare the numbers with the original semantic measures/data results. A successful connection does not produce a correct business answer if the source model's measures, permissions, or licenses are wrong.

### 3. Option C: Work IQ / SharePoint

Use synthetic purchasing policies only in an approved test tenant. Check required user delegation, administrator consent, M365 licensing, and document ACLs. Send the same question as fictional users A/B and verify whether the accessible evidence differs.

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

You have recorded either an actual result for 1 selected extension or the reason access is unavailable, along with your design decision. You can explain the differences between local inference and cloud/enterprise operational capabilities.

## Troubleshooting

Foundry project roles alone do not resolve other products' license, permission, region, or hardware requirements. If the required Preview access is missing, do not work around it using information from another tenant.

## Cleanup

Unload local models and decide whether to retain the model cache. Work with each product's owner to remove test connections, revoke permissions, and disconnect external sources.
