> **What you will build:** A clean stopping point that accounts for lab resources, recurring runs, idle compute, and data retention without touching shared resources.

## Objectives

**Closing the browser does not stop billing.** Deleting an agent also does not automatically remove Search, logs, uploaded files, PTU, or published channels.

## Concepts and lab map

**What you will try:** The separate lifecycles of stopping execution, deleting objects, retaining data, and checking costs.

**What is it, and why does it matter?** Stopping compute leaves storage and always-on resources such as Search, files, and logs in place. Conversely, deleting an agent can lose evidence you need, so deleting everything solely to reduce cost is not necessarily safe either. A receipt is an ownership manifest of the names, IDs, and project created by this lab. It is the starting point for distinguishing your lab resources from shared ones.

**How do you use it?** First prevent recurring execution, verify the stopped state of recorded sessions, then assign an owner and retention deadline for each resource. Delete only exact objects covered by separate approval. Finally, account for billing delays by assigning someone to recheck costs.

**Where do you run it?** Compare portal status/cost screens with the [session-stop code](../../scripts/stop_sessions.py). Some management scripts below call Azure without `--live`. Do not assume a command is read-only or free based on its name alone.

## Prerequisites

Collect the list of created English resources and `results/contoso-lab-....json` receipts from the separate English checkout. Keep `FOUNDRY_LAB_LANGUAGE=en` selected. Do not import Korean-run receipts or use them to stop or delete resources. Mark resources shared with an instructor or other learners.

## Steps

### 1. Stop recurring and long-running execution first

First check active routines, voice sessions, Hosted agent executions/sessions, continuous evaluations, and training jobs. Prevent new runs before beginning deletion.

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
| 2. `routine_lab.py stop --live` | Disables the schedule recorded in the default `results/routine.json`. If you used another receipt, specify `--receipt` as in L17. | Changes actual schedule state. Does not delete other schedules or resource groups. |
| 3. `azure_environment.py status --live` | Reads and checks the Azure environment recorded in the ownership receipt. | Sends Azure read requests and records status. No model inference. |
| 4. `operations_status.py` | Reads sessions, optimizer jobs, evaluation schedules, and routines in the owned English environment. Runs without `--live` and reports remaining work as failure. | Read-only in Azure, but updates local `validation/english/current/operations.json` under the English profile. Do not rerun it in a checkout preserving completed evidence; check the portal instead. |
| 5. `cost_status.py` | Queries ActualCost by service from the owned English resource group's creation time to the present. Reads the real billing API without `--live`. | An authoring tool that updates local `validation/english/current/cost.json` under the English profile. Do not rerun it in a preserved copy. Empty billing rows do not prove zero cost. |

</div>

Use each command only if you ran the corresponding lab and have its receipt.
The final two commands are **read-only Azure queries scoped by ownership receipts**.
`operations_status.py` checks sessions, optimizer jobs, active evaluation schedules, and routines;
`cost_status.py` queries only actual costs posted to the new resource group. It does not report empty cost rows as USD 0.
**The English validation's default retention policy is to retain owned Azure resources until explicit deletion approval.**
Disable routines and stop only recorded Hosted compute, then verify those states. The English one-shot Routine succeeded and was confirmed disabled; the dev-only Optimizer was still running at this reporting cutoff, so do not infer that every job has stopped. Consult the [current English report](../../validation/english/current/report.json) for subsequent job/compute status. `cleanup --live`, `azd down`,
and resource-group deletion are not run automatically. The deletion path below is for learners with separate approval. Existing `validation/current/` operational and cost records describe the historical Korean environment, not the new English one.

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

Each created resource has a recorded **deletion decision / shared-retention decision / retention deadline / responsible owner**, and no unintended routines, continuous evaluations, or voice sessions remain active.

For environments where deletion is prohibited, record “Retain until explicit deletion approval.”
Search Basic, logs, and storage may continue to incur costs without requests.
A follow-up within 24 hours of validation completion is recommended. Do not conclude “zero cost” without someone responsible for checking.

The English Memory lifecycle verified remember, user isolation, and deletion of **only the synthetic item**. Its store was retained; this result does not authorize store or resource-group deletion.

In the **historical Korean validation**, Azure infrastructure and agents/stores were retained. Deletion of **1 synthetic item**
for that Memory lifecycle check was recorded separately from deletion of an Azure store or resource group. Automatic expiration of that validation vector store was also disabled
to preserve it. These are not English-run cleanup results. Record the new English environment's actual retained objects, verified stop states, and ongoing costs separately; storage costs can continue until a later approved cleanup.

## Troubleshooting

Do not hide deletion errors. Record the resource ID, error code, and responsible owner, and flag potential ongoing costs. If a timeout leaves it unclear whether the server created an object, check the lab name and creation time in the portal as well as the receipt.

## Cleanup

The core course is complete. Add further capabilities only when needed. Resetting the progress display does not delete Azure resources.
