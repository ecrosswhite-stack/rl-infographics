---
name: bridge-adapter
description: Reference card only. Describes the Hermes "bridge-adapter" gateway plugin, a JSON-file inbox/outbox bridge that let external chat services (iMessage, Matrix, Telegram wrappers) talk to the Hermes Gateway through a shared directory. Use this card when a user asks what bridge-adapter did, whether Claude can act as a Hermes bridge, or how to read a BRIDGE_DIR layout. It does not make Claude a chat gateway; do not trigger it for real messaging work.
---
# Bridge Adapter (reference card)

**Hermes original:** https://github.com/Kesuek/hermes-bridge-adapter @ 406a53d · tier: community · category: platform · license: MIT
**Port class:** D · it is a Hermes Gateway platform adapter; Claude has no gateway process, inbox poller or MessageEvent dispatcher to plug into.

## What the Hermes plugin does
Per the README, the adapter is a `kind: platform` plugin for the Hermes Gateway. Instead of each messaging platform connecting to the Gateway directly, an external "wrapper" script exchanges JSON files with the adapter in `BRIDGE_DIR`: wrappers write `inbox/<bridge>/` and `status/<bridge>/`, the adapter polls them and writes replies to `outbox/<bridge>/`, with attachments under `media/<bridge>/{incoming,outgoing}/`. Bridges self-register by dropping a manifest in `registry/<bridge>.yaml` (presence = registered, remove = unregistered). It also implements "Unified Threads": several bridges sharing one agent session, cross-bridge reply chains, identity claims and message relay. It registers no agent tools (`cat_tools` is empty); `register()` in `adapter.py` registers the platform adapter class with the Hermes plugin context.

## Equivalent in Claude
None identified. Claude Code and Cowork have no long-running gateway loop that polls a directory and dispatches inbound chat messages to a session. The JSON file contract itself (inbox, outbox, status, registry schemas in the README) is readable by Claude, so Claude can inspect or hand-write such files on request, but nothing consumes them on the Claude side.

## Setup
None.

## Limits
- No Hermes Gateway in Claude, so no inbox polling, outbox writing, typing indicators, reactions, or unified threads.
- The plugin's env vars (`BRIDGE_DIR`, `BRIDGE_POLL_INTERVAL`, `BRIDGE_ALLOWED_USERS`, `BRIDGE_ALLOW_ALL_USERS`, `BRIDGE_HOME_CHANNEL`, `BRIDGE_AGENT_HANDLE`, per plugin.yaml) have no meaning in Claude.
- The bundled wrappers (`wrappers/imsg-wrapper.py`, `wrappers/talk-wrapper.py`) target Hermes-side services and were not ported.
- Hermes Gateway chat platforms (Telegram, Discord, Slack and others) are Hermes features; Claude's own chat integrations are configured through claude.ai connectors, not through this plugin.

## Source
- Catalog entry (reviewed commit): https://github.com/Kesuek/hermes-bridge-adapter/tree/406a53d75cd68378067dddc7273d4261c0155fd5
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/bridge-adapter.yaml
