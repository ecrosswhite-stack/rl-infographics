---
name: carbonvoice-platform
description: Reference card for the Hermes "carbonvoice-platform" gateway adapter, which let a Hermes agent appear as a bot user inside Carbon Voice (carbonvoice.app) channels over Socket.IO and REST. Consult it only when a user asks what this Hermes plugin did, whether Claude can act as a Carbon Voice chat bot, or how the Carbon Voice REST endpoints the plugin used are shaped (POST /v3/messages/start, /v5/messages/text, Bearer cv_pat_ token). It is not a tool for chatting with users on Carbon Voice; Claude has no Carbon Voice connector.
---
# Carbon Voice Gateway Adapter (reference card)

**Hermes original:** https://github.com/PhononX/hermes-plugin-carbonvoice @ 55867db · tier: community · category: platform · license: MIT
**Port class:** D · a chat-platform gateway adapter that runs inside the long-lived Hermes gateway process; Claude has no equivalent inbound message loop.

## What the Hermes plugin does
Registers a `platform` kind plugin (`kind: platform`, no tools, no hooks) that connects the Hermes gateway to Carbon Voice. It listens for `message:created` / `message:updated` events over Socket.IO (via `python-socketio`) and falls back to polling `POST /v3/messages/recent` every `CARBONVOICE_POLL_INTERVAL_MS` (default 5000). It persists a cursor to `$HERMES_HOME/state/carbonvoice.json` so messages received while Hermes was offline are processed on restart. Replies are posted with `POST /v3/messages/start` (legacy) or `POST /v5/messages/text`, threaded via `reply_to_message_id`; it also reacts to inbound messages, marks them read, resolves usernames via `GET /v3/users/{id}`, and enforces a deny-by-default allowlist of senders with owner approval by reaction. Text only: Carbon Voice transcribes voice memos before delivery.

## Equivalent in Claude
None identified. Claude cannot run a persistent Socket.IO listener or act as a bot identity inside Carbon Voice. The outbound half is a plain REST call that Claude could issue once from Claude Code if a user explicitly asks to post a message, using the shapes copied from `api.py`: base URL `https://api.carbonvoice.app` (override `CARBONVOICE_BASE_URL`), header `Authorization: Bearer $CARBONVOICE_PAT` for tokens starting `cv_pat_` (otherwise `x-api-key`), body `{"unique_client_id": "<uuid4>", "transcript": "<text>", "is_text_message": true, "is_streaming": false, "channel_id": "<channel_guid>"}` to `POST /v3/messages/start`. Not verified against a live account.

## Setup
None.

## Limits
- Inbound message handling, session routing, mention gating (`tagged_user_ids`), reactions, mark-as-read, offline catch-up and the owner-approval allowlist all depend on the Hermes gateway runtime and are not replicated.
- The optional voice-reply path (`CARBONVOICE_VOICE_OUT`, Hermes `voice.auto_tts`, Hermes TTS providers) is Hermes-internal.
- Posting to Carbon Voice sends message text to a third-party service (PhononX) under the user's PAT; the agent identity has whatever access that PAT has.
- The many optional `CARBONVOICE_*` tuning variables (poll interval, retry backoff, allowed users, home channel, reaction ids) only have meaning to the Hermes adapter.

## Source
- Catalog entry (reviewed commit): https://github.com/PhononX/hermes-plugin-carbonvoice/tree/55867dba9c6645ce493fd955970302e59a4548ea
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/carbonvoice-platform.yaml
