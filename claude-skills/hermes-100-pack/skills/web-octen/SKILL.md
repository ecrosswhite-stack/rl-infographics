---
name: web-octen
description: Search the web with Octen (results carry query-focused highlights) and extract page content as Markdown or text through the Octen API using OCTEN_API_KEY. Use this when the user says "search with Octen", "use Octen", "octen search for ...", "extract these URLs with Octen", or when the user has an Octen key and wants web search plus page extraction from Claude Code or Cowork. Also usable through the verified octen-mcp MCP server.
---
# Octen Web Search and Extract

**Hermes original:** https://github.com/Octen-Team/hermes-octen-plugin @ 3af8a3f · tier: community · category: web · license: MIT
**Port class:** B — two documented REST calls (`/search`, `/extract`) that Claude can make directly; an MCP server also exists.

## What the Hermes plugin does
Registers an `octen` web-search provider (`provides_web_providers: [octen]`) behind Hermes' existing `web_search` and `web_extract` tools. Search calls `POST https://api.octen.ai/search` with highlights enabled and full content disabled; extract calls `POST https://api.octen.ai/extract` in batches of at most 20 URLs. It adds no tool names of its own.

## Equivalent in Claude
Per the plugin source (`provider.py`). Base URL: `https://api.octen.ai`. Auth header: `x-api-key: $OCTEN_API_KEY`.

Search (plugin timeout 30 s):
```bash
curl -sS -X POST https://api.octen.ai/search -H "x-api-key: $OCTEN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"<query>","count":5,"highlight":{"enable":true},"full_content":{"enable":false}}'
```
`count` is clamped to 1..100. Response: `{"code":0,"data":{"results":[{"url","title","highlight"}, ...]}}`. A non-zero `code` is an API error. Report each hit as title, url, highlight (as description), position.

Extract (plugin timeout 45 s per batch, at most 20 URLs per request, no `query` field so full content is returned):
```bash
curl -sS -X POST https://api.octen.ai/extract -H "x-api-key: $OCTEN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"urls":["https://example.com"],"format":"markdown"}'
```
`format` is `markdown` (default) or `text`. Each result row has `url`, `status` (`success` or `failed`), `title`, `full_content`. Keep input order; report per-URL failures instead of dropping them.

Error handling per the plugin: 401 -> check `OCTEN_API_KEY`; 403 -> account access or balance; 429 -> rate limit. Never echo response bodies that could contain the key.

| Hermes tool | How Claude does it |
|---|---|
| `web_search(query, limit)` | POST `/search` as above |
| `web_extract(urls, format)` | POST `/extract` in batches of 20 |

## Setup
1. Get an API key at https://octen.ai (per the plugin manifest).
2. `export OCTEN_API_KEY=<key>`
3. Optional MCP server, verified with `npm view octen-mcp`: name `octen-mcp`, version 0.7.1, described on npm as an MCP server for Octen web search plus URL extract (LLM-ready markdown with query-driven highlights). Add to `claude_desktop_config.json`:
```json
{"mcpServers":{"octen":{"command":"npx","args":["-y","octen-mcp"],"env":{"OCTEN_API_KEY":"<key>"}}}}
```
The server's own env var name and args were not verified here; check its README before use.

## Limits
- Hermes-side caching, result bucketing, private-URL checks and page truncation are not replicated.
- Octen API usage is billed to the user's Octen account; search queries and URLs are sent to Octen.
- API contract beyond the fields above follows Octen's OpenAPI (`https://docs.octen.ai/api-reference/openapi.json`, per the README); not re-verified here.

## Source
- Catalog entry (reviewed commit): https://github.com/Octen-Team/hermes-octen-plugin/tree/3af8a3fe200d93934c823485f66c3375a4508474
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/web-octen.yaml
