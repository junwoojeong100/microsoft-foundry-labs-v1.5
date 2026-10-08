> **What you will build:** Store and search for a real Memory item, verify user isolation, and confirm that the item is absent after an approved deletion.

<div class="lab-brief" markdown="1">

**Format:** Advanced elective · requires Memory Preview and supported chat/embedding models.

**Start here:** Review the plan and user scope for just one fictional user A preference: answers in table format.

**What to check:** Search finds the same item for A only. Delete only that item if approved; otherwise record deletion as not executed.

</div>

## Objectives

**Conversation is dialogue history, Memory is context across conversations, and IQ is organizational knowledge.**
Do not judge memory success merely from a natural-language answer that happens to use a table.

## Concepts and lab map

**What you will try:** Store and retrieve one fictional user's response-format preference.

**What is it, and why does it matter?** Memory holds user context for later conversations. A store holds items, scope identifies the user boundary, and TTL is retention time. User A's memory must not appear for B.

**How do you use it?** Search for the saved item ID as A and B. After approved deletion, confirm its absence. The answer “I forgot it” is not enough.

**Where do you run it?** Use [memory_lab.py](../../samples/memory_lab.py) and portal **Memory**. This covers one item's storage, retrieval, isolation, and deletion—not all automatic extraction.

## Prerequisites

Memory is in **Preview** and requires a supported region, chat/embedding deployments, and project roles.
Current VNet integration limitations mean you must not change a private environment's security settings just to run the lab.
Prepare the core Python SDK environment and `FOUNDRY_EMBEDDING_DEPLOYMENT_NAME` in the English checkout's `.env`, with `FOUNDRY_LAB_LANGUAGE=en` selected.

The only permitted content is fictional user A's “prefers answers in table format.”
Do not store real personal data, salaries, passwords, or employee information.

### Choose your starting path

If you previously ran Hosted or Agent Framework, use [L01's new-terminal steps](#l01-new-terminal) to return to the **core `.venv`**. Do not mix its packages into an advanced environment.

| Requirement | Where to inspect | If missing |
| --- | --- | --- |
| Project, chat, and embedding deployment names | Your L01/L02 `.env` and deployment list | Read only the `create` plan until names, region, and access are checked |
| Whether this is a new exercise | Presence of this folder's `results/memory.json` | Do not repeat `create` over an existing record |
| Approval to delete the exact item | Verify your receipt's actual `memory_id` and allowed deletion scope | Complete steps 1–3 only before approval; step 4 remains not performed |

Follow **create store → store one item → compare A/B searches → delete only if approved**. Search and Hosted are not prerequisites. Open `results/memory.json` in an editor to read values without modifying the original.

## Steps

### 1. Create a dedicated store

![Stored-item example. The Memories tab shows synthetic user A's English preference for table-formatted answers.](../../assets/portal/en/10-memory.png)

**Read the screen:** The image shows **Build → Memory → your store → Memories** after the remember step below. Enter the exact synthetic scope from your own receipt; the default `{{$userId}}` filter is not this lab's user-A scope. Use **Details** to check chat/embedding models, TTL, and memory types. Follow steps 2–4 below to check storage, user-specific searches, and separately approved deletion.

```bash
python samples/memory_lab.py create
python samples/memory_lab.py create --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `memory_lab.py create` | Prints the plan for the Memory store to create. | No Microsoft Azure requests. Check supported models and regions first. |
| 2. `create --live` | Prepares a unique store and A/B scopes, with settings including a default TTL of 3600 seconds. | Creates the remote store and `results/memory.json`. Check storage and model/embedding usage conditions and costs. |

</div>

The unique store name and A/B scopes are recorded in `results/memory.json`.
Only profiles are enabled; summary/procedural extraction is disabled. The default TTL for new items is **3,600 seconds**.
An existing receipt is not overwritten.

After creation, inspect `name`, `endpoint`, `scope_a`, `scope_b`, and `ttl_seconds`. `memory_id` is added **after remember succeeds**. Do not confuse a store name with the item ID required by `--confirm`.

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

`remember` already searches after writing; `verify` makes a fresh check of the same item. **Read their printed `Evidence:` files here**; no additional search command is needed.
The item must be present for A, while B must be empty. Preserve the raw results for each.
Scopes come only from the receipt; do not replace them with arbitrary user input.
In a real service, the server must derive the scope from the authenticated principal.

| Original event/value | Expected relationship after storage |
| --- | --- |
| ID in `memory_created` / receipt `memory_id` | The same actual item |
| `memory_search` with `scope_label=scope_a` | Returns that item ID |
| `memory_search` with `scope_label=scope_b` | Empty results |
| `verified` | Storage/isolation judgment. Without deletion, do not read `deleted_item_absent` as deletion success |

### 4. Delete only the one item, then search again

Run this step **only after explicit approval to delete your exact lab item**.
Deleting an item is separate from deleting a Microsoft Azure store/RG. If the environment has a no-deletion policy,
record this step as not executed and report only the storage and isolation results.

```bash
python samples/memory_lab.py forget --confirm ACTUAL_MEMORY_ID --live
python samples/memory_lab.py verify --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Perform this only after separate approval to delete the item.

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `forget --confirm ... --live` | Replace `ACTUAL_MEMORY_ID` in `--confirm` with the exact item ID matching your English receipt. Checks the endpoint, store ownership information, and scope, then deletes only that item. | Deletes remote data, not the store/RG. Permission to incur costs and approval to delete are separate. |
| 2. `verify --live` | With the deletion recorded, makes a fresh API search to check that the item is absent and scope boundaries remain intact. | A real query. Does not reuse earlier search results or natural-language answers. |

</div>

After checking the endpoint, store ownership metadata, and item scope, delete only that item.
Success requires a new API search after deletion that does not return the ID.
Do not claim deletion succeeded based only on an “I forgot” answer, an existing conversation, or the TTL setting.

<details class="implementation-detail" markdown="1">
<summary>Implementation reference: Memory store, scope, and item IDs in API calls — read only</summary>

#### Portal Memory and the actual item API

The portal **Memory** view shows stores and items, but the API operation is scoped by `name`, `scope`, and `memory_id`:

```python
store = project.beta.memory_stores
item = store.create_memory(
    name=state["name"],
    scope=state["scope_a"],
    content=PREFERENCE,
    kind="user_profile",
)
state["memory_id"] = item.memory_id

result = store.search_memories(
    name=state["name"],
    scope=state["scope_a"],
    items=[{"role": "user", "type": "message", "content": "What answer format does this workshop user prefer?"}],
    options=MemorySearchOptions(max_memories=5),
)
```

| Portal Memory view | Python code |
| --- | --- |
| Selected Memory store | `state["name"]` |
| User A/B scope | `state["scope_a"]` / `state["scope_b"]` |
| Memories item ID | `item.memory_id` and the ownership receipt |
| Search item | IDs returned by `store.search_memories(...)` |
| Delete an item | Verify exact ID/scope, then `store.delete_memory(...)`; retain the store |

This compares **scope-specific retrieval**. The same API caller selects both scopes, so it does not test whether authenticated A can request B's scope. A real application must derive scope server-side from the authenticated identity. Delete/`forget --confirm` removes one item; store/RG deletion is separate.

</details>

## Success criteria

You have the store/item IDs, A's search results, and B's isolation results; if deletion was performed, you also verified the post-deletion search.
If deletion was not permitted, distinguish **implementation complete / storage and isolation executed / deletion not executed**.
Separately identify features not executed, such as automatic remember/forget prompts and procedural memory.

## Troubleshooting

Check model/embedding support, store settings, user scopes, and Preview API access.
If the API fails, preserve the original error. Do not substitute a local dictionary and label it Microsoft Azure Memory success.
If creation failed but `memory.json` exists, reconcile your portal and original error first. Do not erase the receipt or edit unverified ownership. TTL expiry is not evidence of an approved deletion; a new exercise needs its own ownership record.

## Cleanup

The default is to retain the store. TTL controls item lifetime; it does not delete the entire store, traces, or conversations.
Record the retention policy and review date, and obtain separate approval for resource deletion.

<div class="lab-handoff" markdown="1">

**Keep:** `results/memory.json`, store/item IDs, A/B searches, whether deletion was performed, and TTL/retention deadline. Expiration is not a deletion execution.

**Continue:** [L16](#l17) if you select scheduling, otherwise [L19](#l12). Memory is not a prerequisite for scheduling.

</div>
