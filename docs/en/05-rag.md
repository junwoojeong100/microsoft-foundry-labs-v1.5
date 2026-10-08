> **What you will build:** An answer stating “The laptop limit is KRW 1,500,000, including VAT,” backed by evidence from an actual uploaded document.

<div class="lab-brief" markdown="1">

**Format:** Reuse L04's portal agent · check upload and retrieval costs first.

**Start here:** Read the three English synthetic policies and find the laptop-cap and approval sections.

**What to check:** Actual citations for two answerable questions and a withheld answer for missing policy. The SDK path is optional.

</div>

## Objectives

Make the agent answer from **retrieved documents** rather than the model's pretrained knowledge. This is the shortest path to Retrieval-Augmented Generation, or RAG.

## Concepts and lab map

**What you will try:** Use File search to answer policy questions with evidence.

**What is it, and why does it matter?** RAG means **retrieve documents, then answer**. It does not retrain the model. A vector store holds documents for retrieval; a citation connects a claim to its evidence.

**How do you use it?** Read and upload three policies, then wait for indexing to complete. Compare three answers and their actual citations with the sources. A printed filename alone is not a verified citation.

**Where do you run it?** Add the English [purchasing](../../data/en/policies/procurement-policy.md), [expense](../../data/en/policies/expense-policy.md), and [security policies](../../data/en/policies/security-policy.md) to L04's portal agent. The [SDK](../../samples/workshop.py) is optional.

## Prerequisites

The default path uses L04's English **portal agent** and the three Markdown files in `data/en/policies/`. Check upload permissions and additional File search costs. Do not attach a Korean store or real company documents. If you used only the L04 SDK or File search editing is unavailable, inspect the optional SDK path below and record its new target and completed question scope separately.

## Steps

### 1. Read the three documents first

| File | Information it contains | Information it does not contain |
| --- | --- | --- |
| `procurement-policy.md` | Item-specific limits, 36-month replacement cycle, approval thresholds | Current inventory |
| `expense-policy.md` | Prior approval, supporting documents, exchange-rate checks, no duplicate claims | Today's exchange rate |
| `security-policy.md` | Permission, data, and execution boundaries | Individual employees' HR data |

You cannot evaluate RAG quality if you do not know where the correct answers are.

### 2. Connect File search

1. In **Build → Agents**, open **your agent name recorded in L04**. Do not create another agent.
2. Open the built-in file-search connection under **Tools/Knowledge → File search**. If unavailable, verify project support and choose the SDK path below. L07's Cloud Toolbox extension is not a prerequisite.
3. Create your lab's vector store and upload **only the three Markdown files** from `data/en/policies/`. Do not upload the entire ZIP or `data/` folder.
4. Confirm indexing is **Completed** for all three files. Upload completion is not search readiness. **Save** the connection and record the agent version and store name.
5. Choose **New chat**, then submit each of the three questions below once. Keep this separate from L04's conversation without knowledge.

![Tools and Knowledge in the English Contoso agent. Distinguish File search over English policies from the get_stock and prepare_purchase_request functions.](../../assets/portal/en/05-agent-tools.png)

**Reading the screen:** On the **File search** card under **Tools**, check your own store and retrieval settings. The `get_stock` and `prepare_purchase_request` entries below it are functions covered in L06, not features of file search itself. After indexing completes, ask the questions below and compare the actual citations with the original documents.

### 3. Test known answers, cross-document reasoning, and unknowns

```prompt
What are the laptop price limit and the regular replacement cycle? Give the document name and section.
```

Expected: **KRW 1,500,000, including VAT; 36 months; section 2 of procurement-policy.md**.

```prompt
I want to buy two laptops for a total of KRW 2,900,000.
Whose approval is required, and can I claim the expense if I buy them without prior approval?
```

Expected: Approval from **both the team manager and the purchasing representative**, and **expenses without prior approval are generally not reimbursable, subject to written exception review**. Distinguish the evidence from the two documents.

```prompt
Tell me the purchasing policy for the German branch too.
```

Expected: The agent says that the provided documents do not establish this. Inventing a source is a failure.

### 4. Open the citations

A filename in an answer is not enough for success. Verify that portal citations or SDK `annotations` point to an **actual uploaded file or retrieval result**. Also check that the answer does not mix in unsupported numbers.

**After checking all three portal answers, skip the SDK below.** L06's integrated command prepares its own files; running `rag --live` first is not required.

<details class="optional-path" markdown="1">
<summary>Optional: the SDK creates new files, a store, and an agent</summary>

```bash
python samples/workshop.py rag
python samples/workshop.py rag --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `rag` | Displays the synthetic policies to use and the RAG execution plan. Without `--live`, nothing is uploaded. | Reviews the plan locally only. |
| 2. `rag --live` | Performs file upload → vector store attachment → up to 180 seconds of indexing wait → new agent creation → a question. | Model, File search, and file-storage costs may apply. Compare answer citations with the file/store IDs in the receipt. This command does not reuse portal-created objects. |

</div>

The executable uploads files, attaches the store, waits up to 180 seconds for indexing, creates an agent, and asks **one default price-limit question**, not all three questions above. If indexing does not finish, it stops rather than claiming completion. Use the receipt to inspect remaining files and their status.

To finish the three-question check, find the new agent name/version in the receipt and open it under **Build → Agents**. Verify the additional request budget before sending step 3's questions. If Chat is unavailable, record **default-question retrieval/citations checked / three-question comparison not run**. Do not repeatedly run `rag --live` for each question and recreate resources.

</details>

### 5. Break down retrieval failures

![The learning loop: question, retrieval, evidence, answer, evaluation, and improvement.](../../assets/learning-loop.en.svg)

| Symptom | Layer to check first |
| --- | --- |
| Relevant documents are not retrieved | Indexing, chunks, and retrieval settings |
| The document is right but the answer is wrong | Instructions, question, and model |
| The answer is right but has no source | Citation handling and UI rendering |
| Another user's documents appear | Data permissions, retrieval filters, and caller identity |

<details class="implementation-detail" markdown="1">
<summary>Implementation reference: SDK upload, indexing, and retrieval — read only</summary>

### Portal actions and the actual File search code

The portal sequence is **create store/upload → wait for indexing → attach File search → ask**. This teaching excerpt connects `create_lab_agent()` and `run_turn()`. `project`/`client` are L03's clients; `receipt` is created first by the SDK runner. Do not execute the excerpt separately and create duplicates.

```python
from pathlib import Path
from azure.ai.projects.models import FileSearchTool, PromptAgentDefinition
from lab_profile import DATA

instructions = Path("data/en/prompts/agent-v2.txt").read_text(encoding="utf-8")
store = client.vector_stores.create(
    name=receipt.data["run_id"],
    expires_after={"anchor": "last_active_at", "days": 1},
)
receipt.add("vector_store", store.id)
for path in sorted((DATA / "policies").glob("*.md")):
    with path.open("rb") as handle:
        uploaded = client.files.create(file=handle, purpose="assistants")
    receipt.add("file", uploaded.id)
    index_file(client, uploaded.id, store.id)

file_search = FileSearchTool(vector_store_ids=[store.id], max_num_results=4)
agent = project.agents.create_version(
    agent_name=receipt.data["run_id"],
    definition=PromptAgentDefinition(
        model=deployment_name,
        instructions=instructions,
        tools=[file_search],
    ),
    description="Synthetic workshop agent; never submit real orders.",
)
receipt.add("agent", agent.name, version=agent.version)
conversation = client.conversations.create()
receipt.add("conversation", conversation.id)
response = client.responses.create(
    conversation=conversation.id,
    input=question,
    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference", "version": agent.version}},
    include=["file_search_call.results"],
    max_output_tokens=2048,
)
```

| Portal action | What the code does |
| --- | --- |
| Upload policies and check indexing | `client.files.create(...)`, then wait for `index_file(...)` to complete |
| Connect File search to a store | `FileSearchTool(vector_store_ids=[store.id], ...)` |
| Save the agent configuration | `project.agents.create_version(...PromptAgentDefinition(...))` |
| Send a Chat question and inspect citations | `responses.create(...)` with `include=["file_search_call.results"]` |

This is the raw SDK flow for reading. Running it creates a separate store, agent, and files; use the receipt-tracked `workshop.py rag --live` path only after approval, and do not run both SDK and portal paths.

</details>

## Success criteria

The 2 answerable questions have real supporting evidence, and the agent withholds an answer to the question not covered by the documents. You have compared the facts in the responses with the originals and confirmed that indexing completed.

## Troubleshooting

Do not start by uploading the documents again. Check the connected vector store ID, indexing failure reason, supported file formats, model/tool support, and the correct agent version. If a table appears only as an image in the file, first check for searchable text; do not assume File search has read it.

## Cleanup

Retain the knowledge connection for later labs. SDK store expiration **one day after last activity** does not delete uploaded files. In L19, inspect remaining resources and delete only approved targets or record retention deadlines.

<details markdown="1">
<summary>When should you choose File search or Microsoft Foundry IQ?</summary>

Use File search for quick validation with a few files. Use Microsoft Azure AI Search when you need direct control over indexes, hybrid retrieval, and filters. Consider Microsoft Foundry IQ for sharing multiple knowledge sources and agentic retrieval. None of these paths automatically implements per-user document permissions just by connecting a source.

</details>

<div class="lab-handoff" markdown="1">

**Keep:** The policy agent name, saved version, store, and three answers/actual citations. Reuse **this policy agent in L09**.

**Continue:** [L06 stock and drafts](#l06). Its integrated command creates another agent; do not add functions here or repeat SDK uploads.

</div>
