---
name: web-venice
description: Web search and page extraction through Venice AI's /augment endpoints, replicating the Hermes web-venice backend (privacy-first search routed via Brave or Google, Markdown page scraping, $0.01 per request) with the user's VENICE_API_KEY. Use when the user says "search with Venice", "use my Venice key", "privacy-first web search", "scrape this URL through Venice", wants zero-data-retention search results, or has VENICE_API_KEY set and asks for a web search or a clean text extraction of a URL.
---
# Venice AI Web Search and Extract

**Hermes original:** https://github.com/MnrGreg/hermes-venice-web @ dcc286f · tier: community · category: web · license: MIT
**Port class:** B — the plugin wraps two Venice REST endpoints that Claude can call directly with curl or Python.

## What the Hermes plugin does
Registers `venice` as a Hermes web backend (`kind: backend`, `provides_web_providers: [venice]`) so the standard `web_search` and `web_extract` tools route to Venice. Per provider.py it POSTs JSON to `https://api.venice.ai/api/v1/augment/search` (`{query, limit, search_provider}`) and `https://api.venice.ai/api/v1/augment/scrape` (`{url}`) with `Authorization: Bearer $VENICE_API_KEY`. Search limit is clamped 1-20; `search_provider` comes from `VENICE_SEARCH_PROVIDER` (`brave` default, or `google`). Search results map `title`, `url`, `content` (or `snippet`). Scrape returns `content` from the response, or from its `data` wrapper when present. The README prices both at $0.01 per request or URL.

## Equivalent in Claude
1. Check `VENICE_API_KEY` (`test -n "$VENICE_API_KEY"`); if missing, follow Setup.
2. Search (timeout 20 s in the plugin):
   ```bash
   curl -sS -X POST "https://api.venice.ai/api/v1/augment/search" \
     -H "Authorization: Bearer $VENICE_API_KEY" -H "Content-Type: application/json" \
     -d '{"query":"<query>","limit":10,"search_provider":"'"${VENICE_SEARCH_PROVIDER:-brave}"'"}'
   ```
   Read `.results[]`; report `title`, `url` and `content` (fall back to `snippet`), numbered by position.
3. Extract (timeout 30 s in the plugin), one call per URL:
   ```bash
   curl -sS -X POST "https://api.venice.ai/api/v1/augment/scrape" \
     -H "Authorization: Bearer $VENICE_API_KEY" -H "Content-Type: application/json" \
     -d '{"url":"<url>"}'
   ```
   Take `.data.content` if `.data` exists, else `.content`. The plugin leaves `title` empty.
4. On a non-2xx status, report "Venice returned HTTP <code>" and stop; do not retry automatically.
5. Tell the user each call costs about $0.01 before running batches of extractions.

| Hermes tool | How Claude does it |
|---|---|
| `web_search(query, limit)` via Venice | POST `/augment/search` as above |
| `web_extract(urls)` via Venice | one POST `/augment/scrape` per URL |

No MCP package for Venice was verified; none is listed.

## Setup
1. Get an API key at https://venice.ai.
2. `export VENICE_API_KEY="vk-..."`.
3. Optional: `export VENICE_SEARCH_PROVIDER=google` (default `brave`).

## Limits
- Paid service: $0.01 per search request and per scraped URL per the plugin README. Confirm with the user before large batches.
- Query text and target URLs are sent to Venice, a third party. The zero-data-retention claim is the vendor's, not verified here.
- Hermes config keys (`web.backend: venice`, `search_backend`, `extract_backend`) have no Claude equivalent; Claude simply calls the endpoints when this skill applies.
- Response shapes beyond `results[]`, `content` and `data.content` were not verified; adjust if the API returns something else.

## Source
- Catalog entry (reviewed commit): https://github.com/MnrGreg/hermes-venice-web/tree/dcc286fc40544f4489831ff246de8030fd0417fa
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/web-venice.yaml
