> **What makes the course successful:** Not whether everyone saw the same screen, but whether each learner can explain the boundaries of evidence, tools, safety, and evaluation—and has completed cleanup for the resources they created.

## The day before the course

### Readiness for participants new to Azure

Do not make account/subscription registration an improvised classroom task. Supply each learner's **sign-in organization, project, model deployment name, and cost/cleanup owners** using L01's table. Participants without that setup start with reading/local exercises and are not counted as having completed Azure execution.

Before the first call, check that each learner can open the lab root, distinguish the terminal from a portal input, and find placeholders and expected output. If not, use [local troubleshooting](#troubleshooting) before explaining another feature.

Start each chapter with ‘Format → Start here → What to check.’ Only relevant participants expand **administrator-only/optional** sections. L08 starts with instructions and questions; collecting and evaluating the learner's own answers is optional. Review the integrated result once, in the second half of L06.

Default web progress is **11 core modules plus wrap-up**, advanced progress is **eight plus wrap-up**, and the 90-minute path has **six**. Do not require all 20 checkmarks for core completion. L02 checks a supplied deployment; L04/L05 reuse one portal agent. L06's SDK creates a separate integrated agent, so record its name and response file separately.

Start with **block destination → one command → expected-result comparison**, rather than more background reading. In a new terminal, recheck L01's Python path and English profile. Use L06's `Read again` to inspect originals, functions, and citations; do not rerun `capstone --live` just to see a saved result.

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
| 80–90 minutes | L19 cleanup | Record resources deleted/retained |

Do not try to mark function execution, orchestration, and Hosted deployment all “complete” within 90 minutes.

## One-day / two-day delivery

Core L00–L10 totals **285 minutes (4 hours 45 minutes)**, with **10 minutes** for shared wrap-up L19: 295 minutes (4 hours 55 minutes) combined. Add breaks, resource waits, and questions. Give faster teams failure analysis rather than more features to add.

The eight advanced modules (L11–L18) total **335 minutes (5 hours 35 minutes)**,
and core plus advanced plus wrap-up totals **630 minutes (10 hours 30 minutes)**. Plan for two days with a
prepared environment, allowing additional time for breaks, questions, and Azure waits.
These durations reflect the direct/conditional/design scope shown in each chapter.
Allow separate time for beginners to read concepts, explore the portal, and ask about command walkthroughs. Do not treat the existing sum of hands-on durations as a fixed end time for the entire class.
Administrator approval, regional quota availability, Hosted deployment, and indexing may require additional time.
There is no guarantee that live execution of every optional service will finish within these times.

## Sequential core / independent and connected advanced paths

The core sequence is **L00 → L01 → … → L10 → L19**. If choosing electives, take them after L10 and finish with L19.
L08 is a **12-question fixed dev comparison using a tool-free Prompt Agent**.
It does not reuse L05/L06 retrieval/function results; Search, Hosted, Optimizer, and holdout are not prerequisites.
L09 separately inspects harmless boundary questions and L06 function evidence; L10 correlates actual L05/L06 responses with traces.
L07's local steps 1–2 are required in the core course; cloud Toolbox/Skills are optional extensions.
Integration review is consolidated into L06; publishing and active-version management are in L18 CI/CD. L18 is optional for deployment/operations owners, and organizational publishing access is not a core completion requirement.

| Path type | Modules | How to proceed |
| --- | --- | --- |
| Independent option | L11, L13, L15, L17 | After the shared core environment is ready, meet the chapter's prerequisites and optionally execute it |
| Prerequisite lab required | L12 | Run Hosted after preparing L11's Search/index. If equivalent resources are already provided, the L11 lesson itself may be skipped |
| Choose after environment setup | L14 | Reuse L13's dedicated SDK environment and throughput check; paid runs in the preceding lab are not required |
| Elective for operations owners | L18 | L01 environment/sources for CI, release, publishing, and rollback design; actual deployment/publishing needs separate preparation and approval |
| Feature-specific branch | L16 | Prompt Routine is independent after L05. The Hosted long-running branch requires L12 |

The live Hosted connection is **L11 → L12 → L18 optional live deployment**.
L18's default CI/design is independent of that chain; do not add paid prerequisites merely to complete another chapter.
“Independent option” does not mean “no additional installations, permissions, or models.” Check each chapter's **Prerequisites** and execution-level label.
Do not assume that completing the core course prepares every conditional lab requiring separate models, services, devices, or licenses.

Choose second-day work by team goals.

| Team | Recommended advanced modules |
| --- | --- |
| Application development | L11 IQ, L12 Hosted, L13/L14 orchestration, optional L18 CI/CD |
| Platform/security | L15 memory, L16 automation, L17 governance, L18 CI/CD |

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
Keep execution records outside the reader and kit. Portal images retain their original capture provenance and do not validate a new instruction edit.

## Coaching the later modules

### Require an explanation of the before/after change

The reinforced L13, L14, L17, and L18 exercises follow **Try it → Change one thing → Explain the result**. Ask learners to predict an outcome first, then connect one edited setting/code change to the observed difference.

| Module | Learner change | Evidence to retain |
| --- | --- | --- |
| L13/L14 | Compare sequential/concurrent and group-chat/handoff in two focused labs under the same model/policy/question | Execution order, intermediate/final answers, and tokens/time; missing usage stays null |
| L17 | Check permission before cache | Two of five local tests fail→five pass; not Azure permission verification |
| L18 | Require quality/critical/missing checks beyond completion | Three of five fail→five pass; optional workflow has no Azure step |

Flawed code and tests under `data/exercises/` are teaching originals. Learners repair **only exercise.py** in their `practice/` copy. Never weaken global tests/evaluation criteria or overwrite originals. Preparation rejects an existing destination; choose another folder for a fresh attempt.

Local code/SDK contract checks do not establish real Azure calls, permission changes, or deployment. Optional service waits and approvals are outside the hands-on time estimates.

Ask each learner **“Which value is evidence → what decision follows → what do you inspect first on failure?”** If that explanation is missing, revisit evidence for the same case rather than adding another feature.

| Module | Minimum learning artifact | Judgment to check |
| --- | --- | --- |
| L09/L10 | Three boundary judgments / one run's operations and durations | Separate natural-language refusal from function rejection, and trace correlation from correctness |
| L13/L14 | Compare flow and intermediate/final answers for the patterns selected in both labs | Distinguish SDK execution order from remote protocols, and handoff from human approval |
| L17 | Identity/access table and cache boundary | Adapt worked examples to the learner's input/owners and mark unknowns |
| L18 | CI interpretation and agent release/rollback manifest | Separate documentation generation, Azure deployment, and business release approval |

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
- Forgetting routine, evaluation, Hosted, or Search costs after closing the browser.

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
