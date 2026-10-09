# Microsoft Foundry Lab Guide

**English** | [한국어](README.ko.md)

**[Open the online guide — index.html](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/)** · **[한국어 가이드](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html)**

Build a synthetic Contoso purchasing assistant through **20 labs and five reference sections (25 articles)**. Both languages share the same implementation and use their own data and instructions.

## First time here?

**The core path is L00–L10 → L19.** The core labs take about 4 hours 45 minutes and the wrap-up 10 minutes, excluding installation, approval, and provisioning waits. Advanced L11–L18 are optional.

1. Read [L00: the basics](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.html#l00-first-steps) to see what you will build.
2. Follow [L01: prepare GitHub Codespaces](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.html#l01-codespaces). No PC installation or ZIP download is required. Before creating Microsoft Azure resources, confirm your subscription, permissions, and cost approval.
3. In each module, follow **Prerequisites → Steps → Success criteria → Cleanup**. Check the success criteria, save **Keep**, then go to **Next** at the bottom of the page.

| What you need while learning | How to use the guide |
| --- | --- |
| Preparation or resuming | Check Codespaces readiness in L01. On another day, open the same Codespace and expand **Return in a new terminal** only. |
| Commands, questions, or settings | Check the **terminal / portal Chat / .env / expected output** label first. Inspect the plan, pause, then copy the actual execution command separately. |
| A term or an error | Open **Explain a term / I'm stuck**, then **Return to the lab** to resume at the same reading position. |
| Completion and records | Check success criteria against actual results. Browser progress is a learning marker, not proof of Microsoft Azure execution. |

Collapsed **implementation references and optional extensions** are not required for the core path. A separate capstone, Teams publishing, Hosted, and Optimizer are not core requirements either. The core course uses a portal policy agent, an integrated SDK agent, and an instruction-evaluation agent **separately**; see [L00's three-target table](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.html#l00-agent-map) for how they relate.

**Not ready for Microsoft Azure?** Select **Without Microsoft Azure** in the web contents. Follow only the stated local, reading, and design steps, separately from live completion. When choosing an elective, check its prerequisites first.

### Default environment: GitHub Codespaces

With a browser and GitHub account, open **repository → Code → Codespaces → New with options**. Review the default branch (`main`), payer, allowance, and machine before creating it. Tool and package preparation and the readiness checks are grouped in [L01](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.html#l01-codespaces).

Use **Linux/Bash commands** in Codespaces even from a Windows PC. Microsoft Azure sign-in and resource creation are separate steps. At [L19](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.html#l12), check Microsoft Azure resources and the Codespace **separately**. Stopping a Codespace can leave storage charges and Microsoft Azure resource charges.

<details>
<summary>Only if you need another environment: use your PC</summary>

If Codespaces is unavailable or not permitted, extract the [workshop ZIP](downloads/Contoso-Foundry-Hands-on-2026-09-30.zip) and expand [L01's PC setup](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.html#l01-pc). Windows/macOS/Linux installation, virtual-environment setup, and alternative sign-in instructions are grouped there. Do not mix `.env` or ownership records between environments.

</details>

<details>
<summary>Instructions (v1·v2) and model conditions</summary>

**The learning path is initial v1 → evaluate → analyze and improve → reevaluate v2.** Compare `agent-v1.txt` (the role-and-goal baseline) and `agent-v2.txt` (procedural instructions, the Prompt and Hosted default) under the same conditions.
V2 explicitly separates public and restricted questions, covers every requested part, matches evidence to individual claims, preserves unknown facts, and respects actual tool permissions/results.

L08 collects twelve matched v1/v2 question pairs once (`samples/instruction_prompt_agent_lab.py`) and evaluates those originals in Microsoft Foundry (`samples/instruction_evaluation.py`). Both require explicit `--live`, so verify the cost scope before running them, and keep both files in your `results/`. Reading only is recorded as evaluation not performed.

The kit pins **`gpt-6-sol / 2026-09-22`**; L01 creates deployment `contoso-chat`. Verify model/region availability in your own subscription. No holdout, Hosted redeployment, or Optimizer is required, and actual score improvement is not guaranteed.

</details>

## Read or download

| Format | Location |
| --- | --- |
| English web guide | [GitHub Pages](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/) |
| Korean web guide | [GitHub Pages · 한국어](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html) |
| Markdown | [English](downloads/GUIDE.en.md) · [한국어](downloads/GUIDE.ko.md) |
| Complete kit | [Bilingual ZIP](downloads/Contoso-Foundry-Hands-on-2026-09-30.zip) |
| Narrated walkthroughs | [Chapter player](downloads/replay/index.html) · [English MP4](downloads/replay/Contoso-Foundry-Replay.en.mp4) · [한국어 MP4](downloads/replay/Contoso-Foundry-Replay.ko.mp4) |
| Sample receipt (optional L03 image input) | [English](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/en/receipt.html) · [한국어](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/receipt.html) |

For a file-by-file code reference, see [English](samples/README.md) or [한국어](samples/README.ko.md).

Codespaces already contains the files. Download/extract the ZIP only for offline materials, preserve its structure, and open `index.html` or `index.ko.html`. Open Markdown inside the kit's `downloads/` folder to resolve its images and source links. Reading requires no sign-in.

Work through **what to inspect → a decision grounded in values → the next action on failure**. Later modules provide interpretation examples for traces, orchestration, access, and releases, plus worked Contoso designs. Examples are not Microsoft Azure results; record design completion separately from actual execution. L18's default CI/release-design path does not require Hosted deployment.

The walkthroughs include narration, subtitles, and all 20 module chapters, but they are instructional reconstructions using commands and diagrams, not live portal recordings. They include the PC preparation route. Codespaces is now the default; follow the current L01 text for startup and configuration order.

## Working safely

Use only synthetic Contoso data. These tools never place real orders, take payments, or grant business approval.
Keep private `.env`, `.azure/`, credentials, and raw personal execution files out of Git and the kit.
Select `FOUNDRY_LAB_LANGUAGE=en` in the separate English environment; Korean remains the default. Do not mix environments or ownership receipts.
New Microsoft Azure calls, access changes, and resource deletion require explicit scope and approval.

## For repository maintainers

If you are only learning, you can stop reading here.

<details>
<summary>Regenerating sources and walkthroughs, and GitHub Pages</summary>

### Edit and regenerate

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

The same checked-in sources produce both HTML/Markdown editions and one ZIP. The validation workflow fails when regenerated HTML/Markdown differ from the committed files, and `python scripts/package_guide.py --check` fails when the committed ZIP differs from the sources. The ZIP is built to be reproducible (fixed timestamps, sorted entries), and the existing ZIP is replaced only after every check passed. Keep local reports under private `results/documentation/`; do not package them.
Local checks are not Microsoft Azure execution or measured model improvement.

Learner-facing numbers come from `number` in `content/chapters.json`. Existing IDs and source filenames remain stable identifiers for links, progress, and historical records, so they can differ from display numbers. The former `#l11` link opens L06's integration review; historical validation numbers and originals remain unchanged.

### Rebuild the walkthroughs

Rebuild locally on macOS with installed FFmpeg, system voices, and the declared Playwright dependency: `python scripts/build_replay.py`. Narration and scenes come from `content/replay.json`.

### GitHub Pages

Pages serves the **root of the `main` branch** (`/`). A push to `main` automatically publishes the checked-in HTML and download files; no separate publishing branch is needed.
Merging into `main` still requires approval and now also publishes the site. Regenerate and review HTML/Markdown/ZIP before merging; Pages does not run the guide generators.
The existing validation workflow and Pages deployment run independently: **Pages does not wait for validation to finish**.
Keep `.nojekyll` and do not force-push. Branch deletion, repository visibility changes, and Microsoft Azure operations require explicit approval.
Use `python scripts/check_pages.py` after deployment to compare the public HTML, assets, and ZIP with the merged sources. `python scripts/check_links.py` reports official pages that changed after the recorded source-review date (`--fail-on-changed` turns that into a failure).
To shorten Codespaces startup for learners, you can configure a prebuild for `main` under the repository's **Settings → Codespaces** (optional; it uses quota).

</details>

This is not an official Microsoft curriculum. See [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES).

The repository's code and documentation are released under the [MIT License](LICENSE); Microsoft product names, the icon, and portal screenshots are excluded. Report guide problems or suggestions as an [issue](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/issues/new/choose); never paste `.env`, keys, or personal data.
