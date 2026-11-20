---
name: web-ollama-cloud
description: Web search and page extraction through Ollama Cloud's native REST API (POST https://ollama.com/api/web_search and /api/web_fetch) using the user's OLLAMA_API_KEY, the same key the Ollama Cloud model provider uses. Use when the user says "search the web with Ollama", "use my Ollama key for search", "fetch this page via Ollama", "ollama web_search", or wants search and extraction on Ollama's free tier instead of another search API. Returns title, url and content snippets for search, and title, content and links for a fetched page.
---
# Ollama Cloud Web Search and Fetch

**Hermes original:** https://github.com/rriggs/hermes-plugin-ollama-cloud-search @ 9c739a9 · tier: community · category: web · license: MIT
**Port class:** B — a thin `httpx` client for two Ollama REST endpoints that Claude can call directly with curl.

## What the Hermes plugin does
Registers one web provider, `ollama-cloud` (`provides_web_providers: [ollama-cloud]`, `kind: backend`), serving both Hermes `web_search` and `web_extract`. Search POSTs `{"query", "max_results"}` to `/api/web_search` (results capped at 10 by the API) and maps `content` to `description`; extract POSTs `{"url"}` to `/api/web_fetch` once per URL and returns `url`, `title`, `content`, `raw_content`, `metadata.links`. Both use `Authorization: Bearer $OLLAMA_API_KEY`. Base URL `https://ollama.com`, overridable with `OLLAMA_BASE_URL`; timeout 30 s. No tools or hooks of its own.

## Equivalent in Claude
Per the plugin source (`__init__.py`):

1. Read `OLLAMA_API_KEY`; if unset, stop and point the user to `https://ollama.com/settings/keys`. Base URL is `OLLAMA_BASE_URL` if set (trailing slash stripped), else `https://ollama.com`.
2. Search (clamp `max_results` to 1..10):

```bash
curl -sS -X POST "${OLLAMA_BASE_URL:-https://ollama.com}/api/web_search" \
  -H "Authorization: Bearer $OLLAMA_API_KEY" -H "Content-Type: application/json" \
  --data "$(python3 -c 'import json,sys;print(json.dumps({"query":sys.argv[1],"max_results":5}))' "$QUERY")"
```

   Response: `{"results": [{"title", "url", "content"}, ...]}`. Present position, title, url and the `content` snippet.
3. Fetch one URL per call:

```bash
curl -sS -X POST "${OLLAMA_BASE_URL:-https://ollama.com}/api/web_fetch" \
  -H "Authorization: Bearer $OLLAMA_API_KEY" -H "Content-Type: application/json" \
  --data "$(python3 -c 'import json,sys;print(json.dumps({"url":sys.argv[1]}))' "$URL")"
```

   Response: `{"title", "content", "links": [...]}`. Loop sequentially for several URLs and report per-URL failures (`HTTP <status>: <first 200 chars>`) instead of aborting the batch.
4. Use a 30 s timeout (`--max-time 30`).

| Hermes capability | How Claude does it |
|---|---|
| `web_search` via `ollama-cloud` | curl `POST /api/web_search` |
| `web_extract` via `ollama-cloud` | curl `POST /api/web_fetch` per URL |
| `web.ollama-cloud.timeout` | `--max-time` |

## Setup
1. Create an API key at `https://ollama.com/settings/keys`.
2. `export OLLAMA_API_KEY=...`; optionally `export OLLAMA_BASE_URL=https://ollama.com`.

## Limits
- Queries and fetched URLs are sent to Ollama (third party). The README states a free tier with higher limits on paid Ollama Cloud; rate limits are not documented in the plugin.
- The `web.backend` / `search_backend` / `extract_backend` config selection is Hermes-only; here Claude calls the endpoints when asked.
- Response shapes are copied from the plugin source and README, not re-verified against the live API.

## Source
- Catalog entry (reviewed commit): https://github.com/rriggs/hermes-plugin-ollama-cloud-search/tree/9c739a9ea5985e0ba86c20d7160af06382c2198e
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/web-ollama-cloud.yaml
