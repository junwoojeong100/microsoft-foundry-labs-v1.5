# Microsoft Foundry Lab Guide

**English** | [한국어](README.ko.md)

**[Open the online guide — index.html](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/)** · **[한국어 가이드](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html)**

Learn models, knowledge, tools, evaluation, and operations by building a synthetic Contoso purchasing assistant. Both editions contain **25 labs and five reference sections**. The English guide has **18 newly captured English portal screens and 124 explained commands**; the preserved Korean guide has 17 screens and 120 explained commands.

**English is the default.** Use the language switch to open the same module in Korean. Both editions share learning progress, theme, and learning-path preferences in the same browser.

**Latest English v5 live validation: no release approval.** Both version-4 protocol smokes and **8/8 judge controls** passed. All **40 dev cases** were collected and natively evaluated once, with 40 native passes and zero evaluator errors/skips. The combined business result is **39/40 (97.5%)**, but `v5-dev-30` has a **critical access-evidence failure**, so the unchanged zero-critical-failure gate blocks release. The independent holdout remains **sealed and unexecuted: 0/10**. See the [v5 live report](validation/english/automated-v5/report.json), [quality record](validation/english/automated-v5/quality.json), and [failure diagnosis](validation/english/automated-v5/dev30-diagnosis.json).

The `explicit-request-v2` candidate was frozen as **34 source inputs**, inheriting all 40 v4 dev questions/oracles and the same eight controls. A separate authoring context then sealed ten new holdout cases without using the unused v4 exam. The formerly aborting FX case completed in this run; that does not erase the new access-evidence failure. No answer, required citation, oracle, or threshold was repaired after seeing the result.

The [single dev-only Optimizer job](validation/english/automated-v5/optimizer.json) ended after **647 seconds** with service `succeeded`, but native rows were **38 passed / 1 failed / 1 errored**, so its outcome is **`operational_failure`**. It generated no candidate and promoted none. Fresh SDK [closeout](validation/english/automated-v5/operations.json) confirmed the job and native runs terminal and **all five created sessions stopped**. Scoped Responses job listing succeeded; no project-wide idle claim is made. Publishing these findings is not approval to release the agent.

**Earlier failures remain unchanged.** The [v4 run](validation/english/automated-v4/report.json) stopped after 36 dev responses and had three Optimizer evaluator errors despite service success; its unused holdout, original 27-source archive and five-session closeout are preserved. The [v3 holdout](validation/english/automated-v3/quality.json) remains 7/10 with a critical failure. The [offline correction record](validation/english/citation-remediation/report.json) still records only the local work performed at that earlier point.

## Get started

Begin with **L00: Microsoft Foundry at a glance**. The core course is **L00–L12, about 5 hours 20 minutes**; choose advanced modules L13–L24 as needed. Reading the guide requires no installation or sign-in. L01 explains the setup, permissions, and costs of running Azure labs.

| Format | Open or download |
| --- | --- |
| English web guide · default | [GitHub Pages](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/) |
| Korean web guide | [GitHub Pages · 한국어](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html) |
| Markdown | [English](GUIDE.en.md) · [한국어](GUIDE.ko.md) |
| Printable PDF | [English](Contoso-Foundry-Hands-on-2026-09-30.en.pdf) · [한국어](Contoso-Foundry-Hands-on-2026-09-30.pdf) |
| Complete bilingual workshop kit | [Download ZIP](Contoso-Foundry-Hands-on-2026-09-30.zip) |
| Synthetic receipt for the document lab | [English HTML](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/en/receipt.html) · [Korean HTML](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/receipt.html) |

For offline reading, **extract the ZIP first**, keep its folder structure, and open `index.html` (English) or `index.ko.html` (Korean). Code and configuration files are available in the repository file list or through **File → Open Folder** in VS Code.

## Repository layout

| Path | Contents |
| --- | --- |
| `docs/`, `docs/en/`, `content/` | Korean and English module sources, learning paths, official references, localized reader labels, and screenshot metadata |
| `assets/` | Reader UI, bilingual diagrams, original Korean captures, and new English captures in `assets/portal/en/` |
| `samples/`, `hosted/`, `data/`, `data/en/` | Shared lab/runtime code and separate Korean/English synthetic data profiles |
| `.env.example`, `azure.yaml`, `infra/` | Environment template and deployment definitions |
| `scripts/`, `tests/` | Generation, packaging, and regression checks |
| `validation/` | Latest results by validation category |

**Synthetic data only. The labs do not place real orders, take payments, or grant business approvals.** Read each command's scope, costs, and side effects before running it. Never commit `.env`, credentials, or personal execution results.

Use a separate checkout, `.env`, `.azure/`, and `results/` for a new English Azure run. In that terminal, select `export FOUNDRY_LAB_LANGUAGE=en` (PowerShell: `$env:FOUNDRY_LAB_LANGUAGE = "en"`). English commands then use `data/en/`, English Search analysis and citation labels, language-bound Hosted packages, and `validation/english/` evidence. Existing commands remain Korean unless explicitly opted in. Do not reuse another environment's ownership receipts.

The English profile preserves the business rules and quality thresholds, not Korean display text. Policies, prompts, inventory names, skill content, receipts, and evaluation examples are English. Its final holdout was independently authored and sealed. The `microsoft-foundry` skill remains authoring guidance, not a learner, runtime, or build dependency.

## Evidence and limits

[Latest English live report](validation/english/automated-v5/report.json) · [Preserved English v4 failure](validation/english/automated-v4/quality.json) · [Preserved Korean report](validation/current/report.json) · [Current documentation checks](validation/docs/live-v5/browser.json)

The preserved initial English walkthrough used a then-new owned resource group for model/agent calls, Search/IQ, both Hosted protocols, tools, evaluation, tracing, Memory, A2A, Routine and OIDC deployment. Its incomplete dev attempt and failed holdout remain unchanged. **V5 reused only that existing owned English environment** for the approved candidate/smoke, judge/dev and Optimizer stages; it did not rerun optional features or query costs.

The current file listing keeps only the latest results in each category. Earlier records remain unchanged in the [pre-cleanup Git commit](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/tree/faa5ec26f15cfeb38f69de4036acedc3151c3df4/validation). Paths in historical records refer to the commit used for that run.

Passing documentation or local checks is **not** a new Azure execution or a quality-gate result. The new English execution does not rewrite historical Korean evidence or relax evaluation thresholds.

## Edit and regenerate

Update the Korean sources in `docs/`, their English counterparts in `docs/en/`, and the corresponding metadata in `content/` together. The English metadata overlays preserve canonical module IDs, durations, source URLs, coverage levels, and prerequisites. Do not edit generated HTML or combined Markdown directly.

Install the Python documentation dependencies and Node.js/Playwright Chromium, then run:

```bash
python -m pip install -r requirements-docs.txt -r requirements-qa.txt
npm ci
npx playwright install chromium
python scripts/build_guide.py
FOUNDRY_LAB_LANGUAGE=ko python -m unittest discover -s tests -q
npm run guide:pdf
python scripts/check_guide.py --report-dir validation/docs/live-v5
npm run guide:browser -- --report-dir validation/docs/live-v5
python scripts/check_pdf.py --report-dir validation/docs/live-v5
python scripts/package_guide.py --report-dir validation/docs/live-v5
```

These commands generate and check **both languages**. One ZIP contains both readers, Markdown books, PDFs, and the shared code and data. The latest documentation reports live in `validation/docs/live-v5/`, preserving `validation/docs/citation-remediation/`, `validation/docs/live-v4/` and earlier reports unchanged. Choose a new report directory for later independent follow-ups. Documentation results are separate from Azure evidence.
The test-process-only `ko` setting preserves Korean-baseline assertions; the suite also launches explicit English-profile checks. It does not change the language of later live lab commands.

## GitHub Pages

Pages publishes the **root of the `gh-pages` branch**, kept separately from pull-request branches so merging and deleting a feature branch does not remove the site. Keep `.nojekyll`; after regenerating and checking the artifacts, publish the reviewed commit with `git push origin HEAD:gh-pages`. Never force-push or delete the publishing branch. Merging into `main` and changing repository visibility require separate approval.

Every guide HTML file is listed in the format table above. Relative links work under the repository's GitHub Pages path and in the extracted offline kit. English and Korean retain the same module fragments—for example, `#l13`—for deep links and language switching.

After publishing, run `python scripts/check_pages.py` to compare every public HTML page and its linked assets with the local sources. This makes only unauthenticated requests to this repository's GitHub Pages site; it does not call Azure.

This is not an official Microsoft curriculum. See [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES) for sources and usage terms.
