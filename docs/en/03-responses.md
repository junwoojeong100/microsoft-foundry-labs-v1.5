> **What you will build:** A call to a Foundry model without an API key, with its response and response ID verified.

## Objectives

Understand the smallest unit of a model call. **This is not yet an agent or RAG.**

## Concepts and lab map

**What you will try:** Send input to a model through the Responses API and inspect the response object.

**What is it, and why does it matter?** An API is a contract for requesting actions in code rather than clicking a screen. A Responses result can contain not only readable text but also status, identifiers, and tool requests. A successful HTTP request or printed text does not necessarily mean the business task is complete. Checking both completion status and actual content builds the habit needed for agents, evaluation, and tracing.

**How do you use it?** First review the plan output to see which settings will be used, then send one synthetic question to the prepared model. Read the response text and response ID separately, and check that the model does not invent an answer when it has not been given company documents. The portal Playground provides a visual comparison for understanding inputs and outputs; this chapter's SDK path teaches reproducible calls.

**Where do you run it?** The executable sample is [samples/workshop.py](../../samples/workshop.py). The Python excerpt below explains the core code; it is not a separate shell command. The full sample also handles authentication, errors, and output checks.

## Prerequisites

You need L01's `.env`, CLI sign-in, and `requirements.txt` installation, plus the ready deployment from L02. This path targets projects in the Azure public cloud. Sovereign-cloud endpoints, such as Government endpoints, require their own officially documented authentication and domain settings.

## Steps

### First connect inputs and responses in the portal

Open **Build → Models → Deployments → your deployment → Playground**. The `contoso-chat` shown in the image is an existing `gpt-4.1-mini` deployment in the capture environment; use your own approved deployment name. This is a model exercise: **do not click Save as agent**.

![A live model Playground run with a synthetic Contoso approval-threshold question. The response says that a total of exactly KRW 2,000,000 requires team manager approval. No additional tools are configured under Tools.](../../assets/portal/16-model-response.png)

**Reading the screen:** **Model / Instructions / Tools** on the left define the request's conditions; the right side shows user input and the model response. Because this demonstration stated the synthetic rule in the question itself, it did not validate RAG or private company knowledge. It also did not execute an inventory lookup, purchase draft, or actual approval.

![The live Parameters dialog in the model Playground. Max Completion Tokens is set to 256, with the remaining default parameters visible.](../../assets/portal/17-model-parameters.png)

**Before running:** Set an output limit under **Parameters → Max Completion Tokens**. For the capture, the limit was 256, and **Web search**, which can incur extra charges or external data transfer, was removed from this model Playground before the question was sent once. No existing agent's tools or policies were changed. Temperature/Top P control aspects of generation variability; they are not monetary spending caps. Supported options vary by model.

The displayed answer was, in English, **“If the total is exactly KRW 2,000,000, team manager approval is required.”** The portal's **Response tokens** showed 91 input tokens, 18 output tokens, and 109 tokens in total. This is the result of one model demonstration, not an evaluation score or the total lab cost.

An automated wait that directly watched the API URL timed out, but the portal displayed a response and response ID, so they were **verified by reading the screen without resending the request**. The raw HTTP status and the number of any internal portal retries could not be verified and are not inferred. The CLI path below is a separate execution for learning to read the response object and ID in code. There is no need to make extra calls just to reproduce the screenshot.

### 1. Review the plan at no cost

```bash
python samples/workshop.py model
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `model` | Selects the model-call path in `workshop.py`, but displays only the execution plan because `--live` is absent. | Read `PLAN ONLY`. No Azure calls or model costs. |

</div>

The output should say `PLAN ONLY`, and no Azure request is made. A success message without `--live` is not evidence of a successful model call.

### 2. Call the live model

```bash
python samples/workshop.py model --live
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `model --live` | Sends the default synthetic question using the configured project/deployment and CLI credentials. The output limit is 2048 tokens, and automatic SDK retries are disabled. | Incurs inference cost. Check the response text and `response_id`; no agent or vector store is created. |

</div>

You should see response text and `response_id=...`. The question asks how to respond when company policy has not been provided. Check that the model **does not fabricate company policy**.

To call it with your own input:

```bash
python samples/workshop.py model --live --query "회사 규정이 없는데 노트북 구매 상한을 단정할 수 있나요?"
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `model --query` | The entire quoted string after `--query` is one input to the model. It replaces the default question, and `--live` permits actual transmission. | This is an additional inference request, not a replay of the previous result. It incurs additional cost and produces a new response ID. |

</div>

The Korean question in the command asks, “Without company policy, can you state a laptop purchase limit with certainty?” It is intentionally unchanged as an executable input. The content of `--query` is sent to Azure. Use only synthetic lab inputs.

### 3. Read the core code

This is the core API flow. The complete executable sample, including environment checks and error handling, is `samples/workshop.py`.

```python
with (
    AzureCliCredential() as credential,
    AIProjectClient(endpoint=project_endpoint, credential=credential) as project,
    project.get_openai_client() as client,
):
    response = client.responses.create(
        model=deployment_name,
        input="회사 규정이 없으면 어떻게 답해야 하나요?",
        max_output_tokens=2048,
        store=False,
    )
```

The unchanged Korean `input` asks, “How should you respond if no company policy is available?” `store=False` controls response storage for this model call. It does not mean that all service logs, abuse monitoring, or data retention disappear.

| Value | Meaning | Common mistake |
| --- | --- | --- |
| project endpoint | The project API's address | Substituting the model's `/openai/v1/` address |
| deployment name | The name of the model deployment you created | Assuming it always matches the model ID |
| response ID | The identifier for one generation operation | Confusing it with a conversation ID |
| output text | The model's user-facing response | Treating a response containing only tool calls as a completed answer |

### 4. Locate the extension capabilities

| Feature | How to try it | How to judge success |
| --- | --- | --- |
| Streaming | Receive stream events using the portal's View code or an official SDK example | Record time to first output separately from final completion |
| Structured outputs | Define `sku` and `quantity` fields using a supported model's JSON schema output example | Both JSON parsing and field/type checks pass |
| Embeddings | Vectorize documents with a supported embedding deployment | Recognize this as a search representation, not a human-readable answer |
| Vision | Send a synthetic receipt image to a supported model | Compare price, quantity, and total with the original |

These extensions do not imply that every model supports the same API in the same way. Check the model card before adding a parameter. In particular, do not blindly copy an existing `temperature` setting to a reasoning model.

## Success criteria

The live `--live` response has completed and contains nonempty text. You have recorded the response ID and can explain the difference between a model call without internal company information and a document-grounded answer.

## Troubleshooting

Do not count `incomplete` or empty output as a success. Check the output token limit, refusals, tool requests, quota, and traces. The sample disables automatic SDK retries to reduce costs and duplicate requests. Do not retry 429 errors indefinitely.

## Cleanup

The sample's `model` command creates no agents or vector stores. The model deployment continues to exist.
