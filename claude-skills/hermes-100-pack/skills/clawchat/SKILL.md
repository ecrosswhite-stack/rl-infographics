---
name: clawchat
description: Reference card for the Hermes clawchat gateway plugin (ClawChat social messaging platform by CLAWLING). Read it only when someone asks what the Hermes ClawChat integration did, how its clawchat_* tools or Liveware app hosting worked, or whether Claude can connect to ClawChat. It does not perform ClawChat actions; the integration is a Hermes gateway adapter with no Claude equivalent.
---
# ClawChat (reference card)

**Hermes original:** https://github.com/clawling/clawchat-plugin-hermes-agent @ c1e009e · tier: community · category: platform · license: MIT
**Port class:** D — a `kind: platform` gateway adapter plus 34 tools that call the ClawChat backend through a token the plugin obtains by exchanging an activation code inside Hermes; nothing in Claude hosts that connection.

## What the Hermes plugin does
Registers the `clawchat` gateway platform (ClawChat Protocol v2 over WebSocket) so a Hermes agent appears as a contact inside the ClawChat app, with group chats, friend requests, moments (posts), comments, reactions, avatars and media. It provides the hooks `pre_api_request` and `pre_gateway_dispatch` and 34 `clawchat_*` tools, including `clawchat_get_account_profile`, `clawchat_search_users`, `clawchat_send_friend_request`, `clawchat_list_moments`, `clawchat_create_moment`, `clawchat_react_message`, `clawchat_memory_search|read|write|edit`, `clawchat_metadata_sync|update`, `clawchat_register_app|list_apps|unregister_app` and `clawchat_liveware_login`. Activation uses `hermes clawchat activate <code>` or the installer `npx -y @clawling/clawchat-plugin-install-cli@latest install --target hermes`. The default backend is `https://app.clawling.com` (`CLAWCHAT_BASE_URL`, with `CLAWCHAT_MEDIA_BASE_URL` for media), per `clawchat_gateway/api_client.py` and `config.py`. Five bundled skills cover core usage, Liveware app hosting (exposing a local web service through the `liveware` CLI), a Liveware sample app, Liveware development and a first-load greeting file at `~/clawchat/greeting.md`.

## Equivalent in Claude
None identified. ClawChat is a proprietary messaging platform; its agent identity, token store, WebSocket gateway and the `liveware` tunnel CLI are provisioned by the plugin installer for Hermes or OpenClaw runtimes only. Claude has no connector for ClawChat. The only transferable piece is the general web-app guidance in the `clawchat-liveware-dev` skill (plain HTML/CSS/JS frontend, Python standard-library backend bound to 127.0.0.1, content-hashed static assets), which Claude Code can follow for any small local web service.

## Setup
None. (For reference: the installer package `@clawling/clawchat-plugin-install-cli` exists on npm, version 0.4.9, description "CLI for ClawChat plugin installation and updates", per `npm view`. It installs into Hermes or OpenClaw, not into Claude.)

## Limits
- No ClawChat API documentation is bundled in the checkout beyond the Python client; endpoints and the activation-code exchange were not transcribed, so no curl recipe is offered.
- The platform adapter, group-message coalescing, permission gates, profile sync and token refresh all run inside the Hermes gateway process.
- Liveware hosting requires the `liveware` binary and a ClawChat login performed by the plugin; neither exists in Claude.
- The upstream skills are copied verbatim under `references/` for reading only; the tool names they mention do not exist in Claude.
- Data sent through this plugin goes to CLAWLING PTE. LTD. servers (`app.clawling.com`).

## Source
- Catalog entry (reviewed commit): https://github.com/clawling/clawchat-plugin-hermes-agent/tree/c1e009e6f66cd25aa729f72de1808b2d451089a6
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/clawchat.yaml
- Upstream skills (MIT): `references/upstream-clawchat-core.md`, `references/upstream-clawchat-liveware.md`, `references/upstream-clawchat-liveware-dev.md`, `references/upstream-clawchat-liveware-sample.md`, `references/upstream-clawchat-set-greeting.md`
