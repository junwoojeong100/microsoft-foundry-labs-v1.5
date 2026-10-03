> **What you will build:** A CI interpretation record, agent release manifest, rollback decision table, and model/cost checklist. Design these without deploying, and distinguish plans from execution evidence.

<div class="lab-brief" markdown="1">

**Format:** Advanced elective · local CI failure→repair and release/recovery design by default.

**Start here:** Copy the synthetic candidate-selection exercise in 2-1 and reproduce three failures. Also distinguish the real workflow's approval conditions.

**What to check:** Keep a CI interpretation, release manifest, rollback decision, and cost owner. This chapter does not require a Hosted deployment.

</div>

## Objectives

**Passing source checks, deploying to Azure, and being ready for users are different decisions.** Separate them and decide which failures should block promotion or trigger a return to an approved version.

## Concepts and lab map

**What you will try:** Prevent a failing candidate from shipping and plan recovery.

**What is it, and why does it matter?** CI automatically checks changes; CD deploys reviewed changes. Rollback returns to a previously approved version. Completed execution is not a quality pass.

**How do you use it?** Reproduce three failures and repair the candidate-selection conditions. Use existing results to write a release manifest and rollback decision. No new Hosted deployment is required.

**Where do you run it?** Work on your PC. Read **`.github/workflows/` in your supplied sources** to distinguish [local checks](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/blob/6fddd4642be0d0ac9dfee9b9b51e7b00b5cf1cde/.github/workflows/validate.yml) from [separately approved execution](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/blob/6fddd4642be0d0ac9dfee9b9b51e7b00b5cf1cde/.github/workflows/azure-validation.yml).

## Prerequisites

Use L01's environment and repository sources. **Search, Hosted, and Optimizer are not prerequisites for the default exercise.** Use L11/L14 results for a real manifest; without them, complete it as a design. Do not change the educational v1/v2 or historical evidence.

## Steps

### 1. Read what runs automatically

Open `validate.yml` in an editor and locate `on`, `jobs`, `needs`, and `if`. Compare the table with the actual YAML.

| What to inspect | How to judge it | Next action on failure |
| --- | --- | --- |
| `push` / `pull_request` → `offline`, `sdk` | Document/data/code and SDK contract checks, not Azure deployment | Read the failed job's **first error and command**, not just its final “failed” message |
| `azure` with `needs: [offline, sdk]` | Both prerequisite checks must pass before the paid path can run | Do not call a failed/skipped job a successful deployment |
| `workflow_dispatch`, `acknowledge_cost`, `repository_id` | Explicit opt-in and this repository's identity; forks do not inherit access | Keep the default false; do not remove repository or approval conditions for the exercise |
| `environment`, `id-token: write` in `azure-validation.yml` | OIDC authenticates a workflow identity; Azure roles and environment approval remain separate | Escalate branch/environment/tenant/project mismatches; do not substitute a long-lived secret |

If GitHub is available, open **Actions → run → job → failed step** and locate the same items. Otherwise inspect sources and record “workflow execution unverified.” The default exercise requires neither a new push nor a paid workflow dispatch.

### 2. Check the same sources locally

The repository-wide checks below are a reference. Start with **2-1's failure→repair exercise** to experience what CI blocks without deliberately breaking existing business code or evaluation criteria.

The first line is needed only if documentation dependencies are missing. L01's base dependencies must already be installed.

```bash
python -m pip install -r requirements-docs.txt
python scripts/build_guide.py
FOUNDRY_LAB_LANGUAGE=ko python -m unittest discover -s tests -q
python scripts/check_guide.py
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `pip install -r requirements-docs.txt` | Prepare the declared Markdown dependency in the current virtual environment; skip if present. | Package download/local installation; no Azure calls. |
| 2. `build_guide.py` | Generate both HTML/Markdown editions from sources and metadata. | Local file changes; do not edit generated output manually. |
| 3. `FOUNDRY_LAB_LANGUAGE=ko ... unittest ... -q` | Run shared Korean-baseline tests and explicit English checks. | Local contracts, not Azure or model quality. |
| 4. `check_guide.py` | Check 25 modules, command explanations, links, and capture provenance. | Record current documentation checks only in `validation/docs/`. |

</div>

Record success as **code/document checks passed** only. For import errors, inspect the virtual environment/requirements; for generated drift, inspect `docs/` and `content/`; for business assertions, inspect the relevant function/policy contract. Do not weaken assertions or evaluation criteria.

For PDF/ZIP delivery, continue with the README build path. Artifacts under `downloads/` and the root web entry points are **separate from agent deployment artifacts**. Documentation generation supports this chapter; it is not CD evidence.

### 2-1. Fix it: completion alone must not promote a candidate

<div class="practice-block" markdown="1">

**Try it:** This pure function returns fictional version names. It changes no actual endpoint or Active version.

```bash
python samples/prepare_practice.py delivery --output practice/delivery
python -m unittest discover -s practice/delivery -p "test_exercise.py" -v
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `prepare_practice.py delivery` | Copies a flawed function, tests, and an optional workflow template into a new folder. | Local files only; no GitHub push or Azure deployment. |
| 2. `unittest discover` | Separates a good candidate, failed run, quality failure, critical failure, and missing row. | Initially **three of five tests fail intentionally**. Do not hide these failures. |

</div>

`practice/delivery/exercise.py` chooses `candidate-2` from `status=completed` alone. A completed run with a quality failure, safety failure, or missing row must keep `approved-1`.

**Change one thing:** Make candidate selection an AND of four conditions: completed status, `quality_passed is True`, zero critical failures, and zero missing rows. Change neither tests nor the original release gates. Rerun the same check and require five passes.

<details markdown="1">
<summary>Example repair — a local decision exercise, not the complete production gate</summary>

<!-- solution:delivery -->
```python
def choose_version(previous: str, candidate: str, checks: dict) -> str:
    if (
        checks["status"] == "completed"
        and checks["quality_passed"] is True
        and checks["critical_failures"] == 0
        and checks["missing_rows"] == 0
    ):
        return candidate
    return previous
```

</details>

**Explain the result:** Describe the incorrect promotion prevented by each of the three failed tests. Complete a `previous version / candidate / failure evidence / version to keep` table. This function performs neither deployment nor state migration, so do not call it completed remote rollback.

**Optional: observe the same failure→repair in GitHub.** Use only a new branch in an approved personal training repository. Copy the supplied `workflow.yml` to `.github/workflows/contoso-practice.yml` and include the code/tests under `practice/delivery`. Run **Actions → Contoso local delivery practice → Run workflow** on the flawed commit, then on a commit changing only `exercise.py`; expect failure then success. The template has manual dispatch, read-only permissions, and Python checks—no Azure sign-in, secrets, or deployment. Do not replace this repository's existing `validate.yml` or enable `acknowledge_cost`.

</div>

### 3. Write an agent release manifest

This is a **Contoso worksheet example**. Where actual identifiers/results are absent, write “not executed”; do not copy historical results as evidence for the current candidate.

| Manifest item | What to connect | If missing or different |
| --- | --- | --- |
| Sources | Your commit, changed files, actual v2 instruction hash | Hold promotion if the evaluated sources cannot be distinguished from the candidate |
| Execution target | Language/project, model ID/version/deployment name | A different model version is a different candidate even under the same deployment name |
| Agent | Name, service-issued numeric version, Prompt/Hosted kind and protocol | Instruction v2 does not imply service version 2 |
| Data/tools | Policy/schema/dependency hashes and connection targets | Do not hide retrieval/function changes inside an instruction change |
| Evidence | Same-target response/trace, actual tool results, applied evaluation and failures/missing rows | L08's 12 tool-free questions do not approve an integrated business release |
| Recovery | Previous approved version/configuration bundle, owner, data compatibility | Hold deployment without a viable target and compatible state |

For L11's purchasing task, connect **stock 8, unit price KRW 1,450,000, total KRW 2,900,000, two approval roles, and not ordered** to actual tool/evidence records. L14 Hosted also requires package/runtime contract comparison. Using instruction v2 does not establish newly validated Hosted code; read the scope in [current status](../../validation/current/instructions.json).

### 4. Rehearse a rollback decision

**Synthetic teaching scenario:** An approved version exists, and a candidate describes a purchase draft as “order completed.” This is not an actual deployment record.

| Step | Decision/action | Evidence to inspect |
| --- | --- | --- |
| Detect | Block promotion; stop expansion if a limited trial is underway | Failed input/response, candidate version, actual tool record |
| Isolate | If the function says not ordered but the answer says otherwise, inspect synthesis/instructions first | Difference between function JSON and final answer |
| Prepare recovery | Select the previous approved agent version with its model/connections/settings | Version availability and current data/schema compatibility |
| Approved recovery | Restore L11's Active version or the Hosted consumer's **version binding** | Actual invoked version, not just an unchanged endpoint name |
| Verify recovery | Within separate approval, repeat the same purchase question and check evidence/tools/not-ordered state | New response/trace and results; old success logs are insufficient |

The default exercise stops at identifying what to restore. Actual switching and reinvocation require separate approval. An incompatible data migration is not undone by restoring the agent version alone. Preserve failed originals and earlier versions.

### 5. Respond to model lifecycle and costs

![Operate monitoring. Distinguish requests, errors, and usage from actual quality judgments.](../../assets/portal/en/07-monitor.png)

| Signal/observation | Judgment | Next action |
| --- | --- | --- |
| L02 deployment's version, automatic-update policy, retirement date | The same deployment name can conceal changed behavior conditions | Assign an owner and a pre-retirement comparison date; record existing version/context/criteria |
| Replacement model candidate | Responses, tools, output schema, region, and processing location must fit | Separately approve a same-dev-input comparison; never reuse a sealed holdout arbitrarily or relax gates |
| 429 or increased latency | Separate quota/concurrency/token volume from an outage | Reduce calls and plan bounded recovery; no fallback to unapproved models/regions |
| Costs rise without requests | Inspect Search/storage/logs/Hosted sessions separately | Use L12's per-resource stop/retention owners and next-check time; empty billing rows are not zero cost |

Record **RTO (target service recovery time)** and **RPO (acceptable data-loss interval)** in the recovery design. For example, “restore read-only policy guidance within 30 minutes; allow no loss of approval records” is an **example requirement**, not a measured guarantee or a capability of this kit. Without an owner, recovery path, and rehearsal results, do not claim it was achieved.

## Success criteria

Reproduce the three local failures, repair only the function, and obtain five passes. If you use GitHub, distinguish failed/passing runs from their different commits.
Retain a **CI interpretation record, release manifest, failure/rollback decision, and model/cost follow-up owner**. Distinguish local pass, design complete, and Azure not executed. Hold promotion without quality evidence for the same candidate.

## Troubleshooting

If `azure` is skipped, read its opt-in condition; skipping on an ordinary push is not an error. If a workflow is green but the answer is wrong, check what actually ran. For deployment/rollback failures, inspect agent version, protocol, runtime identity, and model/connections in order rather than blindly redeploying.

## Cleanup

Exclude private settings, raw responses, and receipts from the kit. Generate HTML/Markdown/PDF/ZIP from the same sources. Main merges, Pages publication, paid runs, access changes, and Azure deletion each require separate approval; this exercise performs none automatically.
