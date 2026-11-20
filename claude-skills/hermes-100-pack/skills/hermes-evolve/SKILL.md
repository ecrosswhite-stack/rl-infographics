---
name: hermes-evolve
description: Reference card for the Hermes hermes-evolve plugin, which added a "/evolve now" slash command to hot-reload Hermes plugin modules and invalidate stored system prompts in Hermes's state.db. Not a working port. Consult it only when someone asks what "/evolve" did in Hermes, why there is no Claude equivalent, or how to pick up changed skills and MCP servers in Claude Code. Do not trigger for ordinary coding or reload requests.
---
# Hermes Evolve (reference card)

**Hermes original:** https://github.com/nuffin/hermes-evolve @ 941c0b1 · tier: community · category: general · license: no LICENSE file found (README states MIT, but the checkout has no LICENSE file; catalog row lists no license; plugin is no longer in the live catalog)
**Port class:** D — Hermes self-management: it reaches into Hermes's module registry, tool cache and session database.

## What the Hermes plugin does
Registers one slash command, `/evolve` (plugin.yaml declares no tools or hooks). Per `__init__.py`, `/evolve status` lists loaded plugin modules under `~/.hermes/plugins/` and the bundled `plugins/` directory and flags files modified in the last hour. `/evolve now` re-executes each loaded plugin module in place with `importlib`, calls `hermes_cli.plugins.discover_plugins(force=True)` to re-run every plugin's `register(ctx)`, clears `model_tools._tool_defs_cache` and bumps `registry._generation`, then opens Hermes's `state.db` with sqlite3 and nulls `sessions.system_prompt` / `system_prompt_hash` (deleting orphaned `system_prompts` rows) so every active session rebuilds its system prompt on the next turn without losing history.

## Equivalent in Claude
None identified. Claude Code has no in-session hot reload of its own runtime that this maps to; skills, plugins and MCP server definitions are read when a session starts, so start a new session (or restart the Claude Code process) after editing them. Claude Code does not store a frozen per-session system prompt in a user-editable database.

## Setup
None.

## Limits
- Every step of `/evolve now` targets Hermes internals (`hermes_cli.plugins`, `model_tools`, `hermes_state.DEFAULT_DB_PATH`); none exists in Claude.
- Rewriting another process's SQLite session store is unsafe outside the Hermes design; do not imitate it against Claude's own state files.
- No upstream text copied because the checkout has no LICENSE file.

## Source
- Catalog entry (reviewed commit): https://github.com/nuffin/hermes-evolve/tree/941c0b11a3afa18a88cd26ce1612c0e017525f42
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-evolve.yaml
