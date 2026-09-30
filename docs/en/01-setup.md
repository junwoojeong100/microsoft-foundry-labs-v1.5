> **What you will build:** A Foundry project in the correct tenant, one callable model, a development environment, and a plan for stopping costs.

## Objectives

Separate the **permissions, incorrect endpoints, supported regions, and quota** issues that cause most lab failures before you begin.

## Concepts and lab map

**What you will try:** Connect the Foundry project's scope, a model deployment, Entra sign-in, and a Python virtual environment.

**What is it, and why does it matter?** A subscription defines a billing and management scope; a resource group collects resources; a Foundry resource is the parent service boundary; and a project is a workspace for agents and connections. Knowing a project's address does not grant permission to call it. Sign-in answers “Who are you?”, roles answer “What can you do?”, and quota answers “How much can you use?” Keeping these separate helps you avoid unnecessarily recreating resources or expanding permissions to fix an authentication error.

**How do you use it?** Confirm the project and model supplied by your instructor in the portal, prepare the local environment, and configure the endpoint and deployment name. Skip the administrator-only creation commands if a project is already provided. Until you receive a real response in L03, you have prepared an environment—not demonstrated a successful model call.

**Where do you run it?** Use the portal to check the project and endpoints, and a terminal to check Python, install packages, and sign in with the CLI. Open [.env.example](../../.env.example), the [management script](../../scripts/azure_environment.py), and the [infrastructure definition](../../infra/main.bicep) together to see which settings create which resources.

## Prerequisites

| Item | Core course | Additional conditions |
| --- | --- | --- |
| Azure | An approved subscription and nonproduction resource group | Do not bypass organizational policies |
| Foundry | A **Foundry project in the new portal** | Different from a hub-based Classic project |
| Model | A chat model supporting Responses and tool use | Check support in L02 |
| Development environment | Python 3.13, Azure CLI 2.86.0 | Local standard-library exercises also work with 3.11+ |
| Data | This guide's synthetic data | Do not upload real customer or employee information |
| Budget | A per-person or team limit and someone responsible for stopping usage | Budget alerts do not enforce a hard billing cutoff |

## Steps

### 1. Prepare the project

Use the new Foundry experience at `https://ai.azure.com`. Learners can use an existing approved project.
If none is available, the responsible administrator prepares a new environment. Validation for the production of this guide uses a **new dedicated resource group**, not the existing A/B resources.
Authoring-run results are recorded separately in `validation/current/report.json`.

Record the nonproduction resource group, project name, and region. The default example is `contoso-workshop`.
**Learner path:** Use the project and model supplied by the administrator, with the minimum data-plane roles.
**Administrator path:** The script below creates only a uniquely named new resource group; it does not reuse or delete existing resources.

```bash
python3.13 scripts/azure_environment.py create --subscription 실제-구독-ID --location 허용-리전 --cost-authorization "승인 금액과 보존 정책" --live
python3.13 scripts/azure_environment.py foundation --chat-model 지원-chat모델 --chat-version 실제버전 --judge-model 지원-judge모델 --judge-version 실제버전 --embedding-model 지원-embedding모델 --embedding-version 실제버전 --model-sku GlobalStandard --capacity 10 --live
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

Replace the Korean descriptive placeholders with actual values: the subscription ID, permitted region, approved amount and retention policy, supported chat/judge/embedding model IDs, and their actual versions. Check the model catalog, SKU, and quota first,
and obtain approval for the Global, Data Zone, or Standard processing scope. Capacity units vary by model and are not a spending cap.
`infra/main.bicep` deploys only the Foundry account/project and the specified models.
Add Search with `python scripts/azure_environment.py search --live` only when you need L13. `search` is an administrator operation that creates a search service in the owned resource group; it can incur fixed costs even without requests. It does not mean “try one search.”
The ownership record is `results/azure-environment.json`. For partial failures such as RequestConflict,
inspect the original deployment operation and use `foundation --resume` **only for those same owned resources**. `--resume` continues a recorded partial deployment; it does not select a new environment or erase the original error record.

### 2. Check roles by who needs to do what

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

### 3. Check region, deployment, and cost

Prepare just one model for L02. Start with a usage-based deployment if your data is synthetic and organizational policy allows it. **PTU, paid Search tiers, GPU managed compute, large Batch jobs, and fine-tuning are not needed for the core course.**
L08's native automated evaluation also requires a separate judge deployment. Do not recreate one the administrator has already provided.

The project region, supported model regions, deployment type, and quota are separate conditions. A project in Korea Central does not, by itself, mean that all inference is processed in Korea. L02 covers Global, Data Zone, and geography-based processing scopes.

Review automated evaluation options under **Metrics** in the agent playground. Deselect evaluations you do not need. Playground evaluations can also incur charges. Costs may include File search, Search, Code Interpreter, logs, and the hosted runtime—not just inference.

### 4. Prepare the local exercise environment

Run these commands from the guide's repository folder.

```bash
python3 samples/workshop.py doctor
python3 samples/workshop.py validate-data
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `doctor` | Checks the current Python installation and required tools. It does not automatically install or repair them. | Read the diagnostic items in the terminal. No Azure sign-in or model calls. |
| 2. `validate-data` | Locally checks the bundled synthetic data's format, scenario IDs, and dev/holdout separation. | The checks should complete without errors. This validates data structure, not model quality. |

</div>

The expected result is `dev=10, holdout=10`, with 0 duplicate scenarios. This step **requires no Azure account, network connection, or external packages**.

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

Subsequent `python` commands refer to this environment's Python. If PowerShell activation is restricted, use `.venv\Scripts\python.exe` directly.

### 5. Configure endpoints and authentication

![The live Manage → Project details screen. The project, parent resource, region, and Connected resources are visible; subscription, tenant, endpoint, connection-key, and account values are masked.](../../assets/portal/13-project-settings.png)

**Reading the screen:** Under **Manage → Project details**, first compare **Name / Parent resource / Location** with your records. Put your own **Project endpoint** in the local configuration. In **Connected resources**, read the connection target, Category, and Auth method. Gray areas hide personal or connection information; they are not example values to copy. You do not need to reveal or copy connection keys. **No Add connection action or permission change under Users was performed during this screen observation.**

Copy the project endpoint from **Manage → Project details** or the project's landing page in the portal. Edit these two values in `.env`.

```text
FOUNDRY_PROJECT_ENDPOINT=https://리소스명.services.ai.azure.com/api/projects/프로젝트명
FOUNDRY_MODEL_DEPLOYMENT_NAME=실제-모델-배포이름
```

Replace the Korean placeholders above: `리소스명` is your resource name, `프로젝트명` is your project name, and `실제-모델-배포이름` is your actual model deployment name. **Do not append `/openai/v1` to the project endpoint.** The SDK constructs the correct path. Do not add an API key.

Before L08, also set `.env`'s `FOUNDRY_JUDGE_DEPLOYMENT_NAME` to the actual judge deployment name supplied by your administrator. See `.env.example` for environment-variable definitions and defaults.

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
az account set --subscription "실습용-구독-ID"
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `az account set` | Replace the Korean placeholder after `--subscription` with the approved lab subscription ID to select the CLI's default target. | Changes the local CLI's default subscription. It does not grant new permissions or move existing Azure resources. |

</div>

The sample uses **AzureCliCredential** locally. In production, choose credentials suited to the deployment environment, such as an appropriate managed identity.

## Success criteria

You have recorded the project, model, roles, region, and person responsible for costs, and the local data checks pass. Verify a successful Azure connection separately with **the live response in L03**.

## Troubleshooting

**For 403, check roles first; for 404, check the endpoint and deployment name; for 429, check quota.** A private-endpoint environment requires an approved VPN or development environment inside the VNet. Do not enable public access on your own to resolve a problem.

If SDK installation fails through your organization's mirror, request synchronization of the approved mirror. A package being available on public PyPI does not authorize bypassing organizational policy to install it.

## Cleanup

Record the resource group and its owner, and read L12's shutdown checklist in advance. Do not share or commit `.env`. The `.env` used in this lab should contain no secrets.
