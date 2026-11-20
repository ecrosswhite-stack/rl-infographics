---
name: time-gap
description: Reference card for the Hermes "time-gap" plugin, a pre_llm_call hook that silently appended a coarse "[time-gap: about 2 days have passed since the previous exchange]" note to the user turn when a conversation resumed after a configurable gap or across local midnight. Consult it only when a user asks what this plugin did or how to give Claude a sense of elapsed time between messages; it does not run anything itself.
---
# Time Gap (reference card)

**Hermes original:** https://github.com/Randool/time-gap @ bc5e655 · tier: community · category: general · license: no LICENSE file found
**Port class:** D — a Hermes `pre_llm_call` hook reading Hermes' `state.db`; Claude skills cannot intercept the prompt before each model call.

## What the Hermes plugin does
Registers one hook, `pre_llm_call`, and no tools. Per `__init__.py` it opens `$HERMES_HOME/state.db` read-only (`mode=ro`), takes `MAX(timestamp)` of the session's assistant messages, and if the elapsed time is at least `min_gap_seconds` (default 7200) or the local calendar date rolled over (`notify_date_change`, default true, timezone from `hermes_time.get_timezone`), returns `{"context": "[time-gap: about N hours/days have passed since the previous exchange (today is Weekday, YYYY-MM-DD)] (Your own sense of time, never quote or mention it. Just factor it in: earlier context or the current date may be stale; re-ground if needed.)"}`. The note rides on the current user turn only, is never written to history, is skipped for `exclude_platforms` (default `cron`), and every failure path returns nothing.

## Equivalent in Claude
None identified as a skill. Claude Code can run user-configured hooks from `settings.json` that add context to a turn, which is the closest native mechanism, but no hook script is provided here and Claude Code does not expose a per-session message timestamp store equivalent to `state.db`. Claude Code's system prompt does carry today's date, so date rollover is already visible to the model.

## Setup
None.

## Limits
- No elapsed-time signal between turns within a Claude conversation.
- Configuration keys (`min_gap_seconds`, `notify_date_change`, `exclude_platforms`, `debug`) have no Claude counterpart.
- No LICENSE file in the checkout, so no upstream text is copied.

## Source
- Catalog entry (reviewed commit): https://github.com/Randool/time-gap/tree/bc5e65503a412808029573a98b6008387a0ac2f6
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/time-gap.yaml
