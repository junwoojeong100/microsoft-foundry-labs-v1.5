> **What makes the course successful:** Not whether everyone saw the same screen, but whether each learner can explain the boundaries of evidence, tools, safety, and evaluation—and has completed cleanup for the resources they created.

## The day before the course

### Readiness for participants new to Azure

Do not make account/subscription registration an improvised classroom task. Supply each learner's **sign-in organization, project, model deployment name, and cost/cleanup owners** using L01's table. Participants without that setup start with reading/local exercises and are not counted as having completed Azure execution.

Before the first call, check that each learner can open the lab root, distinguish the terminal from a portal input, and find placeholders and expected output. If not, use [local troubleshooting](#troubleshooting) before explaining another feature.

Start each chapter with ‘Format → Start here → What to check.’ Only relevant participants expand **administrator-only/optional** sections. Read L08's actual answers in the learner's own language inside the guide first; new paid collection is a separate choice. L11 reuses L06's result.

Recheck GA/Preview status, regions, and model support against official sources. The initial source check was on 2026-09-29. Consult [content/portal-screenshots.en.json](../../content/portal-screenshots.en.json) for the English project's actual capture times and scope; do not reuse the old Korean capture date as proof of a new observation. Neither a source date nor a screenshot means the material remains current forever.

Have learners first explain each chapter's **Concepts and lab map** in their own words. After they locate the relevant portal screen, connect it to why the CLI is needed. Allow execution only after they read the **Result / cost or changes** column in the command walkthrough. Encourage pauses between plan → execute → verify instead of copying an entire group of commands at once.

Account and identifying information in the images has been deliberately redacted. Tell learners not to copy example agent names, versions, or trace IDs as their own execution values. **Portal observation / local execution / paid model calls / deployment / permission changes / deletion** involve different approvals and outcomes. If a screen differs, check region, permissions, project, and UI timing; do not create resources just to force a match with the image.

Prepare the English class in a **separate clean checkout/worktree**, with its own `.env`, `.azure/`, and `results/`, and an approved English project such as `contoso-workshop-en`. Have every learner select `FOUNDRY_LAB_LANGUAGE=en` using L01's shell-specific command, and reselect it in every new terminal. The HTML language switch does not choose the runtime corpus. Use only `data/en/` inputs and English-bound Hosted packages; never copy Korean private settings, receipts, or completed results.

| Preparation | Evidence of completion |
| --- | --- |
| Test subscription/project/model | First call under **learner permissions**, not the instructor's account |
| Appropriate roles and quota | Agent creation, file upload, evaluation, and logs checked separately |
| Cost responsibility and limits | Approver, person responsible for stopping work, and time to verify shutdown |
| Data | Distribute the English synthetic files in `data/en/`; verify the selected profile, not just the reader language |
| PC environment | Separate core/advanced venvs and compliance with internal package policies |
| Preview permission | Replace disallowed features with design exercises |
| Network | Approved execution location, DNS, and log access |
| Cleanup | Inventory of created resources, with shared resources marked |

## A 90-minute core experience

This assumes **an environment with deployment and permissions already prepared**. It does not mean the whole of L01 can be completed in 10 minutes.

| Time | Activity | Result to retain |
| --- | --- | --- |
| 0–5 minutes | L00 platform and final outcome | Distinguish models, agents, knowledge, and tools |
| 5–15 minutes | L01 check the prepared environment | Project, model, and permissions |
| 15–35 minutes | L04 Prompt Agent | Withhold answers when information is absent |
| 35–60 minutes | L05 File search | 2 answers with citations |
| 60–80 minutes | L08 evaluation and analysis | Read and judge one row's v1/v2 answers and native reasons from the prepared 12-question comparison |
| 80–90 minutes | L12 cleanup | Record resources deleted/retained |

Do not try to mark function execution, multi-agent work, and tuning all “complete” within 90 minutes.

## One-day / two-day delivery

The core L00–L12 hands-on time totals **320 minutes (5 hours 20 minutes)**. Add breaks, resource waits, and questions. Give faster teams failure analysis rather than more features to add.

The current advanced L13–L24 learning time totals **440 minutes (7 hours 20 minutes)**,
and core plus advanced totals **760 minutes (12 hours 40 minutes)**. With a prepared environment,
breaks, questions, and Azure waits, **2–3 days (roughly 14–20 hours)** is a realistic course schedule.
These durations reflect the direct/conditional/design scope shown in each chapter.
Allow separate time for beginners to read concepts, explore the portal, and ask about command walkthroughs. Do not treat the existing sum of hands-on durations as a fixed end time for the entire class.
Actual fine-tuning, administrator approval, regional quota availability, and on-device model downloads can take several additional hours to a day or more.
There is no guarantee that live execution of every optional service will finish within these times.

## Sequential core / independent and connected advanced paths

The core sequence is **L00 → L01 → … → L12**.
L08 is a **12-question fixed dev comparison using a tool-free Prompt Agent**.
It does not reuse L05/L06 retrieval/function results; Search, Hosted, Optimizer, and holdout are not prerequisites.
L09 separately inspects harmless boundary questions and L06 function evidence; L10 correlates actual L05/L06 responses with traces.
L07's local steps 1–2 are required in the core course; cloud Toolbox/Skills are optional extensions.
Actual Teams publishing in L11 is also a conditional extension, so lacking organizational publishing permission does not prevent core-course completion.

| Path type | Modules | How to proceed |
| --- | --- | --- |
| Independent option | L13, L15, L16, L18, L19, L21, L23, L24 | After the shared core environment is ready, meet the chapter's prerequisites and optionally execute it |
| Prerequisite lab required | L14 | Run Hosted after preparing L13's Search/index. If equivalent resources are already provided, the L13 lesson itself may be skipped |
| Run after source setup | L22 | L01 environment/sources for CI interpretation and release/rollback design. Only optional live Hosted deployment needs L14 and separate approval |
| Feature-specific branch | L17 | Prompt Routine is independent after L05. The Hosted long-running branch requires L14 |
| Feature-specific branch | L20 | Hosted Optimizer requires L14's Responses deployment first. Fine-tuning data/model work is independent once its own prerequisites are met |

The live Hosted connection is **L13 → L14 → {L20 Hosted Optimizer or L22 optional live deployment}**.
L22's default CI/design is independent of that chain; do not add paid prerequisites merely to complete another chapter.
“Independent option” does not mean “no additional installations, permissions, or models.” Check each chapter's **Prerequisites** and execution-level label.
Do not assume that completing the core course prepares every conditional lab requiring separate models, services, devices, or licenses.

Choose second-day work by team goals.

| Team | Recommended advanced modules |
| --- | --- |
| Application development | L13 IQ, L14 Hosted, L15 orchestration, L22 CI/CD |
| Platform/security | L16 memory, L17 automation, L21 governance, L24 migration |
| Documents/voice | L18 multimodal, L19 voice, L20 optimization, L23 extensions |

## Completion record

The table below is an **educational completion record**, not service certification or a score.

| Module/target | Executed / design / not executed | Evidence ID or file | Pass/fail | Unresolved items |
| --- | --- | --- | --- | --- |
| Model call | Record explicitly | Response ID | Judge explicitly | Record explicitly |
| Document retrieval | Record explicitly | Citation + original text | Judge explicitly | Record explicitly |
| Tools | Record explicitly | Arguments/output | Judge explicitly | Record explicitly |
| Evaluation | Record explicitly | L08 response/native JSON and case ID | Judge explicitly | Record explicitly |
| Tracing | Record explicitly | Trace ID | Judge explicitly | Record explicitly |
| Deployment/publishing | Record explicitly | Version + invocation result | Judge explicitly | Record explicitly |
| Cleanup | Record explicitly | Per-resource status | Judge explicitly | Cost owner |

This record is separate from the web guide's progress checkboxes. Browser progress does not connect to Azure.

Use L08's same 12 composite development questions once with the educational v1 baseline and improved v2. Keep model, context, output format, and evaluation criteria identical. Have learners explain the actual per-row answers and native reasons; ties and regressions are valid observations, not reasons to resample.

No Optimizer, new holdout, or repeated release run is required for the lesson. The separate full business gates remain strict and are not replaced by the small learning checklist.
Only [current instructions and latest evidence](../../validation/current/instructions.json) remain in the reader; older originals are preserved in Git history. Portal images retain their original capture provenance and are not fresh v2 validation.

## Coaching the later modules

### Require an explanation of the before/after change

The reinforced L15 and L18–L24 exercises follow **Try it → Change one thing → Explain the result**. Ask learners to predict an outcome first, then connect one edited setting/code change to the observed difference.

| Module | Learner change | Evidence to retain |
| --- | --- | --- |
| L15 | Single→two roles under the same model/policy; optional boundary question | Baseline/drafter/reviewer originals and actual tokens/time; missing usage stays null |
| L18 | Add only SKU to the complete schema | Seven→eight fields, KB-01 source location, preserved original values |
| L19 | Silence detection 500→1500ms | Identical utterance splitting/wait/end comparison; learners operate their own microphones |
| L20 | Repair a label typo in a copy; optional approved SFT lifecycle | Rejection→16/8 files; optional job/checkpoint and identical eight questions |
| L21 | Check permission before cache | Two of five local tests fail→five pass; not Azure permission verification |
| L22 | Require quality/critical/missing checks beyond completion | Three of five fail→five pass; optional workflow has no Azure step |
| L23 | Local output style or Fabric month filter | Changed condition and actual response/total under the same model/data |
| L24 | Repair conversation ID, call_id, JSON string | Three of four fail→four pass; not a real migration |

Flawed code and tests under `data/exercises/` are teaching originals. Learners repair **only exercise.py** in their `practice/` copy. Never weaken global tests/evaluation criteria or overwrite originals. Preparation rejects an existing destination; choose another folder for a fresh attempt.

A complete procedure is not completed Azure/device execution. Local code/SDK contract checks do not establish real SFT, Voice, Local-model, Fabric, or Work IQ execution. Optional service waits, downloads, and approvals are outside the existing hands-on time estimates.

Ask each learner **“Which value is evidence → what decision follows → what do you inspect first on failure?”** If that explanation is missing, revisit evidence for the same case rather than adding another feature.

| Module | Minimum learning artifact | Judgment to check |
| --- | --- | --- |
| L09/L10 | Three boundary judgments / one run's operations and durations | Separate natural-language refusal from function rejection, and trace correlation from correctness |
| L18/L19 | Fields compared with sources / quantity correction, interruption, ended state | Attractive JSON or audible output alone is not execution success |
| L20 | Explanation of one generated JSONL row and the 16/8 split | A classification label is neither a draft execution nor completed training |
| L21/L23/L24 | Identity/access table, selected extension specification, migration/recovery table | Adapt worked examples to the learner's input/owners and mark unknowns |
| L22 | CI interpretation and agent release/rollback manifest | Separate documentation generation, Azure deployment, and business release approval |

Synthetic trace timings, Red teaming counts, and design tables are **teaching examples**. Do not copy them into actual Azure evidence fields. Without service access, record design/interpretation complete and execution incomplete separately. This does not replace or weaken existing evaluation gates.

## Failure signals instructors should watch for

- Passing an invented policy because the model's wording sounds natural.
- A source name with no actual citation or retrieval result.
- Judging an external action successful based only on natural-language claims such as `approved` or `ordered`.
- Averaging only the 17 successful cases when 3 out of 20 failed.
- Repeatedly revising a prompt while looking at the holdout.
- Running English instructions against Korean data, importing another run's receipts, or labeling Korean results as new English evidence.
- Presenting all Preview capabilities to customers as production-ready.
- Teaching new-portal Workflows as the recommended path for new production implementations.
- Forgetting routine, evaluation, voice, or Search costs after closing the browser.

## Feature selection worksheet

Have each team answer each question in one sentence.

| Question | Answer template |
| --- | --- |
| Why an agent? | A single model call is insufficient because ___ |
| Why this knowledge approach? | Among File search/Search/IQ, we chose ___ because ___ |
| Why this model? | Evaluation ___, latency ___, pricing conditions ___ |
| Who authorizes execution? | Principal ___, stored approval evidence ___ |
| Where do you investigate failure? | Response/trace ___, responsible person ___ |
| When do you stop? | Quality/safety/cost criteria ___ |
| Which Preview capabilities do you depend on? | Feature ___, alternative path ___ |

## Final completion check

Policy answers have real evidence, and answers are withheld when information is missing. Invalid quantities and unauthorized access are blocked. Average scores and critical failures are considered separately. The deployed version and recovery path are known. Finally, verify **the paid resources that remain and who is responsible for them**.
