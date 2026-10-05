> **Working rule:** Use the environment you created and your own results. Preparation → execution → evidence-based judgment → cleanup matters more than matching screenshots.

## Starting checklist

The guide follows one participant's end-to-end workflow. Azure permissions, organizational approval, and feature availability remain action prerequisites; do not assume somebody else completed them.

| Item | Evidence |
| --- | --- |
| Local files/Python | Lab-root folder, `.venv` path, synthetic-data check |
| Subscription/region/budget | Signed-in account, allowed creation/request scope, stop criteria |
| L01 provisioning | Your RG/project, three deployments, and telemetry connection |
| Target consistency | Portal, `.env`, and `results/azure-environment.json` identify the same project |
| Effective access | Actual successful/denied requests and errors, not role names alone |
| Records/cleanup | Created-resource list, your output files, retention and next cost-check times |

Setup uses unique names and ownership tags. Do not copy another participant's receipt or invent a replacement. Block unpermitted operations and distinguish local/design work from execution.

## Core course and electives

Follow **L00 → L01 → … → L10 → L19**. If choosing advanced modules, take them after L10 and finish with L19.

| Stage | What you create or verify |
| --- | --- |
| L01–L02 | Dedicated environment, telemetry, and models; actual invocation names/limits |
| L03 | One model answer, without knowledge/tools |
| L04–L05 | Instructions and then retrieval on the same portal agent |
| L06 | Policy, inventory, draft, and approval boundaries of a separate integrated SDK agent |
| L07 | Local HTTP/OpenAPI/MCP exchange; optional Cloud Toolbox after L11 |
| L08 | Fixed 12-question v1/v2 originals/evaluation for a separate tool-free Prompt Agent |
| L09 | Harmless boundary responses versus actual function blocking |
| L10 | Your L04–L06 response/trace IDs, operations, and durations |
| L19 | Stop your schedules/sessions; verify retention/approved deletion and remaining costs |

**Keep targets distinct.** L05's portal agent, L06's integrated SDK agent, and L08's evaluation-only agent are different. L08 scores do not replace L06 tool-quality checks or per-user document ACL validation.

| Elective | Prerequisite and result |
| --- | --- |
| L11 | L01 models/receipt → your Search service/index/KB → three retrieval comparisons |
| L12 | L11 → Hosted package/local call/deployment/exact-version invocation |
| L13–L14 | Same project/chat model, separate `.venv-advanced`; local SDK orchestration, no L12 required |
| L15 | Chat/embedding and supported Memory → store item, compare scopes, approved item deletion |
| L16 | L05's server-executable agent and L01 telemetry → manual/scheduled execution and stop checks |
| L17 | Local access/cache repair and control design, separate from actual RBAC/network testing |
| L18 | Local promotion-gate repair and release/recovery design; live publishing has separate prerequisites |

Choose electives by **capability to learn**, not participant persona. Mark unsupported operations not performed.

## Time planning

Core L00–L10 displays **285 minutes (4 hours 45 minutes)**; L19 adds ten, totaling 295. The eight electives display **335 minutes (5 hours 35 minutes)**. All modules total **630 minutes (10 hours 30 minutes)**.

These estimate direct work. Add initial installation, permissions/cost approval, quota, Azure creation/indexing/deployment waits, and breaks. They do not guarantee every elective's service operations fit within the displayed duration.

### 90-minute summary path

First **complete your own L01/L02 provisioning and readiness checks**. Ninety minutes does not include starting from no resources.

| Time | Step | Evidence |
| --- | --- | --- |
| 0–5 minutes | Revisit L00 | Model, knowledge, and tools |
| 5–15 minutes | Review L01 state | Your project/models/telemetry |
| 15–35 minutes | L04 agent | No invented facts/tool success |
| 35–60 minutes | L05 File search | Actual citations versus originals |
| 60–80 minutes | Shortened L08 | Compare one pair from your outputs; otherwise read inputs/rubric only |
| 80–90 minutes | L19 cleanup | Resource states, costs, and next check |

Reading/partial execution on this short path is not full core-course completion.

## Your progress record

Keep this table privately, separate from browser progress. Unknown values remain unverified.

| Module/target | Live / local / design / not performed | ID/file | Judgment and evidence | Next action |
| --- | --- | --- | --- | --- |
| Provisioning | Record | Your receipt/portal names | Target agreement/readiness | Resolve pending creation/access |
| Model/agent | Record | Response ID/name/version | Actual text/state/unknown handling | Inspect input/instructions/model |
| Retrieval/tools | Record | Citations/arguments/output | Actual sources/amount/not-ordered | Inspect retrieval/function/inputs |
| Evaluation | Record | Your originals/evaluation JSON/case ID | Scores/reasons/errors/omissions | Analyze using fixed criteria |
| Traces | Record | Response/trace ID | Operations/durations/unobserved layers | Check query scope/collection |
| Cleanup | Record | Actual resource state | Stopped/retained/approved deletion | Recheck costs within 24 hours |

## Read code, portal controls, and results in order

1. **Locate the input destination.** Terminal, portal Chat, `.env`, Python excerpts, and sample outputs differ.
2. **Understand the request/change.** Find client, inputs, API, and result in the code; match portal settings. The portal does not run your PC's functions.
3. **Run one command, then pause.** Distinguish plans from requests and verify the next step's prerequisite.
4. **Judge using evidence.** Read originals, actual tool output, citations, errors, and IDs rather than relying on claims.
5. **Manage resources.** Closing the browser or resetting progress does not stop schedules, resources, or costs.

L13/L14/L17/L18 follow **Try it → Change one thing → Explain the result**. Edit only `practice/` copies of `exercise.py`; preserve tests, source fixtures, and evaluation gates.

## Check boundaries before completion

| Observation | Correct interpretation |
| --- | --- |
| Plan output/client initialization | Not an actual successful Azure request |
| File upload | Separate from indexing completion |
| Agent claims a lookup/order succeeded | Requires actual tool evidence; real ordering is not connected |
| `completed` | Execution finished, not answer/quality certification |
| Only some evaluation rows succeed | Do not omit errors/missing rows to produce a passing average |
| Local access/release tests pass | Not actual Azure RBAC/deployment/rollback verification |
| Memory A/B searches | Lab-scope comparison, not a complete authenticated-user access test |
| One successful evaluation | Not generalization, production release, or independent holdout validation |

Do not rewrite criteria, baseline v1, or failed originals after observing results. Finish with **per-resource state, retention deadline, and next cost-check time**.
