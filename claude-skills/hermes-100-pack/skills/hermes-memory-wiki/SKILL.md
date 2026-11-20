---
name: hermes-memory-wiki
description: Reference card only. Describes the Memory Wiki plugin, a Hermes dashboard tab that turns local session history (state.db) into browsable subject pages and daily logs and shows a read-only audit of the MEMORY.md / USER.md persistent memory the agent carries into every session. Consult it when someone asks "what is hermes-memory-wiki", "can Claude show a memory wiki of my sessions", or "audit what the agent remembers". It performs no work and should not trigger on general memory or note-taking requests.
---
# Memory Wiki (Hermes dashboard tab)

**Hermes original:** https://github.com/NousResearch/hermes-memory-wiki @ 9bc3913 · tier: official · category: none listed · license: MIT
**Port class:** D — a dashboard-only plugin (FastAPI router mounted at `/api/plugins/memory-wiki/` plus a React bundle) that reads Hermes' `state.db` through `hermes_state.SessionDB`; `register()` adds no tools or hooks.

## What the Hermes plugin does
Adds a Memory Wiki tab to `hermes dashboard` with Subjects (topics extracted deterministically from session titles, file paths, tool names, slash commands, quoted phrases and CamelCase identifiers), Daily logs, Recent activity (ten most recent sessions) and a Persistent Memory panel rendering `MEMORY.md` / `USER.md` entries exactly as the memory tool parses them. Backend routes: `GET /overview`, `GET /subjects?q=&limit=`, `GET /subjects/{slug}`, `GET /days?limit=`, `GET /days/{date}`. No LLM calls and no writes; `state.db` is opened read-only. Manifest name is `memory-wiki`; requires Hermes >= 0.21.

## Equivalent in Claude
None identified. The plugin aggregates Hermes' own session database and memory files, neither of which exists in Claude. Claude Code keeps project instructions in `CLAUDE.md` files, which the user can read directly; that is not a wiki of session history.

## Setup
None.

## Limits
- Not portable: depends on `hermes_state.SessionDB`, the Hermes dashboard plugin SDK (`window.__HERMES_PLUGIN_SDK__`, `fetchJSON`) and the dashboard's auth gate.
- The aggregation code (`dashboard/memory_wiki_core.py`) is stdlib-only and MIT licensed, but without Hermes session rows it has nothing to aggregate, so it is not copied.
- No data leaves the machine in the original; nothing is replicated here.

## Source
- Catalog entry (reviewed commit): https://github.com/NousResearch/hermes-memory-wiki/tree/9bc3913b8474eaf4d7eec32e97af4d77957c36df
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-memory-wiki.yaml
