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

**Where do you run it?** For local-only work, stop your PC's server. For Azure resources, compare the portal with your ownership records. The advanced [session-stop script](../../scripts/stop_sessions.py) acts without `--live`.

## Prerequisites

Collect the list of created English resources and `results/contoso-lab-....json` receipts from the separate English checkout. Keep `FOUNDRY_LAB_LANGUAGE=en` selected. Do not import Korean-run receipts or use them to stop or delete resources. Mark resources shared with an instructor or other learners.

## Steps

### First: clean up only the paths you actually ran

| What you did | What to do now |
| --- | --- |
| Reading, local data, or local functions only | If you started L07's server, press Ctrl+C in its terminal. Do not run Azure deletion commands when you created no Azure resources |
| Created portal agents/files | Collect their names and compare with step 3; confirm sharing, owner, and retention deadline |
| Ran L04/L05/L06 through the SDK | Find the `--receipt` path in the final `Cleanup:` command; review step 2 |
| Ran Hosted, Routine, Voice, or other electives | In step 1, stop only that lab's recorded sessions/schedules and verify state |

**Do not delete before confirming the retention/deletion decision.** Because costs may continue, record an owner and next review time, not just “retain.”

### 1. Stop recurring and long-running execution first

First check active routines, voice sessions, Hosted agent executions/sessions, continuous evaluations, and training jobs. Prevent new runs before beginning deletion.

Mark work you did not create as not applicable. The following is an **advanced/administrator path**, not a shared shutdown script where everyone runs all five commands.

<details class="operator-only" markdown="1">
<summary>Advanced/administrators only: stop and inspect work with owned receipts</summary>

```bash
python scripts/stop_sessions.py
python samples/routine_lab.py stop --live
python scripts/azure_environment.py status --live
python scripts/operations_status.py
python scripts/cost_status.py
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Administrator path for labs that were run and have ownership receipts.

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `stop_sessions.py` | Sends actual stop requests for recorded Hosted client sessions, then queries the same IDs again. This script has no `--live` safety switch. | Changes session compute state. Does not delete agents, resource groups, or receipts; an unverified stop is an error. |
| 2. `routine_lab.py stop --live` | Disables the schedule recorded in the default `results/routine.json`. If you used another receipt, specify `--receipt` as in L16. | Changes actual schedule state. Does not delete other schedules or resource groups. |
| 3. `azure_environment.py status --live` | Reads and checks the Azure environment recorded in the ownership receipt. | Sends Azure read requests and records status. No model inference. |
| 4. `operations_status.py` | Reads sessions, optimizer jobs, evaluation schedules, and routines in the owned English environment. Runs without `--live` and reports remaining work as failure. | Read-only in Azure; writes private `results/operations-status.json`. Run only when that inspection is approved. |
| 5. `cost_status.py` | Queries ActualCost by service from the owned English resource group's creation time to the present. Reads the real billing API without `--live`. | Requires approval for cost inspection and writes private `results/cost-status.json`. Empty billing rows do not prove zero cost. |

</div>

Use each command only if you ran the corresponding lab and have its receipt.
The final two commands are **read-only Azure queries scoped by ownership receipts**.
`operations_status.py` checks sessions, optimizer jobs, active evaluation schedules, and routines;
it distinguishes optional adapters that are absent from the current project's actual agent inventory. It also finds owned routine receipts under `results/` to query current state when L16 used a custom `--receipt` filename.
`cost_status.py` queries only actual costs posted to the new resource group. It does not report empty cost rows as USD 0.
**In a no-deletion environment, retain owned Azure resources until explicit deletion approval.**
Disable routines and stop only recorded Hosted compute, then verify those exact states. A previous report does not establish that all work is inactive now. `cleanup --live`, `azd down`,
and resource-group deletion are not run automatically. The deletion path below is for learners with separate approval. Inspect your own environment rather than reusing another run's status.

</details>

### 2. Delete only the exact SDK lab resources

Each Azure sample prints a **cleanup command containing your own run ID** on its final line.
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

Do not assume vector store expiration removes the original files. Agents, projects, and connected Azure resources can have different lifecycles.

### 4. Make a final cost and data check

Because Cost Management updates can be delayed, assign someone to recheck the next day. Turning off budget alerts does not stop billing.

Retain only the minimum results needed for learning, and remove real PII, tokens, and connection secrets. Delete a resource group **only after its owner confirms it is a dedicated lab group**, and after reviewing the scope in the Azure portal. This guide does not provide a broad `az group delete` command.

## Success criteria

For each created resource, record **state (deleted / shared / retained)** together with **an owner and next check time**. Retained resources also need a deadline. Check that no unintended routines, continuous evaluations, or voice sessions remain active.

| Resource name | State and evidence | Owner | Retention deadline / next cost check |
| --- | --- | --- | --- |
| Record each resource you created | Observed value; write unverified if you could not inspect it | Assign explicitly | Assign explicitly |

If you created no Azure resources, write **“local exercises only / no Azure creation.”** If you started L07's server, confirm it stopped in that terminal.

For environments where deletion is prohibited, record “Retain until explicit deletion approval.”
Search Basic, logs, and storage may continue to incur costs without requests.
A follow-up within 24 hours of validation completion is recommended. Do not conclude “zero cost” without someone responsible for checking.

## Troubleshooting

Do not hide deletion errors. Record the resource ID, error code, and responsible owner, and flag potential ongoing costs. If a timeout leaves it unclear whether the server created an object, check the lab name and creation time in the portal as well as the receipt.

## Cleanup

Your selected labs and shared wrap-up are complete. If you add electives later, return here for the resources created then. Resetting the progress display does not delete Azure resources.
