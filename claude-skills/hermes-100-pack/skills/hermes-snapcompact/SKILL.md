---
name: hermes-snapcompact
description: Reference card for the Hermes "hermes-snapcompact" context engine, which archives old conversation turns as dense bitmap PNG frames that vision models read back at about one third of the token cost. Use it only when someone asks what snapcompact is, whether Claude can compact context into images, or how Hermes context engines map to Claude. It does not change how Claude compacts its own context.
---
# Snapcompact bitmap context compaction (reference card)

**Hermes original:** https://github.com/vimona3ds/hermes-snapcompact @ 8a274ca · tier: community · category: memory · license: MIT
**Port class:** D — it replaces the Hermes context-compaction engine (`ctx.register_context_engine`); Claude's compaction is built in and not pluggable.

## What the Hermes plugin does
Registers a `SnapcompactEngine` and a `/compact-mode` command with modes `summarize` (default, LLM prose summary) and `snapcompact`. In snapcompact mode, old turns are serialized to a compact text format (`¶user:`, `¶think:`, `¶ai:`, `¶call:` scopes with truncated tool output) and rendered to PNG frames by a Bun script (`bridge/render.ts`) that imports `@oh-my-pi/snapcompact`. Frame shapes are provider-aware (for example `11on16-bw` for Anthropic). The model then receives a reading guide, the frames, and verbatim text at the chronological edges. On load it sets `context.engine: snapcompact` in `~/.hermes/config.yaml` and only detects, never installs, Bun and the bridge dependencies. No LLM call is made for rendering.

## Equivalent in Claude
None identified for swapping the compaction engine. Claude Code's built-in `/compact` command is the nearest feature (prose summary, comparable to the plugin's `summarize` mode). The renderer is a standalone npm package: `npm view @oh-my-pi/snapcompact` returned name `@oh-my-pi/snapcompact`, version 19.0.1, license MIT, so Claude Code could render arbitrary text into frames with Bun if a user asks for that experiment, but it cannot feed those frames back into its own context window as a replacement for history.

## Setup
None.

## Limits
- Claude's context management is not pluggable; no `/compact-mode` equivalent.
- The bridge requires Bun 1.3.14+ and `bun install` in `bridge/`; not run during the port.
- The plugin README notes models spend extra output/thinking tokens decoding images and that non-vision models cannot read the frames.
- The README's token-cost and recall figures were not verified.

## Source
- Catalog entry (reviewed commit): https://github.com/vimona3ds/hermes-snapcompact/tree/8a274ca4a501e5661f1e2762150c4c3f99e374ce
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-snapcompact.yaml
