---
name: icarus
description: Shared agent memory as markdown notes with YAML frontmatter in a FABRIC_DIR (optionally inside an Obsidian vault), plus export of those notes into fine-tuning pairs and Together AI fine-tune jobs, replicating the Hermes icarus plugin's fabric_* tools. Use when the user says "fabric note", "write this to my fabric/vault", "recall what we decided about", "pending handoffs", "what is assigned to me", "curate training value", "export training pairs", "start a Together fine-tune", "check the fine-tune job", or has FABRIC_DIR / TOGETHER_API_KEY set and wants cross-session notes or a replacement-model pipeline.
---
# Icarus: Fabric Memory and Replacement Models

**Hermes original:** https://github.com/esaradev/icarus-plugin @ e46cba3 · tier: community · category: memory · license: MIT
**Port class:** C · the note store (plain markdown files) and the Together AI calls are reproducible from the filesystem and curl; the automatic hooks and the model switch that rewrites Hermes's `.env` depend on the Hermes runtime.

## What the Hermes plugin does
Registers 16 tools in the `fabric` toolset: memory (`fabric_recall`, `fabric_write`, `fabric_search`, `fabric_pending`, `fabric_curate`), training (`fabric_export`, `fabric_train`, `fabric_train_status`), replacement models (`fabric_models`, `fabric_eval`, `fabric_switch_model`, `fabric_rollback_model`) and operations (`fabric_brief`, `fabric_telemetry`, `fabric_report`, `fabric_init_obsidian`); and 4 hooks (`on_session_start` loads SOUL and pending handoffs, `pre_llm_call` injects memories on topic change, `post_llm_call` captures decisions, `on_session_end` scores the session). Entries are `.md` files in `FABRIC_DIR` (default `~/fabric`). Training uploads JSONL to Together AI and starts a fine-tune; switching rewrites `LLM_MODEL`, `OPENAI_BASE_URL=https://api.together.xyz/v1` and `OPENAI_API_KEY` in `$HERMES_HOME/.env`.

## Equivalent in Claude
Env vars (same names as the plugin): `FABRIC_DIR` (required in practice), `HERMES_AGENT_NAME` (agent label, default `agent`), `ICARUS_OBSIDIAN=1` and `OBSIDIAN_VAULT_PATH` (optional wikilinks and `daily/` notes), `FABRIC_SESSION_ID`, `FABRIC_PROJECT_ID`, `TOGETHER_API_KEY`, `TOGETHER_MODEL` (default `Qwen/Qwen2-7B-Instruct`), `TOGETHER_SUFFIX`, `TOGETHER_BATCH_SIZE` (default 8, min 8), `TOGETHER_LR` (default 1e-5), `TOGETHER_CHECKPOINTS` (default 1).

| Hermes tool | How Claude does it |
|---|---|
| `fabric_write(type, content, summary, ...)` | Write `$FABRIC_DIR/<agent>-<type>-<slug40>-<4hex>.md` with the frontmatter below, then the content |
| `fabric_search(query)` | `grep -ril "<query>" "$FABRIC_DIR"/*.md`, show summary lines |
| `fabric_recall(query)` | grep candidates, rank by keyword overlap and recency, return top 5 with id, type, summary |
| `fabric_pending(customer_id?)` | list files with `status: open` and `assigned_to: <agent>`, plus `type: review` entries whose `review_of` points at this agent's ids |
| `fabric_curate(entry_id, training_value)` | edit the `training_value:` line in that file (high, normal, low) |
| `fabric_brief` / `fabric_report` | summarize pending items, entries from the last days, counts by type and training_value |
| `fabric_init_obsidian` | create `$OBSIDIAN_VAULT_PATH/.obsidian/app.json` (or `$FABRIC_DIR/.obsidian/`) and `$FABRIC_DIR/daily/` |
| `fabric_export(mode)` | build `{"messages":[system,user,assistant]}` JSONL from entries; `high-precision` keeps only high-value, verified, linked or completed-with-evidence entries, `normal` drops `training_value: low`, `high-volume` keeps all |
| `fabric_train` | `curl -X POST https://api.together.xyz/v1/files/upload -H "Authorization: Bearer $TOGETHER_API_KEY" -F purpose=fine-tune -F file=@training.jsonl`, then `POST https://api.together.xyz/v1/fine-tunes` JSON `{training_file, model, n_epochs, suffix, batch_size, learning_rate, n_checkpoints}`; record the job in `$FABRIC_DIR/.icarus/models.json` style registry |
| `fabric_train_status(job_id)` | `GET https://api.together.xyz/v1/fine-tunes/<job_id>`; on `completed` note `model_output_name` |
| `fabric_models` | print the local registry file |

Frontmatter written by `fabric_write` (state.py `write_entry`), required fields first:
```
---
id: <8 hex>            agent: <HERMES_AGENT_NAME>     platform: cli
timestamp: <UTC ISO>   type: <decision|review|code-session|...>   tier: hot
summary: <text>        project_id: <FABRIC_PROJECT_ID or cwd name>  session_id: <id>
# optional: tags: [a, b]  status: open  outcome:  review_of: agent:id  revises: agent:id
# customer_id:  assigned_to:  training_value: high|normal|low  verified:  evidence:  source_tool:  artifact_paths: [..]
---
<content>
```
Validation rules from tools.py: `status: open` requires `assigned_to`; `type: review` requires `review_of` in `agent:id` form pointing at an existing entry; `revises` likewise; `training_value` must be high, normal or low.

## Setup
1. `export FABRIC_DIR=~/Documents/my-vault/icarus` (create the directory). Optional: `HERMES_AGENT_NAME=coder`, `ICARUS_OBSIDIAN=1`, `OBSIDIAN_VAULT_PATH=~/Documents/my-vault`.
2. For training only: get a key at Together AI and `export TOGETHER_API_KEY=...`.

## Limits
- Not replicated: the four automatic hooks (SOUL loading, memory injection on topic change, decision capture, session scoring). Claude writes and reads notes only when asked or when this skill tells it to at a natural checkpoint.
- Not replicated: `fabric_switch_model`, `fabric_rollback_model` and `fabric_eval`. They rewrite `$HERMES_HOME/.env` to point Hermes at a Together-hosted model and compare candidate vs base model through the Hermes LLM path; Claude Code and Cowork run on Claude models and have no such switch.
- The ranked retriever (`fabric-retrieve.py`) and export filters (`export-training.py`) are approximated above; exact scoring was not reproduced.
- Training spends money at Together AI and uploads note contents to a third party; confirm with the user first.
- The `.icarus` registry location is a suggestion; the plugin's exact registry path lives under the Hermes home and was not reused.

## Source
- Catalog entry (reviewed commit): https://github.com/esaradev/icarus-plugin/tree/e46cba30fb95a0b54b7c4d6c26169a424283d72b
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/icarus.yaml
