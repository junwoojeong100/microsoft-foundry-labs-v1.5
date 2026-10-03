> **Check these first:** The selected English profile, the current project and endpoint, the calling identity, and the SDK environment used to run the command.

## Stuck before connecting to Azure?

| Symptom | What to do now |
| --- | --- |
| Unsure where to enter a command | Open the lab folder in VS Code and choose **Terminal → New Terminal**, not the browser address bar |
| `python3` / `python3.13` not found | Check the Python installation/version. On Windows use L01's `py -3.13` path |
| `can't open file` / `No such file or directory` | Check that the opened folder contains `samples`, `data`, and `requirements.txt` together; do not run from inside `samples` |
| Python `>>>` prompt or `SyntaxError` | Enter `exit()` and run commands in the terminal. Paste questions, JSON, and `.env` settings only where the step specifies |
| Windows error for `source` / `curl --fail` | Use L01's `.venv\Scripts\python.exe` and use `curl.exe` for HTTP checks |
| No project in the portal | Confirm the supplied account, organization, and project with the instructor; do not create a new project or subscription |

## A 60-second diagnostic sequence

1. Classify where the error occurred: **local installation / management plane / model call / agent / tool / evaluation / logs**.
2. Record the time, status/error code, and request/response ID. Do not record tokens or API keys.
3. Read existing output, files, and settings first. Reproduce a new paid request only after confirming its need and scope. Do not recreate every feature at once.

## Troubleshooting by symptom

The [actual bilingual comparison](../../validation/current/quality.json) shows a limited Korean relevance increase and tied English native metrics on GPT-6 Sol. Do not transfer one language's result to the other. Use the [measurement report](../../validation/current/report.json) to distinguish preserved failures, completed collection, and actual scores; neither service completion nor missing numeric results count as a valid score.

| Symptom | Check first | Next action | Do not |
| --- | --- | --- | --- |
| 401 | CLI login, tenant, and token audience | Sign in to the correct tenant and use authentication appropriate to the service | Paste tokens into chat or screenshots |
| 403 | Data-plane roles, agent/project identity, and network | Check the relevant scope and private network path separately | Give everyone subscription Owner |
| 404 | Project endpoint, model deployment name, and agent version | Copy the values again from the portal | Assume the model ID and deployment name are the same |
| 429 | RPM/TPM, judge quota, and concurrency | Reduce input/concurrency, honor Retry-After, and use bounded retries | Invoke repeatedly in an infinite loop |
| Deployment fails despite available quota | Capacity, deployment type, region, and access restrictions | Consider another approved deployment combination | Ignore country/region policies |
| Resource group shows an inherited diagnostic-policy failure | Whether the failing target is the external governance workspace rather than owned lab infrastructure | Preserve the warning and refer it to the governance owner; this English run's own foundation/observability deployments succeeded | Hide the failure or repair out-of-scope policy/workspace resources |
| Connection timeout | DNS, proxy, private endpoint, and firewall | Check from an environment inside the approved VNet | Enable public access just to pass |
| Remote Hosted request times out before the server budget | Invocations client version and recorded session state | Use the corrected 310-second local/remote client timeout with the unchanged 300-second server budget; inspect existing evidence before a bounded retry | Assume the old 60-second timeout proves nonexecution or extend requests indefinitely |
| `PublicNetworkAccessDisabled` | Whether execution is taking place on an approved path | Use a supported path such as a VPN or development VM | Disable resource security |
| `ImportError` / missing module | Python path, venv, and requirements | Install/run using that venv's Python | Indiscriminately reinstall with global pip |
| Dependency conflict | Mixed core/advanced environments | Separate the two requirements sets and venvs | Force an upgrade of just one package to the latest version |
| `.env` error | Names, format, placeholders, and the separate English checkout | Use `.env.example` and the settings required by the current module | Add an API key or copy Korean-run private configuration |
| English guide produces Korean inputs | `FOUNDRY_LAB_LANGUAGE`, explicit file paths, and packaged `lab-profile.json` | Reselect `en` in this terminal as in L01, use `data/en/` files, and rebuild an English package if necessary | Assume the browser language changes runtime data or overwrite a Korean package/receipt |
| Agent claims tool success without a call | Actual tool calls and traces | Inspect the prompt and tool registration | Trust the natural-language answer alone |
| Function tool stalls | Whether the client execution loop exists | Use the SDK runner or move to Hosted | Expect the portal to execute a local function |
| Hosted output has multiple JSON objects or is `incomplete` | Pending function-call context and completed tool results | Use the bounded two-round tool phase followed by the separate tool-free answer; preserve the original failure | Raise the 2048-token limit, drop strict JSON/citations, or call one corrected case a full dev pass |
| `duplicate_tool_request` for a draft | The rejection's `duplicate_of` and original successful call | Verify exactly one executed draft and preserve both records | Count the rejected repeat as another draft or hide its error |
| No file search results | Ingest status, store ID, and file contents | Check the file → store → agent connection order | Treat upload completion as indexing completion |
| Correct answer without citations | Actual annotations and original text | Preserve/display citations in the UI | Treat a filename string as evidence |
| Read-only `get_stock` ran in a no-tool case | The frozen case's forbidden-tool contract and actual call log | Retain the failed result even when no draft or external business action occurred | Redefine read-only calls as non-tools or relax the case after the holdout |
| Native judge accepts a refusal but the gate fails | Required policy evidence and code-based checks | Preserve missing-evidence failures, including critical safety failures, and keep release blocked | Assume refusal wording alone satisfies the contract |
| `Model-selected citations omitted required policy evidence` on an FX/branch question | The frozen case oracle versus keyword-derived runtime obligations | Diagnose “approved exchange rate” and negated draft wording as potential over-broad intent matching; correct a new candidate and repeat complete dev validation | Auto-fill references, weaken the oracle, rewrite the failed response, or open holdout after an incomplete dev run |
| Optimizer list API returns HTTP 500 | Exact project, retained service error and known job receipts | Use bounded GET for recorded job IDs and scoped SDK session readbacks; explicitly leave the global inventory unverified | Claim all project jobs are idle from a failed list response |
| Optimizer reports “perfect scores” but has errored rows | Full native `result_counts` and all downloaded output items | Preserve errored or missing rows as operational failure; distinguish task-adherence scoring from the business release gate | Average only successful rows or use service success text to override errors |
| Recorded candidate differs from its development freeze | Runtime, active prompt, judge, policy, and dev hashes | Preserve the seal and start a new experiment if code must change; the new exam is still not release evidence | Reseal the same exam around changed code or resample consumed exam cases |
| Optimizer hits its job deadline | Preserved `optimizer_progress`, `optimizer_timeout`, terminal/outcome and cleanup receipts | Distinguish deadline expiry from an established service-side cause; retain the original limit and inspect bounded cleanup | Automatically extend the job, lower gates, or call baseline-only scoring an improvement |
| More sessions appear after Optimizer cancellation | SDK session inventory, exact baseline/draft version, candidate ID and resolver ownership | Use six bounded reconciliation sweeps and same-ID stopped readbacks; retain unknown/unsettled sessions as unverified | Rely only on CLI listing, a `cand_` prefix, or the terminal timestamp cutoff |
| IQ permission leak | ACL metadata, user token, and server validation | Trace permissions from the source through query time | Control access only through prompts |
| MCP does not continue after approval | Approval request ID and the same conversation | Return the correct approval response | Automatically approve every request |
| Toolbox 403 | Developer identity, agent identity, and user delegation | Give the actual calling principal minimum permissions | Assume creator permissions are inherited automatically |
| OpenAPI MCP argument validation fails | The inspected tool's `inputSchema` | Keep `api-version` at the top level and put `search`, `top`, and `select` inside `body`, as in L07 | Flatten the body fields or substitute the Microsoft Learn `query` schema |
| Evaluation is `Partial` | Required evaluator fields, judge quota, and tool runtime | Identify and rerun the failed evaluator | Average only the completed subset |
| Missing/`null` result at the automated gate | Incomplete code/native evidence or evaluator errors | Inspect the preserved originals and rerun only the failed evaluator under unchanged criteria when justified; human review remains optional | Fill values with `true`, lower gates, or recollect the sealed holdout until it passes |
| No trace | App Insights connection, permissions, time range, and ingestion delay | Compare the existing response ID and query scope first | Repeated model calls or treating an empty screen as proof of no errors |
| Request correlation is complete but model spans are partial | Span type, bounded query scope, and the request/model distinction | Report the observed English scope: 10/10 request trace IDs, only 7 model-response spans in the mixed query | Claim all 10 model spans were observed or invent missing spans |
| Memory is not visible | Scope, new conversation, and update delay | Inspect the item/retrieval directly | Judge memory solely from output formatting |
| No response after publishing to Teams | Active version, Bot route, and tool execution location | Test publishing and actual invocation separately | Treat an app listing as final success |
| Costs keep increasing | Routines, voice, continuous evaluation, Search/PTU/runtime | Separate active, idle, and fixed costs | Only close the browser |
| Cleanup fails | Receipt endpoint, permissions, and ownership | Record the remaining IDs and retry | Delete the entire resource group |

## Administrator handoff

The inherited external diagnostics dependency remains for its governance owner to confirm. This instruction update does not query the external workspace, change policy/access, or perform remediation. Keep exact resource/correlation IDs in approved private channels and never hide a prior failure or add broad roles just to pass a lab.

## Safe information to include in a support request

```text
Module:
Execution method: portal / SDK / hosted / design
SDK environment: core or advanced
Lab profile: en
Data root / packaged language: data/en / en
Error time and time zone:
Status / error code:
Response or request ID:
Expected result:
Actual result:
Most recent change:
Items already checked:
Paid resources that may still remain:
```

Redact internal endpoints and tenant/subscription IDs as appropriate for the audience as well. Do not attach secrets, tokens, or real user data.

## When the screen differs from the documentation

First check the new/Classic portal, Preview access, tenant rollout, region, and RBAC. If button names differ, consult official sources based on **the resource and action you intend to create or perform**. Compare the English screenshots with their [capture log](../../content/portal-screenshots.en.json); do not treat the earlier Korean images as current English evidence. Tasks, fields, and completion criteria take precedence over matching a screenshot.
