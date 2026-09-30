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

### 2. Create and find a new run

Send one more synthetic question and record the response ID and time. Allow time for collection, then search in Traces. Check both the selected project and time range.

![The live Prompt Agent Traces screen. Trace/Conversation/Response views, ID search, version/status/date-range filters, and duration, token, and estimated-cost columns are visible. Trace IDs are masked.](../../assets/portal/06-traces.png)

**Reading the screen:** In **Build → Agents → your agent → Traces**, first set **Date range** and **Version**. Search using your own trace/conversation/response ID, then open a row to inspect individual operations. **Completed** means execution finished, not that the answer was correct. This image lists preserved traces from earlier lab runs; no new request was made for the capture.

Find the following in the trace.

| Evidence | What to record |
| --- | --- |
| Agent/model execution | Name, version, and total duration |
| Retrieval call | Actual returned documents and whether results were empty |
| Function/MCP call | Tool name, arguments, and errors |
| Model usage | Input/output tokens and available cost indicators |
| Conversation/response | The link between the user's request and the execution |

### 3. Distinguish three types of failure

**Incorrect policy answer:** Was the correct document retrieved? If not, investigate retrieval. If it was, investigate instructions, the model, or answer synthesis.

**Slow answer:** Break total latency into model, retrieval, tool, and network/wait stages. Do not prescribe a model change when the tool is slow.

**The function succeeded but the answer failed:** Check whether the tool output was returned to the same conversation/call ID and whether the final output completed.

The bundled CLI queries App Insights using response/trace IDs from an actual response file.

```bash
python samples/trace_lab.py --input results/실제-responses.jsonl --app-id 실제-AppInsights-app-ID --agent 실제-agent-name
python samples/trace_lab.py --input results/실제-responses.jsonl --app-id 실제-AppInsights-app-ID --agent 실제-agent-name --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `trace_lab.py` | `--input` is the actual response JSONL, `--app-id` is the Application Insights application ID, and `--agent` is the agent name to query. Replace the Korean “actual ...” placeholders with your own values. Reads identifiers from the file and prints a KQL plan. | No Azure query. Check that the time window and ID conditions refer only to your run. |
| 2. The same command with `--live` | Reads actual logs using the reviewed KQL. Limited to the last 24 hours and at most 200 rows; does not run new model inference. | Sends an Azure read request and records query results. Zero rows means correlation is unverified; do not fill in arbitrary IDs. Log-service usage terms apply separately. |

</div>

Print the KQL first and review its scope. It covers the last 24 hours, returns at most 200 rows, and does not retrieve raw tokens or full message bodies.
`app-id` is not an instrumentation key or connection string. Zero returned rows fail as **unverified correlation**;
do not relabel a request ID as a trace ID to fill the gap. Also compare the Hosted response's `contract.sha256` and version.

### 4. Optional: Add client-side tracing

To see inside your own functions or external applications, add OpenTelemetry and your framework's instrumentation. VS Code Toolkit's local OTLP tracing can show development executions without cloud logs.

Do not enable raw collection of sensitive inputs/outputs by default. Correlate using trace/span IDs and collect only the minimum business metrics needed. Also check that you are not exporting server-side and client-side traces twice.

### 5. Conditional: Monitoring and continuous evaluation

Use the Monitoring dashboard and continuous evaluation in nonproduction after checking their Preview scope. Start with a small sampling rate, a few evaluators, and separate judge quota.

For example, sampling 5% of 1,000 requests per day initially selects 50 for evaluation. Evaluator count, retries, and multiple turns further affect cost. **Do not calculate total cost from the sampling rate alone.**

User thumbs-up/down feedback is a useful signal, not a ground-truth label. Follow the loop: failed trace → anonymization and review → evaluation data → prompt revision → reevaluation. Check the Preview status of traces-to-dataset, cluster analysis, and related capabilities.

## Success criteria

You have found one new run in the traces and can explain an actual bottleneck or failure point using evidence. Do not record a missing trace as “no errors.”

## Troubleshooting

Project permissions alone may not permit log queries. Check read access on Application Insights/Log Analytics, connection status, collection delay, and time filters. Protected tables may require separate permissions.

## Cleanup

Record only the trace IDs needed for diagnosis and minimal evidence. Set log retention, decide whether raw content is included and who can access it, and stop unnecessary continuous evaluation.
