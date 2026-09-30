> **What you will build:** A voice agent that speaks brief purchasing guidance, with interruption, silence, and session termination verified.

## Objectives

**Speech STT/TTS, real-time Voice Live, and a voice Prompt Agent are not interchangeable terms.** Distinguish Speech's GA capabilities from the Voice Agent Preview experience.

## Concepts and lab map

**What you will try:** Speech recognition, speech synthesis, real-time turn detection, user interruption, and session termination.

**What is it, and why does it matter?** STT converts sound into text, TTS converts text into sound, and a Voice Agent also manages conversation state and response timing between them. Even an answer that is correct in text can mishear an amount or miss a corrected quantity in voice. Usability requires checking not just content accuracy, but when the agent listens, speaks, and stops.

**How do you use it?** Start with a short synthetic sentence, then test quantity recognition → confirmation question → interruption → quantity correction → termination. The user grants microphone permission directly in the browser. End the session before changing settings, and compare the resulting transcripts and latency.

**Where do you run it?** Voice input takes place in a browser with a real microphone and speakers. This guide's headless portal captures show where settings are located; they are not evidence of a successful voice conversation. The supplied instructions use this chapter's synthetic scenario and do not include real customer calls or custom voice training.

## Prerequisites

You need voice Preview access for a supported region/project, a compatible voice model, a microphone/speakers, and an approved browser. Check usage/session costs and keep tests short.

## Steps

### 1. Create a Voice Agent

Select **Build → Agents → New agent → Build an agent → Interaction mode: Voice**. The creation dialog states that interaction mode cannot be changed after creation, so use a separate voice lab agent. Record the current UI defaults for model, language, voice, and turn detection.

![The actual Create an agent dialog with the synthetic name contoso-voice-lab and Voice Preview selected. It shows the notice that interaction mode cannot be changed after creation, plus create and cancel buttons.](../../assets/portal/15-voice-setup.png)

**Read the screen:** **Agent name** is a synthetic name distinct from the other labs; **Interaction mode** is **Voice Preview**. During the capture, only these two inputs were selected before closing with **Cancel**. **Create agent and open playground** was not clicked, and no voice agent, microphone session, or paid voice call was created. Viewing the Preview selection screen is different from completing a real voice conversation.

Learners proceeding with the lab should enter a **Voice agent goal** such as “Provide brief guidance in Korean on synthetic Contoso purchasing policies; do not place real orders or perform approvals.” In the capture, this field was empty and the create button was disabled. After creating the agent in an approved environment, review the Playground's instructions, model, voice, and language settings; do not use automatically filled settings without checking them.

Instructions:

```text
You are a Contoso purchasing guidance lab assistant.
Speak briefly in Korean and confirm one thing at a time.
Reconfirm amounts and quantities.
Do not place real orders, grant approvals, or make payments.
If a tool fails, report the failure and do not claim success.
Do not read long tables or full identification numbers aloud.
```

Check whether connecting L05's knowledge is supported. Do not answer as though you remember knowledge that is not available.

### 2. Start a short conversation

After saving, select **Start session** and, if needed, personally allow microphone access in the browser. Say “노트북 두 대를 구매하려고 해요” (“I'd like to buy two laptops”).

### 3. Check conversation quality

| Check | Expected behavior |
| --- | --- |
| Recognizing “두 대” (“two units”) | Understands the quantity as 2 and confirms it |
| A brief silence while the user is speaking | Does not cut off the utterance too quickly |
| The user interrupts the agent's speech | Handles stopping or redirecting the response correctly |
| “두 대가 아니라 한 대요” (“Not two—one”) | Uses the latest quantity |
| Tool failure | Does not say the order was placed |
| End session | The microphone and session close correctly |

End the session before changing settings. Inspect the voice transcript, response/conversation, and latency, and compare the results with a text conversation. A long table may be easy to read in text but unsuitable for voice.

### 4. Separate Foundry Tools by purpose

| Capability | Short additional exercise |
| --- | --- |
| Speech-to-text | Recognize the same synthetic sentence 3 times and check quantity/amount errors |
| Text-to-speech | Check natural pronunciation of “1,450,000원” (KRW 1,450,000) |
| Language / PII | Compare detection and masking of the synthetic `lab.user@example.invalid` |
| Language / classification and summarization | Compare 3 labels: purchasing, inventory, and policy inquiries |
| Translator | Translate the same policy sentence between Korean and English and check that amounts and obligations are preserved |

Translator's `2026-06-06` GA request/response contract may differ from v3.0. Do not casually mix an existing `text` payload example with the new version; check that version's contract, including fields such as `inputs`/`value`.

### 5. Conditional: Avatar and real-time transport

Supported browser/avatar settings or the Hosted Agent real-time WebSocket path are separate experiments. Telephone connections, real customer calls, and custom voice training are not part of the core course and require separate consent, policies, and authorization.

## Success criteria

You have checked pronunciation, pauses, interruption, corrected quantities, and session termination as well as content accuracy. “It made a sound” is not enough to complete the lab.

## Troubleshooting

If Voice mode is absent, first check Preview access and supported regions. Check the microphone, model, voice language, and browser output device. Do not create a text agent instead and record it as a voice success.

## Cleanup

Select **End session** and verify that no active session remains. Define retention and access scope for audio and transcripts.
