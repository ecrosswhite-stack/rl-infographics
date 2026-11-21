---
name: mnemosyne
description: "Keep durable, unlimited plain-markdown memories in a local vault folder and search them with ripgrep, the way the Hermes Mnemosyne memory provider did: write one YAML-frontmatter .md file per memory into YYYY-MM/ folders, search file names and content with rg, and read matches back before answering. Use it when a user asks Claude to \"remember this in my vault\", \"store a note in my Obsidian memory folder\", \"search my memory vault\", \"what did I say about X\" against a markdown vault, or wants a git-tracked, cloud-free memory store. The Hermes write-through mirror and per-turn prefetch injection are not reproduced."
---
# Mnemosyne vault memory

**Hermes original:** https://github.com/Devs-Foundation/mnemosyne @ ad7ece7 · tier: community · category: memory · license: MIT
**Port class:** C · the two tools (`mnemosyne_add`, `mnemosyne_search`) are plain file writes plus ripgrep, which Claude can do; the memory-provider hooks (write-through mirror of Hermes `memory add`, prefetch injection before each turn, system-prompt block) need the Hermes MemoryProvider runtime.

## What the Hermes plugin does
Per the README and `__init__.py`, `register()` calls `ctx.register_memory_provider(MnemosyneProvider)`. The provider stores each memory as a markdown file with frontmatter (`id`, `date`, `category`, `tags`, `source`) under `<vault>/YYYY-MM/YYYY-MM-DD-<slug>.md`, auto-initializes a git repo, mirrors every built-in `memory add` into the vault (`on_memory_write`), searches the vault with `rg` before each turn and injects up to `max_prefetch_results` (default 5) entries or `max_prefetch_chars` (default 2000), and exposes two tools: `mnemosyne_search(query, limit=10)` and `mnemosyne_add(content, category="general", tags="")`. Config keys: `plugins.mnemosyne.vault_path` (default `~/hermes-memory-vault`). No env vars, no network.

## Equivalent in Claude
Agree a vault path with the user once (default from the plugin: `~/hermes-memory-vault`; an Obsidian vault folder works the same).

| Hermes tool | How Claude does it |
|---|---|
| `mnemosyne_add` | Write `<vault>/<YYYY-MM>/<YYYY-MM-DD>-<slug>.md` containing the frontmatter block (`id`: 8 hex chars, `date`: ISO UTC, `category`, `tags`, `source: manual`), a `# <first 80 chars>` heading, then the content. Slug: lowercase, non-alphanumerics to hyphens, max 60 chars. Then `git -C <vault> add -A && git -C <vault> commit -m "memory: <slug>"` if the vault is a repo. |
| `mnemosyne_search` | `rg --ignore-case --max-count 1 --no-heading --line-number --with-filename --glob '*.md' --glob '!.git*' -- '<term1>|<term2>' <vault>` (the plugin ORs the whitespace-split terms); take the first `limit` distinct files, read their frontmatter and first lines, and present path, date, category, matched line. Fall back to `grep -ril` if `rg` is missing. |
| prefetch before each turn | Not automatic. When a conversation touches a topic the user keeps in the vault, run the search step first and quote what you found, capped at roughly 5 entries or 2000 characters. |

## Setup
1. `mkdir -p ~/hermes-memory-vault && git -C ~/hermes-memory-vault init` (or point at an existing Obsidian vault).
2. Install ripgrep (`rg`) for fast search; grep works as fallback.
3. No API keys or env vars.

## Limits
- No automatic mirror of other memory writes and no automatic prefetch injection; these are Hermes MemoryProvider hooks.
- The plugin's `sync.py` (push/conflict handling described in `SYNC.md`) was not ported; commits are local only unless the user adds a remote.
- Keyword search only (ripgrep), no semantic ranking, matching the original.
- Claude Code's own memory (CLAUDE.md, auto memory) is a separate mechanism; this skill does not change it.

## Source
- Catalog entry (reviewed commit): https://github.com/Devs-Foundation/mnemosyne/tree/ad7ece790122d29d478ca71edfab5eb05e54f2db
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/mnemosyne.yaml
