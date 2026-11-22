---
name: hermes-resetwatch
description: Reference card only. Describes hermes-resetwatch, a Hermes Desktop page that showed remaining subscription quota and reset clocks for Nous, Claude, Codex, Cursor, Kimi, GLM, DeepSeek and other vendors by reading logins already on the machine. It is a Hermes Desktop renderer plugin with no Claude equivalent. Use this card when someone asks "what did Resetwatch do", "can Claude show my quota bars like Resetwatch", or why it was not ported. Do not trigger on general billing or usage questions.
---
# Resetwatch (reference card)

**Hermes original:** https://github.com/Adolanium/hermes-resetwatch @ 3be7832 (subdir `catalog`) · tier: community · category: desktop · license: MIT
**Port class:** D · an Electron renderer page (`desktop/plugin.js`) plus a probe script executed through Hermes Desktop's `shell.exec` and gateway JSON-RPC; Claude has no desktop plugin surface or gateway RPCs to host it.

## What the Hermes plugin does
Standalone Hermes Desktop plugin with no tools, hooks or middleware (`register()` is empty). `desktop/plugin.js` adds a "Resetwatch" sidebar page with live quota cards and manual reset clocks. Numbers come from Hermes gateway RPCs (`usage.bars`, `subscription.state`, `account.usage`) and from `desktop/probe.py`, which reads local CLI/app logins (for example `$HERMES_HOME/auth.json`, `~/.claude`, `~/.codex`, Cursor, Kimi, Grok CLIs) and env keys (`DEEPSEEK_API_KEY`, `OPENCODE_GO_API_KEY`, `OLLAMA_API_KEY`, `MINIMAX_API_KEY`, `NOVITA_API_KEY`, `DEEPINFRA_API_KEY`, `AI_GATEWAY_API_KEY`, `COMMANDCODE_API_KEY`, `KIMI_API_KEY`, `ZAI_API_KEY`, `GLM_API_KEY`) to call each vendor's usage endpoint (e.g. `https://api.anthropic.com/api/oauth/usage`, `https://api.deepseek.com/user/balance`, `https://ollama.com/api/usage` per `probe.py`). Results are cached for 5 minutes under `$HERMES_HOME/cache/resetwatch`. The README warns that for Kimi and Grok the probe may refresh and rewrite OAuth tokens.

## Equivalent in Claude
None as a page. Nearest Claude-native feature for the Claude account alone: plan usage shown in the Claude app settings and Claude Code's `/usage` command (not verified in this session). For other vendors, Claude could on request call a vendor balance endpoint listed in `probe.py` with the user's own key, but that is ad hoc and not the plugin.

## Setup
None.

## Limits
- The Desktop page, sidebar entry, keyboard shortcut, manual clocks and 5-minute refresh are Hermes Desktop only.
- Gateway RPCs (`usage.bars`, `account.usage`) do not exist outside Hermes.
- Reading other tools' OAuth token files (`~/.claude`, `~/.codex`, Cursor, Kimi, Grok) is sensitive; the plugin does it locally and never prints tokens. Claude should not read those files unless the user explicitly asks.
- Token refresh side effects for Kimi/Grok noted in the README are not replicated and should not be.
- No upstream skills/ directory exists to copy.

## Source
- Catalog entry (reviewed commit): https://github.com/Adolanium/hermes-resetwatch/tree/3be783290fd66c6070af8eaf7a2286c7ef5e71c5/catalog
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-resetwatch.yaml
