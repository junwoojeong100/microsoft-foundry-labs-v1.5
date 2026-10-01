> **Foundational sources reviewed: 2026-09-29 / Execution APIs rechecked: 2026-09-30, Asia/Seoul.** A review date does not make a source permanently current.

## How we assessed currency

We compared Microsoft Learn overviews, the capability reference, GA tables, feature documentation, and official SDK examples.
Portal GA is distinct from individual feature GA. Where API, region, or access scopes differ, the guide uses the narrower claim.
The monthly What's new roundup then covered August 2026; it was not relabeled as all September changes.

## Boundaries to remember

| Topic | Treatment |
| --- | --- |
| New portal GA | Separate from individual feature GA |
| Scheduled portal Workflows retirement | 2026-12-01; consider MAF for new implementations |
| Foundry IQ | Some APIs GA, portal experience Preview |
| Memory, Voice, Agent guardrails | Keep API-specific Preview/access conditions explicit |
| Agent Optimizer | Limited preview, optional exercise |
| Content Understanding | Distinguish 2025-11-01 GA and 2026-06-01-preview |
| SDKs | Separate installable core and advanced combinations |

## Current instructions and validation

The learning instructions use only **baseline v1 and improved v2**. L08 compares the same questions, context, model, and checks once.
The label v2 does not establish a score increase.

The [current instruction status]({validation}) records preparation and whether a real comparison exists.
Both languages were measured on 12 questions each using version-pinned GPT-6 Sol Prompt Agents. Korean native relevance moved from 4.9167/5 to 5.0/5 on one row; all other Korean metrics and all English metrics tied at 5.0/5. The mechanical checklist tied at 33/40 in Korean and changed from 29/40→28/40 in English. Every changed critical flag was reviewed against its original answer; some regex checks missed paraphrased wording. The [latest report](validation/current/report.json) links agent versions, responses, per-question native reasons, tokens, and latency. Local structure, browser and PDF checks live separately in `{documentation_validation}/`; they are not Azure results.

The [latest actual originals](validation/current/report.json) link these bilingual responses to native judgments.
The 48 target responses were collected once; two native runs completed with 24 rows each. V2 used 7,376 more tokens and 0.427 seconds more mean latency in Korean, and 5,157 more tokens and 0.496 seconds more in English. Neither Optimizer nor the sealed holdout was newly run.
Earlier direct-response instructions and measurements remain unchanged in [the preserved baseline commit](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/tree/39b2bd1a1c85cb18d3d46d8bf876a6e274d32958/validation). The limited observed Korean relevance change is not statistical significance, an independent holdout pass, or release approval.

Screenshots are actual portal observations from their recorded capture times, not new v2 execution or quality evidence.
Optional features, policy/access changes, cost queries, deletion, merges, and publication each require the applicable separate approval.

## Public official sources

{source_table}

## Refresh before the next workshop

Check GA tables, the capability reference, required feature docs, regional/model support, and SDK combinations.
Update the relevant sources and exercises when something actually changes. A learning guide does not need a growing sequence of validation numbers or histories.
