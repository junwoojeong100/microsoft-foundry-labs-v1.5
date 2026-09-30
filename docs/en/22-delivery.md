> **What you will build:** Connect checks, evaluation, approval, and rollback so that a code change does not immediately become a production change.

## Objectives

Manage not only code, but also **model, agent, tool, knowledge, evaluator, and dataset versions** together.

## Concepts and lab map

**What you will try:** Local CI, an explicitly authorized paid validation workflow, OIDC authentication, release/rollback, and cost management.

**What is it, and why does it matter?** CI repeats checks when changes occur; CD deploys a validated version. An agent's behavior can change when models, documents, or tools change even if its code stays the same, so you must record the full release bundle. OIDC lets CI authenticate with an execution-bound identity instead of a long-lived client secret, but managing that identity's permissions is a separate responsibility.

**How do you use it?** First pass local contract checks, then run dev validation in an approved nonproduction environment. Select the release path only after freezing configuration, data, and criteria. Preserve failed runs unchanged and define when to return to the previous approved version. Do not reuse the author's results as pass evidence for a new learner environment.

**Where do you run it?** The checked-out [validate.yml](../../.github/workflows/validate.yml) provides the default checks; [azure-validation.yml](../../.github/workflows/azure-validation.yml) provides separately approved execution; and [ci_live.py](../../scripts/ci_live.py) checks target and quality boundaries. Inspect the reviewed execution branch, language input, environment, and results in GitHub Actions, and compare the actual English deployment in the Foundry portal. Existing `main` workflows remain unchanged until reviewed changes are approved.

## Prerequisites

You need L08's evaluation gates, the English Hosted project from L14 or a version-controlled Prompt agent, and separation between nonproduction and production. Keep L01's English profile and isolated checkout selected locally. OIDC federation and role assignment for real CI/CD are administrator tasks; paid-run approval alone does not authorize identity changes.

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
FOUNDRY_LAB_LANGUAGE=ko python -m unittest discover -s tests -v
python samples/workshop.py validate-data
python samples/evaluation_lab.py prepare --suite automated-v3 --split dev --input results/actual-dev-responses.jsonl
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `FOUNDRY_LAB_LANGUAGE=ko python -m unittest discover -s tests -v` | Sets `ko` for this test process only. The shared suite preserves Korean-baseline assertions and includes explicit English-profile tests; `-v` prints each test's name and result. | Local code contract checks, with no Azure inference or deployment. The terminal's exported `en` selection and live environment remain unchanged. |
| 2. `workshop.py validate-data` | Checks synthetic data structure, IDs, and the default split. | A local check, not a command for calculating the accuracy of model answers. |
| 3. `evaluation_lab.py prepare ...` | Reads the 30 actual English v3 dev responses from `--input` and checks the specified suite/split and evidence contract. Replace `actual-dev-responses.jsonl` with the actual dev response filename. | Local validation. If the file does not exist, do not fill it with dummy data; first perform the approved actual-response collection step. |

</div>

Run the last command when you have 30 actual v3 dev responses. Do not substitute dummy responses or manually entered verdicts for the automated gates.
CI uses the same test-process-only override. Do not globally unset or switch the English profile: the following `validate-data`, evaluation, and live commands still run with `FOUNDRY_LAB_LANGUAGE=en` and the separate English configuration and receipts.

This directory's `.github/workflows/validate.yml` checks only documentation and local tests by default. **It does not automatically run Azure deployment or paid inference.**

### 3. Conditional: Connect Hosted CI/CD

The bundled `.github/workflows/azure-validation.yml` is **only for manual dispatch / explicit reusable-workflow calls**.
Ordinary pushes and PRs have no paid Azure jobs. Deployment occurs only for runs that pass
`acknowledge_cost=true`, the explicit `language=en` input, and approval in the **`contoso-validation-en` GitHub Environment**.
The existing `.github/workflows/validate.yml` continues automatic local validation.

Before setup or dispatch, confirm that you are using the **reviewed `docs/english-live-validation` branch**, `contoso-validation-en`, and the separate English project and receipts. Read [setup_oidc.py](../../scripts/setup_oidc.py) first. Bootstrap in two phases: observe the exact environment-bound identity metadata **before** creating Azure federation, then configure only the owned identity and scoped permissions. Do not omit `language=en`, switch to the Korean environment, or merge `main` as a workaround.

**Preserve existing repository visibility**, whether public or private, and leave existing non-English environments unchanged. Setup is allowed only on an explicitly approved non-`main` feature/docs branch, never on `main` or `master`. Approval for paid calls does not also authorize identity or access changes.

**Bootstrap phase 1: Prepare the GitHub environment, then observe its issued subject.**

After branch and environment-creation approval, the administrator runs:

```bash
FOUNDRY_LAB_LANGUAGE=en python scripts/setup_oidc.py --branch docs/english-live-validation --prepare-environment --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Prepare GitHub configuration only.

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `setup_oidc.py --prepare-environment --live` | The environment prefix selects English for this command. `--branch` restricts the new `contoso-validation-en` environment to the explicitly approved branch; `--prepare-environment` stops before Azure identity setup. | Creates only the new branch-restricted GitHub Environment and its ownership record. No Azure identity, federation, or client secret is created; existing non-English environments and repository visibility are unchanged. |

</div>

Next, dispatch the identity-only probe from that same branch:

```bash
gh workflow run azure-validation.yml --ref docs/english-live-validation -f language=en -f acknowledge_cost=true -f validation_phase=identity
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Observe identity metadata before federation.

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `gh workflow run ... validation_phase=identity` | `--ref` selects the approved branch, `language=en` selects `contoso-validation-en`, and `validation_phase=identity` selects the identity-only probe. `acknowledge_cost=true` is the required workflow opt-in, not a request for paid Azure execution in this phase. | Runs GitHub Actions and prints only nonsecret OIDC `sub`, `aud`, repository, and ref metadata. Makes **zero Azure calls**: no Azure login, deployment, inference, or evaluation. It does not print the raw token or create federation. |

</div>

The existing `validate.yml` entry point can also dispatch this probe with the same `--ref` and inputs. Inspect the actual Actions output and retain only the nonsecret metadata. Verify the repository, approved ref, English environment-bound `sub`, and audience `api://AzureADTokenExchange`. A successful identity probe is not Azure authentication or quality-pass evidence.

Recent subject formats may include the owner's/repository's immutable IDs as `@ID` after their names. Do not assume the old `repo:owner/repo:environment:name` string is still exact, and never construct a guessed subject.

**Bootstrap phase 2: Configure the owned Azure identity using that exact observed subject.**

Only after the administrator has reviewed the probe and approved the scoped identity changes:

```bash
FOUNDRY_LAB_LANGUAGE=en python scripts/setup_oidc.py --branch docs/english-live-validation --subject "OBSERVED_ENVIRONMENT_BOUND_SUBJECT" --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Administrator-only federation and scoped access changes.

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `setup_oidc.py --subject ... --live` | Replace `OBSERVED_ENVIRONMENT_BOUND_SUBJECT` with the complete, exact `sub` printed by the English identity probe. Keep the same approved `--branch` and English ownership receipt. `--live` permits the reviewed Azure identity/federation and access changes. | Creates the owned resource group's identity, environment-bound federation, scoped roles, and nonsecret GitHub configuration variables. Creates no client secret and does not change repository visibility or unrelated environments. |

</div>

The identity receives project-level Foundry User and only the required deployment/read permissions; CI does not expand its own RBAC.
Record the new RG's user-assigned identity, environment-bound federated credential,
new GitHub Environment, and its branch policy together.
The matching environment recorded during preparation is used for phase 2; an unrelated existing environment or identity is not overwritten. No tenant-wide application permissions are granted.
For AADSTS700213, compare issuer, audience, and subject with the non-secret claims in the logs.
`--repair-subject` corrects only the FIC in this receipt; it does not change GitHub-wide OIDC policy.

Environment variables are the client/tenant/subscription/project IDs and model/Search endpoint/index/KB
listed in the workflow's `env`. Register only non-secret configuration values. Do not upload authentication tokens,
the entire `.env`, or raw execution results as artifacts.

The optional English `optimizer` CI phase also requires `FOUNDRY_OPTIMIZER_AGENT_VERSION` in this English environment, pinned to the reviewed Responses baseline. If it is unset or invalid, the job stops rather than guessing a version. The recorded English Optimizer experiment was run separately through the bounded CLI path; an OIDC optimizer run is not claimed.

After bootstrap succeeds, the separately approved **dev and release phases** use the English environment and can incur Azure charges:

```bash
gh workflow run validate.yml --ref docs/english-live-validation -f language=en -f acknowledge_cost=true -f validation_phase=dev
# Only after dev passes and code, data, and criteria are frozen:
gh workflow run validate.yml --ref docs/english-live-validation -f language=en -f acknowledge_cost=true -f validation_phase=release
```

<div class="command-explanation" markdown="1">

**Command walkthrough** — Check the dev results and freeze settings between these two runs.

| # / Command | What it does and options | Result / cost or changes |
| --- | --- | --- |
| 1. `gh workflow run ... validation_phase=dev` | `gh` is the GitHub CLI; `--ref docs/english-live-validation` selects the explicitly approved branch. `-f language=en` selects the English profile and `contoso-validation-en`; `acknowledge_cost=true` explicitly selects the paid path. | Requests a real Actions run. After English-environment approval, nonproduction deployment, 30 English dev cases, 8 judge controls, and related work incur charges; the holdout is not invoked. |
| 2. `gh workflow run ... validation_phase=release` | Requests final English release validation from the same frozen branch, with `language=en` and successful English dev evidence. The comment line is not an executable command. | Real evaluation charges may apply. Collects the new independent sealed English holdout or evaluates preserved English originals under the original conditions; if preparation differs, it stops before the holdout. |

</div>

`validate.yml` is the manual entry point already present on the default branch. Its reviewed English-capable version on `docs/english-live-validation`
calls the reusable Azure workflow after completing local checks. Do not dispatch the unchanged default-branch runtime workflow as an English run, and do not merge into `main` merely to enable dispatch.
If GitHub policy blocks a manual branch run, record it as blocked; do not merge main without authorization.
`scripts/ci_live.py` checks the OIDC principal and RG/project match, deploys Hosted, and verifies
**a KRW 2.9 million draft, both approval roles, and no order placed** through actual tool results.
The English dev phase runs only v3's 30 English regressions and 8 judge controls; it neither passes holdout questions to the model nor invokes them.
After a successful dev run exists, download and preserve its `contoso-ci-summary` artifact in `validation/english/automated-v3/`,
then run release with the same runtime, model, and suite hashes. If successful dev evidence is missing or the code has changed,
release stops before opening the holdout.
The release phase either collects the new independent sealed 10-case English holdout for the first time or evaluates preserved English originals from the same environment/code.
Human review is not a completion requirement of this educational automated gate; it is recorded only as guidance.
Holdout evidence is usable only if its environment fingerprint, runtime hash, and actual model match the current test environment.
You cannot reuse the author's results from another environment as quality evidence for your own CI.
Independent holdout evidence may still be collected after calibration failure, but **the release gate fails**.
Smoke success is separate from the full holdout quality gate. The `always()` step stops only recorded sessions.
Raw English evidence stays in the isolated checkout's `results/`; shareable v3 summaries and reviewed synthetic response files belong under `validation/english/automated-v3/`. The completed English Hosted Invocations version 2 dev result was **29/30**, with **8/8** calibration controls and **0 critical dev failures**. The independent holdout executed **10/10** but passed **7/10**, including a critical safety citation-evidence failure: **release was not approved**. See [quality.json](../../validation/english/automated-v3/quality.json) and [ci-release.json](../../validation/english/automated-v3/ci-release.json). Preserve the immutable [first partial attempt](../../validation/english/attempts/36716203574/ci-dev.json) separately. No thresholds, data, or tested candidate were adjusted and no holdout rerun followed the result; do not redispatch the release collection to seek a passing score.
Existing `validation/automated-v3/` and `validation/current/` remain historical Korean evidence. Earlier Korean v1 CI/failure records remain unchanged in the [pre-cleanup Git commit](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/tree/faa5ec26f15cfeb38f69de4036acedc3151c3df4/validation/history/v1).

For optional operational diagnostics, `validation_phase=optimizer` must use the same approved English OIDC principal,
an explicitly pinned English Responses version, matching English instructions, and dev data only. Verify these bindings before selecting the phase. It is separate from new holdout collection and quality release, and it does not automatically apply or promote candidates.

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

![Prompt Agent Monitor in contoso-workshop-en. Inspect the selected English agent's time range, tokens, estimated cost, and monitoring configuration.](../../assets/portal/en/07-monitor.png)

**Read the screen:** Under **Build → Agents → your agent → Monitor**, select the time range first, then consider execution count, tokens, and estimated cost together. **Configure / Set up insights** can start new observation/evaluation configuration, so do not select it for this read-only exercise. Image values, if present, apply only to the selected English agent/time range recorded in the [English capture log](../../content/portal-screenshots.en.json), not the total RG bill or a quality pass. Reconcile actual billing separately with Cost Management.

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
