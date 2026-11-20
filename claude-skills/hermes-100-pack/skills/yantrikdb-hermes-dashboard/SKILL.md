---
name: yantrikdb-hermes-dashboard
description: "Run and query the local-only YantrikDB dashboard for Hermes Agent memory (a FastAPI app over ~/.hermes/yantrikdb-memory.db) from Claude Code: start it with scripts/start.sh, read stats, browse memories, run recall, review conflicts and export JSONL through its /api routes, or read the SQLite store directly. Use when the user says \"YantrikDB dashboard\", \"inspect my Hermes YantrikDB memory\", \"yantrikdb-memory.db\", \"memory recall debugger\", \"namespace coverage\", or \"start the yantrikdb dashboard\". It does not make Claude use YantrikDB as its own memory."
---
# YantrikDB dashboard for Hermes memory

**Hermes original:** https://github.com/wysie/yantrikdb-hermes-dashboard @ 30e8fa2 · tier: community · category: desktop · license: MIT
**Port class:** C · the dashboard is a standalone FastAPI/uvicorn app with documented env vars and HTTP routes that Claude can launch and query; the Hermes plugin registration, the YantrikDB memory provider it inspects, and the skill-recall features that import `yantrikdb_hermes_plugin` are Hermes-side.

## What the Hermes plugin does
A Hermes plugin whose `register()` is a no-op (no tools, commands or hooks). The payload is `app.py`: a local web dashboard (default `http://127.0.0.1:8767`) for the YantrikDB memory store Hermes writes at `~/.hermes/yantrikdb-memory.db`. Routes include `GET /api/health`, `/api/stats`, `/api/memories` (search, status/domain/source filters, namespace, pagination), `/api/memory/{rid}`, `POST /api/recall`, `/api/conflicts` and `/api/conflicts/{id}/resolve`, `POST /api/think`, `/api/hygiene`, `POST /api/memory/{rid}/forget`, `/api/constellation`, `/api/entities`, `/api/graph/{entity}`, `/api/patterns`, `/api/triggers`, `/api/sessions`, `/api/stale`, `/api/upcoming`, `/api/export/memories.jsonl`, plus settings, auth and identity-scope pages. Browsing is read-only by default; mutations need Admin Mode; an optional password protects the UI. With `YANTRIKDB_SERVER_URL` set it proxies supported routes to a `yantrikdb-server` v0.8.17+ cluster instead of SQLite.

## Equivalent in Claude
1. Confirm the store exists: `ls -l ~/.hermes/yantrikdb-memory.db` (or the path in `YANTRIKDB_DB_PATH`). If a Hermes checkout of the plugin is present (`~/.hermes/plugins/yantrikdb-hermes-dashboard`), use it; otherwise clone the repo at the reviewed commit into its own directory and read it before running.
2. Install dependencies from `requirements.txt` into a venv: `fastapi>=0.110 pydantic>=2 uvicorn>=0.27 requests>=2.31`.
3. Start it bound to localhost: `YANTRIKDB_DASHBOARD_HOST=127.0.0.1 YANTRIKDB_DASHBOARD_PORT=8767 YANTRIKDB_DB_PATH=~/.hermes/yantrikdb-memory.db scripts/start.sh` (runs `python3 app.py`; override the interpreter with `YANTRIKDB_DASHBOARD_PYTHON`). Run it in the background and stop it when done.
4. Query with curl, for example `curl -s http://127.0.0.1:8767/api/stats`, `curl -s "http://127.0.0.1:8767/api/memories?limit=50"`, `curl -s http://127.0.0.1:8767/api/memory/<rid>`, `curl -s http://127.0.0.1:8767/api/export/memories.jsonl`. Keep to GET routes unless the user explicitly asks for a mutation and has enabled Admin Mode (`YANTRIKDB_DASHBOARD_ADMIN_MODE=true` at launch or via Settings).
5. For quick read-only looks without the app, open the SQLite file with `sqlite3 -readonly` and inspect the schema first (`.tables`); the plugin itself connects with `sqlite3.connect(DB_PATH)` and reads tables directly.
6. Give the user the URL so they can use the UI (overview, visualiser, Identity & Scope) in a browser.

| Dashboard feature | How Claude does it |
|---|---|
| Overview / stats | `GET /api/stats`, `GET /api/health` |
| Memory browser, detail drawer | `GET /api/memories`, `GET /api/memory/{rid}` |
| Recall debugger | `POST /api/recall` (JSON body; fields not documented in README, inspect `app.py` first) |
| Conflicts, forget, hygiene, think | Admin Mode only; confirm with the user before any POST |
| JSONL export | `GET /api/export/memories.jsonl` |
| Cluster mode | set `YANTRIKDB_SERVER_URL` (and `YANTRIKDB_TOKEN`); only health/stats/memories/memory routes proxied (Phase 1) |

## Setup
1. A Hermes install using the YantrikDB memory plugin, so `~/.hermes/yantrikdb-memory.db` exists.
2. Python 3.11+ and the four requirements above (`pip index versions yantrikdb` returns 0.23.4 for the engine package, but the dashboard only imports it optionally for recall-related routes; not verified further).
3. Optional env vars (names from the README): `YANTRIKDB_DASHBOARD_HOST` (README default `0.0.0.0`; use `127.0.0.1`), `YANTRIKDB_DASHBOARD_PORT`, `YANTRIKDB_DB_PATH`, `YANTRIKDB_NAMESPACE`, `YANTRIKDB_DASHBOARD_NAMESPACE`, `YANTRIKDB_EMBEDDING_DIM`, `YANTRIKDB_EMBEDDER`, `YANTRIKDB_DASHBOARD_ADMIN_MODE`, `YANTRIKDB_DASHBOARD_SETTINGS_PATH`, `YANTRIKDB_DASHBOARD_PYTHON`, `YANTRIKDB_SERVER_URL`, `YANTRIKDB_TOKEN`.

## Limits
- The dashboard exposes the user's memory content to anyone who can reach the port; bind to `127.0.0.1` and never bind `0.0.0.0` without a dashboard password (README safety model).
- Recall, think, conflict resolution and skill-recall routes import `yantrikdb` / `yantrikdb_hermes_plugin` from the Hermes environment; without them those routes fail.
- The macOS LaunchAgent installer (`scripts/install-launchd.sh`) and Hermes plugin lifecycle (`hermes plugins install/update`) are not part of this skill.
- None of the routes were executed during the port; names come from `app.py` decorators and the README.

## Source
- Catalog entry (reviewed commit): https://github.com/wysie/yantrikdb-hermes-dashboard/tree/30e8fa249a28bef9cb38e62beaa98e38303a8961
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/yantrikdb-hermes-dashboard.yaml
