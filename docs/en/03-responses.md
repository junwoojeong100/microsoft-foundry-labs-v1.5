> **What you will build:** One request to your model, with its actual answer, status, and response ID.

<div class="lab-brief" markdown="1">

**Format:** Default: one Python SDK request. Use the portal to inspect settings or as an alternative execution path.

**Start here:** Find L02's `contoso-chat` in the Playground Model selector and Python `model` argument.

**What to check:** A completed answer/ID and no fabricated company policy.

</div>

## Objectives

**Understand the smallest model call.** There is no agent, document retrieval, or function tool yet. Read how the code and screen settings relate before executing.

## Concepts and lab map

**What you will try:** Send one question through the Responses API and read the answer.

**What is it, and why does it matter?** An API lets code request a service. `response_id` identifies one generation, not a conversation.

**How do you use it?** Verify model/input/output limit, then run the default Python command. If you choose the portal alternative, avoid a duplicate call. Without company policies, acknowledging missing information is correct.

**Where do you run it?** Use the model Playground and [first_response.py](../../samples/first_response.py). The portal does not execute your Python file; both paths call the model service.

## Prerequisites

Use L01's sign-in, virtual environment, `.env`, and L02's ready deployment. Verify model-invocation access and cost scope for one request. This example targets Microsoft Azure public cloud; sovereign clouds need their own authentication/domain settings.

## Steps

### 1. Match portal settings with Python arguments

**On the default path, do not select Send here; use step 2's Python command.** Send the question in Chat only for the portal alternative, then omit Python's `--live` call. The collapsed SDK excerpt is a reading reference.

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

<details class="implementation-detail" markdown="1">
<summary>Implementation reference: read the SDK request — execute through step 2 below</summary>

<a id="l03-2-read-the-direct-sdk-request"></a>

### Read the direct SDK request

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

</details>

<a id="l03-3-inspect-the-plan-then-execute-once"></a>

### 2. Inspect the plan, then execute once

```bash
python samples/first_response.py
```

<div class="command-explanation" markdown="1">

**Command walkthrough — inspect the question without sending it.**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `first_response.py` | Prints the default question and `PLAN ONLY`. | No Microsoft Azure request, configuration validation, or sign-in. |

</div>

**Stop and check:** Confirm the planned question, the project/deployment in `.env`, and cost scope for one request before continuing. If you already selected portal Send, **skip this command and read that answer instead.**

```bash
python samples/first_response.py --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | What it does | Result, cost, or change |
| --- | --- | --- |
| 1. `first_response.py --live` | Sends one question to the project/deployment in `.env`. | At most 512 output tokens, zero automatic SDK retries, 60-second request timeout. Billable inference; no agent/store creation. |

</div>

Portal and Python are separate requests, and even identical questions can produce different IDs/wording.

Record the answer, status, and `response_id`. No company policy was supplied, so definite price limits or stock claims are unsupported. If the portal does not expose an ID, record it unverified rather than inventing one.

`first_response.py` **prints to the terminal; it does not save a result file automatically.** Keep the question, deployment, answer, and ID in your private progress record. L06's integrated run creates the separate response JSONL used in L10.

<a id="l03-4-change-one-input"></a>

### 3. Change one input

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
| Vision | Give a supported model the [sample receipt](../../data/en/receipt.html) as an image or PDF (browser print → save), then compare the document number, items, quantities, and total it reads with `data/en/receipt.expected.json` (KB-01 × 2 at 89,000 = 178,000 KRW, approval pending) |

APIs/tool support vary by model. Check the model card and official SDK examples before adding options.

</details>

## Success criteria

- Your selected portal or Python request returned an actual answer.
- You recorded the question, deployment name, and the available status/ID.
- The Python path passed the completed and nonempty-text checks.
- If you only read the plan, model execution is **not performed**.

## Troubleshooting

| Symptom | Check first | Next action |
| --- | --- | --- |
| Incomplete or empty response | Output limit, refusal, and deployment name | Do not record it as a pass; find the cause first. |
| Authentication or permission error | Sign-in state, model-call permission, and the deployment name in `.env` | Compare with the values you verified in L01 and L02. |
| 429 | Quota and request limits | Do not retry automatically; check the limits. |
| The portal and Python answers/IDs differ | They are separate requests | Neither command replays the other's result; record each separately. |

## Cleanup

Retain the model deployment. This lab creates no separate agent/vector store. Create the instructed agent in L04.

<div class="lab-handoff" markdown="1">

**Keep:** Your question, deployment name, actual answer, completion state, and available `response_id`. Save terminal output in your private progress record.

**Continue:** [L04 an agent with instructions](#l04). Reuse the model, but create a new Prompt Agent.

</div>
