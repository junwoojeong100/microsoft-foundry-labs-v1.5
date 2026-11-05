# Sample file guide

**Core portal labs do not run these scripts.** Current code-required [L12](../docs/en/14-hosted.md) and [L13–L14](../docs/en/15-multiagent.md) use only the explicitly named commands. Other samples are preserved developer references, not additional portal-course steps.

## Before you run anything

- Run current code labs from the complete ZIP's repository root. Hosted uses `.venv-hosted`; MAF uses `.venv-maf`. Their project SDK pins conflict; never combine their requirements.
- `doctor`, `validate-data`, and `tools` inspect the local setup, synthetic data, and functions. For example, `python samples/workshop.py tools` calculates a draft locally without network access or an order.
- Before connecting to Microsoft Foundry or Microsoft Azure, verify the lab's scope and the approved project. Several scripts are plan-only without `--live`, but `--live` is not a universal safety switch. Follow command-specific requirements such as `--confirm`, a receipt, or per-tool approval.
- The data represents synthetic Contoso purchasing scenarios. These samples do not place orders, make payments, or grant business approval. `results/` can contain personal execution results and receipts; do not share or commit them.

## Executable files: current labs versus preserved references

| File | Purpose | Guide location and boundary |
| --- | --- | --- |
| [a2a_lab.py](a2a_lab.py) | Delegates a task to a remote agent through A2A. | Reference only. L14 runs in-process SDK handoff, not this remote protocol. |
| [first_response.py](first_response.py) | Shows one Responses API request in a short, focused script. | Reference only; current L03 uses portal Chat. Default plan, one call with approved `--live`. |
| [hosted_client.py](hosted_client.py) | Invokes or evaluates a local or deployed Hosted Agent and preserves execution evidence. | L12. The agent can call real Microsoft Azure services even with `--local`, so `--live` is required. It does not delete sessions. Labs use `invoke`; `evaluate` runs the maintainer-only validation suites, which are not in the ZIP. |
| [instruction_evaluation.py](instruction_evaluation.py) | Evaluates already-collected v1/v2 answers once in Microsoft Foundry. | Reference only; current L08 uses portal JSONL upload. Does not reinvoke the target agent. |
| [instruction_lab.py](instruction_lab.py) | Collects a bounded v1/v2 instruction comparison on development data. | Reference only; no retries or holdout use. |
| [instruction_prompt_agent_lab.py](instruction_prompt_agent_lab.py) | Collects v1/v2 answers through version-pinned Prompt Agents. | Reference only, not current L08. Approved `--live` can create versions and model calls. |
| [inventory_api.py](inventory_api.py) | Local read-only inventory HTTP server; no drafting endpoint. | Reference only, not current L07. Loopback only; no public exposure/tunnel. |
| [local_lab.py](local_lab.py) | Inspects or runs a Foundry Local device exercise. | Reference only. `--local` executes device work; `--allow-download` permits model/provider downloads. No Microsoft Azure calls. |
| [memory_lab.py](memory_lab.py) | Stores, retrieves, verifies, and deletes a synthetic preference item. | Reference only; L15's portal observation does not execute this CRUD path. Item deletion is not store/group deletion. |
| [model_capacity.py](model_capacity.py) | Plans/checks/changes/tests model throughput. | Current MAF imports its read-only readiness guard. CLI capacity-changing/testing subcommands are reference-only and require separate scoped approval. |
| [multi_agent.py](multi_agent.py) | Executes real MAF sequential, concurrent, group-chat, and handoff builders. | **Current L13–L14.** Default plan; `--offline` runs network-blocked fixed fixtures, approved `--live` uses a real model. Never remote A2A. |
| [mcp_server.py](mcp_server.py) | Local stdio synthetic inventory/draft tools. | Reference only; current L07 uses remote read-only Learn MCP. No external business action. |
| [optimizer_lab.py](optimizer_lab.py) | Starts/monitors bounded development-data optimization. | Reference only, no automatic apply/deploy. Default maintainer-only suite is not in the ZIP or any current lab. |
| [prepare_practice.py](prepare_practice.py) | Copies an intentionally flawed local exercise to a new folder. | Reference only; current L17/L18 use decision tables, not this helper. No Microsoft Azure calls. |
| [prepare_tuning.py](prepare_tuning.py) | Generates small synthetic SFT-format data. | Reference only; no training submission/model changes. |
| [routine_lab.py](routine_lab.py) | Bounded Routine creation, dispatch, inspection, and stop. | Reference only; current L16 cancels before submission. No Routine/group deletion. |
| [search_lab.py](search_lab.py) | Canonical policy corpus and Azure AI Search/Foundry IQ retrieval. | **Current L12 optional initialization** on existing approved Search. Not L11's portal steps. Data writes/embedding charges require approval and `--live`. |
| [toolbox_lab.py](toolbox_lab.py) | MCP/OpenAPI/Toolbox/Skill setup, inspection, and calls. | Reference only, not current L07. `--approve-tool` approves one exact tool call. |
| [trace_lab.py](trace_lab.py) | Correlates saved IDs with Application Insights traces. | Reference only; current L10 uses portal Traces. Missing records remain missing. |
| [workshop.py](workshop.py) | Integrated functions/model/agent/File search/capstone runner. | Preserved reference implementation, **not current L02–L06 steps**. Do not execute it just to finish the portal course. |

### `workshop.py` command groups

| Command | Behavior |
| --- | --- |
| `doctor`, `validate-data`, `tools` | Inspect local setup, synthetic data, and function behavior. No network or Microsoft Azure calls. |
| `read-result --input ...` | Reads saved answers, tool results, and citations locally. It makes no new Microsoft Azure call and does not grade quality. |
| `score --input ...` | Applies the rubric to complete, human-reviewed records. Passing is not production certification. |
| `model`, `agent`, `rag`, `capstone`, `evaluate` | Print a plan unless `--live` is specified. With `--live`, they can send requests to the configured Microsoft Foundry project and create resources; charges may apply. |
| `cleanup --receipt ... --confirm ... --live` | Deletes only resources recorded in the receipt. The confirmation must exactly match that receipt's run ID. Recheck the lab's ownership scope and cleanup instructions before running it. |

## Read terminal commands as code flows

`python samples/file.py subcommand --option value` reads as **interpreter → file → operation → input**. The current L12–L14 walkthroughs explain each command individually. Microsoft Azure requests/resource changes need separate approval, matching receipts, and the stated bounds.

| Lab and representative command | Input → code flow → output | What to change or inspect first |
| --- | --- | --- |
| L12 `search_lab.py initialize` | Canonical synthetic sections → one embedding batch → exact index/knowledge source/base → private Search result | Existing dedicated Search and compatible embedding only; not an arbitrary portal index. |
| L12 `hosted_client.py` | Question/agent version → local or deployed Hosted Agent → saved execution evidence | `--local` can still make real Microsoft Azure calls; check the `--live` requirement. |
| L13/L14 `multi_agent.py --offline` | Mode/case/policy → actual SDK with fixed synthetic backend → transfer/tool/termination evidence | Fixture responses, usage, and fixed policy routing are not model quality, billing, or Microsoft Azure evidence. |
| L13/L14 `multi_agent.py --live` | Verified receipt/TPM/RPM → actual SDK with existing model → original responses/IDs/usage | Local orchestration with Microsoft Azure inference, not Hosted orchestration or remote A2A. |
| Reference `workshop.py tools` | SKU/quantity → local validation/calculation → approval-pending draft | No network/order; not a current core-course step. |

## Distinguish `scripts/` commands from lab code

`python scripts/...` usually runs setup/operations automation. Current L12–L14 explicitly distinguish offline packaging, read-only adoption, data writes, paid deployment, access changes, and invocation.

| Script files | Purpose |
| --- | --- |
| `scripts/adopt_portal.py` | Current L12/L13 read-only bridge from existing portal resources to a private CLI receipt: five reads, or seven with Search/embedding. No provisioning/roles/model calls; no receipt overwrite. |
| `scripts/azure_environment.py` | Preserved CLI provisioning reference, **not current L01/L11**. Do not duplicate existing portal resources. `env --write` copies receipt settings locally without Microsoft Azure calls. |
| `scripts/build_hosted.py`, `run_hosted_local.py`, `configure_hosted.py`, `runtime_roles.py` | Build, run, configure, and set permissions for a Hosted Agent. These are not Python syntax exercises. |
| `scripts/check_sdk.py` | Offline installed-SDK contracts; `--advanced` uses the real MAF fixture. Not live Microsoft Azure validation. |
| `scripts/stop_sessions.py`, `operations_status.py`, `cost_status.py` | Stop recorded sessions or inspect the owned environment and its costs. Follow L19. |
| `scripts/build_guide.py`, `check_guide.py`, `package_guide.py` | Maintainer document generation/validation/packaging, not a learner L18 command or agent deployment. |

## Shared support code and contracts

These files are usually imported by the lab scripts rather than run directly.

| File | Purpose |
| --- | --- |
| [business_checks.py](business_checks.py) | Deterministically checks the structure and business boundaries of actual execution evidence, separately from model-based semantic evaluation. |
| [cloud.py](cloud.py) | Shared Microsoft Azure connection and request-transport code for optional live labs. |
| [evidence.py](evidence.py) | Records bounded execution evidence, redacts sensitive values, and enforces request/time budgets. |
| [evaluation_data.py](evaluation_data.py) | Handles evaluation-data versions and splits; development-data loading does not open sealed holdout data. |
| [evaluation_lab.py](evaluation_lab.py) | Native-evaluation helpers imported by the preserved `instruction_evaluation.py`. `prepare`, `calibrate`, and `run --suite` drive maintainer live-validation suites, not current L08. |
| [grounding.py](grounding.py) | Selects and validates citations against actually retrieved sources; it does not invent references. |
| [hosted_runtime.py](hosted_runtime.py) | One bounded purchasing-assistant turn shared by local and Hosted invocations. |
| [lab_cli.py](lab_cli.py) | Runs a lab entry point and shows an expected learner error as one `ERROR:` line (exit code 2) instead of a traceback; set `FOUNDRY_LAB_DEBUG=1` to see the traceback. |
| [lab_profile.py](lab_profile.py) | Uses `FOUNDRY_LAB_LANGUAGE` to select the Korean or English synthetic corpus without mixing profiles. |
| [maf_fixture.py](maf_fixture.py) | Actual SDK builders with a fixed synthetic backend, blocked sockets/DNS, synthetic usage, and explicitly fixed policy routing. Shared by current MAF labs/tests/SDK checks. |
| [original_files.py](original_files.py) | Keeps one-shot result originals safe: a run that failed before any Azure change keeps its record as `…failed-<time>.json` so the same command can be run again. |
| [request_contract.py](request_contract.py) | Checks that draft-tool arguments are grounded in the user's explicit request and rejects invented quantities. |
| [inventory.openapi.json](inventory.openapi.json) | Preserved local inventory API contract, not current L07. `127.0.0.1` cannot be reached directly from Microsoft Foundry. |

## Maintainer-only validation assets

The Microsoft Azure live-validation lineage stays in the repository for maintainers, but is **not shipped in the ZIP** or used by a lab: suites v2–v5, their authoring/live-CI scripts, and dependent tests. `content/maintainer-only.json` is the single list. Current L08 portal inputs derive from `data/evaluation/instruction-comparison.json`. Neither Hosted `invoke` nor MAF fixture practice opens the maintainer evaluation/holdout suites.

## Where related files live

- `data/` contains policies, prompts, synthetic inventory, and evaluation inputs. The default Korean profile and English profile are separate.
- `.env.example` lists setting names. Keep personal settings in `.env` and do not commit it.
- `results/` is the private location for execution outputs, receipts, and evidence. `completed` means execution finished, not that quality passed; do not record local or fixture checks as Microsoft Azure execution evidence.
- `hosted/`, `scripts/`, and `infra/` contain Hosted services, build/operations scripts, and infrastructure definitions; their respective labs explain those files.
