---
name: nextdns
description: "Triage DNS with the official NextDNS API, read-only, as the Hermes nextdns plugin did: pull the DNS query log with domain, status, device and time filters, list recently blocked queries with the blocklist that matched, get aggregate analytics (top domains, blocklists, devices, protocols, status) and read profile settings such as whether logging is on and its retention. Use it when a user asks \"was this domain blocked by NextDNS and by what\", \"show my NextDNS logs for this device\", \"which blocklist caught X\", \"top blocked domains today\", \"is NextDNS logging enabled\", or anything about NextDNS query logs or analytics. Requires NEXTDNS_API_KEY."
---
# NextDNS triage

**Hermes original:** https://github.com/shanelord01/hermes-nextdns @ 6e46460 · tier: community · category: tools · license: MIT
**Port class:** B · the plugin is a stdlib wrapper over `GET` calls to `https://api.nextdns.io`; Claude can issue the same requests with curl.

## What the Hermes plugin does
Per plugin.yaml and `tools.py`, it registers four read-only tools, `nextdns_logs`, `nextdns_blocked`, `nextdns_analytics`, `nextdns_profile`, plus a `/nextdns` slash command and a dashboard tab. Every call is a `GET` against `_BASE = "https://api.nextdns.io"` with headers `X-Api-Key`, a custom `User-Agent` (NextDNS rejects Python's default with 403) and `Accept: application/json`. Settings resolve from `$HERMES_HOME/nextdns_settings.json`, then env (`NEXTDNS_API_KEY`, `NEXTDNS_PROFILE_ID`). Limits are floored at 10 (the API rejects less with 400), logs are capped at 200 rows per call, and device names are resolved to ids through `/profiles/{id}/analytics/devices`.

## Equivalent in Claude
Use curl with `H='X-Api-Key: '"$NEXTDNS_API_KEY"` and `UA='User-Agent: claude-nextdns-skill/1.0'`, parse with `jq` or Python. Profile id `P` is `$NEXTDNS_PROFILE_ID` or the one the user names (the path segment of `https://dns.nextdns.io/<id>`).

| Hermes tool | Request |
|---|---|
| `nextdns_profile` (no profile set) | `GET https://api.nextdns.io/profiles` and list `data[].id`, `data[].name` |
| `nextdns_profile` | `GET https://api.nextdns.io/profiles/$P`; report `data.name`, `data.settings.logs.enabled`, `data.settings.logs.retention` (seconds), `data.settings.logs.location`, `data.privacy.blocklists[].id` |
| `nextdns_logs` | `GET https://api.nextdns.io/profiles/$P/logs?limit=<10..1000>&raw=true` plus optional `search=`, `status=default|blocked|allowed|error`, `device=<id>`, `from=`, `to=`, `cursor=`; show `timestamp`, `domain`, `status`, `device.name`, `reasons[].name`, `protocol`, `encrypted`; next page via `meta.pagination.cursor` |
| `nextdns_blocked` | same as logs with `status=blocked`; `reasons[].name` is the blocklist that matched |
| `nextdns_analytics` | `GET https://api.nextdns.io/profiles/$P/analytics/<metric>?limit=<10..500>` with optional `from`, `to`, `device`; metrics: `status`, `domains`, `reasons`, `ips`, `devices`, `protocols`, `queryTypes`, `ipVersions`, `dnssec`, `encryption`, `destinations` |
| device name to id | `GET https://api.nextdns.io/profiles/$P/analytics/devices?limit=500`, match `data[].name` case-insensitively to get `data[].id`; pass ids and `__UNIDENTIFIED__` through unchanged |

Example: `curl -s -H "$H" -H "$UA" -H 'Accept: application/json' "https://api.nextdns.io/profiles/$P/logs?limit=50&status=blocked&raw=true" | jq '.data[] | {timestamp,domain,reasons:[.reasons[].name],device:.device.name}'`

Working rules from the plugin: check the profile first when a log query returns nothing (logging off means empty, not an error); never send `limit` below 10; surface the API's `errors[].detail` text verbatim; cap what you print to about 200 rows.

## Setup
1. Create an API key at the bottom of https://my.nextdns.io/account.
2. `export NEXTDNS_API_KEY=<key>` and optionally `export NEXTDNS_PROFILE_ID=<id>`.
3. Install `jq` for parsing (optional).

## Limits
- Read-only by design, same as the plugin: no configuration changes.
- No dashboard tab, "Test connection" button, or `/nextdns` slash totals.
- Router-level clients all appear as `__UNIDENTIFIED__` (README); device attribution needs the NextDNS apps or per-device DoH/DoT.
- Endpoints and parameters are copied from `tools.py`; no live call was made during this port.
- The API key is sent to NextDNS only; do not paste it into chat.

## Source
- Catalog entry (reviewed commit): https://github.com/shanelord01/hermes-nextdns/tree/6e46460e9d7f4775d247fb1e467532cf42bfc52d
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/nextdns.yaml
