# Sample file guide

`samples/` contains both executable lab scripts and support code shared by those scripts. You do not need to run every file. Use only the file and command named by the corresponding lab.

## Before you run anything

- Unless a lab says otherwise, run commands from the repository root after extracting the workshop ZIP. Follow each L00–L19 lab's Python environment and working-directory instructions.
- `doctor`, `validate-data`, and `tools` inspect the local setup, synthetic data, and functions. For example, `python samples/workshop.py tools` calculates a draft locally without network access or an order.
- Before connecting to Foundry or Azure, verify the lab's scope and the approved project. Several scripts are plan-only without `--live`, but `--live` is not a universal safety switch. Follow command-specific requirements such as `--confirm`, a receipt, or per-tool approval.
- The data represents synthetic Contoso purchasing scenarios. These samples do not place orders, make payments, or grant business approval. `results/` can contain personal execution results and receipts; do not share or commit them.

## Files run directly in the labs

| File | Purpose | Guide location and boundary |
| --- | --- | --- |
| [a2a_lab.py](a2a_lab.py) | Delegates a task to a remote agent through A2A. | Optional L14 extension. This differs from the in-process orchestration in `multi_agent.py`. |
| [evaluation_lab.py](evaluation_lab.py) | Prepares, calibrates, and runs fixed evaluation data in Foundry. | Evaluation extension. Check the data split and each command's `--live` requirement. |
| [first_response.py](first_response.py) | Shows one Responses API request in a short, focused script. | L03's first coding exercise. It prints a plan by default and makes one call only with `--live`. |
| [hosted_client.py](hosted_client.py) | Invokes or evaluates a local or deployed Hosted Agent and preserves execution evidence. | L12. The agent can call real Azure services even with `--local`, so `--live` is required. It does not delete sessions. |
| [instruction_evaluation.py](instruction_evaluation.py) | Evaluates already-collected v1/v2 answers once in Foundry. | Optional L08 path. It does not invoke the target agent again. |
| [instruction_lab.py](instruction_lab.py) | Collects a bounded v1/v2 instruction comparison on development data. | Optional comparison script. It does not retry or use the holdout split. |
| [instruction_prompt_agent_lab.py](instruction_prompt_agent_lab.py) | Collects v1/v2 answers through version-pinned Prompt Agents. | Optional L08 path. `--live` can create agent versions and make model calls. |
| [inventory_api.py](inventory_api.py) | Local read-only inventory HTTP server; no drafting endpoint. | L07. Loopback only; do not expose or tunnel it. |
| [local_lab.py](local_lab.py) | Inspects or runs the Foundry Local device exercise. | Inspection is the default. `--local` allows actual local device work; `--allow-download` permits model and execution-provider downloads. It does not call Azure. |
| [memory_lab.py](memory_lab.py) | Demonstrates storing, retrieving, verifying, and deleting a synthetic preference item. | Optional L15 lab. Deleting an item does not delete the Memory store or resource group. |
| [model_capacity.py](model_capacity.py) | Plans throughput by learner count and role, then checks, changes, or tests capacity. | Optional L02/L13 path. Azure capacity changes and tests require explicit `--live` and ownership-scope checks. |
| [multi_agent.py](multi_agent.py) | Runs Agent Framework sequential, concurrent, group-chat, and handoff patterns. | L13–L14. It prints a plan by default; actual model execution requires `--live`. This is not remote A2A. |
| [mcp_server.py](mcp_server.py) | Local stdio MCP server for synthetic inventory lookup and purchase-draft calculation. | L07. It uses synthetic data and performs no external business action. |
| [optimizer_lab.py](optimizer_lab.py) | Starts and monitors a bounded Foundry Agent Optimizer job on development data. | Optional extension. It does not automatically apply or deploy a candidate. |
| [prepare_practice.py](prepare_practice.py) | Copies an intentionally flawed local exercise into a new learner folder. | L17/L18 design-exercise helper. It performs no Azure operations. |
| [prepare_tuning.py](prepare_tuning.py) | Generates a small synthetic SFT-format exercise dataset. | Optional reference tool. It does not submit a training job or change a model. |
| [routine_lab.py](routine_lab.py) | Exercises bounded Routine creation, dispatch, status checks, and stopping. | L16. Follow the stop procedure; the script does not delete a Routine or resource group. |
| [search_lab.py](search_lab.py) | Works with the synthetic policy corpus and Search/Foundry IQ retrieval paths. | L11. `corpus` is local; Azure index initialization and query operations require explicit `--live`. |
| [toolbox_lab.py](toolbox_lab.py) | Exercises setup, inspection, and calls for MCP, OpenAPI, Toolbox, and Skill tools. | L07 and optional extensions. `--approve-tool` names the tool for that one call. |
| [trace_lab.py](trace_lab.py) | Correlates saved response IDs with Application Insights traces. | Optional L10 path. Missing trace records stay missing; they are not inferred as success. |
| [workshop.py](workshop.py) | Integrated runner for local functions, model calls, agents, File search, and the capstone. | L02–L06. Treat it as the complete reference; start learning with the smaller `first_response.py`. |

### `workshop.py` command groups

| Command | Behavior |
| --- | --- |
| `doctor`, `validate-data`, `tools` | Inspect local setup, synthetic data, and function behavior. No network or Azure calls. |
| `read-result --input ...` | Reads saved answers, tool results, and citations locally. It makes no new Azure call and does not grade quality. |
| `score --input ...` | Applies the rubric to complete, human-reviewed records. Passing is not production certification. |
| `model`, `agent`, `rag`, `capstone`, `evaluate` | Print a plan unless `--live` is specified. With `--live`, they can send requests to the configured Foundry project and create resources; charges may apply. |
| `cleanup --receipt ... --confirm ... --live` | Deletes only resources recorded in the receipt. The confirmation must exactly match that receipt's run ID. Recheck the lab's ownership scope and cleanup instructions before running it. |

## Read terminal commands as code flows

`python samples/file.py subcommand --option value` reads as **interpreter → file → operation → input**. Alongside each lab's command walkthrough, use this map to see what the command reads, what it runs, and where the result goes. Start by changing one input in a local or plan-only path. Azure requests and resource changes must follow the lab's approval and `--live` requirements.

| Lab and representative command | Input → code flow → output | What to change or inspect first |
| --- | --- | --- |
| L03 `first_response.py` | Question → configuration/authentication → one Responses API call → answer and `response_id` | Change `--query` and inspect plan output first. |
| L06 `workshop.py tools` | SKU/quantity → stock lookup → input/stock validation → approval-pending draft JSON | Change one SKU or quantity and compare valid and error results. No Azure call. |
| L03–L06 `workshop.py model/agent/rag/capstone` | Question, prompt, policies, and tools → model/retrieval/dispatcher → response JSONL and resource receipt | Without `--live`, inspect the plan. Use `read-result` to review saved integrated output. |
| L02/L13 `model_capacity.py` | Learner count/roles → throughput plan → plan output; live subcommands check, change, or test capacity | Compare `plan --learners 1` with another count. `apply` changes resources. |
| L07 `inventory_api.py` + `toolbox_lab.py` | Local HTTP/MCP server → one approved tool call → synthetic stock/draft result | Select one local tool and identify it with `--approve-tool`. |
| L08 `instruction_prompt_agent_lab.py` → `instruction_evaluation.py` | Fixed questions and v1/v2 → saved answer file → Foundry evaluation of that same file | Keep response JSON and evaluation JSON distinct. Evaluation does not call the target agent again. |
| L10 `trace_lab.py` | Saved response IDs + Application Insights identifiers → trace correlation query → report | Verify the local input file first. Remote queries require `--live`. |
| L11 `search_lab.py` | Synthetic policy corpus → index/retrieval mode → search results and evidence | `corpus` is local. Check the `--live` boundary for indexing and queries. |
| L12 `hosted_client.py` | Question/agent version → local or deployed Hosted Agent → saved execution evidence | `--local` can still make real Azure calls; check the `--live` requirement. |
| L13/L14 `multi_agent.py` | `--mode` → local SDK stages/handoff → evidence | Compare actual inputs/outputs. Remote `a2a_lab.py` is separate reference code, not these labs' execution scope. |
| L15/L16 `memory_lab.py` and `routine_lab.py` | Subcommand/receipt → selected memory item or Routine operation → state/receipt | Verify target IDs and receipts first. Stop a Routine as directed. |
| Optional `prepare_practice.py`, `prepare_tuning.py`, `local_lab.py`, `optimizer_lab.py` | Exercise type/local option/dev input → copy, device exercise, or optimization → folder/device/job output | Run only the path you need. Check download and live-operation conditions first. |

## Distinguish `scripts/` commands from lab code

`python scripts/...` usually runs setup or operations automation, not a small coding exercise. Read the ownership scope and approval instructions in L01/L10/L12 before creating resources or changing access.

| Script files | Purpose |
| --- | --- |
| `scripts/azure_environment.py` | You create your dedicated environment/models/roles/telemetry in L01 and Search in L11. Creation/changes require `--live`, scoped permissions, and cost approval. |
| `scripts/build_hosted.py`, `run_hosted_local.py`, `configure_hosted.py`, `runtime_roles.py` | Build, run, configure, and set permissions for a Hosted Agent. These are not Python syntax exercises. |
| `scripts/stop_sessions.py`, `operations_status.py`, `cost_status.py` | Stop recorded sessions or inspect the owned environment and its costs. Follow L19. |
| `scripts/build_guide.py`, `check_guide.py`, `package_guide.py` | Guide source generation/validation/packaging, referenced in L18; not AI agent deployment or live Foundry execution. |

## Shared support code and contracts

These files are usually imported by the lab scripts rather than run directly.

| File | Purpose |
| --- | --- |
| [business_checks.py](business_checks.py) | Deterministically checks the structure and business boundaries of actual execution evidence, separately from model-based semantic evaluation. |
| [cloud.py](cloud.py) | Shared Azure connection and request-transport code for optional live labs. |
| [evidence.py](evidence.py) | Records bounded execution evidence, redacts sensitive values, and enforces request/time budgets. |
| [evaluation_data.py](evaluation_data.py) | Handles evaluation-data versions and splits; development-data loading does not open sealed holdout data. |
| [grounding.py](grounding.py) | Selects and validates citations against actually retrieved sources; it does not invent references. |
| [hosted_runtime.py](hosted_runtime.py) | One bounded purchasing-assistant turn shared by local and Hosted invocations. |
| [lab_profile.py](lab_profile.py) | Uses `FOUNDRY_LAB_LANGUAGE` to select the Korean or English synthetic corpus without mixing profiles. |
| [request_contract.py](request_contract.py) | Checks that draft-tool arguments are grounded in the user's explicit request and rejects invented quantities. |
| [inventory.openapi.json](inventory.openapi.json) | OpenAPI contract for the L07 local inventory API. Its server is `127.0.0.1` and cannot be reached directly from Foundry. |

## Where related files live

- `data/` contains policies, prompts, synthetic inventory, and evaluation inputs. The default Korean profile and English profile are separate.
- `.env.example` lists setting names. Keep personal settings in `.env` and do not commit it.
- `results/` is the private location for execution outputs, receipts, and evidence. `completed` means execution finished, not that quality passed; do not record local or fixture checks as Azure execution evidence.
- `hosted/`, `scripts/`, and `infra/` contain Hosted services, build/operations scripts, and infrastructure definitions; their respective labs explain those files.
