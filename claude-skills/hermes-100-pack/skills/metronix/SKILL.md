---
name: metronix
description: Read and write memories in a self-hosted Metronix Memory server over its REST API (/api/v1/memory/search, /api/v1/memory/records, /api/v1/knowledge/store) using METRONIX_AUTH_TOKEN, as the Hermes metronix memory provider does. Use when the user has a Metronix backend and asks to "search my Metronix memories", "store this fact in Metronix", "ingest these docs into Metronix knowledge", or mentions Metronix / mtrnix. Automatic prefetch-before-turn and write-through are Hermes-only (see Limits).
---
# Metronix Memory (REST access)

**Hermes original:** https://github.com/mtrnix/hermes-memory-metronix @ 55634c1 · tier: community · category: memory · license: Apache-2.0
**Port class:** C · the HTTP calls in `plugin/metronix/client.py` are reproducible with curl; the `MemoryProvider` lifecycle (prefetch on every turn, write-through of `memory(action="add")`, turn sync) is Hermes-internal.

## What the Hermes plugin does
Registers a Hermes `MemoryProvider` named `metronix` (no tools listed). Per the README it prefetches relevant records before each turn via memory search, mirrors Hermes memory writes into Metronix, optionally stores completed turns as session-scoped records (`sync_turns`, on by default), and authenticates with a REST JWT or `mtk_...` personal key, falling back to email/password login. Config comes from `$HERMES_HOME/metronix.json` plus env vars; a `hermes-metronix-setup` command installs it.

## Equivalent in Claude
Env vars (same names, from the plugin source): `METRONIX_BASE_URL` (README example `http://localhost:8000`), `METRONIX_AUTH_TOKEN` (REST JWT or `mtk_` key; not `METRONIX_MCP_API_KEY`), or `METRONIX_EMAIL` + `METRONIX_PASSWORD`; `METRONIX_WORKSPACE_ID`, `METRONIX_AGENT_ID`; tuning: `METRONIX_PREFETCH_TOP_K` (8), `METRONIX_PREFETCH_TYPES` (`fact,preference,pinned`), `METRONIX_WRITE_SCOPE` (`workspace`), `METRONIX_TIMEOUT_SECONDS` (20).
All requests: `Authorization: Bearer $METRONIX_AUTH_TOKEN`, JSON bodies.

| Hermes behavior | Request (copied from client.py) |
|---|---|
| prefetch / recall | `POST $METRONIX_BASE_URL/api/v1/memory/search` body `{"query": "...", "top_k": 8, "agent_id": "<optional>"}`; results in `results[]` |
| memory add (write-through) | `POST /api/v1/memory/records` body `{"content","agent_id","scope","kind","source_type","tags":[],"metadata":{},"session_id"?}` |
| wiki / document ingest | `POST /api/v1/knowledge/store` |
| delete a record | `DELETE /api/v1/memory/records/<record_id>` (agent_id passed per the client) |
| auth check | `GET /api/v1/auth/me`; login fallback `POST /api/v1/auth/login` |

Scope mapping from the README: Hermes `per_agent` -> `per_agent`; `workspace` and `shared` -> `global`; `session` -> `session`. Kinds used for prefetch: `fact`, `preference`, `pinned`.
Example:
```bash
curl -s -X POST "$METRONIX_BASE_URL/api/v1/memory/search" -H "Authorization: Bearer $METRONIX_AUTH_TOKEN" \
  -H "Content-Type: application/json" -d '{"query":"user timezone","top_k":8}'
```
When the user wants recall at the start of a task, run the search once and quote the sources (the plugin's `cite_sources` default).

## Setup
1. Run or obtain access to a Metronix Memory backend; create a REST personal key (`mtk_...`) or JWT.
2. `export METRONIX_BASE_URL=... METRONIX_AUTH_TOKEN=... METRONIX_WORKSPACE_ID=... METRONIX_AGENT_ID=...`
3. Optional: the Hermes plugin package exists on PyPI (verified `pip index versions hermes-memory-metronix` -> `2026.34.1`) but it is a Hermes plugin, not an MCP server or CLI for Claude.

## Limits
- No automatic prefetch before every turn, no write-through of Claude's own memory, no turn synchronization; Claude calls the API only when asked.
- Request/response field names beyond those in `client.py` (for example the exact shape of `results[]`) are not verified.
- `sync_turns`-style behavior would send conversation text to the Metronix server; do not replicate it without the user's consent.
- Nearest Claude-native equivalent: none identified.

## Source
- Catalog entry (reviewed commit): https://github.com/mtrnix/hermes-memory-metronix/tree/55634c149378f6241a9147a47e67133f6c8a02e6
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/metronix.yaml
