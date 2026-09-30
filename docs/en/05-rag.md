> **What you will build:** An answer stating “The laptop limit is KRW 1,500,000, including VAT,” backed by evidence from an actual uploaded document.

## Objectives

Make the agent answer from **retrieved documents** rather than the model's pretrained knowledge. This is the shortest path to Retrieval-Augmented Generation, or RAG.

## Concepts and lab map

**What you will try:** File search upload, indexing, retrieval, and citations.

**What is it, and why does it matter?** RAG first finds documents relevant to a question, then uses that evidence to produce an answer. It does not retrain the model. A vector store processes and stores documents for retrieval; a citation links an answer to the location of its supporting evidence. When policies change frequently, an answer that can be checked against current documents matters more than one based on memory. Merely printing a source name, however, does not prove that retrieval occurred.

**How do you use it?** Read the three source documents and mark where the answers appear before uploading them. Confirm that indexing has completed, then ask single-document, cross-document, and missing-information questions in order. Check not only the numbers in each answer, but also that opening its evidence leads to the relevant section of the actual document.

**Where do you run it?** Observe the File search connection and citations in the portal, and optionally reproduce the same lifecycle through the SDK. The English [purchasing policy](../../data/en/policies/procurement-policy.md), [expense policy](../../data/en/policies/expense-policy.md), and [security policy](../../data/en/policies/security-policy.md) are the only sources of business-policy evidence. The implementation is in [workshop.py](../../samples/workshop.py).

## Prerequisites

Use the L04 English agent and the 3 Markdown files in `data/en/policies/`. Check upload permissions and additional File search costs. Do not attach a store populated by the Korean run or bring real company documents to the lab.

## Steps

### 1. Read the three documents first

| File | Information it contains | Information it does not contain |
| --- | --- | --- |
| `procurement-policy.md` | Item-specific limits, 36-month replacement cycle, approval thresholds | Current inventory |
| `expense-policy.md` | Prior approval, supporting documents, exchange-rate checks, no duplicate claims | Today's exchange rate |
| `security-policy.md` | Permission, data, and execution boundaries | Individual employees' HR data |

You cannot evaluate RAG quality if you do not know where the correct answers are.

### 2. Connect File search

Add **File search** under **Tools/Knowledge** in the agent builder. If the UI offers a Toolbox connection, connect a Toolbox containing the file-search tool. Direct tool connections are also supported, but Toolbox is recommended for reuse and operational management.

Create a new vector store and upload the 3 files. Wait until indexing is **Completed** before asking questions. Upload completion and search readiness are not the same.

![Tools and Knowledge in the English Contoso agent. Distinguish File search over English policies from the get_stock and prepare_purchase_request functions.](../../assets/portal/en/05-agent-tools.png)

**Reading the screen:** On the **File search** card under **Tools**, check the connected store and retrieval settings. Identifiers are masked in the image; use your own store's values. The `get_stock` and `prepare_purchase_request` entries below it are functions covered in L06, not features of file search itself. A tool list in a screenshot does not establish indexing completion or citation accuracy. Check the actual evidence returned for the questions below.

### 3. Test known answers, cross-document reasoning, and unknowns

```text
What are the laptop price limit and the regular replacement cycle? Give the document name and section.
```

Expected: **KRW 1,500,000, including VAT; 36 months; section 2 of procurement-policy.md**.

```text
I want to buy two laptops for a total of KRW 2,900,000.
Whose approval is required, and can I claim the expense if I buy them without prior approval?
```

Expected: Approval from **both the team manager and the purchasing representative**, and **expenses without prior approval are generally not reimbursable, subject to written exception review**. Distinguish the evidence from the two documents.

```text
Tell me the purchasing policy for the German branch too.
```

Expected: The agent says that the provided documents do not establish this. Inventing a source is a failure.

### 4. Open the citations

A filename in an answer is not enough for success. Verify that portal citations or SDK `annotations` point to an **actual uploaded file or retrieval result**. Also check that the answer does not mix in unsupported numbers.

SDK path:

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

The executable sample uploads the files, attaches them to a vector store, waits up to 180 seconds for indexing, creates an agent, and asks a question. If indexing does not finish within 180 seconds, it stops rather than pretending to have completed. Use the receipt to check remaining files and their status.

### 5. Break down retrieval failures

![The learning loop: question, retrieval, evidence, answer, evaluation, and improvement.](../../assets/learning-loop.en.svg)

| Symptom | Layer to check first |
| --- | --- |
| Relevant documents are not retrieved | Indexing, chunks, and retrieval settings |
| The document is right but the answer is wrong | Instructions, question, and model |
| The answer is right but has no source | Citation handling and UI rendering |
| Another user's documents appear | Data permissions, retrieval filters, and caller identity |

## Success criteria

The 2 answerable questions have real supporting evidence, and the agent withholds an answer to the question not covered by the documents. You have compared the facts in the responses with the originals and confirmed that indexing completed.

## Troubleshooting

Do not start by uploading the documents again. Check the connected vector store ID, indexing failure reason, supported file formats, model/tool support, and the correct agent version. If a table appears only as an image in the file, use L18 to assess whether File search alone is sufficient.

## Cleanup

Keep the portal knowledge connection for the next lab. The SDK sample sets the vector store to expire **1 day after last activity**, but uploaded files are separate. Do not rely on expiration alone; delete them in L12.

<details markdown="1">
<summary>When should you choose File search or Foundry IQ?</summary>

Use File search for quick validation with a few files. Use Azure AI Search when you need direct control over indexes, hybrid retrieval, and filters. Consider Foundry IQ for sharing multiple knowledge sources and agentic retrieval. None of these paths automatically implements per-user document permissions just by connecting a source.

</details>
