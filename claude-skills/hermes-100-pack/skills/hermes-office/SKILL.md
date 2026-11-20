---
name: hermes-office
description: Reference card for the Hermes hermes-office plugin, a Hermes Desktop renderer mod that draws Bot Mode agents as workers in an animated shared office (desks, tasks sent by envelope, pizza rewards, toy-drawer scenes, personalities, a newspaper of incidents). Not a working port. Consult it only when someone asks what "Hermes Office" was or whether Claude has a visual multi-agent office view. Do not trigger for real work.
---
# Hermes Office (reference card)

**Hermes original:** https://github.com/Adolanium/hermes-office @ e1e0255 (subdir `catalog`) · tier: community · category: desktop · license: MIT
**Port class:** D · a Hermes Desktop UI plugin (`desktop/plugin.js`, React via the Hermes Desktop SDK) with no agent tools, hooks or middleware.

## What the Hermes plugin does
The catalog package (`catalog/plugin.yaml`, `kind: standalone`, `provides_tools: []`, `provides_hooks: []`, `requires_env: []`) ships a single `desktop/plugin.js` that Hermes Desktop (Electron) loads; `catalog/__init__.py` registers nothing on the agent side. Per the repository README, the panel lists Bot Mode agents at desks, lets the user type a task and send it to a bot's existing Bot Chat via `host.openSession`, shows raised hands for approval or input requests (routing the user to the chat rather than answering), awards stars, parcels and pizza on confirmed completions, runs scripted scenes (wind-up mouse, iced carpet, lunch bell, UFO), stores per-bot personalities and furniture layout, and keeps a 60-record "Carpet Chronicle" of incidents without copying prompts or results. It requires a Desktop build with owner-routed `host.requestProfile`, `host.onEvent` and `host.openSession`.

## Equivalent in Claude
None identified. Claude Code and Cowork have no desktop-plugin renderer that a third-party React panel can be loaded into. Running several agents and sending each a task is possible with Claude Code subagents or sessions, but there is no animated office view and this card does not attempt to build one.

## Setup
None.

## Limits
- Entirely Hermes Desktop UI code (213 KB `plugin.js`); nothing is callable from Claude.
- Depends on Hermes Bot Mode names, avatars and session events.
- No upstream SKILL.md exists to copy; the plugin ships none.

## Source
- Catalog entry (reviewed commit): https://github.com/Adolanium/hermes-office/tree/e1e0255a48fe7a7549d8d0a5ef0747a41a0fb7e7/catalog
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-office.yaml
