---
name: lancedb
description: Local vector plus full-text memory store built on an embedded LanceDB table with OpenAI-compatible embeddings, ported from the Hermes lancedb memory provider. Use it when the user wants a persistent, searchable fact store on disk for Claude Code work: "remember this fact in LanceDB", "recall what we know about X", "search my memories semantically", "forget that memory", "set up a local vector memory with OpenAI embeddings", or when working with an existing ~/.hermes/lancedb/memories.lance dataset. Automatic fact extraction at session end and context compression is Hermes-only and is not reproduced.
---
# LanceDB Memory

**Hermes original:** https://github.com/lancedb/hermes-agent-memory @ 6691591 · tier: community · category: memory · license: Apache-2.0
**Port class:** C - the store (LanceDB table, OpenAI-compatible embeddings, vector/hybrid search, preview-then-delete forget) can be driven from Python in Claude Code; the MemoryProvider hooks, auxiliary-LLM extraction and system-prompt injection depend on the Hermes runtime.

## What the Hermes plugin does
A MemoryProvider that keeps a single LanceDB table `memories` at `~/.hermes/lancedb/memories.lance` with rows of kind `fact` or `turn` (columns include `id`, `kind`, `content`, `vector`, `abstract`, `category`, `tags`, `provenance_turn_ids`, `content_hash`, plus an `agent_workspace` tag used as a prefilter). It registers four tools: `lancedb_recall` (vector by default, `hybrid` vector plus BM25 fused by RRF, linear or a cross-encoder), `lancedb_remember` (store a durable fact in categories `preference`, `entity`, `event`, `case`, `pattern`, `general`, deduplicated by content hash), `lancedb_read` (fetch one memory by id with provenance turns) and `lancedb_forget` (`action: preview` then `action: delete` by exact id). Hooks `on_pre_compress`, `on_session_end`, `on_memory_write`, `on_session_switch` extract facts with Hermes' auxiliary LLM client and run background `table.optimize()` compaction. Embeddings default to OpenAI `text-embedding-3-small` (1536 dimensions) through any OpenAI-compatible endpoint.

## Equivalent in Claude
Reproduce the store with the same packages in a small Python script kept outside any untrusted directory. Configuration keys and defaults mirror `src/default_config.yaml`.

| Hermes tool | How Claude does it |
|---|---|
| `lancedb_remember` | embed `content` with the embeddings API, compute a content hash of the normalized text, skip if a row with that hash exists, `table.add([...])` with `kind="fact"`, `category`, `tags` |
| `lancedb_recall` | embed the query; `table.search(vec).where(filter).limit(top_k)`; for hybrid add a full-text index on `content` and fuse with the LanceDB hybrid query API (RRF default) |
| `lancedb_read` | `table.search().where(f"id = '{id}'")` and return the row with its `provenance_turn_ids` |
| `lancedb_forget` | first list candidates by a recall on the description (preview), then `table.delete(f"id = '{id}'")` only after the user confirms the exact id |
| extraction at compaction / session end | not reproduced; add facts explicitly when the user asks |
| auto-compaction | run `table.optimize()` occasionally (plugin default: every 50 commits, cleanup older than 7 days) |

Embedding client: `openai.OpenAI(base_url=<embedding.base_url or None>, api_key=os.environ[<embedding.api_key_env>])`, model `text-embedding-3-small`, batches of at most 100 inputs. Changing the model or dimension against an existing table requires recreating it; the plugin fails loudly on a dimension mismatch. Keep `top_k` at or under 50 (hard cap in the plugin). Prefer `vector` mode; the plugin's LongMemEval benchmark found it outperformed RRF hybrid.

## Setup
1. `pip install lancedb openai pyyaml` (verified with `pip index versions`: lancedb 0.41.0 available, plugin requires `>=0.33`; openai 3.57.0 available, plugin requires `>=2.38`).
2. Export the embedding key named by `api_key_env`: default `OPENAI_API_KEY`. Alternatives from the plugin config: `OPENROUTER_API_KEY` with `base_url: https://openrouter.ai/api/v1` and model `google/gemini-embedding-001`, or `OLLAMA_API_KEY` (any value) with `base_url: http://localhost:11434/v1` and model `nomic-embed-text`.
3. Choose a dataset directory, for example `~/.hermes/lancedb` to share with an existing Hermes store, and `lancedb.connect(path).open_table("memories")` or create it with the schema above.
4. Optional cross-encoder reranking needs `sentence-transformers` (pulls in torch, about 2 GB) and model `cross-encoder/ettin-reranker-17m-v1`; the default path needs no local ML stack.

## Limits
- No automatic memory: Hermes extracted facts from conversations at compaction and session end using an auxiliary model; Claude only stores what it is asked to store.
- No system-prompt block or per-turn prefetch; recall happens when Claude runs the query.
- Embedding calls send memory text to the configured embeddings provider (OpenAI by default) and cost money per token.
- Workspace isolation (`agent_workspace`) and `on_session_switch` behavior are Hermes concepts; use a fixed tag per project instead.
- No MCP server for this store was verified, so none is listed.
- The plugin ships no `skills/` directory; nothing to copy. Store logic above is stated per `src/store.py`, `src/retrieval.py` and `src/tools.py`, not executed.

## Source
- Catalog entry (reviewed commit): https://github.com/lancedb/hermes-agent-memory/tree/6691591e62e10438ee32ff671afad337208fdd43
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/lancedb.yaml
