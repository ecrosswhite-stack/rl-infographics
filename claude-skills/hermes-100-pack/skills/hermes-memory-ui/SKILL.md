---
name: hermes-memory-ui
description: Reference card for the Hermes "hermes-memory-ui" plugin, a read-only Hermes Dashboard and Hermes Desktop page for inspecting built-in, holographic, Mem0, Honcho, Mnemosyne, Hindsight and ByteRover memory. Use it only when someone asks what this plugin is, whether Claude has a memory inspector like it, or where Hermes keeps its memory files. It adds no UI to Claude and should not trigger on ordinary memory requests.
---
# Hermes Memory UI (reference card)

**Hermes original:** https://github.com/xraysight/hermes-memory-ui @ 9472bed · tier: community · category: desktop · license: MIT
**Port class:** D · it is a Hermes Dashboard/Desktop renderer plugin plus a FastAPI backend mounted inside the Hermes dashboard process; neither surface exists in Claude.

## What the Hermes plugin does
Adds a `Memory` tab (Dashboard) and a `/memory` full-page route, sidebar item and command-palette action (Desktop) backed by a shared read-only API mounted at `/api/plugins/hermes-memory-ui/`. Endpoints per `README-API.md`: `/status`, `/builtin` (parses `$HERMES_HOME/memories/MEMORY.md` and `USER.md`), `/session-search` (wraps Hermes's `session_search` tool), `/holographic` (SQLite fact store, default `$HERMES_HOME/memory_store.db`), `/mem0`, `/honcho`, `/byterover` and `/byterover/query` (ByteRover `brv` CLI), `/hindsight` plus `/contents`, `/recall`, `/reflect`, `/mnemosyne` plus `/contents`, `/recall`, `/prefetch`, and `/snapshot`. The root `register()` is a no-op; it registers no agent tools, commands or hooks. It is intentionally read-only and never writes memory.

## Equivalent in Claude
None identified. Claude has no plugin-rendered dashboard pages. If a Hermes profile exists on the machine, Claude Code can read the same built-in memory files directly (`$HERMES_HOME/memories/MEMORY.md`, `$HERMES_HOME/memories/USER.md`, entries separated by `§` per the plugin source) and open `$HERMES_HOME/memory_store.db` read-only with `sqlite3`, but the provider-specific views (Mem0, Honcho, Hindsight, Mnemosyne, ByteRover) depend on Hermes provider configuration and were not ported.

## Setup
None.

## Limits
- No Dashboard tab, Desktop route, sidebar item or command-palette action in Claude.
- `/session-search` depends on Hermes's internal `session_search` tool and session database.
- External provider sections read Hermes `config.yaml` and `.env` for Mem0, Honcho, Hindsight, Mnemosyne and ByteRover credentials; Claude does not have that configuration.
- The plugin's backend routes are only mounted by a running Hermes dashboard or gateway (port 9119 in the README examples); nothing here starts one.

## Source
- Catalog entry (reviewed commit): https://github.com/xraysight/hermes-memory-ui/tree/9472bed7e20a51ac4f6c48f882bd9f80ea54d4ee
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-memory-ui.yaml
