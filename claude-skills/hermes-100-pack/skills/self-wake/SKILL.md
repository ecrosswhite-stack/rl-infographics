---
name: self-wake
description: Reference card for the Hermes "self-wake" plugin, which wakes an existing Hermes gateway session when a Kanban task reaches a terminal state or a cron delivery succeeds, with durable receipts and a doctor tool. Use it only when someone asks what self-wake is, how Hermes internal session wake works, or what the Claude equivalent of waking a session on a schedule or event is. It does not install anything in Claude.
---
# Hermes self-wake (reference card)

**Hermes original:** https://github.com/mentatzoe/hermes-self-wake-plugin @ e6057e0 · tier: community · category: automation · license: Apache-2.0
**Port class:** D — it wraps private Hermes gateway internals (`GatewayRunner.wake_session`, cron `_deliver_result`, `SessionStore`) behind exact-host SHA checks; nothing of it applies outside Hermes. The catalog row marks it as no longer in the catalog (`still_in_catalog: false`).

## What the Hermes plugin does
Registers tools `self_wake_sessions` (resolve target sessions), `self_wake_subscribe_kanban` (subscribe a Kanban task so terminal events wake a session, with dry-run), `self_wake_receipts` (durable wake receipts, `source_kind` kanban or cron_delivery) and `self_wake_doctor` (per-surface capability report), the `/self-wake` command, a `pre_llm_call` hook, and the bundled skill `kanban-self-wake`. A compat shim (`self_wake.compat_shim_enabled: true` in `config.yaml`) installs two wrappers around Hermes cron delivery so each successful platform/chat route wakes the owning session (`cron.wake_agent_on_delivery: true`). It refuses to install if the host commit or the SHA-256 of four private callables differs from the supported Hermes commit (`21895bd3`).

## Equivalent in Claude
Claude Code scheduled tasks are the nearest feature: in the environment used for this port they can fire a prompt into the current session, into a named existing session, or into a fresh session on a cron or one-shot schedule, which covers the "resume the session that owns the work" intent. There is no Kanban-event subscription or receipt ledger.

## Setup
None.

## Limits
- No Hermes gateway, session store or cron delivery router exists in Claude; the four tools cannot be reproduced.
- The plugin's safety model (exact-host digest matching, fail-closed drift detection) is specific to Hermes internals.
- The upstream skill is copied for reference at `references/upstream-kanban-self-wake.md`; its instructions name Hermes tools only.

## Source
- Catalog entry (reviewed commit): https://github.com/mentatzoe/hermes-self-wake-plugin/tree/e6057e049f0ee55c5e7e69a38c2bcdebb0bc8fbf
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/self-wake.yaml
