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
for this routine. L13/L14 Agent Framework roles execute in local code and are not remote routine targets. Scheduling an agent with local client-side functions does not execute those local functions.
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

Use the core SDK environment. If azd or Routine support is missing, follow only [L12's azd setup section](#l12-azd) for installation/authentication, then install `azure.ai.routines` using `azd extension install azure.ai.routines` when needed. Inspect the installed `azd ai routine --help`; do not force-update it. Hosted deployment itself is unnecessary.
Query only the English project and App Insights in this checkout's `results/azure-environment.json`.
Do not automatically upgrade CLI extensions/global settings or use resources from another environment.

### Choose your starting path

| Required value | Where to get it | Relationship to verify |
| --- | --- | --- |
| `ACTUAL_AGENT_NAME` | Your L05 project → Build → Agents name, or that SDK run's owned receipt | File search runs server-side; do not substitute L06's local-function agent |
| Project/App Insights | Your own L01 `results/azure-environment.json` and telemetry connection | Matches `.env` and allows reading action traces |
| Two `--receipt` paths | The **distinct new manual/scheduled files** below | Never overwrite previous or other-language records |

Follow **one manual execution → one timer execution → verify both disabled**. Without Microsoft Azure approval, read only the first `create` plan. Resolve log access and response-collection prerequisites before scheduling. Do not reschedule merely because an execution's trace is absent.

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
| 1. `create --agent ... --receipt ...` | Replace `ACTUAL_AGENT_NAME` with the actual English agent name, specify a new ownership-record path, and read only the creation plan. `--receipt` is the file that tracks execution results and targets. | No Microsoft Azure requests. Select an agent capable of server-side execution, not one with only local functions. |
| 2. `create ... --live` | Creates a disabled one-time timer and records it in the specified receipt. The environment variable also passes through to child azd processes. | Creates a real schedule object. This alone does not establish successful scheduled execution. |
| 3. `dispatch ... --live` | Requests one manual execution of the disabled routine in the same receipt. A pre-attempt file limits duplicate requests. | Model/agent invocation charges may apply. Do not label manual acceptance/execution as successful automatic scheduling. |

</div>

Create a uniquely named one-time timer in the **disabled** state, then dispatch it manually.

- The manifest has 1 trigger and 1 action; the English input is “Summarize Contoso policies; no external sending, orders, or approvals.”
- Pass `action.input` through a file; do not use a nonexistent create `--input` option.
- Do not overwrite an existing receipt. Specify a separate path with `--receipt` for a new experiment.
- Before dispatch, the script exclusively creates a separate `.dispatch.json` attempt record, so even after a timeout it does not automatically invoke the same receipt again.
- A manual acceptance ID alone does not establish execution success.

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

The script checks for the actual action trace for up to 6 minutes and disables the routine in `finally`. It puts a unique verification marker in the input and looks only for an `invoke_agent` span for the same agent, after the scheduled time, with exactly the same user input.

- **Verification requires all of these:** a successful span, an actual response ID, an assistant `finish_reason=stop`, and nonempty output.
- **Not success evidence:** redacted output, in-progress/failed records, and responses to different inputs.

<details class="optional-path" markdown="1">
<summary>Why inspect traces instead of CLI run history?</summary>

**Do not interpret an empty array/null in CLI run history as evidence that nothing ran.**
The [current official documentation](https://learn.microsoft.com/azure/foundry/agents/how-to/use-routines#view-run-history)
states that azd does not support history queries. The checked extension decodes `value`/`nextPageToken`
instead of the service's `data`/`next_link`, so it can print
`{"value":null,"next_page_token":""}` even when an execution exists.
Routine creation, inspection, and stopping still use azd; the script does not work around this with Routine REST/SDK calls.
Execution evidence is obtained separately through bounded KQL against the owned App Insights resource.
If the trace cannot be read, end with **execution unverified** rather than assuming success or non-execution.

</details>

Open the `Evidence:` original beside its receipt and connect **same agent → after `trigger_at` → input with the same `marker` → completed response/trace**. Never copy a manual receipt's result as proof that a timer fired.

### 3. Recheck the stopped state

![Paused-schedule list example. Inspect the target agent, trigger, last run, and Paused state under Build → Agents → Routines.](../../assets/portal/en/12-routines.png)

**Read the screen:** Under **Agents → Routines**, first find your schedule name and target agent. The UI may label the stopped state **Paused**; the value to verify in the CLI/API is `enabled=false`. Connect **Last run** to your trace/response from the previous step and inspect the business output.

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

| Record to retain | Manual execution | Timer execution |
| --- | --- | --- |
| Target | Manual receipt's name and agent | Scheduled receipt's name, agent, and `trigger_at` |
| Execution evidence | Actual response/trace after manual dispatch | Actual same-input response/trace after the timer |
| Shutdown evidence | `enabled=false` for that name | `enabled=false` for that name |

`dispatch` and `scheduled-test` attempt shutdown when finishing. After an error, use **the receipt from that attempt** with step 3's `stop` and `status`; do not copy the scheduled path when recovering a manual run.

### 4. Identity and recovery boundaries

Distinguish the routine creator, agent runtime identity, and tool connection identity.
A user creating an event does not mean every downstream call runs as that user.
Even with retries or duplicate invocations, this lab performs only reads/drafts.
Real orders require separate approval and durable idempotency, so do not connect them.

Long-running checkpoints, reconnection, and approval expiry, as well as Autopilot managers, Entra agent users,
and mail/Teams permissions, are **design exercises**. The timer lab does not create an Autopilot account.
If you selected continuous evaluation, stop its schedule separately as well.

<details class="implementation-detail" markdown="1">
<summary>Implementation reference: the one-time trigger and agent-input manifest — read only</summary>

#### Portal Routines and the actual creation manifest

Portal **Agents → Routines** shows the schedule time, target agent, and enabled state. The bundled Python does not guess a recurring schedule: it writes one timer trigger and one agent action to a manifest with a unique receipt.

```python
manifest = {
    "triggers": {
        "default": {"type": "timer", "at": fire_at.strftime("%Y-%m-%dT%H:%M:%SZ")}
    },
    "action": {
        "type": "invoke_agent_responses_api",
        "agent_name": args.agent,
        "input": state["input"],
    },
}
write_new(manifest_path, manifest)
created = azd(
    endpoint, evidence, "create", name,
    "--file", str(manifest_path),
    "--enabled=false",
)
```

| Portal Routines view | Value to compare in code/receipt |
| --- | --- |
| Routine name | `name` and `state["name"]` in the receipt |
| Trigger time | `triggers.default.at` and `state["trigger_at"]` |
| Target agent/input | `action.agent_name` / `action.input` |
| Enabled / Paused | `enabled` from `azd show`; `stop_verified(...)` disables it |
| Last run | Separate App Insights trace and response ID; a receipt alone does not prove execution |

`fire_at` is the UTC trigger time; `manifest_path` is a new JSON file in `results/`. Python invokes azd, not portal UI automation. Compare the portal target/time/Paused state with code inputs; live actions require matching receipt, `--live`, and approval.

</details>

## Success criteria

- You verified the action execution after the actual scheduled time, the completed business response, and the disabled state.
- If you only created a schedule or manually dispatched it, record execution as complete only for that scope.
- If the status query failed, do not write “it has probably stopped.”
- If you could not read the run ID, leave it `null`, distinct from response/trace IDs.
- Human content review is optional guidance; do not mark an unperformed review as completed.

## Troubleshooting

| Symptom | Check first | Next action |
| --- | --- | --- |
| A CLI JSON decode error | It can occur after the service operation has already succeeded | Rather than immediately recreating it under a new name, first check show/list for the receipt's name. |
| A permission, protocol, model quota, or tool authentication error | The actual action traces and the original error | Compare both to tell the causes apart. |
| The CLI run history is empty | An empty result alone does not identify a cause | Do not conclude a cause from it. |

## Cleanup

Retain the routine in the disabled state. Check its state even for a one-time timer that is not scheduled to run.
If it targets Hosted, stop the agent session compute separately as well.

<div class="lab-handoff" markdown="1">

**Keep:** Each manual/scheduled receipt's name, actual response/trace, and `enabled=false` readback. If status is unverified, stop and query that receipt's routine before leaving.

**Continue:** [L17](#l21) for control design, otherwise [L19](#l12). Do not leave a routine active when finishing.

</div>
