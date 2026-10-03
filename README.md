# Microsoft Foundry Lab Guide

**English** | [한국어](README.ko.md)

**[Open the online guide — index.html](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/)** · **[한국어 가이드](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html)**

Build a synthetic Contoso purchasing assistant through **25 labs and five reference sections**. Both languages share the same implementation and use their own data and instructions.

**The learning path is educational initial v1 → evaluate → analyze and improve → reevaluate v2.** Keep current improvements in `agent-v2.txt`; do not create more instruction versions or accumulate release-experiment narratives.
V2 explicitly separates public and restricted questions, covers every requested part, matches evidence to individual claims, preserves unknown facts, and respects actual tool permissions/results.

L02 explicitly deploys **`gpt-6-sol` version `2026-09-22`** as `contoso-gpt-6-sol`. L08 compares 12 fixed composite questions once for each instruction in both languages, then evaluates those preserved answers in Foundry. No holdout, Hosted redeployment, or Optimizer is required. **Actual score increases are not guaranteed or prewritten.**

## Read or download

| Format | Location |
| --- | --- |
| English web guide | [GitHub Pages](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/) |
| Korean web guide | [GitHub Pages · 한국어](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html) |
| Markdown | [English](downloads/GUIDE.en.md) · [한국어](downloads/GUIDE.ko.md) |
| PDF | [English](downloads/Contoso-Foundry-Hands-on-2026-09-30.en.pdf) · [한국어](downloads/Contoso-Foundry-Hands-on-2026-09-30.pdf) |
| Complete kit | [Bilingual ZIP](downloads/Contoso-Foundry-Hands-on-2026-09-30.zip) |
| Synthetic receipt | [English](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/en/receipt.html) · [한국어](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/receipt.html) |

Extract the ZIP first and keep its structure. Open `index.html` or `index.ko.html`; use an editor to inspect code.
The core course is L00–L12, about 5 hours 20 minutes. Choose advanced modules as needed. Reading requires no sign-in.

Work through **what to inspect → a decision grounded in values → the next action on failure**. Later modules provide interpretation examples for traces, extraction, voice, training data, and releases, plus worked Contoso designs. Examples are not Azure results; record design completion separately from actual execution. L22's default CI/release-design path does not require Hosted deployment.

## Instructions and latest evidence

- Educational baseline: `agent-v1.txt` in those folders is a deliberately simple role-and-goal starting instruction; it was not weakened to manufacture a lower score.
- Current: `agent-v2.txt` in those same folders; Prompt/Hosted build defaults use v2.
- One Prompt Agent comparison: `samples/instruction_prompt_agent_lab.py`; native evaluation of its originals: `samples/instruction_evaluation.py`. Both require explicit `--live`.
- [Current status](validation/current/instructions.json), [latest actual Azure originals](validation/current/report.json), and [current documentation checks](validation/docs/structure.json).

**Both languages were measured through GPT-6 Sol Prompt Agent versions.** Korean native relevance moved from **4.9167/5 to 5.0/5** on one question; completeness and groundedness tied. All three English metrics tied at **5.0/5**. This is a limited Korean relevance gain observed in a small, exposed dev sample—not generalization, statistical significance, or operational approval. The supporting mechanical checklist tied at **33/40** in Korean and changed from **29/40 → 28/40 (−1)** in English. Every changed critical flag was reviewed against the answer originals; some wording was missed by the regex checks. The checklist is not a calibrated semantic or safety evaluator. The judge was the separate, fixed GPT-4.1 deployment.

The comparison collected **48 target responses** once and completed **two native runs with 24 rows each**. Evaluation-only Prompt Agents pinned v1/v2 in each language. V2 used more tokens (Korean **+7,376**, English **+5,157**) and had higher mean response latency (Korean **+0.427 s**, English **+0.496 s**). Optimizer and holdout were not run; this exposed dev comparison is not a release pass. Earlier direct-response instructions and measurements remain in [Git history at the preserved baseline commit](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/tree/39b2bd1a1c85cb18d3d46d8bf876a6e274d32958/validation).
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
