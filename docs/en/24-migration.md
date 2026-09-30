> **What you will build:** A migration table that distinguishes what to move to the new Foundry and the order of validation, while preserving existing resources.

## Objectives

**A brand rename, portal transition, resource upgrade, and SDK/API migration are different tasks.**

## Concepts and lab map

**What you will try:** Classifying resource, API, state, and operational differences between Classic and the new Foundry, then writing a migration plan.

**What is it, and why does it matter?** A portal rename does not automatically turn an existing endpoint into a new API. When moving code from Threads/Runs to Conversations/Responses, recheck not only the call structure but also tool execution loops, stored state, permissions, and retries. Seeing an agent on a screen does not establish that user conversations or deletion/retention policies have also been migrated.

**How do you use it?** Inventory definitions, user state, and operational state without changing the existing system. Implement a small synthetic path in a new nonproduction environment and apply the same checks from L03/L05/L06/L08/L10. Switch over only after quality, permission, and recovery conditions pass, starting with a limited set of users.

**Where do you run it?** The default deliverable is a migration table; there is no CLI that automatically makes changes in this chapter. Compare the [current SDK dependencies](../../requirements.txt), [Responses/tool-loop example](../../samples/workshop.py), and [deployment settings](../../azure.yaml) with your existing system. Retention and deletion require separate approval from the accountable owner.

## Prerequisites

Create a read-only inventory of the existing system. This guide does not automatically upgrade existing Azure OpenAI/Classic resources or move data.

## Steps

### 1. Identify what is currently in use

| Earlier/existing approach | New path | Caution |
| --- | --- | --- |
| Azure AI Studio / Azure AI Foundry | Microsoft Foundry | A name change alone does not change the API |
| Hub-based project | Project under a Foundry resource | Some Classic experiences remain separate |
| Assistants / Threads / Runs | Agent Versions / Conversations / Responses | Calls, state, and tool loops change |
| `azure-ai-projects` 1.x | 2.x project client | More than changing imports |
| Multiple inference endpoints | Project/OpenAI-compatible surface | Check support by provider and API |
| Role names such as Azure AI User | Foundry User and others | Check role IDs, scopes, and actual permissions |

Standalone Azure OpenAI resources and Classic hub-based projects do not directly enter every path in the new portal. Follow the official upgrade/migration procedures.

Sovereign clouds such as Azure Government have separate endpoints, authentication audiences, and service/model support. Do not reuse this public-cloud guide's environment files by changing only some addresses; base the migration plan on the official support documentation for that cloud.

### 2. Plan migration for three kinds of state separately

**Definitions:** instructions, models, tools, and connections.<br>
**User state:** conversations, memory, files, and vector stores.<br>
**Operational state:** endpoints, identities, permissions, monitoring, evaluation results, and publishing channels.

Do not assume that an API migration tool moving definitions has also moved all user conversations or business approval state.

### 3. Check regressions in the new environment

With the same synthetic data, repeat L03's model call, L05's citations, L06's functions, L08's evaluation, and L10's traces. Record differences in endpoints/token audiences, response/tool schemas, retries, and storage/retention policies.

### 4. Remove dependencies on retiring features first

Include portal Workflows' **scheduled retirement on 2026-12-01** in your timeline, and do not introduce new dependencies on it. Move required orchestration to currently supported paths such as Microsoft Agent Framework, then revalidate checkpoints, human approval, and resumption after failure.

AI Search agentic retrieval differs in capabilities and payloads between stable `2026-04-01` and the latest preview. Compare changes in knowledge sources, client names, pagination, Work IQ authentication, and response handling with the official migration tables.

### 5. Define staged cutover and recovery criteria

Do not delete the existing endpoint prematurely. Proceed from test users → limited traffic → approved expansion, and prepare a rollback path if quality, safety, latency, or cost thresholds are exceeded.

## Success criteria

You have identified migration targets, Classic features to retain, handling of user state, retirement schedules, evaluation results, and a rollback method. “It appears in the new portal” is not enough to declare migration complete.

## Troubleshooting

Even under the same brand, older documentation URLs/SDK examples may use a different resource model. First check for `foundry-classic`, `azure-ai-projects 1.x`, and Threads/Runs.

## Cleanup

After the new path passes actual usage and evaluation and the recovery period has ended, the responsible owner approves retention or deletion of the old resources.
