---
name: crawl4ai
description: Extract clean Markdown from any web page (including JavaScript-rendered pages) through the user's self-hosted crawl4ai instance, using the same CRAWL4AI_URL and CRAWL4AI_API_TOKEN the Hermes plugin used. Use this whenever the user says "extract this page with crawl4ai", "use my crawl4ai server", "fetch the markdown of <url>", "scrape <url> on my own infrastructure", "read this SPA page", or when a page must be fetched without sending data to a third-party extraction API and the user has a crawl4ai instance. Pairs with a self-hosted SearXNG for search.
---
# Crawl4ai Web Extract (self-hosted)

**Hermes original:** https://github.com/mblauser/hermes-plugin-crawl4ai @ 6eb0842 · tier: community · category: web · license: no LICENSE file found (README text says MIT)
**Port class:** B · the plugin is a thin HTTP client for the crawl4ai `/md` endpoint, which Claude can call directly with curl or Python.

## What the Hermes plugin does
Registers a `crawl4ai` web extract backend (`provides_web_providers: [crawl4ai]`) for the Hermes `web_extract` tool. It POSTs each URL to `{CRAWL4AI_URL}/md` with a Bearer token and returns the Markdown as a normalized document. It is extract-only (`supports_search()` is False); search is left to SearXNG. It refuses URLs that resolve to private or internal network addresses (SSRF check). No tools or hooks are registered.

## Equivalent in Claude
Perform the same request yourself. Per the plugin source (`provider.py`):

1. Read `CRAWL4AI_URL` (instance base URL, trailing slash stripped) and `CRAWL4AI_API_TOKEN` (JWT) from the environment. If either is missing, stop and tell the user; do not guess a URL.
2. Refuse URLs that point at private or internal addresses (localhost, RFC1918, link-local) unless the user explicitly wants that.
3. For each URL run:

```bash
curl -sS -X POST "$CRAWL4AI_URL/md" \
  -H "Authorization: Bearer $CRAWL4AI_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data "$(python3 -c 'import json,sys;print(json.dumps({"url":sys.argv[1]}))' "$URL")"
```

4. Parse the JSON. Per the plugin, the response shape is `{"url": ..., "markdown": ..., "success": true}`; `markdown` may be a string or a dict, in which case use `raw_markdown` (fallback `markdown`).
5. Take the title from the first `# ` heading in the Markdown, else use the URL.
6. On HTTP errors report `Crawl4ai HTTP <status>` with the first 200 chars of the body, as the plugin does. The plugin used a 60 s timeout per request.

| Hermes tool | How Claude does it |
|---|---|
| `web_extract(urls, format)` via crawl4ai backend | One `POST $CRAWL4AI_URL/md` per URL as above; return `{url, title, content, raw_content}` |
| `web_search` | Not provided by this plugin (search-only backends such as SearXNG were used) |

## Setup
1. Run a crawl4ai instance, for example `docker run -d -p 11235:11235 unclecode/crawl4ai` (per the plugin README; the API token is logged on startup).
2. `export CRAWL4AI_URL=http://localhost:11235`
3. `export CRAWL4AI_API_TOKEN=<jwt-from-your-instance>`
4. If your instance has auth disabled, omit the `Authorization` header (the plugin itself required the token).

## Limits
- Hermes' automatic backend selection (`web.extract_backend: crawl4ai` in config.yaml) has no equivalent; invoke the request explicitly.
- Hermes' result caching, large-page truncation and private-URL blocklist live in Hermes core; apply the SSRF check manually.
- No LICENSE file in the checkout, so no upstream text is copied; the README states MIT.
- Data stays on the user's infrastructure; no third-party cost.
- The `crawl4ai` PyPI package exists (`pip index versions crawl4ai` -> 0.9.6) but the plugin only talks to the HTTP server, not the Python library.

## Source
- Catalog entry (reviewed commit): https://github.com/mblauser/hermes-plugin-crawl4ai/tree/6eb0842a39e2d89fb02ca85512945700dbebdc86
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/crawl4ai.yaml
