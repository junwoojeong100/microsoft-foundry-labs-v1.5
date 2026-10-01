# Microsoft Foundry Lab Guide

**English** | [한국어](README.ko.md)

**[Open the online guide — index.html](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/)** · **[한국어 가이드](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html)**

Build a synthetic Contoso purchasing assistant through **25 labs and five reference sections**. Both languages share the same implementation and use their own data and instructions.

**The learning path is now simple: unchanged v1 → improved v2 → one comparison.** Keep current improvements in `agent-v2.txt`; do not create more instruction versions or accumulate release-experiment narratives.
V2 explicitly separates public and restricted questions, covers every requested part, matches evidence to individual claims, preserves unknown facts, and respects actual tool permissions/results.

L08 compares three fixed questions once per prompt with the same model, context, output format, and checklist. No repeated runs, holdout, Hosted redeployment, or Optimizer are required.
**Actual score increases are not guaranteed or prewritten.** Ties, regressions, errors, and incomplete results remain visible.

## Read or download

| Format | Location |
| --- | --- |
| English web guide | [GitHub Pages](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/) |
| Korean web guide | [GitHub Pages · 한국어](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html) |
| Markdown | [English](GUIDE.en.md) · [한국어](GUIDE.ko.md) |
| PDF | [English](Contoso-Foundry-Hands-on-2026-09-30.en.pdf) · [한국어](Contoso-Foundry-Hands-on-2026-09-30.pdf) |
| Complete kit | [Bilingual ZIP](Contoso-Foundry-Hands-on-2026-09-30.zip) |
| Synthetic receipt | [English](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/en/receipt.html) · [한국어](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/receipt.html) |

Extract the ZIP first and keep its structure. Open `index.html` or `index.ko.html`; use an editor to inspect code.
The core course is L00–L12, about 5 hours 20 minutes. Choose advanced modules as needed. Reading requires no sign-in.

## Instructions and latest evidence

- Baseline: `data/prompts/agent-v1.txt` and `data/en/prompts/agent-v1.txt`, unchanged.
- Current: `agent-v2.txt` in those same folders; Prompt/Hosted build defaults use v2.
- One comparison: `samples/instruction_lab.py`; plan only unless separately approved with `--live`.
- [Current status](validation/current/instructions.json), [latest actual Azure originals](validation/current/report.json), and [current documentation checks](validation/docs/structure.json).

The edited v2 has **not** been newly compared in Azure. The preserved latest Azure run predates the edit and remains **39/40 with a critical access-evidence failure**, with an Optimizer error/failure and no holdout execution. It is not relabeled as a pass for the current instructions.
Older reports were removed from the current tree, not rewritten: [immutable pre-cleanup history](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/tree/6fddd4642be0d0ac9dfee9b9b51e7b00b5cf1cde/validation).
Original run/deployment IDs remain in raw evidence for provenance; they are not instruction versions.

## Working safely

Use only synthetic Contoso data. These tools never place real orders, take payments, or grant business approval.
Keep private `.env`, `.azure/`, credentials, and raw personal execution files out of Git and the kit.
Select `FOUNDRY_LAB_LANGUAGE=en` in the separate English environment; Korean remains the default. Do not mix environments or ownership receipts.
The `microsoft-foundry` skill is authoring guidance, not a learner/runtime dependency. New Azure calls, access changes, and resource deletion require explicit scope and approval.

## Edit and regenerate

Edit `docs/`, `docs/en/`, `content/`, and the shared sources; never hand-edit generated readers.
With the declared Python/Node dependencies installed:

```bash
python scripts/build_guide.py
FOUNDRY_LAB_LANGUAGE=ko python -m unittest discover -s tests -q
npm run guide:pdf
python scripts/check_guide.py
npm run guide:browser
python scripts/check_pdf.py
python scripts/package_guide.py
```

The same checked-in sources produce both HTML/Markdown/PDF editions and one ZIP. Keep only current local reports under `validation/docs/`.
Local checks are not Azure execution or measured model improvement.

## GitHub Pages

Pages serves the **root of the `gh-pages` branch**. Keep `.nojekyll`; publish only reviewed artifacts after approval, without force-pushing or deleting that branch.
Merging into `main`, Pages publication, and visibility changes are separate actions, not automatic consequences of editing instructions.
Use `python scripts/check_pages.py` after approved publication to compare the public HTML/assets with the generated sources.

This is not an official Microsoft curriculum. See [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES).
