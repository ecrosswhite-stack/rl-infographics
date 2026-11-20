---
name: recency-anchor
description: Restate a short standing instruction at the end of every user turn so it is the last thing the model reads, the trick the Hermes recency-anchor plugin performs with a pre_llm_call hook. Use when a user complains that Claude "keeps forgetting the persona/instruction after a few messages", "drifts from the system prompt", wants an instruction "repeated every turn", or asks for a recency anchor. In Claude Code this maps to a UserPromptSubmit hook; elsewhere it is a manual discipline.
---
# Recency Anchor

**Hermes original:** https://github.com/etkecc/hermes-recency-anchor @ 24d1906 · tier: community · category: general · license: LGPL-3.0 (catalog: other)
**Port class:** C · the effect (append a fixed block to every user turn) is reproducible with a Claude Code hook; the Hermes config block, channel filters and `/anchor` command are not.

## What the Hermes plugin does
One `pre_llm_call` hook and one `/anchor` command, no tools. Per the source, the hook reads `plugins.entries.recency-anchor.text` from `config.yaml` and returns `{"context": text}`, which Hermes appends to the API copy of the user message (the stored transcript and the cached system prefix stay unchanged). `channels` (allow-list) and `exclude_channels` (deny-list, wins) filter by the channel a turn arrived on. `/anchor` prints the resolved channel, whether the anchor fires, and which rule decided.

## Equivalent in Claude
Claude Code: use a `UserPromptSubmit` hook whose stdout is added as context on every prompt. Keep the text in a file so edits take effect on the next message, as in the plugin.
1. Write the anchor text to `~/.claude/recency-anchor.txt` (short; the README's rule: "write it like a telegram", it is re-sent every turn).
2. Add to `~/.claude/settings.json` (or the project `.claude/settings.json`):
   ```json
   {"hooks": {"UserPromptSubmit": [{"hooks": [{"type": "command", "command": "cat ~/.claude/recency-anchor.txt"}]}]}}
   ```
3. Check with `/hooks` in Claude Code that the hook is registered. Hook stdout for `UserPromptSubmit` is documented as context added to the turn; the exact JSON shape above should be checked against the current hooks reference, it was not executed in this port.
Claude.ai / Cowork (no hooks): the nearest option is to restate the instruction yourself at the end of each reply, or ask the user to add it to project instructions (which sits at "message zero", the position the plugin argues against).

| Hermes piece | Claude equivalent |
|---|---|
| `text:` in config.yaml | `~/.claude/recency-anchor.txt` |
| `pre_llm_call` returning `context` | `UserPromptSubmit` hook stdout |
| `channels` / `exclude_channels` | None; use per-project settings files instead |
| `/anchor` diagnostics | `/hooks` listing; run the command manually to see the text |

## Setup
1. Claude Code installed; create the text file and settings entry above.
2. Nothing else.

## Limits
- Applies only in Claude Code; the desktop app and Cowork have no per-turn hook.
- The plugin's guarantee that the anchor never enters the stored transcript does not carry over; hook context becomes part of the conversation.
- Token cost: the block is paid on every turn, as the README states.
- License is LGPL-3.0, so no upstream text is copied beyond short quotes.

## Source
- Catalog entry (reviewed commit): https://github.com/etkecc/hermes-recency-anchor/tree/24d1906a285fdfe37ecaf6253da8712db28f5a7b
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/recency-anchor.yaml
