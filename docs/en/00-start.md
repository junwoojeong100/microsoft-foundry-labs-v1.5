> **What you will build:** An agent that answers questions about company policy with supporting evidence, checks inventory, and prepares a purchase draft for human approval—plus the evaluation, tracing, and operational practices needed to explain whether it works correctly.

<div class="lab-brief" markdown="1">

**Format:** Reading · no Azure account or installation needed.

**Start here:** Read “New to Azure? Start here” below, then choose your learning path.

**What to check:** Explain one thing the purchasing assistant will do and one thing it must not do.

</div>

<a id="l00-first-steps"></a>

## New to Azure? Start here

**Azure is Microsoft's cloud platform. Foundry is a workspace on Azure for building and managing AI models and agents.** Here you build a purchasing assistant for the fictional company Contoso. Do not use real company accounts, purchasing records, or payment information as lab data.

```text
User: "Check policy and stock for two laptops, then prepare a draft."
  → Model: interprets the question and writes an answer
  → Document search: finds the relevant policy evidence
  → Function tools: read synthetic stock and calculate a draft
  → User: receives evidence and a draft awaiting approval — not an order
```

Start with these five terms. Learn other acronyms when you need them and use the [glossary](#glossary) as a reference.

| Term | Meaning in this lab |
| --- | --- |
| Portal | A management website. Azure portal focuses on resources, access, and costs; Foundry portal focuses on AI work |
| Project | A workspace organizing this assistant's agents and connections |
| Model | The AI that receives input and generates text |
| Agent | A program combining a model with instructions, knowledge, and tools |
| Deployment | Making a model available to call in your environment; not training the model |

**Start with 11 core modules, L00–L10.** The eight advanced modules, L11–L18, are electives. **Finish every path with shared wrap-up L19.** Core-only learners jump directly from L10 to L19 without completing the electives.

| Your situation | Start here | Ready to continue when |
| --- | --- | --- |
| The instructor supplied a project and cost approval | [L01 setup](#l01) → L02 deployment check → L03 first call | You have an actual answer and response ID from your project |
| No Azure account/access, or setup is still pending | [L01 PC setup](#l01-pc) → [English profile](#l01-language) → [local checks](#l01-local) → L06 local functions → L08 result reading | Data checks pass, you calculate the KRW 2,900,000 draft, and compare two answers |

The second path **does not count as passing Azure execution exercises**. Do not create an account or add payment details on your own; mark live calls not executed. Choose **Without Azure** in the web contents to find modules containing these steps.

## Objectives

**Foundry is more than a screen for calling models.** It is a development and operations platform for selecting models, connecting agents to knowledge and tools, and managing quality, safety, and cost.

<details markdown="1">
<summary>Optional reference: which Foundry capabilities do the core labs use?</summary>

| What you need | Responsible component | What you will do in this guide |
| --- | --- | --- |
| Reasoning and text generation | Foundry Models | Compare models using the same questions |
| Goals, conversations, and tool use | Foundry Agent Service | Build a purchasing and policy assistant |
| Evidence from company documents | File search / AI Search / Foundry IQ | Find answers in documents and cite them |
| Connections to real systems | Functions / MCP / OpenAPI / Toolbox | Check inventory and prepare purchase drafts |
| A way to judge correctness | Evaluations / Red teaming | Test answers, tool use, refusals, and approval boundaries |
| Execution paths and operations | Tracing / Monitoring / Control Plane | Inspect failures, costs, and permissions |

</details>

![Contoso lab architecture. The user sends a request to the agent, which uses a model, policy documents, read-only tools, and a drafting tool. Human and business-system approval is required before an actual order.](../../assets/architecture.en.svg)

## Concepts and lab map

**What you will try:** Add company documents and inventory lookup to a model, one capability at a time.

**What is it, and why does it matter?** A model writes an answer; an agent connects the model to instructions, documents, and tools. Saying “I will check inventory” is different from a tool returning eight units in stock.

**How do you use it?** Add one capability per module and check the result. Compare policy claims with the documents, and quantities and amounts with function results. You do not need to memorize every menu.

**Where do you run it?** This page is a guide. The portal is the AI workspace in your browser; the terminal is the command window on your PC. **Copy is not Run.**

### The five entry points in the live portal

![Home in the English Contoso project, contoso-workshop-en. Locate Home, Discover, Build, Operate, Manage, and the project and Azure OpenAI endpoint fields.](../../assets/portal/en/01-home.png)

**Reading the screen:** First confirm your own lab project in the project selector at the top. **Discover** is for exploring candidates, **Build** for configuring models, agents, and tools, **Operate** for operational status, and **Manage** for project and resource management. The **Project endpoint** and **Azure OpenAI endpoint** on Home are different addresses.

Masked areas contain identifying information, not values to copy. Use your own project's values. If menus differ, first check new/Classic portal mode, the current project, and your access.

<details class="provenance-note" markdown="1">
<summary>Reference: screenshot scope and validation records</summary>

The English edition uses a separate **`contoso-workshop-en` project and English synthetic data**. All **16 English portal screenshots used in this guide** were captured from the signed-in English environment and are under `assets/portal/en/`, with identifying information masked or cropped—not translated overlays on the earlier Korean-data screenshots. The models, features, and versions you see depend on your permissions, region, and the date.

**Backend execution and portal observation are separate activities.** Keep your agent, retrieval, and evaluation results outside the guide. Consult the [English screenshot provenance](../../content/portal-screenshots.en.json) for capture scope, times, masking, and hashes. A screenshot is an observation, not deployment or release-quality certification.

**Current learning path: educational initial v1 → evaluate → analyze and improve → reevaluate v2.** L08 uses the same 12 composite development questions and fixed criteria in both languages. V1 is a simple role-and-goal starting point; v2 adds request decomposition, verified-versus-unknown separation, claim-specific evidence, and omission checks. It does not memorize evaluation answers, and ties or regressions are reported as observed.

Keep your own comparison results outside the guide. A small dev observation does not establish general improvement or release approval.

</details>

### How to read the source code and commands

Download and extract the complete workshop ZIP, then use **File → Open Folder** in VS Code. The **lab folder (repository root)** contains `samples`, `data`, and `requirements.txt` together. Your browser's “View page source” shows the guide's HTML, not the executable samples. Git command knowledge is not required to start.

<details markdown="1">
<summary>Reference: what the source files do</summary>

| What to look for | Source file |
| --- | --- |
| Core labs and function implementations | [samples/workshop.py](../../samples/workshop.py) |
| Hosted request handling | [hosted/main.py](../../hosted/main.py), [samples/hosted_runtime.py](../../samples/hosted_runtime.py) |
| Environment variables and model names | [.env.example](../../.env.example) — the starting point for your personal `.env` |
| Services and entry points to deploy | [azure.yaml](../../azure.yaml) |
| Infrastructure definitions | [infra/main.bicep](../../infra/main.bicep) |
| English synthetic inputs and unchanged business contracts | [data/en/profile-manifest.json](../../data/en/profile-manifest.json) |
| Learner module sources | [docs/en/00-start.md](../../docs/en/00-start.md) in English and [docs/00-start.md](../../docs/00-start.md) in Korean — regenerate HTML/Markdown/PDF/ZIP after editing |

</details>

In `python samples/workshop.py model --live`, `python` is the interpreter, `samples/workshop.py` is the file, `model` is the subcommand to run, and `--live` is this sample's opt-in flag for real Azure execution. The numbered rows in the **Command walkthrough** below each executable block follow the commands in that block. Unless stated otherwise, run commands from the root of your separate English checkout. Descriptive placeholders such as `ACTUAL_NUMERIC_VERSION`, `approved-subscription-id`, and `results/actual-dev-responses.jsonl` must be replaced with your own verified values, not entered literally.

**Check where to paste first.** Bash/PowerShell commands go in a terminal, questions in the portal input named by the step, and `.env` values in the editor's `.env` file. Python excerpts and JSON result examples are not terminal commands. Run multi-command blocks one line at a time, reading the result before continuing.

`--live` is not a universal CLI safety switch. `azd deploy`, `az login`, and some management scripts work without it, so always read the accompanying explanation. Nor does `--local` always mean “no Azure cost”: the local Hosted server in L12 can call real models and search services. Browser sign-in and terminal `az login` also use separate sessions.

<details markdown="1">
<summary>For advanced commands: environment variables, continued lines, and azd</summary>

A `KEY=value` prefix passes an environment variable to **that command only** in macOS/Linux shells. In PowerShell, set `$env:KEY = "value"` for the current session, run the command portion, and restore the previous value when finished. A trailing `\` continues a line in bash; do not paste it unchanged into PowerShell. Combine the command into one line instead. `AZURE_DEV_USER_AGENT=microsoft_foundry_skill` only identifies the authoring tool; learners do not need to install a Copilot skill.

</details>

## Prerequisites

This guide is for **developers, architects, and technical professionals applying generative AI to business workflows**. You do not need coding experience for the portal observation steps, but you will use Python and a terminal to complete the full core course. Before copying an unfamiliar command, read its explanation and execution scope immediately below it.

Keep all files in their original folder structure. Open `index.html` directly to use the web guide. This guide is bilingual: English is the default at `index.html`, Korean is available at `index.ko.html`, and the generated Markdown/PDF/ZIP downloads are grouped under `downloads/`. The language switch preserves your current module and progress, but **does not select the runtime's data language**.

Follow L01 to select `FOUNDRY_LAB_LANGUAGE=en` in every terminal. Samples then use `data/en/` for English policies, prompts, inventory, evaluation, and tuning inputs; without the flag, the original Korean profile remains the default. SKU IDs, wire-contract names/statuses, KRW amounts, quantities, and quality gates remain unchanged. Hosted packages bind their selected language in `lab-profile.json`. Use a clean, separate checkout/worktree with its own `.env`, `.azure/`, and `results/`; never reuse or overwrite a Korean run's private configuration or receipts. You can read the guide and use local exercises offline. Azure labs and official-source links require internet access.

## Steps

### 1. Choose your path

| Path | Suggested sequence | Assumptions |
| --- | --- | --- |
| 90-minute introduction | L00 → preconfigured L01 → L04 → L05 → shortened L08 → L19 | The instructor has prepared the project, models, and permissions |
| Core course | L00–L10 → L19 | Core: 4 hours 45 minutes + 10-minute wrap-up; waits and breaks extra |
| Developer extensions | Core → L11 → L12 → L13/L14 → optional L18 → L19 | Deeper SDK, deployment, and search work |
| Enterprise adoption | Core → L15 → L16 → L17 → optional L18 → L19 | Collaboration with administrators and security teams |
| Without an account | L01 local → L06 local → read existing L08 results → design exercises | Do not record these as successful live Azure runs |

Times are **estimates of hands-on work**. They exclude waits for quota approval, resource preparation, indexing, and administrator approval.

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

Mark progress only after meeting the **Success criteria** at the end of each module. Browser progress is stored only in this device's local storage; it does not establish service execution. Save your own originals in your English lab folder's `results/`, outside the guide. Do not record personal information or tokens or relabel one environment's evidence as another's.

Web progress counts **only the selected path**: 11 core modules plus wrap-up, eight advanced modules plus wrap-up, or six including wrap-up in the 90-minute tour. A merged chapter's old checkmark is not transferred to a new feature. Use **Explain a term / I'm stuck**, then **Return to the lab** to resume without losing your path. On a phone, find these links under **Menu**.

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
