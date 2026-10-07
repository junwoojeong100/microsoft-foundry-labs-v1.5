# Microsoft Foundry Lab Guide

**English** | [한국어](README.ko.md)

**[Open the online guide — index.html](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/)** · **[한국어 가이드](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html)**

Build a synthetic Contoso purchasing assistant through **20 labs and five reference sections (25 articles)**. Both languages share the same implementation and use their own data and instructions.

## First time here?

**You create your own environment and follow the guide end to end.** In L01, prepare your PC/subscription, verify permissions/budget, and create a dedicated Foundry project, models, and telemetry. Then build agents, retrieval, tools, evaluations, and traces. Actual operations require the relevant scoped Azure permissions and cost approval.

1. Read [L00: the basics](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.html#l00-first-steps) to see what you will build.
2. Extract the [workshop ZIP](downloads/Contoso-Foundry-Hands-on-2026-09-30.zip), then follow [L01](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.html#l01) for PC/project setup. Git commands are not required.
3. Follow **Format → Start here → What to check** in each module. Take 11 core modules in order, choose among eight advanced electives, and finish with shared wrap-up L19.

The web reader starts with **11 core modules plus one shared wrap-up** and counts progress only within the selected path. Action-led titles also identify features such as Responses API, File search, Function Calling, Evaluation, and Tracing. **Explain a term / I'm stuck** opens help with a return link to the original lab.

Blocks distinguish **terminal commands / portal Chat / .env settings / expected output**. On narrow screens, command walkthroughs read vertically. L01 explains new-terminal and Windows Python selection. L06's `read-result --input` displays saved answers, function results, and citations **without new Azure calls**, changing neither originals nor evaluation judgments.

For a first run, follow **Prerequisites → Steps → Success criteria → Cleanup**, opening collapsed **implementation references** only when needed. Every module ends with **Keep / Continue** to identify saved results and reused targets. L03 defaults to one Python request; L04/L05/L09 reuse one portal policy agent; L06 and L08 create separate SDK agents. L08 collection and evaluation use separate command blocks with an original-completion check between them.

Without Azure access, practice local functions and read L08's inputs, separately from live completion. The default path collects/evaluates your own answers and reads your logs. Review integration in L06 and optional publishing/version management in L18. No separate capstone, Teams publishing, Hosted, or Optimizer is required for core completion.

Every advanced lab identifies its starting path, configuration sources, and result locations. Create the L11 Search/L12 Hosted resources yourself. Agent Framework is split into L13 sequential/concurrent and L14 group-chat/handoff. L17 access and L18 CI/CD use local repairs/design, separately from actual Azure validation or publishing.

<details>
<summary>Instruction learning path and model conditions</summary>

**The learning path is initial v1 → evaluate → analyze and improve → reevaluate v2.** Compare `agent-v1.txt` and `agent-v2.txt` under the same conditions.
V2 explicitly separates public and restricted questions, covers every requested part, matches evidence to individual claims, preserves unknown facts, and respects actual tool permissions/results.

The kit pins **`gpt-6-sol / 2026-09-22`**; L01 creates deployment `contoso-chat`. Verify model/region availability in your own subscription. L08 collects twelve matched v1/v2 question pairs once and evaluates those originals. No holdout, Hosted redeployment, or Optimizer is required, and actual score improvement is not guaranteed.

</details>

## Read or download

| Format | Location |
| --- | --- |
| English web guide | [GitHub Pages](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/) |
| Korean web guide | [GitHub Pages · 한국어](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html) |
| Markdown | [English](downloads/GUIDE.en.md) · [한국어](downloads/GUIDE.ko.md) |
| Complete kit | [Bilingual ZIP](downloads/Contoso-Foundry-Hands-on-2026-09-30.zip) |
| Synthetic receipt | [English](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/en/receipt.html) · [한국어](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/receipt.html) |

For a file-by-file code reference, see [English](samples/README.md) or [한국어](samples/README.ko.md).

Extract the ZIP first and keep its structure. Open `index.html` or `index.ko.html`; use an editor to inspect code.
Open Markdown inside the kit's `downloads/` folder to resolve its images and source links.
The core course is **L00–L10, about 4 hours 45 minutes**. Advanced electives are **L11–L18**, followed by **L19 shared wrap-up (10 minutes)**; lab numbers are continuous from 00 through 19. Core-only learners go directly from L10 to L19; others finish their selected electives before L19. Reading requires no sign-in.

Work through **what to inspect → a decision grounded in values → the next action on failure**. Later modules provide interpretation examples for traces, orchestration, access, and releases, plus worked Contoso designs. Examples are not Azure results; record design completion separately from actual execution. L18's default CI/release-design path does not require Hosted deployment.

## Compare instruction versions

`agent-v1.txt` is the role-and-goal baseline; `agent-v2.txt` is the procedural instruction used by Prompt and Hosted defaults.

L08 uses `samples/instruction_prompt_agent_lab.py` for collection, followed by `samples/instruction_evaluation.py` on the same originals. Both require explicit `--live` and verified cost scope. Keep both files in your `results/`; reading only is recorded as evaluation not performed.

## Narrated lab walkthroughs

[Chapter player](downloads/replay/index.html) · [English MP4](downloads/replay/Contoso-Foundry-Replay.en.mp4) · [한국어 MP4](downloads/replay/Contoso-Foundry-Replay.ko.mp4). Both include narration, subtitles, and all 20 module chapters. These are instructional reconstructions using commands and diagrams, not live portal recordings.

Rebuild locally on macOS with installed FFmpeg, system voices, and the declared Playwright dependency: `python scripts/build_replay.py`. Narration and scenes come from `content/replay.json`.

## Working safely

Use only synthetic Contoso data. These tools never place real orders, take payments, or grant business approval.
Keep private `.env`, `.azure/`, credentials, and raw personal execution files out of Git and the kit.
Select `FOUNDRY_LAB_LANGUAGE=en` in the separate English environment; Korean remains the default. Do not mix environments or ownership receipts.
New Azure calls, access changes, and resource deletion require explicit scope and approval.

## Edit and regenerate

Edit `docs/`, `docs/en/`, `content/`, and the shared sources; never hand-edit generated readers.
Keep learner-facing text and captions focused on actions, results to check, and prerequisites. Preserve capture records in `content/portal-screenshots*.json` and source-review dates/notes in `content/sources*.json` rather than repeating them in the reader. Do not change original screenshots, hashes, or historical validation records.
The `microsoft-foundry` skill is development guidance, not a learner, runtime, or documentation-build dependency.
With the declared Python/Node dependencies installed:

```bash
python scripts/build_guide.py
FOUNDRY_LAB_LANGUAGE=ko python -m unittest discover -s tests -q
python scripts/check_guide.py
npm run guide:browser
python scripts/package_guide.py
```

The same checked-in sources produce both HTML/Markdown editions and one ZIP. Keep local reports under private `results/documentation/`; do not package them.
Local checks are not Azure execution or measured model improvement.

Learner-facing numbers come from `number` in `content/chapters.json`. Existing IDs and source filenames remain stable identifiers for links, progress, and historical records, so they can differ from display numbers. The former `#l11` link opens L06's integration review; historical validation numbers and originals remain unchanged.

## GitHub Pages

Pages serves the **root of the `main` branch** (`/`). A push to `main` automatically publishes the checked-in HTML and download files; no separate publishing branch is needed.
Merging into `main` still requires approval and now also publishes the site. Regenerate and review HTML/Markdown/ZIP before merging; Pages does not run the guide generators.
The existing validation workflow and Pages deployment run independently: **Pages does not wait for validation to finish**.
Keep `.nojekyll` and do not force-push. Branch deletion, repository visibility changes, and Azure operations require explicit approval.
Use `python scripts/check_pages.py` after deployment to compare the public HTML/assets with the merged sources.

This is not an official Microsoft curriculum. See [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES).
