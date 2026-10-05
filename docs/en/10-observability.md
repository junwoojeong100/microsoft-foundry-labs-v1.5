> **What you will build:** An evidence-based explanation of “Why was it wrong?”, “Why was it slow?”, and “How much did it use?” for a single run.

<div class="lab-brief" markdown="1">

**Format:** Query and interpret your own agent execution using L01's telemetry connection.

**Start here:** Find the same L05/L06 execution in Traces using its response ID, time, and agent version.

**What to check:** Record observed operations, durations, and next actions. Without log access, use the synthetic example and leave actual tracing unverified.

</div>

## Objectives

**Evaluation shows whether it was good, Trace shows what happened, and Monitoring shows how behavior changes over time.**

## Concepts and lab map

**What you will try:** Read the operations and durations for one question you already ran.

**What is it, and why does it matter?** A trace records one request; a span is an operation such as retrieval, a model call, or a tool call. Find the slow operation rather than judging only the total time. No logs means unverified, not error-free.

**How do you use it?** Find an L05 or L06 execution by response ID, time, and version. Read its operation durations and status, then choose one cause to investigate.

**Where do you run it?** Use portal **Traces**; [trace_lab.py](../../samples/trace_lab.py) is an optional query path. Without log access, practice interpreting the synthetic timing table below.

## Prerequisites

Use the Application Insights connection/read access you prepared in L01 and your L04–L06 results. Application Insights collects/queries Azure execution logs; ingestion and retention have costs.

<details class="optional-path" markdown="1">
<summary>If not connected yet: finish your project's telemetry setup</summary>

Inspect receipt `monitoring` and the portal connection first. If absent, follow **L01 step 5** to plan/create Log Analytics, App Insights, and the connection in your owned group. Do not recreate existing resources. Thirty-day retention and daily ingestion limits are not hard total-spend caps.

Inspect your own connection under **Agents → Traces → Connect** or **Manage → Project details → Connected resources**, without replacing an existing binding. Telemetry is collected **after connection**, not retroactively for earlier requests.

</details>

## Steps

### 1. Check the log-collection connection

Open your agent's **Traces**. If only **Connect** appears, compare the connection and current project. For 403, inspect **IAM → View my access** on your App Insights/Log Analytics resources and assign the required minimum scoped roles if permitted. Otherwise block the query and record actual tracing unverified.

Server-side tracing for Prompt/Hosted agents can begin after connection without code changes. It does not automatically trace every detail inside your client-side functions.

### 2. Find and correlate one of your runs

First reuse an L05/L06 run collected after tracing was connected. If none exists, send one approved synthetic question and record its response ID/time. Do not repeatedly resend questions because the list is empty.

| Required value | Where to obtain it | Check the binding |
| --- | --- | --- |
| Response JSONL | The `results/contoso-lab-…-responses.jsonl` path printed after `Responses:` by the L05/L06 SDK | Use L06's `read-result` for record/response IDs and agent/version. The source fields are `id`, `response_id`, `agent_name`, and `configuration.agent_version` |
| Agent name/version | That row, or the configuration of the agent you invoked in the portal | Do not substitute the L08 evaluation agent or L12 Hosted name |
| Application Insights app ID | Your `results/azure-environment.json` → `monitoring.appId.value`, or that resource's Overview | Match `monitoring.appInsightsId.value` with the actual project connection. Do not copy keys/connection strings. |

With portal-only results, completing the **portal path** using the response ID is sufficient. Do not fabricate a JSONL file or pass L08's comparison JSON to this JSONL input. The CLI reads only the last 24 hours; read older evidence within the portal's approved retention scope or leave correlation unverified.

![Execution-list example. Locate ID search, version/status/date filters, durations, tokens, and estimated costs in Prompt Agent Traces.](../../assets/portal/en/06-traces.png)

**Reading the screen:** In **Build → Agents → your agent → Traces**, first set **Date range** and **Version**. Search using your own run's trace/conversation/response ID, then open a row to inspect individual operations. **Completed** means execution finished, not that the answer was correct.

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
do not relabel a request ID as a trace ID. Compare `contract.sha256` and version only when using L12 Hosted results; do not require that Hosted contract in the basic Prompt Agent JSONL.

Equal `input_rows` and `correlated_rows`, with empty `missing_case_ids`, establish **input-to-log correlation**. `model_response_spans_observed` and `request_trace_ids_observed` measure different observation layers. This CLI checks correlation, not bottlenecks or answer correctness. Read the query rows in the printed `Evidence:` file and the portal details, then fill the table with your own values.

#### Portal Traces and the actual correlation query

In the portal, use **Traces** to select your agent/version, time range, and response ID. The Python path reads the same IDs from JSONL, builds KQL, then sends one read query to Application Insights.

```python
rows = load_jsonl(args.input)
query = query_for(rows, args.agent)

result = rest.request(
    "POST",
    f"/v1/apps/{args.app_id}/query",
    {"query": query, "timespan": "P1D"},
)
report = correlation_report(rows, result)
```

| Portal value | Code input/use |
| --- | --- |
| Agent filter in Traces | `args.agent` |
| Response/trace IDs in request details | `response_id` / `trace_id` in `rows`, used as `responseIds` / `traceIds` in KQL |
| Selected Application Insights app | `args.app_id` (app ID, not a connection string) |
| Time range | `timespan="P1D"` and KQL restricted to the last 24 hours |
| Correlated rows | `correlation_report()` fields `correlated_rows` and `missing_case_ids` |

The code path **only reads telemetry** and does not call a model. Zero rows or missing IDs remain unobserved/failures; do not fill them from what appears on a portal screen.

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
| 403 | Log-read access is separate from project roles | Check minimum roles/scope in your App Insights/Log Analytics IAM; block the query without permission |
| Zero rows / partial correlation | Project connection, run time, 24-hour window, collection delay | Compare scope/IDs before any new model request. If still absent, leave correlation unverified |
| Parent exists but function/content is absent | Instrumentation and sensitive-content read permissions | Record JSONL evidence and observation limits; do not indiscriminately enable content recording |

## Cleanup

Record only the trace IDs needed for diagnosis and minimal evidence. Set log retention, decide whether raw content is included and who can access it, and stop unnecessary continuous evaluation.
