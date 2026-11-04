## Objectives

Inspect scope, access, connections, and safety boundaries read-only in Azure portal and Microsoft Foundry. Distinguish policy text from enforcement.

<div class="lab-brief" markdown="1">

**Format:** Read-only portal inspection and a decision-table exercise. No role, network, or policy changes.

**Start here:** Check only your group/project and current-user role.

**What to check:** User/runtime/data scopes, evidence limits, and a nonsensitive decision table.

</div>

## Concepts and lab map

**What you will try:** RBAC, managed identities, connections, guardrails, and isolation inspection.

**What is it, and why does it matter?** Instructions are not authorization. Cached answers can leak information when tenant/user/document ACL boundaries are lost.

**How do you use it?** Read actual owned scopes, then review synthetic access decisions without requesting forbidden data.

**Where do you run it?** Owned Azure portal IAM/Identity/Networking and Microsoft Foundry project connections/agent settings.

## Prerequisites

Do not record/share people lists, email, object IDs, tokens, or keys. Prefer `View my access`; do not open others' full access lists. Project Contributor does not automatically grant log, Blob, or Search data-plane access.

## Steps

### 1. Distinguish your scope from runtime identity

Actual IAM role details, Identity, and Networking values are not in the recordings. Entry-point and warning images below do not verify those settings. Mark values you cannot read in your owned scope `not exposed/unverified`.

<div class="screen-step" markdown="1">

**Scope first: enter your own IAM inspection from Overview**

![Dedicated group Overview with Access control IAM and Tags entry points.](../../assets/portal/steps/rg-created.png)

**1 IAM:** Use `View my access` for your own permissions. This image shows the entry point, not a role list or completed authorization test. **2 Tags:** Reconcile ownership and scope first.

[Captioned video 01 · 01:04](../../downloads/portal/index.html?clip=01-environment&t=64&lang=en#01-environment)

</div>

<div class="screen-step" markdown="1">

**Runtime identity: different from personal sign-in**

![Actual Memory warning requesting a separate project managed-identity role.](../../assets/portal/steps/memory-warning.png)

**1 Zero stores / 2 Setup incomplete:** An observed dependency warning, not a performed role assignment or live denial test. Do not expand access with `Resolve`.

[Captioned video 05 · 01:58](../../downloads/portal/index.html?clip=05-inspection-retention&t=118&lang=en#05-inspection-retention)

</div>

<div class="practice-block" markdown="1">

**Try it:** Perform these read-only steps and mark each `observed/not exposed/unverified`.

| Step | Click or enter | Expected screen or value | If it fails |
| --- | --- | --- | --- |
| 1 | Open the dedicated Microsoft Azure group → `Access control (IAM) → View my access`. | Your actual role and scope. | No role additions or Owner escalation. |
| 2 | Read owned Microsoft Foundry account/project Identity/access settings. | User and runtime managed identities differ. | Do not change toggles/role assignments. |
| 3 | Read current `Networking`. | Approved public/private boundary. | Do not disable private endpoints/firewalls. |

### 2. Read connections, tools, protection, and execution separately

| Step | Click or enter | Expected screen or value | If it fails |
| --- | --- | --- | --- |
| 1 | Open Microsoft Foundry `Manage → Connected resources`. | Owned targets, authentication type, and scope. | Do not open/record raw keys or connection strings. |
| 2 | Inspect your agent's Tools/Guardrails under `Build → Agents`. | Actual tools, filters, and permission dependencies. | Instructions do not prove tool authorization. |
| 3 | Compare L09 safety outcomes with L10 trace access. | Filter observations and data-plane allow/deny remain separate. | Settings are not observed denial logs. |

<div class="screen-step" markdown="1">

**Authentication: form defaults differ from saved connections**

![Unconnected IQ form showing resource selection and default API Key Auth Type.](../../assets/portal/steps/iq-connect.png)

**1 Target / 2 Auth Type:** This is L11's unconnected form. Default API Key neither describes your saved connection nor authorizes key use. Inspect the actual saved target/authentication without revealing keys. **3 Create resource:** Do not select.

[Captioned video 05 · 01:46](../../downloads/portal/index.html?clip=05-inspection-retention&t=106&lang=en#05-inspection-retention)

</div>

<div class="screen-step" markdown="1">

**Attached tools: the actual policy agent uses File search**

![Current policy agent's saved model and File search attachment.](../../assets/portal/steps/policy-final.png)

**1 Model / 2 File search:** Record actual saved configuration. This attachment does not implement ordering tools, per-user document ACLs, or Memory. Do not report the canceled MCP allowlist as a saved restriction.

[Captioned video 05 · 01:36](../../downloads/portal/index.html?clip=05-inspection-retention&t=96&lang=en#05-inspection-retention)

</div>

<div class="screen-step" markdown="1">

**Protection: inspect the actual applied targets**

![Actual DefaultV2 Applied to, Model deployments, and Agents details.](../../assets/portal/steps/guardrail-targets.png)

**1 Applied to / 2 Model deployments / 3 Agents:** Read your target's actual scope. Model protection differs from server authorization for documents and ordering APIs. Make no policy changes.

[Captioned video 03 · 03:41](../../downloads/portal/index.html?clip=03-retrieval-boundaries&t=221&lang=en#03-retrieval-boundaries)

</div>

<div class="screen-step" markdown="1">

**Execution: returned policy text is not an ACL test**

![Actual File search Input + Output with returned policy text.](../../assets/portal/steps/trace-input-output.png)

**1 Input + Output / 2 Content source:** Inspect actual returned content. One synthetic public-policy retrieval does not test another user/tenant's denied access or cache isolation.

[Captioned video 03 · 04:18](../../downloads/portal/index.html?clip=03-retrieval-boundaries&t=258&lang=en#03-retrieval-boundaries)

</div>

### 3. Cache decisions: a manual exercise, not portal inspection

| Step | Click or enter | Expected screen or value | If it fails |
| --- | --- | --- | --- |
| 1 | Complete the synthetic cache table below. | Current user/tenant/ACL checks are explicit. | Do not claim the portal inspected cache implementation. |

| Synthetic request | Safe decision | Required checks |
| --- | --- | --- |
| Same tenant, user A, authorized public synthetic policy | Reuse candidate | Current access, document version, retention, key scope |
| Same tenant, user B, no permission to A's private document | Deny | B's current ACL **before cache hit** |
| Different tenant/project | Separate/deny | Tenant/project boundary and shared-store isolation |
| Revoked access or updated source | Invalidate/revalidate | Current authorization and source version |

**Change one thing:** Change only A→B in the first row. Decide whether an identical question allows answer reuse. Explain why B does not inherit A's document access.

**Explain the result:** Tenant/project/user in the key is insufficient without **current per-request authorization/ACL checks**. This table is neither a code repair nor a live cross-user security test.

</div>

## Success criteria

Separate actual scopes/roles/connections from unverified items. Finish read-only without escalation or public access changes. Do not report the cache table as implementation/security validation.

## Troubleshooting

Mark unexposed permissions unknown and request exact least-privilege actions/scope from the owner. An Azure Policy assignment does not establish agent document ACL enforcement.

## Cleanup

Keep only nonsensitive observations. Exclude any captured people/group/email lists from distribution. Permission/network/policy changes require separate authorization.

<div class="lab-handoff" markdown="1">

**Keep:** Owned scope/identity/connection checklist, cache decisions, and unverified live cross-user isolation.

**Continue:** [L18: evaluation gates, versions, and release decisions](#l22).

</div>
