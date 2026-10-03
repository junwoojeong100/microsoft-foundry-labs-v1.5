> **What you will build:** Compare local execution and business-data integration options, and select only the extensions your project needs.

<div class="lab-brief" markdown="1">

**Format:** Advanced elective · choose only one needed path: Local, Fabric, or Work IQ.

**Start here:** Decide whether you need on-device answers, expense totals, or authorized document retrieval.

**What to check:** Record the selection reason, prerequisites, expected output, and shutdown method. Mark actual execution separately.

</div>

## Objectives

**Foundry cloud, Foundry Local, and Foundry Local on Azure Local are not the same deployment approach.** Fabric IQ, Work IQ, and Foundry IQ also provide different knowledge contexts.

## Concepts and lab map

**What you will try:** Choose one path: on-device answers, expense totals, or work-document retrieval.

**What is it, and why does it matter?** Foundry Local runs a model on your device. Fabric IQ connects analytical business data; Work IQ connects Microsoft 365 context. Similar names do not mean identical hardware, permissions, or licenses.

**How do you use it?** Choose one path matching your goal and available environment. Record unprepared paths as designs; do not install every product.

**Where do you run it?** Local needs a supported PC; Fabric and M365 need separately approved test environments. Use only the English [synthetic expenses](../../data/en/monthly-spend.csv) and [purchasing policy](../../data/en/policies/procurement-policy.md).

## Prerequisites

This module consists of **optional mini-labs**. Perform one that fits your available environment and leave the others as selection/design records. Check additional licenses, administrator consent, model downloads, and hardware requirements beforehand.

**Selection example:** Choose Fabric with the synthetic CSV for “exact monthly equipment totals,” Local for “brief guidance on a disconnected device,” or Work IQ for “authorized M365 document retrieval.” Success in one capability does not establish success in another.

Before starting, record the selected path's **purpose, prepared runtime/resource, input, expected output, unsupported conditions, and shutdown action**. Without resources, use the worked examples to deliver a design, not a claim of execution.

## Steps

### 1. Option A: Foundry Local

Use the native SDK flow from the [Foundry Local quickstart](https://learn.microsoft.com/azure/foundry-local/get-started) through the bundled [local_lab.py](../../samples/local_lab.py). Do not clone another sample repository. The example uses `qwen2.5-0.5b`; a small model does not guarantee business accuracy or equal quality across languages.

<div class="practice-block" markdown="1">

**Try it — plan first:** This command prints a plan without initializing the SDK or downloading a model.

```bash
python samples/local_lab.py chat
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `local_lab.py chat` | Read the default model and sentence-style plan. | `plan_only`, `sdk_initialized=false`, `azure_calls=0`; no installation or model execution. |

</div>

Create a separate environment only when choosing real device execution. **On Windows use `.venv-local\Scripts\python.exe` instead of `.venv-local/bin/python`.** The first `python` is L01's Python 3.13. Keep `FOUNDRY_LAB_LANGUAGE=en` selected in each new terminal.

```bash
python -m venv .venv-local
.venv-local/bin/python -m pip install -r requirements-local.txt
.venv-local/bin/python samples/local_lab.py inspect --local
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `venv .venv-local` | Separate the local-model environment from core and MAF dependencies. | Creates a folder on your PC. |
| 2. `pip install` | Install the declared OS-specific SDK: 2.1.0 on non-Windows, WinML 1.2.4 on Windows. | Approved package download/installation; no Azure deployment. |
| 3. `inspect --local` | Initialize the SDK and inspect actual model ID/cache/load state. | Catalog metadata may use the network; no automatic weight download or inference. |

</div>

Check model terms, disk space, and device support. Continue **only after approval to download the model/execution providers**.

```bash
.venv-local/bin/python samples/local_lab.py download --local --allow-download
.venv-local/bin/python samples/local_lab.py chat --style sentence --local
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `download --allow-download` | Download the model and required execution providers. The model cache is `.build/local-model-cache/en`. | Downloads/disk use; no Azure subscription or inference. |
| 2. `chat --style sentence --local` | Load the cached model and ask once about a synthetic draft versus an order, with at most 256 output tokens. | Actual on-device inference. Inspect `load_seconds`, `inference_seconds`, `answer`, and `unloaded=true`. Missing cache errors rather than downloading automatically. |

</div>

In this file, `--local` permits **actual device work**, unlike L14's local server that can call Azure. Separate download, load, and inference times; retain errors or truncation as failures. If organizational policy blocks downloads, use the approved installation route, not a security bypass.

**Change one thing:** Keep model/question unchanged and switch only the instruction's output format from sentence to checklist. This performs one additional device inference.

```bash
.venv-local/bin/python samples/local_lab.py chat --style checklist --local
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `--style checklist` | Requests three short items for the same synthetic question. | Another local load/inference/unload; no Azure calls. A person checks the actual output format. |

</div>

**Explain the result:** Compare `model ID / requested format / actual item count / preserved draft≠approval or order meaning / inference time / unloaded state`. Record unmet formatting as a failure. A longer answer or one faster run does not establish superior quality. The example never automatically switches to cloud inference.

</div>

| What to inspect | How to judge it | Next action on failure |
| --- | --- | --- |
| Official sample's OS/SDK/device memory requirements | Your environment meets the chosen model's requirements | Stop or use another supported device; a cloud model is not Local execution |
| Model ID and completed download state | The selected model is actually available on the device | Separate download failures from inference failures; inspect approved storage/network access |
| Sample's single generation call with the input below | A draft prepares a request; an order requires separate approval/system execution | Check response language, truncation, and model support; do not conflate inference with a business API call |
| State after unload | The running model is unloaded from memory | Inspect process/model state; distinguish unloading from deleting the cache |

```text
Input: "Explain the difference between a purchase request draft and an actual order in one sentence."
```

Distinguish the initial download time from subsequent inference time, and record model/version, memory use, hardware acceleration, and the response. After preparing the model and runtime, check whether the same inference also works in an approved offline test environment.

The core of current Foundry Local is a **runtime/SDK** embedded in an application. An optional server/CLI is also available, but this does not mean “installing the cloud Agent Service locally.” On-device inference does not require an Azure subscription or cloud token charges, but initial model/component downloads, licensing, and optional diagnostics conditions still apply.

### 2. Option B: Fabric IQ

Start with an approved workspace and data agent/semantic model supplied by an administrator. Check support and caller identity in the [Fabric IQ connection documentation](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/fabric-iq). Without that setup, write the specification below rather than creating every Fabric component.

**Use one concrete path: CSV → Lakehouse table → Fabric data agent → Foundry Toolbox.** Do not also create an ontology or Power BI semantic model.

| Prerequisite | Values to obtain |
| --- | --- |
| Fabric | Approved paid F2+ or Fabric-enabled P1+ workspace and a lab Lakehouse in the same region |
| Access | Your test user, read access to data/agent, and authoring permissions for these lab items |
| Connection | An administrator-prepared **data-agent** Foundry connection name/ID with delegated user authentication, not an API key |
| Cost/processing scope | Approved capacity/AI usage/cross-geo processing and a shutdown owner; no new subscription/capacity purchases in the lab |

1. Upload only the bundled `data/en/monthly-spend.csv` under the lab Lakehouse's **Files**. Use **Load to tables → New table**, name `contoso_spend`, select Column header, and use separator `,`. Do not Append/Overwrite an existing table. Compare the [Load to tables fields](https://learn.microsoft.com/fabric/data-engineering/load-to-tables); check **nine rows, month/category/amount_krw**, and numeric amounts.
2. In the workspace, select **+ New item → Fabric data agent**, name it `contoso-spend-agent`, Add the Lakehouse from the OneLake catalog, and select **only `contoso_spend`** in Explorer. Apply the [data-agent creation steps](https://learn.microsoft.com/fabric/data-science/how-to-create-data-agent) to that one table.
3. Set Agent instructions to “Use only selected contoso_spend. Sum amount_krw by month and overall; report KRW. Do not invent rows.” Ask the aggregation question below once inside Fabric, check the source totals, then Publish.
4. Have the administrator compare the **published data agent's** workspace/item IDs and MCP endpoint with the Foundry connection. The general URL is `https://api.fabric.microsoft.com/v1/mcp/workspaces/<workspaceId>/dataagents/<dataAgentId>/agent`; copy your own values and have the owner verify any workspace-private-link host.
5. In Foundry Toolkit, select **My Resources → your project → Tools → Toolbox → Add tools → Configured → Fabric IQ (OneLake Catalog)**, choose the prepared connection, then **Add Tools → Publish/Save Changes**. Toolkit does not directly create the first Fabric IQ connection; the administrator must prepare it in the Foundry portal. Do not substitute another Fabric item's connection.
6. Attach that exact published Toolbox version to a new lab Text agent. Instruct it to query only this synthetic expense tool and withhold unsupported answers. Ask the same aggregation question once and compare the values below with the **actual tool result and connected item**. Source-product and Foundry checks are separate requests.

**Contoso specification example — not an actual Fabric result.**

| Step | Input/choice | Result to judge |
| --- | --- | --- |
| Source preparation | English `monthly-spend.csv`, 9 rows excluding the header | `month`, `category`, numeric `amount_krw` |
| Aggregation | Sum `amount_krw` by `month`, with no filters | July 3,718,000 / August 2,677,000 / September 4,759,000 KRW |
| Source-product check | Run that aggregation in Fabric first | Verify overall 11,154,000 and 9 rows before connecting Foundry |
| Connection | Supply the approved item and read identity to a supported Fabric IQ tool | Same item/identity as the source check |
| Question | “Give the monthly equipment expense totals and the overall total.” | Actual tool results and final answer match the source aggregation |

For mismatches, inspect **source types/duplicates → measure and filters → connected item/identity → answer synthesis**. Do not change the prompt when the source aggregation is already wrong. Correct numbers without tool evidence leave the connection unverified.

**Single-change exercise:** If an additional question is approved, change only the filter to “2026-09.” Expect **three rows and KRW 4,759,000**; the overall 11,154,000 indicates that the filter was not applied. Do not also change data, tools, or models.

### 3. Option C: Work IQ / SharePoint

Use only an approved test tenant and **administrator-provided test accounts A/B**. Check delegation, administrator consent, and licensing in the [Work IQ connection documentation](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/work-iq). Do not create accounts or change permissions arbitrarily during the lab.

Use only **Work IQ Chat through A2A**. The administrator prepares the Work IQ service principal, delegated `WorkIQAgent.Ask`, consent, and an existing connection. This API path uses **Copilot Credits usage-based billing**, not every connector's licensing model. Learners do not need Global Administrator and must not add Outlook/mail-sending tools.

| Step | Action/check |
| --- | --- |
| Synthetic source | One document in an approved test SharePoint location: title “Contoso restricted quote exercise”; content “Case LAB-73, training quote code CONTOSO-QUOTE-DEMO-73. Not a real transaction.” |
| Source permission | Administrator isolates access to A. First verify **A can open the original and B is denied**. Stop if B retains inherited site/group access |
| Toolbox | Foundry Toolkit → My Resources → project → Tools → **+ Add Toolbox → Add tools → Work IQ → Work IQ Chat**. Select the existing connection → Add → Publish |
| Agent | Connect only that Toolbox version to a separate Text agent. No File search, Web search, or other business tools |
| A/B calls | Separate logins/new conversations; each asks once: “Find the quote code and original document for training case LAB-73.” |
| Interpretation | A needs actual tool evidence and the code. B must not receive the unprovided code, content, or document URL; inspect actual tool results too |

Do not put the quote code into the question, instructions, or a public search index. Knowing the reference answer in this guide does not prove an authorized source lookup. Limit the A/B exercise to two user questions; service-internal processing/billing is separate. Without an approved test environment containing only synthetic target documents, do not execute it.

Use only the isolated quote document in the table. Substituting L05's public purchasing policy could let B answer from another authorized source, confounding the restricted-document test.

If B sees restricted evidence, inspect source ACLs, delegated identity, and conversation/cache mixing before repeating queries. Two conversations under one account do not test user isolation.

Do not treat Work IQ Preview, remote SharePoint search, the direct SharePoint tool, and a Foundry IQ knowledge source as the same feature. Record the search protocol and where source permissions are enforced.

### 4. Summarize product boundaries on one page

| Need | Option | Conditions beyond the core course |
| --- | --- | --- |
| Inference on an application user's device | Foundry Local | Model size, hardware, and SDK |
| Inference on enterprise on-premises infrastructure | Foundry Local on Azure Local | Separate Preview access, Kubernetes/Arc, and operational infrastructure |
| Knowledge retrieval over organizational documents | Foundry IQ | Search, knowledge sources, and permissions |
| Analytics/business semantics layer | Fabric IQ | Fabric items and semantic context |
| M365 work context | Work IQ | M365 permissions, delegation, and licenses |
| Use from Copilot Studio | Foundry agent/knowledge connection | The connector's support and Preview conditions |

### 5. Optional specialized model and framework exercises

When considering community/Hugging Face models, Fireworks integration, healthcare models, or image/video/audio models, record **licenses, responsibilities, supported deployment options, and evaluation methods rather than focusing on names**. This is not an exercise in directly using healthcare-specific models for clinical judgment or diagnosis.

Teams already using LangGraph/LangChain or Semantic Kernel should first consider integration with Foundry endpoints, Toolbox, tracing, and hosted runtime rather than a complete rewrite. Bringing existing code does not automatically make its state, retry, and security contracts compatible.

## Success criteria

Record one selected path's **input, runtime/identity, expected and actual values, next action on failure, and shutdown state**. If access is unavailable, retain the reason and completed design specification. Mark other paths not executed; Local inference does not count as Fabric/M365 authorization testing.

## Troubleshooting

Foundry project roles alone do not resolve other products' license, permission, region, or hardware requirements. If the required Preview access is missing, do not work around it using information from another tenant.

## Cleanup

Unload local models and decide whether to retain the model cache. Work with each product's owner to remove test connections, revoke permissions, and disconnect external sources.
