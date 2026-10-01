> **What you will build:** Package this repository's purchasing assistant with English synthetic data and invoke it locally and in Azure.

## Objectives

A Prompt Agent uses instructions and service tools; a **Hosted Agent runs code you manage yourself**.
The bundled implementation uses the **Invocations protocol** to exchange structured requests and evidence without changing their form.
Do not describe this as validation of the Responses, Voice, or Teams protocols.

## Concepts and lab map

**What you will try:** Packaging custom agent code, running a local server, deploying to managed Hosted infrastructure, and invoking a pinned version.

**What is it, and why does it matter?** For a Prompt Agent, the service executes the declared instructions and tools; for a Hosted Agent, a managed environment runs server code that you wrote. To address the fact that L06's local functions do not run automatically from Teams or a schedule, you need to move the executor to a server. The data, dependencies, environment variables, and input/output protocol must match—not just the code. This is why you verify deployment success separately from a successful business response.

**How do you use it?** Inspect the local package's files and hashes, start the server, and send a request that follows the same contract. Deploy only to a prepared project and invoke a numerically specified version. Compare the function results, citations, and runtime hash in the response with the local contract. The Responses adapter is a separate interface for Optimizer integration; do not confuse it with the default Invocations path.

**Where do you run it?** [azure.yaml](../../azure.yaml) defines the services, entry point, and protocol; [build_hosted.py](../../scripts/build_hosted.py) defines the bundled files; [hosted/main.py](../../hosted/main.py) is the server entry point; and [hosted_runtime.py](../../samples/hosted_runtime.py) is the business engine. Check Hosted/Prompt types and versions in the portal, and run and deploy the code from a terminal.

## Prerequisites

This lab is based on the Search service/index and model from L13, Python **3.13**, azd **1.34.0**,
and `azure.ai.agents` **1.0.0-beta.10**.
Check the official Hosted documentation for supported capabilities and regions. Do not require learners to be Owners of a particular subscription.
Distinguish the deployment operator from learners using an already prepared project.

```bash
python3.13 -m venv .venv-live
source .venv-live/bin/activate
python -m pip install -r requirements-hosted.txt
python -m pip check
python scripts/check_sdk.py
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `python3.13 -m venv .venv-live` | Creates a Python 3.13 virtual environment for Hosted. | Creates a local directory. Do not mix it with the advanced MAF environment. |
| 2. `source .venv-live/bin/activate` | Selects the new environment's Python for the current shell. | Changes only the current terminal; no Azure resources are touched. |
| 3. `pip install -r requirements-hosted.txt` | Installs the pinned dependencies for the Hosted server and SDK. | Package downloads and local installation. No model inference. |
| 4. `pip check` | Checks for conflicts between the installed packages' dependency requirements. | A read-only check. Do not proceed if it reports errors. |
| 5. `check_sdk.py` | Locally checks the SDK classes and call contracts used by the samples. | An import/API contract check, not evidence of remote deployment or model quality. |

</div>

The `.venv-advanced` environment for the MAF lab is separate. Do not simply merge incompatible `azure-ai-projects` constraints. Keep `FOUNDRY_LAB_LANGUAGE=en` selected in every terminal and use only this English checkout's configuration and receipts.

## Steps

### 1. Build the package before making Azure calls

```bash
python scripts/build_hosted.py
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `build_hosted.py` | Generates a deployment directory, ZIP, and file-hash manifest from checked-in runtime code and the selected English policies, inventory, and instructions. Binds `en` in the generated `lab-profile.json`. | Changes only this English checkout's local `.build/` artifacts. No Azure deployment. The archive does not include `.env` or evaluation reference answers. |

</div>

This creates `.build/contoso/` and `.build/contoso-code.zip`.
The Responses profile for Optimizer is generated separately in `.build/contoso-responses/`.
The default Invocations and Optimizer Responses builds are separate; each needs its own execution evidence.
Only purchasing policies, inventory, instructions, runtime code, profile metadata, and pinned dependencies are included.
The package excludes `.env`, authentication material, evaluation reference answers, existing results, and personal environment files.
Check `language=en` in `lab-profile.json` and the language, per-file hashes, and runtime contract in `package-manifest.json`. The package keeps its bound language at runtime and rejects a conflicting profile; a browser-language change cannot switch a deployed package's corpus. Rebuild from the selected English profile before deployment rather than reusing a Korean ZIP.
There is no need to clone an external sample repository.

### 2. Run and invoke locally

In the server terminal, run the following bundled helper. It passes only approved, non-secret values
from the L01/L13 `.env` and `results/search.json` to the child process.

```bash
python scripts/run_hosted_local.py
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `run_hosted_local.py` | Starts the default Invocations server on loopback port 8088 and passes safe environment settings to the child process. | Keep the server terminal open. Even when execution is local, real requests can use Azure models and search. Stop it with Ctrl+C when finished. |

</div>

In another terminal, reselect L01's `FOUNDRY_LAB_LANGUAGE=en` and the Hosted Python environment in the same English checkout:

```bash
curl --fail http://127.0.0.1:8088/readiness
python samples/hosted_client.py invoke --local
python samples/hosted_client.py invoke --local --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Run these in a second terminal.

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `curl --fail .../readiness` | Reads the local server's readiness endpoint. `--fail` treats HTTP errors as failures. | Checks server connectivity; it is not a purchasing question or model call. |
| 2. `invoke --local` | Selects the local target but prints only a plan because `--live` is absent. | No business request to the server or Azure inference. `--local` alone does not authorize a real invocation. |
| 3. `invoke --local --live` | Sends a real synthetic purchasing request to the local server. `--live` authorizes the cost of the model/Search calls behind the server. | Inspect the response JSONL and the function, citation, and contract checks. Do not label local results as a successful Azure Hosted deployment. |

</div>

**The local server also uses real Azure models and search, so invocations incur charges.**
The default binding is loopback; do not expose this unauthenticated development server externally.
Each request is split into **at most two tool rounds → a separate tool-free, evidence-based answer → source correspondence check**.
Each tool-round output and the answer remain limited to **2048 tokens**; the source check remains limited to 512 tokens.
The limits remain **8 tool calls, 12 requests, and a 300-second server budget**, with SDK retries at 0. Local and remote Invocations HTTP clients both use a **310-second timeout**; the remote client's previous 60-second timeout was inconsistent with the local client and server budget. A longer client wait does not authorize extra requests or establish a successful answer.

The current engine performs question-specific search and retrieves the 13 sections of the small synthetic policy corpus **before** running the model.
It does not wait for the model to select a search function. Internally, the answer is `answer`/`citation_ids` JSON;
only the sections the model selects from the actual returned results are rendered as citations. Missing search results or citations are errors, not successes.
In `tool_calls`, `execution=server_required` records a real server-side search; it does not pretend the model called it.
The current runtime requires explicit permission for inventory calls and rechecks every attempted business tool. Missing or invalid draft quantities do not authorize an unrequested lookup. Read-only calls are still tool execution.
Both packages now load the current `agent-v2.txt`. Its improved answer procedure is not a new Azure deployment or quality pass; inspect the [current status](../../validation/current/instructions.json) before making that claim.

Use the actual service-issued deployment version, not the instruction number. When a session is already bound to a version, invoke it with `--session-id` only; combining that flag with `--version` is rejected by azd.

The tool-execution stage is skipped when no business tools are authorized. Otherwise it does not force an answer JSON format; a second bounded round lets the model request a draft after obtaining stock information.
The answer-only stage uses a fresh input built from the user's question, actual retrieved documents, function definitions, and recorded tool results/errors—not pending function calls or planning text. It has no tools available and must produce exactly one strict `answer`/`citation_ids` JSON object.
Do not publish a statement of intent to call a tool as an answer or as execution evidence.

Draft-tool arguments must be tied to a SKU explicitly provided by the user and one unambiguous integer quantity.
Even if the model fills in a missing quantity with 1 or reduces 11 items to 10, the code rejects the call before execution.
If the same SKU/quantity draft has already succeeded in this turn, a repeated request is rejected before execution with `duplicate_tool_request` and `duplicate_of` pointing to the original call ID. Preserve the original successful result and the rejection separately; do not count the rejection as a second draft or hide it as a successful repeat.
The answer stage also receives the actual function definitions so that it does not confuse the tool's 1–10 input constraint with company policy.
The final source-check stage selects evidence using only the actual retrieved material and the written answer,
and the actual selections from both models are displayed together. Required draft/approval/authority evidence must be selected by the model; missing selections are not filled in automatically. The original answer and the response IDs for source selection are preserved separately.

### 3. Deploy only to a prepared project

![Build → Agents in contoso-workshop-en. Compare Prompt/Hosted types and actual numeric versions for the separate English deployments.](../../assets/portal/en/03-agents.png)

**Read the screen:** Use **Type** to distinguish Hosted/Prompt and **Version** to identify the code/definition version. Open the name to inspect the deployment settings and protocol, and compare the version with CLI `show`. The version numbers in the image are examples from the captured environment, not values to copy. **Running does not by itself establish whether individual session compute is active, what the total cost is, or whether business quality checks passed.**

If the administrator created the environment using the bundled IaC from L01:

```bash
python scripts/configure_hosted.py
azd deploy contoso-purchasing --no-prompt
azd ai agent show contoso-purchasing --output json
python scripts/runtime_roles.py --agent contoso-purchasing --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Perform these only within the deployment operator's approved scope.

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `configure_hosted.py` | Binds the project, region, model, and Search values from the owned environment's receipt to the azd environment. It does not automatically discover and select another project. | Changes local azd environment settings. For a separately provided project, use the manual environment configuration path below. |
| 2. `azd deploy contoso-purchasing --no-prompt` | Performs a real deployment of only the specified service in `azure.yaml`. `--no-prompt` skips interactive confirmation; it is not a dry run. | Remote deployment, a new immutable version, and possible charges. This CLI does not require `--live`. |
| 3. `azd ai agent show ... --output json` | Reads deployed agent metadata as structured JSON. | Record the numeric version and target project. No business request has been sent yet. |
| 4. `runtime_roles.py --agent ... --live` | Configures the minimum scoped roles for project access, Search reads, and model calls on the owned agent's runtime identity. | An administrator permission change. This is separate from the developer's signed-in roles; it does not authorize arbitrary agents or subscription-wide roles. |

</div>

If learners receive a separately provisioned project, use `azd env new` and `azd env set` to configure
`AZURE_AI_PROJECT_ID`, `AZURE_AI_PROJECT_ENDPOINT`, `AZURE_SUBSCRIPTION_ID`,
`AZURE_TENANT_ID`, `AZURE_RESOURCE_GROUP`, **`AZURE_LOCATION`**, and the model/Search values.
These are environment bindings, not credentials. Keep the English `.azure/` environment separate from all Korean-run settings and keep `FOUNDRY_LAB_LANGUAGE=en` selected while building/configuring. Do not print the full output of `azd env get-values` to public logs.
`azd env new` creates a local environment name, and `azd env set` stores one configuration value in that environment. Neither command deploys a model by itself, but they change the target of a later `deploy`, so compare the project and subscription before setting values. `get-values` reads the entire configuration; it is not a check of lab results.

`AZURE_LOCATION` is the project's actual region name. Code deployment fails if this value is missing.
The `scripts/configure_hosted.py` path uses an ownership receipt created by the bundled administration script.
When using a separate project supplied by an instructor, configure the azd environment with that project's actual values.

The bundled `azure.yaml` uses **code deployment**; Docker/ACR is not required.
Do not casually run `azd provision` with this file. Resource creation belongs to the L01 administration path.
Each deployment creates a new immutable version. Grant the agent runtime identity only the relevant Search read role.

The native optimizer in L20 currently supports **only the Responses protocol**.
An optional `contoso-purchasing-responses` adapter using the same business engine is also bundled.
Deploy that service explicitly only when needed, and record its separate agent/version/identity.
Do not use success in the default Invocations lab as execution evidence for this adapter.

```bash
python scripts/run_hosted_local.py --protocol responses --port 8089
azd deploy contoso-purchasing-responses --no-prompt
python scripts/runtime_roles.py --agent contoso-purchasing-responses --live
azd ai agent invoke contoso-purchasing-responses "What is the price cap for a standard laptop?" --protocol responses --version ACTUAL_NUMERIC_VERSION
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — This is the separate Responses path for when Optimizer is needed.

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `run_hosted_local.py --protocol responses --port 8089` | Runs the Responses adapter on a different port from the default Invocations server. Keep this server in its own terminal and run the deployment commands in another. | Starts a local server. Stop it with Ctrl+C after use. The remote invocation below does not call this local server. |
| 2. `azd deploy contoso-purchasing-responses --no-prompt` | Performs a real deployment of the Responses service/code rather than the default service. | Creates a separate agent/version; charges may apply. Do not reuse quality evidence from the default Invocations service. |
| 3. `runtime_roles.py --agent contoso-purchasing-responses --live` | Configures data/model roles within the owned scope for that separate runtime identity. | A real permission change requiring administrator approval. |
| 4. `azd ai agent invoke ... --protocol responses --version` | Sends the English question to the exact remote numeric version. `--protocol responses` selects the request/response contract. Replace `ACTUAL_NUMERIC_VERSION` with the version number from your English Responses deployment. | Real Hosted, model, and search charges. Check the completion event, content, and session state after invocation. |

</div>

Pass the question directly to the Responses CLI. Do not wrap a JSON request file as the question text.
If the raw response is SSE, check for the `response.completed` terminal event; output deltas alone do not establish success.

### 4. Invoke the exact remote version

```bash
python samples/hosted_client.py invoke --version ACTUAL_NUMERIC_VERSION --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `invoke --version ... --live` | Creates a new session for the exact numeric version of the default `contoso-purchasing` Invocations service and sends one English synthetic question. Replace `ACTUAL_NUMERIC_VERSION` with your English deployment's version number. The projects in azd and `.env` must match. | Real Hosted, model, and Search charges, plus response evidence. Confirms that compute for the same session is stopped in `finally`. Does not delete the agent. |

</div>

Use the actual version from `show`. Invoke it in a new version-bound session and
**stop only its compute** in `finally`. The response, internal model response IDs, tool call IDs, citations, and trace ID are returned.
A mismatch between the local package contract and remote contract causes failure.
If there is no trace ID, leave it recorded as not collected rather than guessing.

Deployment and session management use azd. To collect the response body, the bundled Invocations client sends
**an Entra-authenticated HTTP JSON request to the endpoint returned by the service**. This addresses an observed case in which
extra output appeared in azd stdout in CI; do not assume CLI display output is a stable API JSON contract.

### 5. Verify the basic tools in action

The question is “Check the policies and stock for 2 NB-14 laptops and create only a purchase request draft.”
Inspect the arguments and results for `search_policies`, `get_stock`, and `prepare_purchase_request`.
The total must be **KRW 2,900,000**, with both approval roles and `order_submitted=false`.
When connecting a separate Toolbox, retain L07's authentication principal and one-time approval policy.

## Success criteria

You have separately verified packaging, server startup, the local business result, deployment, and the remote business result for the same version.
Hashes, tools, and citations are connected; a successful deployment alone is not labeled a quality pass.

The [current instruction status](../../validation/current/instructions.json) separates the edited v2 from the latest actual deployment evidence. A working package or a historical native score does not validate a new instruction edit.

## Troubleshooting

For health failures, check the entry point/dependencies; for 502, the preserved upstream error; and for 403,
the runtime identity's model/Search roles first. For a 424 cold start, inspect logs and retry only a bounded number of times.
Do not turn an error message into a normal answer with HTTP 200.

For multiple JSON objects or `incomplete` output, inspect the tool/answer boundary and actual results rather than increasing the 2048-token limit or weakening citation checks. A remote timeout does not prove that the server did nothing: inspect existing evidence and the recorded session state before any separately approved action.

## Cleanup

Stop the local server with Ctrl+C in the terminal where you started it. For interrupted runs,
use `python scripts/stop_sessions.py` to stop **only recorded sessions**.
The agent/version/session files and Azure resources remain. Record the remaining storage, log, and Search costs in L12.

Hosted's `/app` is read-only. Write remote raw evidence only to the session's `$HOME/.contoso/evidence`,
not to the code directory. Do not include it in the package.
