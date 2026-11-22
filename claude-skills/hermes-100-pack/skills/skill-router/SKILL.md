---
name: skill-router
description: Reference card for the Hermes "skill-router" plugin, which hooked pre_llm_call to inject a relevance-filtered list of matching skills into the first turn of a session and learned keyword-to-skill associations from tool usage. Consult it only when a user asks what this plugin did or how Claude decides which skills to load; it performs no routing itself and should not trigger on real tasks.
---
# Skill Router (reference card)

**Hermes original:** https://github.com/xXLODXx/hermes-skill-router @ 445c32f · tier: community · category: general · license: MIT
**Port class:** D · built entirely on Hermes runtime hooks (`pre_llm_call`, `pre_tool_call`, `post_tool_call`, `post_llm_call`) and the Hermes skill index; Claude exposes no hook that rewrites the prompt before each model call from a skill.

## What the Hermes plugin does
Registers four hooks and no tools. On `pre_llm_call` it scores the user message against an optional routing-matrix markdown file (`SKILL_ROUTER_MATRIX_PATH`) and the tags, name, category and description of every installed skill under `HERMES_HOME`, then injects a compact "Skill Routing" block (at most three candidates, 70 to 200 tokens) telling the model which skills to `skill_view`. A per-session match signature suppresses repeats until the topic changes. `pre_tool_call` learns keyword-to-tool associations weighted by lift and stores them locally in `learned_keywords.json` and `tool_stats.json`; `post_tool_call` and `post_llm_call` add opt-in output learning. It writes anonymized JSONL diagnostics to `data/v2_injections.jsonl` and ships a dashboard tab ("Mission Control"). No network calls, no telemetry.

## Equivalent in Claude
None needed as a separate mechanism. Claude Code already places every available skill's name and description in the system prompt and loads a skill through the Skill tool when the description matches the task, which is the gap this plugin filled for Hermes. The learning store, routing matrix and injection budget have no Claude counterpart; writing pushy, keyword-rich skill descriptions is the equivalent lever.

## Setup
None.

## Limits
- No live rescoring per turn, no usage learning, no diagnostics or dashboard.
- The routing-matrix file format (numbered topics with Keywords and Required/Optional tables) is not consumed by Claude.
- Hermes-specific concepts (`skill_view`, `always_load`, `HERMES_HOME/skills`) do not map.

## Source
- Catalog entry (reviewed commit): https://github.com/xXLODXx/hermes-skill-router/tree/445c32f9b274f53bf3d37ce1b37ec1b3e5530ac4
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/skill-router.yaml
