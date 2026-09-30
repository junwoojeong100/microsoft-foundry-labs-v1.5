> **What you will build:** A one-page explanation of who is responsible for controlling identity, data, networks, policies, and costs when operating multiple agents.

## Objectives

**Seeing a Control Plane screen is not the same as policies actually being enforced.** Operate's Overview/Assets/Compliance and the Foundry AI Gateway experience include Preview capabilities.

## Concepts and lab map

**What you will try:** Separating responsibilities across identities, RBAC scopes, Control Plane, AI Gateway, and private networks.

**What is it, and why does it matter?** RBAC defines what a particular principal may do within a particular scope, while networks define the paths over which connections are possible. A gateway is an entry point for routing requests or applying limits; it does not replace permissions on the source data. Putting a document authorized for employee A into a shared cache and serving it to B can happen even on a private network. That is why understanding actual authentication and data flows matters more than a green status on a screen.

**How do you use it?** Draw the identities, permissions, and networks at each step of a request's path: user → agent → tool → data. In the portal, distinguish Manage for the current project from Operate's view across assets. Before changing policies, design the allow/deny conditions and identify who is responsible for auditing.

**Where do you run it?** The default path is read-only portal inspection and design. [infra/main.bicep](../../infra/main.bicep) and [runtime_roles.py](../../scripts/runtime_roles.py) are reference code for understanding this kit's scope; opening them to read is different from executing them to grant roles.

## Prerequisites

The default exercise is design and read-only verification. Perform real role assignments, gateway setup, private endpoint creation, or policy changes only with the administrator and after separate approval.

## Steps

### 1. Separate four identities

| Identity | Used for | Question |
| --- | --- | --- |
| Developer | Development, deployment, and evaluation | Who can change the agent? |
| Project managed identity | Connected resources | Who reads Search/Storage? |
| Agent identity | Runtime tools | What permissions does the agent itself have? |
| End user | Delegated data access | May this user view the original document? |

Record each identity's roles, scopes, and the person responsible for expiry/revocation. Do not design on the assumption that “the agent can access it, so every user can see it.”

### 2. Inspect the fleet in Control Plane

Under **Operate → Assets**, find the agents/models/tools your permissions allow you to see. Check how resources from other projects appear. **Manage** covers quota, details, gateways, and similar settings for the currently selected project/resource; **Operate** takes a fleet-wide view.

Compare execution status, costs, alerts, evaluations, and policy information. Registering an external agent expands visibility; registration does not automatically apply Foundry runtime guardrails to that agent.

### 3. Optional AI Gateway exercise

Choose one reason you need an APIM-based gateway: token limits, rate limits, allowed backends, observability, routing, or another specific need.

| Policy | What you must verify |
| --- | --- |
| Rate/token limit | How the user/agent/project is identified, and the response when the limit is exceeded |
| Backend routing/fallback | Whether only approved models and regions are used |
| Caching | Whether data remains separated by user/permissions |
| Logging | Whether prompts, secrets, or PII are exposed in logs |
| Tool/API management | Whether source-service permissions and gateway policies are both present |

Exceed a small nonproduction test limit and inspect the actual rejection response and logs. **Quota is not a billing cap, and a budget alert is not a hard stop.** Do not confuse the status of Foundry's gateway UI with the status of the Azure API Management service itself.

### 4. Network design exercise

Draw three paths in different colors: **user → Foundry**, **Foundry → tools/data**, and **tools/data → external destinations**.

| Configuration | What it addresses | What it does not address |
| --- | --- | --- |
| Private endpoint | Private inbound connections to Foundry | Blocking all tool egress |
| VNet/managed network settings | Supported outbound paths | Automatically supporting unsupported tools |
| Private DNS | Correct address resolution | RBAC or application authentication |
| Firewall/egress policy | Control over allowed destinations | User ACLs on the data itself |

Prepare the required private endpoints separately for private Search, Storage, and other resources. One Foundry private endpoint does not make every connected resource private.

**Representative limitations:** Memory stores do not support VNet integration; Routines do not support CMK; some browser/computer/image tools do not support network isolation; and public web/Bing/SharePoint tools use public communication. For Hosted Agent private ACR, recheck documented conditions such as **projects created after 2026-06-25**.

### 5. Check policies, encryption, and information protection

Use Azure Policy to review allowed models, deployment types, and network conditions. CMK protects data at rest for supported resources; it does not mean runtime leak prevention or support for every feature.

Defender, Purview, and Entra integrations may each require product-specific configuration, permissions, and licenses. Do not present the existence of a dashboard as organizational compliance certification. Include diagnostic logs, content provenance, and how users are informed of AI use in operational documentation.

## Success criteria

Network paths, the four identities, allowed models/tools, prohibited data, and audit/revocation owners are clear. If you performed real tests, retain evidence for both allowed and denied cases.

## Troubleshooting

Do not assume every 403 is an RBAC problem. Separate endpoint DNS, public network blocking, VNet paths, and identity. Broader permissions do not fix an unsupported feature.

## Cleanup

Record temporary roles, policies, gateways, and connections, and revoke/remove them through administrator procedures. Do not arbitrarily delete shared networks or production policies.
