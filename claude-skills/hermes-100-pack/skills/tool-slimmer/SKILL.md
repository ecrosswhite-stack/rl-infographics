---
name: tool-slimmer
description: "Reference card for Hermes Tool Slimmer, a Hermes plugin that shrinks the per-request tool-schema payload by BM25-ranking tools and reports estimated token savings in the Hermes dashboard. Not a working skill. Read it only when someone asks what tool-slimmer did, or how Claude handles large tool catalogs (answer: Claude Code defers tools and loads them on demand via ToolSearch)."
---
# Tool Slimmer (reference card)

**Hermes original:** https://github.com/aliasocracy/hermes-tool-slimmer @ 3128c8f · tier: community · category: tools · license: MIT
**Port class:** D · it patches Hermes request construction (`select_tool_schemas` hook / core patch) and ships a Hermes dashboard plugin; both are Hermes-internal.

## What the Hermes plugin does
Registers `tool_slimmer_select`, `tool_slimmer_status`, `tool_slimmer_request_full_tools`, `tool_slimmer_hydrate_tools`, a `pre_llm_call` hook, the optional `select_tool_schemas` selector hook, a `/tool-slimmer` slash command and a `hermes tool-slimmer` CLI (`status`, `doctor`, `index`, `select`, `benchmark`, `eval`, `advisor`, `privacy`, `diagnostics`). Modes: `eager`, `keyword` (BM25 plus boosts), `hybrid`, `anthropic_tool_search`, experimental `two_pass`. It fails open to the full schema list on errors, keeps `always_include` tools, and shows "estimated schema tokens saved" (bytes/4) in the dashboard. The README notes that recent Hermes builds have a native progressive tool loader that is usually the better default.

## Equivalent in Claude
None to port: Claude Code already defers rarely used tools and loads their schemas on demand through the built-in `ToolSearch` tool, which is the same goal (less schema overhead per request). Users cannot tune ranking, `top_k`, profiles, or see savings counters.

## Setup
None.

## Limits
- No deterministic keyword selector, no `always_include`/`always_exclude` lists, no dashboard metrics, no eval/benchmark CLI.
- The PyPI name `hermes-tool-slimmer` from `pyproject.toml` is not published (`pip index versions hermes-tool-slimmer` found no distribution at the time of this port).
- Savings figures in the README are estimates, as the README itself states.

## Source
- Catalog entry (reviewed commit): https://github.com/aliasocracy/hermes-tool-slimmer/tree/3128c8fe3c27694c7d2f2dd16e5d639cf65b63f6
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/tool-slimmer.yaml
