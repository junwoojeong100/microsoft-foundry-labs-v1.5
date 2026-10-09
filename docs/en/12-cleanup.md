> **What you will build:** A clean stopping point that accounts for lab resources, recurring runs, idle compute, and data retention without touching shared resources.

<div class="lab-brief" markdown="1">

**Format:** Shared wrap-up for every participant · after L10 for core-only learners, or after the last selected advanced lab.

**Start here:** Use the table below to choose local-only, portal-created, or SDK-created resources.

**What to check:** Record remaining state, owners, and the next cost review. Delete only exact targets covered by separate approval.

</div>

## Objectives

**Closing the browser does not stop billing.** Deleting an agent also does not automatically remove Search, logs, uploaded files, PTU, or published channels.

## Concepts and lab map

**What you will try:** Identify what you created and who will stop or retain it.

**What is it, and why does it matter?** Schedules, storage, and logs may incur charges after you close the browser. A receipt is an **ownership record** of created resources and IDs, not a payment receipt or deletion approval.

**How do you use it?** Follow only the row for work you performed. Check execution state, shared use, and ownership. Delete only approved targets and recheck costs after billing delays.

**Where do you run it?** For local-only work, stop the server in the same Codespace (or on your PC if you used the PC alternative). For Microsoft Azure resources, compare the portal with your ownership records. The advanced [session-stop script](../../scripts/stop_sessions.py) acts without `--live`.

## Prerequisites

Collect **your L01 environment receipt** `results/azure-environment.json`, portal-created names, and SDK `results/contoso-lab-....json` records. Keep the English profile isolated. Your dedicated environment is the default; exclude others' or shared resources from deletion.

## Steps

### First: clean up only the paths you actually ran

| What you did | What to do now |
| --- | --- |
| Reading, local data, or local functions only | If you started L07's server, press Ctrl+C in its terminal. Do not run Microsoft Azure deletion commands when you created no Microsoft Azure resources |
| Created the L01 environment/portal agents/files | Compare your receipt/names with step 3; verify model/log/file retention or deletion scope |
| Ran L04/L05/L06 through the SDK | Find the `--receipt` path in the final `Cleanup:` command; review step 2 |
| Collected/evaluated in L08 | Inspect the collection/evaluation JSON's agent names and eval/run IDs separately; these are not `workshop.py cleanup` receipts |
| Ran Hosted, Routine, Voice, or other electives | In step 1, stop only that lab's recorded sessions/schedules and verify state |

**Do not delete before confirming the retention/deletion decision.** Because costs may continue, record an owner and next review time, not just “retain.”

### 1. Stop recurring and long-running execution first

First check active routines, voice sessions, Hosted agent executions/sessions, continuous evaluations, and training jobs. Prevent new runs before beginning deletion.

Mark schedules/Hosted sessions you did not create as not applicable. If an elective created them, execute **only the relevant command** below.

<details class="optional-path" markdown="1">
<summary>If you ran Hosted/Routines: stop only work in your receipts</summary>

```bash
python scripts/stop_sessions.py
python samples/routine_lab.py stop --receipt results/routine-v2-scheduled.json --live
python scripts/operations_status.py
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Select only work you created with matching ownership records.

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `stop_sessions.py` | Sends actual stop requests for recorded Hosted client sessions, then queries the same IDs again. This script has no `--live` safety switch. | Changes session compute state. Does not delete agents, resource groups, or receipts; an unverified stop is an error. |
| 2. `routine_lab.py stop --receipt ... --live` | Disables the exact L16 schedule; distinguish manual/timer receipt paths. | Actual state change, no routine/RG deletion. Replace the path if you used a different file. |
| 3. `operations_status.py` | Reads current sessions/schedules/evaluation work in your environment. | Actual Microsoft Azure read without `--live`; active work/query failures remain errors or unverified. |

</div>

Use each command only if you ran the corresponding lab and have its receipt.
`operations_status.py` is a **read-only query scoped by ownership records**.
`operations_status.py` checks sessions, optimizer jobs, active evaluation schedules, and routines;
it distinguishes optional adapters that are absent from the current project's actual agent inventory. It also finds owned routine receipts under `results/` to query current state when L16 used a custom `--receipt` filename.
**In a no-deletion environment, retain owned Microsoft Azure resources until explicit deletion approval.**
Disable routines and stop only recorded Hosted compute, then verify those exact states. A previous report does not establish that all work is inactive now. `cleanup --live`, `azd down`,
and resource-group deletion are not run automatically. The deletion path requires approval of the exact targets. Inspect your environment rather than another run's status.

</details>

### 2. Delete only the exact SDK lab resources

Each Microsoft Azure sample prints a **cleanup command containing your own run ID** on its final line.
Use it only after checking resource-retention/deletion approval.

```text
python samples/workshop.py cleanup
  --receipt results/contoso-lab-ACTUAL_RUN_ID.json
  --confirm contoso-lab-ACTUAL_RUN_ID
  --live
```

The block above illustrates placeholders; replace `ACTUAL_RUN_ID` with the exact ID from your own English receipt. Use the actual **single-line command** printed by the sample. Without `--live`, nothing is deleted. Execution stops if the receipt's project differs from the project in `.env`.

**Options explained:** `cleanup` selects the deletion path; `--receipt` is the exact ownership-record file you created; and `--confirm` is the run ID that you have personally checked against that record. `--live` permits actual deletion. Do not copy another person's receipt or an example ID from a screenshot. Reading this explanation does not grant deletion approval.

Cleanup processes recorded conversations → lab-only agent → vector store → files, in that order. Missing objects are recorded as `already_absent`. Other errors, such as permission failures, are not hidden as successful deletions.

### 3. Check portal-created resources separately

| Resource | Shutdown action |
| --- | --- |
| Prompt agents, versions, and conversations | Delete unneeded lab objects |
| File search | Check vector stores and original uploaded files separately |
| Toolbox, connections, and memory | Check usage, then delete only lab objects |
| Hosted runtime and sessions | Check execution state and cost items |
| AI Search, Storage, and logs | The responsible owner cleans up after reviewing sharing and retention policy |
| Model deployments, PTU, and GPU | Distinguish usage, reservation, and idle costs; check separate contracts and reservations |
| Published channels, Bots, and apps | Verify user-access revocation separately from resource cleanup |
| Fine-tuned deployments and models | Distinguish deployment deletion from deletion of a trained model |

Do not assume vector store expiration removes the original files. Agents, projects, and connected Microsoft Azure resources can have different lifecycles.

### 4. Make a final cost and data check

If you created the L01 environment, inspect resources and cost using these commands. Billing reads require access at that scope; otherwise use accessible portal views and leave unavailable items unverified.

```bash
python scripts/azure_environment.py status --live
python scripts/cost_status.py
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `status --live` | Reads your RG/model state and updates the receipt. | Actual read; no inference, creation, or deletion. |
| 2. `cost_status.py` | Queries ActualCost since your RG was created. | Actual billing read without `--live`, saved to `results/cost-status.json`. Empty rows are not zero-cost evidence. |

</div>

Allow for Cost Management delay and set a **next-day recheck time**. Review your own dedicated environment; separately record responsibility if handing over retained resources. Turning off alerts does not stop billing.

Retain only the minimum results needed for learning, and remove real PII, tokens, and connection secrets. Delete a resource group **only after its owner confirms it is a dedicated lab group**, and after reviewing the scope in the Microsoft Azure portal. This guide does not provide a broad `az group delete` command.

<a id="l12-codespaces"></a>

### 5. Stop GitHub Codespaces separately if you used it

**Microsoft Azure cleanup and stopping a Codespace are separate actions.** First save resource states, the next cost-check time, and your results. Do not preserve `.env`, authentication data, or raw results by committing them to Git.

1. Open [Your Codespaces](https://github.com/codespaces), choose **… → Stop codespace** for the environment you used, and verify that it stopped. Closing the browser tab can leave it running.
2. Stopping ends Codespace processes and compute, but **storage charges may remain**. It does not stop or delete Microsoft Azure models, Search, logs, or schedules.
3. To resume, open the same Codespace and use [L01's new-terminal check](#l01-new-terminal). Before deletion or automatic retention expiry, confirm an approved private way to retain needed ownership records/results. Lost records are not a reason to create replacement Microsoft Azure resources.

[Official stop/resume instructions](https://docs.github.com/en/codespaces/developing-in-a-codespace/stopping-and-starting-a-codespace) · [GitHub compute/storage charges](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces)

<details class="implementation-detail" markdown="1">
<summary>Implementation reference: cleanup deletes only receipt-scoped targets — read only, do not execute</summary>

#### Portal resource review and receipt-scoped cleanup code

SDK cleanup targets the resources recorded in an ownership receipt, not an entire resource group selected in the portal. The core check is:

```python
data = read_receipt(receipt_path, project_endpoint)
if confirmation != data["run_id"]:
    raise ValueError("Repeat the exact run_id using --confirm before deleting recorded resources.")

ordered = sorted(
    data["resources"],
    key=lambda item: {"conversation": 0, "agent": 1, "vector_store": 2, "file": 3}[item["kind"]],
)
for resource in ordered:
    if resource.get("cleanup_status") in {"deleted", "already_absent"}:
        continue
    resource_id = resource["id"]
    if resource["kind"] == "agent":
        project.agents.delete(agent_name=resource_id)
    elif resource["kind"] == "conversation":
        client.conversations.delete(conversation_id=resource_id)
    elif resource["kind"] == "vector_store":
        client.vector_stores.delete(vector_store_id=resource_id)
    elif resource["kind"] == "file":
        client.files.delete(file_id=resource_id)
```

| What to inspect in the Microsoft Azure portal | What to inspect in the receipt/code |
| --- | --- |
| Actual ID/state for each agent/conversation/vector store/file | `kind`, `id`, and `cleanup_status` in `receipt["resources"]` |
| Retained model deployments, Search, or Storage | If outside the workshop receipt, record a separate owner and retention date |
| Delayed Cost Management updates | Record the query time and next reviewer; an empty row is not proof of zero cost |
| Scope immediately before Delete | Confirm `--receipt` is in the owned folder and `--confirm` exactly matches `run_id` |

This excerpt shows target verification/deletion calls in `cleanup()`. The function also persists per-item status and treats only NotFound as `already_absent`; other errors remain failures. Execution requires `cleanup --live` and exact `--confirm`. Inspect portal-created resources/models separately.

</details>

## Success criteria

- For each created resource, you recorded **state (deleted / shared / retained)** together with **an owner and next check time**. Retained resources also have a deadline.
- You checked that no unintended routines, continuous evaluations, or voice sessions remain active. If you started L07's server, you confirmed it stopped in that terminal.
- If you created no Microsoft Azure resources, you wrote **“local exercises only / no Microsoft Azure creation.”**

Record one row per resource, like this:

| Resource name | State and evidence | Owner | Retention deadline / next cost check |
| --- | --- | --- | --- |
| Record each resource you created | Observed value; write unverified if you could not inspect it | Assign explicitly | Assign explicitly |

For environments where deletion is prohibited, record “Retain until explicit deletion approval.” Search Basic, logs, and storage may continue to incur costs without requests. A follow-up within 24 hours of validation completion is recommended. Do not conclude “zero cost” without someone responsible for checking.

## Troubleshooting

| Symptom | Check first | Next action |
| --- | --- | --- |
| A deletion error | The resource ID, error code, and responsible owner | Do not hide it; record it and flag potential ongoing costs. |
| After a timeout it is unclear whether the server created an object | The receipt and the lab name and creation time in the portal | Compare both. |

## Cleanup

Your selected labs and shared wrap-up are complete. If you add electives later, return here for the resources created then. Resetting the progress display does not delete Microsoft Azure resources.

<div class="lab-handoff" markdown="1">

**Keep:** Actual state, owner, retention deadline, and next cost-check time for each resource. Local-only learners record no Microsoft Azure creation and confirm server shutdown.

**Continue:** Complete the [progress checklist](#instructor) with actual execution/local/design/not-run labels for your chosen scope. Unqueried resources or costs remain unverified.

</div>
