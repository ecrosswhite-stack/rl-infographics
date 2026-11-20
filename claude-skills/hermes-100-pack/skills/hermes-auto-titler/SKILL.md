---
name: hermes-auto-titler
description: Reference card only. Describes the Hermes plugin hermes-auto-titler, which periodically re-evaluated and rewrote Hermes session titles with an auxiliary model while never overriding user-set titles. There is no Claude equivalent because it depends on Hermes SessionDB, Hermes lifecycle hooks and Hermes auxiliary-model routing. Use this card when someone asks "what did hermes-auto-titler do", "can Claude auto-rename my sessions like the Hermes titler", or needs to explain why the port is not possible. Do not trigger on ordinary requests to summarize or name a document.
---
# Hermes Auto Titler (reference card)

**Hermes original:** https://github.com/Vocllum/hermes-auto-titler @ 307993c · tier: community · category: automation · license: Apache-2.0
**Port class:** D · session-title maintenance wired into Hermes hooks, SessionDB and the host's auxiliary `title_generation` task; Claude exposes none of these surfaces to a skill.

## What the Hermes plugin does
Registers the hooks `on_session_end` and `on_session_finalize` (no tools). After every N foreground turns (default 4) and at session close, it builds a compact context (opening turns, recent turns, the full user-message trajectory, compaction summary), asks an auxiliary model for strict JSON `{"action":"keep"}` or `{"action":"rename","title":"..."}`, and writes the new title into the Hermes session database while enforcing provenance `derived < llm < user` so user-set titles are never overwritten. It adds `/autotitler status|config|rename-now|retitle-all` commands, rename throttles (`min_interval_minutes`, `renames_per_hour`, `rename_confirmations`), and reads its own `config.yaml`. The README discloses that conversation excerpts are sent to the configured model provider and billed there.

## Equivalent in Claude
None. Claude Code and Cowork do not expose a session-title store or a turn-boundary hook that a skill could use to rewrite titles. Nearest Claude-native feature: none identified. Claude can, on request, propose a short title for a transcript the user pastes (the plugin's prompt rules: 12-char soft target, 24-char hard max, subject label not last message, keep brand casing), but that is manual and not the plugin's automation.

## Setup
None.

## Limits
- Hooks, periodic evaluation, SessionDB writes, provenance enforcement and the `/autotitler` commands are all Hermes-internal; nothing is replicated.
- The plugin's model routing (`provider`/`model` overrides, `allow_task_override`) has no Claude counterpart.
- Cost and privacy disclosure from the README (session excerpts sent to a model provider per evaluation) does not apply to Claude because nothing runs.
- No upstream skills/ directory exists to copy, although the license (Apache-2.0) would have allowed it.

## Source
- Catalog entry (reviewed commit): https://github.com/Vocllum/hermes-auto-titler/tree/307993c36e261af2769e486befc6841e96f93423
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-auto-titler.yaml
