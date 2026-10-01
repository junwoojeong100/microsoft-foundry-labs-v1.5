> **What you will build:** An agent that answers questions about company policy with supporting evidence, checks inventory, and prepares a purchase draft for human approval—plus the evaluation, tracing, and operational practices needed to explain whether it works correctly.

## Objectives

**Foundry is more than a screen for calling models.** It is a development and operations platform for selecting models, connecting agents to knowledge and tools, and managing quality, safety, and cost.

| What you need | Responsible component | What you will do in this guide |
| --- | --- | --- |
| Reasoning and text generation | Foundry Models | Compare models using the same questions |
| Goals, conversations, and tool use | Foundry Agent Service | Build a purchasing and policy assistant |
| Evidence from company documents | File search / AI Search / Foundry IQ | Find answers in documents and cite them |
| Connections to real systems | Functions / MCP / OpenAPI / Toolbox | Check inventory and prepare purchase drafts |
| A way to judge correctness | Evaluations / Red teaming | Test answers, tool use, refusals, and approval boundaries |
| Execution paths and operations | Tracing / Monitoring / Control Plane | Inspect failures, costs, and permissions |

![Contoso lab architecture. The user sends a request to the agent, which uses a model, policy documents, read-only tools, and a drafting tool. Human and business-system approval is required before an actual order.](../../assets/architecture.en.svg)

## Concepts and lab map

**What you will try:** Connect Foundry's Home, Discover, Build, Operate, and Manage areas into a single development workflow.

**What is it, and why does it matter?** A model is an engine that generates text. An agent is a program that connects that engine to a role, knowledge, and tools that perform actions. For example, a model can say, “I will check inventory,” but a tool must retrieve the actual inventory value. Foundry provides a shared workspace for building, evaluating, and observing both. Understanding each component's responsibility before memorizing menu names helps you avoid changing the model or prompt every time an answer is wrong.

**How do you use it?** First locate the features in the portal, then carry out each chapter's small experiment and compare the result with the source material. Use the portal to inspect settings and results visually; use Python and the CLI to reproduce actions and inspect the details. Even in chapters with CLI commands, follow this sequence: observe the screen → read the code and configuration → review the plan → perform an approved live run → interpret the results.

**Where do you run it?** This HTML guide is documentation, not an application that controls Azure. Code copy buttons only copy; they do not execute anything. Completing the full lab requires a terminal. Each chapter distinguishes portal-only steps from those that require an SDK.

### The five entry points in the live portal

![Home in the English Contoso project, contoso-workshop-en. Locate Home, Discover, Build, Operate, Manage, and the project and Azure OpenAI endpoint fields.](../../assets/portal/en/01-home.png)

**Reading the screen:** First confirm your own lab project in the project selector at the top. **Discover** is for exploring candidates, **Build** for configuring models, agents, and tools, **Operate** for operational status, and **Manage** for project and resource management. The **Project endpoint** and **Azure OpenAI endpoint** on Home are different addresses.

The English edition uses a separate **`contoso-workshop-en` project and English synthetic data**. All **18 English portal screenshots** were captured from the signed-in English environment and are under `assets/portal/en/`, with identifying information masked or cropped—not translated overlays on the earlier Korean-data screenshots. The models, features, and versions you see depend on your permissions, region, and the date.

**English backend validation and portal observation are separate activities.** The English run created and invoked owned agents, retrieved English policies, and submitted approved evaluations. Consult the [English screenshot log](../../content/portal-screenshots.en.json) for exact capture scope, times, masking, and hashes. Fine-tuning image 14 is a product sample, not Contoso training; Voice image 15 records a canceled form, not a voice session. A screenshot is an observation, not deployment or release-quality certification.

**Current learning path: educational initial v1 → evaluate → analyze and improve → reevaluate v2.** L08 uses the same 12 composite development questions and fixed criteria in both languages. V1 is a simple role-and-goal starting point; v2 adds request decomposition, verified-versus-unknown separation, claim-specific evidence, and omission checks. It does not memorize evaluation answers, and ties or regressions are reported as observed.

The [current instruction status](../../validation/current/instructions.json) links the [latest Prompt Agent comparison](../../validation/current/report.json). Korean native relevance changed from 4.9167/5 to 5.0/5 on one question; the other Korean metrics and all English metrics tied at 5.0/5. This limited dev observation is not a generalized improvement or release pass.

### How to read the source code and commands

Open the complete kit from the repository's file list on GitHub or through **File → Open Folder** in VS Code. Extract the ZIP first if you downloaded it. Your browser's “View page source” shows only the guide's HTML.

| What to look for | Source file |
| --- | --- |
| Core labs and function implementations | [samples/workshop.py](../../samples/workshop.py) |
| Hosted request handling | [hosted/main.py](../../hosted/main.py), [samples/hosted_runtime.py](../../samples/hosted_runtime.py) |
| Environment variables and model names | [.env.example](../../.env.example) — the starting point for your personal `.env` |
| Services and entry points to deploy | [azure.yaml](../../azure.yaml) |
| Infrastructure definitions | [infra/main.bicep](../../infra/main.bicep) |
| English synthetic inputs and unchanged business contracts | [data/en/profile-manifest.json](../../data/en/profile-manifest.json) |
| Learner module sources | [docs/en/00-start.md](../../docs/en/00-start.md) in English and [docs/00-start.md](../../docs/00-start.md) in Korean — regenerate HTML/Markdown/PDF/ZIP after editing |

In `python samples/workshop.py model --live`, `python` is the interpreter, `samples/workshop.py` is the file, `model` is the subcommand to run, and `--live` is this sample's opt-in flag for real Azure execution. The numbered rows in the **Command walkthrough** below each executable block follow the commands in that block. Unless stated otherwise, run commands from the root of your separate English checkout. Descriptive placeholders such as `ACTUAL_NUMERIC_VERSION`, `approved-subscription-id`, and `results/actual-dev-responses.jsonl` must be replaced with your own verified values, not entered literally.

`--live` is not a universal CLI safety switch. `azd deploy`, `az login`, and some management scripts work without it, so always read the accompanying explanation. Nor does `--local` always mean “no Azure cost”: the local Hosted server in L14 can call real models and search services. Browser sign-in and terminal `az login` also use separate sessions.

A `KEY=value` prefix passes an environment variable to **that command only** in macOS/Linux shells. In PowerShell, set `$env:KEY = "value"` for the current session, run the command portion, and restore the previous value when finished. A trailing `\` continues a line in bash; do not paste it unchanged into PowerShell. Combine the command into one line instead. `AZURE_DEV_USER_AGENT=microsoft_foundry_skill` only identifies the authoring tool; learners do not need to install a Copilot skill.

## Prerequisites

This guide is for **developers, architects, and technical professionals applying generative AI to business workflows**. You do not need coding experience for the portal observation steps, but you will use Python and a terminal to complete the full core course. Before copying an unfamiliar command, read its explanation and execution scope immediately below it.

Keep all files in their original folder structure. Open `index.html` directly to use the web guide. This guide is bilingual: English is the default at `index.html`, Korean is available at `index.ko.html`, and the generated Markdown/PDF/ZIP downloads are grouped under `downloads/`. The language switch preserves your current module and progress, but **does not select the runtime's data language**.

Follow L01 to select `FOUNDRY_LAB_LANGUAGE=en` in every terminal. Samples then use `data/en/` for English policies, prompts, inventory, evaluation, and tuning inputs; without the flag, the original Korean profile remains the default. SKU IDs, wire-contract names/statuses, KRW amounts, quantities, and quality gates remain unchanged. Hosted packages bind their selected language in `lab-profile.json`. Use a clean, separate checkout/worktree with its own `.env`, `.azure/`, and `results/`; never reuse or overwrite a Korean run's private configuration or receipts. You can read the guide and use local exercises offline. Azure labs and official-source links require internet access.

## Steps

### 1. Choose your path

| Path | Suggested sequence | Assumptions |
| --- | --- | --- |
| 90-minute introduction | L00 → preconfigured L01 → L04 → L05 → shortened L08 → L12 | The instructor has prepared the project, models, and permissions |
| Start to finish | L00–L12 | About 5 hours 20 minutes, plus resource waits and breaks |
| Developer extensions | Core → L13 → L14 → L15 → L22 | Deeper SDK, deployment, and search work |
| Enterprise adoption | Core → L16 → L17 → L21 → L22 → L24 | Collaboration with administrators and security teams |
| Document and voice experiences | Core → L18 → L19 → L23 | Access to supported models and services |
| Without an account | L01 local → L06 local → L08 gates → design exercises | Do not record these as successful live Azure runs |

Times are **estimates of hands-on work**. They exclude waits for quota approval, model downloads, indexing, training, and administrator approval.

### 2. Keep one scenario in mind

An employee at the fictional company Contoso asks:

```text
I need two laptops.
Check company policy and NB-14 inventory, then prepare a purchase request draft.
```

The completed system searches the policy, retrieves an inventory count of 8 and a unit price of KRW 1,450,000, and returns a **draft awaiting approval** for a total of KRW 2,900,000. Approval is required from both the team manager and the purchasing representative. **An answer claiming “Order completed” is a failure.**

### 3. Learn three important distinctions

| Common source of confusion | The distinction |
| --- | --- |
| Model vs. agent | A model is an inference engine. An agent is an execution unit using a model + instructions + state + tools |
| Knowledge vs. tools vs. memory | Knowledge supplies company evidence. Tools provide capabilities. Memory retains authorized context across sessions, within the user's scope |
| GA vs. Preview | A GA portal does not mean that Memory, Voice, and every operational feature are also GA |

### 4. Keep evidence of your results

Mark progress only after meeting the **Success criteria** at the end of each module. Browser progress is stored only in this device's local storage; it does not establish service execution. Save personal originals in your English checkout's `results/`. Keep only the latest reviewed set under `validation/current/`, retaining its actual language and input hashes. Do not record personal information or tokens or relabel one environment's evidence as another's.

## Success criteria

- You can distinguish a model-only call from an agent that uses tools.
- You can explain why the finished result needs **supporting evidence, real tool results, and a not-yet-approved status**.
- You have chosen your learning path and its final cleanup step.

## Troubleshooting

**Do not enable every feature at the start.** A Prompt Agent, File search, function tools, evaluation, and tracing are enough for the first day. Add Preview features, complex networking, and further business integrations only after completing the core result.

## Cleanup

This module creates no resources. Continue to **L01: Prepare an environment you can run**.

<details markdown="1">
<summary>What this guide means by “all core capabilities”</summary>

The learning paths cover the capability families in Microsoft's capability map and reference. This does not mean that every model, region, and API combination has been executed. Core capabilities are hands-on; those requiring administrators or additional licenses are clearly marked as conditional labs or design exercises. See **Feature coverage** for the detailed mapping.

</details>
