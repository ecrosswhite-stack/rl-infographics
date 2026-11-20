---
name: hermes-pets-all
description: Reference card for the Hermes Desktop plugin hermes-pets-all ("All Pets"), which showed every installed Hermes mascot pet in a gallery pane and exposed a read-only list_pets tool. Read it only when someone asks what that plugin did or whether Claude has pets or mascots. It performs no action and has no Claude equivalent.
---
# All Pets (reference card)

**Hermes original:** https://github.com/poponline63/hermes-pets-all @ 2130957 · tier: community · category: desktop · license: MIT
**Port class:** D · a Hermes Desktop pane plus one tool that reads Hermes-internal state (`agent.pet.store`, `display.pet.slug`); the concept of an animated desktop pet does not exist in Claude.

## What the Hermes plugin does
Hermes Desktop ships animated "pets" (mascots) and a settings picker capped at 60 rows. This plugin opens a docked workspace pane (`host.openWorkspace`) that lists every installed pet with thumbnails, a search box, a live count and click-to-adopt, reachable from a status-bar chip, `Ctrl+Alt+P`, or the command palette. It calls the Desktop RPCs `pet.gallery` (with `localOnly: true`), `pet.thumb` and `pet.select`. The agent half registers one read-only tool, `list_pets`, which returns each pet's slug, display name, whether the sprite file exists, whether it is generated, and which pet is active. No network access, credentials or environment variables are involved.

## Equivalent in Claude
None identified. Claude has no mascot or pet feature and no per-profile pet store to list.

## Setup
None.

## Limits
- Desktop-only React pane written against `@hermes/plugin-sdk`; nothing to port.
- `list_pets` depends on `agent.pet.store` and `hermes_cli.config`, both Hermes-internal.
- The plugin ships no `skills/` directory, so there is nothing to copy despite the MIT license.

## Source
- Catalog entry (reviewed commit): https://github.com/poponline63/hermes-pets-all/tree/2130957d3d84d68f2e367c7aa2f52a61bf3c8064
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-pets-all.yaml
