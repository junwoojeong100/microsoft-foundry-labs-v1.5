> **What you will build:** One request to your model, with its actual answer, status, and response ID.

<div class="lab-brief" markdown="1">

**Format:** Compare portal settings with direct Python SDK code, then send the request through one path.

**Start here:** Find L02's `contoso-chat` in the Playground Model selector and Python `model` argument.

**What to check:** A completed answer/ID and no fabricated company policy.

</div>

## Objectives

**Understand the smallest model call.** There is no agent, document retrieval, or function tool yet. Read how the code and screen settings relate before executing.

## Concepts and lab map

**What you will try:** Send one question through the Responses API and read the answer.

**What is it, and why does it matter?** An API lets code request a service. `response_id` identifies one generation, not a conversation.

**How do you use it?** Verify model/input/output limit, then choose portal or Python. Without company policies, acknowledging missing information is correct.

**Where do you run it?** Use the model Playground and [first_response.py](../../samples/first_response.py). The portal does not execute your Python file; both paths call the model service.

## Prerequisites

Use L01's sign-in, virtual environment, `.env`, and L02's ready deployment. Verify model-invocation access and cost scope for one request. This example targets Azure public cloud; sovereign clouds need their own authentication/domain settings.

## Steps

### 1. Match portal settings with Python arguments

Open **Build → Models → Deployments → contoso-chat → Playground**. Do not select **Save as agent**. Verify a model-only request without extra instructions or retrieval tools.

![Model response example. The answer applies the synthetic Contoso rule supplied in the question to the KRW 2,000,000 approval boundary.](../../assets/portal/en/16-model-response.png)

The screenshot's model/question illustrate the UI. Select your own project/deployment and use this question:

```prompt
How should you respond when no company policy has been provided?
```

![Output-limit setting example. Max Completion Tokens is set to 256 in the model Playground's Parameters dialog.](../../assets/portal/en/17-model-parameters.png)

| Portal control | Python argument/result |
| --- | --- |
| Select your deployment in Model | `model=deployment_name` |
| Enter the question in Chat | `input=question` |
| Parameters → Max Completion Tokens | `max_output_tokens=512` |
| Send a service request | `client.responses.create(...)` |
| Inspect response text/ID | `response.output_text`, `response.id` |

The screenshot's 256 is an example. Set 512 to match this code's budget and keep unnecessary **Web search** tools off. Do not add unsupported Temperature/Top P settings.

### 2. Read the direct SDK request

Trace connection → request → response validation below. The endpoint is a placeholder; find where `client` and `response` are created. **This is a reading block**. Use the next step's `--live` command to execute the request once.

```python
from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential

project_endpoint = "https://<resource>.services.ai.azure.com/api/projects/<project>"
deployment_name = "contoso-chat"
question = "How should you respond when no company policy has been provided?"

with (
    AzureCliCredential(process_timeout=30) as credential,
    AIProjectClient(
        endpoint=project_endpoint,
        credential=credential,
        retry_total=0,
    ) as project,
    project.get_openai_client(max_retries=0, timeout=60.0) as client,
):
    response = client.responses.create(
        model=deployment_name,
        input=question,
        max_output_tokens=512,
        store=False,
    )

if response.status != "completed" or not response.output_text or not response.output_text.strip():
    raise RuntimeError(f"Response not complete: {response.status}")

print(response.output_text)
print(f"response_id={response.id}")
```

`AzureCliCredential` uses L01's CLI sign-in; `AIProjectClient` connects to the Project endpoint. `get_openai_client()` supplies the request client; `responses.create()` sends the question. `store=False` controls response storage, not all service logs, abuse monitoring, or retention.

The executable adds `.env` loading, input-size checks, and `--live` opt-in. `read_config()` and `ensure_response()` are shared settings/status checks; they do not issue hidden additional model calls.

### 3. Inspect the plan, then execute once

```bash
python samples/first_response.py
python samples/first_response.py --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough — execute the second line only when the inspected scope is correct.**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `first_response.py` | Prints the default question and `PLAN ONLY`. | No Azure request, configuration validation, or sign-in. |
| 2. `first_response.py --live` | Sends one question to the project/deployment in `.env`. | At most 512 output tokens, zero automatic SDK retries, 60-second request timeout. Billable inference; no agent/store creation. |

</div>

If you already selected portal Send, skip the second line and inspect that answer. Portal and Python are separate requests, and even identical questions can produce different IDs/wording.

Record the answer, status, and `response_id`. No company policy was supplied, so definite price limits or stock claims are unsupported. If the portal does not expose an ID, record it unverified rather than inventing one.

### 4. Change one input

Change the question without transmitting it first:

```bash
python samples/first_response.py --query "Without company policy, can you state a laptop purchase limit with certainty?"
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `--query` | Selects the quoted question as this execution's input. | Printed locally without `--live`; no extra inference. |

</div>

If a real comparison is necessary, verify cost scope and send **one additional request** through the selected path. Compare treatment of unknown policy, not wording. Do not repeatedly call to match the screenshot.

<details class="optional-path" markdown="1">
<summary>Optional reference: streaming, structured output, and images</summary>

| Feature | What to inspect |
| --- | --- |
| Streaming | First-output time versus final completion |
| Structured outputs | JSON parsing, schema, and type checks |
| Embeddings | Retrieval vectors, not generated answers |
| Vision | Supported synthetic receipt input versus actual price/quantity |

APIs/tool support vary by model. Check the model card and official SDK examples before adding options.

</details>

## Success criteria

Your selected portal or Python request returned an actual answer; record the available status/ID, question, and deployment name. SDK execution must pass completed/nonempty-text checks. Plan-only means model execution not performed.

## Troubleshooting

Incomplete/empty responses do not pass. Check output limits, refusals, quota, authentication, and deployment names instead of automatically retrying 429. Portal Send and Python commands do not replay each other's results.

## Cleanup

Retain the model deployment. This lab creates no separate agent/vector store. Create the instructed agent in L04.
