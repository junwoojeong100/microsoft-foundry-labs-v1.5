> **Models reason, agents pursue goals, tools provide actual capabilities, and the operations layer verifies and controls that behavior.**

Use the product names **Microsoft Azure** and **Microsoft Foundry**. Commands, API identifiers, and actual menu/role names such as `New Foundry`, `Foundry User`, and `Azure AI User` retain their literal spelling so you can match the screen.

## Getting started and PC setup

| Term | Plain-language meaning | Do not confuse it with |
| --- | --- | --- |
| Microsoft Azure | Microsoft's cloud platform | A program running only on your PC |
| Tenant / Microsoft Entra ID | An organizational account boundary / identity service | The subscription used for billing |
| Subscription / Resource group | A billing/management scope / a collection of resources within it | A Microsoft Foundry project |
| Portal / Playground | A management website / a screen for trying inputs and responses | The guide website you are reading |
| Endpoint | The service address used by code | Sign-in permission or an API key |
| CLI / Terminal / SDK | A command-line tool / its input window / libraries used by code | One application that provides all three |
| `.env` / venv | A project settings file / a folder isolating Python packages | The same environment feature |
| JSON / JSONL | Named data values / one JSON record per line | Commands to execute in a terminal |
| `true` / `false` / `null` | True / false / no value; `order_submitted=false` means no order was submitted | Treating null as success, zero cost, or no problem |
| Receipt | A record of resource IDs and the lab's ownership scope | A payment receipt or deletion approval |
| RBAC / Scope | Role-based permissions / the boundary where they apply | Full access obtained by signing in |
| Microsoft Foundry resource | A parent Microsoft Azure resource grouping resources related to security, management, and billing | A single agent |
| Project | A workspace for agents, connections, data, and related work | A Classic hub |
| Lab language profile | `FOUNDRY_LAB_LANGUAGE=en` selects English synthetic inputs; Hosted packages bind their language in `lab-profile.json` | The guide's browser-language switch or a new quality-pass result |

## Models, documents, and tools

| Term | Plain-language meaning | Do not confuse it with |
| --- | --- | --- |
| Model ID | A model name defined by its provider | Your deployment name |
| Model version | A specific version of a model | An agent version |
| Deployment | A model prepared for invocation through an API | A model catalog card |
| Prompt / Instructions | Input for this request / common instructions for the agent | Actual permissions or company documents |
| Token / Latency | A unit of model input/output processing / time to an answer | Token counts being identical to words, characters, or a currency amount |
| Prompt Agent | A managed agent defined by a model, instructions, and tools | A single prompt string |
| Hosted Agent | Your code/framework running in Microsoft Foundry | Running Python locally |
| Conversation | Dialogue context across multiple turns | Long-term memory |
| Response | The result of one model/agent execution | Only the final text |
| Tool | A capability an agent can call | Permission to make the call |
| SKU / Schema | Here, an item code such as `NB-14` / agreed input and output names and types | A Microsoft Azure deployment SKU denotes a service type, a different use of the term |
| Function calling | A pattern in which application functions execute model requests | Running Python inside the model |
| MCP | A common protocol for connecting tools and context | A security policy granting permissions |
| OpenAPI | An HTTP API's input/output contract | A platform that deploys APIs |
| A2A | A protocol for capability invocation/collaboration between agents | A function call within one process |
| Toolbox | A managed tool collection and MCP endpoint | A container that necessarily supports every tool type |
| Skill | A reusable bundle describing how to perform recurring work | A role assignment |
| RAG | Generating answers using retrieved evidence | Training model weights |
| Vector store / Indexing | A document store for retrieval / processing documents to make them searchable | Upload completion being the same as search readiness |
| Citation | A connection to actual evidence supporting a claim | A model-written filename alone proving the claim |
| Embedding | Meaning represented as a numeric vector | A natural-language reference answer |
| Hybrid search | Using keyword and vector search together | Multi-agent orchestration |
| Microsoft Foundry IQ | An enterprise knowledge retrieval layer across multiple sources | A new name for Fabric/Work IQ |

## Evaluation, operations, and advanced topics

| Term | Plain-language meaning | Do not confuse it with |
| --- | --- | --- |
| Memory | Context retained across conversations | A source repository for company policies |
| Routine | Invoking an agent on a schedule or event | Complex orchestration itself |
| Autopilot | A persistent organizational agent, including an agent user account | Every form of automated execution |
| Evaluation | Comparing expected behavior with actual results | Checking whether a string is nonempty |
| Judge / Native evaluation | A grading model / evaluation run by Microsoft Foundry's service | The answer-generating model or an infallible judgment |
| Dev / Holdout | Practice data used while improving / separate exam data excluded from improvement | A guarantee that every file named `holdout` is unexposed |
| Groundedness | The degree to which supplied evidence supports an answer | Truthfulness about every fact in the world |
| Trace / Span | The full execution path / an individual operation within it | Permission to store unlimited raw content |
| Guardrail | A set of risk detection and response rules | Business-system authentication or approval |
| Control Plane | A fleet-wide management, observation, and policy interface | The runtime itself |
| AI Gateway | A layer applying request policies, routing, and limits | Automatic resolution of every security problem |
| GA / Preview | Support status and usage conditions | Availability in every region |
| Quota / Capacity | Allowed usage / actually available capacity | A billing cap |
| SFT / DPO / RFT | Model improvement based on examples / preferences / rewards | Adding documents to retrieval |
| OIDC | A way for CI and other callers to authenticate through short-lived trust | A long-lived secret string |
| CMK | A customer-managed encryption key | Isolation of every capability and every path |

## Choose the smallest solution

| What you need now | Smallest starting point | Next step |
| --- | --- | --- |
| One summary | A model call | An agent if recurring work emerges |
| Answers from 3 files | File search | Search if you need index control |
| Enterprise knowledge from multiple sources | Consider Microsoft Foundry IQ | ACLs, freshness, and observability |
| One API call | A function/OpenAPI | Toolbox for reuse |
| Custom execution code | Hosted Agent | CI/CD, scale, and operations |
| A simple periodic invocation | Routine | A framework for complex branching |
| A speech-based experience | Consider a Voice Agent | Voice quality, sessions, and tools |
| Quality checks before deployment | Evaluation with a fixed dataset | Sampled evaluation in production |
| Control of AI assets across teams | RBAC, policies, and Control Plane | Gateway and security/information-protection integrations |

## Status labels in this guide

**GA** refers to the verified capability scope. **Partial GA / mixed** means API, portal, and feature statuses differ. Check support before using **Preview** in nonproduction. **Conditional lab** means additional resources, permissions, and licensing are required. **Design/reference** is not actual cloud success.
