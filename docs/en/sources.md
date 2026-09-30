> **Foundational sources reviewed: 2026-09-29 / Execution APIs rechecked and Contoso edition updated: 2026-09-30, Asia/Seoul.** A review date does not make a document permanently current.

## How we assessed currency

We reviewed Microsoft Learn platform overviews, the capability reference, the GA table, feature-specific documentation, and official SDK examples. Where status descriptions conflicted or covered different scopes, we distinguished the specific APIs, portal experiences, and regions rather than making a broader claim.

At the time of review, the monthly What's new roundup covered **August 2026**. We did not relabel it as a comprehensive list of September releases. Feature-specific documentation, including Content Understanding, contained September updates that were considered separately.

## Changes to keep in mind

| Topic | How this guide treats it |
| --- | --- |
| New portal GA | Separate from the GA status of individual features |
| Scheduled retirement of portal Workflows | State the 2026-12-01 date; use MAF for new implementations |
| Foundry IQ | Some APIs are GA; the portal experience is Preview |
| Foundry RBAC names | Explain both new names and previous Azure AI names |
| Memory / Voice / Agent guardrails / some operations features | Mark as Preview |
| Agent Optimizer | Limited preview according to the GA table |
| Content Understanding | Distinguish 2025-11-01 GA from 2026-06-01-preview |
| SDK combinations | Separate installable base and advanced environments |

## Validation boundaries

### Current automated validation results

**The actual automated-v3 release gate passed:** dev 29/30, independent holdout 9/10, zero critical failures, and calibration 8/8. Original non-critical failures are retained. Human review is identified separately as an optional recommendation.

For Routine, the scheduled response, trace, and disabled state were verified. Optimizer ran successfully after a fix explicitly inherited the model when an instruction-only candidate omitted it. In a separate 20-case Optimizer dev evaluation, baseline and best scores were both 1.0. There was no additional improvement, so the candidate was not promoted. Details are in `validation/current/` and `validation/automated-v3/`.

Current documentation, browser, PDF, and package checks are kept separately in `{documentation_validation}/`. These are documentation checks, not evidence of a new Azure run.

### Earlier v1 results and the current automated path

Earlier validation files remain available in the [original pre-cleanup Git commit]({historical_validation}). Duplicate and older runs were removed from the current file listing; their recorded content and verdicts were not changed.

**The following numbers are the preserved v1 results.** In a new resource group, that run exercised Hosted, Search/IQ, Toolbox/MCP/OpenAPI/Skills, Memory, A2A, native evaluation, Tracing, and an actual OIDC deployment.

| Category | Recorded result |
| --- | --- |
| Implementation complete | This repository alone supports installation, document generation, tests, and packaging |
| Execution complete | New Azure environment; 10 dev and 10 independent holdout cases; traces 10/10; CI deployment and business smoke check |
| Quality gate | **Failed:** holdout 9/10, but safety case hold-08 omitted the required security-policy citation |
| v1 operational limitations | Routine history/output not confirmed; zero new native optimizer candidates |
| Not executed | Voice, CU service, actual fine-tuning, Foundry Local device execution, document-level ACLs, and Teams publishing |

hold-08 rejected the approval bypass but did not cite the required section 4 of `security-policy.md`. Neither the scoring criteria nor the zero-safety-failure rule was relaxed, and instructions were not retuned after inspecting the holdout. The judge calibration controls agreed in 6/6 cases, but that is not equivalent to review by real users.

**Current automated-v3 treats human review as an optional recommendation.** Existing v1/v2 test sets are retained for dev regression; v3 uses a newly sealed holdout and automated retrieval, citation, and tool checks. The overall 90% threshold and zero safety/access failures remain unchanged. See the latest `validation/current/report.json` and `validation/automated-v3/` for v3's actual outcome.

In v1, the Routine was created and dispatch was requested; it was retained in the disabled state. A completed Optimizer service job does not by itself mean a new candidate was generated or quality improved. The original v1 results, CI summary, and operational status remain in the [historical validation archive]({historical_validation}).

**Local contract checks are not cloud execution checks.** Distinguish implementation complete, execution complete, quality passed, blocked, and not executed. The recorded execution targeted only a new dedicated resource group; previous A/B results are not reused as Contoso evidence.

Local checks cover document structure, internal links, synthetic data, tool validation, evaluation gates, SDK contracts, and the web UI. Consult the [execution report](validation/current/report.json) for actual results and unverified scope. Historical evidence remains in the immutable Git commit above; it is not rewritten as a new result.

This material is not an official Microsoft curriculum or a warranty. The scenario, explanations, and diagrams were created for this workshop. The sources below support product facts; the guide does not reproduce their full documentation.

## Public official sources

{source_table}

## Refresh before the next workshop

Recheck the GA table, capability reference, relevant feature documentation, region/model cards, and compatible SDK combinations—in that order. Update changed facts in `content/sources.json`, its English translation, and the affected module together. Updating a source URL alone is not enough: the code, packages, and success criteria must still agree.

## Language editions

English is the default web edition at `index.html`; the original Korean reader is at `index.ko.html`. Both contain the same 25 labs, five reference sections, and evidence boundaries. The language switch keeps the current module and shares browser progress. Some executable inputs and synthetic fixtures intentionally retain their original Korean text so that the published commands and evaluation contracts do not change. This translation is not a new Azure execution or a re-evaluation of historical results.
