---
name: web-search-plus
description: Run web searches and clean page extraction against the user's own search-provider API keys (Serper, Brave, Tavily, Exa, Linkup, Firecrawl, You.com, Parallel, Perplexity, SerpBase, Querit, Keenable, a SearXNG instance) with provider fallback and an optional multi-provider research mode, replicating the Hermes web-search-plus plugin. Use it when the user says "search the web with my Tavily/Serper/Brave key", "which of my search providers are configured", "research this topic across several providers and cite sources", "extract clean text from these URLs", "web_search_plus" or "web_extract_plus", or when Claude needs current information and the environment carries one of these *_API_KEY variables. Uses the plugin's exact env var names and endpoints.
---
# Web Search Plus

**Hermes original:** https://github.com/robbyczgw-cla/hermes-web-search-plus @ 053fcce · tier: community · category: web · license: MIT
**Port class:** B · every provider is a documented HTTPS API keyed by an env var; Claude can call them with curl and apply the same routing and fallback logic by hand.

## What the Hermes plugin does
Registers two tools, `web_search_plus(query, provider="auto", freshness, mode="research", quality_report, ...)` and `web_extract_plus(urls, provider, render_js, ...)`, an opt-in native backend `wsp`, and an `on_session_start` hook that only logs a hint when no provider is configured. Routing v2 picks a provider from query language, intent and configured keys, falls back to another provider on failure, caches results, and can emit a quality report. Keys are read from `~/.hermes/plugins/config.json` (override `WEB_SEARCH_PLUS_CONFIG`) or the env vars below. Nothing is required globally: one search-capable key enables search, one extraction-capable key enables extract. Optional local providers: SearXNG, Keenable public tier, and a separately installed DonSeTch binary (`DONSETCH_BIN`, AGPL-3.0-only, stdio MCP).

## Equivalent in Claude
Endpoints and header names are copied from `providers.py`; request body fields beyond `q`/`query`/`url(s)` are not enumerated here, so read each provider's docs for extras such as freshness or domain filters.

| Provider (env var) | Search endpoint and auth | Extract endpoint |
|---|---|---|
| Serper (`SERPER_API_KEY`) | `POST https://google.serper.dev/search` or `/news` (the only `search_type` values in the source; `/images` is used for image metadata) header `X-API-KEY` | `POST https://scrape.serper.dev` header `X-API-KEY` |
| Brave (`BRAVE_API_KEY`) | `GET https://api.search.brave.com/res/v1/web/search?q=...` header `X-Subscription-Token` | none |
| Tavily (`TAVILY_API_KEY`) | `POST https://api.tavily.com/search` with `api_key` in the JSON body | `POST https://api.tavily.com/extract` header `Authorization: Bearer` |
| Exa (`EXA_API_KEY`) | `POST https://api.exa.ai/search` (also `/findSimilar`) header `x-api-key` | `POST https://api.exa.ai/contents` header `x-api-key` |
| Linkup (`LINKUP_API_KEY`) | `POST https://api.linkup.so/v1/search` header `Authorization: Bearer` | `POST https://api.linkup.so/v1/fetch` Bearer |
| Firecrawl (`FIRECRAWL_API_KEY`) | `POST https://api.firecrawl.dev/v2/search` Bearer | `POST https://api.firecrawl.dev/v2/scrape` Bearer |
| You.com (`YOU_API_KEY`) | `GET https://ydc-index.io/v1/search` header `X-API-KEY` | `https://ydc-index.io/v1/contents` header `X-API-Key` |
| Parallel (`PARALLEL_API_KEY`) | `POST https://api.parallel.ai/v1/search` header `x-api-key` | `POST https://api.parallel.ai/v1/extract` header `x-api-key` |
| Perplexity (`PERPLEXITY_API_KEY`) | `POST https://api.perplexity.ai/chat/completions` (chat-completions style; result handling per source, not detailed here) | none |
| SerpBase (`SERPBASE_API_KEY`) | `https://api.serpbase.dev/google/search` header `X-API-Key` | none |
| Querit (`QUERIT_API_KEY`) | base `https://api.querit.ai` Bearer | none |
| Keenable (`KEENABLE_API_KEY`, keyless public tier allowed) | `https://api.keenable.ai/v1/search` header `X-API-Key` | `https://api.keenable.ai/v1/fetch` |
| SearXNG (`SEARXNG_INSTANCE_URL`, `SEARXNG_ALLOW_PRIVATE`) | `GET $SEARXNG_INSTANCE_URL/search?q=...&format=json` | none |
| Octen via Monid (`MONID_API_KEY`), TinyFish (`TINYFISH_API_KEY`), DonSeTch (`DONSETCH_BIN`) | explicit-only in the plugin; endpoints not copied here, read `providers.d/` first | per source |

Workflow:
1. `env | grep -E 'SERPER_API_KEY|BRAVE_API_KEY|TAVILY_API_KEY|EXA_API_KEY|LINKUP_API_KEY|FIRECRAWL_API_KEY|YOU_API_KEY|PARALLEL_API_KEY|PERPLEXITY_API_KEY|SERPBASE_API_KEY|QUERIT_API_KEY|KEENABLE_API_KEY|SEARXNG_INSTANCE_URL' | cut -d= -f1` to see what is configured (never print values). This is the plugin's `setup.py status`.
2. `web_search_plus(query)`: pick a provider in the user's priority order (plugin default recommendation: You.com, then Serper, Exa, Firecrawl, Tavily, Linkup, Parallel); on HTTP error or empty results try the next (plugin fallback). Return title, URL, snippet per result and name the provider used (the quality report).
3. `mode="research"`: run the query on 2-3 configured providers, merge by URL, prefer results seen by more than one provider, and cite every URL.
4. `web_extract_plus(urls)`: use Linkup `/v1/fetch`, Firecrawl `/v2/scrape`, Tavily `/extract`, Exa `/contents` or Serper scrape with the configured key; without any extraction key, `curl -sL` the page and reduce to text with `python3 -I` (`html.parser`), which is the plugin's keyless fallback in spirit, not its code.
5. Cache: keep per-session results in memory only; the plugin's disk cache is optional and not required.

Verified MCP alternatives (`npm view <pkg> name version description`): `@brave/brave-search-mcp-server` 2.2.0 "Brave Search MCP Server: web results, images, videos, rich results, AI summaries, and more."; `tavily-mcp` 0.2.22 "MCP server for advanced web search using Tavily"; `exa-mcp-server` 3.5.1 "Connect AI agents to Exa for web search, content fetching, and multi-step research." Their config keys were not checked here; follow each package's README.

## Setup
1. Obtain at least one search key (plugin's recommended starters: `YOU_API_KEY`, `SERPER_API_KEY`) and, for extraction, `LINKUP_API_KEY` or another extraction-capable key; or run a SearXNG instance and set `SEARXNG_INSTANCE_URL`.
2. Export the keys in the shell or a 0600 env file using the exact names above.
3. Optional MCP: add one of the verified packages above to `claude_desktop_config.json` per its README.

## Limits
- Routing v2 heuristics (language/script detection, intent classes, provider demotions), disk cache, budget preflight, operator console and the `wsp` native backend are not replicated; Claude applies the simple priority-plus-fallback rule above.
- Provider privacy differs; the README flags TinyFish terms (training on customer data, no fixed deletion period) and points to a provider privacy matrix. Tell the user which third party receives a query.
- Paid providers bill per request; the plugin's budget checks are not replicated, so state the provider before high-volume runs.
- DonSeTch is a separate AGPL-3.0-only program; this skill does not install or redistribute it.
- No upstream skills/ directory exists to copy.

## Source
- Catalog entry (reviewed commit): https://github.com/robbyczgw-cla/hermes-web-search-plus/tree/053fcce7432c58d7329ef556c971394c80040f98
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/web-search-plus.yaml
