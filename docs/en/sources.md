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
Both languages were actually compared using `gpt-6-sol` / `2026-09-22`. For the same three questions per instruction, native completeness/relevance/groundedness means tied at 5.0/5. The Korean local checklist tied 9→9 and English 8→8. Local structure, browser and PDF checks live separately in `{documentation_validation}/`; they are not Azure results.

The [latest actual originals](validation/current/report.json) link these bilingual responses to native judgments.
The initial custom metric's missing numeric-output contract is preserved; only that contract was corrected and completeness evaluated on the same answers. Targets were not resampled.
Earlier full-dev and Optimizer failures remain unchanged in [immutable Git history]({historical_validation}). This tie is not relabeled as v2 improvement or an independent holdout pass.

Screenshots are actual portal observations from their recorded capture times, not new v2 execution or quality evidence.
Optional features, policy/access changes, cost queries, deletion, merges, and publication each require the applicable separate approval.

## Public official sources

{source_table}

## Refresh before the next workshop

Check GA tables, the capability reference, required feature docs, regional/model support, and SDK combinations.
Update the relevant sources and exercises when something actually changes. A learning guide does not need a growing sequence of validation numbers or histories.
