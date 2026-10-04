# Microsoft Foundry Lab Guide

**English** | [한국어](README.ko.md)

**[Open the online guide — index.html](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/)** · **[한국어 가이드](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html)**

Build a synthetic Contoso purchasing assistant through **20 labs and five reference sections (25 articles)**. Both languages share the same implementation and use their own data and instructions.

## First time here?

**Azure is the cloud platform; Foundry is a workspace on it for building and managing AI.** Start with the concepts without prior product experience. Actual calls require an instructor-prepared project, permissions, and cost approval.

1. Read [L00: the basics](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.html#l00-first-steps) to see what you will build.
2. Extract the [workshop ZIP](downloads/Contoso-Foundry-Hands-on-2026-09-30.zip), then follow [L01](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.html#l01) for PC/project setup. Git commands are not required.
3. Follow **Format → Start here → What to check** in each module. Take the 13 core modules in order; choose among seven advanced electives.

The web reader starts with the **13-module core path** and counts progress only within the selected path. Action-led titles and shorter concept introductions across all 20 modules keep the next task clear. **Explain a term / I'm stuck** opens help with a return link to the original lab.

Blocks distinguish **terminal commands / portal Chat / .env settings / expected output**. On narrow screens, command walkthroughs read vertically. L01 explains new-terminal and Windows Python selection. L06/L11's `read-result --input` displays saved answers, function results, and citations **without new Azure calls**, changing neither originals nor evaluation judgments.

Without an account, you can still use local functions and **read instructions and evaluation questions** in L08. Collecting and grading your own answers is optional. Administrator creation is in expandable sections; L11 reuses L06's result. Teams publishing, Hosted, and Optimizer are not core-course prerequisites.

L15, L21, and L22 include **change-and-compare exercises**. Use Agent Framework's sequential, concurrent, group-chat, and handoff patterns to compare execution flow and intermediate answers. Access and CI/CD use repairable local fixtures, clearly separate from Azure evidence.

<details>
<summary>Instruction learning path and model conditions</summary>

**The learning path is educational initial v1 → evaluate → analyze and improve → reevaluate v2.** Keep current improvements in `agent-v2.txt`; do not create more instruction versions or accumulate release-experiment narratives.
V2 explicitly separates public and restricted questions, covers every requested part, matches evidence to individual claims, preserves unknown facts, and respects actual tool permissions/results.

L02 explicitly deploys **`gpt-6-sol` version `2026-09-22`** as `contoso-gpt-6-sol`. L08 compares 12 fixed composite questions once for each instruction in both languages, then evaluates those preserved answers in Foundry. No holdout, Hosted redeployment, or Optimizer is required. **Actual score increases are not guaranteed or prewritten.**

</details>

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
Open Markdown inside the kit's `downloads/` folder to resolve its images and source links. PDFs include the expandable reference and administrator sections.
The core course is L00–L12, about 5 hours 20 minutes. Choose among L13–L17 and L21–L22 as needed; retained modules keep their original numbers. Reading requires no sign-in.

Work through **what to inspect → a decision grounded in values → the next action on failure**. Later modules provide interpretation examples for traces, orchestration, access, and releases, plus worked Contoso designs. Examples are not Azure results; record design completion separately from actual execution. L22's default CI/release-design path does not require Hosted deployment.

## Instructions and execution boundaries

`agent-v1.txt` is the role-and-goal baseline; `agent-v2.txt` is the current procedural instruction used by Prompt and Hosted defaults. Never weaken the baseline or lower evaluation gates to manufacture improvement.

L08's optional collection uses `samples/instruction_prompt_agent_lab.py`, followed by `samples/instruction_evaluation.py` on the same originals. Both require explicit `--live`. Keep responses, scores, failures, ownership receipts, and cost records in private `results/`, outside the reader and kit. The guide describes procedures and criteria, not an author's completed run or guaranteed scores.

## Narrated lab walkthroughs

[Chapter player](downloads/replay/index.html) · [English MP4](downloads/replay/Contoso-Foundry-Replay.en.mp4) · [한국어 MP4](downloads/replay/Contoso-Foundry-Replay.ko.mp4). Both include narration, subtitles, and all 20 module chapters. These are instructional reconstructions using commands and diagrams, not live portal recordings or validation reports.

Rebuild locally on macOS with installed FFmpeg, system voices, and the declared Playwright dependency: `python scripts/build_replay.py`. Narration and scenes come from `content/replay.json`.

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

The same checked-in sources produce both HTML/Markdown/PDF editions and one ZIP. Keep local reports under private `results/documentation/`; do not package them.
Local checks are not Azure execution or measured model improvement.

## GitHub Pages

Pages serves the **root of the `gh-pages` branch**. Keep `.nojekyll`; publish only reviewed artifacts after approval, without force-pushing or deleting that branch.
Merging into `main`, Pages publication, and visibility changes are separate actions, not automatic consequences of editing instructions.
Use `python scripts/check_pages.py` after approved publication to compare the public HTML/assets with the generated sources.

This is not an official Microsoft curriculum. See [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES).
