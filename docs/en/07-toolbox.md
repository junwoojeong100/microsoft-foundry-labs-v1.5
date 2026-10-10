> **What you will build:** Query the same inventory over local HTTP and MCP, and verify that a tool call without approval is blocked. Cloud Toolbox/Skills are an optional extension.

<div class="lab-brief" markdown="1">

**Format:** Local steps 1–2 are the core exercise · cloud Toolbox/Skills are optional.

**Start here:** Open two terminals in the same lab folder, one for the server and one for calls.

**What to check:** The HTTP inventory response, both MCP tool results, and rejection without approval. Stop the server afterward.

</div>

## Objectives

**MCP is a connection protocol, OpenAPI is an HTTP contract, Toolbox is a versioned collection of tools,
and a Skill provides instructions for repeatable work.** A Skill is neither approval authority nor evidence of successful execution.

## Concepts and lab map

**What you will try:** Call the same inventory lookup through HTTP and MCP.

**What is it, and why does it matter?** OpenAPI describes requests and responses; MCP is a common way to discover and call tools. A Toolbox groups tools; a Skill supplies instructions. None is business approval.

**How do you use it?** Read the local server's inventory response, then retrieve the same values through MCP. Distinguish a listed tool from an executed tool.

**Where do you run it?** Use two terminals in the same Codespace. The [HTTP server](../../samples/inventory_api.py), [OpenAPI](../../samples/inventory.openapi.json), [MCP server](../../samples/mcp_server.py), and [client](../../samples/toolbox_lab.py) are included. The [English Skill](../../data/en/skills/purchase-review/SKILL.md) belongs to the optional extension.

## Prerequisites

**Reuse L01's Codespace.** Core/MCP dependencies are already prepared; do not reinstall them.

| Scope | Steps to do | What you need |
| --- | --- | --- |
| Core course | 1. Local HTTP/OpenAPI → 2. MCP calls → stop the server | Two terminals in the same Codespace. No Microsoft Azure account |
| Optional extension | The collapsed cloud Toolbox/Skills in steps 3–4 | Search from L11 and the Search Index Data Reader role for the project managed identity |

**Core-course learners do not need to complete L11 first.** Open both terminals in the same Codespace. Here `127.0.0.1` means the Codespace, so run `curl` in its terminal too. Browser port forwarding or Public port exposure is not needed.

<details class="environment-option" markdown="1">
<summary>Only on your PC or when MCP packages are missing: manual installation</summary>

First select L01's Python environment. If absent, follow [PC setup](#l01-pc). Installation needs internet and an approved package source, but no Microsoft Azure sign-in. Skip this in a successfully prepared Codespace.

```bash
python -m pip install -r requirements-tools.txt
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `pip install -r requirements-tools.txt` | Adds MCP lab dependencies to the activated base virtual environment. `python -m pip` keeps the installer aligned with the current Python. | Downloads packages and changes the local environment only; no Microsoft Azure tools are invoked. |

</div>

</details>

## Steps

### 1. Explore the local HTTP/OpenAPI contract

Start the server in the first terminal with L01's English profile selected and leave it running.

```bash
python samples/inventory_api.py
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `inventory_api.py` | Starts an HTTP server that reads synthetic inventory at `127.0.0.1:8766`. It is normal for the shell prompt not to return immediately. | Listens only inside the same Codespace. No Microsoft Azure cost. Stop it with Ctrl+C in this terminal when finished. |

</div>

In a second terminal, change to the same English checkout, reselect `FOUNDRY_LAB_LANGUAGE=en` as in L01 and the appropriate Python environment, then run:

<details class="environment-option" markdown="1">
<summary>Only for Windows PowerShell on your PC: avoid the curl alias</summary>

Use `curl.exe` instead of `curl` below. Do not make this substitution in Codespaces.

</details>

Leave the first terminal's server running. If you are unsure about the second terminal, revisit [L01's new-terminal check](#l01-new-terminal).

```bash
curl --fail http://127.0.0.1:8766/health
curl --fail http://127.0.0.1:8766/inventory/NB-14
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `curl .../health` | `curl` is an HTTP client. `--fail` makes HTTP error statuses produce a failure exit rather than being treated as normal responses. | Checks only local server readiness. This is not a model or MCP call. |
| 2. `curl .../inventory/NB-14` | `NB-14` in the URL is the item to look up. The server returns inventory JSON read from the CSV. | Compare the stock count of 8 and unit price of KRW 1,450,000 with the contract. Read-only; no Microsoft Azure cost. |

</div>

Compare the result with the `get_stock` response in `samples/inventory.openapi.json`.
This unauthenticated loopback server is for local practice. It is expected to be inaccessible from the cloud.
Do not expose it publicly through a tunnel.

### 2. Make real calls to the bundled MCP server

Continue in the **second terminal**, not the one waiting for server requests. These commands start the MCP server separately; no third terminal is needed.

**Codespaces Bash terminal:** Run one line at a time. The second line's approval error is intentional; compare it with the approved calls afterward.

```bash
python samples/toolbox_lab.py inspect --local
python samples/toolbox_lab.py call --local --tool get_stock --arguments '{"sku":"NB-14"}'
python samples/toolbox_lab.py call --local --tool get_stock --arguments '{"sku":"NB-14"}' --approve-tool get_stock
python samples/toolbox_lab.py call --local --tool prepare_purchase_request --arguments '{"sku":"NB-14","quantity":2}' --approve-tool prepare_purchase_request
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `inspect --local` | Starts a separate stdio MCP server as a child process, initializes it, and retrieves tool names and contracts. This does not reuse the HTTP server from the previous step. | Check the actual local MCP exchange and tool names. No Microsoft Azure calls. |
| 2. Unapproved `call` | Supplies the exact tool/arguments but omits `--approve-tool`. | A one-line `ERROR: Approval required: …` and exit code 2 are expected; rejection occurs before `tools/call`. |
| 3. Approved `call ... get_stock` | `--tool` names the tool; `--arguments` supplies JSON; `--approve-tool` permits this name/arguments once. | Check actual inventory and local evidence. |
| 4. `call ... prepare_purchase_request` | Calls the draft function with quantity 2. Outer single quotes preserve the JSON's double quotes. | KRW 2,900,000, pending approval, and not ordered. Tool approval is not purchase approval. |

</div>

<details class="environment-option" markdown="1">
<summary>Only when running on your PC: macOS/Linux and Windows PowerShell commands</summary>

Use the Bash block above on macOS/Linux. In **Windows PowerShell**, use this block **instead**. [`--%`](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_parsing#the-stop-parsing-token) preserves JSON quotes when passing arguments to a Windows executable. It is PowerShell syntax, not a Python option or an approval bypass. Keep each command on one line.

```powershell
.\.venv\Scripts\python.exe samples/toolbox_lab.py inspect --local
.\.venv\Scripts\python.exe --% samples/toolbox_lab.py call --local --tool get_stock --arguments "{\"sku\":\"NB-14\"}"
.\.venv\Scripts\python.exe --% samples/toolbox_lab.py call --local --tool get_stock --arguments "{\"sku\":\"NB-14\"}" --approve-tool get_stock
.\.venv\Scripts\python.exe --% samples/toolbox_lab.py call --local --tool prepare_purchase_request --arguments "{\"sku\":\"NB-14\",\"quantity\":2}" --approve-tool prepare_purchase_request
```

<div class="command-explanation" markdown="1">

**Command walkthrough — Windows**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `inspect --local` | Lists local MCP tools using the environment's Python. | No Microsoft Azure call. |
| 2. Unapproved `call` | Preserves the JSON but does not approve the tool. | Expected `Approval required` error; no tool execution. |
| 3. Approved `get_stock` | Permits this exact name and JSON once. | Local stock 8 and unit price KRW 1,450,000. |
| 4. Approved draft function | Checks quantity 2 and the tool name together. | KRW 2,900,000, not ordered; no purchase approval. |

</div>

</details>

A stdio child process runs the server and performs the actual initialize → tools/list → tools/call exchange.
Check inventory 8, unit price KRW 1,450,000, draft total KRW 2,900,000, and `order_submitted=false`.
Without `--approve-tool`, execution stops **before the call**. Do not interpret tool approval as actual order approval.

### 3. Optional extension: Create a version-pinned Toolbox and Skill

Core-course participants can now go to **Success criteria → Cleanup → L08**.

<details class="optional-path" markdown="1">
<summary>Only after L11 preparation: cloud Toolbox/Skill creation and invocation (steps 3–4)</summary>

```bash
python samples/toolbox_lab.py create
python samples/toolbox_lab.py create --live
python samples/toolbox_lab.py inspect --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Optional, and only after the L11 resources and managed-identity permissions are ready.

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `create` | Displays the plan for creating a remote Toolbox/Skill. Creation with `--local` is neither necessary nor allowed. | No Microsoft Azure requests. |
| 2. `create --live` | Registers a uniquely named Toolbox and script-free Skill, and connects the exact version. | Creates remote objects and a local `results/toolbox.json` record. First check the connected services' costs and permission requirements. |
| 3. `inspect --live` | Connects to the receipt's remote endpoint as the current Entra identity and reads lists and Skill resources. | A remote read request, distinct from a successful business-tool execution. An empty list is not marked as success. |

</div>

Register the bundled `data/en/skills/purchase-review/SKILL.md` as a script-free Skill,
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

Copy the Contoso OpenAPI search tool's exact name returned by `inspect`. Do not guess it or substitute the Microsoft Learn search tool, which has a different argument schema.

```bash
python samples/toolbox_lab.py call --tool ACTUAL_OPENAPI_SEARCH_TOOL_NAME --arguments '{"api-version":"2024-07-01","body":{"search":"laptop purchase approval","top":3,"select":"id,document_id,title,section,filename,content,content_sha256"}}' --approve-tool ACTUAL_OPENAPI_SEARCH_TOOL_NAME --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `call --live` | Replace both occurrences of `ACTUAL_OPENAPI_SEARCH_TOOL_NAME` with the same Contoso OpenAPI tool name returned by `inspect`. `api-version` is a top-level argument; `body` contains `search`, `top`, and `select`. `--approve-tool` records one-time approval of that exact name and payload. | Reads at most 3 English synthetic policy sections through the project managed identity. Check actual returned content and hashes against `data/en/policies/`; Search service charges still apply. No draft or order is created. |

</div>

OpenAPI tool arguments must follow the `inputSchema` from `tools/list`.
For this MCP tool, pass `"api-version":"2024-07-01"` at the top level and nest `search`, `top`, and `select` inside **`body`**. The example uses `top: 3`; keep it at most 5 and retain the specified `select` fields. A flat object containing `search`/`top`/`select` is not this tool's contract. The Microsoft Learn tool's `query` argument is a separate schema, not an alternative for this OpenAPI call.
Use `python samples/toolbox_lab.py openapi` to inspect **the complete contract generated by this repository**. `openapi` is a local command that builds and prints contract JSON from the Search configuration/receipt. It makes no Microsoft Azure requests or tool calls, but requires the L11 configuration to produce the correct endpoint.
Specifying only an API version's schema default does not send the actual query parameter.

Preserve actual output and tool errors in `results/contoso-toolbox-*.jsonl`.
The Skill must appear in resources/list; also inspect its body through resources/read.
This verifies instruction discovery and reading, not that the model follows the instructions every time.

For the optional cloud call in Windows PowerShell, replace `python` with `.\.venv\Scripts\python.exe` and place `--%` after the executable. Wrap `--arguments` in outer **double quotes** and change JSON's inner double quotes to `\"`, as in the local examples. Manually replace both tool-name placeholders. Do not omit approval or `--live` to work around an error.

</details>

<details class="implementation-detail" markdown="1">
<summary>Implementation reference: local MCP servers versus Microsoft Foundry connections — read only</summary>

<a id="l07-local-code-versus-the-foundry-portal"></a>

### Local code versus the Microsoft Foundry portal

The bundled MCP server exposes the synthetic Python functions as MCP tools:

```python
from mcp.server.fastmcp import FastMCP
from workshop import get_stock as stock, prepare_purchase_request as draft

server = FastMCP("contoso-purchasing-v1")

@server.tool()
def get_stock(sku: str) -> dict:
    return stock(sku)

@server.tool()
def prepare_purchase_request(sku: str, quantity: int) -> dict:
    return draft(sku, quantity)

server.run(transport="stdio")
```

| Lab surface | Actual code and behavior |
| --- | --- |
| HTTP server in terminal one | `Handler.do_GET()` in `inventory_api.py` handles `/inventory/<sku>`. It listens only on `127.0.0.1`, so the Microsoft Foundry portal cannot call it directly. |
| MCP call in terminal two | `mcp_server.py` exposes stdio tools; `toolbox_lab.py --local` starts it as a child process and sends `tools/list` / `tools/call`. |
| Optional Foundry Toolbox | `toolbox_lab.py create` registers `MCPToolboxTool` / `OpenApiToolboxTool` and managed identity settings. Inspect the same Toolbox/version in the portal. |
| One-time tool approval | `--approve-tool` is enforced by the bundled client for the exact tool name and arguments. It is not business approval or permission to order. |

The local HTTP/MCP code runs on your computer, not inside a portal button. Portal integration uses an approved cloud Toolbox/OpenAPI connection, not a tunnel to the local server.

</details>

## Success criteria

- You verified the local HTTP response (8 units in stock, unit price KRW 1,450,000).
- You verified the actual results from both MCP tools, and that an unapproved call is blocked before it is made.
- You stopped the server terminal with Ctrl+C.
- If you perform the cloud extension, separately retain tools/list, call, and Skill-read results, plus the version, caller, backend identity, and approval records. Do not count these as execution of Tool search Preview or an external business-system integration.

## Troubleshooting

| Symptom | Next action |
| --- | --- |
| `Connection refused` | Check the server and its port in the first terminal; call from the second terminal |
| `Address already in use` | Check your own server window first. Do not forcibly stop another process. If you use an available port with `inventory_api.py --port 18766`, change both `curl` URLs to that same port |
| `No module named mcp` | Check the L01 Python path and whether that environment has `requirements-tools.txt` installed |
| JSON parsing error | Use your OS's block, particularly Windows's `--%` and quoting syntax |
| `Approval required` | Expected for the unapproved-call exercise; for an approved call, compare the exact reviewed name/arguments with `--approve-tool` |
| `403` in the cloud extension | Distinguish the caller from the project managed identity |
| Empty list in the cloud extension | Check the connection, schema, and tool-support status |

Do not hide errors by switching authentication to `anonymous` or approval to `never`.

## Cleanup

The local stdio child process exits with the client. Stop the HTTP server with Ctrl+C.
Retain Toolbox/Skill versions with their ownership receipt, and delete them only after separate approval.

<div class="lab-handoff" markdown="1">

**Keep:** HTTP inventory, MCP tool names/results, and the unapproved-call rejection. Confirm **Ctrl+C stopped the HTTP server**.

**Continue:** [L08 instruction comparison/evaluation](#l08). Cloud Toolbox is not required to continue the core course.

</div>
