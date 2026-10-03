> **What you will build:** An evidence-based explanation of “Why was it wrong?”, “Why was it slow?”, and “How much did it use?” for a single run.

## Objectives

**Evaluation shows whether it was good, Trace shows what happened, and Monitoring shows how behavior changes over time.**

## Concepts and lab map

**What you will try:** Traces/spans, Application Insights connections, correlation between responses and logs, and Monitoring over time.

**What is it, and why does it matter?** A trace is the path a request takes; a span is an individual operation within it, such as a model call, retrieval, or tool call. Total duration alone cannot tell you whether a slow answer was caused by retrieval or the model. Response IDs and trace IDs are also different identifiers, so you must find the actual correlation. Missing logs may mean you have not observed the run yet, not that no error occurred.

**How do you use it?** Check the project's collection connection and read permissions, then narrow the scope using the time, agent, and response ID of a synthetic run you already have. Inspect parent/child span order, duration, and status to explain where failure first occurred. Read quality scores in L08, individual execution causes in this chapter, and long-term changes through Monitoring.

**Where do you run it?** Use the portal's agent Traces together with [trace_lab.py](../../samples/trace_lab.py). Automatic collection does not expose every detail inside local functions. Review privacy and cost before collecting more raw log content.

## Prerequisites

You need results from L05 or L06, Application Insights that can be connected to the project, and log-read permissions. Log collection and retention also incur costs.

The administrator of a new dedicated environment uses `python scripts/azure_environment.py monitoring --live`
to create Log Analytics/App Insights and the project connection. `monitoring` adds observability resources to the environment in the ownership receipt; `--live` permits actual creation and connection. Log-retention costs may apply, so learners using an already-connected project must not run it again. The definition is in [observability.bicep](../../infra/observability.bicep).
Connection secrets in the bundled Bicep are referenced only within Azure and must not appear in output, Git, or packages.
The 30-day log retention and daily ingestion limit do not enforce a hard cap on total charges.

## Steps

### 1. Connect server-side tracing first

Connect Application Insights through **Agents → Traces → Connect**. If that button is unavailable, use **Manage → Project details → Connected resources → Add connection → Application Insights**.

Server-side tracing for Prompt/Hosted agents can begin after connection without code changes. It does not automatically trace every detail inside your client-side functions.

### 2. Find and correlate one of your runs

First reuse an L05/L06 run collected after tracing was connected. If none exists, send one approved synthetic question and record its response ID/time. Do not repeatedly resend questions because the list is empty.

| Required value | Where to obtain it | Check the binding |
| --- | --- | --- |
| Response JSONL | The `results/contoso-lab-…-responses.jsonl` path printed after `Responses:` by the L05/L06 SDK | Open one row in an editor; inspect `id`, `response_id`, `agent_name`, and `configuration.agent_version` |
| Agent name/version | That row, or the configuration of the agent you invoked in the portal | Do not substitute the L08 evaluation agent or L14 Hosted name |
| Application Insights app ID | Supplied by the administrator. Bundled environments store it at `monitoring.appId.value` in `results/azure-environment.json` | Compare `monitoring.appInsightsId.value` with the project's actual connection. Do not copy a key/connection string |

With portal-only results, completing the **portal path** using the response ID is sufficient. Do not fabricate a JSONL file or pass L08's comparison JSON to this JSONL input. The CLI reads only the last 24 hours; read older evidence within the portal's approved retention scope or leave correlation unverified.

![Prompt Agent Traces for the English Contoso project. Locate ID search, version/status/date filters, durations, tokens, and estimated costs without exposing identifying values.](../../assets/portal/en/06-traces.png)

**Reading the screen:** In **Build → Agents → your agent → Traces**, first set **Date range** and **Version**. Search using your own English run's trace/conversation/response ID, then open a row to inspect individual operations. **Completed** means execution finished, not that the answer was correct. Use the [English capture log](../../content/portal-screenshots.en.json) for the exact observation scope; do not treat historical Korean trace IDs as evidence for this run.

Find the following in the trace.

| Evidence | What to record |
| --- | --- |
| Agent/model execution | Name, version, start time, and total duration |
| Retrieval call | Actual returned documents and empty results; mark content unobserved if access is unavailable |
| Function/MCP call | Name, arguments, and errors; inspect JSONL `tool_calls` separately if local-function spans are absent |
| Model usage | Input/output tokens and available cost indicators; absent means uncollected, not zero |
| Conversation/response | Request-to-execution link; shared `operation_Id`, parent `operation_ParentId`, and child `id` |

### 3. Distinguish three types of failure

**Incorrect policy answer:** Was the correct document retrieved? If not, investigate retrieval. If it was, investigate instructions, the model, or answer synthesis.

**Slow answer:** Break total latency into model, retrieval, tool, and network/wait stages. Do not prescribe a model change when the tool is slow.

**The function succeeded but the answer failed:** Check whether the tool output was returned to the same conversation/call ID and whether the final output completed.

**Timing example — synthetic teaching data, not an Azure trace.** Assume these child operations run sequentially without overlap.

| Operation | Start–end (ms) | Observed duration | Judgment |
| --- | ---: | ---: | --- |
| Whole request | 0–4,000 | 4,000ms | Parent span; do not add child durations to it again |
| Policy retrieval | 100–800 | 700ms | Also check whether the evidence sections are correct |
| Model response | 900–3,800 | 2,900ms | Largest observed interval; inspect output length/tokens first |
| Inventory tool | 3,800–3,850 | 50ms | Not the primary bottleneck in this example |

Observed children total 3,650ms, leaving 350ms. **Do not call the remaining 350ms network latency without evidence.** Parallel spans overlap and cannot simply be summed. If the model dominates, inspect token counts and repeated calls; if retrieval dominates, inspect returned volume and retrieval stages. For a successful request, explain the longest observed interval and missing intervals rather than inventing an error.

The bundled CLI queries App Insights using response/trace IDs from an actual response file.

```bash
python samples/trace_lab.py --input results/actual-responses.jsonl --app-id ACTUAL_APP_INSIGHTS_APP_ID --agent ACTUAL_AGENT_NAME
python samples/trace_lab.py --input results/actual-responses.jsonl --app-id ACTUAL_APP_INSIGHTS_APP_ID --agent ACTUAL_AGENT_NAME --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `trace_lab.py` | `--input` is the actual English response JSONL, `--app-id` is the Application Insights application ID, and `--agent` is the agent name to query. Replace the placeholders with values from your owned English environment. Reads identifiers from the file and prints a KQL plan. | No Azure query. Check that the time window and ID conditions refer only to your run. |
| 2. The same command with `--live` | Reads actual logs using the reviewed KQL. Limited to the last 24 hours and at most 200 rows; does not run new model inference. | Sends an Azure read request and records query results. Zero rows means correlation is unverified; do not fill in arbitrary IDs. Log-service usage terms apply separately. |

</div>

Print the KQL first and review its scope. It covers the last 24 hours, returns at most 200 rows, and does not retrieve raw tokens or full message bodies.
`app-id` is not an instrumentation key or connection string. Zero returned rows fail as **unverified correlation**;
do not relabel a request ID as a trace ID. Compare `contract.sha256` and version only when using L14 Hosted results; do not require that Hosted contract in the basic Prompt Agent JSONL.

Equal `input_rows` and `correlated_rows`, with empty `missing_case_ids`, establish **input-to-log correlation**. `model_response_spans_observed` and `request_trace_ids_observed` measure different observation layers. This CLI checks correlation, not bottlenecks or answer correctness. Read the query rows in the printed `Evidence:` file and the portal details, then fill the table with your own values.

### 4. Optional: Add client-side tracing

To see inside your own functions or external applications, add OpenTelemetry and your framework's instrumentation. VS Code Toolkit's local OTLP tracing can show development executions without cloud logs.

Do not enable raw collection of sensitive inputs/outputs by default. Correlate using trace/span IDs and collect only the minimum business metrics needed. Also check that you are not exporting server-side and client-side traces twice.

### 5. Conditional: Monitoring and continuous evaluation

Use the Monitoring dashboard and continuous evaluation in nonproduction after checking their Preview scope. Start with a small sampling rate, a few evaluators, and separate judge quota.

For example, sampling 5% of 1,000 requests per day initially selects 50 for evaluation. Evaluator count, retries, and multiple turns further affect cost. **Do not calculate total cost from the sampling rate alone.**

User thumbs-up/down feedback is a useful signal, not a ground-truth label. Follow the loop: failed trace → anonymization and review → evaluation data → prompt revision → reevaluation. Check the Preview status of traces-to-dataset, cluster analysis, and related capabilities.

## Success criteria

Link one of your runs' **response/trace IDs, version, observed operations/durations, judgment, and next action**. If you only read the example, record **design complete / actual trace unverified**. Missing traces are not “no errors.”

## Troubleshooting

| Symptom | Inspect first | Next action |
| --- | --- | --- |
| Cannot open JSONL / no actual IDs | The `Responses:` path and one file row | Select the L05/L06 output, not example IDs or L08 comparison JSON |
| 403 | Log-read permissions, separate from project roles | Request access to the exact App Insights/Log Analytics scope from the administrator |
| Zero rows / partial correlation | Project connection, run time, 24-hour window, collection delay | Compare scope/IDs before any new model request. If still absent, leave correlation unverified |
| Parent exists but function/content is absent | Instrumentation and sensitive-content read permissions | Record JSONL evidence and observation limits; do not indiscriminately enable content recording |

## Cleanup

Record only the trace IDs needed for diagnosis and minimal evidence. Set log retention, decide whether raw content is included and who can access it, and stop unnecessary continuous evaluation.
