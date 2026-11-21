---
name: intelligent_memory
description: Local-first Arabic/English fact memory kept in a SQLite database with lifecycle states, ported from the Hermes intelligent_memory provider. Use it when the user wants Claude to keep or search durable bilingual facts on disk, says "remember this in my local memory", "search my memory for ...", "export my memories to markdown or JSON-LD", "import these facts", or asks to run the intelligent-memory CLI on an existing ~/.hermes/intelligent_memory/memory.db. The automatic per-turn recall and session-end extraction hooks are Hermes-only and are not reproduced.
---
# Intelligent Memory

**Hermes original:** https://github.com/hoysama/hermes-intelligent-memory @ 2d15ce5 (subdir `plugin/intelligent_memory`) · tier: community · category: memory · license: no LICENSE file found (README badge says MIT, no LICENSE file in the checkout)
**Port class:** C · the SQLite store and its standard-library CLI run without Hermes, but the memory-provider hooks, per-turn recall injection and cloud extraction through Hermes' configured model provider cannot be reproduced.

## What the Hermes plugin does
A `kind: exclusive` MemoryProvider. It stores canonical facts in SQLite (WAL mode, FTS5 and character-trigram indexes) under `$HERMES_HOME/intelligent_memory/memory.db`, with provenance, confidence, importance and lifecycle states (`active`, `superseded`, `archived`, `rejected`), Arabic/English normalization, bounded per-turn recall (defaults `max_recall_facts: 6`, `max_recall_chars: 1800`), staleness auto-archiving, epoch compression, and projection of high-importance facts into `MEMORY.md` and `USER.md`. It registers the hooks `on_session_end`, `on_pre_compress`, `on_memory_write`, `on_delegation` and six provider tools: `intelligent_memory_remember`, `intelligent_memory_recall`, `intelligent_memory_revise`, `intelligent_memory_forget`, `intelligent_memory_status`, `intelligent_memory_feedback`. Optional `cloud_mode` (`off`, `selective`, `session`) sends conversation text to Hermes' configured provider for fact extraction. The package has no third-party dependencies.

## Equivalent in Claude
The reproducible part is the standalone CLI documented in the README and defined in `plugin/intelligent_memory/cli.py`. Run it from Claude Code with the repository's `plugin/` directory as the working directory (the package is `intelligent_memory`, standard library only):

| Hermes tool / feature | How Claude does it |
|---|---|
| `intelligent_memory_recall` | `python -m intelligent_memory.cli search "query" [--target memory|user] [--limit 8] [--hermes-home PATH]` |
| `intelligent_memory_status` | `python -m intelligent_memory.cli status [--hermes-home PATH]` |
| export for review | `python -m intelligent_memory.cli export --format json|json-ld|markdown [--status active|archived|superseded|all] [--output FILE]` |
| bulk `remember` | `python -m intelligent_memory.cli import FILE [--format auto|json|markdown]` |
| projections to MEMORY.md / USER.md | `python -m intelligent_memory.cli project` |
| migrate legacy Hermes markdown memory | `python -m intelligent_memory.cli migrate [--dry-run]`, `rollback --backup PATH` |
| single `remember` / `revise` / `forget` / `feedback` | no CLI subcommand per the source; write a fact to a markdown or JSON file and `import` it, or edit through the `MemoryStore` class in `core/store.py` |
| per-turn recall, session-end extraction, `on_delegation` | not reproducible; Claude's own memory feature covers persistent user context instead |

`--hermes-home` defaults to the Hermes home; pass it explicitly (for example a project directory) to keep a Claude-specific database. Treat exported markdown as data for Claude to read at the start of a session when the user wants recall.

## Setup
1. Clone https://github.com/hoysama/hermes-intelligent-memory at commit 2d15ce5 into a directory of your choice.
2. Use Python 3.11 or newer (per `pyproject.toml`); no packages to install for the CLI.
3. Run CLI commands with the clone's `plugin/` directory as the working directory, or add it to `PYTHONPATH`.
4. Optional: `python doctor.py --fix` from the repository root rebuilds indexes and projections (per the README).

## Limits
- No automatic recall or write: Hermes called the provider on every turn and at compaction; Claude only runs the CLI when asked.
- Cloud enrichment (`cloud_mode`) relies on Hermes' auxiliary model client and is not available.
- No `remember` subcommand exists in the CLI as reviewed; adding facts one at a time means writing an import file first.
- `pip index versions hermes-intelligent-memory` found no PyPI distribution; install is from source only.
- No LICENSE file in the checkout, so no upstream text is copied; the CLI was read, not executed, and its behavior is stated per the plugin source.

## Source
- Catalog entry (reviewed commit): https://github.com/hoysama/hermes-intelligent-memory/tree/2d15ce5ba5878ddd7e18ca8cb1f0c62311965da0/plugin/intelligent_memory
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/intelligent_memory.yaml
