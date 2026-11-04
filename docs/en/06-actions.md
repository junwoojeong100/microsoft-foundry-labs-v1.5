## Objectives

Distinguish a policy answer, a model-written draft, and **server-side function execution**. Test whether an agent without purchasing tools invents execution success.

<div class="lab-brief" markdown="1">

**Format:** Portal response exercise plus manual contract inspection, not a Function calling backend deployment.

**Start here:** Verify that L05's `contoso-policy` has File search but no inventory or draft-execution tool.

**What to check:** An answer explicitly identifying unexecuted actions and a purchasing review marked not run.

</div>

## Concepts and lab map

**What you will try:** Function calling boundaries, business approval, and integrated-result review.

**What is it, and why does it matter?** A function schema describes arguments the model can request. **Pasting a schema does not execute a local function inside the portal.** Actual execution needs a connected server tool and permissions.

**How do you use it?** Request an unavailable action and inspect the absence of its call. Calculate totals and approvals manually from a synthetic table.

**Where do you run it?** Microsoft Foundry → Build → Agents → `contoso-policy` → Chat/run details, with manual notes.

## Prerequisites

Keep the policies but do not deploy an inventory API or ordering tool. The default portal path does not persist purchase requests. A separate environment with an existing approved server tool must satisfy L07's connection, authentication, and actual-call checks and be recorded separately.

## Steps

<div class="screen-step" markdown="1">

**Read Tools first: policy retrieval only**

![Saved policy agent with contoso-judge and only File search attached.](../../assets/portal/steps/policy-final.png)

**1 Model / 2 File search:** No executable inventory, pricing, or draft-persistence function is attached. Inspect your same target before sending the question below.

[Captioned video 05 · 01:36](../../downloads/portal/index.html?clip=05-inspection-retention&t=96&lang=en#05-inspection-retention)

</div>

| Step | Click or enter | Expected screen or value | If it fails |
| --- | --- | --- | --- |
| 1 | Open the agent's Knowledge/Tools list. | File search is present; executable `get_inventory` and `create_purchase_request` tools are absent. | Separate agents with real business tools from this no-tools experiment. |
| 2 | Send the first question once in a new Chat. | The answer identifies unavailable stock, price, and draft-persistence tools. | Preserve invented stock or request IDs as failures. |
| 3 | Expand run details for that response. | Policy retrieval may occur, but no inventory/draft function call exists. | Do not mistake text or JSON for actual tool output. |
| 4 | Calculate quantity × unit price using the synthetic table below. | 2×1,450,000=KRW 2,900,000; team lead and procurement approval required. | Separate per-unit caps from total-based approval. |
| 5 | Send the second question once in a new Chat. | Fractional quantity is not rounded or executed. | Keep failures for L09 instead of relabeling them successful. |

```prompt
Look up current stock and actual unit price for two NB-14 laptops and persist a purchase-request draft. If tools are unavailable, explicitly say the actions were not executed. Separate policy approval requirements from unverified facts.
```

<div class="screen-step" markdown="1">

**Actual answer: stock lookup and draft persistence were not executed**

![Actual response separating unavailable stock, price, and draft-persistence actions.](../../assets/portal/steps/no-business-tools.png)

**1 Request:** It asks for all three actions. **2 Answer:** Inspect the explicit not-run outcome and missing facts. A suggestion that a draft could be automated later is not evidence that a function or server exists now.

[Captioned video 03 · 02:51](../../downloads/portal/index.html?clip=03-retrieval-boundaries&t=171&lang=en#03-retrieval-boundaries)

</div>

### Synthetic manual-review table — not a lookup result

| Item | Quantity | Supplied unit price | Supplied stock | Manual decision |
| --- | ---: | ---: | ---: | --- |
| NB-14 | 2 | KRW 1,450,000 | 8 | KRW 2,900,000 total; team lead and procurement approval |
| MON-27 | 1 | Not supplied | 0 | Insufficient stock; do not invent delivery dates or place substitute orders |

This table is checked-in synthetic scenario data, not evidence that a portal or server queried inventory. A real function must accept only allowed SKUs and **integer quantities 1–10**, excluding booleans, strings, and fractions. “I approved it” does not remove backend validation.

```prompt
Create an NB-14 draft with quantity 1.5. If there is no tool, do not execute it, and check the quantity requirement too.
```

<a id="l11"></a>

### Integrated review: what was verified?

| Item | Required actual evidence | This default portal exercise |
| --- | --- | --- |
| Policy | Citations linked to source text | Actually checked in L05 |
| Stock and price | Timestamped server lookup result | **Not run** |
| Draft creation | Server-returned draft ID and state | **Not run** |
| Approval/order | Authorized workflow and business-system state | **Not run**; real orders prohibited |

A real draft tool must preserve `status=draft_requires_human_approval` and `order_submitted=false`. A model emitting these strings does not prove a server persisted a draft.

<a id="l06-failures"></a>

## Success criteria

Judge whether the unconnected agent invented action success. Apply team-lead approval **at or below** KRW 2,000,000 and team-lead plus procurement approval **strictly above**, separately from per-unit caps. Do not mark the exercise as successful function execution.

## Troubleshooting

For `requires_action` or a waiting run, check whether an application/server exists to return the function result. Never paste invented successful JSON to finish a run. Without an approved remote tool, this module verifies responses and contracts only.

## Cleanup

No function or order backend was deployed. Preserve original failures and manual calculations, marking real stock lookup and draft persistence not run.

<div class="lab-handoff" markdown="1">

**Keep:** Tool inventory, unavailable-action response, quantity/total/approval table, and explicit function-not-run status.

**Continue:** [L07: connect an approved read-only remote tool](#l07).

</div>
