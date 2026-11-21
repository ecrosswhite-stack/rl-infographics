---
name: web-oxylabs
description: Reference card only. Records what is known about the Hermes "web-oxylabs" plugin, an Oxylabs AI Studio web search and extraction provider that required OXYLABS_API_KEY, whose source repository is no longer public. Use this card when a user asks what web-oxylabs did or whether Claude can use Oxylabs AI Studio; it holds no verified API details and should not be triggered for real web search or scraping work.
---
# Oxylabs AI Studio web provider (reference card)

**Hermes original:** https://github.com/oxylabs/hermes-web-oxylabs @ e6a5ee8 · tier: community · category: web · license: no LICENSE file found (no checkout available)
**Port class:** D · the only source of truth is the catalog row; the repository could not be read, so nothing can be reproduced with confidence.

## What the Hermes plugin does
Per the catalog description: "Oxylabs AI Studio web search and extraction provider for Hermes Agent. Requires OXYLABS_API_KEY (sign up at https://aistudio.oxylabs.io/api-key)." The catalog marks it `still_in_catalog: false` and lists no tools or hooks. By analogy with other Hermes `web` providers it most likely registered a web search/extract provider through `register_web_search_provider`, but that is not verified: the checkout at the reviewed commit is empty (no `plugin.yaml`, `__init__.py` or README was fetched).

## Equivalent in Claude
None documented. Oxylabs AI Studio is a paid third-party API; without the plugin source the endpoints, request shapes and response fields it used are not verified, so this skill does not instruct Claude to call them. If the user has Oxylabs documentation at hand, Claude Code can call the API with curl using `OXYLABS_API_KEY`, following that documentation rather than this card.

## Setup
None. (Original requirement: `OXYLABS_API_KEY` from https://aistudio.oxylabs.io/api-key.)

## Limits
- Source repository no longer public at 2026-11-20: the clone at the reviewed commit returned no files, and the repository could not be read from this session.
- No endpoints, parameters or install commands are given because none could be verified.
- Oxylabs AI Studio is a paid service that receives the URLs and queries you send it; usage costs money.

## Source
- Catalog entry (reviewed commit): https://github.com/oxylabs/hermes-web-oxylabs/tree/e6a5ee8fbabae43a7cd7f77610f187dbc890e76a
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/web-oxylabs.yaml
