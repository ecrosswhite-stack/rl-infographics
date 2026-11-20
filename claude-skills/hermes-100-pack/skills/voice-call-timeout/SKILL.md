---
name: voice-call-timeout
description: Reference card only. Describes the voice-call-timeout plugin, which makes the Hermes Discord adapter's voice-channel inactivity auto-leave timeout configurable with a /voice-timeout command (values like 20m, 1h 30m, 900, off) persisted to settings.json. Consult it when someone asks "what does voice-call-timeout do" or "how long does Hermes stay in a Discord voice call". It performs no work and should not trigger on Discord or voice tasks for Claude.
---
# Voice Call Timeout (Discord voice idle timer)

**Hermes original:** https://github.com/RenoMG/hermes-voice-call-timeout-plugin @ 80ea52e · tier: community · category: voice · license: no LICENSE file found
**Port class:** D — it monkeypatches `gateway.platforms.discord.DiscordAdapter` inside the Hermes gateway process; there is nothing to call from outside.

## What the Hermes plugin does
At startup it patches three `DiscordAdapter` methods (`__init__`, `_reset_voice_timeout`, `_voice_timeout_handler`) so the hard-coded voice inactivity timeout is read from `$HERMES_HOME/plugin-data/voice-call-timeout/settings.json` (default 300 s). It registers one command, `/voice-timeout`, accepting `status`, durations such as `20m`, `1h 30m` or `900`, and `off`/`disable`/`none` to stop auto-leave, and re-applies the value to live voice sessions immediately. No tools, hooks or env vars. This plugin is no longer in the current catalog (`still_in_catalog: false` in the classified row).

## Equivalent in Claude
None identified. Claude has no Discord voice adapter to patch.

## Setup
None.

## Limits
- Not portable: depends on private attributes of the Hermes Discord adapter (`VOICE_TIMEOUT`, `_voice_timeout_tasks`, `_voice_clients`).
- No LICENSE file in the checkout, so no upstream text is copied; behavior is summarized from the README and `__init__.py`.
- The duration parser (`parse_timeout_spec`) is trivial and not worth porting on its own.

## Source
- Catalog entry (reviewed commit): https://github.com/RenoMG/hermes-voice-call-timeout-plugin/tree/80ea52e64a4bae042b8e31d938de78a3d3f25669
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/voice-call-timeout.yaml
