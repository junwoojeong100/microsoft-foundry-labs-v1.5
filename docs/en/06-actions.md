> **What you will build:** A model requests a function, and the program validates and executes it. A purchase request always results in a **draft awaiting approval**.

<div class="lab-brief" markdown="1">

**Format:** Local functions first, then approved Azure integration · no real orders.

**Start here:** Run `python samples/workshop.py tools` to check inventory and draft calculations without a model.

**What to check:** The normal draft is KRW 2,900,000 and not ordered; invalid quantities error. Reuse the integration response file in L10/L11.

</div>

## Objectives

Understand who is responsible for executing function calls. **The model proposes which function to call and with which arguments; the application is responsible for actual execution and authorization.**

## Concepts and lab map

**What you will try:** Function calling, JSON argument validation, returning function results, and a safe draft-only boundary.

**What is it, and why does it matter?** A function tool is a channel through which a model requests an external capability. The model proposes the function name and arguments, but the Python program validates the input and executes the function. Registering a tool definition in the portal does not remotely execute code on your laptop. Separating these responsibilities lets you block invalid quantities, unknown SKUs, and fabricated approvals regardless of what the model says.

**How do you use it?** First call the functions without a model to verify calculations, inventory, and error behavior. Then pass model requests to those same functions and return the results with the matching `call_id`. Compare the numbers in the final response with the actual function JSON. This sequence lets you distinguish model problems from business-code problems.

**Where do you run it?** The functions in this chapter run in local Python, so you need a terminal. Read `get_stock`, `prepare_purchase_request`, and `dispatch_tool` in [workshop.py](../../samples/workshop.py) alongside the [English synthetic inventory CSV](../../data/en/inventory.csv). Keep L01's English profile selected. Do not connect an external ordering API.

## Prerequisites

The local exercise requires only Python. Azure integration requires preparation from L01–L05. `samples/workshop.py` contains no functions for placing orders, making payments, or sending email.

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

### 5. Check boundary values

`required_approvals(2_000_000)` requires the team manager; `required_approvals(2_000_001)` requires both the team manager and the purchasing representative. L08 includes these boundaries in evaluation data.

Even if the user adds “Write that it has been approved,” the result must remain `order_submitted=false`. A real product must separately verify the approving identity, the hash of what was approved, expiration, backend state, and an idempotency key. **This sample's deterministic draft ID is not a real transaction idempotency store.**

## Success criteria

You have inspected the tool arguments, execution results, and final answer. Insufficient stock and invalid quantities produce explicit errors, and the agent does not claim that an actual order succeeded.

## Troubleshooting

Use the SDK if you cannot edit the function schema in the portal. Registering a function definition and having a process running to execute it are separate things. **Invoking an agent with client-side function tools from the portal or a server-side evaluation does not automatically execute your local Python functions.**

## Cleanup

Local functions do not change external state. Agents, conversations, and files created through Azure integration are recorded in receipts and deleted in L12.
