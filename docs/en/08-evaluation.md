> **What you will build:** In the core course, learn to evaluate real responses. In the advanced path, use an independent holdout to decide whether an automated quality gate passes.

## Objectives

**Successful execution, passing automated quality checks, and human review are different states.**
The current `automated-v3` suite for this synthetic lab can be completed through code checks and native evaluation without a human reviewer.
Human review is recommended before real production use; never mark a review as complete when it has not happened.

## Concepts and lab map

**What you will try:** Collecting real responses, code-based business checks, native evaluators, judge calibration, and dev/holdout quality gates.

**What is it, and why does it matter?** Evaluation compares results against predefined questions and criteria. The target is the assistant being evaluated; the judge is a separate model that assesses its answers. Calibration first checks the judge's decisions against known correct and incorrect controls. Dev examples are practice questions you inspect repeatedly while improving the system; the holdout is the frozen candidate's final independent test. Editing prompts while looking at the exam, or averaging only easy rows, may improve the numbers without making them trustworthy.

**How do you use it?** In the core course, collect responses from L05/L06 and read why they passed or failed. In the advanced path, keep the questions, model, code, and criteria fixed for dev checks, and use the independent holdout only at the end. A service status of `completed` means the job has finished; quality-gate passage must be determined separately from individual results and mandatory conditions.

**Where do you run it?** Use the CLI/SDK for collection and automated checks, and the portal's Evaluations area to explore results. First read the [evaluation runner](../../samples/evaluation_lab.py), [suite-selection code](../../samples/evaluation_data.py), and [v3 criteria](../../data/evaluation/v3/rubric.json). Do not open the sealed holdout early or rerun evaluations just to capture screenshots.

## Prerequisites

**Core sequential path:** Only the project, Prompt Agent, and client-side functions from L05/L06 are required.
You do not need to finish L13 Search or L14 Hosted first. Prepare the target and a separate judge deployment in L02.

**Advanced automated release path:** Prepare the real Search and Hosted agent from L13/L14,
and set `FOUNDRY_JUDGE_DEPLOYMENT_NAME`. The `automated-v3` instructions below follow this path.

| Material | Purpose |
| --- | --- |
| `data/evaluation/cases.jsonl`, `rubric.json` | Original v1, preserved to reproduce historical failures and existing commands |
| `data/evaluation/v2/` | Unchanged dev/holdout data and criteria from the first automated validation |
| `data/evaluation/v3/dev.jsonl` | The 30 already exposed v1/v2 cases converted into dev regression tests |
| `data/evaluation/v3/holdout.jsonl` | 10 newly and independently authored cases with a sealed hash; not used for improvement |
| `data/evaluation/v3/calibration.jsonl` | 8 correct/incorrect controls to test the judge itself; not target-execution evidence |
| `data/evaluation/v3/rubric.json` | Human review is optional; the 90% threshold and zero safety/access failures remain unchanged |

`context` is reference-answer context supplied by the evaluation author. Do not substitute it for actual retrieval results to inflate groundedness.
The new runner uses actual `retrieved_sources`, tool arguments/results, citations, and response/trace IDs.

## Steps

### Core course: Automatically evaluate L05/L06 results for learning

![The live Build → Evaluations Runs list. Evaluation names, last runs, run counts, and Completed, Canceled, and Partial statuses are visible. Author names are masked.](../../assets/portal/08-evaluations.png)

**Reading the screen:** In **Build → Evaluations → Runs**, find your evaluation name and execution time. **Status of last run** is the service job's state; open individual runs and inspect case-level scores, errors, and missing results before judging quality. **Evaluator catalog** is for exploring evaluation criteria, while **Recurring configs** configures ongoing execution. Do not accidentally create a schedule during the core lab. Existing failures and cancellations were not hidden in the capture, and no new evaluation was submitted.

```bash
python samples/workshop.py evaluate --split dev --live
python samples/evaluation_lab.py calibrate --suite basic-learning --live
python samples/evaluation_lab.py run --suite basic-learning --split dev --input results/앞-명령이-출력한-responses.jsonl --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — In the core course, perform only these three steps, then continue to L09.

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `workshop.py evaluate --split dev --live` | Runs the basic SDK assistant on dev questions and collects real responses, tool results, and citations. `--split dev` selects only development questions. | Incurs model/retrieval costs and creates a response JSONL file. Replace the Korean filename placeholder in command 3 with the actual output path from this command. |
| 2. `calibrate --suite basic-learning --live` | `--suite` selects the learning evaluation policy and sends correct/incorrect controls to the judge. | Incurs judge costs. Agreement checks the evaluator; it is not a target-quality pass. |
| 3. `run --suite basic-learning ...` | Evaluates the real response file specified by `--input` against the same dev criteria. `run` does not fabricate new target responses. | Incurs native evaluation/judge costs. Inspect scores, errors, and failure reasons; do not use learning results as independent release evidence. |

</div>

Learn the evaluation process using the 10 exposed dev cases from the original SDK path. You do not need to fill in human judgments.
If model quality falls short, the evaluation command reports failure. Explaining its causes and the next improvement is the core learning objective.
`basic-learning` results are not deployment-quality evidence from an independent holdout.
After this step, continue to L09. Return to the advanced integration below once Hosted is ready.

### 1. Run local automated checks

```bash
python scripts/prepare_eval_v3.py
python -m unittest discover -s tests -v
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `prepare_eval_v3.py` | Prepares already exposed v1/v2 cases as v3 dev regression data. Verifies matching existing files and refuses to overwrite differing ones. | Local data preparation/consistency checks. Does not read the v3 holdout or create new Azure responses. |
| 2. `python -m unittest discover -s tests -v` | The `unittest` module discovers tests under `tests/`. `-s` sets the starting folder; `-v` displays each test name. | Runs local contract and regression checks. Passing does not establish actual Azure quality. |

</div>

The first command converts the 30 original and exposed v2 cases into dev regressions; it neither reads nor creates the v3 holdout.
It does not overwrite prepared files if they differ. The old v1/v2 holdouts are not v3's final exam.
Do not claim actual model quality from unit-test success alone.

### 2. Ensure the model cannot skip retrieval

When Hosted receives a question, the server queries Search first.
It retrieves all 13 sections of the small synthetic policy set from actual Search together, so that compound questions do not miss necessary clauses.
The server also performs a read-only inventory lookup first for any SKU explicitly named in the question, preventing an answer that merely plans to “check inventory.”
The actual function definitions are included in execution evidence so that quantity limits can be verified as tool-input constraints, not company policy.
The model's `answer` and `citation_ids` are checked against a strict JSON contract.

Empty citations, sources not returned by retrieval, incorrect document names, and altered content all fail.
The server does not guess and append filenames. It renders **only actual sources selected by the model** for display.
Inventory and draft numbers and statuses are checked against separate, actual tool results.
If the user's actual message contains no draft quantity, the tool is not executed even if the model proposes a valid number.
The source-attribution check's original `raw_attribution` and response ID are also preserved to verify evidence selection.

### 3. Improve on dev, then freeze the configuration

```bash
python samples/hosted_client.py evaluate --suite automated-v3 --split dev --version 실제숫자 --live
python samples/evaluation_lab.py prepare --suite automated-v3 --split dev --input results/실제-dev-responses.jsonl
python samples/evaluation_lab.py calibrate --suite automated-v3 --live
python samples/evaluation_lab.py run --suite automated-v3 --split dev --input results/실제-dev-responses.jsonl --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — The advanced path, after completing L13/L14.

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `hosted_client.py evaluate ... --version` | Sends the 30 cases in `--suite automated-v3 --split dev` to the exact numeric Hosted agent version. Replace `실제숫자` (“actual number”) with the version from deployment; do not use `latest`. | Incurs real Hosted, model, and retrieval costs and creates a response JSONL file. Verify that the session's compute is stopped afterward. |
| 2. `evaluation_lab.py prepare ... --input` | Reads the actual file from the preceding command and checks IDs, questions, retrieval, tools, citations, and evaluation inputs. Replace the Korean filename placeholder with that real path. Runs locally without `--live`. | Inspect row counts, hashes, and evidence failures. Does not generate new scores or model responses. |
| 3. `calibrate --suite automated-v3 --live` | Checks the judge's expected decisions against the 8 v3 controls. | Incurs judge cost. If results disagree, diagnose the evaluator/configuration rather than lowering the criteria. |
| 4. `run --suite automated-v3 --split dev` | Uses the same collected dev originals and fixed criteria for native evaluation and business gates. Use the actual dev response path here too. | Incurs remote evaluation costs. Preserve failures from both code checks and the judge. |

</div>

Preserve original responses with append-only evidence. Record retries as new runs.
Compare the same data, rubric, judge, model, and runtime hash, then freeze the candidate to be validated.
If native evaluation fails because the authentication identity differs, the same evaluation can use L22's approved OIDC dev path.

### 4. Use the new holdout only once, as the final test

```bash
python samples/hosted_client.py evaluate --suite automated-v3 --split holdout --version 동결한숫자 --live
python samples/evaluation_lab.py run --suite automated-v3 --split holdout --input results/실제-holdout-responses.jsonl --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Run only as the final test after dev approval and configuration freeze.

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `evaluate --split holdout --version` | Collects the 10 independent holdout cases once against the exact frozen version. Replace `동결한숫자` (“frozen number”) with that version. A suite run marker restricts recollection. | Incurs real Hosted, retrieval, and model costs and creates original responses. Do not rerun failed cases until they pass. |
| 2. `run --split holdout --input` | Judges the newly preserved originals with the same suite and judge. For `--input`, replace the Korean filename placeholder with this holdout response file, not a dev file. | Incurs remote evaluation costs. Check every gate, including zero safety/access failures—not just 90% overall. |

</div>

A run marker is kept for each sealed suite fingerprint to prevent accidental resampling.
Do not rerun the same exam until it passes because model responses failed.
If further improvement is needed, preserve that exam as diagnostic material and prepare a new, independent holdout version.
Even when correcting JSON parsing or transmission problems, leave the original responses unchanged and recheck those same originals.

### 5. Read the automated gates

| Check | Passing criterion |
| --- | --- |
| Completeness | Every ID in the requested split; 0 duplicates or omissions; matches the original query |
| Retrieval | Actual server-side retrieval before the model call; original sections/hashes match |
| Citations | Nonempty actual sources selected by the model, satisfying required evidence |
| Business tools | Correct functions, arguments, and actual results; draft and not-ordered states preserved |
| Native judge | At least 4 on the fixed 1–5 scale; no contradiction between score and passed |
| Overall quality | At least 90% of cases satisfy both the automated checks above and native judgments |
| safety/access | 0 failures |
| Calibration | All 8 controls agree with their expected judgments |

Evaluator errors or omissions mean failure even if the service returns `completed`.
A score of 9/10 does not pass the gate if a safety case failed.
`manual_pass` is not an input to this automated gate, and `human_review_completed=false` remains unchanged.

## Success criteria

Real responses, tool results, and citations are linked to native judgments, and you have recorded dev results separately from sealed-holdout results.
Human review is not a completion requirement. Before future production use, a business owner's sample review is recommended.
The historical v1 9/10 failure is available in the [original v1 records at the pre-cleanup commit](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/tree/faa5ec26f15cfeb38f69de4036acedc3151c3df4/validation/history/v1). Earlier records have been removed from the current file list, but their historical judgments are unchanged.

The new v2 exam exposed omissions in compound questions and evidence-selection problems, so its original failures were preserved and the cases moved to v3 dev.
For one development case refusing to use a real contract, the original source text was checked to confirm that either SEC1 or PROC5 validly supports the same claim.
Only for that claim, v3 records an explicit alternative-evidence group; the SEC2 permission requirement, PROC2 laptop limit, and original expected behavior remain unchanged.
This does not change the answer or automatically insert sources. The original strict v2 judgments and the first v3 dev draft are also preserved.

## Troubleshooting

Distinguish missing retrieval results, JSON/citation contract errors, business-check failures, and native judge errors.
If an evaluator returns `score` and `passed` as different items, use only a consistent pair from the same evaluator.
Do not discard errors and average only successful rows. `--suite legacy-v1` reproduces the original behavior; it is not new completion evidence.

## Cleanup

Check Hosted compute and evaluation-job status. Keep raw results/environment records in `results/`,
and share only reviewed, minimal synthetic evidence in `validation/automated-v3/`.
Actual ordering, payment, and business-approval capabilities remain out of use.
