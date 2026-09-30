> **What you will build:** Connect checks, evaluation, approval, and rollback so that a code change does not immediately become a production change.

## Objectives

Manage not only code, but also **model, agent, tool, knowledge, evaluator, and dataset versions** together.

## Concepts and lab map

**What you will try:** Local CI, an explicitly authorized paid validation workflow, OIDC authentication, release/rollback, and cost management.

**What is it, and why does it matter?** CI repeats checks when changes occur; CD deploys a validated version. An agent's behavior can change when models, documents, or tools change even if its code stays the same, so you must record the full release bundle. OIDC lets CI authenticate with an execution-bound identity instead of a long-lived client secret, but managing that identity's permissions is a separate responsibility.

**How do you use it?** First pass local contract checks, then run dev validation in an approved nonproduction environment. Select the release path only after freezing configuration, data, and criteria. Preserve failed runs unchanged and define when to return to the previous approved version. Do not reuse the author's results as pass evidence for a new learner environment.

**Where do you run it?** [validate.yml](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/blob/main/.github/workflows/validate.yml) provides the default checks; [azure-validation.yml](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/blob/main/.github/workflows/azure-validation.yml) provides separately approved execution; and [ci_live.py](../../scripts/ci_live.py) checks target and quality boundaries. Inspect the execution branch, inputs, and results in GitHub Actions, and compare the actual deployed version in the Foundry portal.

## Prerequisites

You need L08's evaluation gates, the Hosted project from L14 or a version-controlled Prompt agent, and separation between nonproduction and production. OIDC federation and role assignment for real CI/CD are administrator tasks.

## Steps

### 1. Define the release path

```text
Propose a change
 → Local contract tests
 → Nonproduction deployment
 → Smoke test
 → Representative-data evaluation + permission/safety checks
 → Human approval
 → Switch the production active version
 → Monitor
 → Restore the previous approved version on failure
```

Checking that a response file is nonempty is only a smoke test. **A file containing error logs may also be nonempty.** Check actual response status, output schema, and expected behavior.

### 2. Reproduce the kit's local checks

```bash
python -m unittest discover -s tests -v
python samples/workshop.py validate-data
python samples/evaluation_lab.py prepare --suite automated-v3 --split dev --input results/실제-dev-responses.jsonl
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `unittest discover -s tests -v` | Discovers tests in `tests/` and prints each test's name and result. | Local code contract checks. No Azure inference or deployment. |
| 2. `workshop.py validate-data` | Checks synthetic data structure, IDs, and the default split. | A local check, not a command for calculating the accuracy of model answers. |
| 3. `evaluation_lab.py prepare ...` | Reads the 30 actual v3 dev responses from `--input` and checks the specified suite/split and evidence contract. Replace `실제-dev-responses.jsonl` with the actual dev response filename. | Local validation. If the file does not exist, do not fill it with dummy data; first perform the approved actual-response collection step. |

</div>

Run the last command when you have 30 actual v3 dev responses. Do not substitute dummy responses or manually entered verdicts for the automated gates.

This directory's `.github/workflows/validate.yml` checks only documentation and local tests by default. **It does not automatically run Azure deployment or paid inference.**

### 3. Conditional: Connect Hosted CI/CD

The bundled `.github/workflows/azure-validation.yml` is **only for manual dispatch / explicit reusable-workflow calls**.
Ordinary pushes and PRs have no paid Azure jobs. Deployment occurs only for runs that pass
`acknowledge_cost=true` and approval in the `contoso-validation` GitHub Environment.
The existing `.github/workflows/validate.yml` continues automatic local validation.

The administrator grants minimum roles to the workload identity in the new test RG
and restricts the federated credential subject to **A's environment-bound `sub` actually issued by Actions**.
Recent formats may include the owner's/repository's immutable IDs as `@ID` after their names.
Do not assume the old `repo:owner/repo:environment:name` string is still the exact format.
The audience is `api://AzureADTokenExchange`. Do not create a client secret.
The identity receives project-level Foundry User and only the required deployment/read permissions; CI does not expand its own RBAC.

The administrator command is `python scripts/setup_oidc.py --branch 실제-feature-branch --subject "확인한-sub-claim" --live`.
`--branch` selects the permitted GitHub working branch; replace `실제-feature-branch` with that branch. `--subject` is the complete, actually issued, non-secret OIDC `sub` claim; replace `확인한-sub-claim` with that value. `--live` authorizes real identity, federation, and GitHub Environment configuration. Read [setup_oidc.py](../../scripts/setup_oidc.py) first and ask the administrator to perform it. This is not a simple login command; approval for paid calls does not also authorize access changes.
Record the new RG's user-assigned identity, environment-bound federated credential,
new GitHub Environment, and its branch policy together.
An existing environment/identity causes a conflict and stops the setup; no tenant-wide application permissions are granted.
For AADSTS700213, compare issuer, audience, and subject with the non-secret claims in the logs.
`--repair-subject` corrects only the FIC in this receipt; it does not change GitHub-wide OIDC policy.

Environment variables are the client/tenant/subscription/project IDs and model/Search endpoint/index/KB
listed in the workflow's `env`. Register only non-secret configuration values. Do not upload authentication tokens,
the entire `.env`, or raw execution results as artifacts.

```bash
gh workflow run validate.yml --ref 승인된-작업브랜치 -f acknowledge_cost=true -f validation_phase=dev
# Only after dev passes and code, data, and criteria are frozen:
gh workflow run validate.yml --ref 같은-동결브랜치 -f acknowledge_cost=true -f validation_phase=release
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Check the dev results and freeze settings between these two runs.

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `gh workflow run ... validation_phase=dev` | `gh` is the GitHub CLI; `--ref` is the approved execution branch. Replace `승인된-작업브랜치` with that branch. `-f` passes workflow inputs, and `acknowledge_cost=true` explicitly selects the paid path. | Requests a real Actions run. After environment approval, nonproduction deployment, 30 dev cases, 8 judge controls, and related work incur charges; the holdout is not invoked. |
| 2. `gh workflow run ... validation_phase=release` | Requests final release validation with the same frozen branch and successful dev evidence. Replace `같은-동결브랜치` with that same branch. The comment line is not an executable command. | Real evaluation charges may apply. Collects the sealed holdout or evaluates preserved originals under the original conditions; if preparation differs, it stops before the holdout. |

</div>

`validate.yml` is the manual entry point already present on the default branch. The same file on the approved working branch
calls the reusable Azure workflow after completing local checks, so the new workflow does not need to be merged into main first.
If GitHub policy blocks a manual branch run, record it as blocked; do not merge main without authorization.
`scripts/ci_live.py` checks the OIDC principal and RG/project match, deploys Hosted, and verifies
**a KRW 2.9 million draft, both approval roles, and no order placed** through actual tool results.
The dev phase runs only the current v3's 30 regressions and 8 judge controls; it neither passes holdout questions to the model nor invokes them.
Download and preserve the successful dev run's `contoso-ci-summary` artifact in `validation/automated-v3/`,
then run release with the same runtime, model, and suite hashes. If successful dev evidence is missing or the code has changed,
release stops before opening the holdout.
The release phase either collects the new sealed holdout for the first time or evaluates preserved originals from the same environment/code.
Human review is not a completion requirement of this educational automated gate; it is recorded only as guidance.
Holdout evidence is usable only if its environment fingerprint, runtime hash, and actual model match the current test environment.
You cannot reuse the author's results from another environment as quality evidence for your own CI.
Independent holdout evidence may still be collected after calibration failure, but **the release gate fails**.
Smoke success is separate from the full holdout quality gate. The `always()` step stops only recorded sessions.
Raw evidence stays in `results/`; shareable v3 results are separated into `validation/automated-v3/ci-dev.json`,
`ci-release.json`, and synthetic response files. Earlier v1 CI/failure records remain unchanged in the [pre-cleanup Git commit](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/tree/faa5ec26f15cfeb38f69de4036acedc3151c3df4/validation/history/v1).

For operational diagnostics, `validation_phase=optimizer` runs a bounded comparison under the same OIDC principal,
targeting only the pinned previous Responses version and dev data. It is separate from new holdout collection and quality release,
and it does not automatically apply or promote candidates.

### 4. Check model upgrades and knowledge changes

| Change | Recheck alongside it |
| --- | --- |
| Model version/auto-update | Response format, tool selection, latency, and cost |
| Model router pool/subset | Allowed models, quality, fallback, and context |
| Knowledge documents/index | Accuracy, citations, deletion, permissions, and freshness |
| Tool schema/endpoint | Call arguments, authentication, errors, and duplicate actions |
| Instructions/skills | Regressions and safety boundaries |
| Evaluator/judge | Score meaning and consistency of judgments |

Monitor model retirement notices and allow enough time to compare replacement models. Even for the same agent version, changes to a router pool or external data can change behavior.

### 5. Build a cost worksheet

![The actual Prompt Agent Monitor screen. It shows a time-range filter, Estimated cost, Total token usage, execution/token charts, and a separate evaluation configuration card.](../../assets/portal/07-monitor.png)

**Read the screen:** Under **Build → Agents → your agent → Monitor**, select the time range first, then consider execution count, tokens, and estimated cost together. **Configure / Set up insights** can start new observation/evaluation configuration, so do not select it for this read-only exercise. The image's values are observations for the selected existing agent/time range, not the total RG bill or the cost of this documentation revision. Reconcile actual billing separately with Cost Management.

Approximate inference cost:

```text
Input tokens / 1,000,000 × input unit price
+ Output tokens / 1,000,000 × output unit price
+ Evaluation judges, search, tools, voice/video, logs, and hosted runtime
+ Fixed capacity, reservations, and storage costs
```

Use the price list applicable to your region, currency, contract, and model at execution time. Also check billing rules for cache discounts, reasoning tokens, routers, Batch, and similar features. This guide does not guarantee a fixed “exactly this many dollars per learner” cost.

### 6. Practice failure response

Simulate tool timeouts, 429 responses, incorrect connections, and a single-backend outage in a nonproduction environment. Record how stopping, retrying, fallback, and human handoff should work.

Use bounded retries with backoff/Retry-After, and do not blindly retry non-idempotent operations. Multi-region recovery must not send data to prohibited regions. Set RTO/RPO as organizational goals and measure them through real drills.

## Success criteria

You have a release-version bundle, evaluation criteria, an approver, a rollback target, a cost owner, and an incident-response path. Distinguish CI success from passing business quality checks.

## Troubleshooting

If something works in development but not in CI, check the OIDC subject, environment, identity roles, network access, and SDK/CLI version differences. Do not print tokens or full environment values in logs.

## Cleanup

Work with the responsible owners to clean up unnecessary staging deployments, continuous evaluations, temporary federated credentials, and permissions.
