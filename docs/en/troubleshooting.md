> **Check these first:** The selected English profile, the current project and endpoint, the calling identity, and the SDK environment used to run the command.

<a id="troubleshooting-stuck-before-connecting-to-azure"></a>

## Stuck before connecting to Microsoft Azure?

| Symptom | What to do now |
| --- | --- |
| Unsure where to enter a command | Open the lab folder in VS Code and choose **Terminal → New Terminal**, not the browser address bar |
| `python3` / `python3.13` not found | Check the Python installation/version. On Windows use L01's `py -3.13` path |
| `can't open file` / `No such file or directory` | Check that the opened folder contains `samples`, `data`, and `requirements.txt` together; do not run from inside `samples` |
| Python `>>>` prompt or `SyntaxError` | Enter `exit()` and run commands in the terminal. Paste questions, JSON, and `.env` settings only where the step specifies |
| Windows error for `source` / `curl --fail` | Use L01's `.venv\Scripts\python.exe` and use `curl.exe` for HTTP checks |
| Packages disappear in a new terminal | Use [L01's new-terminal check](#l01-new-terminal), including the English profile. Do not reinstall packages into a different Python |
| `read-result` reports a file, format, or language error | Check L06's `Responses:` path, the `-responses.jsonl` ending, and English profile. Ownership receipts and L08 JSON use different formats; do not fix this with another paid call |
| No project in the portal | Compare your L01 account, tenant, receipt, and creation state; do not duplicate the environment or erase records |

## A 60-second diagnostic sequence

**First check whether failure is intentional.**

| Output or symptom | Interpretation and next action |
| --- | --- |
| `PLAN ONLY` / `plan_only=true` | Normal plan output, not live Microsoft Azure execution. Continue with the stated live command only after approval conditions are ready |
| L06 stock/quantity errors | Expected rejection for the specified failure inputs; record the error kind and continue |
| L07 `Approval required` | Expected unapproved-local-call rejection; compare it with the exact one-call approval command |
| Two initial L17 / three initial L18 test failures | Deliberate exercise defects; repair only `exercise.py` and rerun the same tests |
| Server does not return to an input prompt | Normal while waiting; check health/readiness in the second terminal, not the server window |
| Windows MCP JSON parsing error | Use L07's **Windows PowerShell block**; a JSON format error is not an approval rejection |

For other symptoms or an unexpected error kind, follow the diagnostic sequence below. Do not relabel a failure or repeatedly issue billable calls.

1. Classify where the error occurred: **local installation / management plane / model call / agent / tool / evaluation / logs**.
2. Record the time, status/error code, and request/response ID. Do not record tokens or API keys.
3. Read existing output, files, and settings first. Reproduce a new paid request only after confirming its need and scope. Do not recreate every feature at once.

## Troubleshooting by symptom

Inspect your own bilingual comparison files, keeping each language's results separate. Distinguish failed attempts, complete collections, and valid scores; neither service completion nor missing numeric results count as a valid score.

| Symptom | Check first | Next action | Do not |
| --- | --- | --- | --- |
| 401 | CLI login, tenant, and token audience | Sign in to the correct tenant and use authentication appropriate to the service | Paste tokens into chat or screenshots |
| 403 | Data-plane roles, agent/project identity, and network | Check the relevant scope and private network path separately | Give everyone subscription Owner |
| 404 | Project endpoint, model deployment name, and agent version | Copy the values again from the portal | Assume the model ID and deployment name are the same |
| 429 | RPM/TPM, judge quota, and concurrency | Reduce input/concurrency, honor Retry-After, and use bounded retries | Invoke repeatedly in an infinite loop |
| Deployment fails despite available quota | Capacity, deployment type, region, and access restrictions | Consider another approved deployment combination | Ignore country/region policies |
| Resource group shows an inherited diagnostic-policy failure | Whether the failing target is an external governance workspace or owned lab infrastructure | Preserve the warning and refer an external dependency to the governance owner | Hide the failure or repair out-of-scope policy/workspace resources |
| Connection timeout | DNS, proxy, private endpoint, and firewall | Check from an environment inside the approved VNet | Enable public access just to pass |
| Remote Hosted request times out | Client/server timeouts, logs, and recorded session state | Inspect the existing request and session before a separately approved, bounded retry | Assume a client timeout means the server did nothing or extend requests indefinitely |
| `PublicNetworkAccessDisabled` | Whether execution is taking place on an approved path | Use a supported path such as a VPN or development VM | Disable resource security |
| `ImportError` / missing module | Python path, venv, and requirements | Install/run using that venv's Python | Indiscriminately reinstall with global pip |
| Dependency conflict | Mixed core/advanced environments | Separate the two requirements sets and venvs | Force an upgrade of just one package to the latest version |
| `.env` error | Names, format, placeholders, and the separate English checkout | Use `.env.example` and the settings required by the current module | Add an API key or copy Korean-run private configuration |
| English guide produces Korean inputs | `FOUNDRY_LAB_LANGUAGE`, explicit file paths, and packaged `lab-profile.json` | Reselect `en` in this terminal as in L01, use `data/en/` files, and rebuild an English package if necessary | Assume the browser language changes runtime data or overwrite a Korean package/receipt |
| Agent claims tool success without a call | Actual tool calls and traces | Inspect the prompt and tool registration | Trust the natural-language answer alone |
| Function tool stalls | Whether the client execution loop exists | Use the SDK runner or move to Hosted | Expect the portal to execute a local function |
| Hosted output has multiple JSON objects or is `incomplete` | Pending function-call context and completed tool results | Inspect the tool outputs and final answer separately; retain the original error | Raise the output limit or disable JSON/citation checks just to pass |
| `duplicate_tool_request` for a draft | The rejection's `duplicate_of` and original successful call | Verify exactly one executed draft and preserve both records | Count the rejected repeat as another draft or hide its error |
| No file search results | Ingest status, store ID, and file contents | Check the file → store → agent connection order | Treat upload completion as indexing completion |
| Correct answer without citations | Actual annotations and original text | Preserve/display citations in the UI | Treat a filename string as evidence |
| Native judge accepts a refusal but the gate fails | Required policy evidence and code-based checks | Preserve missing-evidence failures, including critical safety failures, and keep release blocked | Assume refusal wording alone satisfies the contract |
| IQ permission leak | ACL metadata, user token, and server validation | Trace permissions from the source through query time | Control access only through prompts |
| MCP does not continue after approval | Approval request ID and the same conversation | Return the correct approval response | Automatically approve every request |
| Toolbox 403 | Developer identity, agent identity, and user delegation | Give the actual calling principal minimum permissions | Assume creator permissions are inherited automatically |
| OpenAPI MCP argument validation fails | The inspected tool's `inputSchema` | Keep `api-version` at the top level and put `search`, `top`, and `select` inside `body`, as in L07 | Flatten the body fields or substitute the Microsoft Learn `query` schema |
| Evaluation is `Partial` | Required evaluator fields, judge quota, and tool runtime | Identify and rerun the failed evaluator | Average only the completed subset |
| Missing/`null` result at the automated gate | Missing required results or evaluator errors | Inspect original results and required fields; keep unknown values unresolved | Fill values with `true` or lower the criteria |
| No trace | App Insights connection, permissions, time range, and ingestion delay | Compare the existing response ID and query scope first | Repeated model calls or treating an empty screen as proof of no errors |
| Request correlation is complete but model spans are partial | Span types, instrumentation, and query filters | Record request-correlation and model-span counts separately, then inspect missing spans | Treat the two counts as equivalent or invent missing spans |
| Memory is not visible | Scope, new conversation, and update delay | Inspect the item/retrieval directly | Judge memory solely from output formatting |
| No response after publishing to Teams | Active version, Bot route, and tool execution location | Test publishing and actual invocation separately | Treat an app listing as final success |
| Costs keep increasing | Routines, voice, continuous evaluation, Search/PTU/runtime | Separate active, idle, and fixed costs | Only close the browser |
| Cleanup fails | Receipt endpoint, permissions, and ownership | Record the remaining IDs and retry | Delete the entire resource group |

## Problems outside your permissions or scope

Inspect your resource state, effective roles, scope, and original error first. For organizational policy or resources outside your scope, use the permitted support channel. Share IDs only privately; do not bypass a failure with broader roles or unauthorized resource access.

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

First check the new/Classic portal, Preview access, tenant rollout, region, and RBAC. If button names differ, consult official sources based on **the resource and action you intend to create or perform**. Follow the step's tasks, fields, and success criteria rather than matching a screenshot.
