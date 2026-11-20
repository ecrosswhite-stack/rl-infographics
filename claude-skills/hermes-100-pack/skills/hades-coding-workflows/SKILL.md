---
name: hades-coding-workflows
description: Three coding workflow patterns ported from the Hermes "hades-coding-workflows" plugin: write implementation plans with bite-sized 2 to 5 minute tasks, exact file paths, complete code and verification commands; execute a plan by dispatching one fresh subagent per task with a two-stage review (spec compliance, then code quality); and a design, implement, verify harness that only delegates genuinely parallel sub-tasks. Use when the user says "write an implementation plan", "break this feature into tasks", "execute this plan with subagents", "subagent-driven development", "use the dual-model harness", "plan then implement", or asks for a structured multi-step coding workflow in Claude Code.
---
# Hades Coding Workflows

**Hermes original:** https://github.com/singhguri/hades-coding-workflows @ b68546d · tier: community · category: automation · license: MIT
**Port class:** A — a skills-only package (three SKILL.md files, no tools, hooks or MCP server); the content ports directly, with Hermes `delegate_task` mapped to Claude Code subagents.

## What the Hermes plugin does
`__init__.py` registers every `skills/*/SKILL.md` via `ctx.register_skill`, exposing `hades-coding-workflows:dual-model-harness`, `:subagent-driven-development` and `:writing-plans`. No tools, hooks or env vars. The skills are adapted from obra/superpowers and the GSD project (both MIT) and encode: plans with 2 to 5 minute tasks, TDD and frequent commits; fresh subagent per task with spec review then quality review; and a harness that keeps serial multi-file work in the main agent because delegation overhead outweighs the benefit.

## Equivalent in Claude
Read the copied upstream text in `references/` and follow it with these substitutions:

| Hermes concept | Claude Code equivalent |
|---|---|
| `delegate_task(goal=, context=, toolsets=)` | Launch a subagent with the Agent tool; put the full task text, project context, TDD steps and commit instruction in the prompt |
| `skill_view("hades-coding-workflows:<name>")` | Read `references/upstream-<name>.md` in this skill |
| `todo([...])` | Claude Code's task list / TodoWrite |
| `read_file`, `write_file`, `terminal` | Read, Write/Edit, Bash |
| "DeepSeek V4 Flash / Pro", "GLM 5.2" model roles | Ignore the model names; Claude is the main agent and subagents run Claude. The structural lesson (do serial multi-file work in-session, delegate only isolated parallel tasks) still applies |
| `npx tsc --noEmit --pretty` verification gate | Same command for TypeScript projects; use the project's own typecheck or test command otherwise |

Procedure:
1. Planning request: follow `references/upstream-writing-plans.md`. Save the plan under `docs/plans/<date>-<feature>.md` with the required header, one task per 2 to 5 minutes, exact paths, complete code, test command and expected output. No TBD or placeholders.
2. Execution request: follow `references/upstream-subagent-driven-development.md`. Read the plan once, extract all tasks, then per task: dispatch an implementer subagent with complete context, run a spec-compliance review subagent, then a code-quality review subagent, fix findings before the next task.
3. General multi-step coding task: follow `references/upstream-dual-model-harness.md`: clarify, batch-read 4 to 6 existing files for patterns, design and get approval, implement (new files in one batch, patch existing files one at a time), verify with real tool output before claiming done.

## Setup
None.

## Limits
- The `delegation:` YAML config block and provider quirk notes (`references/glm-provider-quirks.md` upstream) are Hermes model-routing settings and are not copied; Claude Code does not route subagents to other vendors' models this way.
- `context-budget-discipline.md`, `gates-taxonomy.md` and `server-action-result-pattern.md` upstream reference files are not copied here; read them in the source repo if needed.
- The skills assume git, pytest or tsc are available in the project; verify before quoting their commands.

## Source
- Catalog entry (reviewed commit): https://github.com/singhguri/hades-coding-workflows/tree/b68546d66fe684a49633a9174e44362eff77cbfc
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hades-coding-workflows.yaml
