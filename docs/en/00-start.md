> **What you will build:** An agent that answers questions about company policy with supporting evidence, checks inventory, and prepares a purchase draft for human approval—plus the evaluation, tracing, and operational practices needed to explain whether it works correctly.

<div class="lab-brief" markdown="1">

**Format:** Reading · no Microsoft Azure account or installation needed.

**Start here:** Read “New to Microsoft Azure? Start here” below, then choose your learning path.

**What to check:** Explain one thing the purchasing assistant will do and one thing it must not do.

</div>

<a id="l00-first-steps"></a>

<a id="l00-new-to-azure-start-here"></a>

## New to Microsoft Azure? Start here

**Microsoft Azure is Microsoft's cloud platform. Microsoft Foundry is a workspace on Microsoft Azure for building and managing AI models and agents.** Here you build a purchasing assistant for the fictional company Contoso. Do not use real company accounts, purchasing records, or payment information as lab data.

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
| Portal | A management website. Microsoft Azure portal focuses on resources, access, and costs; Microsoft Foundry portal focuses on AI work |
| Project | A workspace organizing this assistant's agents and connections |
| Model | The AI that receives input and generates text |
| Agent | A program combining a model with instructions, knowledge, and tools |
| Deployment | Making a model available to call in your environment; not training the model |

**Core is 11 modules (L00–L10); finish every path with shared wrap-up L19.** The eight advanced modules (L11–L18) are electives and need not all be completed. The default environment is **GitHub Codespaces**, the prepared browser terminal. Expand PC installation and OS-specific alternatives only when needed.

```text
Prepare      L00 overview → L01 your environment → L02 model checks
Build        L03 first answer → L04 instructions → L05 documents → L06 functions → L07 MCP
Check/finish L08 evaluation → L09 boundaries → L10 traces → L19 costs and wrap-up
```

Each module follows **Prerequisites → Steps → Success criteria → Cleanup**. Record a successful result before continuing; on failure, use that module's **Troubleshooting** section. Collapsed **optional and implementation-reference** sections are not required for the main path. Core-only learners go directly from L10 to L19.

**Choose the path that matches your situation.**

| Your situation | Start here | Ready to continue when |
| --- | --- | --- |
| Your Microsoft Azure subscription, permissions, and budget scope are ready | [Create your environment in L01](#l01) → inspect your deployment in L02 → first call in L03 | An actual answer/response ID from the project you created |
| Microsoft Azure account, permissions, or cost conditions are still pending | [L01 Codespaces setup/local checks](#l01-codespaces) → L06 local functions → L07 local MCP → L08 instructions/questions | Valid data, the KRW 2,900,000 draft, and MCP calls; live Microsoft Azure execution remains not performed |

The default is **create your environment → run the labs → clean up your resources**. The second path is local preparation, not completion of the Microsoft Foundry experience. **Without Microsoft Azure** groups those local, reading, and design steps.

<a id="l00-agent-map"></a>

### Same scenario, three different agents

**Not every module modifies the same agent.** The core course uses the targets below. Do not mix their names or result files.

| Target | Created in → reused in | What to check and keep |
| --- | --- | --- |
| Portal policy agent | L04 creation → L05 documents → L09 boundary questions | Your name/version/store, answers, and citations. No inventory functions |
| Integrated SDK agent | Created separately in L06 → the same result traced in L10 | Printed `Responses:` JSONL and `Resource receipt:` JSON paths |
| Instruction-evaluation agent | Created separately in L08 → only the saved originals evaluated | Collection JSON and Native evaluation JSON; not an evaluation of L06 function execution |

Keep your names and paths in the [progress record](#instructor). Do not reuse screenshot names or another participant's files.

## Objectives

**Microsoft Foundry is more than a screen for calling models.** It is a development and operations platform for selecting models, connecting agents to knowledge and tools, and managing quality, safety, and cost.

<details markdown="1">
<summary>Optional reference: which Microsoft Foundry capabilities do the core labs use?</summary>

| What you need | Responsible component | What you will do in this guide |
| --- | --- | --- |
| Reasoning and text generation | Microsoft Foundry Models | Compare models using the same questions |
| Goals, conversations, and tool use | Microsoft Foundry Agent Service | Build a purchasing and policy assistant |
| Evidence from company documents | File search / AI Search / Microsoft Foundry IQ | Find answers in documents and cite them |
| Connections to real systems | Functions / MCP / OpenAPI / Toolbox | Check inventory and prepare purchase drafts |
| A way to judge correctness | Evaluations / Red teaming | Test answers, tool use, refusals, and approval boundaries |
| Execution paths and operations | Tracing / Monitoring / Control Plane | Inspect failures, costs, and permissions |

</details>

![Contoso lab architecture. The user sends a request to the agent, which uses a model, policy documents, read-only tools, and a drafting tool. Human and business-system approval is required before an actual order.](../../assets/architecture.en.svg)

## Concepts and lab map

**What you will try:** Add company documents and inventory lookup to a model, one capability at a time.

**What is it, and why does it matter?** A model writes an answer; an agent connects the model to instructions, documents, and tools. Saying “I will check inventory” is different from a tool returning eight units in stock.

**How do you use it?** Add one capability per module and check the result. Compare policy claims with the documents, and quantities and amounts with function results. You do not need to memorize every menu.

**Where do you run it?** This page is a guide. The portal is the AI workspace in your browser; the default terminal is **the command window inside Codespaces**. **Copy is not Run.**

### The five entry points in the live portal

![Home in the English Contoso project, contoso-workshop-en. Locate Home, Discover, Build, Operate, Manage, and the project and Azure OpenAI endpoint fields.](../../assets/portal/en/01-home.png)

**Reading the screen:** First confirm your own lab project in the project selector at the top. **Discover** is for exploring candidates, **Build** for configuring models, agents, and tools, **Operate** for operational status, and **Manage** for project and resource management. The **Project endpoint** and **Azure OpenAI endpoint** on Home are different addresses.

**About the screens:** Screens are examples to help you follow the labs. Menus and available models/features can differ with permissions, region, and updates. Use your own project's values rather than copying names or identifiers from an image. Check completion against each module's **Success criteria**.

### How to read the source code and commands

Use the repository prepared in [L01's Codespace](#l01-codespaces). Run commands from the **lab folder (repository root)**, where `samples`, `data`, and `requirements.txt` appear together. Even from a Windows PC, the Codespaces terminal is **Linux/Bash**. The default `python` is the prepared `.venv`; advanced modules specify their separate Python environment.

| Block in the text | Where to paste it and how to use it |
| --- | --- |
| Bash / PowerShell command | The terminal the step names. Run a multi-command block one line at a time and read each result |
| Question or instructions | The portal input the step names |
| `.env` settings | The editor's `.env` file |
| Python excerpt or JSON result example | Reading material to compare against; not a terminal command |

**Three things to remember before running a command**

1. **Copy is not Run.** Read the walkthrough below the command first for request counts, changes, and costs. Replace descriptive placeholders with your verified values, and judge the result by each module's success criteria.
2. **“Local” means running inside the same Codespace.** Both terminals and `127.0.0.1` refer to that Codespace. “No Microsoft Azure calls” does not mean there are no GitHub Codespaces compute/storage charges.
3. **Do not judge safety by option names.** `--live` is not a universal CLI safety switch: `azd deploy`, `az login`, and some management scripts work without it. `--local` does not always mean “no Microsoft Azure cost” either; the local Hosted server in L12 can call real models and search services. Browser sign-in and terminal `az login` also use separate sessions.

<details class="environment-option" markdown="1">
<summary>Only for the PC alternative: open the ZIP in VS Code</summary>

Extract the complete workshop ZIP, preserve its structure, and use **File → Open Folder** in VS Code. Follow [L01's PC setup](#l01-pc). Only when choosing this alternative do subsequent local exercises run on your PC.

</details>

<details markdown="1">
<summary>Reference: find the source files and read Python commands</summary>

Your browser's “View page source” shows only the guide's HTML. Find the executable code in the files below. Code-backed labs pair **Microsoft Foundry portal settings/actions ↔ the Python code that runs ↔ the result to inspect**; local Agent Framework and design exercises explicitly state when there is no portal counterpart and when no Microsoft Azure operation was performed.

| What to look for | Source file |
| --- | --- |
| First code lab: send one model question | [samples/first_response.py](../../samples/first_response.py) |
| Integrated lab runner and function implementations | [samples/workshop.py](../../samples/workshop.py) |
| What each sample file does | [samples/README.md](../../samples/README.md) — entry points and shared helpers |
| Hosted request handling | [hosted/main.py](../../hosted/main.py), [samples/hosted_runtime.py](../../samples/hosted_runtime.py) |
| Environment variables and model names | [.env.example](../../.env.example) — the starting point for your personal `.env` |
| Services and entry points to deploy | [azure.yaml](../../azure.yaml) |
| Infrastructure definitions | [infra/main.bicep](../../infra/main.bicep) |
| English synthetic inputs and unchanged business contracts | [data/en/profile-manifest.json](../../data/en/profile-manifest.json) |
| Learner module sources | [docs/en/00-start.md](../../docs/en/00-start.md) in English and [docs/00-start.md](../../docs/00-start.md) in Korean — regenerate HTML/Markdown/ZIP after editing |

Read `python samples/first_response.py --query "..." --live` as four parts:

| Part | Meaning |
| --- | --- |
| `python` | The Python interpreter |
| `samples/first_response.py` | The focused, one-request lesson |
| `--query "..."` | The model input. Without `--live`, it is only shown in the plan |
| `--live` | Permits one actual Microsoft Azure request in this example |

Read each command as file, operation, and inputs. Compare the SDK blocks with the [sample guide](../../samples/README.md), then check request bounds and ownership.

</details>

<details class="environment-option" markdown="1">
<summary>Only for Windows PowerShell on your PC: change the interpreter path</summary>

Replace the core environment's `python` with `.\.venv\Scripts\python.exe`: for example, `.\.venv\Scripts\python.exe samples/first_response.py`. Do not make this substitution in Codespaces, even from a Windows PC.

</details>

<details markdown="1">
<summary>For advanced commands: environment variables, continued lines, and azd</summary>

A `KEY=value` prefix passes an environment variable to **that command only** in Codespaces Bash. If you chose PowerShell on your PC, set `$env:KEY = "value"` for the current session, run the command portion, and restore the previous value when finished. A trailing `\` continues a line in Bash; do not paste it unchanged into PowerShell. Combine the command into one line instead.

</details>

## Prerequisites

This guide is for **developers, architects, and technical professionals applying generative AI to business workflows**. You do not need coding experience for the portal observation steps, but you will use Python and a terminal to complete the full core course. Before copying an unfamiliar command, read its explanation and execution scope immediately below it.

Keep all files in their original folder structure. Open `index.html` directly to use the web guide. This guide is bilingual: English is the default at `index.html`, Korean is available at `index.ko.html`, and the generated Markdown/ZIP downloads are grouped under `downloads/`. The language switch preserves your current module and progress, but **does not select the runtime's data language**.

Follow L01 to select `FOUNDRY_LAB_LANGUAGE=en` in every terminal. Samples then use `data/en/` for English policies, prompts, inventory, evaluation, and tuning inputs; without the flag, the original Korean profile remains the default. SKU IDs, wire-contract names/statuses, KRW amounts, quantities, and quality gates remain unchanged. Hosted packages bind their selected language in `lab-profile.json`. Use a clean, separate checkout/worktree with its own `.env`, `.azure/`, and `results/`; never reuse or overwrite a Korean run's private configuration or receipts. You can read the downloaded guide and use PC-local exercises offline. Codespaces access, Microsoft Azure labs, and official-source links require internet access.

## Steps

### 1. Choose your path

| Path | Suggested sequence | Assumptions |
| --- | --- | --- |
| 90-minute summary | L00 → L01 status review → L04 → L05 → shortened L08 → L19 | Complete your own L01/L02 provisioning first; creation time is additional |
| Core course | L00–L10 → L19 | Core: 4 hours 45 minutes + 10-minute wrap-up; waits and breaks extra |
| Developer extensions | Core → L11 → L12 → L13/L14 → optional L18 → L19 | Deeper SDK, deployment, and search work |
| Control and operations | Core → L15 → L16 → L17 → optional L18 → L19 | Create memory/schedules and design access/recovery boundaries in your environment |
| Practice without Microsoft Azure | L01 local → L06 local → L07 local MCP → L08 instructions/questions → optional design → L19 | Neither live Microsoft Azure execution nor full-course completion |

The displayed core time is **4 hours 45 minutes**, plus ten minutes for wrap-up. It estimates direct work; allow extra time for first installation, access/cost approval, provisioning, indexing, and breaks.

### 2. Keep one scenario in mind

An employee at the fictional company Contoso asks:

```text
I need two laptops.
Check company policy and NB-14 inventory, then prepare a purchase request draft.
```

The completed system searches the policy, retrieves an inventory count of 8 and a unit price of KRW 1,450,000, and returns a **draft awaiting approval** for a total of KRW 2,900,000. Approval is required from both the team manager and the purchasing representative. **An answer claiming “Order completed” is a failure.**

The labs use the agents and result files separated in the [three-target table](#l00-agent-map) above.

### 3. Learn three important distinctions

| Common source of confusion | The distinction |
| --- | --- |
| Model vs. agent | A model is an inference engine. An agent is an execution unit using a model + instructions + state + tools |
| Knowledge vs. tools vs. memory | Knowledge supplies company evidence. Tools provide capabilities. Memory retains authorized context across sessions, within the user's scope |
| GA vs. Preview | A GA portal does not mean that Memory, Voice, and every operational feature are also GA |

### 4. Check results and mark progress

Check each module's **Success criteria** before marking progress. Browser progress is local to this device, not proof of service execution. Save actual results in your English folder's `results/` and [progress/completion checklist](#instructor), without personal information or tokens.

Web progress counts **only the selected path**: 11 core modules plus wrap-up, eight advanced modules plus wrap-up, or six including wrap-up in the 90-minute tour. Use **Explain a term / I'm stuck**, then **Return to the lab** to resume at the original section and reading position. On a phone, find these links under **Menu**.

## Success criteria

- You can distinguish a model-only call from an agent that uses tools.
- You can explain why the finished result needs **supporting evidence, real tool results, and a not-yet-approved status**.
- You have chosen your learning path and its final cleanup step.

## Troubleshooting

**Do not enable every feature at the start.** A Prompt Agent, File search, function tools, evaluation, and tracing are enough for the first day. Add Preview features, complex networking, and further business integrations only after completing the core result.

## Cleanup

This module creates no resources. Continue to **L01: Prepare an environment you can run**.

<details markdown="1">
<summary>Find the learning path for a capability</summary>

Core capabilities are hands-on. Additional permissions, licenses, and Preview access are action prerequisites, not separate participant roles. Distinguish design-only work from actual execution; see [Feature coverage](#coverage).

</details>

<div class="lab-handoff" markdown="1">

**Keep:** Your selected path, what the purchasing assistant will do, and its prohibited actions. No Microsoft Azure call has been made.

**Continue:** [L01 setup](#l01). If you select the tour or local path on the web, **Next at the page footer** follows that selection; body links describe the core/elective sequence.

</div>
