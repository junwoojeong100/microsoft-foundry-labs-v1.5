# Microsoft Foundry Lab Guide

**English** | [한국어](README.ko.md)

**[Open the online guide — index.html](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/)** · **[한국어 가이드](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html)**

Learn models, knowledge, tools, evaluation, and operations by building a synthetic Contoso purchasing assistant. The guide includes **25 labs and five reference sections in English and Korean**, 17 actual portal screenshots, and individual explanations for 120 CLI commands.

**English is the default.** Use the language switch to open the same module in Korean. Both editions share learning progress, theme, and learning-path preferences in the same browser.

## Get started

Begin with **L00: Microsoft Foundry at a glance**. The core course is **L00–L12, about 5 hours 20 minutes**; choose advanced modules L13–L24 as needed. Reading the guide requires no installation or sign-in. L01 explains the setup, permissions, and costs of running Azure labs.

| Format | Open or download |
| --- | --- |
| English web guide · default | [GitHub Pages](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/) |
| Korean web guide | [GitHub Pages · 한국어](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html) |
| Markdown | [English](GUIDE.en.md) · [한국어](GUIDE.ko.md) |
| Printable PDF | [English](Contoso-Foundry-Hands-on-2026-09-30.en.pdf) · [한국어](Contoso-Foundry-Hands-on-2026-09-30.pdf) |
| Complete bilingual workshop kit | [Download ZIP](Contoso-Foundry-Hands-on-2026-09-30.zip) |
| Synthetic receipt for the document lab | [Open HTML on GitHub Pages](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/receipt.html) |

For offline reading, **extract the ZIP first**, keep its folder structure, and open `index.html` (English) or `index.ko.html` (Korean). Code and configuration files are available in the repository file list or through **File → Open Folder** in VS Code.

## Repository layout

| Path | Contents |
| --- | --- |
| `docs/`, `docs/en/`, `content/` | Korean and English module sources, learning paths, official references, localized reader labels, and screenshot metadata |
| `assets/` | Reader UI, diagrams in both languages, and original portal screenshots |
| `samples/`, `hosted/`, `data/` | Lab code, agent runtime, and synthetic data |
| `.env.example`, `azure.yaml`, `infra/` | Environment template and deployment definitions |
| `scripts/`, `tests/` | Generation, packaging, and regression checks |
| `validation/` | Latest results by validation category |

**Synthetic data only. The labs do not place real orders, take payments, or grant business approvals.** Read each command's scope, costs, and side effects before running it. Never commit `.env`, credentials, or personal execution results.

Translation does not change runtime behavior. Executable inputs, Korean placeholders, synthetic fixtures, and original portal screenshots are preserved where needed for reproducibility. Their meaning is explained in English. The `microsoft-foundry` skill is authoring guidance, not a learner, runtime, or build dependency.

## Evidence and limits

[Last Azure execution report](validation/current/report.json) · [Latest automated quality results](validation/automated-v3/quality.json) · [Current documentation checks](validation/docs/browser.json)

The current file listing keeps only the latest results in each category. Earlier records remain unchanged in the [pre-cleanup Git commit](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/tree/faa5ec26f15cfeb38f69de4036acedc3151c3df4/validation). Paths in historical records refer to the commit used for that run.

Passing documentation or local checks is **not** a new Azure execution or a new quality-gate result. Translation does not rewrite historical evidence or relax evaluation thresholds.

## Edit and regenerate

Update the Korean sources in `docs/`, their English counterparts in `docs/en/`, and the corresponding metadata in `content/` together. The English metadata overlays preserve canonical module IDs, durations, source URLs, coverage levels, and prerequisites. Do not edit generated HTML or combined Markdown directly.

Install the Python documentation dependencies and Node.js/Playwright Chromium, then run:

```bash
python -m pip install -r requirements-docs.txt -r requirements-qa.txt
npm ci
npx playwright install chromium
python scripts/build_guide.py
python -m unittest discover -s tests -q
npm run guide:pdf
python scripts/check_guide.py
npm run guide:browser
python scripts/check_pdf.py
python scripts/package_guide.py
```

These commands generate and check **both languages**. One ZIP contains both readers, Markdown books, PDFs, and the shared code and data. Documentation reports live in `validation/docs/`; they are separate from Azure evidence.

## GitHub Pages

Pages publishes the **root of the `docs/bilingual-guide` branch**. Keep `.nojekyll` and push regenerated artifacts to that branch to update the site. Merging into `main` and changing repository visibility require separate approval.

Every guide HTML file is listed in the format table above. Relative links work under the repository's GitHub Pages path and in the extracted offline kit. English and Korean retain the same module fragments—for example, `#l13`—for deep links and language switching.

After publishing, run `python scripts/check_pages.py` to compare every public HTML page and its linked assets with the local sources. This makes only unauthenticated requests to this repository's GitHub Pages site; it does not call Azure.

This is not an official Microsoft curriculum. See [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES) for sources and usage terms.
