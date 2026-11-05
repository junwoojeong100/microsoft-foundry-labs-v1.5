## Objectives

Connect three synthetic policies to `contoso-policy` and verify figures and conditions using actual citations or **the same request's retrieval output**.

<div class="lab-brief" markdown="1">

**Format:** Direct File search exercise: three files and two questions.

**Start here:** Download and extract the [portal input ZIP](../../downloads/Contoso-Portal-Inputs.zip). Use `en/policies`.

**What to check:** Three successful uploads, a saved attachment, an actual search call, and citations supporting each claim.

</div>

## Concepts and lab map

**What you will try:** File search, vector stores, indexing, and citations.

**What is it, and why does it matter?** Uploading is only the first step. Files must finish processing and be connected to the agent. A citation must support the specific claim, not merely name a relevant document.

**How do you use it?** Add exactly three files, wait until ready, and compare a policy question with an unknown-information question.

**Where do you run it?** Microsoft Foundry → Build → Agents → `contoso-policy` → Tools → Upload files. File search also appears under `Tools → Add → Add tools → Configured`. Knowledge's Add connects Foundry IQ; it is a different path.

## Prerequisites

Reuse L04's agent. Upload only `procurement-policy.md`, `expense-policy.md`, and `security-policy.md`. You can read the original [procurement](../../data/en/policies/procurement-policy.md), [expense](../../data/en/policies/expense-policy.md), and [security](../../data/en/policies/security-policy.md) documents in the browser. No PDF conversion or code is needed. Never substitute actual company documents.

**Check model compatibility first.** In the recorded environment, File search was disabled for `gpt-6-sol / contoso-chat`, with “This tool doesn't work with the model you selected.” Reuse L02's already approved `gpt-4.1 / 2025-04-14 / contoso-judge` deployment only for this **separate RAG version**. Despite its name, it is the answer model for this distinct experiment. Preserve L04's original version; both L08 comparison agents must still use `contoso-chat`. Without a compatible deployment, record unsupported rather than creating another model or region.

## Steps

### 1. Verify compatibility and a separate RAG version

These are Korean-run frames. For your English exercise, use the English instructions and `en/policies`, not text copied from the images.

<div class="screen-step" markdown="1">

**Grey File search? Check compatibility first**

![Disabled File search with the actual selected-model incompatibility message.](../../assets/portal/steps/files-unsupported.png)

**1 File search:** Do not keep clicking a disabled item. **2 Message:** The current model/tool combination is unsupported. Check the approved separate RAG conditions above first.

[Captioned video 03 · 00:16](../../downloads/portal/index.html?clip=03-retrieval-boundaries&t=16&lang=en#03-retrieval-boundaries)

</div>

| Step | Click or enter | Expected screen or value | If it fails |
| --- | --- | --- | --- |
| 1 | Open `Build → Agents → contoso-policy`. | L04's deployment and v2 instructions remain. | Stop if this is another agent or a Hosted target. |
| 2 | Open Model and select the supported existing `contoso-judge` deployment. | It is the deployed `gpt-4.1`; Upload files becomes available. | Read the compatibility warning and stop if File search is disabled. |
| 3 | Reenter `2048` under `Parameters → Max output tokens`; press `Tab → Esc → Save`. | A separate numeric version is saved. Changing models can clear the output limit. | Record both saved conditions rather than assuming the earlier version was overwritten. |

<div class="screen-step" markdown="1">

**Verify the model, then Upload files**

![Separate RAG configuration with contoso-judge selected and Upload files enabled.](../../assets/portal/steps/rag-model.png)

**1 Model:** `contoso-judge` is the answer model here. **2 Upload files:** Use the button under Tools, not the Knowledge connection below it.

[Captioned video 03 · 01:01.5](../../downloads/portal/index.html?clip=03-retrieval-boundaries&t=61.5&lang=en#03-retrieval-boundaries)

</div>

### 2. Upload only the three policies

| Step | Click or enter | Expected screen or value | If it fails |
| --- | --- | --- | --- |
| 1 | Select `Tools → Upload files`. | `Attach files` opens. | Do not create a Search service under Knowledge. |
| 2 | Keep Index option `Create a new index`; enter `contoso-policy-files-<your-suffix>` as Vector index name. | The store belongs to your exercise. | Do not add to a shared store or duplicate an existing owned store. |
| 3 | Select `browse for files` and choose **only the three** files in `en/policies`. | Three names and sizes appear; uploading starts. | Do not upload the whole folder, evaluation files, or real documents. |

<div class="screen-step" markdown="1">

**Uploading is not Success**

![New-index selection, browse for files, and three policy rows still Uploading.](../../assets/portal/steps/files-upload.png)

**1 Index option:** Your new store. **2 Uploading:** Keep waiting. **3 browse for files:** Choose only the three files; do not upload again while pending.

[Captioned video 03 · 01:07](../../downloads/portal/index.html?clip=03-retrieval-boundaries&t=67&lang=en#03-retrieval-boundaries)

</div>

<div class="screen-step" markdown="1">

**Attach only after all three rows say Success**

![Successful procurement, expense, and security uploads with Attach enabled.](../../assets/portal/steps/files-success.png)

**1 Names:** Compare all three policies. **2 Status:** Every row must say `Success`. **3 Attach:** Select once; Save in the agent afterward to retain the attachment.

[Captioned video 03 · 01:17](../../downloads/portal/index.html?clip=03-retrieval-boundaries&t=77&lang=en#03-retrieval-boundaries)

</div>

| Step | Click or enter | Expected screen or value | If it fails |
| --- | --- | --- | --- |
| 1 | Wait until all three Status values are `Success`. | None is Uploading, Not started, or Failed, and Attach is enabled. | Upload success is not search success. Preserve errors without duplicate uploads. |
| 2 | Select `Attach` once and wait until the dialog closes. | `File search` appears under Tools. | Do not click again while Attaching. |
| 3 | Select `Save` once and verify the new numeric version. | The model and File search attachment are saved. | Do not send a question if saving failed. |

<div class="screen-step" markdown="1">

**Check the attached File search in the agent**

![Actual editor with contoso-judge selected and File search under Tools.](../../assets/portal/steps/files-attached.png)

**1 Model / 2 File search:** Both must match. This frame is after Attach; a visible attachment alone does not establish saved configuration or successful retrieval.

[Captioned video 03 · 01:35](../../downloads/portal/index.html?clip=03-retrieval-boundaries&t=95&lang=en#03-retrieval-boundaries)

</div>

<div class="screen-step" markdown="1">

**Reopen after Save: retain the RAG version and attachment**

![Policy agent Version 4 and Save/Publish control locations.](../../assets/portal/steps/policy-version-bar.png)

**1 Version:** The recorded separate RAG version is `4`. Verify your own saved number, model, and File search together. **2 Save / 3 Publish:** Saving is required; publishing is not this exercise. A version number alone does not establish retrieval success.

[Captioned video 05 · 01:36](../../downloads/portal/index.html?clip=05-inspection-retention&t=96&lang=en#05-inspection-retention)

</div>

### 3. Verify answer, citations, and the same request's retrieval

| Step | Click or enter | Expected screen or value | If it fails |
| --- | --- | --- | --- |
| 1 | Send the first question once in `New chat`. | An actual File search call, policy answer, and citations appear. | Preserve processing/attachment errors. Without a tool record, this is model-only output. |
| 2 | Select a citation number/file link. If no preview opens, use the response's `Traces → Execute Tool execute_tool file_search.msearch → Input + Output` to read the actual returned document. | Laptop cap KRW 1,500,000, VAT included, and 36 months match procurement §2 in the retrieval result. | A filename alone or an unavailable source/result is not completed evidence verification. |
| 3 | Send the second question once in `New chat`. | The answer identifies missing information and the authorized next step. | Preserve invented overseas rules as a failure. |

```prompt
What are Contoso's per-unit standard laptop cap, VAT treatment, and regular replacement interval? Cite the document and section for each claim.
```

```prompt
Tell me the laptop purchasing cap at Contoso's overseas branches and my individual salary. Do not guess anything absent from the documents.
```

<div class="screen-step" markdown="1">

**Policy answer: pair every figure with its citation**

![Actual policy answer with the cap, VAT, 36-month interval, citations, and Traces.](../../assets/portal/steps/policy-answer.png)

**1 Claims:** Compare cap, VAT, and interval with the source. **2 Citations:** Open the specific file/section. **3 Traces:** If preview fails, inspect the same request's returned content.

[Captioned video 03 · 02:09](../../downloads/portal/index.html?clip=03-retrieval-boundaries&t=129&lang=en#03-retrieval-boundaries)

</div>

<div class="screen-step" markdown="1">

**Trace: select the real search span below the agent**

![Actual timeline with Execute Tool file_search.msearch and Chat below Invoke Agent.](../../assets/portal/steps/policy-trace.png)

**1 Invoke Agent:** The parent request. **2 Execute Tool:** Select this row to open retrieval details. The pictured parent is selected; this is not yet the returned-content pane.

[Captioned video 03 · 02:30](../../downloads/portal/index.html?clip=03-retrieval-boundaries&t=150&lang=en#03-retrieval-boundaries)

</div>

<div class="screen-step" markdown="1">

**Input + Output: read the actual returned policy**

![file_search.msearch details with query input and returned procurement-policy content.](../../assets/portal/steps/trace-input-output.png)

**1 Input + Output:** Inspect queries and returned results together. **2 Content source:** Read procurement §2 and compare its figures and conditions with the uploaded original.

[Captioned video 03 · 04:18](../../downloads/portal/index.html?clip=03-retrieval-boundaries&t=258&lang=en#03-retrieval-boundaries)

</div>

### Record citation checks

In the recorded environment, citation buttons did not open a preview. The actual returned policy text was inspected in the same request's retrieval span instead. Clicking a control and verifying its source are different outcomes.

| Claim | Source to open | Decision |
| --- | --- | --- |
| Laptop cap, VAT, 36 months | Procurement policy §2 | Figure, currency, and inclusion condition must all match |
| At most KRW 2,000,000: team lead; above: team lead and procurement | Procurement policy §3 | Equality must not be treated as strictly above |
| Unknown overseas policy and individual salary | Procurement §5 and the security access boundary | Do not conflate missing information with denied access |

## Success criteria

All three files are ready, and you inspected actual retrieval and source citations. A policy **cap** is not a current sale price or stock level. An unrelated cited section still fails.

## Troubleshooting

For empty answers, check processing state, agent attachment, then question wording/language. Do not use duplicate uploads or unbounded sends. Follow [troubleshooting](#troubleshooting) for account and network errors.

## Cleanup

Retain the store and files for subsequent modules. Storage charges can remain after closing the browser. Deletion requires separate approval.

<div class="lab-handoff" markdown="1">

**Keep:** Three file states, connected store, actual questions/answers, and the source section checked for each claim.

**Continue:** [L06: inspect purchasing-tool execution boundaries](#l06).

</div>
