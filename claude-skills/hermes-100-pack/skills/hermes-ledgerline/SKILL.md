---
name: hermes-ledgerline
description: Reference card only. Describes Ledgerline, a Hermes Desktop plugin that shows per-session and per-model token and dollar costs, cache-hit splits, budgets, live spend chips and AI "explain this session's cost" audits inside the Hermes Desktop app. Consult it when someone asks "what is hermes-ledgerline", "is there a Claude version of Ledgerline", or wants session cost dashboards for Hermes. It performs no work and should not trigger on cost or billing questions about Claude itself.
---
# Ledgerline (Hermes Desktop cost pane)

**Hermes original:** https://github.com/Adolanium/hermes-ledgerline @ 9be4b85 (subdir `catalog`) · tier: community · category: desktop · license: no LICENSE file found
**Port class:** D — a single Electron renderer plugin (`desktop/plugin.js`) built on the Hermes Desktop plugin SDK and the gateway's internal REST/RPC bridge; `__init__.py` registers nothing.

## What the Hermes plugin does
Adds a Ledgerline page, sidebar entry, command-palette action (Ctrl/Cmd+Alt+L) and statusbar chip to Hermes Desktop. It reads the gateway's own session list, `session.usage` RPC and `/api/analytics/usage` route to show spend today/week/month, per-model token splits (input, cache reads, cache writes, output), per-helper-task costs, budgets with 80 % and 100 % warnings, cost recommendations, and a live running cost for the current turn. "Quick explain" and "full audit" send a session digest to the user's configured Hermes model; scheduled spend reports and budget alerts run through `hermes cron` and `hermes send` on the gateway host. Manifest: `kind: standalone`, `provides_tools: []`, `provides_hooks: []`, `requires_env: []`.

## Equivalent in Claude
None identified. The data source (Hermes gateway session store and analytics routes) and the rendering surface (Hermes Desktop plugin SDK, `host.request` JSON-RPC) do not exist in Claude. For Claude Code usage, the `/cost` command in a session and the account usage pages are the places to look; they are not a port of this plugin.

## Setup
None.

## Limits
- Not portable: the whole plugin is desktop UI code loaded by Hermes Desktop; it requires `ctx.onDispose` from the desktop SDK and an internal REST bridge the README calls "not a public SDK guarantee".
- No LICENSE file in the checkout, so no upstream text is copied; the README is summarized above.
- AI explain/audit actions incur model usage on the user's Hermes providers; budget alerts can post to messaging platforms the gateway already has. Neither applies here.

## Source
- Catalog entry (reviewed commit): https://github.com/Adolanium/hermes-ledgerline/tree/9be4b850c874cebaa18b0077cdc5164b5e7b953b/catalog
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-ledgerline.yaml
