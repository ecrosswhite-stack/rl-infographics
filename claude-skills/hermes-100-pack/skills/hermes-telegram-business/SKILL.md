---
name: hermes-telegram-business
description: Reference card for the official Hermes hermes-telegram-business plugin, a Telegram Business Mode "secretary bot" that drafts replies to incoming customer messages and sends them to the account owner with Send / Edit / Discard buttons, never auto-sending. Not a working port. Consult it only when someone asks what the Hermes Telegram Business plugin did, why Claude cannot run it, or wants the drafting rules it used. Do not trigger for general Telegram or messaging questions.
---
# Hermes Telegram Business (reference card)

**Hermes original:** https://github.com/NousResearch/hermes-telegram-business @ e905f3b · tier: official · category: platform · license: MIT
**Port class:** D — a gateway/chat-platform adapter: it hooks python-telegram-bot handlers into the Hermes Telegram gateway via `ctx.register_telegram_handler` and drafts through the host LLM surface `ctx.llm`.

## What the Hermes plugin does
Registers no tools or hooks (plugin.yaml) but one Telegram handler factory. Per `__init__.py` and manager.py it adds a `BusinessConnectionHandler`, `MessageHandler`s for `business_message` and `edited_business_message` (text only), a `CallbackQueryHandler` on the `bd:` prefix for the draft buttons, an owner-DM handler for Edit capture (group -1, raises `ApplicationHandlerStop` when it consumes the text) and a `/biz` command (status, pause, resume, on/off per chat). Incoming customer text is debounced 8 s, drafted once by `ctx.llm.complete` with a persona system prompt, and DMed to the owner with inline [Send] [Edit] [Discard]; Send goes out via `business_connection_id` only when Telegram granted `can_reply`. Drafts expire after 24 h. State is SQLite at `<HERMES_HOME>/telegram-business/state.db`. Config lives under `plugins.entries.telegram-business` (`debounce_seconds`, `draft_ttl_hours`, `max_customer_text_chars`, `owner_persona`).

## Equivalent in Claude
None identified. Claude Code and Cowork have no Telegram gateway to receive Business Mode updates or send on a user's behalf. The drafting instruction can be reused manually: per the source the system prompt is the persona ("draft a short, friendly reply on behalf of the account owner ... do not introduce yourself as an assistant or AI ... reply in the same language the customer used") followed by "Output only the message text. No preamble, no quotes, no markdown headers. Keep it under 4 sentences unless the customer asked something that genuinely needs a longer reply." Paste a customer message and ask Claude to draft under those rules; the user then sends it themselves.

## Setup
None.

## Limits
- Requires a Hermes gateway with `register_telegram_handler` (hermes-agent v0.18+), python-telegram-bot 21.1+, a Telegram Business subscription and a bot with Business Mode enabled in BotFather; none applies to Claude.
- The approval loop (buttons, debounce, edit capture, owner-only authorization, 24 h expiry) is not reproduced.
- The plugin itself notes v1 limits: text only, no conversation history, no learning from edits.

## Source
- Catalog entry (reviewed commit): https://github.com/NousResearch/hermes-telegram-business/tree/e905f3bc5eeaa5a9dab9bc5155601b3ebec75757
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-telegram-business.yaml
