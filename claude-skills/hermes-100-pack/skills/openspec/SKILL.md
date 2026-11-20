---
name: openspec
description: Run spec-driven development with the OpenSpec CLI (@fission-ai/openspec) from Claude Code: capture ideas, create and promote changes, write proposal, design, spec and task artifacts, track task status, validate, diff delta specs against main specs, and archive, all inside the repo's openspec/ directory. Use when the user mentions OpenSpec, "/opsx", "propose a change", "create a change for <feature>", "apply the change tasks", "verify the change", "archive the change", "sync specs", "show me the spec diff", or wants a structured proposal, design, specs, tasks workflow before coding.
---
# OpenSpec Spec-Driven Development

**Hermes original:** https://github.com/FelineStateMachine/hermes-openspec @ 493b42c · tier: community · category: desktop · license: MIT
**Port class:** B — the tools shell out to the `openspec` CLI or edit files under `openspec/`, both of which Claude can do directly; the 11 bundled upstream skills are copied.

## What the Hermes plugin does
Registers 21 tools in toolset `openspec`: CLI-backed `openspec_list`, `openspec_show`, `openspec_validate`, `openspec_status`, `openspec_instructions`, `openspec_cli` (gated on the binary, found via `OPENSPEC_BIN` or PATH; per `tools.py` they run `openspec list --json`, `openspec show <name> --json --no-interactive`, `openspec validate --json --no-interactive`, `openspec status --change <c> --json`, `openspec instructions --json`, `openspec templates --json`), and filesystem-backed `openspec_context`, `openspec_idea_create|enrich|promote`, `openspec_change_create|promote|archive|unarchive|sequence_set`, `openspec_task_list|set_status`, `openspec_spec_create|show|list|diff` (diff uses `git show HEAD:openspec/specs/<path>/spec.md`). It also ships a dashboard tab and Desktop plugin (Kanban board, spec browser, SQLite source registry at `<hermes_home>/openspec.db`) and bundles 11 upstream OpenSpec workflow skills.

## Equivalent in Claude
1. Check the CLI: `openspec --version`. If missing, install per README (verified with `npm view @fission-ai/openspec name version description`: `name = '@fission-ai/openspec'`, `version = '2.1.1'`, "AI-native system for spec-driven development", license MIT): `npm install -g @fission-ai/openspec@latest`. Honor `OPENSPEC_BIN` if the user set it.
2. Pick the matching upstream skill in `references/` by intent and follow it; they already instruct the agent to run the CLI directly:
   - new feature or fix: `upstream-openspec-new-change.md`, then `upstream-openspec-continue-change.md` or `upstream-openspec-ff-change.md` (all artifacts at once); one-shot full proposal: `upstream-openspec-propose.md`
   - think first: `upstream-openspec-explore.md`; first time in a repo: `upstream-openspec-onboard.md`
   - implement tasks: `upstream-openspec-apply-change.md`; check: `upstream-openspec-verify-change.md`
   - finish: `upstream-openspec-archive-change.md`, `upstream-openspec-bulk-archive-change.md`, `upstream-openspec-sync-specs.md`
3. Core CLI calls used by those skills: `openspec list --json`, `openspec status --change <name> --json`, `openspec instructions <proposal|design|specs|tasks|apply> --change <name>`, `openspec new change <name>`, `openspec archive <name>`, `openspec schemas --json`.
4. Filesystem conventions (per `docs/lifecycle.md`): ideas in `openspec/ideas/<slug>.md`; active changes in `openspec/changes/<change>/` with `proposal.md`, `design.md`, `tasks.md`, `specs/<spec>/spec.md`, `.openspec.yaml`; archived in `openspec/changes/archive/<change>/`; main specs in `openspec/specs/<spec>/spec.md`. State is derived from `tasks.md` checkboxes: Draft, Todo, In progress, Done, Archived.

| Hermes tool | How Claude does it |
|---|---|
| `openspec_list` / `_show` / `_validate` / `_status` / `_instructions` / `_cli` | Run the CLI commands above with Bash |
| `openspec_idea_create|enrich|promote` | Write `openspec/ideas/<slug>.md`; promote by `openspec new change <slug>` |
| `openspec_change_create|promote|archive|unarchive` | `openspec new change`, edit `tasks.md`, `openspec archive`, or move the folder back from `archive/` |
| `openspec_task_list` / `_set_status` | Read and toggle `- [ ]` / `- [x]` lines in `tasks.md` |
| `openspec_spec_diff` | `git show HEAD:openspec/specs/<spec>/spec.md` vs the change's delta spec |
| `openspec_context` | Resolve a change, spec or idea name by listing those folders |

## Setup
1. Node.js, then `npm install -g @fission-ai/openspec@latest`; or set `OPENSPEC_BIN=/path/to/openspec`.
2. In the repo, `openspec init` if `openspec/` does not exist (the upstream onboarding skill covers this).

## Limits
- Dashboard tab, Kanban board, spec browser, deep links and the source registry (`openspec.db`) are Hermes UI and are not replicated.
- The Desktop plugin's read-only project surface is not replicated.
- CLI flags are quoted from the plugin and skill text at the reviewed commit; check `openspec --help` on the installed version before relying on them.
- Upstream skills reference the `/opsx:*` slash commands of other agents; in Claude just follow the skill text.

## Source
- Catalog entry (reviewed commit): https://github.com/FelineStateMachine/hermes-openspec/tree/493b42cd95d2a30f967ede5a53eb22d1bd248fb9
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/openspec.yaml
