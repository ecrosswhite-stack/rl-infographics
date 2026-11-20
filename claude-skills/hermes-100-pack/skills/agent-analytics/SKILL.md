---
name: agent-analytics
description: Read a user's Agent Analytics (agentanalytics.sh) project data from Claude Code or Cowork, replacing the Hermes dashboard-only agent-analytics plugin. Use it when the user says "show my Agent Analytics stats", "pull analytics for project X", "list my Agent Analytics projects", "what were my top entry pages, events or insights this week", "sign me in to Agent Analytics", or asks for the numbers the Hermes Signals/Analytics tab showed. Claude performs the agent-session login flow and reads the same REST endpoints with curl. Read-only; do not use for configuring tracking or writing events.
---
# Agent Analytics (read-only project summary)

**Hermes original:** https://github.com/Agent-Analytics/agent-analytics-hermes-plugin @ 63f11d3 · tier: community · category: desktop · license: MIT
**Port class:** C · the Hermes Web dashboard tab is not portable, but the REST calls its backend makes (per `dashboard/plugin_api.py`) can be issued by Claude directly.

## What the Hermes plugin does
Dashboard-only read plugin. It registers no agent tools or hooks (`register()` is a no-op). It adds an "Analytics" tab to the Hermes web dashboard (`dashboard/manifest.json`, `dist/index.js`) backed by a FastAPI router (`dashboard/plugin_api.py`) that signs the user in to an existing Agent Analytics account with a browser-approval flow, stores tokens under `$HERMES_HOME/state/agent-analytics-hermes-plugin.json`, lets the user pick a project, and shows a read-only summary (project, usage, stats, top entry pages, events, insights). The README states the plugin reports its own usage telemetry to Agent Analytics.

## Equivalent in Claude
Base URL copied from the plugin source: `https://api.agentanalytics.sh`. All calls send `Accept: application/json`; authenticated calls send `Authorization: Bearer <access_token>`.

1. Start login (per `start_auth`): generate a random `code_verifier` (32 hex chars), compute `code_challenge = sha256_hex(code_verifier)`, then
   `curl -s -X POST https://api.agentanalytics.sh/agent-sessions/start -H 'Content-Type: application/json' -d '{"mode":"interactive","code_challenge":"<hex>","client_type":"hermes_dashboard","client_name":"Agent Analytics Hermes Plugin","client_instance_id":"agent-analytics","scopes":["account:read","projects:read","analytics:read"]}'`
   Response fields used: `auth_request_id`, `authorize_url`, `poll_token`, `expires_at`.
2. Ask the user to open `authorize_url` in a browser and approve.
3. Poll: `POST /agent-sessions/poll` with `{"auth_request_id":..., "poll_token":...}` until `status` is `approved` or `exchanged`; read `exchange_code`.
4. Exchange: `POST /agent-sessions/exchange` with `{"auth_request_id":..., "exchange_code":..., "code_verifier":...}`. Response: `agent_session.access_token`, `agent_session.refresh_token`, `account.email`, `account.tier`.
5. Read data with the access token. The plugin uses no env var for the token; keep it in a file with mode 0600 and never paste it into chat.

| Hermes dashboard action | How Claude does it |
|---|---|
| Status / project list | `GET /projects` -> `projects[]` (`id`, `name`, `allowed_origins`) |
| Select project | remember `id` and `name` locally |
| Summary, project card | `GET /projects/{id}` |
| Summary, usage | `GET /projects/{id}/usage?days=7` |
| Summary, stats | `GET /stats?project=<name>&days=7` |
| Summary, top entry pages | `GET /pages?project=<name>&type=entry&days=7&limit=10` |
| Summary, events | `GET /events?project=<name>&days=7&limit=10` |
| Summary, insights | `GET /insights?project=<name>&period=7d` |
| Disconnect | delete the stored token file |

`days` defaults to 7 in the plugin; change it when the user asks for another window. Present results as a table per project. Field names inside those responses are not enumerated in the plugin source; show what comes back.

## Setup
1. Have an existing Agent Analytics account (the plugin requires one; setup help at https://docs.agentanalytics.sh/installation/hermes/ per the source).
2. Run the login flow above once; approve in the browser.
3. Store the access token in a 0600 file of the user's choosing; refresh handling is not implemented in the plugin source (it clears auth on error), so re-run login when calls return 401.

## Limits
- The Hermes dashboard tab, sidebar icon, project picker UI and empty-state screens are not replicated; Claude returns text or tables instead.
- The plugin's own usage telemetry (`window.aa.track` events) is not replicated.
- The PKCE-style challenge is a plain SHA-256 hex digest per the plugin source, not standard base64url PKCE; follow the source, not RFC 7636.
- Token refresh via `refresh_token` is not exercised in the plugin source; "not verified".
- Data is sent to and read from a third-party service (Agent Analytics); account scopes are read-only (`account:read`, `projects:read`, `analytics:read`).
- No upstream skills/ directory exists to copy.

## Source
- Catalog entry (reviewed commit): https://github.com/Agent-Analytics/agent-analytics-hermes-plugin/tree/63f11d3669330e40dad977b7d32f9b69e69a9fb8
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/agent-analytics.yaml
