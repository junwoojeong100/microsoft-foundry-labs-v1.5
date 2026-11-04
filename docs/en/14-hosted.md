## Objectives

Distinguish Prompt and Hosted Agents in the portal and identify what this no-code path cannot execute.

<div class="lab-brief" markdown="1">

**Format:** Portal inspection only. No Hosted packaging, deployment, or remote invocation.

**Start here:** Open your Prompt Agent under `Build → Agents`.

**What to check:** A table distinguishing kind, model, version, supported protocol, and where tools execute.

</div>

## Concepts and lab map

**What you will try:** Managed Prompt Agent versus custom-code Hosted runtime.

**What is it, and why does it matter?** Hosted runs your code/container. Saving Instructions does not deploy a purchasing-function server.

**How do you use it?** Inspect existing details and creation options, stopping where code or an executable image is required.

**Where do you run it?** Microsoft Foundry → Build → Agents list, details, and creation screens, without installing development tools.

## Prerequisites

Inspect only owned project resources. Read Hosted details only if **your own separately approved deployment already exists**. Never invoke another person's agent for this exercise.

## Steps

### 1. Start with Type and Version in the list

<div class="screen-step" markdown="1">

**Agents list: Running does not mean Hosted**

![Actual Agents list showing Version, Prompt Type, and New agent.](../../assets/portal/steps/agents-type-list.png)

**1 Version:** Both comparison agents show `2`; the policy agent shows `4`. **2 Type:** All three are `Prompt`. Running alone does not establish Hosted deployment. **3 New agent:** Inspect that creation path only in section 3.

[Captioned video 05 · 02:23](../../downloads/portal/index.html?clip=05-inspection-retention&t=143&lang=en#05-inspection-retention)

</div>

| Step | Click or enter | Expected screen or value | If it fails |
| --- | --- | --- | --- |
| 1 | Open `Build → Agents → contoso-policy`. | A Prompt Agent defined by Instructions, model, and File search. | Do not label it Hosted. |
| 2 | Inspect `Details/Versions` and record displayed kind/version. | Agent version differs from conversation ID. | Do not infer missing protocol/runtime fields. |

### 2. Reconcile Prompt settings and saved version

<div class="screen-step" markdown="1">

**Read the current target: Prompt configuration**

![Existing policy Prompt Agent's model, Instructions, and File search.](../../assets/portal/steps/policy-final.png)

**1 Model / 2 File search:** The current Prompt Agent configuration. This editor is not evidence of Hosted code/container deployment.

[Captioned video 05 · 01:36](../../downloads/portal/index.html?clip=05-inspection-retention&t=96&lang=en#05-inspection-retention)

</div>

<div class="screen-step" markdown="1">

**Version bar: the current policy agent is 4**

![Current policy agent's Version 4, Save, and Publish controls.](../../assets/portal/steps/policy-version-bar.png)

**1 Version:** Match the policy agent's `4` in the list above. **2 Save:** Saving Instructions differs from deployment. **3 Publish:** Do not select it in this inspection. This screen exposes no Hosted protocol or container state.

[Captioned video 05 · 01:36](../../downloads/portal/index.html?clip=05-inspection-retention&t=96&lang=en#05-inspection-retention)

</div>

### 3. Open Code agent, then cancel before developer setup

| Step | Click or enter | Expected screen or value | If it fails |
| --- | --- | --- | --- |
| 1 | Return to the list and select `New agent → Code an agent`. | The `Code agent` dialog describes frameworks, Microsoft Foundry hosting, and SDK/Get started links. | Record absent options; do not download, install, or deploy development tools. |
| 2 | Select `Cancel` without opening developer setup or SDK links. | No Hosted runtime, container, or deployment was created. | Inspecting this dialog or saving a Prompt Agent does not establish Hosted deployment. |
| 3 | If you own an existing Hosted agent, read its version, protocol, state, and connections. | An actually deployed target is inspected. | Otherwise record `Hosted not deployed`. |
| 4 | Complete the table below using actual state. | Execution and reading are distinguished. | Do not substitute Chat output for runtime state. |

<div class="screen-step" markdown="1">

**Code agent: cancel at the development boundary**

![Code agent framework/hosting information and Cancel.](../../assets/portal/steps/hosted-dialog.png)

**1 Code agent:** A separate path requiring code or an executable image. **2 Cancel:** Return without running developer setup. The recording performed zero Hosted deployments/invocations.

[Captioned video 05 · 02:19](../../downloads/portal/index.html?clip=05-inspection-retention&t=139&lang=en#05-inspection-retention)

</div>

| Item | Current Prompt Agent | Additional Hosted requirement |
| --- | --- | --- |
| Definition | Model, Instructions, service tools | Code/container, entrypoint, dependencies |
| Business functions | Only connected server tools | Runtime implementation, authorization, validation |
| Version | Saved agent version | Deployed source/image and exact remote version |
| Protocol | Supported target request path | Actual Responses, Invocations, activity, or other protocol |
| Cost/end state | Model, files, logs | Additional compute, sessions, scaling, and stop state |

<a id="l12-azd"></a>

### Development paths are outside this exercise

Hosted source/container deployment and Microsoft Agent Framework execution are code-first. This portal-only guide classifies them as **reference**, not execution. No Canvas, Visual Studio Code, DevPack, or development skill installation is required.

Successful Invocations does not validate Responses, Voice, or Teams `activity`. Agent Inspector and browser Chat are not automatically the same execution surface. Do not fill unsupported fields with invented YAML or function schemas to imply deployment.

## Success criteria

Identify your target kind from actual configuration. Record missing Hosted deployments as absent. Do not claim real purchasing-function deployment or execution without code/backend evidence.

## Troubleshooting

For missing Hosted options/details, inspect region, access, and actual deployment existence. The core path continues with Prompt Agents. Do not change public access, identities, or projects to bypass browser errors.

## Cleanup

No runtime, container, or development environment was created. Existing Hosted resources were inspected only, not stopped/deleted. Review their session/compute costs with the owner in L19.

<div class="lab-handoff" markdown="1">

**Keep:** Prompt/Hosted comparison and explicit Hosted deployment/invocation **not run** status.

**Continue:** [L13: manually compare sequential and independent review](#l15).

</div>
