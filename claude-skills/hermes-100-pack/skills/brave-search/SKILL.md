---
name: brave-search
description: Run live web searches through the Brave Search API, replicating the Hermes `brave_web_search` tool with the user's BRAVE_API_KEY. Use when the user says "search the web with Brave", "use Brave Search", "look this up with my Brave key", wants fresh ranked search-engine results filtered by country, language, freshness (past day/week/month/year) or SafeSearch, or has BRAVE_API_KEY set and wants a result list rather than a single page fetch. Also covers adding a verified Brave Search MCP server to Claude Desktop.
---
# Brave Search

**Hermes original:** https://github.com/rabilrbl/hermes-brave-search-plugin @ 4134cbe · tier: community · category: web · license: MIT
**Port class:** B — the plugin is a thin wrapper over one Brave Search REST endpoint that Claude can call with curl or Python.

## What the Hermes plugin does
Registers one tool, `brave_web_search`, in the `brave-search` toolset. Per the plugin source (tools.py) the handler sends GET `https://api.search.brave.com/res/v1/web/search` with header `X-Subscription-Token: $BRAVE_API_KEY`, forwards `q`, `count` (clamped 1-20, default 10), `safesearch` (default `moderate`) and the optional `country`, `search_lang`, `freshness` parameters, with a 20 second timeout and no retry. It returns `{query, count, results[]}` where each result carries title, url, description (HTML stripped), age, language, source (`profile.long_name`) and display_url. Requires `BRAVE_API_KEY` (plugin.yaml).

## Equivalent in Claude
1. Check `BRAVE_API_KEY` is set (`test -n "$BRAVE_API_KEY"`). If not, stop and follow Setup.
2. Send the same request the plugin sends:
   ```bash
   curl -sS -G --compressed "https://api.search.brave.com/res/v1/web/search" \
     -H "Accept: application/json" -H "Accept-Encoding: gzip" \
     -H "X-Subscription-Token: $BRAVE_API_KEY" \
     --data-urlencode "q=<query>" --data-urlencode "count=10" \
     --data-urlencode "safesearch=moderate"
   ```
   Add `--data-urlencode "country=us"`, `--data-urlencode "search_lang=en"` or `--data-urlencode "freshness=pw"` when the user asks for them.
3. Read `.web.results[]` from the JSON. Report title, url, description, age and `profile.long_name`. Strip HTML tags from title and description, as the plugin does.
4. Keep `count` in 1-20. Freshness values per the plugin README: `pd`, `pw`, `pm`, `py`. SafeSearch values: `off`, `moderate`, `strict`.
5. On HTTP status 400 or above, report the status and the start of the body. Do not retry in a loop; the plugin does not retry.

| Hermes tool | How Claude does it |
|---|---|
| `brave_web_search(query, count, country, search_lang, freshness, safesearch)` | curl GET to `/res/v1/web/search` as above, then summarize `.web.results` |

Optional MCP route, verified with `npm view` on 2026-11-20: `@brave/brave-search-mcp-server` version 2.2.0 ("Brave Search MCP Server: web results, images, videos, rich results, AI summaries, and more.") and the older `@modelcontextprotocol/server-brave-search` version 0.6.2 ("MCP server for Brave Search API integration"). Their tool names and env var names were not verified here; read the package README before relying on them.

## Setup
1. Create a key at https://api-dashboard.search.brave.com/app/keys (sign up, "+ Add API Key", copy the subscription token).
2. `export BRAVE_API_KEY="..."` in the environment Claude Code or Cowork runs in.
3. Optional, Claude Desktop MCP server (package name verified, env var name not verified):
   ```json
   {"mcpServers":{"brave-search":{"command":"npx","args":["-y","@brave/brave-search-mcp-server"],"env":{"BRAVE_API_KEY":"<key>"}}}}
   ```

## Limits
- Brave Search is a metered, paid API; every call counts against the subscription quota.
- Query text is sent to Brave, a third party. Do not send confidential text as a query without the user's awareness.
- Only the `web.results` block is mapped; news, video and discussion blocks are dropped, as in the plugin.
- The MCP packages are confirmed to exist on npm only; their behavior was not tested.
- No caching or rate limiting is replicated because the plugin has none.

## Source
- Catalog entry (reviewed commit): https://github.com/rabilrbl/hermes-brave-search-plugin/tree/4134cbef910c14c63e6b284b0820b30f3811ab47
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/brave-search.yaml
