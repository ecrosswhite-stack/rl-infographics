---
name: minecraft-platform
description: Reference card for the Hermes Minecraft gateway adapter, which runs a Mineflayer bot inside a Minecraft server and relays player chat to Hermes sessions. Not a working skill. Read it only when someone asks what minecraft-platform did or whether Claude can be chatted with from inside Minecraft (it cannot through this pack).
---
# Minecraft Platform (reference card)

**Hermes original:** https://github.com/kyssta-exe/hermes-minecraft-gateway @ 8ff37a6 · tier: community · category: platform · license: MIT
**Port class:** D — a `kind: platform` gateway adapter (`BasePlatformAdapter` subclass) whose purpose is to make Hermes reachable from a chat platform; Claude has no gateway to plug it into.

## What the Hermes plugin does
Spawns a Node.js bridge (`bridge/index.js`, Mineflayer bot plus a local HTTP server on `MINECRAFT_BRIDGE_PORT`, default 13000) that joins a Minecraft server, idles and wanders, and queues player chat. The Python adapter polls the bridge, gives each player their own Hermes session, converts markdown to Minecraft section-sign codes, chunks replies to 256 characters, supports `$new`, `$help`, `$model`, `$stop` style commands via `MINECRAFT_PREFIX`, and private tool progress via `/tell`. Env vars: `MINECRAFT_ENABLED`, `MINECRAFT_SERVER` (required); `MINECRAFT_PORT`, `MINECRAFT_USERNAME`, `MINECRAFT_AUTH` (offline or microsoft), `MINECRAFT_PREFIX`, `MINECRAFT_PRIVATE_MESSAGES`, `MINECRAFT_BRIDGE_PORT`, `MINECRAFT_ALLOWED_USERS`, `MINECRAFT_ALLOW_ALL_USERS`, `MINECRAFT_HOME_CHANNEL`. No tools or hooks.

## Equivalent in Claude
None. Claude Code and the Claude desktop app do not expose a message gateway that a chat-platform adapter could feed. The bot library itself is public (`npm view mineflayer` -> `mineflayer` 4.39.0), so Claude could help write or debug a Mineflayer bot as ordinary code, but that is not this plugin's function.

## Setup
None.

## Limits
- No per-player sessions, no in-game commands, no chat relay.
- Nearest Claude-native feature: none identified.
- The adapter runs `npm install` and a persistent Node process; `MINECRAFT_ALLOW_ALL_USERS=true` lets any player on the server drive the agent, a risk the README flags as "dev only".

## Source
- Catalog entry (reviewed commit): https://github.com/kyssta-exe/hermes-minecraft-gateway/tree/8ff37a626439caecb9ceb724b5da7718eb77a8b1
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/minecraft-platform.yaml
