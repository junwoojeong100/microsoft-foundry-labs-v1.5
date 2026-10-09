> **What you will build:** A verified record of your model deployments' names, versions, processing scopes, and request limits.

<div class="lab-brief" markdown="1">

**Format:** Inspect the deployments you created in L01 using the portal and ownership record; do not redeploy them.

**Start here:** Distinguish Model ID, Version, and Deployment Name for your `contoso-chat` deployment.

**What to check:** The deployment is ready and actual TPM/RPM meets the plan. Get the first answer in L03.

</div>

## Objectives

**Model ID, model version, and deployment name are different.** This kit pins chat to `gpt-6-sol / 2026-09-22`; L01 names its deployment `contoso-chat`. Availability must be verified in your actual subscription/region during provisioning.

## Concepts and lab map

**What you will try:** Check your model settings, supported features, and throughput.

**What is it, and why does it matter?** Model ID identifies a product, version identifies its release, and deployment name is what code calls. `model="contoso-chat"` uses an existing deployment; it does not create one.

**How do you use it?** Compare portal readiness with the ownership record and save the same name in `.env`. Inspect insufficient capacity before changing it within your scope.

**Where do you run it?** Use Models in the Microsoft Foundry portal and [model_capacity.py](../../samples/model_capacity.py) in your terminal. Listing models/limits is not inference.

## Prerequisites

Use L01's `results/azure-environment.json`, `.env`, project, and model deployments. Resolve an incomplete L01 deployment first; do not substitute another environment or model.

## Steps

### 1. Inspect the models you deployed

1. Open **Build → Models → Deployments → contoso-chat**.
2. Compare Model ID, Version, deployment type, and ready state with the table and receipt `model_configuration`.
3. Inspect `contoso-judge` and `contoso-embedding` too. If absent, investigate L01's deployment rather than creating duplicate names in the portal.

| Purpose | Model ID / version | Name created in L01 |
| --- | --- | --- |
| Answers/agents | `gpt-6-sol` / `2026-09-22` | `contoso-chat` |
| L08 evaluation | `gpt-4.1` / `2025-04-14` | `contoso-judge` |
| L11 retrieval/L15 Memory | `text-embedding-3-small` / `1` | `contoso-embedding` |

![Discover → Models in the English Contoso project, with search, Available in my project, feature/deployment filters, and model cards.](../../assets/portal/en/02-model-catalog.png)

**Reading the screen:** **Discover → Models** shows candidates/cards; **Build → Models → Deployments** shows your actual deployments. A visible card does not establish quota/capacity. Verify Responses API, function calling, File search, current pricing, and retirement conditions.

### 2. Read processing scope and cost conditions

L01's `GlobalStandard` is a usage-based example. Project location, model availability, and inference-processing scope can differ. Confirm the type meets your organizational policy.

| Type | What to verify |
| --- | --- |
| Standard | Microsoft Azure geography processing scope and availability |
| Global Standard | Processing across supported worldwide regions is permitted |
| Data Zone Standard | The designated zone; APAC does not mean Korea alone |
| Provisioned / PTU | Reserved capacity/cost; not created for the core course |

Distinguish storage location from inference processing. Additional model/type comparisons require their own cost, permissions, and matched-input conditions and must be recorded as separate experiments.

### 3. Connect the portal deployment name to code

L01 sets `.env` to `FOUNDRY_MODEL_DEPLOYMENT_NAME=contoso-chat`. Pass the **actual deployment name**, not the catalog Model ID, in API `model`.

| Portal value | Python use |
| --- | --- |
| Home → Project endpoint | `AIProjectClient(endpoint=project_endpoint, ...)` |
| Deployments → Name | `responses.create(model=deployment_name, ...)` |
| Model ID / Version | Deployment/receipt configuration; not separately chosen on every inference request |

This is the **request excerpt** expanded in L03. `client` is the project client from L01/L03; `question` is a synthetic input. This makes a billable inference request, not a deployment:

<details class="implementation-detail" markdown="1">
<summary>Implementation reference: the deployment name in a Python request — read only</summary>

```python
response = client.responses.create(
    model=deployment_name,
    input=question,
    max_output_tokens=512,
    store=False,
)
```

</details>

Do not execute the excerpt in this settings step. Verify portal Name, receipt `model_deployments.chat`, and `.env` all identify `contoso-chat`.

<a id="l02-capacity"></a>

### 4. Compare TPM/RPM plans with actual limits

**TPM is tokens per minute; RPM is requests per minute.** Input and maximum-output reservation affect throughput estimates, not just billed tokens. Neither is a monetary spending cap.

| Purpose | Per-learner recommended TPM / RPM | Planning assumption |
| --- | --- | --- |
| chat | 100,000 / 60 | `(8,192 + 2,048) × 6 starts/minute × 1.5 headroom`, rounded to 10,000 |
| judge | 100,000 / 60 | Same starting budget; evaluation concurrency/context may need more |
| embedding | 10,000 / 6 | `8,192 × 1 start/minute × 1.2 headroom`, rounded to 1,000 |

The calculation is explicit below. **It is not a service minimum or a no-429 guarantee.**

<details class="implementation-detail" markdown="1">
<summary>Implementation reference: the recommended TPM calculation — use the plan command below</summary>

```python
from math import ceil

learners = 1
chat_tpm = ceil((8192 + 2048) * 6 * 1.5 * learners / 10000) * 10000
embedding_tpm = ceil(8192 * 1 * 1.2 * learners / 1000) * 1000
print(chat_tpm, embedding_tpm)
```

</details>

L01's foundation converts the plan using the catalog's model-specific capacity units, increments, and quota. It does not apply `capacity=100` uniformly.

For the portal form comparison, **Deploy → Custom settings** on a model card exposes region, deployment type, and TPM fields corresponding to the code's region, SKU, and throughput plan. Do not submit another deployment after L01.

```bash
python samples/model_capacity.py plan --learners 1
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `plan --learners 1` | Calculates request budgets and recommended limits. | Local only; use actual simultaneous learner count for shared deployments. |

</div>

**After reading the plan, query the actual limits.** This command does not send a model question or change the deployment.

```bash
python samples/model_capacity.py check --learners 1 --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `check ... --live` | Reads your RG, model/version, SKU, and actual `rateLimits`. | Read-only; insufficient limits fail without a model test. |

</div>

Compare `tpm`, `rpm`, `minimum_tpm`, `minimum_rpm`, and `ready` for each `deployments.<purpose>`. Unknown limits do not establish readiness.

<details class="optional-path" markdown="1">
<summary>Only if capacity is insufficient: adjust your deployment</summary>

Verify the exact receipt `run_id`, update permissions, and cost scope. Do not reduce sufficient allocations.

```bash
python samples/model_capacity.py apply --learners 1 --max-capacity 100 --confirm OWN_RUN_ID --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `apply ... --confirm ... --live` | Checks required units/quota, changes only insufficient capacity, and reads it back. | Actual Microsoft Azure change; retains model/version/protection settings and creates no PTU. |

</div>

Exceeding the ceiling or missing quota stops before changes. Do not alter models/regions just to make the check pass.

</details>

<details class="optional-path" markdown="1">
<summary>Optional: multi-model connectivity check, not a duplicate of L03</summary>

The first core inference request is in L03. Choose this separate test only when up to three chat requests, one judge request, and one embedding request are needed.

```bash
python samples/model_capacity.py test --learners 1 --confirm OWN_RUN_ID --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `test ... --confirm ... --live` | Rechecks limits, then sends at most five requests. | At most 180 seconds, zero retries, and 2,048 output tokens per generative request; connectivity, not quality certification. |

</div>

Embedding uses the parent resource's `/openai/v1/embeddings`; project Responses support is not embedding support.

</details>

### 5. Optional extension: Model router

Model router is a separate deployment that selects a model per request. Inspect allowed models, region, fallback, and prices, then compare **the same dev questions**. Do not expose an independent holdout during improvement or assume a router is cheaper/better. Batch, PTU, and fine-tuning have separate conditions/costs outside the core path.

## Success criteria

- You can identify your provider, Model ID, version, Name, region/type, and actual TPM/RPM.
- The deployment name agrees across the portal, `.env`, and ownership record.
- The deployment is ready before L03.

## Troubleshooting

| Symptom | Check first | Next action |
| --- | --- | --- |
| A model is missing or the limit query fails | Region, type, quota, and access | If you could not read the numbers, do not mark the deployment ready. |
| Quota is available but deployment fails | The model's capacity unit and increment | A particular capacity can fail despite available quota. Read the query result and adjust within your own scope. |
| 429 | Current TPM/RPM | Do not retry indefinitely. |

## Cleanup

Reuse L01's three deployments in subsequent modules. Record names, costs, and retention deadlines for additional comparison deployments and inspect them in L19.

<div class="lab-handoff" markdown="1">

**Keep:** Actual chat/judge/embedding deployment names, model versions, TPM/RPM, and ready states. The portal, `.env`, and receipt must match.

**Continue:** [L03 first answer](#l03), using the ready deployment without redeploying it.

</div>
