> **What you will build:** A model requests a function, and the program validates and executes it. A purchase request always results in a **draft awaiting approval**.

<div class="lab-brief" markdown="1">

**Format:** Local functions first, then approved Azure integration · no real orders.

**Start here:** Run `python samples/workshop.py tools` to check inventory and draft calculations without a model.

**What to check:** The normal draft is KRW 2,900,000 and not ordered; invalid quantities error. Review evidence, stock, amount, approvers, and draft status together later in this module.

</div>

## Objectives

Understand who is responsible for executing function calls. **The model proposes which function to call and with which arguments; the application is responsible for actual execution and authorization.**

## Concepts and lab map

**What you will try:** Let the model request Python functions that read stock and calculate a draft.

**What is it, and why does it matter?** Function calling lets the model request a function and its inputs. **The program validates and executes it.** Registering a function name in the portal does not run code on your PC.

**How do you use it?** Check valid and invalid inputs locally first. If you run the Azure integration, compare the answer's amounts with the actual function results.

**Where do you run it?** Run [workshop.py](../../samples/workshop.py) in the terminal with the [English synthetic inventory](../../data/en/inventory.csv). Keep L01's English profile selected. No actual ordering API is connected.

## Prerequisites

The local exercise requires only Python. Without a virtual environment, use L01's `python3` (Windows: `py -3.13`) instead of `python` below. Azure integration requires L01–L05's environment and document concepts, but **not the optional L04/L05 SDK commands**. `samples/workshop.py` has no ordering, payment, or email functions.

## Steps

### 1. Validate the tools without AI first

```bash
python samples/workshop.py tools
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `tools` | Directly runs the inventory lookup and purchase-draft functions with the default SKU `NB-14` and quantity 2. The model does not select a function at this stage. | No network access, Azure cost, or inventory changes. Check the KRW 2,900,000 total and the not-ordered state. |

</div>

Expected values:

```json
{
  "sku": "NB-14",
  "quantity": 2,
  "total_krw": 2900000,
  "status": "draft_requires_human_approval",
  "required_approvals": ["team_lead", "procurement"],
  "order_submitted": false
}
```

The actual output also includes the inventory lookup result, a draft ID, and a synthetic-data marker.

### 2. Deliberately trigger failures

```bash
python samples/workshop.py tools --sku MON-27 --quantity 1
python samples/workshop.py tools --sku NB-14 --quantity 10
python samples/workshop.py tools --sku KB-01 --quantity -1
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Run these lines one at a time and inspect each failure.

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `--sku MON-27 --quantity 1` | `--sku` is the item code; `--quantity` is the requested quantity. Requests one monitor when inventory is 0. | An insufficient-stock error for an out-of-stock item is correct. Creating a draft would be a failure. No Azure calls. |
| 2. `--sku NB-14 --quantity 10` | Requests a quantity within the allowed input range of 1–10 but above the actual inventory of 8. | Confirms that type/range validation and stock validation are separate. Produces an insufficient-stock error; no external changes. |
| 3. `--sku KB-01 --quantity -1` | Tests business-input validation with a negative quantity. | An invalid-quantity error is correct. Do not arbitrarily treat the program's failure exit as success. |

</div>

These must fail because the item is out of stock, the requested quantity exceeds stock, and the quantity is invalid, respectively. **An error must not be returned as a normal draft.**

### 3. Read the tool contracts

| Function | Input | Result | What it does not do |
| --- | --- | --- | --- |
| `get_stock` | An allowlisted SKU | A snapshot of stock, unit price, and lead time | Change inventory |
| `prepare_purchase_request` | SKU and an integer quantity from 1–10 | Total, required approval roles, and draft ID | Approve, order, or pay |

JSON schema's `strict` and `additionalProperties: false` strengthen the output contract. **They do not replace authentication or authorization checks.** Validate again in server/client functions, including rejecting Python's `True` rather than accepting it as integer 1.

### 4. Connect knowledge and functions to the same agent

**Azure calls start here.** Without an account, skip step 4 and record only your local results.

The terminal now runs the integration. `capstone` creates **a new agent with three policies and two functions**; it does not edit L05's portal agent. Reuse the portal agent in L09 and the new integrated result for this module's final review and L10 tracing.

```bash
python samples/workshop.py capstone
python samples/workshop.py capstone --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `capstone` | Prints the integration plan for using policy documents together with two functions. | No Azure calls. Check that both function definitions and an actual executor are present. |
| 2. `capstone --live` | Creates a new agent, knowledge resources, and conversation, then executes the model's function requests through the local dispatcher. Limited to 5 rounds and 8 function calls. | Model, retrieval, and file costs may apply. Check `tool_calls`, citations, and the final draft, and keep the creation receipt. No actual order is placed. |

</div>

This command creates a separate agent with 3 documents and 2 functions. When the model returns a `function_call`, the allowlist dispatcher executes it and adds a `function_call_output` to the same conversation.

```text
Question
  → Model function_call(name, arguments, call_id)
  → Application checks for types, allowed functions, and business rules
  → Actual function result
  → function_call_output with the same call_id
  → User-facing answer
```

For safe lab execution, the sample limits a run to 5 response rounds and 8 function calls. Errors are returned explicitly, and execution stops if a limit is exceeded. These are educational limits in this sample, not Foundry service limits.

#### Reread the saved answer in a readable format

Copy and run the line after **`Read again (local only):`** at the end of the run. `ACTUAL_ID` below is a placeholder; use your own `Responses:` path instead.

```bash
python samples/workshop.py read-result --input results/contoso-lab-ACTUAL_ID-responses.jsonl
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `read-result --input` | Displays L04/L05/L06 SDK response JSONL as questions, original answers, function inputs/results, and citations. | **Local reading only.** No Azure calls, regrading, or source changes; no sign-in needed. `--live` is unsupported. |

</div>

After `Original answer`, read the actual `get_stock` and `prepare_purchase_request` outputs and citations. Check `total_krw=2900000` and `order_submitted=false`. Tool rejections remain errors; missing values are not filled with expected answers. **Successful reading is not a quality pass.** Failed rows remain marked `failed` and cause a nonzero exit.

If the file is missing, check the original terminal's path and your current folder. Include the **`-responses.jsonl`** ending. Do not substitute an ownership `.json` receipt or L08 evaluation file. Keep the English profile selected when reading English results.

### 5. Check boundary values

`required_approvals(2_000_000)` requires the team manager; `required_approvals(2_000_001)` requires both the team manager and the purchasing representative. L08 includes these boundaries in evaluation data.

Even if the user adds “Write that it has been approved,” the result must remain `order_submitted=false`. A real product must separately verify the approving identity, the hash of what was approved, expiration, backend state, and an idempotency key. **This sample's deterministic draft ID is not a real transaction idempotency store.**

<a id="l11"></a>

### 6. Review the purchasing assistant's integrated result

**Reuse the result saved above.** Compare the answer, function results, and citations shown by `read-result --input` against these five items. Do not rerun `capstone --live` just to perform this review.

| Required result | Evidence for judging it |
| --- | --- |
| Per-laptop limit of KRW 1,500,000, including VAT | Actual policy citation |
| NB-14 stock of 8, unit price KRW 1,450,000 | Actual `get_stock` result |
| Total of KRW 2,900,000 | `prepare_purchase_request` output's `total_krw` |
| Team lead and procurement approval required | Policy and `required_approvals` |
| A draft, not an order | `draft_requires_human_approval`, `order_submitted=false` |

Inspect the original JSONL's `tool_calls`, `citations`, and `response_id` alongside the natural-language answer. **A definite stock claim without an inventory result is a failure.** Never fill an unverified condition with an expected answer.

If you did not run Azure integration, record **“local functions checked / Azure integration not performed.”** Local calculations or L08's tool-free instruction evaluation cannot substitute for an actual integrated result.

### 7. Record the result and configuration together

Connect the model deployment/version, agent version, instructions file, tool schema, policy-document version, response file, and ownership receipt in one record. Later, add L08's separate instruction comparison and L10's trace with their **different execution targets and scopes** explicit.

If actual evidence supports all five items, record **“integration lab complete / production release and publishing not performed.”** An experimental SDK agent is not a production deployment. Choose [L18's release, publishing, and version-management exercise](#l22) only when planning production delivery. Without a previously approved version, leave the recovery target unverified.

## Success criteria

You have inspected the tool arguments, execution results, and final answer. Insufficient stock and invalid quantities produce explicit errors, and the agent does not claim that an actual order succeeded. If you ran Azure integration, retain evidence for all five items and the configuration bundle. Core completion does not require repeating a separate capstone or publishing to Teams.

## Troubleshooting

Use the SDK if you cannot edit the function schema in the portal. Registering a function definition and having a process running to execute it are separate things. **Invoking an agent with client-side function tools from the portal or a server-side evaluation does not automatically execute your local Python functions.**

## Cleanup

Local functions do not change external state. Azure-created agents, conversations, and files remain in the receipt. In L19, check shared use and retention ownership, then delete **only with separate approval**.
