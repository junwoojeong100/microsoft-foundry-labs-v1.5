> **What you will build:** Verification of actual MCP/OpenAPI results—not just tool lists—along with Toolbox/Skill versions, authentication identities, and approval decisions.

## Objectives

**MCP is a connection protocol, OpenAPI is an HTTP contract, Toolbox is a versioned collection of tools,
and a Skill provides instructions for repeatable work.** A Skill is neither approval authority nor evidence of successful execution.

## Concepts and lab map

**What you will try:** A local HTTP API, an OpenAPI contract, MCP tool discovery and invocation, and optional Toolbox/Skill connections.

**What is it, and why does it matter?** OpenAPI describes the shape of HTTP requests and responses; MCP standardizes how clients discover and call tools. Toolbox lets you reuse multiple connections as a versioned collection, while a Skill supplies task instructions. These are not interchangeable names. As connections multiply, reproducing behavior and controlling access requires clarity about who called which tool with which arguments.

**How do you use it?** First compare HTTP responses with the source contract, then distinguish MCP tool listing from actual calls. Review the tool name and arguments before approving that single call. The cloud extension adds remote authentication and version pinning to the same concepts.

**Where do you run it?** The core exercise runs locally in two terminals. Compare the [HTTP server](../../samples/inventory_api.py), [OpenAPI contract](../../samples/inventory.openapi.json), [MCP server](../../samples/mcp_server.py), [client](../../samples/toolbox_lab.py), and [Skill source](../../data/skills/purchase-review/SKILL.md) to see the boundary between the protocol and business code.

## Prerequisites

Install `requirements-tools.txt` in the base Python environment.
The cloud steps require Search from L13 and the Search Index Data Reader role for the project managed identity.
**Only steps 1–2 below—local HTTP/OpenAPI and MCP—are required for the core course.**
Cloud Toolbox/Skills in steps 3–4 are optional extensions after preparing the L13 resources.
Core-course learners do not need to complete L13 first.

```bash
python -m pip install -r requirements-tools.txt
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `pip install -r requirements-tools.txt` | Adds MCP lab dependencies to the activated base virtual environment. `python -m pip` keeps the installer aligned with the current Python. | Downloads packages and changes the local environment only; no Azure tools are invoked. |

</div>

## Steps

### 1. Explore the local HTTP/OpenAPI contract

Start the server in the first terminal and leave it running.

```bash
python samples/inventory_api.py
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `inventory_api.py` | Starts an HTTP server that reads synthetic inventory at `127.0.0.1:8766`. It is normal for the shell prompt not to return immediately. | Listens only on your computer. No Azure cost. Stop it with Ctrl+C in this terminal when finished. |

</div>

In a second terminal, change to the same repository folder, then run:

```bash
curl --fail http://127.0.0.1:8766/health
curl --fail http://127.0.0.1:8766/inventory/NB-14
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `curl .../health` | `curl` is an HTTP client. `--fail` makes HTTP error statuses produce a failure exit rather than being treated as normal responses. | Checks only local server readiness. This is not a model or MCP call. |
| 2. `curl .../inventory/NB-14` | `NB-14` in the URL is the item to look up. The server returns inventory JSON read from the CSV. | Compare the stock count of 8 and unit price of KRW 1,450,000 with the contract. Read-only; no Azure cost. |

</div>

Compare the result with the `get_stock` response in `samples/inventory.openapi.json`.
This unauthenticated loopback server is for local practice. It is expected to be inaccessible from the cloud.
Do not expose it publicly through a tunnel.

### 2. Make real calls to the bundled MCP server

```bash
python samples/toolbox_lab.py inspect --local
python samples/toolbox_lab.py call --local --tool get_stock --arguments '{"sku":"NB-14"}' --approve-tool get_stock
python samples/toolbox_lab.py call --local --tool prepare_purchase_request --arguments '{"sku":"NB-14","quantity":2}' --approve-tool prepare_purchase_request
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `inspect --local` | Starts a separate stdio MCP server as a child process, initializes it, and retrieves tool names and contracts. This does not reuse the HTTP server from the previous step. | Check the actual local MCP exchange and tool names. No Azure calls. |
| 2. `call ... get_stock` | `--tool` is the exact tool name, `--arguments` is a JSON object, and `--approve-tool` permits this call with that name and those arguments. | Check the inventory result and local evidence. Omitting the approval option blocks the call before execution. |
| 3. `call ... prepare_purchase_request` | Calls the drafting tool with quantity 2 in the JSON. The outer single quotes preserve the JSON's double quotes in the shell. | Check the KRW 2,900,000 total, pending-approval status, and not-ordered state. Approval to call this tool is not approval to make a purchase. |

</div>

A stdio child process runs the server and performs the actual initialize → tools/list → tools/call exchange.
Check inventory 8, unit price KRW 1,450,000, draft total KRW 2,900,000, and `order_submitted=false`.
Without `--approve-tool`, execution stops **before the call**. Do not interpret tool approval as actual order approval.

### 3. Optional extension: Create a version-pinned Toolbox and Skill

```bash
python samples/toolbox_lab.py create
python samples/toolbox_lab.py create --live
python samples/toolbox_lab.py inspect --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Optional, and only after the L13 resources and managed-identity permissions are ready.

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `create` | Displays the plan for creating a remote Toolbox/Skill. Creation with `--local` is neither necessary nor allowed. | No Azure requests. |
| 2. `create --live` | Registers a uniquely named Toolbox and script-free Skill, and connects the exact version. | Creates remote objects and a local `results/toolbox.json` record. First check the connected services' costs and permission requirements. |
| 3. `inspect --live` | Connects to the receipt's remote endpoint as the current Entra identity and reads lists and Skill resources. | A remote read request, distinct from a successful business-tool execution. An empty list is not marked as success. |

</div>

Register the bundled `data/skills/purchase-review/SKILL.md` as a script-free Skill,
and attach the **exact Skill version** to a uniquely named Toolbox version.
`results/toolbox.json` records the version-specific MCP endpoint.

| Component | Authentication/approval | Purpose of the call |
| --- | --- | --- |
| Toolbox endpoint | Current Entra identity | tools/list, resources/list, resources/read |
| Microsoft Learn MCP | Public documentation; only one search tool allowed | Search product documentation, `require_approval=always` |
| Contoso OpenAPI | Project managed identity → Search audience | Read the synthetic policy index |
| Skill | Pinned version in the same project | Purchase-draft review instructions; no executable scripts |

**Important:** The Toolbox MCP endpoint itself may not hold `tools/call` pending approval.
The **calling runtime must enforce the approval policy** described by the `require_approval` metadata it receives.
The bundled client requires one-time approval for the exact name and arguments of every tool call.

### 4. Optional extension: Call cloud tools by their exact listed names

Copy the name returned by `inspect`. Do not guess an actual name from an example.

```bash
python samples/toolbox_lab.py call --tool 실제-검색도구명 --arguments '{"query":"Microsoft Foundry hosted agents"}' --approve-tool 실제-검색도구명 --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `call --live` | Replace both occurrences of `실제-검색도구명` (“actual search-tool name”) with the same name returned by `inspect`. `--arguments` must follow that tool's schema; `--approve-tool` records one-time approval. | Sends the question to the remote tool. This example searches public product documentation; do not include company data. Check the actual result or error and any service-specific cost. |

</div>

OpenAPI tool arguments must follow the `inputSchema` from `tools/list`.
Pass `api-version=2024-07-01`, `search`, `top<=5`, and the specified `select`.
Use `python samples/toolbox_lab.py openapi` to inspect **the complete contract generated by this repository**. `openapi` is a local command that builds and prints contract JSON from the Search configuration/receipt. It makes no Azure requests or tool calls, but requires the L13 configuration to produce the correct endpoint.
Specifying only an API version's schema default does not send the actual query parameter.

Preserve actual output and tool errors in `results/contoso-toolbox-*.jsonl`.
The Skill must appear in resources/list; also inspect its body through resources/read.
This verifies instruction discovery and reading, not that the model follows the instructions every time.

## Success criteria

For the core course, complete this chapter by verifying the local HTTP response, actual results from both MCP tools, and the approval block for each tool.
If you perform the cloud extension, separately retain tools/list, call, and Skill-read results, plus the version, caller, backend identity, and approval records.
Do not count these as execution of Tool search Preview or an external business-system integration.

## Troubleshooting

For 403 errors, distinguish the caller from the project managed identity. For an empty list, check
the connection, schema, and tool-support status. Do not hide errors by switching authentication to `anonymous` or approval to `never`.

## Cleanup

The local stdio child process exits with the client. Stop the HTTP server with Ctrl+C.
Retain Toolbox/Skill versions with their ownership receipt, and delete them only after separate approval.
