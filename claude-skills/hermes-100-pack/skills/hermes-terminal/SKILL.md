---
name: hermes-terminal
description: Reference card for the Hermes "hermes-terminal" Desktop plugin, which opened the Hermes TUI (hermes --tui) as a workspace tab inside Hermes Desktop on the gateway that window was connected to. Consult it only when a user asks what this plugin did or whether Claude has an equivalent; it performs no work and should not trigger on ordinary terminal or shell tasks.
---
# Hermes Terminal (reference card)

**Hermes original:** https://github.com/Adolanium/hermes-terminal @ 43658bf · tier: community · category: desktop · license: no LICENSE file found
**Port class:** D — a Hermes Desktop renderer plugin (single `desktop/plugin.js`) that embeds the Hermes TUI; it has no tools, hooks or data and nothing for Claude to execute.

## What the Hermes plugin does
A `standalone` manifest with `provides_tools: []`, `provides_hooks: []`, `requires_env: []`. `__init__.py` registers nothing on the agent side; the Electron app loads `desktop/plugin.js`, which adds a sidebar item **TUI**, a palette command **TUI: Open** and the shortcut Ctrl/Cmd+Alt+T. Each opens the stock `hermes --tui` of the connected gateway (local or remote) in a main-area tab over the same PTY the web dashboard Chat tab uses, with a session rail backed by `session.list` to resume sessions, a resizable divider, and WebSocket reconnect by re-minting the ticket. Installed by copying `plugin.js` to `$HERMES_HOME/desktop-plugins/hermes-terminal/`.

## Equivalent in Claude
None identified. The plugin is a view onto Hermes' own TUI inside Hermes Desktop; Claude Code is itself a terminal interface, so there is nothing to port.

## Setup
None.

## Limits
- Entirely Hermes Desktop UI; not reproducible as a skill.
- No license file in the checkout, so no upstream text is copied.

## Source
- Catalog entry (reviewed commit): https://github.com/Adolanium/hermes-terminal/tree/43658bf3c883178bf035d2163f7f541500d17407/catalog
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-terminal.yaml
