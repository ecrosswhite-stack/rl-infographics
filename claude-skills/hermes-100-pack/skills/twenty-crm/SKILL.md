---
name: twenty-crm
description: Work with Twenty CRM (twenty.com) the way the Hermes twenty-crm plugin does: inspect the workspace connection, call the REST API, run core-record or metadata GraphQL, introspect the live schema before any write, and optionally run a self-hosted Twenty stack with Docker Compose. Use when the user mentions "Twenty CRM", "twenty.com", TWENTY_API_KEY or TWENTY_BASE_URL, asks to read/create/update people, companies, opportunities, notes, custom objects, fields, views, dashboards or workflows in Twenty, or wants a local Twenty instance started, diagnosed or stopped. Do not use for other CRMs.
---
# Twenty CRM

**Hermes original:** https://github.com/TREE-Ind/hermes-twenty-crm @ 3d87c16 · tier: community · category: tools · license: MIT
**Port class:** B — the plugin is a standard-library HTTP client over Twenty's REST and GraphQL APIs plus a Docker Compose launcher; Claude can do both from bash.

## What the Hermes plugin does
Registers the `twenty` toolset: `twenty_describe_workspace` (connection mode, base URL, endpoints, configured auth modes, OAuth discovery), `twenty_rest` (any path under `/rest/`), `twenty_graphql` (`api=core` -> `/graphql`, `api=metadata` -> `/metadata`), `twenty_schema` (GraphQL introspection, optionally one type), the `/twenty` slash command (status, bootstrap, start, logs, stop, doctor) and hooks `on_session_start`, `pre_tool_call` that autostart the managed stack. Auth per tools.py: `TWENTY_API_KEY`, then `TWENTY_ACCESS_TOKEN`, then OAuth client credentials (`TWENTY_CLIENT_ID`/`TWENTY_CLIENT_SECRET`, `POST /oauth/token`, scope `TWENTY_OAUTH_SCOPE` default `api`), all sent as `Authorization: Bearer`. Managed mode writes a Docker Compose file (twentycrm/twenty, postgres:16, redis:7) under `~/.hermes/projects/twenty-crm` bound to `127.0.0.1:3000`. It ships one skill, `twenty-crm`.

## Equivalent in Claude
Resolve the base URL first: if `TWENTY_CONNECTION_MODE=external`, use `TWENTY_BASE_URL` (default `https://api.twenty.com`); if `managed` (the plugin default), use `http://${TWENTY_MANAGED_BIND_HOST:-127.0.0.1}:${TWENTY_MANAGED_PORT:-3000}`. Timeout `TWENTY_TIMEOUT_SECONDS` (default 30). Pick the token in the same order as the plugin and set `AUTH="Authorization: Bearer $TOKEN"`.

| Hermes tool | How Claude does it |
|---|---|
| `twenty_describe_workspace` | `curl -sS $BASE/healthz`; list which of the three auth env vars are set; `curl -sS $BASE/.well-known/oauth-authorization-server` (unauthenticated) |
| `twenty_rest(method, path, params, body)` | `curl -sS -X <METHOD> -H "$AUTH" -H "Accept: application/json" -H "Content-Type: application/json" "$BASE/rest/<...>" -d '<json>'`; path must start with `/rest/` |
| `twenty_graphql(query, variables, api)` | `curl -sS -X POST -H "$AUTH" -H "Content-Type: application/json" "$BASE/graphql"` (or `$BASE/metadata`) `-d '{"query":"...","variables":{}}'`; treat a body with `errors` as failure |
| `twenty_schema(api, type_name)` | POST the standard `__schema { types { name kind fields { name type {...} } inputFields enumValues } }` introspection query to `/graphql` or `/metadata`, filter out `__*` types, print the requested type |
| `/twenty start|stop|logs|status|doctor` | in the project dir: `docker compose up -d`, `docker compose down`, `docker compose logs --tail 80`, `curl $BASE/healthz`, `which docker` |
| OAuth client credentials | `curl -sS -X POST "$BASE/oauth/token" -d grant_type=client_credentials -d client_id=... -d client_secret=... -d scope=api`; cache `access_token` until `expires_in` |

Managed bootstrap, if the user wants a local stack: create `~/.hermes/projects/twenty-crm/docker-compose.yml` from the `COMPOSE` string in the plugin's runtime.py (services server, worker, db, redis; volumes db-data, server-local-data) and a `.env` with `TWENTY_IMAGE_TAG`, `TWENTY_BIND_HOST`, `TWENTY_SERVER_PORT`, `SERVER_URL`, random `APP_SECRET` and `PG_DATABASE_PASSWORD`, then `docker compose up -d` and poll `/healthz` for up to 120 s. Then the user creates an API key in the Twenty UI and sets `TWENTY_API_KEY`.

Follow `references/upstream-twenty-crm.md` for schema-first discipline: introspect before assuming object or field names, dedupe before create, read back after every write, never stop or edit an external instance.

No Twenty MCP package was verified (`npm view twenty-mcp` returned 404 on 2026-11-20); none is listed.

## Setup
1. External instance or Twenty Cloud: `export TWENTY_CONNECTION_MODE=external TWENTY_BASE_URL=https://crm.example.com TWENTY_API_KEY=...` (create the key in Twenty's settings). Alternatives: `TWENTY_ACCESS_TOKEN`, or `TWENTY_CLIENT_ID` plus `TWENTY_CLIENT_SECRET` (optional `TWENTY_OAUTH_SCOPE`, `TWENTY_TIMEOUT_SECONDS`).
2. Managed local stack: install Docker with Compose, optionally set `TWENTY_MANAGED_AUTOSTART`, `TWENTY_MANAGED_BIND_HOST`, `TWENTY_MANAGED_PORT`, `TWENTY_MANAGED_PROJECT_DIR`, `TWENTY_MANAGED_IMAGE_TAG`, `TWENTY_MANAGED_APP_SECRET`, `TWENTY_MANAGED_PG_PASSWORD`; then follow the bootstrap steps above.

## Limits
- Session-start autostart and the `pre_tool_call` hook are Hermes runtime features; Claude starts the stack only when asked.
- The OAuth token cache at `~/.hermes/cache/twenty-crm-oauth.json` is not reproduced; re-request tokens as needed.
- Writes change CRM data; confirm destructive mutations with the user and verify by reading back.
- Credentials go to the configured Twenty host; with Twenty Cloud that is a third party.
- Endpoint paths come from the plugin source and were not re-verified against a live Twenty instance.

## Source
- Catalog entry (reviewed commit): https://github.com/TREE-Ind/hermes-twenty-crm/tree/3d87c1634e4b159738b35954ac4efc15c876d46d
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/twenty-crm.yaml
