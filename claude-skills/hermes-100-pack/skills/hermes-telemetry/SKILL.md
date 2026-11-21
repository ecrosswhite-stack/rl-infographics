---
name: hermes-telemetry
description: Reference card for the Hermes hermes-telemetry plugin, which hooked every Hermes API request, tool call and session boundary to record tokens, cost, latency and tool usage in a local SQLite database, refreshed OpenRouter pricing, and enforced daily/monthly spend budgets via /stats and /budget slash commands and a web dashboard. Not a working port. Consult it only when someone asks what hermes-telemetry did, why Claude has no equivalent budget enforcement, or where to see Claude Code's own session cost. Do not trigger for general observability or analytics work.
---
# Hermes Telemetry (reference card)

**Hermes original:** https://github.com/nujovich/hermes-telemetry @ 146f674 · tier: community · category: general · license: MIT
**Port class:** D · it is built entirely on Hermes runtime hooks (`pre_api_request`, `post_api_request`, `api_request_error`, `pre_llm_call`, `pre_tool_call`, ...) and Hermes slash commands; there is no API or file format for Claude to call.

## What the Hermes plugin does
Per plugin.yaml (`kind: standalone`) it registers twelve hooks: `on_session_start`, `pre_api_request`, `post_api_request`, `api_request_error`, `post_tool_call`, `post_llm_call`, `on_session_end`, `on_session_finalize`, `subagent_start`, `subagent_stop`, `pre_llm_call`, `pre_tool_call`; slash commands `/stats`, `/budget` and `/setup`; and a `hermes-telemetry` CLI (`stats today|week|month|cron|providers|models|efficiency|smells`, `budget`, `budget forecast`, `--from/--to`, `--json`). It writes `~/.hermes/telemetry/telemetry.db` (SQLite WAL), `telemetry.log`, `pricing.yaml` and `budget.yaml`, refreshes prices from `https://openrouter.ai/api/v1/models`, estimates tokens at 4 chars/token when usage is missing, detects cron sessions by id pattern, and blocks the next LLM call when a configured budget is breached. A separate web dashboard reads the same database.

## Equivalent in Claude
None identified as a port. Claude Code shows the current session's usage with the built-in `/cost` command; it reports, it does not enforce a cap. Per-tool latency logging, cron-job cost attribution, pricing refresh and hard budget blocking have no Claude-native counterpart that this card can point to with certainty.

## Setup
None.

## Limits
- Every measurement depends on Hermes hook payloads (usage dicts, tool names, session ids); Claude exposes no equivalent hook stream to a user plugin.
- Budget enforcement (blocking `pre_llm_call`) cannot be reproduced; agree on spend limits with the user verbally instead.
- The dashboard, `/setup` wizard, `pricing.yaml` overrides and `budget.yaml` hot reload (watchdog) are Hermes-only.
- No upstream SKILL.md exists to copy; the plugin ships none.

## Source
- Catalog entry (reviewed commit): https://github.com/nujovich/hermes-telemetry/tree/146f6744fc4117ade784eefd7aa231c9b3f36281
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-telemetry.yaml
