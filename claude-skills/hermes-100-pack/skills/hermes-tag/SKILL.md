---
name: hermes-tag
description: Reference card only. Describes the Hermes Tag plugin, a Feishu/Lark (plus Slack and DingTalk) platform override that gives a Hermes group-chat bot bounded per-chat context (original images, notes, relevant replies) when @-mentioned, with Tier-0/Tier-1 memory, standing jobs and /tag admin privacy controls. Consult it when someone asks "what does hermes-tag do", "can Claude do Hermes Tag in Feishu", or compares it with Claude Tag. It performs no work and should not trigger on ordinary Feishu, Slack or chat tasks.
---
# Hermes Tag (Feishu context-selection layer)

**Hermes original:** https://github.com/DanielLi202/hermes-tag @ 250785b · tier: community · category: platform · license: MIT
**Port class:** D — it is a Hermes gateway platform override (Feishu/Slack/DingTalk adapters) with its own SQLite memory store; nothing runs outside the Hermes gateway.

## What the Hermes plugin does
Overrides Hermes' built-in Feishu platform (and adds Slack and DingTalk bindings) so that an @-mentioned bot in an allowlisted group answers from bounded evidence selected by a `ContextSelector` with scopes `focused_reply`, `thread`, `deictic_recent` and `plain`, instead of full-history RAG. Tier-0 is a short-term per-chat buffer of all group messages (requires the sensitive Feishu scope `im:message.group_msg` and `require_mention: false`); Tier-1 is long-term memory built only from @-mention interactions, isolated per chat. Chat commands: `/tag status`, `/tag admin count|clear|disable|audit`, `/tag standing add|confirm|list|cancel|pause|enable`. Requires `FEISHU_APP_ID` and `FEISHU_APP_SECRET` (Slack: `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`). Registers no agent tools; config lives under `platforms.feishu.extra.feishu_tag`.

## Equivalent in Claude
None as a port: the plugin's value is the inbound gateway loop, message buffering and memory store inside Hermes. The plugin's own README positions it as bringing "Claude-Tag-style capability" to Feishu; Claude Tag is the Claude that answers in a Slack channel, thread or DM, so for Slack workspaces use Claude Tag directly. No Claude-native equivalent for Feishu/Lark or DingTalk was identified. The upstream skill text is kept in `references/upstream-hermes-tag.md` for reference.

## Setup
None.

## Limits
- Not portable: Feishu WebSocket long-connection, per-chat SQLite buffers (`encryption_posture: plaintext-db-on-local-disk`), standing jobs and admin lifecycle commands all depend on the Hermes gateway and `lark-oapi` (pinned 1.6.9 by the plugin; PyPI has 1.8.0).
- The plugin buffers every message in enabled chats locally; its audit events never store message bodies. These privacy properties are not reproduced here because nothing is reproduced.
- Feishu platform limits noted upstream (one WebSocket per App ID, 5 QPS send cap, 30 MB media cap, no WS on Lark International) apply to any Feishu bot, not to Claude.

## Source
- Catalog entry (reviewed commit): https://github.com/DanielLi202/hermes-tag/tree/250785b9c7485918f142e961e15ac084063a37e2
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-tag.yaml
