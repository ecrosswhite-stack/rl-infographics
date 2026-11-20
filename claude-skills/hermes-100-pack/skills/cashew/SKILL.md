---
name: cashew
description: Reference card for the Hermes "cashew" memory-provider plugin (persistent thought-graph memory with local embeddings, decay and think cycles). Use it only when someone asks what Cashew / hermes-cashew is, whether Claude can use a Cashew brain.db, or how Hermes memory providers map to Claude. It does not add a memory backend to Claude and should not trigger on ordinary "remember this" requests.
---
# Cashew thought-graph memory (reference card)

**Hermes original:** https://github.com/magnus919/hermes-cashew @ d89e59e · tier: community · category: memory · license: Apache-2.0
**Port class:** D — it is a Hermes memory provider wired into Hermes session hooks, auxiliary LLM roles and the Hermes cron scheduler; Claude has no plugin slot for a memory provider.

## What the Hermes plugin does
Cashew registers a `CashewMemoryProvider` with Hermes (`ctx.register_memory_provider`). It stores conversation knowledge in a local SQLite "thought graph" (`$HERMES_HOME/cashew/brain.db`) using `cashew-brain`, `sentence-transformers` embeddings (default model `thenlper/gte-large`, 1024-dim) and `sqlite-vec` similarity search. It exposes two LLM tools, `cashew_query` (semantic search with `domain`, `tag`, `exclude_tags` filters) and `cashew_extract` (persist a turn), prefetches graph context into the system prompt at session start, and hooks `on_session_end` and `on_pre_compress` to extract insights. Graph consolidation ("sleep cycle") runs as a Hermes `no_agent` cron job (default `every 12h`). LLM-powered extraction uses the Hermes `auxiliary.memory` role when configured, otherwise heuristic extraction only. Configuration lives in `~/.hermes/cashew.json`, overridable with `CASHEW_*` environment variables.

## Equivalent in Claude
None identified as a drop-in. Claude cannot install a memory provider or run session-boundary hooks. The nearest Claude-native features are the Claude Code memory files (`CLAUDE.md` and the per-project memory directory), which are plain text rather than an embedded graph. The underlying library `cashew-brain` is published on PyPI (`pip index versions cashew-brain` returned 1.2.1), so Claude Code could read an existing `brain.db` with a Python script if a user asks, but the plugin pins a forked source archive and that compatibility was not verified.

## Setup
None.

## Limits
- No automatic recall or extraction: Hermes hooks (`on_session_end`, `on_pre_compress`), prompt prefetch and the cron sleep cycle have no Claude equivalent.
- `cashew_query` / `cashew_extract` tools are not available in Claude.
- The plugin pins `cashew-brain` to a GitHub source archive (not the PyPI 1.2.1 release) and requires SQLite 3.35+ and `sqlite-vec`; none of this was run during the port.
- Embedding models download from Hugging Face and run locally; LLM extraction, when enabled, spends tokens on the configured auxiliary provider.
- Optional Sentry/OpenTelemetry diagnostics (`HERMES_CASHEW_SENTRY_DSN`, `HERMES_CASHEW_OTEL_ENABLED`) send telemetry to third parties when enabled.

## Source
- Catalog entry (reviewed commit): https://github.com/magnus919/hermes-cashew/tree/d89e59e63315f7c356c868a4ce7db64cb3c1aa1b
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/cashew.yaml
