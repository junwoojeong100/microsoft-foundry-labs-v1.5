> **What you will build:** Verify a real scheduled Contoso policy summary through its response/trace, then confirm that the routine is disabled.

<div class="lab-brief" markdown="1">

**Format:** Advanced elective · requires a server-executable agent and log-read access.

**Start here:** Confirm the L05 agent and distinguish a manual invocation from a one-time schedule.

**What to check:** An actual response after the scheduled time and `enabled=false`. Creation or manual dispatch alone is not successful scheduled execution.

</div>

## Objectives

**A Routine determines when to run, orchestration determines how to process the work, and Autopilot determines which organizational identity acts.**
Creating a schedule object is separate from a successful business result.

## Concepts and lab map

**What you will try:** Schedule one policy summary and confirm execution and stopped state.

**What is it, and why does it matter?** A Routine schedules an agent. The trigger defines “when,” and the action defines “what.” It can run after the browser closes, so check the response and stopped state, not just creation.

**How do you use it?** Record manual and scheduled executions separately. Find the actual response after the scheduled time and recheck `enabled=false`. Do not rerun merely because a list is empty.

**Where do you run it?** Use portal **Agents → Routines** and [routine_lab.py](../../samples/routine_lab.py). Autopilot accounts, business messaging, and long-running work are separate design exercises.

## Prerequisites

You first need a Prompt Agent that runs on the server. Use L05's File search agent
or L15's policy worker. Scheduling an agent with local client-side functions does not execute those local functions.
Distinguish the GA status of the Routines service from the Beta status of the azd extension, and check current conditions such as CMK limitations.

```bash
AZURE_DEV_USER_AGENT=microsoft_foundry_skill azd version
AZURE_DEV_USER_AGENT=microsoft_foundry_skill azd extension list
AZURE_DEV_USER_AGENT=microsoft_foundry_skill azd ai routine --help
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `azd version` | Checks the current azd version. The preceding `AZURE_DEV_USER_AGENT=...` is an environment variable identifying this command process. | Prints a local version. It does not mean the skill is installed, a user is signed in, or permissions have been granted. |
| 2. `azd extension list` | Lists installed extensions and their versions. | Reads the list only; it does not automatically install or upgrade anything. |
| 3. `azd ai routine --help` | Reads the actual subcommands and options available in the installed extension. | Shows help; no schedule creation or inference. |

</div>

Prepare the core SDK environment and the azd `azure.ai.routines` extension. Keep L01's English profile selected and do not save tokens to files.
Query only the English project and App Insights in this checkout's `results/azure-environment.json`.
Do not automatically upgrade CLI extensions/global settings or use resources from another environment.

## Steps

### 1. First, manually invoke a disabled routine

```bash
python samples/routine_lab.py create --agent ACTUAL_AGENT_NAME --receipt results/routine-en-manual.json
AZURE_DEV_USER_AGENT=microsoft_foundry_skill python samples/routine_lab.py create --agent ACTUAL_AGENT_NAME --receipt results/routine-en-manual.json --live
AZURE_DEV_USER_AGENT=microsoft_foundry_skill python samples/routine_lab.py dispatch --receipt results/routine-en-manual.json --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `create --agent ... --receipt ...` | Replace `ACTUAL_AGENT_NAME` with the actual English agent name, specify a new ownership-record path, and read only the creation plan. `--receipt` is the file that tracks execution results and targets. | No Azure requests. Select an agent capable of server-side execution, not one with only local functions. |
| 2. `create ... --live` | Creates a disabled one-time timer and records it in the specified receipt. The environment variable also passes through to child azd processes. | Creates a real schedule object. This alone does not establish successful scheduled execution. |
| 3. `dispatch ... --live` | Requests one manual execution of the disabled routine in the same receipt. A pre-attempt file limits duplicate requests. | Model/agent invocation charges may apply. Do not label manual acceptance/execution as successful automatic scheduling. |

</div>

Create a uniquely named one-time timer in the **disabled** state, then dispatch it manually.
The manifest has 1 trigger and 1 action; the English input is “Summarize Contoso policies; no external sending, orders, or approvals.”
Pass `action.input` through a file; do not use a nonexistent create `--input` option.
Do not overwrite an existing receipt. Specify a separate path with `--receipt` for a new experiment.
Before dispatch, the script exclusively creates a separate `.dispatch.json` attempt record, so even after a timeout
it does not automatically invoke the same receipt again. A manual acceptance ID alone does not establish execution success.

### 2. Verify real scheduled execution

Using the path below with a new receipt creates a **one-time timer** for 2 minutes later.
Do not substitute manual dispatch for successful scheduled execution.

```bash
AZURE_DEV_USER_AGENT=microsoft_foundry_skill python samples/routine_lab.py scheduled-test --agent ACTUAL_AGENT_NAME --receipt results/routine-en-scheduled.json --delay-seconds 120 --wait-seconds 360 --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `scheduled-test` | `--delay-seconds 120` schedules one execution 2 minutes later; `--wait-seconds 360` allows up to 6 minutes to verify evidence. Replace `ACTUAL_AGENT_NAME` with the English agent name and use a new `--receipt` file, separate from the manual experiment. | Real scheduling, model, and log-query charges may apply. Checks the unique input and completed trace, then disables the routine at the end. Six minutes is not a monetary spending cap. |

</div>

The script checks for the actual action trace for up to 6 minutes and disables the routine in `finally`.
It puts a unique verification marker in the input and looks only for an `invoke_agent` span for the same agent,
after the scheduled time, with exactly the same user input. Verification requires all of the following:
a successful span, an actual response ID, an assistant `finish_reason=stop`, and nonempty output.
Redacted output, in-progress/failed records, and responses to different inputs are not success evidence.

**Do not interpret an empty array/null in CLI run history as evidence that nothing ran.**
The [current official documentation](https://learn.microsoft.com/azure/foundry/agents/how-to/use-routines#view-run-history)
states that azd does not support history queries. The checked extension decodes `value`/`nextPageToken`
instead of the service's `data`/`next_link`, so it can print
`{"value":null,"next_page_token":""}` even when an execution exists.
Routine creation, inspection, and stopping still use azd; the script does not work around this with Routine REST/SDK calls.
Execution evidence is obtained separately through bounded KQL against the owned App Insights resource.
If the trace cannot be read, end with **execution unverified** rather than assuming success or non-execution.

### 3. Recheck the stopped state

![Build → Agents → Routines in contoso-workshop-en. Inspect each English policy timer's target, trigger, last run, and actual enabled or paused state.](../../assets/portal/en/12-routines.png)

**Read the screen:** Under **Agents → Routines**, first find your English schedule name and target agent. The UI may label the stopped state **Paused**; the value to verify in the CLI/API is `enabled=false`. A **Last run** value does not prove that the business output was correct; connect it to the trace/response from the previous step. The [English capture log](../../content/portal-screenshots.en.json) records observed states separately from backend execution. The English one-shot Routine **succeeded and was disabled**, as recorded in the [execution report](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/blob/6fddd4642be0d0ac9dfee9b9b51e7b00b5cf1cde/validation/english/current/report.json); this is a scoped timer result, not a release-quality pass or proof that every other job stopped.

```bash
AZURE_DEV_USER_AGENT=microsoft_foundry_skill python samples/routine_lab.py stop --receipt results/routine-en-scheduled.json --live
AZURE_DEV_USER_AGENT=microsoft_foundry_skill python samples/routine_lab.py status --receipt results/routine-en-scheduled.json --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `stop --receipt ... --live` | Sets the specified owned schedule's enabled state to false. | Sends a real schedule-stop request. Does not delete the routine itself or the RG. |
| 2. `status --receipt ... --live` | Reads the current state of the same schedule again. | Confirm `enabled=false` in the remote readback. Sending a stop request alone is not completion. |

</div>

Target only the name and endpoint in the receipt. Do not automatically enable recurring cron schedules.
Run this stop command even after an exception or interruption. The script does not delete routines or RGs.
A default `results/routine.json` in the same English checkout remains readable with `status`/`stop`; do not overwrite or redispatch it. Never import a historical Korean receipt into this checkout.
Even if disable ends with a timeout/decoding error, run `show` again and confirm **`enabled=false` for the same name**.

### 4. Identity and recovery boundaries

Distinguish the routine creator, agent runtime identity, and tool connection identity.
A user creating an event does not mean every downstream call runs as that user.
Even with retries or duplicate invocations, this lab performs only reads/drafts.
Real orders require separate approval and durable idempotency, so do not connect them.

Long-running checkpoints, reconnection, and approval expiry, as well as Autopilot managers, Entra agent users,
and mail/Teams permissions, are **design exercises**. The timer lab does not create an Autopilot account.
If you selected L19 Voice or continuous evaluation, stop those sessions/schedules separately as well.

## Success criteria

You have verified the action execution after the actual scheduled time, the completed business response, and the disabled state.
If you only created a schedule or manually dispatched it, record execution as complete only for that scope.
If the status query failed, do not write “it has probably stopped.”
If you could not read the run ID, leave it `null`, distinct from response/trace IDs.
Human content review is optional guidance; do not mark an unperformed review as completed.

<details markdown="1">
<summary>Historical Korean-run observations and recovery — not new English lab results</summary>

The following observations belong to the **historical Korean run**, whose private configuration and receipts stay in their original checkout. They are not evidence that the English run succeeded. The original failure/observation records stating “CLI history was empty” remain preserved.
A follow-up investigation found successful action spans and actual policy summary output (`finish_reason=stop`)
for the same policy worker at the scheduled time `2026-09-29T22:38:35Z` and manual dispatch time `22:44:59Z`.
The trace for the scheduled time is `8bf878b65509efa39d9643632629f506`,
and the response is `resp_07018918263947dc006abc3deaaf34819787a318905a8318ad`.
The 404 from direct response retrieval was also preserved; inability to retrieve a response was not reclassified as absence of a response.
This evidence was not substituted with successful results from other File search, Hosted, or A2A executions.

In a separate v2 validation of the corrected runner, `contoso-policy-timer-v2-9a3154d0` was scheduled only once.
The trace `ebd60144b61d68788cb939b085f6c308` at `2026-09-30T01:58:35Z`
and response `resp_0a4cb48ea4632934006abc6cca6314819390ca3283c545e1c2`
showed completed output matching the unique marker. No manual dispatch was performed, and `enabled=false` was rechecked.
Those originals belong to their recorded environment; do not copy them into another run as new evidence. Keep personal execution receipts under `results/` and share only the latest reviewed set with its actual scope.

</details>

## Troubleshooting

A CLI JSON decode error can occur after the service operation has already succeeded.
Rather than immediately recreating it under a new name, first check show/list for the receipt's name.
Distinguish permission, protocol, model quota, and tool authentication errors in run history.

## Cleanup

Retain the routine in the disabled state. Check its state even for a one-time timer that is not scheduled to run.
If it targets Hosted, stop the agent session compute separately as well.
