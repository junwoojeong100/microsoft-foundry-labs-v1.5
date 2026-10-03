> **What you will build:** The settings and rationale for one lab model deployment. Comparing alternatives is optional.

<div class="lab-brief" markdown="1">

**Format:** Foundry portal · do not recreate a model deployment already supplied.

**Start here:** Record the model ID, version, and deployment name separately in your own project.

**What to check:** Confirm the ready deployment, processing location, and cost conditions, then save its name in `.env`. L03 is the first required call.

</div>

## Objectives

**This guide uses OpenAI `gpt-6-sol` as the target model**, with version `2026-09-22`. Distinguish the model ID, model version, and deployment name. Cost/performance comparisons with alternatives are optional.

## Concepts and lab map

**What you will try:** Identify the one model deployment that the labs will call.

**What is it, and why does it matter?** A model ID is the product name, a version is its release, and a deployment name is what your code calls. If `gpt-6-sol` is deployed as `contoso-chat`, your code uses `contoso-chat`.

**How do you use it?** Check the supplied deployment's model, version, and ready state. Save its **actual deployment name** in `.env`. Creating a deployment and comparing questions are optional.

**Where do you run it?** Use the Foundry portal and [.env.example](../../.env.example). Reading a list is not a model call; deployment and Playground submissions need permissions and cost approval.

## Prerequisites

You need L01's project and permission to inspect and use the supplied model. **Learners using a ready deployment do not need permission to deploy a new model.**

**The default path is inspect → check cost conditions → save the name.** New deployment, extra questions, and Model router are in expandable optional sections.

## Steps

### 1. Inspect the supplied deployment first

1. Open **Build → Models → Deployments** in your project.
2. Select the deployment name supplied by your instructor. Compare its **model ID / version / ready state** with the table below.
3. If it is missing or failed, stop and check with the owner. **This is not a step to choose Create / Deploy and make a new resource.**

<details markdown="1">
<summary>Optional reference: reading the model catalog and model card</summary>

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

</details>

| Lab setting | Value |
| --- | --- |
| Publisher / model ID | OpenAI / `gpt-6-sol` |
| Model version | `2026-09-22` |
| Suggested deployment name | `contoso-gpt-6-sol` |
| Deployment type | `GlobalStandard`, subject to availability and organizational policy |
| Inference API | Responses API |

Quota and capacity vary by subscription. A visible card does not establish deployability in the selected project. Check supported versions and capacity; if unavailable, record that limitation rather than silently substituting another model.

### 2. Check processing location and cost conditions

Start with **one administrator-approved usage-based type**. `GlobalStandard` is this guide's example, not the correct choice for every organization. Deployment type affects data-processing location as well as cost.

<details markdown="1">
<summary>Optional reference: other deployment types and processing scopes</summary>

| Type | When to use it | In this lab |
| --- | --- | --- |
| Standard / Global Standard / Data Zone Standard | Usage-based service | Choose one allowed by policy |
| Provisioned / PTU | Sustained high throughput and predictable performance | Do not create one for the core course |
| Batch | Large asynchronous workloads | Design as a separate path from online chat |
| Developer | Temporary evaluation of fine-tuned models | Do not confuse it with a general base-model development tier |
| Managed compute | Dedicated VM capacity for models | Check the Preview deployment method and idle costs |
| Instant access | Immediate calls to supported models without deployment | Preview; not a core-course prerequisite |

**Storage location and inference processing location are different.** For Global, check the scope of available regions worldwide; for Data Zone, check the specified zone; for geography-based Standard, check the relevant Azure geography. An APAC zone does not mean Korea alone.

</details>

### 3. Save the actual deployment name in your settings

If you name it `contoso-gpt-6-sol`, set `FOUNDRY_MODEL_DEPLOYMENT_NAME=contoso-gpt-6-sol` in `.env`. The API uses the **actual deployment name**, not merely the catalog model ID.

L01's administrator foundation script can deploy the same model under the name `contoso-chat`. If using that path, keep the actual returned deployment name and do not deploy it again. Changing a model deployment does not automatically redeploy an existing Hosted agent's code or configuration.

**Pause and check:** Does the portal deployment name match the saved `.env` value? If it is also ready, continue to **Success criteria → L03**. No question submission is required here.

<details class="operator-only" markdown="1">
<summary>Administrators only: no deployment exists and creation is approved</summary>

On the model card, choose **Deploy → Custom settings**. Check **model `gpt-6-sol` / version `2026-09-22` / approved type and capacity / deployment name**, then choose **Deploy**. Confirm **Succeeded/ready** before giving learners the actual name. Do not proceed with only the name of a failed deployment.

</details>

<details class="optional-path" markdown="1">
<summary>Optional: compare two model answers after additional cost approval</summary>

In the ready deployment's **Playground → Chat**, submit each input once. L08's v1/v2 measurement uses its own 12 fixed composite questions.

```prompt
Summarize this rule in one sentence:
A total of KRW 2,000,000 or less requires team manager approval; a total above KRW 2,000,000 requires approval from both the team manager and the purchasing representative.
```

```prompt
Rule: A total of KRW 2,000,000 or less requires team manager approval; a higher total requires approval from both the team manager and the purchasing representative.
Compare a total of KRW 2,000,000 with a total of KRW 2,000,001 in a table.
Do not add anything that is not in the rule.
```

| Candidate | Actual results for both questions | Approximate latency | Token/pricing terms | Selection |
| --- | --- | --- | --- | --- |
| `gpt-6-sol` | Record your result | Record your result | Based on the model card | Lab target |
| Separately approved alternative (optional) | Record only if executed | Record your result | Based on the model card | Comparison reason |

A public leaderboard is a starting point for narrowing candidates, not a guarantee of performance on your business data.

</details>

### 4. Optional extension: Model router

<details class="optional-path" markdown="1">
<summary>Not required for the core lab: compare per-request model selection</summary>

Model router is a **model deployment** that selects an appropriate model for each request. Where available, start by comparing `Balanced`, then review `Cost`, `Quality`, and the permitted model subset. Use the same 20 evaluation examples.

The routing pool can change even under the same router version identifier. Check allowed models, the minimum context window, data-processing scope, and fallback behavior. Include only approved models in a custom subset; fallback experiments require at least two. **Do not assume the router is necessarily cheaper or more accurate.**

<details markdown="1">
<summary>Going deeper into cost and performance</summary>

Prompt caching depends on conditions such as matching prefixes and the model actually selected. Batch is a separate asynchronous workflow, not just a different option on an online request. Flex/Priority are processing tiers on supported deployments, intended for latency-tolerant and prioritized processing respectively. Review PTU reservation costs, capacity, and cancellation terms, and obtain separate approval before proceeding.

</details>

</details>

## Success criteria

You can record the model's **provider / ID / version / deployment name / region / type** separately and explain your selection using pricing, features, and data-processing terms.

## Troubleshooting

**If a model is missing from the deployment menu**, first check model, region, and deployment-type support and access requirements. **Quota and actual capacity are not the same.** A deployment of a particular capacity can fail even when quota is available. Do not quietly switch to a different model without checking its capabilities.

## Cleanup

Keep the deployment you will use and review whether comparison deployments still need to be retained. Record any fixed-cost resources you created in addition to usage-based models.
