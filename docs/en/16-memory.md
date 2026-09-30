> **What you will build:** Store and search for a real Memory item, verify user isolation, and confirm that the item is absent after an approved deletion.

## Objectives

**Conversation is dialogue history, Memory is context across conversations, and IQ is organizational knowledge.**
Do not judge memory success merely from a natural-language answer that happens to use a table.

## Concepts and lab map

**What you will try:** A Memory store, items, user scopes, TTL, and verification through actual searches and deletion checks.

**What is it, and why does it matter?** Memory stores useful user context so that it can be retrieved after a conversation ends. Its purpose differs from RAG over organizational policies or the current conversation's history. Applying fictional user A's preference for tables to user B would break the user boundary. Likewise, a deletion request requires checking that the item has disappeared from the store, not merely that the model says it has “forgotten.”

**How do you use it?** Create a new store and save only one approved synthetic preference. Search for the same item ID in the A/B scopes to test isolation. Only if deletion is approved, remove that one item and search again. TTL expiry, immediate deletion, and log deletion are separate operations.

**Where do you run it?** Use the direct API path in [memory_lab.py](../../samples/memory_lab.py) and observe the store settings under Memory in the portal. This chapter covers the store/search/isolate/delete lifecycle, not the full process of automatic memory extraction.

## Prerequisites

Memory is in **Preview** and requires a supported region, chat/embedding deployments, and project roles.
Current VNet integration limitations mean you must not change a private environment's security settings just to run the lab.
Prepare the core Python SDK environment and `FOUNDRY_EMBEDDING_DEPLOYMENT_NAME` in `.env`.

The only permitted content is fictional user A's “prefers answers in table format.”
Do not store real personal data, salaries, passwords, or employee information.

## Steps

### 1. Create a dedicated store

![The actual Memory store Details screen. It shows the chat and embedding models, a default TTL of 3600 seconds, User profile enabled, and Chat summary and Procedural memory disabled.](../../assets/portal/10-memory.png)

**Read the screen:** Under **Build → Memory → your store → Details**, check the models, TTL, and memory types. **Memories** is a separate tab for inspecting stored items. The captured store uses profiles only, and the screen was observed with **Save** disabled. No new item was stored, searched for, or deleted during the capture, so this screen alone is not evidence of successful user isolation or deletion.

```bash
python samples/memory_lab.py create
python samples/memory_lab.py create --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `memory_lab.py create` | Prints the plan for the Memory store to create. | No Azure requests. Check supported models and regions first. |
| 2. `create --live` | Prepares a unique store and A/B scopes, with settings including a default TTL of 3600 seconds. | Creates the remote store and `results/memory.json`. Check storage and model/embedding usage conditions and costs. |

</div>

The unique store name and A/B scopes are recorded in `results/memory.json`.
Only profiles are enabled; summary/procedural extraction is disabled. The default TTL for new items is **3,600 seconds**.
An existing receipt is not overwritten.

### 2. Store an item and search for it

```bash
python samples/memory_lab.py remember --live
python samples/memory_lab.py verify --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `remember --live` | Creates the synthetic “prefers answers in table format” item in the receipt's A scope and records its ID. | Writes remote data. Do not arbitrarily add personal information or a new user scope. |
| 2. `verify --live` | Performs actual Memory searches in the A/B scopes and checks the stored ID's presence and isolation. | Service query/search charges may apply. This is not a lookup in a local dictionary (`dict`); the item must be present for A and absent for B. |

</div>

Using the low-level `create_memory` operation makes the write and item ID explicit.
Search uses the real Memory API, and the result's `memory_id` must match the saved ID.
For eventual consistency, wait only up to 6 attempts at 3-second intervals.
This direct CRUD path does not validate automatic memory extraction from conversations.

### 3. Read the isolation checks

Run the same search with scope A and scope B.
The item must be present for A, while B must be empty. Preserve the raw results for each.
Scopes come only from the receipt; do not replace them with arbitrary user input.
In a real service, the server must derive the scope from the authenticated principal.

### 4. Delete only the one item, then search again

Run this step **only if the administrator has approved deletion of the lab item**.
Deleting an item is separate from deleting an Azure store/RG. If the environment has a no-deletion policy,
record this step as not executed and report only the storage and isolation results.

```bash
python samples/memory_lab.py forget --confirm 실제-memory-id --live
python samples/memory_lab.py verify --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Perform this only after separate approval to delete the item.

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `forget --confirm ... --live` | Replace `실제-memory-id` in `--confirm` with the actual item ID matching the receipt. Checks the endpoint, store ownership information, and scope, then deletes only that item. | Deletes remote data, not the store/RG. Permission to incur costs and approval to delete are separate. |
| 2. `verify --live` | With the deletion recorded, makes a fresh API search to check that the item is absent and scope boundaries remain intact. | A real query. Does not reuse earlier search results or natural-language answers. |

</div>

After checking the endpoint, store ownership metadata, and item scope, delete only that item.
Success requires a new API search after deletion that does not return the ID.
Do not claim deletion succeeded based only on an “I forgot” answer, an existing conversation, or the TTL setting.

## Success criteria

You have the store/item IDs, A's search results, and B's isolation results; if deletion was performed, you also verified the post-deletion search.
If deletion was not permitted, distinguish **implementation complete / storage and isolation executed / deletion not executed**.
Separately identify features not executed, such as automatic remember/forget prompts and procedural memory.

## Troubleshooting

Check model/embedding support, store settings, user scopes, and Preview API access.
If the API fails, preserve the original error. Do not substitute a local dictionary and label it Azure Memory success.

## Cleanup

The default is to retain the store. TTL controls item lifetime; it does not delete the entire store, traces, or conversations.
Record the retention policy and review date, and obtain separate approval for resource deletion.
