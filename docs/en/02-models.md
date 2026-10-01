> **What you will build:** One model deployment whose selection you can justify, and a comparison table of alternatives.

## Objectives

**This guide uses OpenAI `gpt-6-sol` as the target model**, with version `2026-09-22`. Distinguish the model ID, model version, and deployment name. Cost/performance comparisons with alternatives are optional.

## Concepts and lab map

**What you will try:** The model catalog, model cards, deployment names, and Playground comparisons.

**What is it, and why does it matter?** A model ID identifies the product, a version identifies a particular release, and a deployment name is the name your environment uses to address that deployment. Even the same model can have different usage conditions depending on its region, deployment type, and configuration. A larger model is not guaranteed to distinguish “greater than” from “at or below” in a purchasing rule more accurately. Compare accuracy on real task questions alongside latency and cost so you can explain your choice.

**How do you use it?** Find candidates in the catalog and read their cards for supported APIs, tools, and processing locations. If a deployment already exists, open its Playground rather than recreating it. Compare identical boundary-value questions, then record the selected **deployment name** in your configuration.

**Where do you run it?** This chapter is portal-focused. Browsing models and reading cards are not inference, but deployment and Playground submissions require permissions and cost approval. `FOUNDRY_MODEL_DEPLOYMENT_NAME` in [.env.example](../../.env.example) is the setting that connects to the L03 code.

## Prerequisites

You need the L01 project and permission to deploy models. If learners do not have deployment permissions, use a model deployed by the instructor.

## Steps

### 1. Select gpt-6-sol in the model catalog

In **Discover → Models**, search for **`gpt-6-sol`** and open the OpenAI model card. It is supplied directly through Azure; verify Responses API, structured-output, and function-calling support. Both v1 and v2 use the same model/version in the comparison.

![Discover → Models in the English Contoso project, with search, Available in my project, feature/deployment filters, and model cards.](../../assets/portal/en/02-model-catalog.png)

**Reading the screen:** Check the scope in this order: **Discover** at the top → **Models** on the left → **Available in my project**. Search for candidates and narrow **Supported features / Deployment options / Region**. A visible card does not mean that quota or capacity is available. The models and model count shown when the image was captured are not a required model list for learners.

| What to check on the model card | Why it matters |
| --- | --- |
| Responses / function calling / File search support | Must match the features used in this guide |
| Input and output modalities | Image input and image generation are separate capabilities |
| Regions, deployment types, and quota | A model may appear in the catalog but still be unavailable to deploy |
| Model version and retirement policy | Behavior can vary across versions of the same model name |
| Pricing, context length, and input/output limits | A larger maximum context does not mean a lower cost |
| License and data-processing terms | Terms vary by provider and deployment method |

| Lab setting | Value |
| --- | --- |
| Publisher / model ID | OpenAI / `gpt-6-sol` |
| Model version | `2026-09-22` |
| Suggested deployment name | `contoso-gpt-6-sol` |
| Deployment type | `GlobalStandard`, subject to availability and organizational policy |
| Inference API | Responses API |

Quota and capacity vary by subscription. A visible card does not establish deployability in the selected project. Check supported versions and capacity; if unavailable, record that limitation rather than silently substituting another model.

### 2. Choose a deployment type

| Type | When to use it | In this lab |
| --- | --- | --- |
| Standard / Global Standard / Data Zone Standard | Usage-based service | Choose one allowed by policy |
| Provisioned / PTU | Sustained high throughput and predictable performance | Do not create one for the core course |
| Batch | Large asynchronous workloads | Design as a separate path from online chat |
| Developer | Temporary evaluation of fine-tuned models | Do not confuse it with a general base-model development tier |
| Managed compute | Dedicated VM capacity for models | Check the Preview deployment method and idle costs |
| Instant access | Immediate calls to supported models without deployment | Preview; not a core-course prerequisite |

**Storage location and inference processing location are different.** For Global, check the scope of available regions worldwide; for Data Zone, check the specified zone; for geography-based Standard, check the relevant Azure geography. An APAC zone does not mean Korea alone.

### 3. Deploy and record the name

From the model card's deployment action, select **`gpt-6-sol` / `2026-09-22`** with a supported type/capacity. If you name it `contoso-gpt-6-sol`, set `FOUNDRY_MODEL_DEPLOYMENT_NAME=contoso-gpt-6-sol` in `.env`. The API uses the **actual deployment name**, not merely the catalog model ID.

L01's administrator foundation script can deploy the same model under the name `contoso-chat`. If using that path, keep the actual returned deployment name and do not deploy it again. Changing a model deployment does not automatically redeploy an existing Hosted agent's code or configuration.

Once ready, run each of the following two inputs once in a separately approved Playground check. L08's v1/v2 measurement uses its own three fixed questions.

```text
Summarize this rule in one sentence:
A total of KRW 2,000,000 or less requires team manager approval; a total above KRW 2,000,000 requires approval from both the team manager and the purchasing representative.
```

```text
Rule: A total of KRW 2,000,000 or less requires team manager approval; a higher total requires approval from both the team manager and the purchasing representative.
Compare a total of KRW 2,000,000 with a total of KRW 2,000,001 in a table.
Do not add anything that is not in the rule.
```

| Candidate | Actual results for both questions | Approximate latency | Token/pricing terms | Selection |
| --- | --- | --- | --- | --- |
| `gpt-6-sol` | Record your result | Record your result | Based on the model card | Lab target |
| Separately approved alternative (optional) | Record only if executed | Record your result | Based on the model card | Comparison reason |

A public leaderboard is a starting point for narrowing candidates, not a guarantee of performance on your business data.

### 4. Optional extension: Model router

Model router is a **model deployment** that selects an appropriate model for each request. Where available, start by comparing `Balanced`, then review `Cost`, `Quality`, and the permitted model subset. Use the same 20 evaluation examples.

The routing pool can change even under the same router version identifier. Check allowed models, the minimum context window, data-processing scope, and fallback behavior. Include only approved models in a custom subset; fallback experiments require at least two. **Do not assume the router is necessarily cheaper or more accurate.**

<details markdown="1">
<summary>Going deeper into cost and performance</summary>

Prompt caching depends on conditions such as matching prefixes and the model actually selected. Batch is a separate asynchronous workflow, not just a different option on an online request. Flex/Priority are processing tiers on supported deployments, intended for latency-tolerant and prioritized processing respectively. Review PTU reservation costs, capacity, and cancellation terms, and obtain separate approval before proceeding.

</details>

## Success criteria

You can record the model's **provider / ID / version / deployment name / region / type** separately and explain your selection using pricing, features, and data-processing terms.

## Troubleshooting

**If a model is missing from the deployment menu**, first check model, region, and deployment-type support and access requirements. **Quota and actual capacity are not the same.** A deployment of a particular capacity can fail even when quota is available. Do not quietly switch to a different model without checking its capabilities.

## Cleanup

Keep the deployment you will use and review whether comparison deployments still need to be retained. Record any fixed-cost resources you created in addition to usage-based models.
