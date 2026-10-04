> **What you will build:** A call to a Foundry model without an API key, with its response and response ID verified.

<div class="lab-brief" markdown="1">

**Format:** Terminal · the default is a plan check followed by one approved model call.

**Start here:** Select L01's environment and run `python samples/workshop.py model` to inspect the plan.

**What to check:** Record the actual answer and `response_id`. Do not resend questions merely to reproduce a screenshot.

</div>

## Objectives

Understand the smallest unit of a model call. **This is not yet an agent or RAG.**

## Concepts and lab map

**What you will try:** Send one question from code through the Responses API.

**What is it, and why does it matter?** An API is how a program requests a service. The result includes an answer and a `response_id`, which helps you find the same execution later.

**How do you use it?** Read the plan, then make one approved call. Check the answer, completion state, and ID. Without company documents, acknowledging that the policy is unknown is correct.

**Where do you run it?** Run [samples/workshop.py](../../samples/workshop.py) in the terminal. The Python excerpt below is **code to read**, not an additional terminal command.

## Prerequisites

You need L01's `.env`, CLI sign-in, and `requirements.txt` installation, plus the ready deployment from L02. This path targets projects in the Azure public cloud. Sovereign-cloud endpoints, such as Government endpoints, require their own officially documented authentication and domain settings.

## Steps

### Optional: understand input and output in the portal

**The default path is terminal steps 1–3 below.** You do not need to call both the portal and the SDK. Expand this only for the screen reference.

<details class="optional-path" markdown="1">
<summary>Portal reference and the preserved one-call demonstration — no need to reproduce the image</summary>

Open **Build → Models → Deployments → your deployment → Playground** in `contoso-workshop-en`. `contoso-chat` is an example deployment name; use your own approved deployment and verify its model/version. This is a model exercise: **do not click Save as agent**.

![The English model Playground for a synthetic Contoso approval-boundary question in contoso-workshop-en. Inspect the actual input, response, and response ID.](../../assets/portal/en/16-model-response.png)

**Reading the screen:** **Model / Instructions / Tools** on the left define the request's conditions; the right side shows user input and the model response. A question that states the synthetic rule itself tests model behavior, not RAG or private company knowledge. It does not execute an inventory lookup, purchase draft, or actual approval.

![The Parameters dialog for the English model Playground. Check Max Completion Tokens before any approved request.](../../assets/portal/en/17-model-parameters.png)

**Before running:** Inspect **Parameters → Max Completion Tokens**. The captured demonstration used 256; choose an approved, supported limit for your actual model rather than treating that screenshot value as universal. Keep **Web search** and other unnecessary tools off in this model-only experiment; they can add charges or external data transfer. Do not modify existing agents or policies to match a screenshot. Temperature/Top P control generation variability, not monetary spending caps. Supported options vary by model.

For one separately approved, bounded portal request, use this English synthetic input:

```text
Contoso's synthetic rule: a total of KRW 2,000,000 or less requires team manager approval.
A higher total requires approval from both the team manager and the purchasing representative.
What approval is required for a total of exactly KRW 2,000,000?
```

The **expected** answer is team manager approval. Inspect your actual response and its identifier. Displayed tokens describe that request, not an evaluation score, proof of RAG, or the total lab cost.

If a capture or wait times out, inspect the existing response before considering another request. Do not infer raw HTTP status or internal retries from the screen. The CLI path below is a separate execution for learning to read the response object and ID in code; there is no need to make extra calls merely to reproduce an image.

</details>

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

This plan **describes the intended operation**; it does not validate `.env`, sign-in, or permissions. Compare L01's settings with L02's actual deployment name before execution.

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

**Optional additional request:** Run this only if you want to send your own question. It is not required after the default response succeeds.

```bash
python samples/workshop.py model --live --query "Without company policy, can you state a laptop purchase limit with certainty?"
```

<div class="command-explanation" markdown="1">

**Command walkthrough**

| Order and command | Details and options | Result, cost, or change |
| --- | --- | --- |
| 1. `model --query` | The entire quoted string after `--query` is one input to the model. It replaces the default question, and `--live` permits actual transmission. | This is an additional inference request, not a replay of the previous result. It incurs additional cost and produces a new response ID. |

</div>

The English content of `--query` is sent to Azure. Use only synthetic lab inputs; the English profile also supplies an English default question when the option is omitted.

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
        input="How should you respond if no company policy is available?",
        max_output_tokens=2048,
        store=False,
    )
```

The English `input` tests handling of missing policy information. `store=False` controls response storage for this model call. It does not mean that all service logs, abuse monitoring, or data retention disappear.

| Value | Meaning | Common mistake |
| --- | --- | --- |
| project endpoint | The project API's address | Substituting the model's `/openai/v1/` address |
| deployment name | The name of the model deployment you created | Assuming it always matches the model ID |
| response ID | The identifier for one generation operation | Confusing it with a conversation ID |
| output text | The model's user-facing response | Treating a response containing only tool calls as a completed answer |

### 4. Locate the extension capabilities

<details class="optional-path" markdown="1">
<summary>Optional reference: streaming, structured output, and image input</summary>

| Feature | How to try it | How to judge success |
| --- | --- | --- |
| Streaming | Receive stream events using the portal's View code or an official SDK example | Record time to first output separately from final completion |
| Structured outputs | Define `sku` and `quantity` fields using a supported model's JSON schema output example | Both JSON parsing and field/type checks pass |
| Embeddings | Vectorize documents with a supported embedding deployment | Recognize this as a search representation, not a human-readable answer |
| Vision | Send a synthetic receipt image to a supported model | Compare price, quantity, and total with the original |

These extensions do not imply that every model supports the same API in the same way. Check the model card before adding a parameter. In particular, do not blindly copy an existing `temperature` setting to a reasoning model.

</details>

## Success criteria

The live `--live` response has completed and contains nonempty text. You have recorded the response ID and can explain the difference between a model call without internal company information and a document-grounded answer.

## Troubleshooting

Do not count `incomplete` or empty output as a success. Check the output token limit, refusals, tool requests, quota, and traces. The sample disables automatic SDK retries to reduce costs and duplicate requests. Do not retry 429 errors indefinitely.

## Cleanup

The sample's `model` command creates no agents or vector stores. The model deployment continues to exist.
