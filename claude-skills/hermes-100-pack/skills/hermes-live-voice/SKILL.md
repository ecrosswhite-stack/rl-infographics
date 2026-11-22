---
name: hermes-live-voice
description: Reference card only. Describes the Hermes "hermes-live-voice" (talk-desktop) plugin, a full-duplex WebRTC voice mode for Hermes Desktop driven by OpenAI's gpt-live-1 through the local Codex app-server on a ChatGPT subscription, with live transcript and voice-to-chat task delegation. Use this card when a user asks what hermes-live-voice did or whether Claude Code or Cowork has an equivalent voice call feature. It performs no voice work; do not trigger it for audio transcription or TTS tasks.
---
# Live Voice for Hermes Desktop (reference card)

**Hermes original:** https://github.com/Synero/hermes-live-voice @ 5f0022b · tier: community · category: voice · license: MIT
**Port class:** D · it is a Hermes Desktop renderer plugin plus a Hermes dashboard API route; neither surface exists in Claude.

## What the Hermes plugin does
Per the README, the plugin (manifest name `talk-desktop`, version 0.2.1) ships two halves: `dashboard/plugin_api.py`, mounted by the Hermes dashboard under `/api/plugins/talk-desktop/`, and `desktop/plugin.js`, loaded by Hermes Desktop. The desktop half negotiates a WebRTC session; a local broker spawns `codex app-server` and drives a realtime conversation with model `gpt-live-1-codex` on the user's ChatGPT/Codex login. It shows a live transcript, mic and mute controls, usage panels, and delegates spoken task requests into the focused Hermes chat (`delegation: client`) or an opt-in server-side Codex agent thread. `__init__.py` registers no tools or hooks. Settings live in `settings.json` (`codexAgentModel`, `delegation`). It bundles MIT-licensed fallback code from TheSmokeDev/hermes-talk.

## Equivalent in Claude
None identified for Claude Code or Cowork. The Claude mobile apps offer a voice mode, but it is a separate product feature, not a port of this plugin, and it does not drive a Codex app-server or delegate tasks into a Claude Code session.

## Setup
None.

## Limits
- Requires Hermes Desktop, the Hermes dashboard, and `codex` CLI >= 0.154 logged in with a ChatGPT plan; none of these are part of Claude.
- The voice lane sends audio and transcript to OpenAI's ChatGPT backend per the README; this is a third-party data flow the user should know about if they run the original.
- No live transcript UI, voice tool calls, or usage panels in Claude.

## Source
- Catalog entry (reviewed commit): https://github.com/Synero/hermes-live-voice/tree/5f0022b97105da26783854aca9dac855c9ca865f
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-live-voice.yaml
