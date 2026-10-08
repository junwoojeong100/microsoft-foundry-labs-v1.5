# Microsoft Foundry Lab Guide

**English** | [한국어](README.ko.md)

**[Open the online guide — index.html](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/)** · **[한국어 가이드](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html)**

Build a synthetic Contoso purchasing assistant through **20 labs and five reference sections (25 articles)**. Both languages share the same implementation and use their own data and instructions.

## First time here?

**For a first run, follow core L00–L10 → shared wrap-up L19.** Create your own environment in L01 and verify scoped permissions and cost approval before actual Microsoft Azure operations. Advanced L11–L18 are not required for core completion.

1. Read [L00: the basics](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.html#l00-first-steps) to see what you will build.
2. **For fewer local installations, choose the [GitHub Codespaces route](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.html#l01-codespaces).** To use your own PC instead, extract the [workshop ZIP](downloads/Contoso-Foundry-Hands-on-2026-09-30.zip) and follow [L01](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.html#l01). Use one environment, not both; Git commands are not required.
3. Read each module's start card, then follow **Prerequisites → Steps → Success criteria → Cleanup**. Check **Keep / Continue** before using **Next** at the bottom of the page.

| What you need while learning | How to use the guide |
| --- | --- |
| Installation or resuming | In L01, check versions and expand installation instructions only for missing tools. Use **Return in a new terminal** on another day. |
| Commands, questions, or settings | Check the **terminal / portal Chat / .env / expected output** label first. Inspect the plan, pause, then copy the actual execution command separately. |
| A term or an error | Open **Explain a term / I'm stuck**, then **Return to the lab** to resume at the same reading position. |
| Completion and records | Check success criteria against actual results. Browser progress is a learning marker, not proof of Microsoft Azure execution. |

Collapsed **implementation references and optional extensions** are not a to-do list. The core path checks your answers, evidence, function results, evaluations, and logs; it does not require a separate capstone, Teams publishing, Hosted, or Optimizer.

**Not ready for Microsoft Azure?** Select **Without Microsoft Azure** in the web contents. Follow only the stated local, reading, and design steps, separately from live completion. When choosing an elective, check its prerequisites first.

### Minimize installation with GitHub Codespaces

With a browser and GitHub account, open **repository → Code → Codespaces → New with options**. Select the lab branch containing `.devcontainer/devcontainer.json` and review the payer, allowance, and machine before creating it. The configuration prepares Python 3.13, Microsoft Azure CLI, Bicep, the Python extension, and core/MCP dependencies. **You do not need Python, CLI, VS Code, or Docker installed on your own PC.**

Wait for post-creation setup to finish, then run L01's readiness checks. Microsoft Azure authentication, permissions, and cost approval remain separate; no resources are created automatically. Use **Linux/Bash commands** in Codespaces even from a Windows PC. At [L19](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.html#l12), check Microsoft Azure resources and the Codespace **separately**. Stopping a Codespace can leave storage charges and Microsoft Azure resource charges.

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

Work through **what to inspect → a decision grounded in values → the next action on failure**. Later modules provide interpretation examples for traces, orchestration, access, and releases, plus worked Contoso designs. Examples are not Microsoft Azure results; record design completion separately from actual execution. L18's default CI/release-design path does not require Hosted deployment.

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
New Microsoft Azure calls, access changes, and resource deletion require explicit scope and approval.

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
Local checks are not Microsoft Azure execution or measured model improvement.

Learner-facing numbers come from `number` in `content/chapters.json`. Existing IDs and source filenames remain stable identifiers for links, progress, and historical records, so they can differ from display numbers. The former `#l11` link opens L06's integration review; historical validation numbers and originals remain unchanged.

## GitHub Pages

Pages serves the **root of the `main` branch** (`/`). A push to `main` automatically publishes the checked-in HTML and download files; no separate publishing branch is needed.
Merging into `main` still requires approval and now also publishes the site. Regenerate and review HTML/Markdown/ZIP before merging; Pages does not run the guide generators.
The existing validation workflow and Pages deployment run independently: **Pages does not wait for validation to finish**.
Keep `.nojekyll` and do not force-push. Branch deletion, repository visibility changes, and Microsoft Azure operations require explicit approval.
Use `python scripts/check_pages.py` after deployment to compare the public HTML/assets with the merged sources.

This is not an official Microsoft curriculum. See [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES).
