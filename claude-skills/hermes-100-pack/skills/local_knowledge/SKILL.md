---
name: local_knowledge
description: Route a question about local operational knowledge (custom skills and their support docs, helper scripts, runbooks, memory docs, cron jobs, MCP server configs) to the whole artifact to read first, before doing broad file search, replicating the Hermes local_knowledge router. Use it when the user asks "which skill or runbook covers X", "do I have a script for Y", "what cron job handles the backups", "where is the MCP wrapper for Z", "find the doc about our deployment", or whenever Claude is about to grep a large personal or homelab repository for how something is done. Claude searches the configured source tree with Glob/Grep, reads frontmatter and titles, ranks candidates, and reads the winner before acting.
---
# Local Knowledge Router

**Hermes original:** https://github.com/stepanov1975/hermes-local-knowledge @ c13a1a3 · tier: community · category: tools · license: MIT
**Port class:** C · the routing workflow (search, fetch, inspect, verify freshness) is reproducible with Claude's file tools; the SQLite index, hooks, telemetry, implicit feedback and model-backed tool-OKF generation are Hermes-internal.

## What the Hermes plugin does
Registers five tools in toolset `local_knowledge`: `knowledge_search` (find artifacts by intent, optional `artifact_type`, `rebuild`), `knowledge_get` (one artifact by ID, optional neighbors), `knowledge_neighbors` (graph edges), `knowledge_feedback` (`useful`, `missing`, `stale`, `wrong_artifact`), `knowledge_usage_report`. It registers hooks `pre_llm_call`, `post_tool_call`, `on_session_end`, `on_session_finalize` to inject a one-line prompt hint and learn implicit feedback. It indexes whole artifacts, not chunks: `SKILL.md` files, skill support docs, scripts, markdown runbooks/memory/docs under `source_root`, `$HERMES_HOME/cron/jobs.json`, `mcp_servers` in `$HERMES_HOME/config.yaml`, and generated `tool_okf` notes. Automatic OKF generation calls the active model and costs tokens (README disclosure). A standalone CLI `python -m hermes_local_knowledge.cli build|search|get|neighbors|evaluate|doctor` ships in the package.

## Equivalent in Claude
Treat the same locations as the index, and reproduce the bundled router skill's workflow (copied in `references/upstream-local-knowledge-router.md`).

1. Determine the source tree: `$LOCAL_KNOWLEDGE_ROOT`, else the configured `source_root`, else `$HERMES_HOME` (default `~/.hermes`). Skip the plugin's built-in excluded dirs: `.archive`, `.git`, `.mypy_cache`, `.pytest_cache`, `.venv`, `.worktrees`, `__pycache__`, `htmlcov`, `logs`, `node_modules`, `venv`, `worktrees`.
2. Enumerate artifacts by type with Glob:
   - skills: `**/SKILL.md` under `custom_skill_dirs` (default `custom_skills`) and `$HERMES_HOME/skills`; support docs: markdown under those skills' `references/`, `templates/`, `scripts/`, `assets/`.
   - scripts: files under `script_dirs` (default `scripts`, `hermes_home/scripts`).
   - runbooks / memory / docs: markdown under `runbook_dirs` (default `docs`) and `memory_dirs` (default `memory`).
   - cron jobs: `$HERMES_HOME/cron/jobs.json`; MCP servers: `mcp_servers` (or `mcp.servers`) in `$HERMES_HOME/config.yaml`.
3. Rank with Grep over frontmatter `name`/`description`, first heading, file path and body; prefer matches where a known entity (`Hermes`, `GitHub`, `MCP`, `Cron` by default) and an operation/topic word both appear in the ID, title or path. Return at most 8 candidates with type, path and one-line reason.
4. Read the winning artifact fully before acting (skill -> read SKILL.md; script -> read it and its help text; cron -> verify the live registry; MCP -> inspect the live config). Results are routing hints, not proof.
5. If results look weak, retry once with a shorter query and an explicit type; then fall back to broad search.
6. Feedback: if the user wants it, append a line to a local `knowledge-feedback.jsonl` the user owns (`{"query","artifact","rating","note"}`); the plugin's telemetry database is not replicated.

| Hermes tool | How Claude does it |
|---|---|
| `knowledge_search(query, artifact_type, limit, rebuild)` | steps 1-3 (rebuild = re-glob) |
| `knowledge_get(artifact_id, include_neighbors)` | read the file; list files in the same skill/dir as neighbors |
| `knowledge_neighbors(artifact_id)` | sibling files, scripts referenced by path in the artifact, cron jobs naming the script |
| `knowledge_feedback(...)` | step 6 |
| `knowledge_usage_report()` | summarize the local feedback file if present; otherwise say none |

The plugin's own CLI can also run outside Hermes per its README (`python -m hermes_local_knowledge.cli ... --from-hermes-config`) after installing the package from the repository; not verified here.

## Setup
None for the Claude workflow. Optional: set `LOCAL_KNOWLEDGE_ROOT` to the curated tree (same override the plugin honours) so Claude knows where to look.

## Limits
- No persistent index, graph edges or ranking model; each lookup re-scans, which is slower on large trees.
- `pre_llm_call` prompt hint, `post_tool_call` consumption tracking, implicit feedback learning and `on_session_*` hooks are not available.
- Tool-OKF generation (model calls in a background worker) is not replicated; nothing spends tokens in the background.
- `knowledge_usage_report` metrics (zero-result queries, failures) are not collected.
- Do not put secrets or private document text into feedback notes; the plugin's warning applies equally.

## Source
- Catalog entry (reviewed commit): https://github.com/stepanov1975/hermes-local-knowledge/tree/c13a1a357eb110fe62d6d4f8a715187079766541
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/local_knowledge.yaml
