> **What you will build:** Your own lab resource group, Microsoft Foundry project, model deployments, telemetry connection, and Python environment.

<div class="lab-brief" markdown="1">

**Format:** Prepare your execution environment → verify sign-in and permissions → create a dedicated environment → configure endpoints and telemetry.

**Start here:** Check your Microsoft Azure subscription, permissions, and budget, then open [GitHub Codespaces](#l01-codespaces) and use its prepared terminal.

**What to check:** Your portal resources match `results/azure-environment.json`. The first model request is in L03.

</div>

## Objectives

**You create the environment used throughout the labs.** Check permissions for creation, inspection, and role assignment separately. Leave an action blocked until its required permission is available.

## Concepts and lab map

**What you will try:** Check Python in Codespaces, then prepare a Microsoft Foundry project, models, access, and telemetry.

**What is it, and why does it matter?** A subscription is a billing scope, a resource group (RG) groups resources, and a project is the agent workspace. Sign-in identifies the caller; RBAC permits actions; quota provides capacity.

**How do you use it?** Create a dedicated environment and compare actual portal names and endpoints with `.env` and the ownership record (`results/azure-environment.json`). An endpoint alone does not grant access.

**Where do you run it?** The default is the **Codespaces terminal in browser VS Code**. Inspect results in Microsoft Azure and Microsoft Foundry portals. The [setup script](../../scripts/azure_environment.py) and [Bicep](../../infra/main.bicep) define the resources created.

## Prerequisites

| Item | What to verify |
| --- | --- |
| Microsoft Azure account and active subscription | You can sign in and the subscription is Enabled |
| Creation permission | Permission to create a resource group and deploy Microsoft Foundry/telemetry resources inside it |
| Role-assignment permission | `Microsoft.Authorization/roleAssignments/write` at the target scope; `Contributor` alone cannot grant roles |
| Quota-read permission | `Cognitive Services Usages Reader` or equivalent subscription permission |
| Region and budget | Supported models, permitted processing scope, spend limit, stop criteria, and retention deadline |
| Default environment | Browser, GitHub account, repository access, and approved Codespaces usage/cost scope. Repository configuration prepares Python 3.13, Azure CLI, Azure Developer CLI (azd), and core/MCP packages |

Verify permissions even in your own subscription. In an organizational subscription, secure the required scoped permissions and cost approval before proceeding. If an action is not permitted, leave it blocked; do not disable security or broaden subscription-wide access. Local exercises work without Microsoft Azure access but **do not complete the live Microsoft Foundry path**.

## Steps

**Follow these five steps in order.** Move on only when a step's result is correct. If a step is already done, compare it with the records from the same environment instead of creating it again.

| Step | What to do | Check before moving on |
| --- | --- | --- |
| [1. Prepare Codespaces](#l01-codespaces) | Check tools and data in the prepared terminal | Python 3.13, your `.venv`, and local checks pass |
| [2. Sign in and confirm scope](#l01-sign-in) | Confirm your account, subscription, permissions, region, and cost | An approved scope and budget |
| [3. Dedicated resource group](#l01-resource-group) | Read the creation plan, then run only the approved scope | Your RG in `results/azure-environment.json` |
| [4. Project, models, and roles](#l01-4-create-the-foundry-project-models-and-required-roles) | Read the deployment plan → create for real → grant the required roles | Your project, three models, and usable access |
| [5. Telemetry and settings](#l01-settings) | Connect logs and save `.env` | Portal, `.env`, and ownership record match one environment |

If you do not yet have Microsoft Azure access, stop after **step 1** and continue to [L06 local functions](#l06). When you resume in a new terminal or on another day, start with the [interpreter check](#l01-new-terminal).

<a id="l01-1-prepare-the-pc-and-lab-files"></a>

### 1. Start in GitHub Codespaces

**GitHub Codespaces is this guide's default environment.** Work in your browser without installing Python, CLI, VS Code, or Docker on your PC. Codespaces is a remote Linux development environment, not a Microsoft Foundry project. Expand the **PC alternative** below only when needed.

<section class="codespaces-path" markdown="1">

<a id="l01-codespaces"></a>

#### Create a Codespace → check readiness → continue the same labs

**Required:** A GitHub account, read access to this repository, organizational permission to use Codespaces, and an approved cost scope. Microsoft Azure subscription/access is separate and needed for the live labs. Codespaces does not automatically connect to your organization's private endpoint/VNet. Without a permitted network route, use local exercises rather than changing security settings.

1. Open [this lab repository](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5), select the default branch `main` (it contains `.devcontainer/devcontainer.json`), then **Code → Codespaces → … → New with options**. There is no need to download the ZIP again or run `git clone`.
2. Review **who pays, available allowance, Region, and Machine type**, then select **Create codespace**. Do not assume free use; check first.
    - A small 2-core configuration is a starting point for core labs; use an organization-approved option.
    - This Region locates the development environment, not your subsequent Microsoft Azure resources or model-processing scope.
    - [GitHub usage and costs](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces) are separate from Microsoft Azure charges.
3. Even after browser VS Code opens, **wait for post-create setup to finish** and display `Lab tools ready.`.
    - The repository configuration prepares Python 3.13, Azure CLI, Azure Developer CLI (azd), Bicep, the Python extension, `.venv`, and core/MCP packages, and copies the `.env` template only if absent.
    - It does not sign into Microsoft Azure, create resources, or grant roles.
4. Open **Terminal → New Terminal** in the lab root containing `samples`, `data`, and `requirements.txt`. **This is Linux/Bash even on a Windows PC**, so do not substitute PowerShell commands. Select the English data profile before the checks:

```bash
export FOUNDRY_LAB_LANGUAGE=en
python --version
python -c "import sys; print(sys.executable)"
az version
python samples/workshop.py doctor
python samples/workshop.py validate-data
```

<div class="command-explanation" markdown="1">

**Command walkthrough — Codespaces readiness**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `export FOUNDRY_LAB_LANGUAGE=en` | Selects English synthetic data for this terminal. | Repeat in every new terminal; do not reuse Korean ownership records. |
| 2. `python --version` | Checks the selected Python version. | `Python 3.13.x`; no Microsoft Azure request. |
| 3. `python -c` | Reads the actual interpreter path. | Must be this lab folder's `.venv/bin/python`. |
| 4. `az version` | Reads the installed CLI version. | `azure-cli` 2.86.0 baseline; not a sign-in check. |
| 5. `doctor` | Checks the SDK installation and the `.env` format, offline. | Core SDKs must be installed. At this point `.env` still holds the example values, so `project endpoint: not set yet` is expected. This does not test the endpoint. |
| 6. `validate-data` | Checks the bundled synthetic data structure. | Twenty cases, ten dev, ten holdout, three inventory rows; not model evaluation. |

</div>

**Continue:** If the checks match, go to **[2. Sign-in, subscription, permissions, and costs](#l01-sign-in)**. The collapsed alternatives/resumption notes are not steps to perform now. Without Microsoft Azure prerequisites, use [L06 local functions](#l06). Fill the project values in `.env` in step 5, after creating the resources.

| Where you are blocked | Next action |
| --- | --- |
| Codespaces menu missing or creation denied | Check repository access, organizational permission, and GitHub usage. Expand the [PC alternative](#l01-pc) if Codespaces is not permitted. |
| No `Lab tools ready.` or package installation fails | Inspect the first creation-log error and approved package access. After resolving it, rerun `bash .devcontainer/post-create.sh` in the same terminal. Existing `.env` and ownership records are preserved. |
| Wrong interpreter path | Open a new terminal or run `source .venv/bin/activate`, then recheck. Do not recreate Microsoft Azure resources. |

On another day, restart **the same Codespace** from [Your Codespaces](https://github.com/codespaces). Its `.env` and `results/` belong to that environment; do not assume they transfer automatically to a new Codespace. Use a separate Codespace per language and do not commit results or authentication data. **[Stop the Codespace in L19](#l12-codespaces)**; closing a browser tab does not stop it. azd is already installed; prepare `.venv-live` or `.venv-advanced` only when choosing the corresponding elective.

[Official creation instructions](https://docs.github.com/en/codespaces/developing-in-a-codespace/creating-a-codespace-for-a-repository) · [Dev-container configuration](https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/adding-a-dev-container-configuration/introduction-to-dev-containers)

</section>

<details class="environment-option pc-setup" markdown="1">
<summary>Only if you need another environment: prepare your PC (Windows/macOS/Linux)</summary>

<a id="l01-pc"></a>

**Do not run this section in Codespaces.** Only for the PC path, extract the lab ZIP and prepare the tools/environment below. Rejoin the same step 2 afterward; do not mix `.env` or ownership records between environments.

**Already installed? Do not repeat installation.** Check versions for your OS, then select the [English profile](#l01-language), [prepare files and the virtual environment](#l01-local), and [select Python](#l01-interpreter). For a first installation, follow **only your OS's sections** below. Without Microsoft Azure access, complete PC/local preparation and leave step 2 onward pending.

Prepare Python, Azure CLI, and VS Code through organization-approved paths. **Check existing tools first and install only what is missing.** Prefer your organization's software portal, approved installers, and package sources. Follow the official download steps below only when permitted. If installation or downloads are blocked, obtain an approved distribution path; do not bypass security warnings, certificate validation, or execution policies.

| Tool | Its role in this lab | Ready when |
| --- | --- | --- |
| Python 3.13 | Runs actual Python code and the Microsoft Foundry SDK on your PC. | The version check prints `Python 3.13.x`. |
| Azure CLI | Signs into Microsoft Azure and creates or inspects lab resources. | `az version` prints an `azure-cli` version. This kit's baseline is 2.86.0. |
| VS Code | Displays and edits code and opens a PC terminal. | You can open the lab folder and a Python file. Prepare the Python extension below. |

<a id="l01-python"></a>

#### Install and check Python 3.13

**Windows**

<details class="setup-detail" markdown="1">
<summary>Only if Python 3.13 is missing: Windows installation</summary>

1. On [Python Downloads](https://www.python.org/downloads/windows/), choose a **3.13.x release** and download the installer for your PC. The latest version shown on the landing page is not necessarily 3.13. Use the regular installer, not the `embeddable package`.
2. Run the approved installer. In the regular installer, select **Add python.exe to PATH** and include `pip` and the Python launcher (`py`). Use **Install Now** or the installation options required by your organization.
3. Close existing terminals and open a new **PowerShell** window. Explicitly select 3.13 with:

</details>

```powershell
py -3.13 --version
```

<div class="command-explanation" markdown="1">

**Command walkthrough — Windows**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `py -3.13 --version` | Prints the installed Python 3.13 version. | Local check; no installation, sign-in, or Microsoft Azure request. |

</div>

<details class="setup-detail" markdown="1">
<summary>Only if Python 3.13 is missing: macOS/Linux installation</summary>

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
| 1. `apt install ...` | Installs Python 3.13 and virtual-environment support. | Approved package download and PC changes; no Microsoft Azure request. |

</div>

</details>

On macOS/Linux, open a new terminal and check:

```bash
python3.13 --version
```

<div class="command-explanation" markdown="1">

**Command walkthrough — macOS/Linux**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `python3.13 --version` | Prints the Python 3.13 version you will run. | The `x` in `Python 3.13.x` is the actual patch number; no Microsoft Azure request. |

</div>

Having only 3.12, 3.14, or another version does not complete this step. Keep other applications' Python installations and prepare 3.13 separately for this lab.

<a id="l01-azure-cli"></a>

#### Install and check Azure CLI

<details class="setup-detail" markdown="1">
<summary>Only if az is missing: Azure CLI installation by OS</summary>

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
| 1. `brew install azure-cli` | Installs Homebrew's Azure CLI package and required dependencies. | Download and PC changes; separate from preparing the lab's Python 3.13; no Microsoft Azure request. |

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
| 1. `apt install azure-cli` | Installs Azure CLI from the configured, approved source. | Download and PC changes; no Microsoft Azure sign-in or resource creation. |

</div>

</details>

**Check on every OS:** Run this in a new PC terminal. The same command works in PowerShell.

```bash
az version
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `az version` | Prints local Azure CLI and installed extension versions. | Not a sign-in, permission, or Microsoft Azure connectivity check; no model call or resource creation. |

</div>

Record the `azure-cli` value. Current MSI, Homebrew, and apt packages may differ from the kit baseline of 2.86.0. With another approved version, check subsequent commands' behavior; do not arbitrarily upgrade or downgrade. **Microsoft Azure sign-in is in step 2 below.**

<a id="l01-vscode"></a>

#### Install VS Code and open the lab folder

<details class="setup-detail" markdown="1">
<summary>Only if VS Code is missing: installation by OS</summary>

**Windows:** On [VS Code Downloads](https://code.visualstudio.com/download), choose the **User Installer** for your PC and follow approved installation options. Use your organization's distribution when available. Open **Visual Studio Code** from the Start menu.

**macOS:** On the same page, choose Apple Silicon, Intel, or Universal for your Mac. Open the distribution's `.dmg` or `.zip`, move **Visual Studio Code.app → Applications**, and launch it.

**Linux:** Choose the `.deb` or `.rpm` for your distribution and install it through an approved software installer. Apply only approved settings if it asks to add a package source.

</details>

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
| 1. `doctor` | Prints Python/SDK availability and whether `.env` exists. | Local inspection; not CLI sign-in or Microsoft Azure connection validation. |
| 2. `validate-data` | Checks synthetic data shape, scenario separation, and inventory. | Data validation, not model-quality evaluation. |

</div>

```output
Validated 20 cases: dev=10, holdout=10; scenario overlap=0; inventory=3.
```

`not installed (needed only for --live)` means the SDK installation below is still needed. These twenty cases are the existing dev/holdout data, not L08's fixed twelve-question comparison.

Create and install into the virtual environment once. If this folder already has a prepared `.venv`, use [Return in a new terminal](#l01-new-terminal) instead.

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
| 3. `pip install -r ...` | Installs the declared SDK dependencies. | Package download/local installation; no Microsoft Azure request. |
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

</details>

<details class="resume-setup" markdown="1">
<summary>Only when resuming or opening another terminal: recheck Python</summary>

<a id="l01-new-terminal"></a>

#### Return in a new terminal or another day

In the same Codespace, open **the same lab folder → Terminal → New Terminal** in VS Code. Do not recreate the environment or reinstall packages. Use the Bash commands below to recheck readiness, including in both L07 terminals.

**Codespaces terminal**

```bash
source .venv/bin/activate
export FOUNDRY_LAB_LANGUAGE=en
python -c "import sys; print('Python', sys.version.split()[0]); print(sys.executable)"
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `source .venv/bin/activate` | Selects the core lab's Python in this terminal. | Local shell change only. |
| 2. `export FOUNDRY_LAB_LANGUAGE=en` | Reselects English synthetic inputs in this terminal. | Does not change the web reader language or any Microsoft Azure resource. |
| 3. `python -c` | Prints the current interpreter **version and path**. | Both `Python 3.13.x` and this folder's `.venv/bin/python` must match; no Microsoft Azure request. |

</div>

<details class="environment-option" markdown="1">
<summary>Only when resuming on your PC: macOS/Linux or Windows PowerShell</summary>

Use the Bash block above on macOS/Linux. On Windows PowerShell, use this **instead**:

```powershell
$env:FOUNDRY_LAB_LANGUAGE = "en"
.\.venv\Scripts\python.exe -c "import sys; print('Python', sys.version.split()[0]); print(sys.executable)"
```

<div class="command-explanation" markdown="1">

**Command walkthrough — Windows**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `$env:FOUNDRY_LAB_LANGUAGE = "en"` | Reselects English synthetic inputs in this session. | No Microsoft Azure change; do not reuse Korean records. |
| 2. `.venv\Scripts\python.exe -c` | Directly selects the environment's executable and prints its **version and path**. | Both `Python 3.13.x` and this folder's `.venv\Scripts\python.exe` must match. No activation, policy change, or Microsoft Azure request. |

</div>

Continue replacing `python` with `.\.venv\Scripts\python.exe` in Windows core commands. If the path is missing, check the current folder and return to environment creation only if it was never prepared.

</details>

**Do not reuse a `.venv` based on 3.12, 3.14, or another version.** Preserve it and create a Python 3.13 environment under a new name such as `.venv-core313`. Consistently replace the guide's `.venv` paths with that name and select the same interpreter in VS Code. Changing Python environments does not require recreating Microsoft Azure resources or ownership records.

</details>

<a id="l01-sign-in"></a>

### 2. Check sign-in, subscription, permissions, and costs

**Sign in from your Codespaces terminal.** Portal or GitHub sign-in does not sign the CLI in automatically. Use [device-code sign-in](https://learn.microsoft.com/cli/azure/authenticate-azure-cli-interactively#sign-in-with-a-browser) below.

```bash
az login --use-device-code
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `az login --use-device-code` | Starts authentication for the CLI in Codespaces. | Open the Microsoft sign-in page named by your terminal, enter **the code you just requested**, and complete MFA yourself. Do not share codes, tokens, or passwords. No resource creation. |

</div>

If organizational policy blocks device-code authentication, use an approved execution/authentication path. Do not disable MFA/Conditional Access or substitute a long-lived secret.

<details class="environment-option" markdown="1">
<summary>Only for the PC alternative: sign in through your local browser</summary>

You can use this command instead from a PC terminal. Do not run both sign-in paths.

```bash
az login
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `az login` | Starts authentication for your PC's CLI. | Enter passwords/MFA directly in the sign-in screen; no resource creation. |

</div>

</details>

**After sign-in, check the subscription:** Run these lines one at a time. Find your subscription ID in the list before replacing the placeholder.

```bash
az account list --query "[].{subscription:name,id:id,tenant:tenantId,state:state}" -o table
az account set --subscription "actual-subscription-id"
az account show --query "{subscription:name,id:id,tenant:tenantId,state:state}" -o table
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `az account list` | Lists subscriptions, tenants, and states accessible to your account. | Find the ID of the permitted Enabled subscription; no model call or resource creation. |
| 2. `az account set` | Replaces the placeholder with your subscription ID and selects it. | Changes the local CLI target, not permissions. |
| 3. `az account show` | Rechecks the current subscription, tenant, and state **after selection**. | Confirm the selected ID and Enabled state before creation. |

</div>

In Microsoft Azure portal **Subscriptions → Access control (IAM) → View my access**, verify the prerequisite permissions. Creation and role assignment are different capabilities. Grant subsequent roles only at your lab project/resource scopes.

Some screens still show **Azure AI User**, the previous name of **Foundry User**. The role ID and core permissions are unchanged; the rename does not require a duplicate assignment.

Record **the amount, services, stop time, and retention deadline**. Budget alerts, TPM/RPM, and log-ingestion limits are not hard spending caps. At the limit, stop new requests/schedules and use [L19](#l12) to inspect remaining resources.

<details markdown="1">
<summary>Before you set a budget: the scale of the core course — up to 42 model requests; see per-module caps</summary>

The table lists the **maximum requests per run that the guide documents or the code enforces**. It gives no money amounts because prices change. Multiply the requests by (input size + output-token cap) to get a token ceiling, enter it with your model and SKU in the [Microsoft Azure pricing calculator](https://azure.microsoft.com/pricing/calculator/), and add the "left behind" items for as long as you keep them.

| Module | Runs that can cost money | Model-request cap | Left behind (check in L19) |
| --- | --- | --- | --- |
| L01 | `create`, `foundation`, `roles`, `monitoring --live` | 0 | Resource group, project, three model deployments, logs |
| L02 | Optional `model_capacity.py test --live` | 5 (chat 3, judge 1, embedding 1; code cap) | Three deployments |
| L03 | `first_response.py --live` | 1, optional +1 (512 output tokens; code cap) | None |
| L04 | Portal Send; optional `workshop.py agent --live` | Portal 5; SDK 1 | Agent version |
| L05 | Portal Send; optional `workshop.py rag --live` | Portal 3; SDK 1 plus three file uploads | Vector store, three files, agent |
| L06 | `workshop.py capstone --live` | Up to 5 rounds and 8 function calls (code cap) | Agent, conversation, vector store, files |
| L07 | Local lab (the core path makes no Microsoft Azure call) | 0 | None |
| L08 | `instruction_prompt_agent_lab.py --live` → `instruction_evaluation.py --live` | 24 per language (code cap) plus one evaluation run | Prompt Agent, evaluator, eval run |
| L09 | Portal Send | 3 | None |
| L10 | Optional `trace_lab.py --live` | One log query, 0 model requests | L01 logs (30-day retention, 1 GB/day cap; not a spend cap) |
| L19 | `cost_status.py`, `operations_status.py`, `stop_sessions.py` (read Microsoft Azure without `--live`) | 0 | — |

The core path totals **at most 42** requests (L03 1 + L04 5 + L05 3 + L06 5 + L08 24 + L09 3 + optional L10 1), and L08's evaluation run is separate. Caps for the electives (L11–L18) are in each module's **Steps** tables; for Search, Hosted sessions, Memory, and Routines, check in L19 what stays after you create them. Quota, TPM, budget alerts, and log limits do not stop spending, so write your own limit into `--cost-authorization`.

</details>

<a id="l01-resource-group"></a>

### 3. Create your dedicated resource group

The default path creates a **new dedicated environment** using the bundled code, then inspects it in the portal. It does not alter a shared environment. Generated names and ownership tags are recorded in `results/azure-environment.json`, which later evaluation, retrieval, and deployment use to verify scope.

Read the plan first. This command has no values to replace.

```bash
python scripts/azure_environment.py create
```

<div class="command-explanation" markdown="1">

**Command walkthrough — inspect the plan first.**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `create` | Prints the resource-group name pattern, tags, record location, and the options a real run needs. | `PLAN ONLY` plus a plan JSON; no Microsoft Azure request or sign-in/permission validation. |

</div>

<a id="l01-regions"></a>

**Choose the region before you create.** The region of the resource group and project cannot be changed later; a different region means a new environment. The core course needs only a region where `foundation` can deploy the models, but optional labs have regional limits (per the official documentation, checked 2026-10-09).

| Optional lab | Region condition | Source |
| --- | --- | --- |
| L05 File search | Not available in Italy North or Brazil South | [Tool support by region](https://learn.microsoft.com/azure/foundry/agents/concepts/limits-quotas-regions) |
| L12 Hosted agents | Only in the officially supported regions | [Supported regions](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents) |
| L15 Memory | Only in the officially supported regions (East US is not listed) | [Supported regions](https://learn.microsoft.com/azure/foundry/agents/concepts/what-is-memory) |
| L16 Routines | Unavailable in UK West, Switzerland West, Japan West, UAE North, and Norway East | [Routines article](https://learn.microsoft.com/azure/foundry/agents/how-to/use-routines) |

To do the optional labs, check these pages and [Microsoft Foundry region support](https://learn.microsoft.com/azure/foundry/reference/region-support) before choosing. The lists can change. If you pick a region that does not support an optional lab, record only that lab as not performed and continue the core course.

**Create for real:** When the plan is right and you have approval for that subscription, region, and cost scope, replace the three placeholders below with your own values and run the line that follows.

| Placeholder | Value to supply | Where to verify |
| --- | --- | --- |
| `actual-subscription-id` | The selected subscription ID | `id` in the preceding `az account show`, not the display name or tenant ID |
| `permitted-region` | An approved Microsoft Azure **location code** | For example, `eastus`. Use the lowercase region **code**, not a portal display name such as `East US`. The example does not guarantee model or feature availability, and optional labs have [regional limits](#l01-regions) |
| `"Approved amount, service scope, and retention deadline"` | Your approved amount, services, and stop/retention deadline | Step 2's actual cost approval. Supplying this text does not grant approval or access |

```bash
python scripts/azure_environment.py create --subscription actual-subscription-id --location permitted-region --cost-authorization "Approved amount, service scope, and retention deadline" --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `create ... --live` | Records scope and cost authorization and creates a unique resource group. | Actual Microsoft Azure creation; no reuse or overwrite of an existing group/receipt. |

</div>

**If it stops halfway, run the same command again.** This also applies to a policy denial, a missing permission, a timeout, or Ctrl+C. When no resource group was created, the earlier attempt's record is **kept** as `results/azure-environment.failed-<time>.json` (never deleted) and a fresh attempt starts. When the group exists and is proven to belong to this run, it is adopted and reused. First fix the cause on the first error line (permission, policy, or region).

**Stop and check:** Match `resource_group` and `location` in `results/azure-environment.json` to the name, region, and ownership tags in Microsoft Azure portal **Resource groups** before step 4. Do not share or commit `.env` or the receipt. A finished receipt is never overwritten by `create`, so do not delete it. If the same command shows `ledger already exists`, the environment already exists; continue to step 4.

![Resource-group example. Compare your own generated group, region, and ownership tags in Microsoft Azure portal before proceeding.](../../assets/portal/en/18-resource-group.png)

<a id="l01-4-create-the-foundry-project-models-and-required-roles"></a>

### 4. Create the Microsoft Foundry project, models, and required roles

`foundation` uses [main.bicep](../../infra/main.bicep) to create **a Microsoft Foundry resource/project and three chat/judge/embedding deployments**. Chat supports the core labs, judge supports L08, and embedding supports optional L11/L15. It sends no inference request.

This kit pins `gpt-6-sol / 2026-09-22`, `gpt-4.1 / 2025-04-14`, and `text-embedding-3-small / 1`. Verify availability in your subscription/region. If unavailable, record the limitation and stop; do not silently substitute a model and claim equivalent validation.

```bash
python scripts/azure_environment.py foundation --learners 1 --max-capacity 100
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `foundation` | Shows the per-learner TPM/RPM and capacity-sizing plan. | Local calculation; not live catalog/quota verification. |

</div>

**Deploy for real:** Continue only when the model, processing scope, and capacity plan match your approved scope.

```bash
python scripts/azure_environment.py foundation --chat-model gpt-6-sol --chat-version 2026-09-22 --judge-model gpt-4.1 --judge-version 2025-04-14 --embedding-model text-embedding-3-small --embedding-version 1 --model-sku GlobalStandard --learners 1 --max-capacity 100 --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `foundation ... --live` | Checks the actual catalog/quota and deploys the project and models in the owned group. | Real creation; capacity ceiling 100 per deployment is not money. Converts model-specific units and verifies actual limits afterward. |

</div>

**Stop and check:** The command must finish without errors, and the receipt's `operations` must contain an entry with `step=foundation` and `status=Succeeded`. For partial failure or timeout, read the recovery guidance below instead of proceeding to role assignment.

**Assign roles:** Run only after deployment completes and you have role-assignment permission on the target project and parent resource.

```bash
python scripts/azure_environment.py roles --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `roles --live` | Assigns the current user/project identity scoped data roles on the project and parent resource. | Access change requiring `roleAssignments/write`; no subscription-wide role is created. |

</div>

**Portal check:** In [Microsoft Foundry](https://ai.azure.com), enable **New Foundry**, open your project, and compare **Manage → Project details** Name/Parent resource/Location with the receipt. Under **Build → Models → Deployments**, verify `contoso-chat`, `contoso-judge`, and `contoso-embedding` are ready. Do not create them again in the portal.

| Creation code | What to inspect in the portal |
| --- | --- |
| RG creation in `create` | Unique Microsoft Azure resource group name and ownership tags |
| Microsoft Foundry account/project in `foundation` | Project name, parent resource, and region |
| Bicep model deployments | Model ID/version and deployment names such as `contoso-chat` |
| Scoped assignments in `roles` | Caller/managed identity and scope in the resource's IAM |

Preserve the original error and deployment operations after partial failure. Use `foundation --resume --live` only for the same owned partial deployment, with **the same model/SKU arguments**. It does not select a new environment or erase previous failure records.

<a id="l01-settings"></a>

### 5. Connect telemetry and complete local settings

#### 5-1. Connect telemetry

Connect telemetry **before the first agent request**, so L10 can inspect L04 and later runs:

```bash
python scripts/azure_environment.py monitoring
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `monitoring` | Prints the telemetry-resource/connection plan. | No Microsoft Azure request. |

</div>

**Connect for real:** Continue only when no connection already exists and log collection/retention costs are within your approved scope.

```bash
python scripts/azure_environment.py monitoring --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `monitoring --live` | Creates Log Analytics, Application Insights, and the project connection in the owned group. | Collection/retention charges may apply; a recorded existing connection is not overwritten. |

</div>

Inspect the connection under **Agents → Traces** or **Manage → Project details → Connected resources**. Querying logs requires read access to the target Application Insights/Log Analytics resources. If necessary, assign scoped `Log Analytics Reader` or the required minimum equivalent in your resource IAM. Protected tables may require additional access.

Model/agent SDK requests use Entra authentication. The bundled [observability.bicep](../../infra/observability.bicep) references the telemetry connection string inside Microsoft Azure without printing it. This is not a claim of Entra-authenticated trace ingestion.

![Project settings example. Locate the project, parent resource, region, and Connected resources under Manage → Project details.](../../assets/portal/en/13-project-settings.png)

#### 5-2. Save the project values in `.env`

The project endpoint and deployment names are already in the ownership record. Do not retype them; let the command below save them into `.env`. First preview only what would change.

```bash
python scripts/azure_environment.py env
```

<div class="command-explanation" markdown="1">

**Command walkthrough — preview what would change.**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `env` | Compares the ownership record's project endpoint and three deployment names with the current `.env`. | Each setting is shown as `added`, `updated`, or `unchanged`. No file change and no Microsoft Azure request. |

</div>

If the values are your environment, save them and check right away.

```bash
python scripts/azure_environment.py env --write
python samples/workshop.py doctor
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `env --write` | Saves only those four settings into `.env`; comments, Search settings, and every other line are kept. | Local file change (a new file is readable and writable only by you). No Microsoft Azure request. |
| 2. `doctor` | Checks the `.env` format and its agreement with the ownership record, offline. | You should see `.env check: matches results/azure-environment.json`. Fix any `PROBLEM` as advised. This is not an endpoint connection test. |

</div>

To edit by hand, open `.env` in VS Code and save the values. The block below is **file configuration**, not a terminal command:

```env
FOUNDRY_PROJECT_ENDPOINT=https://actual-resource.services.ai.azure.com/api/projects/contoso-workshop-en
FOUNDRY_MODEL_DEPLOYMENT_NAME=contoso-chat
FOUNDRY_JUDGE_DEPLOYMENT_NAME=contoso-judge
FOUNDRY_EMBEDDING_DEPLOYMENT_NAME=contoso-embedding
```

Copy `FOUNDRY_PROJECT_ENDPOINT` from receipt `project_endpoint` or Home's **Project endpoint**; do not append `/openai/v1`. Compare deployment names with receipt `model_deployments`. `.env` and `.venv` are different; do not add API keys.

**Before saving:** **Edit** existing entries instead of appending duplicate keys. Replace every example resource/project value with your own, and save as **`.env`**, not `.env.txt`. Leave Search settings empty until you select L11. Shell environment variables override `.env`; check for values left over from another lab.

<details class="implementation-detail" markdown="1">
<summary>Implementation reference: Python project connection — not required to continue</summary>

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

</details>

## Success criteria

- You created your dedicated resource group, project, three model deployments, and telemetry connection, and checked permissions, region, and budget.
- Local data checks (`validate-data`) pass.
- The portal, `.env`, and `results/azure-environment.json` identify the same English environment.
- A plan or client configuration alone is not recorded as a successful model request. Send the first request in L03; inspect your deployments in [L02](#l02).

## Troubleshooting

| Symptom | Check first | Next action |
| --- | --- | --- |
| 401 | CLI sign-in state | Recheck `az login --use-device-code` and `az account show` in [step 2](#l01-sign-in). |
| 403 | Action-specific permissions (create, role assignment, read) and the network path | Secure only the missing permission and hold that action. Do not broaden access or disable security. |
| Deployment failure | Model, region, quota, and capacity | If unsupported, record the limitation and stop. Do not substitute a model and claim the same validation. |
| Private-endpoint environment | An approved VPN/VNet path | Connect through that path. Do not turn on public access as a bypass. |
| Installation failure | The current Python and the permitted package source | Recheck the Python path and version with the [interpreter check](#l01-new-terminal). |
| `create` stops halfway (policy, permission, timeout) | The first error line and the record files in `results/` | Fix the cause and **run the same `create` command again**. An attempt that created nothing is kept automatically as `…failed-<time>.json`. |
| `.env:N: unknown setting` or a `FOUNDRY_LAB_LANGUAGE` error | Whether `.env` has lines other than the `FOUNDRY_…` settings | Select the language in the terminal with `export FOUNDRY_LAB_LANGUAGE=en`, not in `.env`. Save the four settings again with `python scripts/azure_environment.py env --write`. |
| `doctor` shows `PROBLEM .env endpoint differs…` | The endpoint in `.env` versus `results/azure-environment.json` | Save the ownership record's values again with `python scripts/azure_environment.py env --write`. |

## Cleanup

Do not delete resources yet. Retain your ownership record and deadline, then review schedules and costs in L19. This module creates an environment; it does not validate answer quality.

<div class="lab-handoff" markdown="1">

**Keep:** `results/azure-environment.json`, your `.env`, the `.venv` path, permissions, budget, and retention deadline. Reuse this environment in later modules.

**Continue:** With a created environment, [L02 deployment checks](#l02). Without live prerequisites, practice [L06 local functions](#l06) and record environment creation not performed.

</div>
