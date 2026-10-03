> **What you will build:** Extract structured values from a fictional receipt, calculate totals from an expense CSV, and compare them with the originals.

<div class="lab-brief" markdown="1">

**Format:** Advanced elective · distinguish Vision, document extraction, and code-based calculations.

**Start here:** Open the English synthetic receipt and check that its PDF/image text is not clipped.

**What to check:** Compare the executed path's fields, totals, and source locations. File preparation alone is not service execution.

</div>

## Objectives

Distinguish **Vision model descriptions, OCR/layout, schema extraction with Content Understanding, and Code Interpreter calculations** according to their purpose.

## Concepts and lab map

**What you will try:** Image/document understanding, schema-based field extraction, and CSV calculations with Code Interpreter.

**What is it, and why does it matter?** Vision describes image content, OCR/layout extracts text and positions, and Content Understanding interprets documents using the field structure you want. Code Interpreter is a separate tool that calculates over supplied data using code. Reading a receipt total in natural language is different from summing its rows to verify it, so business applications need both an output format and a comparison with the source.

**How do you use it?** Process the same synthetic receipt once as a free-form description and once as structured extraction, then compare missing values, guesses, and evidence. Next, calculate over the CSV's 9 rows and compare with the known monthly/overall totals. Correct values and source row counts matter more than attractive JSON or charts.

**Where do you run it?** Open the English [receipt.html](../../data/en/receipt.html) in a browser and read it alongside the [expected-results file](../../data/en/receipt.expected.json) and [expense CSV](../../data/en/monthly-spend.csv). Inference, analyzers, and Code Interpreter each require a supported portal/service and cost approval; simply opening a file does not count as completing a service execution.

## Prerequisites

Use `data/en/receipt.html`, `data/en/receipt.expected.json`, and `data/en/monthly-spend.csv`. No real receipts, bank accounts, or identity documents are needed. Content Understanding additionally requires the service, model deployments, permissions, and cost approval.

| Path | Prepare before execution | Retain |
| --- | --- | --- |
| Vision | An approved image-capable deployment and a readable PNG | Source image and extraction response |
| Content Understanding | An administrator-provided Foundry resource with default analyzer model connections | Field values, source locations, and available confidence/warnings |
| Code Interpreter | An agent supporting the tool and file-upload permissions | Actual execution record, 9-row aggregation, and an opening chart file |

Record execution separately for each path. Without prerequisites, practice interpretation below but mark **service not executed**. A model answer alone does not establish analyzer or code execution.

## Steps

### 1. Prepare the synthetic receipt

Open `data/en/receipt.html` and choose **Print → Save as PDF**. Reopen it and check that the document number, item row, total, and pending approval are not clipped. This PDF is the CU input. For Vision, capture the same document area or export it as a PNG from a viewer and check legibility. Do not supply a PDF to an image-only input. Use the English synthetic document, which has no validity as a real transaction.

### 2. Compare Vision with structured extraction

In L03's model Playground, select **your own image-capable deployment**. Attach the PNG, inspect its preview, and send the following question once. If attachments are unavailable or the format is rejected, check model/input support before changing the default model in `.env`.

```text
Extract the document number, date, currency, items, quantities, unit prices,
total, and purchase approval status from this synthetic receipt.
Use null for values that are not visible; do not guess.
```

The expected values are document `CONTOSO-2026-0929`, date `2026-09-29`, quantity 2, unit price KRW 89,000, total KRW 178,000, and **approval pending**. Understanding a printed document does not approve a real purchase.

### 3. Process the same document with a Content Understanding analyzer

Follow the entry point in the [Content Understanding Studio quickstart](https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/content-understanding-studio). **First check the administrator-provided resource and default model connections in Settings.** Do not enable automatic model deployment without approval. L02's single model does not necessarily meet every analyzer prerequisite.

Apply the [custom analyzer procedure](https://learn.microsoft.com/azure/ai-services/content-understanding/how-to/customize-analyzer-content-understanding-studio) in this order. A Studio project is not the same object as L01's Foundry project.

1. Select **Create project → Extract content and fields with a custom schema** and give it a lab name. With a supplied analyzer, start by inspecting its schema instead.
2. Upload the synthetic PDF and choose a suitable document/receipt template. Review the fields and descriptions below, then **Save**. Do not accept every suggested field.
3. Select **Run analysis** once. Open the source and results side by side and compare each value with its source location. Saving a schema alone is not successful analysis.
4. Only if a reusable analyzer is needed, select **Build analyzer** and record its name/resource/API version. Do not share displayed keys or autogenerated credential-bearing code.

| Field | Type | Expected value |
| --- | --- | --- |
| document_id | string | CONTOSO-2026-0929 |
| date | date | 2026-09-29 |
| currency | string | KRW |
| quantity | number | 2; separately verify an integral quantity |
| unit_price | number | 89000 |
| total | number | 178000 |
| approval_status | string | Normalize the document's pending approval to `pending`; never perform an approval |

Review **`2025-11-01` GA** as the default production API. Agentic mode and some classification/metadata/signature features in **`2026-06-01-preview`** are separate experiments. The September 2026 CU Toolkit/CU CLI is also in Preview.

For this single-item example, compare `quantity` and `unit_price` with `items[0]` in the expected-results file. Multiple-item documents need an array schema, not one representative value.

<div class="practice-block" markdown="1">

**Try it:** Open the [complete analyzer configuration](../../data/en/exercises/receipt-analyzer.json) in an editor. It is a **GA `2025-11-01` configuration example**, not a creation/analysis result. In Studio, replace suggested fields with the same **seven names, types, descriptions, and methods** under `fieldSchema.fields`. Do not send the full JSON to a chat box.

| Setting | Lab choice | Reason |
| --- | --- | --- |
| Base analyzer | `prebuilt-document` | Use the requested seven fields, not a receipt template's unrelated field names |
| Date / quantity | `date` / `number` | Supported CU field types; `integer` is not a type in this field schema |
| Literal values | `method=extract`, per-field `estimateSourceAndConfidence=true` | Request original locations and confidence |
| Currency | `method=generate` | Normalize the printed won indication to `KRW`, not a new amount |
| Approval state | `method=classify`, `pending/approved/unknown` | Classify the document; do not perform approval |
| Details | `returnDetails=true` | Inspect source positions as well as values |
| Model connections | Administrator-provided defaults on this resource | Do not insert L02's model name or enable automatic deployment |

Use the [analyzer configuration reference](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/analyzer-reference) for supported types and options. If Studio does not expose an option, request an analyzer using this JSON from the administrator and compare its name/settings. Do not silently substitute “similar” settings and claim identical conditions.

In the first result, inspect the target document under `contents` and its `fields`: the date value, numeric `quantity/unit_price/total`, and string `approval_status`. Record normalized values alongside highlighted source locations. Missing confidence means unavailable; do not enter an invented 1.0.

**Change one thing:** Add **only the item-code field `sku`** for the same document. Add the definition below under `fieldSchema.fields` in a copy of the configuration and add/save the same field in Studio. Preserve the first result/settings and obtain approval for one additional analysis before running it.

```json
{"sku":{"type":"string","method":"extract","description":"Extract the SKU code printed in the item row. Do not infer a code from the item name.","estimateSourceAndConfidence":true}}
```

Expect seven→eight fields and a new `sku` value of **KB-01**. Existing total 178,000, quantity 2, and pending approval should remain unchanged. Record absent or different results as observed. This tests **a changed output contract**, not a claim that the model became smarter.

**Explain the result:** Record `configuration change / new field / original values preserved / source evidence / unknowns`. Explain what new information you requested and why correct JSON types still need business-value checks. The baseline and additional analysis total at most two runs; do not repeat failed requests indefinitely.

</div>

| What to inspect | How to judge it | Next action on failure |
| --- | --- | --- |
| `total` and the document's total location | 178,000, matching 2 × 89,000 | Check clipping and whether unit price was mistaken for total |
| `approval_status` and original text | Pending, not approved | Check the field's extraction/normalization description; do not fill results from the answer key |
| Confidence, source grounding, warnings | Available evidence supports that field | An incorrect value fails even with high confidence. Missing confidence is unavailable, not zero |
| Null or omitted field | Withhold absent information; a visible omitted field is an extraction failure | Inspect legibility, then field name/type/description, then analyzer settings |

For OCR/layout alone, compare Document Intelligence. One correct document does not establish quality on other layouts or authority to approve real work.

### 4. Analyze numbers with Code Interpreter

In a lab agent's **Tools**, connect Code Interpreter or a Toolbox containing it and save the version. This is different from uploading the CSV to File search. Attach `data/en/monthly-spend.csv` in a new conversation and verify its name. If this UI is unavailable, review the supported path in the [official Code Interpreter documentation](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/code-interpreter) with the administrator; do not run the sample's cleanup code without approval.

```text
Calculate monthly expense totals from the CSV and create a bar chart.
Include the source row count, monthly totals, and overall total.
Do not add data that is not in the CSV.
```

Expected values for comparison:

| Month | Total (KRW) |
| --- | ---: |
| 2026-07 | 3,718,000 |
| 2026-08 | 2,677,000 |
| 2026-09 | 4,759,000 |
| Overall | 11,154,000 |

Inspect CSV-reading and aggregation code in the response's tool execution details. Require **9 rows excluding the header**, 3 monthly groups, and the correct overall total. Inspect the Code Interpreter execution item for a direct tool or the actual tool result for a Toolbox path. “I calculated it with Python” is not enough.

Download and open the chart; compare its month axis and KRW units with the table. For incorrect totals, check column names, numeric parsing, and missing/duplicate rows. For a broken download, inspect generated-file identifiers and session lifetime first. Without execution evidence, Code Interpreter remains unverified. Additional sessions can incur costs beyond model tokens.

### 5. Add image, video, and browser tools separately

| Capability | Optional exercise | Boundary |
| --- | --- | --- |
| Image generation | An illustrative image of a fictional product without copyright concerns | Check each model/tool's status; do not use the image as factual evidence |
| Video playground / video understanding | A time-based summary of a short synthetic scene | Generation and understanding are separate; check Preview status |
| Web search / Bing grounding | Compare public product specifications with dates and sources | Check external data transmission and search terms of use |
| Browser automation / Computer use | Read-only work on an approved test screen | Preview; exclude credentials, purchases, sending, and production UIs |

This is not an exercise in enabling every tool in the menu at once. Choose one tool you need and one failure scenario, then proceed optionally.

## Success criteria

Extracted fields match the source, and the synthetic CSV totals match the table. Record confidence, warnings, and source locations together. Label optional tools you did not execute as design/reference material.

## Troubleshooting

Check supported file formats, image resolution, analyzer model deployments, roles, regions, and API versions. Correct JSON structure with incorrect values is still a failure.

## Cleanup

Review whether uploaded files, generated files, sandbox sessions, analyzers, and additional model deployments need to be retained.
