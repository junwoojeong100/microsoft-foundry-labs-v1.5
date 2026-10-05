> **What you will build:** Your own lab resource group, Foundry project, model deployments, telemetry connection, and Python environment.

<div class="lab-brief" markdown="1">

**Format:** Prepare the PC → verify sign-in and permissions → create a dedicated environment → configure endpoints and telemetry.

**Start here:** Extract the kit, open it in VS Code, and identify your Azure subscription, region, and budget.

**What to check:** Your portal resources match `results/azure-environment.json`. The first model request is in L03.

</div>

## Objectives

**You create the environment used throughout the labs.** Creation, inspection, and role-assignment permissions are prerequisites for actions, not separate participant personas.

## Concepts and lab map

**What you will try:** Prepare a Foundry project, models, access, telemetry, and local Python.

**What is it, and why does it matter?** A subscription is a billing scope, a resource group groups resources, and a project is the agent workspace. Sign-in identifies the caller; RBAC permits actions; quota provides capacity.

**How do you use it?** Create a dedicated environment and compare actual portal names and endpoints with `.env` and the ownership record. An endpoint alone does not grant access.

**Where do you run it?** Use your PC's VS Code terminal, then inspect the results in Azure and Foundry portals. The [setup script](../../scripts/azure_environment.py) and [Bicep](../../infra/main.bicep) define the resources created.

## Prerequisites

| Item | What to verify |
| --- | --- |
| Azure account and active subscription | You can sign in and the subscription is Enabled |
| Creation permission | Permission to create a resource group and deploy Foundry/telemetry resources inside it |
| Role-assignment permission | `Microsoft.Authorization/roleAssignments/write` at the target scope; `Contributor` alone cannot grant roles |
| Quota-read permission | `Cognitive Services Usages Reader` or equivalent subscription permission |
| Region and budget | Supported models, permitted processing scope, spend limit, stop criteria, and retention deadline |
| PC | Python 3.13, Azure CLI 2.86.0 baseline, VS Code, internet, and an approved package source |

Verify permissions even in your own subscription. In an organizational subscription, secure the required scoped permissions and cost approval before proceeding. If an action is not permitted, leave it blocked; do not disable security or broaden subscription-wide access. Local exercises work without Azure access but **do not complete the live Foundry path**.

<a id="l01-pc"></a>

## Steps

### 1. Prepare the PC and lab files

Prepare Python, Azure CLI, and VS Code through organization-approved paths. **Check existing tools first and install only what is missing.** Prefer your organization's software portal, approved installers, and package sources. Follow the official download steps below only when permitted. If installation or downloads are blocked, obtain an approved distribution path; do not bypass security warnings, certificate validation, or execution policies.

| Tool | Its role in this lab | Ready when |
| --- | --- | --- |
| Python 3.13 | Runs actual Python code and the Foundry SDK on your PC. | The version check prints `Python 3.13.x`. |
| Azure CLI | Signs into Azure and creates or inspects lab resources. | `az version` prints an `azure-cli` version. This kit's baseline is 2.86.0. |
| VS Code | Displays and edits code and opens a PC terminal. | You can open the lab folder and a Python file. Prepare the Python extension below. |

<a id="l01-python"></a>

#### Install and check Python 3.13

**Windows**

1. On [Python Downloads](https://www.python.org/downloads/windows/), choose a **3.13.x release** and download the installer for your PC. The latest version shown on the landing page is not necessarily 3.13. Use the regular installer, not the `embeddable package`.
2. Run the approved installer. In the regular installer, select **Add python.exe to PATH** and include `pip` and the Python launcher (`py`). Use **Install Now** or the installation options required by your organization.
3. Close existing terminals and open a new **PowerShell** window. Explicitly select 3.13 with:

```powershell
py -3.13 --version
```

<div class="command-explanation" markdown="1">

**Command walkthrough — Windows**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `py -3.13 --version` | Prints the installed Python 3.13 version. | Local check; no installation, sign-in, or Azure request. |

</div>

**macOS**

1. On [Python Downloads](https://www.python.org/downloads/macos/), choose a **3.13.x release with an installer**. The **macOS 64-bit universal2 installer** (`.pkg`) supports Apple Silicon and Intel Macs.
2. Open the approved `.pkg`, verify the version and destination, and follow the installer. Do not remove or replace Apple's system Python.
3. For the python.org distribution, complete its default certificate setup with **Applications → Python 3.13 → Install Certificates.command**. Use approved certificate and proxy settings if your organization requires them; do not disable certificate validation.

**Linux — Ubuntu/Debian example**

Run the following only if an organization-approved package source provides `python3.13` and `python3.13-venv`. Availability depends on the distribution. If those packages are unavailable, obtain an approved Python 3.13 distribution instead of adding an arbitrary external repository.

```bash
sudo apt install python3.13 python3.13-venv
```

<div class="command-explanation" markdown="1">

**Command walkthrough — Ubuntu/Debian**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `apt install ...` | Installs Python 3.13 and virtual-environment support. | Approved package download and PC changes; no Azure request. |

</div>

On macOS/Linux, open a new terminal and check:

```bash
python3.13 --version
```

<div class="command-explanation" markdown="1">

**Command walkthrough — macOS/Linux**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `python3.13 --version` | Prints the Python 3.13 version you will run. | The `x` in `Python 3.13.x` is the actual patch number; no Azure request. |

</div>

Having only 3.12, 3.14, or another version does not complete this step. Keep other applications' Python installations and prepare 3.13 separately for this lab.

<a id="l01-azure-cli"></a>

#### Install and check Azure CLI

**Windows**

1. Open **Microsoft Installer (MSI)** in the [official Windows installation instructions](https://learn.microsoft.com/cli/azure/install-azure-cli-windows). Use the 64-bit MSI on a typical x64 PC; for another architecture, check official support and your organization's distribution.
2. If you need the kit baseline of 2.86.0, use **Specific version** on that page or the [official 2.86.0 x64 MSI](https://azcliprod.blob.core.windows.net/msi/azure-cli-2.86.0-x64.msi). Run the approved MSI and complete setup. Follow your organization's approval process for PC changes.
3. Fully close and reopen PowerShell and VS Code after installation.

**macOS**

If organization-approved [Homebrew](https://docs.brew.sh/Installation) is **already available**, follow the [official macOS installation instructions](https://learn.microsoft.com/cli/azure/install-azure-cli-macos) and run the following. If Homebrew is unavailable or not permitted, obtain an approved installation path first.

If you need Homebrew itself, use an approved distribution from your organization's software portal. When official downloads are permitted on an Apple Silicon Mac, you can also install the `.pkg` from the official release linked in the Homebrew instructions above. Check OS/CPU requirements and post-installation PATH setup, then verify `brew --version` in a new terminal before continuing below.

```bash
brew install azure-cli
```

<div class="command-explanation" markdown="1">

**Command walkthrough — macOS**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `brew install azure-cli` | Installs Homebrew's Azure CLI package and required dependencies. | Download and PC changes; separate from preparing the lab's Python 3.13; no Azure request. |

</div>

**Linux — Ubuntu/Debian example**

Check supported distributions in the [official Linux installation instructions](https://learn.microsoft.com/cli/azure/install-azure-cli-linux?pivots=apt). Run the following only when a Microsoft package source or organizational mirror is **already approved and configured** and provides `azure-cli`. Otherwise, complete the approved repository setup first; do not blindly execute downloaded scripts.

```bash
sudo apt install azure-cli
```

<div class="command-explanation" markdown="1">

**Command walkthrough — Ubuntu/Debian**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `apt install azure-cli` | Installs Azure CLI from the configured, approved source. | Download and PC changes; no Azure sign-in or resource creation. |

</div>

**Check on every OS:** Run this in a new PC terminal. The same command works in PowerShell.

```bash
az version
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `az version` | Prints local Azure CLI and installed extension versions. | Not a sign-in, permission, or Azure connectivity check; no model call or resource creation. |

</div>

Record the `azure-cli` value. Current MSI, Homebrew, and apt packages may differ from the kit baseline of 2.86.0. With another approved version, check subsequent commands' behavior; do not arbitrarily upgrade or downgrade. **Azure sign-in is in step 2 below.**

<a id="l01-vscode"></a>

#### Install VS Code and open the lab folder

**Windows:** On [VS Code Downloads](https://code.visualstudio.com/download), choose the **User Installer** for your PC and follow approved installation options. Use your organization's distribution when available. Open **Visual Studio Code** from the Start menu.

**macOS:** On the same page, choose Apple Silicon, Intel, or Universal for your Mac. Open the distribution's `.dmg` or `.zip`, move **Visual Studio Code.app → Applications**, and launch it.

**Linux:** Choose the `.deb` or `.rpm` for your distribution and install it through an approved software installer. Apply only approved settings if it asks to add a package source.

In VS Code, check the installed version under **Help → About** (macOS: **Code → About Visual Studio Code**). You can use the folder-opening steps below without a `code` terminal command.

Extract the ZIP and use **VS Code → File → Open Folder** to open the folder containing `samples`, `data`, and `requirements.txt`. Choose **Terminal → New Terminal**. This is your PC shell, not the browser address bar, Cloud Shell, or Python's `>>>` prompt. Exit that prompt with `exit()` if necessary.

In **Extensions** on the left, search for `Python` and check the publisher **Microsoft** and extension ID **`ms-python.python`**. Do not reinstall it if present; otherwise, install it through your organization's permitted extension distribution path. The extension does not install the Python interpreter itself. If extensions are not permitted, the PC terminal commands below still provide the lab execution path.

**If preparation is blocked**

| Symptom | Check or action |
| --- | --- |
| `py` or `python3.13` is not found | Retry in a new terminal, then check the approved installation path, launcher, and PATH. If Windows `python` opens the Store, use the explicit `py -3.13` check above. |
| `az` is not found | Reopen VS Code after installation and check that the approved CLI installation path is in PATH. |
| Download, certificate, or proxy errors | Check approved sources, proxies, and certificates. Do not bypass errors by disabling SSL validation or changing security policy. |
| Extension installation is blocked | Use an approved extension distribution or continue through the terminal path. |

<a id="l01-language"></a>

#### Select the English data profile

Use a separate lab folder with its own `.env`, `.azure/`, and `results/`. Set the profile in every terminal **before** running a sample:

```bash
export FOUNDRY_LAB_LANGUAGE=en
```

<div class="command-explanation" markdown="1">

**Command walkthrough — macOS/Linux**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `export FOUNDRY_LAB_LANGUAGE=en` | Selects English synthetic inputs for this terminal. | Local environment only; the browser language switch does not select runtime data. |

</div>

On Windows, use this **instead**:

```powershell
$env:FOUNDRY_LAB_LANGUAGE = "en"
```

<div class="command-explanation" markdown="1">

**Command walkthrough — Windows**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `$env:FOUNDRY_LAB_LANGUAGE = "en"` | Selects English synthetic inputs in this PowerShell session. | Repeat in a new terminal; do not reuse Korean ownership records. |

</div>

<a id="l01-local"></a>

#### Check the lab files and create a virtual environment

Run the two standard-library checks first. On Windows, use `py -3.13` instead of `python3.13`.

```bash
python3.13 samples/workshop.py doctor
python3.13 samples/workshop.py validate-data
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `doctor` | Prints Python/SDK availability and whether `.env` exists. | Local inspection; not CLI sign-in or Azure connection validation. |
| 2. `validate-data` | Checks synthetic data shape, scenario separation, and inventory. | Data validation, not model-quality evaluation. |

</div>

```output
Validated 20 cases: dev=10, holdout=10; scenario overlap=0; inventory=3.
```

`not installed (needed only for --live)` means the SDK installation below is still needed. These twenty cases are the existing dev/holdout data, not L08's fixed twelve-question comparison.

macOS/Linux:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp -n .env.example .env
```

<div class="command-explanation" markdown="1">

**Command walkthrough — macOS/Linux**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `venv .venv` | Creates this folder's Python environment. | Local folder creation. |
| 2. `source .../activate` | Selects it in the current terminal. | Reselect it in each new terminal. |
| 3. `pip install -r ...` | Installs the declared SDK dependencies. | Package download/local installation; no Azure request. |
| 4. `cp -n ...` | Copies the settings template only if absent. | Preserves existing `.env`. |

</div>

Use this block **instead** in Windows PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

<div class="command-explanation" markdown="1">

**Command walkthrough — Windows**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `py -3.13 -m venv` | Creates a Python 3.13 environment. | Local folder creation. |
| 2. `.venv\Scripts\python.exe -m pip ...` | Installs into that environment directly. | No activation or execution-policy change is needed. |
| 3. `if ... Copy-Item` | Copies `.env` only when absent. | Does not overwrite existing settings. |

</div>

Later `python` means this environment's Python. On Windows, replace it with `.\.venv\Scripts\python.exe`.

<a id="l01-interpreter"></a>

#### Select the lab Python in VS Code

If you prepared the Python extension, also use the `.venv` created above for the editor's run and debug actions.

1. Open `samples/first_response.py` to display a Python file.
2. Open the Command Palette with **Ctrl+Shift+P** (macOS: **Cmd+Shift+P**) and choose **Python: Select Interpreter**.
3. Select this lab folder's **Python 3.13 (`.venv`)**. If it is missing, use **Enter interpreter path** to select `.venv/bin/python` on macOS/Linux or `.venv\Scripts\python.exe` on Windows.
4. Check the environment in the window's bottom Status Bar. Do not assume that editor selection changes an existing terminal's interpreter; also run the path check below. Continue using `.\.venv\Scripts\python.exe` for Windows terminal commands.

<a id="l01-new-terminal"></a>

#### Return in a new terminal or another day

Select the same folder/environment and reselect the English profile. Check the path in each terminal, including both L07 terminals:

```bash
python -c "import sys; print(sys.executable)"
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `python -c` | Prints the current interpreter path. | If it is not this folder's `.venv`, reselect the environment instead of reinstalling packages. |

</div>

### 2. Check sign-in, subscription, permissions, and costs

```bash
az login
az account show --query "{subscription:name,id:id,tenant:tenantId,state:state}" -o table
az account set --subscription "actual-subscription-id"
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `az login` | Starts CLI user authentication. | Enter passwords/MFA directly in the authentication screen; portal sign-in is separate. |
| 2. `az account show` | Shows the subscription, tenant, and state. | Inspection only; no model call or resource creation. |
| 3. `az account set` | Replaces the placeholder with your subscription ID and selects it. | Changes the local CLI target, not permissions. |

</div>

In Azure portal **Subscriptions → Access control (IAM) → View my access**, verify the prerequisite permissions. Creation and role assignment are different capabilities. Grant subsequent roles only at your lab project/resource scopes.

Record **the amount, services, stop time, and retention deadline**. Budget alerts, TPM/RPM, and log-ingestion limits are not hard spending caps. At the limit, stop new requests/schedules and use [L19](#l12) to inspect remaining resources.

### 3. Create your dedicated resource group

The default path creates a **new dedicated environment** using the bundled code, then inspects it in the portal. It does not alter a shared environment. Generated names and ownership tags are recorded in `results/azure-environment.json`, which later evaluation, retrieval, and deployment use to verify scope.

```bash
python scripts/azure_environment.py create
python scripts/azure_environment.py create --subscription actual-subscription-id --location permitted-region --cost-authorization "Approved amount, service scope, and retention deadline" --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough — read the plan, then supply your actual values.**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `create` | Prints the dedicated-environment plan. | `PLAN ONLY`; no Azure request or sign-in/permission validation. |
| 2. `create ... --live` | Records scope and cost authorization and creates a unique resource group. | Actual Azure creation; no reuse or overwrite of an existing group/receipt. |

</div>

In Azure portal **Resource groups**, verify the returned name, region, and tags. Do not share or commit `.env` or the receipt. If a receipt already exists, inspect its resources instead of deleting it and restarting.

![Resource-group example. Compare your own generated group, region, and ownership tags in Azure portal before proceeding.](../../assets/portal/en/18-resource-group.png)

### 4. Create the Foundry project, models, and required roles

`foundation` uses [main.bicep](../../infra/main.bicep) to create **a Foundry resource/project and three chat/judge/embedding deployments**. Chat supports the core labs, judge supports L08, and embedding supports optional L11/L15. It sends no inference request.

This kit pins `gpt-6-sol / 2026-09-22`, `gpt-4.1 / 2025-04-14`, and `text-embedding-3-small / 1`. Verify availability in your subscription/region. If unavailable, record the limitation and stop; do not silently substitute a model and claim equivalent validation.

```bash
python scripts/azure_environment.py foundation --learners 1 --max-capacity 100
python scripts/azure_environment.py foundation --chat-model gpt-6-sol --chat-version 2026-09-22 --judge-model gpt-4.1 --judge-version 2025-04-14 --embedding-model text-embedding-3-small --embedding-version 1 --model-sku GlobalStandard --learners 1 --max-capacity 100 --live
python scripts/azure_environment.py roles --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `foundation` | Shows the per-learner TPM/RPM and capacity-sizing plan. | Local calculation; not live catalog/quota verification. |
| 2. `foundation ... --live` | Checks the actual catalog/quota and deploys the project and models in the owned group. | Real creation; capacity ceiling 100 per deployment is not money. Converts model-specific units and verifies actual limits afterward. |
| 3. `roles --live` | Assigns the current user/project identity scoped data roles on the project and parent resource. | Access change requiring `roleAssignments/write`; no subscription-wide role is created. |

</div>

**Portal check:** In [Foundry](https://ai.azure.com), enable **New Foundry**, open your project, and compare **Manage → Project details** Name/Parent resource/Location with the receipt. Under **Build → Models → Deployments**, verify `contoso-chat`, `contoso-judge`, and `contoso-embedding` are ready. Do not create them again in the portal.

| Creation code | What to inspect in the portal |
| --- | --- |
| RG creation in `create` | Unique Azure Resource groups name and ownership tags |
| Foundry account/project in `foundation` | Project name, parent resource, and region |
| Bicep model deployments | Model ID/version and deployment names such as `contoso-chat` |
| Scoped assignments in `roles` | Caller/managed identity and scope in the resource's IAM |

Preserve the original error and deployment operations after partial failure. Use `foundation --resume --live` only for the same owned partial deployment, with **the same model/SKU arguments**. It does not select a new environment or erase previous failure records.

### 5. Connect telemetry and complete local settings

Connect telemetry **before the first agent request**, so L10 can inspect L04 and later runs:

```bash
python scripts/azure_environment.py monitoring
python scripts/azure_environment.py monitoring --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `monitoring` | Prints the telemetry-resource/connection plan. | No Azure request. |
| 2. `monitoring --live` | Creates Log Analytics, Application Insights, and the project connection in the owned group. | Collection/retention charges may apply; a recorded existing connection is not overwritten. |

</div>

Inspect the connection under **Agents → Traces** or **Manage → Project details → Connected resources**. Querying logs requires read access to the target Application Insights/Log Analytics resources. If necessary, assign scoped `Log Analytics Reader` or the required minimum equivalent in your resource IAM. Protected tables may require additional access.

Model/agent SDK requests use Entra authentication. The bundled [observability.bicep](../../infra/observability.bicep) references the telemetry connection string inside Azure without printing it. This is not a claim of Entra-authenticated trace ingestion.

![Project settings example. Locate the project, parent resource, region, and Connected resources under Manage → Project details.](../../assets/portal/en/13-project-settings.png)

Open `.env` in VS Code and save your actual values. This is **file configuration**, not a terminal command:

```env
FOUNDRY_PROJECT_ENDPOINT=https://actual-resource.services.ai.azure.com/api/projects/contoso-workshop-en
FOUNDRY_MODEL_DEPLOYMENT_NAME=contoso-chat
FOUNDRY_JUDGE_DEPLOYMENT_NAME=contoso-judge
FOUNDRY_EMBEDDING_DEPLOYMENT_NAME=contoso-embedding
```

Copy `FOUNDRY_PROJECT_ENDPOINT` from receipt `project_endpoint` or Home's **Project endpoint**; do not append `/openai/v1`. Compare deployment names with receipt `model_deployments`. `.env` and `.venv` are different; do not add API keys.

The following client setup **uses** the existing project; it does not create resources or grant roles:

```python
from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential

with (
    AzureCliCredential(process_timeout=30) as credential,
    AIProjectClient(endpoint=project_endpoint, credential=credential, retry_total=0) as project,
    project.get_openai_client(max_retries=0, timeout=60.0) as client,
):
    print("Client configured; no model request sent.")
```

## Success criteria

You created your dedicated resource group, project, three models, and telemetry connection and checked permissions, region, and budget. Local data checks pass; the portal, `.env`, and `results/azure-environment.json` identify the same English environment. A plan/client configuration is not a successful model request. Continue to [L02](#l02) to inspect your deployments.

## Troubleshooting

For 401, check CLI authentication; for 403, check action-specific permissions and networking; for deployment failure, check model, region, quota, and capacity. Private endpoints require an approved VPN/VNet path, not a public-access bypass. For installation failures, check the interpreter and permitted package source.

## Cleanup

Do not delete resources yet. Retain your ownership record and deadline, then review schedules and costs in L19. This module creates an environment; it does not validate answer quality.
