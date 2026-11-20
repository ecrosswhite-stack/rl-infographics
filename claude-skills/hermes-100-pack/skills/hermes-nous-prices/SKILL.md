---
name: hermes-nous-prices
description: Reference card for the Hermes Desktop plugin "Nous Portal Pricing" (catalog name hermes-nous-prices), which showed Nous Portal model prices, sale discounts, account balance and the default model inside Hermes Desktop. Read it only when someone asks what that plugin did or whether Claude can show Nous Portal pricing. It performs no action and has no Claude equivalent.
---
# Nous Portal Pricing (reference card)

**Hermes original:** https://github.com/Adolanium/hermes-nous-prices @ 94f9943 (subdir `catalog`) · tier: community · category: desktop · license: no LICENSE file found
**Port class:** D - a Hermes Desktop UI plugin whose data comes from Hermes-internal Python modules (`hermes_cli.inventory`, `agent.billing_view`) and the Desktop plugin SDK; there is no external API Claude could call.

## What the Hermes plugin does
Adds a `/nous-prices` page, sidebar entry, command-palette command, `Ctrl/Cmd+Alt+P` keybinding and a status-bar price chip to Hermes Desktop. It lists Nous Portal models with input and output prices in USD per million tokens, cached-read pricing, sale percentages, free models, lab grouping, search and filters, shows the signed-in account's plan and spendable balance, and lets the user set the default model for the active profile. A gateway-side FastAPI companion (`dashboard/plugin_api.py`) exposes `/health`, `/catalog`, `/billing` and `/default-model`, each of which imports Hermes internals (`build_model_options_payload`, `build_billing_state`, `load_picker_context`). It registers no agent tools and requires no environment variables; prices are cached locally per profile and refreshed every five minutes.

## Equivalent in Claude
None identified. The pricing and balance data are read from the Hermes installation's own model catalog and the user's Nous Portal login state inside Hermes; the plugin source contains no Nous Portal HTTP endpoint that Claude could query directly (the only URL is the portal home, `https://portal.nousresearch.com`, used for an "open portal" link). A user who wants current Nous model prices should open that portal in a browser.

## Setup
None.

## Limits
- Desktop-only renderer plugin written against `@hermes/plugin-sdk` (React); no Claude surface renders it.
- Account balance and default-model switching depend on Hermes profile configuration and `hermes_cli` modules.
- No API documentation for the Nous Portal pricing feed is present in the checkout, so nothing is reproduced.
- No LICENSE file in the repository; no upstream text copied.

## Source
- Catalog entry (reviewed commit): https://github.com/Adolanium/hermes-nous-prices/tree/94f99436786e6fbbfcce161635d11c67bf094c8e/catalog
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-nous-prices.yaml
