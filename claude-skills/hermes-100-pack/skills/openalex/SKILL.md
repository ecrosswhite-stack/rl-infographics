---
name: openalex
description: Search and map scholarly literature through the OpenAlex REST API (works, authors, sources, institutions, topics) with the cost discipline of the Hermes openalex plugin: resolve names to ids for free, count with group_by before searching, traverse citations, fetch records by id or DOI for free, probe fulltext availability, and track the per-call USD cost against a session budget. Use it when a user asks for papers on a topic, "how many papers since 2015 on X", "who publishes most on Y", "what cites this DOI", "find this author's works", "literature review", "citation tracing", bibliometrics, h-index, open access status, or anything OpenAlex. OPENALEX_API_KEY is optional.
---
# OpenAlex scholarly search

**Hermes original:** https://github.com/Adolanium/hermes-plugin-openalex @ 04e673e · tier: community · category: tools · license: MIT
**Port class:** B — the plugin is an httpx client for `https://api.openalex.org` plus local budgeting and response shaping; Claude can issue the same requests with curl and apply the same rules by hand.

## What the Hermes plugin does
Per plugin.yaml and the README, it registers ten tools: `openalex_resolve` (name to id, free), `openalex_get` (metadata by OpenAlex id, DOI, ORCID, ROR, ISSN or PMID, up to 20 ids, free), `openalex_count` (totals and `group_by`, $0.0001), `openalex_search` (records, $0.001), `openalex_related` (cited_by, references, related, $0.0001), `openalex_account` (budget ledger), `openalex_fields` (valid filter names, offline), `openalex_fulltext` (availability probe free, download $0.01 with `confirm`), `openalex_harvest` (cursor paging, full profile) and `openalex_classify` (text to topics, $0.01, off by default). Hooks `on_session_start` and `on_session_reset` reset a session budget (default $0.05). `BASE = "https://api.openalex.org"` in `client.py`; `OPENALEX_API_KEY` is sent as a Bearer header. It reconstructs inverted abstracts, strips deprecated `concepts`, caps author lists, and refuses locally when a call would exceed the session budget.

## Equivalent in Claude
Read `references/upstream-query-syntax.md` and `references/upstream-lit-review.md` (copied from the plugin, MIT) before composing queries. Then use curl, with `-H "Authorization: Bearer $OPENALEX_API_KEY"` when the key is set.

| Hermes tool | Request (base `https://api.openalex.org`) | Price per plugin README |
|---|---|---|
| `openalex_resolve` | `GET /autocomplete/<entity>?q=<name>` where entity is `authors`, `institutions`, `sources`, `works`, `topics` | $0 |
| `openalex_get` | `GET /works/W...`, `GET /works/doi:10....`, `GET /authors/orcid:...`, `GET /institutions/ror:...`; several ids: `GET /works?filter=openalex:W1|W2` | $0 (prefixed id form); URL form `https://doi.org/...` is billed |
| `openalex_count` | `GET /works?filter=<f>&group_by=<field>` or `&search=<q>&group_by=...`; read `meta.count` and `group_by[]` | $0.0001 |
| `openalex_search` | `GET /works?search=<q>&per_page=25` or `filter=title_and_abstract.search:<q>`; `per_page` max 200 | $0.001 |
| `openalex_related` | `GET /works?filter=cites:W...` (references), `filter=cited_by:W...` (citing), `filter=related_to:W...`; add `sort=cited_by_count:desc` | $0.0001 |
| `openalex_fields` | the filter lists in `references/upstream-query-syntax.md` | $0 |
| `openalex_fulltext` | probe: inspect `has_fulltext` and `best_oa_location` on the work record; download only after the user confirms the $0.01 charge | $0 probe / $0.01 download |
| `openalex_account` | keep a running tally of the prices above in the conversation; read `X-RateLimit-Remaining` and `Retry-After` headers with `curl -D -` | $0 |
| `openalex_harvest` | `GET /works?filter=...&per_page=200&cursor=*`, then follow `meta.next_cursor`; estimate pages times $0.0001 first and ask before large harvests | $0.0001 per page |
| `openalex_classify` | not ported (costs $0.01 per call and is disabled by default upstream) | |

Rules carried over from the plugin: resolve names to ids instead of filtering on `display_name`; count before you search; use prefixed ids (`doi:`, `orcid:`, `ror:`); `sort=field:desc`, not `-field`; a 400 is billed $0.0001 so check filter names first; a 429 with a small `Retry-After` is a throttle (retry once), a 429 with tens of thousands of seconds is the spent daily budget (do not retry, fall back to free id lookups); reconstruct `abstract_inverted_index` into prose before quoting; ignore `concepts`. Stop and tell the user when the running session total reaches $0.05 unless they raised it.

## Setup
1. Optional: free key from https://openalex.org/settings/api, then `export OPENALEX_API_KEY=<key>` (raises the daily allowance from $0.10 to $1.00 per the README).
2. curl and jq.
3. No MCP server is listed; none was verified.

## Limits
- The local budget guard, cost prediction, cache and response shaping are manual here; Claude must apply the price table itself and will not refuse a call automatically.
- Prices are copied from the plugin README (February 2026) and may have changed; the API bills in USD after the daily allowance.
- `openalex_classify`, the `hermes openalex` terminal CLI and the `/openalex` slash command are not ported.
- Semantic search returned HTTP 500 per the README; avoid it.
- No live request was made during this port; endpoint paths follow the plugin source and the OpenAlex filters it documents.

## Source
- Catalog entry (reviewed commit): https://github.com/Adolanium/hermes-plugin-openalex/tree/04e673e34bfd09ea9cf20626373ce48df096f813
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/openalex.yaml
