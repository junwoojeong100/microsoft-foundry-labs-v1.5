> **Models reason, agents pursue goals, tools provide actual capabilities, and the operations layer verifies and controls that behavior.**

## One-line glossary

| Term | Plain-language meaning | Do not confuse it with |
| --- | --- | --- |
| Foundry resource | A parent Azure resource grouping resources related to security, management, and billing | A single agent |
| Project | A workspace for agents, connections, data, and related work | A Classic hub |
| Lab language profile | `FOUNDRY_LAB_LANGUAGE=en` selects English synthetic inputs; Hosted packages bind their language in `lab-profile.json` | The guide's browser-language switch or a new quality-pass result |
| Model ID | A model name defined by its provider | Your deployment name |
| Model version | A specific version of a model | An agent version |
| Deployment | A model prepared for invocation through an API | A model catalog card |
| Prompt Agent | A managed agent defined by a model, instructions, and tools | A single prompt string |
| Hosted Agent | Your code/framework running in Foundry | Running Python locally |
| Conversation | Dialogue context across multiple turns | Long-term memory |
| Response | The result of one model/agent execution | Only the final text |
| Tool | A capability an agent can call | Permission to make the call |
| Function calling | A pattern in which application functions execute model requests | Running Python inside the model |
| MCP | A common protocol for connecting tools and context | A security policy granting permissions |
| OpenAPI | An HTTP API's input/output contract | A platform that deploys APIs |
| A2A | A protocol for capability invocation/collaboration between agents | A function call within one process |
| Toolbox | A managed tool collection and MCP endpoint | A container that necessarily supports every tool type |
| Skill | A reusable bundle describing how to perform recurring work | A role assignment |
| RAG | Generating answers using retrieved evidence | Training model weights |
| Embedding | Meaning represented as a numeric vector | A natural-language reference answer |
| Hybrid search | Using keyword and vector search together | Multi-agent orchestration |
| Foundry IQ | An enterprise knowledge retrieval layer across multiple sources | A new name for Fabric/Work IQ |
| Memory | Context retained across conversations | A source repository for company policies |
| Routine | Invoking an agent on a schedule or event | Complex orchestration itself |
| Autopilot | A persistent organizational agent, including an agent user account | Every form of automated execution |
| Evaluation | Comparing expected behavior with actual results | Checking whether a string is nonempty |
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
| Enterprise knowledge from multiple sources | Consider Foundry IQ | ACLs, freshness, and observability |
| One API call | A function/OpenAPI | Toolbox for reuse |
| Custom execution code | Hosted Agent | CI/CD, scale, and operations |
| A simple periodic invocation | Routine | A framework for complex branching |
| A speech-based experience | Consider a Voice Agent | Voice quality, sessions, and tools |
| Quality checks before deployment | Evaluation with a fixed dataset | Sampled evaluation in production |
| Control of AI assets across teams | RBAC, policies, and Control Plane | Gateway and security/information-protection integrations |

## Status labels in this guide

**GA** refers to the verified scope of that capability. **Partial GA / mixed** means that API, portal, and individual feature statuses differ. **Preview** is treated as an optional nonproduction lab. **Conditional lab** means execution is allowed only when the additional resources, administrators, and licenses are ready. **Design/reference** does not count toward actual cloud success.
