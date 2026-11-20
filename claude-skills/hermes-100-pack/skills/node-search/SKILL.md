---
name: node-search
description: "Decide which Markdown or Obsidian notes to read next by scanning only their metadata and link graph, as the Hermes node_search tool did: YAML frontmatter, headings, tags, [[wikilinks]], backlinks, orphan notes, unresolved or ambiguous links, and small neighborhood expansion, inside configured allowed roots, returning compact candidates instead of file bodies. Use it when a user asks \"which notes mention project X\", \"find orphan notes in my vault\", \"dangling wikilinks\", \"notes tagged status:open\", \"what links to this note\", \"give me the link neighborhood of X\", or any triage over an Obsidian vault or Markdown wiki before reading files."
---
# Node Search for Markdown vaults

**Hermes original:** https://github.com/Heeervas/node-search-plugin @ 3a1ad9d · tier: community · category: tools · license: MIT
**Port class:** B · a local Python indexer over `.md` files with no external service; Claude Code can reproduce the same scan with ripgrep and a short Python script using PyYAML.

## What the Hermes plugin does
Per the README and plugin.yaml, it registers one tool, `node_search`, a bounded first-pass candidate selector for Markdown roots. It indexes `.md` files only: YAML frontmatter, headings, Obsidian wikilinks, outgoing links, backlinks, malformed YAML, unresolved links, orphan or no-backlink notes, and ambiguous basename resolution. Modes: `auto`, `topic_context`, `graph_health`, `metadata`, `link_neighborhood`. Filters: `query` (optionally regex) over `path`, `basename`, `frontmatter`, `links`; `frontmatter`, `tags`, `has_links_to`, `linked_from`, `link_state` (`orphan`, `no_backlinks`, `unresolved`/`dangling`, `ambiguous`, `has_outgoing`, `has_incoming`), `path_filter`, `exclude_path_filter`, `depth`, `expand`, `limit`. Output is compact (`frontmatter_summary`, link counts, `why_read`) and capped (`max_chars_per_result` 2000, `max_total_chars` 12000). Roots come from `NODE_SEARCH_ALLOWED_ROOTS` (default `$HERMES_HOME/brain`), legacy `NODE_SEARCH_ROOT`, cache at `NODE_SEARCH_CACHE`. It never returns file bodies.

## Equivalent in Claude
1. Resolve the scope: a path inside one of the roots in `NODE_SEARCH_ALLOWED_ROOTS` (comma-separated) or `NODE_SEARCH_ROOT`; refuse paths or symlinks that escape the roots, as the plugin does.
2. Build the index with a Python script run with `python3 -I` from outside the vault: for every `*.md` under scope, parse frontmatter between the leading `---` lines with `yaml.safe_load` (record `malformed_yaml` on failure), collect `#` headings, and extract `[[target|alias#heading]]` wikilinks. Resolve each target by basename against all indexed notes: zero matches = unresolved, more than one = ambiguous. Backlinks are the inverse map. Cache the index as JSON under `NODE_SEARCH_CACHE` (default `$HERMES_HOME/.cache/hermes/node_search/index.json`) or a scratch file.
3. Apply the requested filter, then expand `depth` hops along incoming, outgoing or both links.
4. Return at most `limit` candidates with: path, title, matched fields, a frontmatter summary (default preset drops source/url-style fields; clip values to 240 chars), link counts (incoming, outgoing, resolved, unresolved, ambiguous), and a one-line `why_read`. Do not paste bodies; read chosen files afterwards with the Read tool.
5. Require `scope` plus at least one narrowing parameter; if the request is just "search my vault", ask for a query, tag, link state or path filter instead of dumping everything (plugin guardrail).

| Hermes argument | Claude shortcut |
|---|---|
| `query` over path/basename | `rg --files -g '*.md' <scope> \| rg -i '<query>'` |
| `query` over frontmatter | `rg -i -n -g '*.md' --max-count 3 '<query>' <scope>` limited to the frontmatter block in the script |
| `tags` | frontmatter `tags` list or inline `#tag` in the index |
| `link_state: unresolved` | targets with no basename match |
| `link_state: orphan` | notes with zero incoming and zero outgoing links |
| `has_links_to` / `linked_from` | outgoing / incoming maps |

## Setup
1. `export NODE_SEARCH_ALLOWED_ROOTS="$HOME/notes,$HOME/work/wiki"` (same variable name as the plugin).
2. `python3 -m pip install pyyaml` and install ripgrep.
3. No API keys.

## Limits
- Not a drop-in binary: the indexer is rewritten per request from the plugin's described behavior; scoring weights (`score` values in the README) are not reproduced exactly.
- Body text is intentionally not searched, matching v0.3.0; use `rg` directly for prose.
- The plugin's `benchmark_node_search.py` and test suite were not run.
- Large vaults: the plugin caps result count, graph depth, links per node and frontmatter size; keep the same caps to avoid flooding context.

## Source
- Catalog entry (reviewed commit): https://github.com/Heeervas/node-search-plugin/tree/3a1ad9df4ae367d27a1b9533fb271a968b6099be
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/node-search.yaml
