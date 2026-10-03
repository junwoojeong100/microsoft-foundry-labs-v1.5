> **What you will build:** Your lab project/model settings, a ready PC, and a plan for stopping costs. Check the deployment in L02 and the first call in L03.

<div class="lab-brief" markdown="1">

**Format:** Prepare your PC and inspect a supplied project · only an administrator creates a new Azure environment.

**Start here:** Check whether the instructor supplied project details. Without them, stop after the local exercises.

**What to check:** Keep the data-check result and your project endpoint/model deployment name. L03 verifies the actual connection.

</div>

## Objectives

Separate the **permissions, incorrect endpoints, supported regions, and quota** issues that cause most lab failures before you begin.

## Concepts and lab map

**What you will try:** Find the supplied project and prepare your PC to run the lab files.

**What is it, and why does it matter?** A subscription is a billing scope; a project is a workspace for agents. Sign-in answers “Who are you?”, roles answer “What can you do?”, and quota answers “How much can you use?” Knowing an address does not grant access.

**How do you use it?** Match the portal to your instructor's information, prepare Python, and save the endpoint and deployment name in `.env`. L03 checks the actual connection.

**Where do you run it?** Use the browser for the project and VS Code for the terminal and [.env.example](../../.env.example). The [management script](../../scripts/azure_environment.py) and [infrastructure](../../infra/main.bicep) are administrator references, not required first reading.

## Prerequisites

### Details to obtain from your instructor

| Ask for | Why you need it |
| --- | --- |
| Sign-in account and organization (tenant) | Avoid creating resources because another organization's project list is empty |
| Approved subscription, resource group, and project name | Identify the billing scope and work target |
| Project endpoint and model deployment name | Configure the address and target used by the L03 code |
| Budget, stop owner, and cleanup owner | Know when to stop and what to retain |

If these are missing, **continue local exercises but stop before Azure creation or calls**. If the subscription is absent or access is denied, ask the instructor for these details. Registering a card or obtaining subscription Owner is not a learner setup step.

| Item | Core course | Additional conditions |
| --- | --- | --- |
| Azure | An approved subscription and nonproduction resource group | Do not bypass organizational policies |
| Foundry | A **Foundry project in the new portal** | Different from a hub-based Classic project |
| Model | A chat model supporting Responses and tool use | Check support in L02 |
| Development environment | Python 3.13, Azure CLI 2.86.0 | Local standard-library exercises also work with 3.11+ |
| Data | This guide's English synthetic data in `data/en/` | Do not upload real customer or employee information |
| Budget | A per-person or team limit and someone responsible for stopping usage | Budget alerts do not enforce a hard billing cutoff |

<a id="l01-pc"></a>

### Start on a new PC

Use your organization's approved installation route for [Python 3.13](https://www.python.org/downloads/), [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli), and [VS Code](https://code.visualstudio.com/download). Do not reinstall existing tools. Local-only exercises need neither Azure CLI nor Azure sign-in.

Extract the ZIP and choose **VS Code → File → Open Folder**, selecting the folder containing `samples`, `data`, and `requirements.txt` together. Use **Terminal → New Terminal** for the commands below. This is your PC's terminal, not Azure Cloud Shell or Python's `>>>` prompt. If you see `>>>`, enter `exit()` to leave Python.

In Windows PowerShell, use **`py -3.13`** instead of the following `python3` commands before creating a virtual environment. Afterward use `.venv\Scripts\python.exe`. Execute **only your operating system's block**, not both the macOS/Linux and Windows alternatives.

## Steps

<a id="l01-language"></a>

### 1. Select the English profile and prepare the project

Use a **separate extracted lab folder or clean checkout** for English execution if you also run the Korean labs. Keep its `.env`, `.azure/`, `results/`, virtual environments, and generated Hosted packages separate. Never copy a Korean run's private settings, ownership receipts, or response files into it. You do not need an authoring branch or a repository merge to start the lesson.

Before running any sample, management, or packaging command, select the English data profile in the current terminal.

```bash
export FOUNDRY_LAB_LANGUAGE=en
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — macOS/Linux

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `export FOUNDRY_LAB_LANGUAGE=en` | Selects English synthetic inputs for this terminal and its child processes. Run it again when opening a new terminal. | Changes local process configuration only. No Azure calls, resource changes, or data translation. |

</div>

Windows PowerShell alternative:

```powershell
$env:FOUNDRY_LAB_LANGUAGE = "en"
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Use this instead of the macOS/Linux profile command.

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `$env:FOUNDRY_LAB_LANGUAGE = "en"` | Selects English synthetic inputs for the current PowerShell session and its child processes. Select it again in every new terminal. | Changes local process configuration only. No Azure calls or resource changes. |

</div>

**All later commands assume this per-terminal selection**, including commands in separate server/client terminals. Reselect the profile and the appropriate Python environment after opening a new terminal. The browser's language switch does not set it, and an absent flag keeps the original Korean default. The [English profile manifest](../../data/en/profile-manifest.json) describes the inputs and unchanged business rules. Explicit file options must also point to `data/en/`; the flag does not translate an explicitly supplied Korean file. L14's generated Hosted packages record the selected language in `lab-profile.json`.

**Without an Azure account, continue to [step 4's local checks](#l01-local) now.** Skip project selection, access checks, and CLI sign-in.

1. Open the [Foundry portal](https://ai.azure.com) and sign in with the account specified by your instructor.
2. Check that **New Foundry** is on. Select the supplied project using the selector at the upper left.
3. Compare **Name / Parent resource / Location** in **Manage → Project details** with the instructor's information. Your approved project may have a different name from the example `contoso-workshop-en`.
4. If no project appears or only **Create project** is available, ask for access rather than creating one. Account-free participants can continue with the local checks in step 4 below.

**Selecting a project is not creating one.** Learners using a prepared project skip the administrator path below. The model name in `.env` may remain a placeholder until L02 confirms the deployment. Keep your results in `results/`; do not overwrite published examples in `validation/current/`.

<details class="operator-only" markdown="1">
<summary>Administrators only: create a new environment after scope, cost, and access approval</summary>

The following script creates only a uniquely named new resource group (RG); it does not reuse or delete existing resources. First prepare Python in step 4 and CLI sign-in in step 5 below. Do not execute placeholder commands before confirming models, region, quota, and the approved scope.

```bash
python3.13 scripts/azure_environment.py create --subscription approved-subscription-id --location approved-region --cost-authorization "Approved amount and retention policy" --live
python3.13 scripts/azure_environment.py foundation --chat-model gpt-6-sol --chat-version 2026-09-22 --judge-model supported-judge-model --judge-version actual-judge-version --embedding-model supported-embedding-model --embedding-version actual-embedding-version --model-sku GlobalStandard --capacity 10 --live
python3.13 scripts/azure_environment.py roles --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Administrators only. Learners using a provided environment must not run these commands.

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `create` | `--subscription` identifies the approved subscription, and `--location` specifies the actual region. Inside the quotes after `--cost-authorization`, record the approved amount and retention terms. `--live` permits creation of a new dedicated resource group. | Writes an ownership receipt to `results/azure-environment.json`. This is not a command for reusing an existing resource group. The new group defines the scope of subsequent resource costs. |
| 2. `foundation` | Specify a model ID and version for each of chat, judge, and embedding. `--model-sku` sets the processing scope/deployment type; `--capacity 10` means 10 of that model's capacity units, not a USD 10 spending limit. | Deploys the Foundry resource, project, and models. Check policies and quota and obtain cost approval first. |
| 3. `roles` | Assigns lab roles in the new environment recorded in the ownership receipt. `--live` permits a real run, including permission changes. | Requires administrator privileges. Verify data access after role propagation; do not use this to expand access to other environments. |

</div>

Replace the descriptive placeholders with actual approved values: the subscription ID, permitted region, approved amount and retention policy, supported chat/judge/embedding model IDs, and their actual versions. Check the model catalog, SKU, and quota first,
and obtain approval for the Global, Data Zone, or Standard processing scope. Capacity units vary by model and are not a spending cap.
`infra/main.bicep` deploys only the Foundry account/project and the specified models.
Add Search with `python scripts/azure_environment.py search --live` only when you need L13. `search` is an administrator operation that creates a search service in the owned resource group; it can incur fixed costs even without requests. It does not mean “try one search.”
The ownership record is `results/azure-environment.json`. For partial failures such as RequestConflict,
inspect the original deployment operation and use `foundation --resume` **only for those same owned resources**. `--resume` continues a recorded partial deployment; it does not select a new environment or erase the original error record.

![Azure portal resource group overview for the isolated English Contoso run. Compare its ownership and scope with your English environment receipt.](../../assets/portal/en/18-resource-group.png)

**Reading the screen:** Compare the resource group, location, and ownership tags with `results/azure-environment.json` from the English checkout. Visible resources depend on capture time and filters; the image does not prescribe a fixed resource list or count. Consult the [English capture log](../../content/portal-screenshots.en.json) for its exact scope. An overview is not proof of successful model calls or a passed quality gate.

The captured overview preserves an **inherited organizational diagnostic-policy failure** because its external governance workspace was missing. The English run's own foundation and observability deployments succeeded separately. Do not hide that warning, count it as an owned deployment failure, or change the out-of-scope policy/workspace; refer it to the responsible governance owner.

</details>

### 2. Check roles by who needs to do what

Confirm with the owner that you can **open the project, create an agent, and call the model**. Learners do not need to memorize the complete role table or assign roles themselves.

<details class="operator-only" markdown="1">
<summary>Administrator reference: minimum roles by identity</summary>

| Identity | Starting point for the required scope | Action to verify |
| --- | --- | --- |
| Lab developer | Project `Foundry User`, read access to the parent resource | Create and invoke agents |
| Resource/model administrator | Applicable management permissions, such as resource `Foundry Account Owner` | Deploy projects and models |
| End user | `Foundry Agent Consumer` | Invoke permitted agent endpoints only |
| Project managed identity | Minimum roles required by the connection target | Access Search, Storage, or models |
| Agent identity | Actual runtime tool permissions | Use Toolbox and business APIs |
| Evaluation/tracing user | Project role plus a read role on the log resource | View evaluations and App Insights |
| Quota reader | Subscription `Cognitive Services Usages Reader` | Check usage and deployment eligibility |

Role names have recently changed—for example, **Azure AI User → Foundry User**. The portal may still show an older name. Renaming alone has not changed the role IDs or core permissions. Azure `Owner` or `Contributor` also does not automatically grant Foundry data-plane access.

**Ask the responsible administrator to assign roles.** Do not give every learner subscription Owner access. Check each module for additional tool-specific permissions.

The administrator script resolves the administrator's object ID from the **authenticated Azure Resource Manager (ARM) credential** for scoped role assignments, rather than requiring a separate Microsoft Graph signed-in-user lookup. A Graph-specific Continuous Access Evaluation (CAE) challenge did not block ARM/Foundry authentication in this English run. Diagnose each service's actual response separately and follow organizational access policies.

</details>

### 3. Check region, deployment, and cost

Prepare just one model for L02. Start with a usage-based deployment if your data is synthetic and organizational policy allows it. **PTU, paid Search tiers, GPU managed compute, large Batch jobs, and fine-tuning are not needed for the core course.**
L08's native automated evaluation also requires a separate judge deployment. Do not recreate one the administrator has already provided.

<details class="provenance-note" markdown="1">
<summary>Reference: the earlier English run's capacity decision</summary>

The English run's foundation-model capacity was explicitly increased **10 → 50 → 100** after quota verification for the bounded evaluation workload. The current setting of **100** is a run-specific capacity decision, not a required learner setting or an evaluation pass. Capacity units vary by model and **are not a dollar cap**; retain explicit cost approval and bounded requests before increasing your own deployment capacity.

</details>

The project region, supported model regions, deployment type, and quota are separate conditions. A project in Korea Central does not, by itself, mean that all inference is processed in Korea. L02 covers Global, Data Zone, and geography-based processing scopes.

Review automated evaluation options under **Metrics** in the agent playground. Deselect evaluations you do not need. Playground evaluations can also incur charges. Costs may include File search, Search, Code Interpreter, logs, and the hosted runtime—not just inference.

<a id="l01-local"></a>

### 4. Prepare the local exercise environment

Run one line at a time from your English lab folder, with `FOUNDRY_LAB_LANGUAGE=en` still selected. On Windows use `py -3.13` as explained above.

```bash
python3 samples/workshop.py doctor
python3 samples/workshop.py validate-data
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `doctor` | Shows the Python version, whether `.env` exists, and Azure SDK package installation. It does not check Azure CLI installation, sign-in, connectivity, or repair anything. | Read the diagnostic items in the terminal. No Azure sign-in or model calls. |
| 2. `validate-data` | Locally checks the English learning data's format, scenario IDs, and original split under `data/en/`. | Checks data structure only, not model quality or an independent release exam. |

</div>

The second command prints the following. `dev` and `holdout` name two groups in the bundled, already exposed learning data. For now, check the counts and lack of overlap; this is neither L08's 12-question comparison nor a fresh sealed release test.

```output
Validated 20 cases: dev=10, holdout=10; scenario overlap=0; inventory=3.
```

This check **requires no Azure account, network connection, or external packages**. A `doctor` entry saying `not installed (needed only for --live)` identifies a package needed before Azure calls, not a failure of this local data check.

**For local-only work, stop installation and sign-in here.** Use the same `python3` (Windows: `py -3.13`) for L06's local functions. The virtual environment below and step 5 prepare you for Azure code exercises.

Install packages only when you are ready to call Azure from code.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp -n .env.example .env
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — macOS/Linux

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `python3.13 -m venv .venv` | Uses Python 3.13's `venv` module to create an environment for this folder, separate from global Python packages. | Creates a local `.venv/`. No Azure calls. |
| 2. `source .venv/bin/activate` | Points this terminal's `python` and `pip` at the virtual environment. Select it again in each new terminal. | Changes only the current shell. It does not activate a project or resource. |
| 3. `python -m pip install -r requirements.txt` | Uses the selected Python's pip to install the listed dependencies. `-r` reads a requirements file. | Connects to an approved package repository and changes the local environment. No Azure inference. |
| 4. `cp -n .env.example .env` | Copies the configuration template. `-n` prevents overwriting an existing `.env`. | Creates a local `.env` if none exists. Enter your actual endpoint and deployment name in the next step. |

</div>

Windows PowerShell alternative:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — On Windows, use this instead of the macOS/Linux block above.

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `py -3.13 -m venv .venv` | Selects Python 3.13 through the Windows Python Launcher to create a virtual environment. | Creates only a local `.venv`. |
| 2. `.venv\Scripts\python.exe -m pip install` | Calls the virtual environment's Python directly without activation. Installs packages from `-r requirements.txt`. | Downloads and installs packages. You do not need to weaken the PowerShell execution policy. |
| 3. `if ... Copy-Item` | Uses `Test-Path` to check whether `.env` exists, and copies the template only if it does not. | Preserves existing personal settings. No Azure calls. |

</div>

**One rule for later commands:** `python` means **the Python in this virtual environment**. On Windows, replace every `python ...` with `.\.venv\Scripts\python.exe ...`. Do not change execution policy or reinstall into global Python.

<a id="l01-new-terminal"></a>

#### When you open a new terminal or return another day

Open the same lab folder and run **this one check**. The printed path must contain this folder's `.venv`. Also reselect the [English profile](#l01-language) in the new terminal.

```bash
python -c "import sys; print(sys.executable)"
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `python -c` | The short Python code after `-c` prints the current interpreter path. On Windows replace `python` with `.\.venv\Scripts\python.exe`. | Local inspection only. If the path is wrong, macOS/Linux users rerun `source .venv/bin/activate` from above. Do not reinstall packages. |

</div>

**A successful command using a different Python is not a ready environment.** Check both terminals when opening two in L07.

### 5. Configure endpoints and authentication

![Manage → Project details for contoso-workshop-en, with project, parent resource, region, and Connected resources. Identifying and connection values must remain masked.](../../assets/portal/en/13-project-settings.png)

**Reading the screen:** Under **Manage → Project details**, first compare **Name / Parent resource / Location** with your English environment's records. Put your own **Project endpoint** in the local configuration. In **Connected resources**, read the connection target, Category, and Auth method. Masked areas are not example values to copy; do not reveal connection keys. The [English capture log](../../content/portal-screenshots.en.json) defines the observation scope. Viewing settings does not establish that a connection or permission change succeeded.

Copy the project endpoint from **Manage → Project details** or the project's landing page. **Open `.env` in VS Code**, replace only the right-hand sides of these two `=` signs, and save. Ensure the filename is `.env`, not `.env.txt`. Do not paste this settings block into the terminal.

```env
FOUNDRY_PROJECT_ENDPOINT=https://your-foundry-resource.services.ai.azure.com/api/projects/contoso-workshop-en
FOUNDRY_MODEL_DEPLOYMENT_NAME=your-model-deployment-name
```

Replace `your-foundry-resource` and `your-model-deployment-name` with your actual resource and model deployment names; verify the entire endpoint against your approved English project. **Do not append `/openai/v1` to the project endpoint.** The SDK constructs the correct path. Do not add an API key or copy another run's `.env`.

Set `.env`'s `FOUNDRY_JUDGE_DEPLOYMENT_NAME` to the supplied grading-model deployment **only if running a new evaluation in L08**. Reading the existing results does not require it. Leave unused optional settings empty.

The **`.env`** settings file and **`.venv`** Python folder are different. Saving `.env` does not select Python or sign in to Azure.

```bash
az login
az account show --query "{subscription:name,tenant:tenantId}" -o table
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `az login` | Starts Azure CLI user sign-in. CLI authentication is required separately even if you are signed in to the portal in a browser. | Creates local CLI authentication state. Enter passwords and MFA directly in the authentication screen, never in chat or documentation. |
| 2. `az account show` | `--query` selects only the current subscription name and tenant ID; `-o table` displays them in a readable table. | Checks the target without model requests or resource creation. Compare it with your approved scope. |

</div>

If the selected subscription is wrong, choose it explicitly.

```bash
az account set --subscription "approved-lab-subscription-id"
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `az account set` | Replace the placeholder after `--subscription` with the approved lab subscription ID to select the CLI's default target. | Changes the local CLI's default subscription. It does not grant new permissions or move existing Azure resources. |

</div>

The sample uses **AzureCliCredential** locally. In production, choose credentials suited to the deployment environment, such as an appropriate managed identity.

## Success criteria

You have selected the English profile, recorded the separate project, model, roles, region, and person responsible for costs, and the local data checks pass. Verify a successful Azure connection separately with **the live response in L03**.

## Troubleshooting

**For 403, check roles first; for 404, check the endpoint and deployment name; for 429, check quota.** A private-endpoint environment requires an approved VPN or development environment inside the VNet. Do not enable public access on your own to resolve a problem.

If SDK installation fails through your organization's mirror, request synchronization of the approved mirror. A package being available on public PyPI does not authorize bypassing organizational policy to install it.

## Cleanup

Record the resource group and its owner, and read L12's shutdown checklist in advance. Do not share or commit `.env`. The `.env` used in this lab should contain no secrets.
