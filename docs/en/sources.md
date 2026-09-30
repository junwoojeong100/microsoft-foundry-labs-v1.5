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

### Current English Azure validation

**The English release-quality gate failed.** In a new dedicated resource group, the core learning evaluation passed 10/10 with calibration 6/6. The fixed Hosted candidate passed the 30-case dev gate at 29/30 with no critical failures. Its new independent English holdout then passed **7/10, with one critical safety-evidence failure**, despite calibration 8/8 and complete execution of all ten cases. A successful deployment, a completed evaluation job, and a passing quality gate are different outcomes.

The minimum pass rate remains 90%, with zero safety/access failures. Neither the questions, citation requirements, evaluator, nor threshold was weakened. The frozen candidate was not changed or rerun after inspecting the holdout. Human review remains optional guidance and was not recorded as completed.

| English result | What the evidence establishes |
| --- | --- |
| New environment | A separately owned resource group, Foundry project, online models, Search Basic, telemetry, and a branch-restricted OIDC identity |
| Core labs | Actual English model and Prompt Agent responses, File search over English policies, inventory lookup, and draft-only purchase tools |
| Advanced integrations | Actual keyword/hybrid/GA-minimal IQ retrieval, both Hosted protocols, Toolbox/MCP/managed-identity OpenAPI/Skills, MAF and A2A |
| Memory and Routine | An English synthetic preference, scope isolation, and deletion of that item; a one-shot scheduled English response correlated to a trace, then disabled |
| Trace correlation | All ten holdout request trace IDs found; the bounded combined query also observed seven model-response spans, not ten |
| Final holdout | 7/10; one critical safety citation-evidence failure; **not release-approved** |
| Remaining conditions | Voice, Content Understanding service calls, actual fine-tuning, Foundry Local device inference, document-level ACLs, and Teams publishing remain conditional or not executed |

The initial English dev attempt stopped after 23 completed cases. A sequential request first called the stock tool, but the runtime moved to an answer while a draft was still pending. Actual server evidence showed repeated JSON messages and an output-limit failure. Before the holdout, the controller was corrected to allow at most two tool rounds and then one separate, tool-free answer built from completed evidence. Duplicate drafts are rejected with provenance, and the remote timeout now matches the existing bounded server window. The original failed attempt remains under `validation/english/attempts/`; it is not relabeled as a pass.

The final failures are also retained. Two clarification/validation cases triggered a read-only stock lookup forbidden by their frozen case contracts; one response discussed an unacceptable quantity-mismatch workaround. The safety case refused the injected approval/payment claim but omitted required policy evidence. No actual approval, order, payment, or stock mutation occurred.

See the [English execution report](validation/english/current/report.json), [quality result](validation/english/automated-v3/quality.json), and [original release summary](validation/english/automated-v3/ci-release.json). The separate dev-only Optimizer job reached its 1200-second limit and was canceled; no completed improvement or promotion is claimed. Final closeout stopped five discovered optimizer baseline/candidate sessions and verified zero active work across the project. This does not repair or replace the held-out verdict.

The resource-group screen also preserves an inherited organizational diagnostic-policy deployment failure: its external governance log workspace was missing. The lab's own foundation and observability deployments succeeded. No shared governance resource was changed to hide that failure.

Resources are retained until explicit deletion approval. Stopping sessions and schedules does not stop all costs: Search Basic and retained storage/logs can continue charging. An empty Cost Management result means billing has not yet been reported, **not** that the run cost zero.

Current documentation, browser, PDF, and package checks are kept separately in `{documentation_validation}/`. These are documentation checks, not evidence of a new Azure run.

### Preserved Korean runs and earlier v1 results

The original Korean automated-v3 gate passed at dev 29/30 and holdout 9/10, with zero critical failures and calibration 8/8. Its Routine and dev-only Optimizer records remain unchanged in `validation/current/` and `validation/automated-v3/`. **Those are not results for the new English environment.**

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

**The Korean automated-v3 path treats human review as an optional recommendation.** Its v1/v2 test sets are retained for dev regression; its v3 uses a separately sealed holdout and automated retrieval, citation, and tool checks. The overall 90% threshold and zero safety/access failures remain unchanged. Its original outcome is in `validation/current/report.json` and `validation/automated-v3/`; the English outcome is in the separate paths above.

In v1, the Routine was created and dispatch was requested; it was retained in the disabled state. A completed Optimizer service job does not by itself mean a new candidate was generated or quality improved. The original v1 results, CI summary, and operational status remain in the [historical validation archive]({historical_validation}).

**Local contract checks are not cloud execution checks.** Distinguish implementation complete, execution complete, quality passed, blocked, and not executed. The recorded execution targeted only a new dedicated resource group; previous A/B results are not reused as Contoso evidence.

Local checks cover document structure, internal links, synthetic data, tool validation, evaluation gates, SDK contracts, and the web UI. Consult the [English execution report](validation/english/current/report.json) for actual results and unverified scope. Historical evidence remains in the immutable Git commit above; it is not rewritten as a new result.

This material is not an official Microsoft curriculum or a warranty. The scenario, explanations, and diagrams were created for this workshop. The sources below support product facts; the guide does not reproduce their full documentation.

## Public official sources

{source_table}

## Refresh before the next workshop

Recheck the GA table, capability reference, relevant feature documentation, region/model cards, and compatible SDK combinations—in that order. Update changed facts in `content/sources.json`, its English translation, and the affected module together. Updating a source URL alone is not enough: the code, packages, and success criteria must still agree.

## Language editions

English is the default web edition at `index.html`; the original Korean reader is at `index.ko.html`. Both contain the same 25 labs and five reference sections. The language switch keeps the current module and shares browser progress. English execution explicitly selects `FOUNDRY_LAB_LANGUAGE=en` and the synthetic `data/en/` profile in an isolated checkout. Korean remains the default runtime profile for existing commands. English portal images are genuine new captures from the English environment; the original Korean images and historical evidence are preserved separately.
