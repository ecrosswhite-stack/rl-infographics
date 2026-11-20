---
name: gondola-provider
description: Reference card only. Describes the Hermes "gondola-provider" model-provider plugin, which registered Gondola (a USDC-settled, OpenAI-compatible marketplace for Venice AI inference at api.gondola-ai.com) as a model backend for Hermes. Use this card when a user asks what gondola-provider did, whether Claude can switch its own model to Gondola, or how to query Gondola's model catalog. It does not change which model Claude runs on; do not trigger it for ordinary inference work.
---
# Gondola model provider (reference card)

**Hermes original:** https://github.com/Gondola-Market/hermes-gondola-provider @ ad3f352 · tier: community · category: models · license: MIT
**Port class:** D · a `kind: model-provider` plugin; Claude cannot swap its own inference backend, so the core feature has no Claude equivalent.

## What the Hermes plugin does
Per the README and `__init__.py`, it registers a `ProviderProfile` named `gondola` (alias `gondola-ai`) with `base_url="https://api.gondola-ai.com/v1"`, `auth_type="api_key"`, env vars `GONDOLA_API_KEY` and `GONDOLA_BASE_URL`, and a curated fallback list (`deepseek-v4-flash`, `claude-sonnet-5`, `kimi-k2-7-code`, `qwen3-coder-480b-a35b-instruct-turbo`, `venice-uncensored-1-2`). `fetch_models()` calls `GET {base_url}/models` with a Bearer header and keeps entries whose `endpoint` is `/v1/chat/completions` (or `modality == "text"`). It registers no agent tools or hooks. Gondola requests are metered against a prepaid USDC balance.

## Equivalent in Claude
None for the provider role: Claude's model is chosen by the Claude app, not by a plugin. If a user only wants to inspect the catalog, Claude Code can run `curl -s -H "Authorization: Bearer $GONDOLA_API_KEY" https://api.gondola-ai.com/v1/models` (URL copied from the plugin source; the README says this endpoint is public). Calling chat completions there on the user's behalf is possible with curl but spends their USDC balance and is not what the plugin did.

## Setup
None for Claude. (The plugin itself needed `GONDOLA_API_KEY`, minted at https://gondola-ai.com/wallet?tab=keys.)

## Limits
- Claude cannot run on Gondola-hosted models; the `hermes model` / `--provider gondola` behavior has no counterpart.
- Any direct call to `api.gondola-ai.com` costs money (USDC on Base) per the README; warn the user before issuing paid requests.
- Model ids in the fallback list are copied from the plugin and were not verified against the live catalog.

## Source
- Catalog entry (reviewed commit): https://github.com/Gondola-Market/hermes-gondola-provider/tree/ad3f352b6a9814f1b550c819bee5ef2fb92a1851
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/gondola-provider.yaml
