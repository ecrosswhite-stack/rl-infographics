---
name: yantrikdb
description: "Reference and partial port of the Hermes \"yantrikdb\" memory provider: a self-maintaining memory substrate (remember, recall with why_retrieved reasons, think, conflicts, relate, forget, tasks, knowledge gaps, agent-authored skills) backed by the yantrikdb Python engine in-process or a yantrikdb-server over HTTP. Use it when a user asks what the yantrikdb Hermes plugin did, wants to reuse an existing YantrikDB store from Claude Code, mentions YANTRIKDB_MODE, YANTRIKDB_URL, YANTRIKDB_TOKEN, \"contradiction tracking\", \"explainable recall\", or asks whether Claude can get Hermes-style long-term memory from YantrikDB. The automatic hooks (session end consolidation, pre-compress injection, memory-write mirroring) are not reproduced."
---
# YantrikDB memory

**Hermes original:** https://github.com/yantrikos/yantrikdb-hermes-plugin @ d7ccc7e · tier: community · category: memory · license: MIT
**Port class:** C · the engine (`yantrikdb` on PyPI) and the HTTP server are usable from Claude Code, but the plugin's value is in Hermes MemoryProvider hooks and system-prompt injection, which Claude has no runtime for.

## What the Hermes plugin does
Per plugin.yaml and the README, it is a Hermes memory provider with hooks `on_session_end`, `on_pre_compress`, `on_memory_write`, `on_delegation`, and `pip_dependencies` `yantrikdb>=0.12.1,!=0.15.0,!=0.15.1,!=0.15.2,<0.24.0` and `requests`. Default backend is in-process with a bundled `potion-base-2M` embedder; alternative `YANTRIKDB_MODE=http` talks to a `yantrikdb-server` (`YANTRIKDB_URL`, default example `http://localhost:7438`, `YANTRIKDB_TOKEN`). Tools exposed to the agent (README "What it does"): `yantrikdb_remember`, `_recall`, `_forget`, `_think`, `_conflicts`, `_resolve_conflict`, `_relate`, `_stats`, trigger consumers `_pending_triggers`, `_acknowledge_trigger`, `_dismiss_trigger`, `_act_on_trigger`, and opt-in `_skill_search`, `_skill_define`, `_skill_outcome` (`YANTRIKDB_SKILLS_ENABLED=true`); the README elsewhere also names `_hygiene`, `_knowledge_gaps`, `_recent_turns`, `_tasks`, `_packs`. Before each compression it injects the highest-salience memories; at session end it runs `think()` to canonicalize duplicates and surface contradictions. Other env toggles named in the README: `YANTRIKDB_OWNER_SCOPING`, `YANTRIKDB_SHARED_BRAIN_NAMESPACE`, `YANTRIKDB_FLEET_VIEW`, `YANTRIKDB_PACKS_ENABLED`, `YANTRIKDB_AUTO_MOUNT_PACKS`, `YANTRIKDB_TOOL_PROFILE`, `YANTRIKDB_AUTO_GAP_TASKS`, `YANTRIKDB_SURFACE_AGENDA`, `YANTRIKDB_MAINTENANCE_CADENCE_TURNS`, `YANTRIKDB_MAINTENANCE_MIN_INTERVAL_SECONDS`, `YANTRIKDB_SHARE_ENGINE`, `YANTRIKDB_INCLUDE_BASE_NAMESPACE_RECALL`. Standing rules live in `$HERMES_HOME/yantrikdb-constitution.md`.

## Equivalent in Claude
What can be reproduced is explicit read/write access to a YantrikDB store the user already has, on request:

1. Engine access from Python in Claude Code: `python -m pip install yantrikdb` (verified with `pip index versions yantrikdb`: latest `0.23.4`; the plugin pins `<0.24.0`). The engine's Python API (`remember()`, `recall()`, `think()`, `conflicts()`, `resolve_conflict()`, `relate()`, `forget()`) is named in the plugin README; exact signatures were not verified here, so read the installed package's docstrings (`python -c "import yantrikdb, inspect; help(yantrikdb)"`) before calling.
2. Server access: if the user runs `yantrikdb-server` (README: `docker run -d -p 7438:7438 ... ghcr.io/yantrikos/yantrikdb:latest`, token via `yantrikdb token ... create`), use `YANTRIKDB_URL` and `YANTRIKDB_TOKEN` as a bearer credential. The HTTP route names were not in the plugin checkout and are not verified; consult https://github.com/yantrikos/yantrikdb-server.
3. MCP option: a package named `yantrikdb-mcp` exists on PyPI (verified with `pip index versions yantrikdb-mcp`: latest `0.24.0`). Its launch command and tool list were not verified in this port; check its PyPI page before adding it to `claude_desktop_config.json`.

| Hermes tool | Claude path |
|---|---|
| `yantrikdb_remember`, `_recall`, `_forget`, `_relate`, `_conflicts`, `_resolve_conflict`, `_think`, `_stats` | engine Python API or server HTTP, called explicitly when the user asks |
| hooks (`on_pre_compress`, `on_session_end`, `on_memory_write`) | none; run `think()` manually at the end of a long task if asked |
| constitution file | paste the user's `yantrikdb-constitution.md` into CLAUDE.md if they want standing rules in Claude Code |

## Setup
1. `pip install yantrikdb` in a Python 3.11+ environment, or run `yantrikdb-server` and set `YANTRIKDB_MODE=http`, `YANTRIKDB_URL`, `YANTRIKDB_TOKEN`.
2. Optional: evaluate `yantrikdb-mcp` from PyPI (not verified beyond its existence).

## Limits
- No automatic recall before turns, no pre-compression injection, no session-end consolidation, no owner scoping, fleet view, packs, triggers or self-directing gap-to-task loop: all of these ride on Hermes hooks.
- The engine and server APIs were not exercised; this skill names only what the plugin README names.
- The bundled embedder and `yantrikdb` engine download roughly 10 MB per the README.
- Claude Code's own memory (CLAUDE.md, auto memory) is unrelated to this store.

## Source
- Catalog entry (reviewed commit): https://github.com/yantrikos/yantrikdb-hermes-plugin/tree/d7ccc7ec423591438f1897ad9a2f4ca197500fe5
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/yantrikdb.yaml
