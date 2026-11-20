---
name: obsidian-memory
description: Browse, search, edit and map the links of an Obsidian vault from Claude Code or Cowork, ported from the Hermes obsidian-memory dashboard plugin. Use it when the user mentions their Obsidian vault or notes: "find the note about X in my vault", "list notes tagged #project", "which notes link to this one", "show backlinks", "edit my daily note", "add a section to this note", "draw the link graph of my vault", or when OBSIDIAN_VAULT_PATH is set. The force-directed graph pane in the Hermes dashboard is UI-only; Claude produces an artifact or a list instead.
---
# Obsidian Memory

**Hermes original:** https://github.com/kyssta-exe/hermes-obsidian-memory @ 1123998 · tier: community · category: desktop · license: no LICENSE file found (plugin.yaml states MIT, no LICENSE file in the checkout)
**Port class:** C - everything the FastAPI backend does is plain filesystem work on markdown files that Claude can do directly; the React dashboard tab with the force-directed graph is Hermes UI and is not reproduced.

## What the Hermes plugin does
Adds an "Obsidian" tab to the Hermes dashboard (`/obsidian`). Its backend (`dashboard/api.py`) discovers vaults, scans every `*.md` under a vault, extracts `#tags` and front-matter `tags:` lists, extracts `[[wikilinks]]` (dropping the `|alias` part), computes backlinks, builds graph nodes and edges, renders markdown with code blocks, tables, callouts and checkboxes, and lets the user edit a note in place with save/cancel. Multi-vault switching, name search and folder or tag filters are included. It registers no agent tools and no hooks; the only setting is `OBSIDIAN_VAULT_PATH`.

## Equivalent in Claude
Work on the vault directory with the filesystem and shell tools.

| Hermes dashboard feature | How Claude does it |
|---|---|
| vault discovery | use `$OBSIDIAN_VAULT_PATH`; otherwise look for directories containing `.obsidian` in the primary vault's parent, `~/Documents/Obsidian/`, `~/obsidian-vaults/`, `~/vaults/` (the plugin's default primary path is `/home/ubuntu/ObsidianVault`, a server-specific value; ask the user instead) |
| list notes | `find "$VAULT" -name '*.md'` (skip `.obsidian/` and `.trash/`) |
| search by name or text | `rg -l` / `rg -n` over the vault |
| tags | regex `#(\w+)` on the body plus the `tags:` block inside the leading `---` front matter |
| outgoing links | regex `\[\[([^\]|]+?)(?:\|[^\]]+)?\]\]` |
| backlinks | `rg -l '\[\[Note Name' "$VAULT"` |
| view a note | `Read` the file; markdown renders in the reply |
| edit a note | `Edit` the file in place; confirm before overwriting, Obsidian picks the change up live |
| graph view | build nodes (notes) and edges (wikilinks) and render an HTML artifact with an SVG or force layout if the user wants a picture; otherwise list the top-linked notes |
| folder filter | group by the note's parent directory (`root` for top level) |

Keep Obsidian conventions: wikilinks resolve by note name without extension, front matter is YAML between `---` lines, and callouts use `> [!type]` syntax.

## Setup
1. Export `OBSIDIAN_VAULT_PATH=/path/to/your/vault` (optional; otherwise tell Claude where the vault is).
2. Optional MCP alternative: the package `mcp-obsidian` exists on npm (version 1.0.0, "Model Context Protocol server for Obsidian Vaults", per `npm view`) and on PyPI (version 0.2.3, per `pip index versions`). Their configuration was not reviewed here; consult the package README before adding a `claude_desktop_config.json` entry.

## Limits
- No live graph pane or in-app rendering; visualization is an artifact Claude generates on request.
- Editing writes files directly; there is no undo beyond Obsidian's own file recovery or git.
- Vault auto-discovery defaults in the plugin are tuned to one author's server layout.
- No LICENSE file in the checkout, so no upstream text copied (there are no `skills/` anyway).
- Not verified: behavior described per `dashboard/api.py`, not executed.

## Source
- Catalog entry (reviewed commit): https://github.com/kyssta-exe/hermes-obsidian-memory/tree/11239984e82caa6dbf02106ce315e3019368b5fc
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/obsidian-memory.yaml
