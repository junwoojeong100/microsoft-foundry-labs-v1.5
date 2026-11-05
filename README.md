# Microsoft Foundry Lab Guide

**English** | [한국어](README.ko.md)

**[index.html · online guide](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/)** · [한국어](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html)

**Twenty portal-first modules and five references.** The core course needs no CLI, Python, or SDK. Optional **L12–L14 use real Hosted/MAF code and explained terminal commands** where portals cannot execute the task. No development skill or Codespaces is required. Use synthetic Contoso purchasing data only.

## Start here

1. Use [L00](docs/en/00-start.md) to bound resources, requests, and costs. The core path is **L00–L10 → L19**, about **4 hours 45 minutes** plus ten-minute wrap-up, excluding approval/provisioning waits.
2. Follow [L01](docs/en/01-setup.md), sign in in a new window, and create a dedicated group/account/project/logging. In L02 inspect exact model version, SKU, TPM, and processing location before deployment.
3. Follow **Prerequisites → one table row → observed screen/value → failure action**. Verify before proceeding.

| Need | Use |
| --- | --- |
| Policies/instructions/evaluation input | Extract the [small portal-input ZIP](downloads/Contoso-Portal-Inputs.zip) and use `en/`: three policies, v1/v2 Instructions, fixed twelve-row JSONL and review CSV, manual checklist. |
| Practice screens | Azure portal for resources/costs; Foundry portal for models, agents, files, evaluations, traces. Buttons/fields identify every input destination. |
| Actual footage | [Live portal recordings and coverage](downloads/portal/index.html). Missing video stages are not successful executions. |
| Hosted/MAF code practice | Extract the **complete kit**, not the portal-input ZIP. L12 and L13 explain separate Python 3.13 environments, real source, offline checks, and separately approved live steps. |
| Read without installation/sign-in | Choose **Read without executing**, or use offline HTML/Markdown. Reading is not Microsoft Azure execution. |

The core targets are a portal policy agent and **two tool-free v1/v2 evaluation Prompt Agents**. L06 does not pretend the portal executes unimplemented inventory/persistence/approval functions. L07's read-only MCP requires supported UI and permissions.

L08 is a new portal experiment, separate from historical SDK collections. Keep identical synthetic context/model, twelve fixed questions, and only v1/v2 Instructions different. Evaluate actual generated answers, not invented responses. Preserve **quality ≥90%, zero safety/access failures**, errors, and missing rows. There is no holdout or production-generalization claim.

Read advanced prerequisites first. L12 follows source → offline packaging → optional single-service azd deployment/exact-version invocation. L13–L14 execute actual SDK sequential, concurrent, group-chat, and handoff builders with **network-blocked synthetic fixtures** by default; live model calls require ownership, capacity, and cost approval. Fixture responses/usage are not Microsoft Azure or quality evidence. Hosted and MAF require **separate environments**. Existing footage contains neither Hosted deployment nor MAF execution.

Additional Search requires separate approval. Inspect Memory's creation form/runtime warning and cancel; conditional recall with an approved existing store is not CRUD/isolation validation. Routines cancel before submission; governance/release decisions remain read-only. Remote A2A, HITL, and business approval are not executed.

**Recorded portal execution:** Created the owned group, Microsoft Foundry account/project, logging, two manual model deployments plus an observed automatic embedding dependency, and three policy files. Recorded eleven direct Chat sends and two twelve-row Korean evaluations. Both generated twelve answers, but **one v2 Relevance row returned APIConnectionError**: native comparison incomplete, release held. Read the [identifier-redacted actual answers/error](downloads/portal/evaluation-summary.json) with the video's original twenty-module coverage. Historical examples and local checks are not new Microsoft Azure successes.

## Materials

| Format | Location |
| --- | --- |
| Web | [English](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/) · [한국어](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html) |
| Markdown | [English](downloads/GUIDE.en.md) · [한국어](downloads/GUIDE.ko.md) |
| Browser-uploadable input | [Small input ZIP](downloads/Contoso-Portal-Inputs.zip) |
| Complete offline kit | [Bilingual HTML/Markdown/images/materials ZIP](downloads/Contoso-Foundry-Hands-on-2026-10-15.zip) |
| Actual screen recording | [Video, captions, executed/blocked coverage](downloads/portal/index.html) |
| Optional document-analysis example | [English receipt](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/en/receipt.html) · [한국어 영수증](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/receipt.html); not a required upload |
| Historical reconstructions | [Legacy walkthrough](downloads/replay/index.html): command/diagram/narration reconstruction, **not actual portal footage**. Do not follow it as the current workflow. |

Preserve the complete kit's directory structure and open `index.html`. Upload only the three `en/policies/` Markdown files or L08's `evaluation-12.jsonl`, not the entire kit. CSV is a human-readable sidecar. Never publish login screens, keys, email, people lists, or raw logs.

The online site serves `main`. Working-branch revisions remain local HTML/Markdown/ZIP until an explicitly approved main update.

## Costs and safety

Canonical target: **`gpt-6-sol / 2026-09-22`**, deployment `contoso-chat`; judge **`gpt-4.1 / 2025-04-14`**, `contoso-judge`. Verify actual subscription/version/region availability. Record absence as blocked; never silently substitute another model.

Use dedicated scope, private ownership records, and explicit resource/request limits. Request bounds are not a monetary ceiling; budget alerts are not spending enforcement. No real orders, payments, or business approval. Access expansion, schedules, publishing, and deletion require separate approval.

**Closing the browser does not stop resources/schedules.** Retain resources without deletion approval; logging, files, Search, or compute charges may continue. Hand off inventory, retention, and next cost review in [L19](docs/en/12-cleanup.md).

## Repository maintainers

The generation/validation commands below are maintainer-only. Learner terminal steps belong only to L12–L14.

<details>
<summary>Sources, generation, validation, and GitHub Pages</summary>

Edit `docs/`, `docs/en/`, `content/`, not generated HTML/Markdown. Display numbers come from `number`; preserve canonical IDs, filenames, former `#l11` links, the Korean twenty-module reader, and bilingual structure.

The `microsoft-foundry` skill is **development guidance**, not a learner/runtime/build dependency. Developers read it for Foundry-related changes; document builds do not download/run it.

With existing declared Python/Node dependencies:

```bash
python scripts/build_guide.py
FOUNDRY_LAB_LANGUAGE=ko python -m unittest discover -s tests -q
python scripts/check_guide.py
npm run guide:browser
python scripts/package_guide.py
python scripts/package_guide.py --check
```

The builder creates portal inputs, both HTML/Markdown editions, and a reviewed-footage index that checks asset hashes and twenty-module coverage. It does not record new footage or call Microsoft Azure. ZIP entries use fixed timestamps/sorting and replace the old archive only after link/integrity/private-data/maintainer exclusions pass. Keep local reports under private `results/documentation/`; they are not Microsoft Azure evidence.

Preserve screenshot originals/hashes/provenance and historical `validation/` evidence. New actual footage has separate provenance and executed/not-run coverage. Never package raw footage with authentication, identities, keys, subscriptions, or people lists.

Maintainer-only evaluation v2–v5, authoring/live-CI scripts, and dependent tests stay out of the kit through `content/maintainer-only.json`. Never alter frozen data/gates/history to pass a run. Portal input uses twelve questions from `instruction-comparison.json`. The [sample map](samples/README.md) distinguishes current L12–L14 code from preserved developer references; core portal labs do not run those legacy scripts.

Legacy reconstructions rebuild on macOS with FFmpeg, voices, and declared Playwright via `python scripts/build_replay.py`. Never reclassify `content/replay.json` scenes as real footage.

Pages serves the **root of the `main` branch** (`/`). Merging into `main` requires explicit approval; a push automatically publishes checked-in HTML/downloads. Pages does not wait for validation to finish or run generators. Keep `.nojekyll`; no force-push, unapproved merge, or visibility changes.

After approved publication, use `python scripts/check_pages.py` to compare public assets/ZIP with sources. `python scripts/check_links.py` detects official-document changes after recorded review dates. This portal revision does not rewrite those dates or historical live results.

</details>

Not an official Microsoft curriculum. See [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES) and [MIT License](LICENSE); Microsoft names/icons/screens retain their applicable rights. Never attach credentials or personal data to [guide issues](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/issues/new/choose).
