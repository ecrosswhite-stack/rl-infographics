---
name: sendblue
description: Send iMessage or SMS texts and list recent messages through the Sendblue API using SENDBLUE_API_KEY, SENDBLUE_API_SECRET and SENDBLUE_PHONE, the same env vars the Hermes plugin used. Use this when the user says "text <number> via Sendblue", "send an iMessage", "send an SMS from my Sendblue number", "what texts came in on Sendblue", "show recent Sendblue messages", or "send a typing indicator". Sending costs Sendblue credits and messages real phones, so confirm the number and text with the user first.
---
# Sendblue iMessage / SMS

**Hermes original:** https://github.com/duoi/hermes-sendblue-plugin @ 3318aaa · tier: community · category: platform · license: MIT
**Port class:** C — the two tools are plain Sendblue REST calls Claude can make; the inbound polling daemon, per-phone session routing and the `pre_llm_call` typing-indicator hook depend on the Hermes runtime.

## What the Hermes plugin does
Registers tools `sendblue_send_message` and `sendblue_list_messages` (toolset `sendblue`) and a `pre_llm_call` hook that fires a typing indicator to `SENDBLUE_ACTIVE_USER_PHONE` while the model thinks. A separate `daemon.py` polls Sendblue for inbound texts, gates them against `USER_PHONE`, maps each phone number to a Hermes session in a SQLite DB, invokes the `hermes` CLI, and texts the answer back. Tool use is gated to admin numbers (`SENDBLUE_ADMIN_PHONES`, falling back to `USER_PHONE`).

## Equivalent in Claude
Per the plugin source (`tools.py`, `daemon.py`). All calls use headers `sb-api-key-id: $SENDBLUE_API_KEY`, `sb-api-secret-key: $SENDBLUE_API_SECRET`, `Content-Type: application/json`.

Send a message (confirm recipient and text with the user before sending):
```bash
curl -sS -X POST https://api.sendblue.co/api/send-message \
  -H "sb-api-key-id: $SENDBLUE_API_KEY" -H "sb-api-secret-key: $SENDBLUE_API_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"number":"+14155551234","content":"<text>","from_number":"'"$SENDBLUE_PHONE"'"}'
```

List recent messages (default limit 10):
```bash
curl -sS "https://api.sendblue.co/api/v2/messages?limit=10" \
  -H "sb-api-key-id: $SENDBLUE_API_KEY" -H "sb-api-secret-key: $SENDBLUE_API_SECRET"
```

Typing indicator (optional, what the hook did):
```bash
curl -sS -X POST https://api.sendblue.co/api/send-typing-indicator \
  -H "sb-api-key-id: $SENDBLUE_API_KEY" -H "sb-api-secret-key: $SENDBLUE_API_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"number":"+14155551234","from_number":"'"$SENDBLUE_PHONE"'"}'
```

Respect the plugin's admin gate: only act on behalf of numbers listed in `SENDBLUE_ADMIN_PHONES` (or `USER_PHONE`) when the request itself came in over SMS; from the desktop, the user running Claude is the admin.

| Hermes tool | How Claude does it |
|---|---|
| `sendblue_send_message(number, message)` | POST `/api/send-message` as above |
| `sendblue_list_messages(limit)` | GET `/api/v2/messages?limit=N` |
| `pre_llm_call` typing hook | POST `/api/send-typing-indicator` manually, if wanted |
| `daemon.py` inbound loop | Not replicated; poll `/api/v2/messages` on request instead |

## Setup
1. Create a Sendblue account and obtain the API key, API secret and the assigned Sendblue phone number (per the README).
2. `export SENDBLUE_API_KEY=... SENDBLUE_API_SECRET=... SENDBLUE_PHONE=+1...`
3. Optional: `export SENDBLUE_ADMIN_PHONES=+1...,+1...` and `USER_PHONE=...` to mirror the plugin's authorization lists.
4. An npm package `sendblue` exists (verified: `npm view sendblue` -> version 3.23.0, "The official TypeScript library for the Sendblue API"); not an MCP server.

## Limits
- No background daemon: Claude does not receive texts in real time, keep per-phone sessions, route voice notes to STT, or upload generated media (the plugin used S3/R2 via `S3_BUCKET_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `R2_ENDPOINT_URL`, with a public `tmpfiles.org` fallback that the README warns about).
- The "text me a Technical Plan and wait for Yes" approval flow over SMS is a daemon prompt, not replicated.
- Sending costs money and delivers to real phones; message bodies go to Sendblue.
- Response JSON shapes were not verified beyond the plugin returning them verbatim.

## Source
- Catalog entry (reviewed commit): https://github.com/duoi/hermes-sendblue-plugin/tree/3318aaa4402769ce440d43e0445ea2151ad5e73e
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/sendblue.yaml
