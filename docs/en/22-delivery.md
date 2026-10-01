> **What you will build:** A reproducible learning kit and a safe process for changing and delivering its sources.

## Objectives

Keep the guide understandable as **baseline v1, improved v2, and one latest result set**.
Publishing documentation is not an agent quality release; each edit does not require paid validation or another experiment number.

## Concepts and lab map

**What you will try:** Local CI, GitHub Actions, OIDC's purpose, deployment/rollback, and cost/resource lifecycle boundaries.

**What is it, and why does it matter?** CI checks documents, data, and code against the same sources.
A green CI check does not establish Azure execution or better model quality.

**How do you use it?** Improve the v2 file and explain L08's single comparison.
Keep only the latest originals in the current file tree; preserve previous failures, questions, and criteria in Git history.

**Where do you run it?** The reviewed [validate.yml](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/blob/6fddd4642be0d0ac9dfee9b9b51e7b00b5cf1cde/.github/workflows/validate.yml) demonstrates default checks;
[azure-validation.yml](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/blob/6fddd4642be0d0ac9dfee9b9b51e7b00b5cf1cde/.github/workflows/azure-validation.yml) demonstrates separately approved execution.
Inspect the current kit's sources locally. The short learning path uses terminal and GitHub Actions **offline/SDK checks**.

## Prerequisites

Use L01's environment and this repository's sources. Do not package `.env`, tokens, `.azure/`, `results/`, or virtual environments.
Both languages use the same implementation with their own synthetic corpus and instructions.

## Steps

### 1. Build the guide from source

```bash
python scripts/build_guide.py
FOUNDRY_LAB_LANGUAGE=ko python -m unittest discover -s tests -q
python scripts/check_guide.py
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `build_guide.py` | Generate both HTML/Markdown editions from module sources and metadata. | Local files only; do not hand-edit generated output. |
| 2. `FOUNDRY_LAB_LANGUAGE=ko ... unittest ... -q` | Run shared Korean-baseline tests and their explicit English checks. `-q` requests concise output. | Local checks, not a new Azure pass or measured score increase. |
| 3. `check_guide.py` | Check all 25 modules, explained commands, links, and capture provenance. | Keep current documentation checks in `validation/docs/` only. |

</div>

Generate PDFs and the ZIP from the same sources using the README commands. The [current status](../../validation/current/instructions.json)
records the actual bilingual GPT-6 Sol measurement, tied scores, and preserved output-contract failure separately.
Generated Markdown, PDF, and ZIP files are grouped under the root `downloads/` directory. Keep `index.html` and `index.ko.html` at the root for the existing Pages routes.

### 2. Read GitHub Actions checks

Push/PR workflows run offline/SDK checks by default. Do not dispatch paid Azure jobs without explicit opt-in.
Main merges and Pages publication also require approval. Publication cannot turn a failed quality judgment into a pass.

Review OIDC only when needed. It authenticates a workflow identity instead of storing a long-lived secret.
Check `repository_id`, branch/environment, tenant/subscription/project, and least-privilege roles; do not reuse another person's environment or access.
This learning comparison does not require creating an identity, role, or Environment policy.

### 3. Separate deployment and rollback

| Object | Retain |
| --- | --- |
| Instructions | V1 baseline, current v2, exact instruction-file hashes |
| Execution | Actual response/trace IDs, model, and data |
| Deployment | The service-issued agent version, distinct from instruction v1/v2 |
| Delivery | Source-matching HTML/Markdown/PDF/ZIP |

Do not relabel service deployment IDs or historical evidence IDs as “v2.” Keep the learning instructions at v2 while preserving actual IDs and hashes.
Reconfirm the target and approval scope before deployment changes or rollback.

### 4. Understand cost and lifecycle

![Operate monitoring. Distinguish requests, errors, and usage from actual quality judgments.](../../assets/portal/en/07-monitor.png)

Inference, Search, Hosted compute, and retained data have separate charging mechanisms.
Stopping a session is neither resource deletion nor proof of zero total cost. An empty billing response does not mean free usage.
Actual cost queries, extra feature execution, and deletion each need the appropriate approved scope.

## Success criteria

Another learner can extract the ZIP, read both 25-module editions, and inspect the same v1/v2 comparison plan.
They can distinguish latest originals, current instructions, local checks, Azure execution, and quality judgments.

## Troubleshooting

First check `.env`/language selection, missing dependencies, and generated-file drift.
Do not hide CI failures, lower paid-validation gates, or copy historical logs as new execution.

## Cleanup

Keep private settings and raw responses under `results/`; share only the latest reviewed originals.
Do not rewrite Git history. Azure resource deletion is not a default part of this module.
