> **What you will build:** A one-page explanation of who is responsible for controlling identity, data, networks, policies, and costs when operating multiple agents.

<div class="lab-brief" markdown="1">

**Format:** Optional design exercise · the synthetic example needs no Azure account.

**Start here:** Mark who may do what along user → agent → tool → data.

**What to check:** Produce an allow/deny table, network paths, and owners. Writing the design neither grants access nor verifies security.

</div>

## Objectives

**Seeing a Control Plane screen is not the same as policies actually being enforced.** Operate's Overview/Assets/Compliance and the Foundry AI Gateway experience include Preview capabilities.

## Concepts and lab map

**What you will try:** Separating responsibilities across identities, RBAC scopes, Control Plane, AI Gateway, and private networks.

**What is it, and why does it matter?** RBAC defines what a particular principal may do within a particular scope, while networks define the paths over which connections are possible. A gateway is an entry point for routing requests or applying limits; it does not replace permissions on the source data. Putting a document authorized for employee A into a shared cache and serving it to B can happen even on a private network. That is why understanding actual authentication and data flows matters more than a green status on a screen.

**How do you use it?** Draw the identities, permissions, and networks at each step of a request's path: user → agent → tool → data. In the portal, distinguish Manage for the current project from Operate's view across assets. Before changing policies, design the allow/deny conditions and identify who is responsible for auditing.

**Where do you run it?** The default path is read-only portal inspection and design. [infra/main.bicep](../../infra/main.bicep) and [runtime_roles.py](../../scripts/runtime_roles.py) are reference code for understanding this kit's scope; opening them to read is different from executing them to grant roles.

## Prerequisites

The default exercise is design and read-only inspection. Turn the Contoso example into your own **principal → operation → scope → deny condition → owner** table. Without Azure access, complete it as a design, not a verified permission test. Real roles, gateways, private endpoints, and policy changes require administrator involvement and separate approval.

## Steps

### 1. Separate four identities

**Worked design — L14's public-policy Hosted path, not a record of actual role assignments.**

| Identity | Allowed operation/scope | Not allowed | Inspection/revocation owner |
| --- | --- | --- | --- |
| Developer | Change/read agents in the approved lab project | Subscription-wide administration or other teams' agents | Project administrator |
| Project managed identity | Read designated Search through connections that actually use this ID, such as L07 OpenAPI | Assuming automatic inheritance of agent runtime roles | Connection administrator |
| Agent runtime identity | Invoke the designated model and read policies in owned Search | Index updates, arbitrary data sources, orders/payments | Runtime/data administrator |
| End user | Invoke an allowed agent and receive authorized evidence | Edit agents or read another user's documents/conversations | Application/data owner |

Do not assume L14's direct Search caller and L07's connection caller are identical. Read **connection authentication in Manage → that identity's role assignment/scope → target service**. A role listing shows potential permission, not a successful call. Actual testing requires a separately approved read request.

### 2. Inspect the fleet in Control Plane

Under **Operate → Assets**, find the agents/models/tools your permissions allow you to see. Check how resources from other projects appear. **Manage** covers quota, details, gateways, and similar settings for the currently selected project/resource; **Operate** takes a fleet-wide view.

Compare execution status, costs, alerts, evaluations, and policy information. Registering an external agent expands visibility; registration does not automatically apply Foundry runtime guardrails to that agent.

For one owned asset, record **name, project, owner, last observation time, and policy target**. An empty list is not proof of no assets; check filters, tenant, and read scope first. Do not inspect an unfamiliar team's assets for workshop material.

### 3. Optional AI Gateway exercise

Choose one reason you need an APIM-based gateway: token limits, rate limits, allowed backends, observability, routing, or another specific need.

| Policy | What you must verify |
| --- | --- |
| Rate/token limit | How the user/agent/project is identified, and the response when the limit is exceeded |
| Backend routing/fallback | Whether only approved models and regions are used |
| Caching | Whether data remains separated by user/permissions |
| Logging | Whether prompts, secrets, or PII are exposed in logs |
| Tool/API management | Whether source-service permissions and gateway policies are both present |

**Example plan:** Assume a limit of 2 requests per 60 seconds for an isolated synthetic test principal and design a check that rejects the third request. Record identity key, policy scope, rejection status such as 429, counter/trace location, at most 3 requests with zero retries, and a stop owner. Actual configuration and requests require separate approval. Distributed counters or prior requests may affect observations; inspect that evidence rather than retrying until a pass.

**Quota is not a billing cap, and a budget alert is not a hard stop.** Distinguish Foundry's gateway UI from APIM service state. Do not leave tool/document authorization solely to the gateway.

### 4. Network design exercise

Draw three paths: **user → Foundry**, **Foundry → tools/data**, and **tools/data → external destinations**.

```text
Fictional users A/B
  -> Application authentication and access check
  -> Foundry agent endpoint                    [inbound]
  -> Search read using the runtime identity    [data egress]
  -> Shared synthetic policy index

Order/payment APIs and arbitrary external sites [not connected]
```

This is a **desired-boundary design**, not a claim that the bundled IaC builds private networking. For private requirements, annotate each arrow with DNS, connection path, caller identity, and allowed destination. Do not create every component in the following table automatically.

| Configuration | What it addresses | What it does not address |
| --- | --- | --- |
| Private endpoint | Private inbound connections to Foundry | Blocking all tool egress |
| VNet/managed network settings | Supported outbound paths | Automatically supporting unsupported tools |
| Private DNS | Correct address resolution | RBAC or application authentication |
| Firewall/egress policy | Control over allowed destinations | User ACLs on the data itself |

Prepare the required private endpoints separately for private Search, Storage, and other resources. One Foundry private endpoint does not make every connected resource private.

| What to inspect | How to judge it | Next action on failure |
| --- | --- | --- |
| Endpoint DNS from an approved execution location | Must resolve through the required private path | Escalate to the DNS/VNet/VPN owner; do not enable public access |
| Runtime policy reads | Design for reads from designated Search, not changes | Compare developer-login permissions separately from runtime roles |
| User B requests restricted material | No content, title, URL, or cached result should leak | Inspect source ACLs, query filters/user tokens, and cache separation |

The last row is an **ACL design exercise**. The current shared Contoso index cannot demonstrate restricted-document isolation. An actual test needs approved test identities, separate synthetic restricted documents, and access logs.

**Representative limitations:** Memory stores do not support VNet integration; Routines do not support CMK; some browser/computer/image tools do not support network isolation; and public web/Bing/SharePoint tools use public communication. For Hosted Agent private ACR, recheck documented conditions such as **projects created after 2026-06-25**.

### 5. Check policies, encryption, and information protection

Use Azure Policy to review allowed models, deployment types, and network conditions. CMK protects data at rest for supported resources; it does not mean runtime leak prevention or support for every feature.

Defender, Purview, and Entra integrations may each require product-specific configuration, permissions, and licenses. Do not present the existence of a dashboard as organizational compliance certification. Include diagnostic logs, content provenance, and how users are informed of AI use in operational documentation.

## Success criteria

Complete a per-principal allow/deny table, three network paths, one denied-case design, and audit/revocation owners. Distinguish **design example, read-only observation, and actual allow/deny tests**; claim a live test only with evidence from both sides.

## Troubleshooting

Do not assume every 403 is an RBAC problem. Separate endpoint DNS, public network blocking, VNet paths, and identity. Broader permissions do not fix an unsupported feature.

## Cleanup

Record temporary roles, policies, gateways, and connections, and revoke/remove them through administrator procedures. Do not arbitrarily delete shared networks or production policies.
