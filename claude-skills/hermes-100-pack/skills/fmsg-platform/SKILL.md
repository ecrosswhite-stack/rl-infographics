---
name: fmsg-platform
description: Send and read fmsg messages (the federated, threaded @user@domain messaging protocol) through the fmsg Web API using FMSG_API_URL, FMSG_API_KEY and FMSG_HOME_CHANNEL. Use this when the user says "send an fmsg to @alice@example.com", "check my agent's fmsg inbox", "reply in that fmsg thread", "post to my fmsg address", or mentions api.fmsg.io, fmsg-webapi or an fmsgk_ API key. Real-time inbound listening is not available here; read the inbox on request.
---
# fmsg

**Hermes original:** https://github.com/markmnl/hermes-fmsg @ 562f45a · tier: community · category: platform · license: MIT
**Port class:** C · outbound sends and inbox reads are documented JSON REST calls Claude can make; the WebSocket inbound loop, thread-to-session mapping and allowlist gating live in the Hermes gateway.

## What the Hermes plugin does
A platform adapter for fmsg. It exchanges an API key for a short-lived JWT (`POST /fmsg/token`), streams inbound events over `/fmsg/ws`, maps fmsg roots and branches to Hermes sessions, and sends replies via the REST routes (create draft, attach, send, mark read). Access is deny-by-default via `FMSG_ALLOWED_USERS`. No tools or hooks are registered; sending from Hermes uses `hermes send --to fmsg` or the `send_message` tool.

## Equivalent in Claude
Per the plugin source (`plugin/fmsg_client.py`). Base URL `FMSG_API_URL` (default `https://api.fmsg.io`).

1. Exchange the API key for a JWT (default TTL 12 h per the source):
```bash
TOKEN=$(curl -sS -X POST "$FMSG_API_URL/fmsg/token" -H "Authorization: Bearer $FMSG_API_KEY" | python3 -c 'import json,sys;print(json.load(sys.stdin)["access_token"])')
```
The response carries `access_token` and `expires_at`; the JWT `sub` claim is the agent's own address, which the plugin used as the `from` field.
2. Use `Authorization: Bearer $TOKEN` for every call below.
3. Create a draft, then send it:
```bash
curl -sS -X POST "$FMSG_API_URL/fmsg" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"version":1,"from":"@agent@example.com","to":["@alice@example.com"],"type":"text/plain; charset=utf-8","size":<utf8-byte-length>,"data":"<text>","topic":"Hermes"}'
# response: {"id": <msg_id>}
curl -sS -X POST "$FMSG_API_URL/fmsg/<msg_id>/send" -H "Authorization: Bearer $TOKEN"
```
To reply inside a thread, set `"pid": <parent message id>` instead of `topic` (they are mutually exclusive). Optional flags: `"important": true`, `"no_reply": true`.

| Plugin client method | REST route |
|---|---|
| `list_messages(limit, offset)` | GET `/fmsg?limit=&offset=` (inbox) |
| `list_sent` | GET `/fmsg/sent` |
| `get_message(id)` / `get_data(id)` | GET `/fmsg/{id}` / GET `/fmsg/{id}/data` |
| `create_draft` / `send` / `delete_draft` | POST `/fmsg` / POST `/fmsg/{id}/send` / DELETE `/fmsg/{id}` |
| `mark_read(id)` | POST `/fmsg/{id}/read` |
| `attach(id, filename, bytes)` / `get_attachment` | POST `/fmsg/{id}/attach` / GET `/fmsg/{id}/attach/{filename}` |
| `iter_events` | WebSocket `/fmsg/ws` (not used from Claude) |

Reply-all per the plugin: include every participant of the parent (`from`, `to`, `add_to`) except the agent itself. Default topic for new roots: `FMSG_DEFAULT_TOPIC` (default `Hermes`). Send only to `FMSG_HOME_CHANNEL` or addresses the user names.

## Setup
1. Get an agent sub-account and `fmsgk_...` API key from a hosted provider (fmsg.io, per the README) or a self-hosted fmsg-docker stack.
2. `export FMSG_API_URL=https://api.fmsg.io FMSG_API_KEY=fmsgk_... FMSG_HOME_CHANNEL=@you@example.com FMSG_ALLOWED_USERS=@you@example.com`
3. No MCP package verified for fmsg; use the REST calls.

## Limits
- No WebSocket listener: Claude cannot be woken by inbound fmsg messages; poll `GET /fmsg` when asked.
- Root/branch-to-session mapping, allowlist enforcement, inbox catch-up after reconnect and cron delivery are gateway behaviors.
- Attachment upload body format (`POST /fmsg/{id}/attach`) was not read in detail.
- Messages leave the machine to the configured fmsg host; keep the API key out of logs and prompts.

## Source
- Catalog entry (reviewed commit): https://github.com/markmnl/hermes-fmsg/tree/562f45a48a6b10504c8d6ff5c677f1ec990e6b7b
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/fmsg-platform.yaml
