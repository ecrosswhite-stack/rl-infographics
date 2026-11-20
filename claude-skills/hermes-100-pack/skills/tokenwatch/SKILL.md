---
name: tokenwatch
description: Reference card for the Hermes "tokenwatch" plugin, which hooked pre/post_api_request to count input, output, cache and reasoning tokens per session, day or all time, warned at 50/80/95 percent of a configured budget, and froze further tool calls and gateway dispatches when the limit tripped. Consult it only when a user asks what this plugin did or whether Claude can enforce a hard token budget; it does not meter anything itself.
---
# TokenWatch (reference card)

**Hermes original:** https://github.com/0xBernard/tokenwatch @ b06c293 · tier: community · category: general · license: no LICENSE file found
**Port class:** D — implemented as six Hermes lifecycle hooks (`pre_api_request`, `post_api_request`, `pre_tool_call`, `pre_gateway_dispatch`, `on_session_start`, `on_session_end`) plus gateway interrupts; Claude has no skill-level hook that can block its own tool calls on a counter.

## What the Hermes plugin does
No tools. It accumulates `input_tokens`, `output_tokens`, cache read/write and reasoning tokens from each API response into counters scoped `session`, `daily` or `all_time`, compares against `limit_total_tokens`, `limit_input_tokens`, `limit_output_tokens`, emits warnings at `warning_levels` (default 0.5, 0.8, 0.95) and a predicted-limit warning, and when `freeze_on_limit` is on blocks later tool calls via the `pre_tool_call` block directive, skips new gateway dispatches, injects a CLI interrupt and asks the gateway session to stop. Notifications go to the console, the active gateway channel (`notification_channel`, `notification_platform`) or an HTTP webhook (`notify_webhook_url`, JSON POST with plugin, level, message, scope, session_id, model, provider, platform, timestamp). Commands: `/tokenwatch status|reset|unfreeze`, `hermes tokenwatch ...`. Config and state paths can be overridden with `HERMES_TOKENWATCH_CONFIG` and `HERMES_TOKENWATCH_STATE`. Installed with `python install.py --interactive`.

## Equivalent in Claude
None identified. Claude cannot read its own per-request usage from inside a skill or refuse tool calls based on a running total. Budget control in Claude is an account or product setting, not something a skill can enforce.

## Setup
None.

## Limits
- No token counting, thresholds, freeze, webhook or gateway notifications.
- The README itself notes Hermes cannot cancel the exact LLM request that crosses the budget, so even upstream the freeze is best-effort.
- No LICENSE file in the checkout, so no upstream text is copied.

## Source
- Catalog entry (reviewed commit): https://github.com/0xBernard/tokenwatch/tree/b06c293e254d7af6d889fdfa07934a9fc5ca38a7
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/tokenwatch.yaml
