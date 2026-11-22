---
name: fluxer-platform
description: Post, edit, pin and react to messages in Fluxer channels or DMs through Fluxer's bot REST API with FLUXER_BOT_TOKEN (and FLUXER_BASE_URL for self-hosted instances). Use this when the user says "send this to my Fluxer channel", "post in Fluxer", "edit that Fluxer message", "list my Fluxer guild's channels", or mentions api.fluxer.app or a Fluxer bot token. The live gateway (answering inbound Fluxer messages, approvals, voice bridge) is not available from Claude; outbound REST calls are.
---
# Fluxer

**Hermes original:** https://github.com/elkimek/hermes-fluxer-plugin @ 6d2ef97 · tier: community · category: platform · license: MIT
**Port class:** C · outbound REST routes are visible in the adapter and callable with curl; the Gateway WebSocket inbound loop, mention gating, approval flows and LiveKit voice bridge are Hermes gateway machinery.

## What the Hermes plugin does
A `kind: platform` adapter for Fluxer, a Discord-like chat platform. It receives `MESSAGE_CREATE` events over the Fluxer Gateway WebSocket (discovered via `GET /gateway/bot`), gates them by `FLUXER_ALLOWED_USERS` (deny-by-default) and mention rules, and sends replies through the bot REST API: messages, edits, deletes, pins, reactions, typing, media uploads, channel directory enumeration, optional native slash-command registration, and an optional realtime voice bridge. It registers no agent tools.

## Equivalent in Claude
Per the plugin source (`adapter.py`): base URL `FLUXER_BASE_URL`, default `https://api.fluxer.app/v1`; header `Authorization: Bot $FLUXER_BOT_TOKEN`.

```bash
FX="${FLUXER_BASE_URL:-https://api.fluxer.app/v1}"
fx() { curl -sS -H "Authorization: Bot $FLUXER_BOT_TOKEN" -H "Content-Type: application/json" "$@"; }
fx -X POST "$FX/channels/<channel_id>/messages" -d '{"content":"<text>"}'
```

| Adapter action | Route used by the plugin |
|---|---|
| send message | POST `/channels/{id}/messages` (JSON with `content`; optional `message_reference` for replies) |
| edit / delete message | PATCH / DELETE `/channels/{id}/messages/{message_id}` |
| react / unreact | PUT / DELETE `/channels/{id}/messages/{message_id}/reactions/{emoji}/@me` |
| pin / unpin, list pins | PUT / DELETE `/channels/{id}/pins/{message_id}`, GET `/channels/{id}/messages/pins` |
| typing indicator | POST `/channels/{id}/typing` |
| list my guilds / guild channels | GET `/users/@me/guilds`, GET `/guilds/{guild_id}/channels` |
| threads | GET `/guilds/{guild_id}/threads/active`, POST `/channels/{id}/messages/{message_id}/threads` |
| gateway discovery | GET `/gateway/bot` |
| register slash commands | PUT `/applications/{app_id}/commands` or `.../guilds/{guild_id}/commands` |

PUT/DELETE for reactions and pins were read from the source; PATCH/DELETE for message edit and delete follow the route shape and were not read, so check the first response. Only send to channels the user names (`FLUXER_HOME_CHANNEL` is the plugin's default target). Neutralize `@everyone`/`@here` in outbound text unless the user wants them, as the plugin does by default.

## Setup
1. Create a Fluxer bot/application and copy its token in `<applicationId>.<secret>` form (per the README).
2. `export FLUXER_BOT_TOKEN=<token>`; for self-hosted, `export FLUXER_BASE_URL=https://your-host/v1`.
3. Note the channel or DM ID to post to (`FLUXER_HOME_CHANNEL` in the plugin). Fluxer features such as pins, components and threads are deployment-dependent.
4. No Fluxer MCP package verified.

## Limits
- No inbound: Claude cannot answer Fluxer messages, run approval prompts via reactions or buttons, recover backlog, or join voice rooms (the plugin's `FLUXER_VOICE_*` LiveKit/xAI/STT bridge is out of scope).
- Media upload payload format, delivery verification and the roughly 90 optional `FLUXER_*` tuning variables are not replicated.
- Outbound messages go to the Fluxer deployment under the bot identity; confirm before posting.

## Source
- Catalog entry (reviewed commit): https://github.com/elkimek/hermes-fluxer-plugin/tree/6d2ef9767d0a0811a3ae26a76290b9b1e4636d4c
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/fluxer-platform.yaml
