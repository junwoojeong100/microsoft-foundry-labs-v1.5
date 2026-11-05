> **Before using a feature:** Check official documentation for supported APIs/SDKs, regions/models, permissions, and licenses.

## Use the official documentation

Use Microsoft Learn overviews and the capability reference for concepts, and feature documentation and GA tables for availability.
Core work uses Azure portal/Foundry portal; only code-required L12–L14 use terminals/SDKs. SDK/API support does not establish portal controls. A GA portal does not mean every individual feature is GA.

## Feature-specific conditions

| Topic | Treatment |
| --- | --- |
| New portal GA | Separate from individual feature GA |
| Scheduled portal Workflows retirement | 2026-12-01; consider Microsoft Agent Framework for new implementations |
| Foundry IQ | Some APIs GA, portal experience Preview |
| Memory, Voice, Agent guardrails | Keep API-specific Preview/access conditions explicit |
| Agent optimizer | Limited preview, optional exercise |
| Azure Content Understanding in Foundry Tools | Distinguish 2025-11-01 GA and 2026-06-01-preview |
| Advanced SDK environments | L12 Hosted pins `azure-ai-projects 2.7.0`; L13–L14 MAF pin `azure-ai-projects 2.6.0` and `agent-framework-foundry 1.13.1`. Separate environments; core portal work needs neither |

## Official document list

{source_table}

## Refresh before the next workshop

Check GA tables, the capability reference, feature docs, regional/model support, and portal availability. These cloud experiences roll out incrementally.
If unavailable, consult the owner and record inspection/not run. Do not bypass with hidden APIs/CLI or change security/spending scope. Instructions and recorded coverage differ; original review dates, screenshots, and validation are not relabeled as new execution.
