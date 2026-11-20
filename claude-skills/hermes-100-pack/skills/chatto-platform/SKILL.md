---
name: chatto-platform
description: Post to and read from a self-hosted Chatto team-chat server over its ConnectRPC JSON API, ported from the Hermes chatto-platform gateway adapter. Use it when the user asks to "send this to our Chatto room", "post a message in Chatto", "list my Chatto rooms", "reply in that Chatto thread", "start a Chatto DM", or wants a script that logs into Chatto with CHATTO_URL, CHATTO_LOGIN and CHATTO_PASSWORD. The inbound side (a bot that listens to rooms and answers automatically) is a Hermes gateway feature and is not reproduced here.
---
# Chatto Platform

**Hermes original:** https://github.com/jrimmer/hermes-chatto-plugin @ aab0a20 · tier: community · category: platform · license: no LICENSE file found (README states MIT, no LICENSE file in the checkout)
**Port class:** C · outbound calls use a documented JSON-over-HTTP API that Claude can call with curl; the inbound relay (WebSocket protobuf listener, mention filtering, auto-threading, cron delivery) lives in the Hermes gateway and has no Claude equivalent.

## What the Hermes plugin does
A `kind: platform` gateway adapter. It logs into a Chatto server, opens the realtime WebSocket at `/api/realtime` (binary protobuf, protocol version 1, decoded with a stdlib codec), watches joined rooms, and relays `message_posted`, mention and DM events to the Hermes agent. Replies go back through ConnectRPC `CreateMessage` with thread support, typing indicators, reactions, presence and chunked asset upload. It registers no tools; configuration is entirely through `CHATTO_*` environment variables or `gateway.platforms.chatto` in Hermes config. Tested against Chatto v0.4.19 per the README.

## Equivalent in Claude
Reproduce the outbound half from Claude Code with curl or Python `urllib`, using the exact paths from `adapter.py`.

1. Log in: `POST $CHATTO_URL/auth/login` with JSON `{"login": "$CHATTO_LOGIN", "password": "$CHATTO_PASSWORD"}`. The response carries `success` and `token`; reuse the token as `Authorization: Bearer <token>` and re-login on 401.
2. Every other call is `POST $CHATTO_URL/api/connect/<Service>/<Method>` with headers `Content-Type: application/json`, `Connect-Protocol-Version: 1`, `Authorization: Bearer <token>`, and a JSON body.
3. Keep messages at or under 10000 characters (`_MAX_MESSAGE_LENGTH`); split longer text into several `CreateMessage` calls.

| Hermes behavior | How Claude does it |
|---|---|
| discover rooms | `chatto.api.v1.RoomDirectoryService/ListRooms` with body `{}` |
| join a room | `chatto.api.v1.RoomService/JoinRoom` with `{"roomId": "..."}` |
| read recent room events | `chatto.api.v1.RoomService/GetRoomEvents` with `{"roomId": "..."}` |
| read a thread | `chatto.api.v1.ThreadService/GetThreadEvents` with `{"roomId": "...", "threadRootEventId": "..."}` |
| send a message | `chatto.api.v1.MessageService/CreateMessage` with `{"roomId": "...", "body": "text"}`; add `"threadRootEventId"` to reply in a thread |
| start a DM | `chatto.api.v1.RoomService/StartDM` |
| react, edit, delete | `MessageService/AddReaction`, `RemoveReaction`, `UpdateMessage`, `DeleteMessage` |
| look up users | `UserService/ListUsers`, `GetUser`, `BatchGetUsers` |
| presence / status | `MyAccountService/UpdatePresence` (online=1, away=2, dnd=3), `UpdateCustomStatus` |
| upload a file | `AssetUploadService/CreateUpload`, `UploadChunk`, `CompleteUpload` |

Exact request fields for the services other than login, ListRooms, JoinRoom, GetRoomEvents and CreateMessage were not transcribed here; read `adapter.py` in the checkout or run `GetViewer` and inspect responses before relying on them.

Example:

```bash
TOKEN=$(curl -s -X POST "$CHATTO_URL/auth/login" -H 'Content-Type: application/json' \
  -d "{\"login\":\"$CHATTO_LOGIN\",\"password\":\"$CHATTO_PASSWORD\"}" | jq -r .token)
curl -s -X POST "$CHATTO_URL/api/connect/chatto.api.v1.MessageService/CreateMessage" \
  -H 'Content-Type: application/json' -H 'Connect-Protocol-Version: 1' \
  -H "Authorization: Bearer $TOKEN" -d '{"roomId":"ROOM_ID","body":"Hello from Claude"}'
```

## Setup
1. Have a Chatto account on the target server (a dedicated bot user is recommended).
2. Export `CHATTO_URL` (base URL such as `https://chat.example.com`), `CHATTO_LOGIN` and `CHATTO_PASSWORD`. Optional variables the plugin reads: `CHATTO_CHANNELS`, `CHATTO_HOME_CHANNEL`, `CHATTO_ALLOWED_USERS`, `CHATTO_ALLOW_ALL_USERS`, `CHATTO_REQUIRE_MENTION`, `CHATTO_AUTO_THREAD`, `CHATTO_FREE_RESPONSE_CHANNELS`, `CHATTO_CONTEXT_MESSAGES`, `CHATTO_HEARTBEAT_FILE`; only `CHATTO_HOME_CHANNEL` (a default room id) is meaningful outside the gateway.
3. Find room ids with `ListRooms` or, in the Chatto client, right-click a room and copy its id (per `after-install.md`).

## Limits
- No always-on listener: Claude does not run a WebSocket loop, so it cannot answer mentions or DMs on its own. Scheduled posts need a Claude Code scheduled task that runs the curl calls.
- The binary protobuf realtime protocol (`/api/realtime`) is not reproduced; use `GetRoomEvents` polling instead.
- Mention filtering, allowed-user checks, auto-thread, presence refresh and heartbeat file are gateway behaviors and are not replicated.
- The password is a plain credential sent to the user's own server; keep it in the environment, never in chat.
- No MCP package for Chatto was verified; none is listed.
- Not verified: calls were read from the plugin source, not executed against a server.

## Source
- Catalog entry (reviewed commit): https://github.com/jrimmer/hermes-chatto-plugin/tree/aab0a20635cb578253a8014bc8d93e1b32f020fc
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/chatto-platform.yaml
