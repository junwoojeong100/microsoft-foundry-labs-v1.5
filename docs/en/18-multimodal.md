> **What you will build:** Extract structured values from a fictional receipt, calculate totals from an expense CSV, and compare them with the originals.

## Objectives

Distinguish **Vision model descriptions, OCR/layout, schema extraction with Content Understanding, and Code Interpreter calculations** according to their purpose.

## Concepts and lab map

**What you will try:** Image/document understanding, schema-based field extraction, and CSV calculations with Code Interpreter.

**What is it, and why does it matter?** Vision describes image content, OCR/layout extracts text and positions, and Content Understanding interprets documents using the field structure you want. Code Interpreter is a separate tool that calculates over supplied data using code. Reading a receipt total in natural language is different from summing its rows to verify it, so business applications need both an output format and a comparison with the source.

**How do you use it?** Process the same synthetic receipt once as a free-form description and once as structured extraction, then compare missing values, guesses, and evidence. Next, calculate over the CSV's 9 rows and compare with the known monthly/overall totals. Correct values and source row counts matter more than attractive JSON or charts.

**Where do you run it?** Open the English [receipt.html](../../data/en/receipt.html) in a browser and read it alongside the [expected-results file](../../data/en/receipt.expected.json) and [expense CSV](../../data/en/monthly-spend.csv). Inference, analyzers, and Code Interpreter each require a supported portal/service and cost approval; simply opening a file does not count as completing a service execution.

## Prerequisites

Use `data/en/receipt.html`, `data/en/receipt.expected.json`, and `data/en/monthly-spend.csv`. No real receipts, bank accounts, or identity documents are needed. Content Understanding additionally requires the service, model deployments, permissions, and cost approval.

## Steps

### 1. Prepare the synthetic receipt

Open `data/en/receipt.html` in a browser and choose **Print → Save as PDF**. Use this English document rather than a Korean receipt image. The file is marked as synthetic lab data and has no validity as a real transaction.

### 2. Compare Vision with structured extraction

Provide a receipt image to a model that supports image input and request:

```text
Extract the document number, date, currency, items, quantities, unit prices,
total, and purchase approval status from this synthetic receipt.
Use null for values that are not visible; do not guess.
```

The expected values are document `CONTOSO-2026-0929`, date `2026-09-29`, quantity 2, unit price KRW 89,000, total KRW 178,000, and **approval pending**. Understanding a printed document does not approve a real purchase.

### 3. Process the same document with a Content Understanding analyzer

Use the current entry point in the [Content Understanding Studio quickstart](https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/content-understanding-studio). In the new Foundry portal's GA list, Content Understanding is an item requiring a separate experience; do not substitute another feature just because it is not visible on the screen.

Check for a supported invoice/receipt prebuilt analyzer, or create a custom analyzer with these fields.

| Field | Type | Expected value |
| --- | --- | --- |
| document_id | string | CONTOSO-2026-0929 |
| date | date/string | 2026-09-29 |
| currency | string | KRW |
| quantity | integer | 2 |
| unit_price | number | 89000 |
| total | number | 178000 |
| approval_status | string | pending |

Review **`2025-11-01` GA** as the default production API. Agentic mode and some classification/metadata/signature features in **`2026-06-01-preview`** are separate experiments. The September 2026 CU Toolkit/CU CLI is also in Preview.

Check field confidence, source grounding, and warnings together. High confidence does not guarantee business accuracy or approval authority. For OCR/layout-focused requirements, also compare the suitability of Document Intelligence capabilities.

### 4. Analyze numbers with Code Interpreter

Connect Code Interpreter to a supported agent in the English project and upload only `data/en/monthly-spend.csv`.

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

Verify that 9 rows were used and that you can actually open the generated files. Code Interpreter is a code-execution sandbox, not your company's trusted ERP calculation engine or a network gateway.

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
