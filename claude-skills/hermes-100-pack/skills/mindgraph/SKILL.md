---
name: mindgraph
description: Semantic graph memory in the MindGraph cloud (goals, decisions, claims, entities, cross-document synthesis) through the mindgraph-sdk Python package, ported from the Hermes mindgraph memory provider. Use it when the user has a MINDGRAPH_API_KEY and asks to "store this in MindGraph", "retrieve from my knowledge graph", "what are my open decisions or goals", "ingest this article into MindGraph", "synthesize what the graph knows about project X", or wants Claude Code scripts against api.mindgraph.cloud. Per-turn prefetch, system-prompt injection and session-end transcript ingestion are Hermes-only.
---
# MindGraph Memory

**Hermes original:** https://github.com/shuruheel/mindgraph @ b96c259 · tier: community · category: memory · license: MIT
**Port class:** C · the five graph tools wrap the public `mindgraph-sdk` client, which Claude Code can call directly; the session lifecycle, prefetch thread and behavioral contract injected into the system prompt depend on the Hermes MemoryProvider interface.

## What the Hermes plugin does
Registers `MindGraphMemoryProvider`. On each conversation it opens a MindGraph `Session` node (`hermes-<session_id[:8]>`), bakes active goals, policies, open questions, open decisions and weak claims into the system prompt, prefetches hybrid full-text plus semantic context for the next turn in a background thread, and on session end ingests the transcript for five-layer extraction (Reality, Epistemic, Intent, Action, Agent). It exposes five tools: `mindgraph_remember` (entities, observations, claims, preferences, notes), `mindgraph_retrieve` (hybrid search, structured queries, traversal), `mindgraph_commit` (goals, decisions, plans, tasks, risks, questions), `mindgraph_ingest` (bulk articles, transcripts, code) and `mindgraph_synthesize` (project-scoped synthesis producing Article nodes). It declares `pip_dependencies: mindgraph-sdk>=0.4.0` and `requires_env: MINDGRAPH_API_KEY`.

## Equivalent in Claude
Call the SDK from a Python script in Claude Code. Client construction per `tools.py`:

```python
import os
from mindgraph import MindGraph
client = MindGraph("https://api.mindgraph.cloud", api_key=os.environ["MINDGRAPH_API_KEY"])
```

SDK methods the plugin uses (names from `tools.py`; consult the SDK's own documentation for signatures): `search`, `retrieve`, `retrieve_context`, `get_nodes`, `neighborhood`, `update_node`, `get_goals`, `get_open_questions`, `get_open_decisions`, `get_weak_claims`, `get_contradictions`, `ingest_session`, `distill`, `session`.

| Hermes tool | How Claude does it |
|---|---|
| `mindgraph_remember` | create or update nodes with `client.update_node` / the SDK's node creation calls, stamping `MINDGRAPH_AGENT_ID` as provenance |
| `mindgraph_retrieve` | `client.search(...)` for full-text, `client.retrieve(...)` / `client.retrieve_context(...)` for hybrid, `client.neighborhood(...)` for traversal |
| `mindgraph_commit` | goal, decision, plan, task, risk and question nodes via the same node calls; read back with `get_goals`, `get_open_decisions`, `get_open_questions` |
| `mindgraph_ingest` | `client.ingest_session(...)` with the document or transcript text |
| `mindgraph_synthesize` | `client.distill(...)` scoped to a project |
| system-prompt block, prefetch, session open/close | not reproduced; run `get_goals` and `get_open_decisions` at the start of a working session when the user asks for context |

The exact action tables and parameter names live in `tools.py` in the checkout; read them before writing a script rather than guessing.

## Setup
1. Create an account and API key at https://mindgraph.cloud.
2. Export `MINDGRAPH_API_KEY`. Optional per `plugin.yaml` comments: `MINDGRAPH_BASE_URL` (default `https://api.mindgraph.cloud`; note that `tools.py` as reviewed hardcodes that URL in `_get_client`) and `MINDGRAPH_AGENT_ID` (provenance tag, default `hermes`).
3. `pip install "mindgraph-sdk>=0.4.0"` (verified with `pip index versions mindgraph-sdk`: latest 0.18.0; import name `mindgraph`).

## Limits
- All memory content, including ingested transcripts and documents, is sent to the MindGraph cloud service (third party, paid account).
- No automatic session ingestion or per-turn context; Claude calls the graph only when asked.
- The behavioral contract (when to route knowledge into which layer, anti-patterns) lives in `provider.py` and is not injected into Claude's prompt; read it there if you want to follow the same conventions.
- SDK method signatures and the `_request` fallback used by the plugin were not verified against the current SDK (0.18.0) and may differ from the `>=0.4.0` version the plugin targeted.
- No MCP server for MindGraph was verified; none is listed. The plugin ships no `skills/` directory.

## Source
- Catalog entry (reviewed commit): https://github.com/shuruheel/mindgraph/tree/b96c2590435bb625210506a47df682967215b6d7
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/mindgraph.yaml
