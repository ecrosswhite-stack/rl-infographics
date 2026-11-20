---
name: shodan
description: Query Shodan.io the way the Hermes shodan plugin does, with the user's SHODAN_API_KEY or keyless fallbacks. Covers host intel (ports, products, TLS certs, CVEs), free match counts with facets, filtered host search, DNS subdomain enumeration and resolution, CVEDB vulnerability lookups (CVSS, EPSS, CISA KEV), account credits, filter/facet lists and query validation, plus the opt-in alert, exploit, saved-query, trends and on-demand scan endpoints. Use when the user says "shodan", "what is exposed on this IP/domain", "attack surface", "how many hosts run X", "is CVE-... exploited in the wild", "subdomains of", "InternetDB", or asks for OSINT on internet-facing infrastructure.
---
# Shodan

**Hermes original:** https://github.com/Adolanium/hermes-plugin-shodan @ c7d5621 · tier: community · category: tools · license: MIT
**Port class:** B — every tool is a flat HTTPS GET/POST against Shodan's public APIs that Claude can issue with curl; the credit ledger, caching and response shaping are plugin conveniences reproduced as working rules.

## What the Hermes plugin does
Registers twelve tools in the `shodan` toolset: core `shodan_host`, `shodan_search`, `shodan_count`, `shodan_dns`, `shodan_cve`, `shodan_account`, `shodan_meta`, and full-profile `shodan_scan`, `shodan_alert`, `shodan_exploits`, `shodan_query`, `shodan_trends`; hooks `on_session_start` and `on_session_reset` reset a per-session credit budget (default 50 query credits, 0 scan credits). Per client.py the API families are `https://api.shodan.io` (REST, `?key=`), `https://exploits.shodan.io/api`, `https://trends.shodan.io`, and the keyless `https://internetdb.shodan.io` and `https://cvedb.shodan.io`. It enforces 1 request per second, retries 429/5xx, caches free idempotent lookups, shapes huge host JSON down to identity plus one line per service, and ships three skills (query-syntax, recon, monitoring).

## Equivalent in Claude
Set `BASE=https://api.shodan.io` and send the key as the `key` query parameter. Pace calls to about one per second. Never print the key; redact it from any URL you show. Prefer the free endpoints first (count, host, CVEDB) and confirm with the user before any credit-spending call.

| Hermes tool | Endpoint(s) per handlers_core.py / handlers_full.py | Credits |
|---|---|---|
| `shodan_host(ip, history?)` | `GET $BASE/shodan/host/{ip}?key=` ; no key: `GET https://internetdb.shodan.io/{ip}` (label result `source: internetdb`) | free |
| `shodan_search(query, facets?, page?)` | `GET $BASE/shodan/host/search?key=&query=&facets=&page=` | 1 per filtered query, +1 per extra page |
| `shodan_count(query, facets?)` | `GET $BASE/shodan/host/count?key=&query=&facets=` | free |
| `shodan_dns(mode=resolve\|reverse\|domain)` | `GET $BASE/dns/resolve?hostnames=` ; `GET $BASE/dns/reverse?ips=` ; `GET $BASE/dns/domain/{domain}` | domain costs 1, others free |
| `shodan_cve(action=get\|search\|cpes)` | `GET https://cvedb.shodan.io/cve/{CVE}` ; `GET .../cves?product=\|cpe23=&limit=&is_kev=true&sort_by_epss=true` ; `GET .../cpes?product=` | free, no key |
| `shodan_account` | `GET $BASE/api-info?key=` (plan, credits); `GET $BASE/tools/myip?key=` | free |
| `shodan_meta(action)` | `GET $BASE/shodan/host/search/filters`, `/shodan/host/search/facets`, `/shodan/ports`, `/shodan/protocols`, validate: `/shodan/host/search/tokens?query=` | free |
| `shodan_scan` | `GET $BASE/shodan/scans` ; `GET $BASE/shodan/scan/{id}` ; `POST $BASE/shodan/scan` form `ips=a,b` | scan credits, 1 per IP (a /24 = 256) |
| `shodan_alert(action)` | `GET /shodan/alert/info`, `/shodan/alert/triggers`, `/shodan/alert/{id}/info`; `POST /shodan/alert` JSON `{name, filters:{ip:[...]}, expires?}`; `DELETE /shodan/alert/{id}`; `PUT`/`DELETE /shodan/alert/{id}/trigger/{name}` | free, uses monitored-IP allowance |
| `shodan_exploits(query, facets?, page?)` | `GET https://exploits.shodan.io/api/search?key=&query=` ; `.../api/count` | plan-dependent |
| `shodan_query(action)` | `GET $BASE/shodan/query/tags?size=40`, `/shodan/query/search?query=&page=`, `/shodan/query` | free |
| `shodan_trends(query, facets?)` | `GET https://trends.shodan.io/api/v1/search?key=&query=` | Enterprise plan |

Working rules carried over from the plugin:
1. Validate unfamiliar queries with `/shodan/host/search/tokens` and answer aggregate questions with `/shodan/host/count` plus facets before ever calling `/shodan/host/search`.
2. Shape host output: identity (ip, hostnames, org, isp, asn, location, last_update), open ports, then one compact line per service (port, transport, module, product, version, http title, cert CN). Drop HTML bodies, favicons, screenshots and PEM chains; say that you dropped them.
3. Sort CVEs worst first; mark `verified: false` ones as inferred from banners.
4. Shodan returns 401 as an HTML page and can return 200 with `{"error": ...}`; treat both as errors and distinguish "no key", "insufficient credits" and "plan does not allow filter" (`vuln:` needs Small Business, `tag:` needs Corporate).
5. Keep a running tally of credits spent in the conversation and stop at the budget the user agrees to (plugin default 50).
6. On-demand scans send real probes: only with explicit user authorization for targets they own, and only after telling the user the scan-credit cost.

Reference material: read `references/upstream-query-syntax.md` (filters, facets, plan gating), `references/upstream-recon.md` (credit-efficient workflow) and `references/upstream-monitoring.md` (alerts and triggers), plus the full filter and facet tables in `references/upstream-query-syntax-references-filters.md` and `...-facets.md`.

No Shodan MCP package was verified (`npm view shodan-mcp` returned 404 on 2026-11-20), so none is listed.

## Setup
1. Sign in at https://account.shodan.io and copy the API key from "Account".
2. `export SHODAN_API_KEY="..."`. Without a key only InternetDB host lookups and CVEDB queries work.
3. Check plan and credits once: `curl -sS "https://api.shodan.io/api-info?key=$SHODAN_API_KEY"`.

## Limits
- Query credits cost money and Membership gets 100 per month; `search` and `dns/domain` spend them. There is no automatic budget enforcement here, only the agreed tally.
- `shodan_scan` sends probes to real hosts and `shodan_alert` creates monitors that outlive the conversation; both change state at Shodan and need explicit user approval.
- Targets, queries and IPs are sent to Shodan, a third party.
- The plugin's TTL cache, thread-safe rate limiter, `hermes shodan` CLI, `/shodan` slash command, `doctor`, profiles and config.yaml options are not replicated.
- Response shapes were taken from the plugin source, not re-verified against live Shodan.

## Source
- Catalog entry (reviewed commit): https://github.com/Adolanium/hermes-plugin-shodan/tree/c7d56211420438bd300c3526b7536f55aafb0fce
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/shodan.yaml
