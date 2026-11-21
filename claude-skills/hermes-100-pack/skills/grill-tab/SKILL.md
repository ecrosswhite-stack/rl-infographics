---
name: grill-tab
description: Interrogate a rough task draft before executing it. Ask the single highest-leverage decision at a time (goal, deliverable, scope, verification, architecture), each with a recommended answer and 2 to 4 short options, then synthesize the settled answers into a faithful execution brief for the user to review before any work starts. Use this when the user says "grill me on this", "grill this draft", "ask me the decisions first", "help me pin this down before you start", "turn this into a brief", "preflight this task", or hands over a vague multi-step request (research, writing, planning, ops, design, data or code) where a wrong assumption would waste the run. Never start the work itself until the user approves the brief.
---
# Grill Tab (draft interrogation and execution brief)

**Hermes original:** https://github.com/thanhan-a17/grill-tab @ 2630fe2 · tier: community · category: (none in catalog) · license: MIT
**Port class:** C · the interrogation and brief-synthesis prompts are reproducible as conversational behavior; the Hermes Desktop Tab-key composer integration and the auxiliary-model routing are not.

## What the Hermes plugin does
A Hermes Desktop plugin (`kind: standalone`, no tools, no hooks). Pressing Tab in the Desktop composer sends the draft to a dashboard API (`/api/plugins/grill-tab/{interrogate,brief,health}`) backed by `dashboard/grill_engine.py`, which calls a fast auxiliary model (task `grill_tab`) to ask one decision question per rung. Enter synthesizes the settled ladder into a markdown execution brief that is placed back in the composer; nothing is auto-sent. It never asks facts the agent could look up, skips questions where every answer leads to the same plan, and treats "you decide" as accepting the recommendation.

## Equivalent in Claude
Run the same two-phase protocol in chat, following the rules copied from `_INTERROGATE_SYSTEM` and `_BRIEF_SYSTEM` in `grill_engine.py`.

Phase 1, interrogate (repeat until nothing critical is left or the user says "write the brief"):
1. Model the draft as a decision tree. Ask exactly one decision whose prerequisites are already known. Do not assume software; the draft may be research, writing, planning, ops, design or code.
2. Each question is 18 words or fewer, in the user's language, with a short recommended answer and, where natural, 2 to 4 short options.
3. Ask decisions only, never facts that can be inspected or looked up. Skip a question if every plausible answer leads to the same work.
4. Pick the highest-leverage unanswered category in this order: goal, deliverable, scope, verification. Use architecture only for clearly code-oriented intents. Do not repeat a category unless the user opened a new branch.
5. If the user answers with hesitation, a question, "you decide", "your call", "whatever you recommend" or "simplest", treat the recommendation as settled and move on; do not re-ask.
6. Greetings, thanks and tiny underspecified intents: stop immediately with a one-line reason instead of manufacturing questions.
7. Never ask generic checklist questions (tone, length, language, tests, error handling) unless the answer changes the plan.

Phase 2, brief: return markdown only, using these exact headings and only those with content: `## Goal`, `## Success criteria`, `## Deliverable`, `## Scope & non-goals`, `## Settled decisions`, `## Constraints`, `## Verify before reporting done`, `## Assumptions to make explicitly (do not ask)`, `## Directive`.
- Fidelity first: restate the user's intent at their stated ambition; do not enlarge it, add deliverables, steps, audiences or polish, or change medium, tone, length or language.
- "Settled" means stated in the draft, answered, or a recommendation the user accepted (including by deferring). Every line under Settled decisions traces to one of those and is written as a directive.
- Unsettled needs go under Assumptions, choosing the smallest, least surprising option. Never invent facts, numbers, names or constraints. An unnamed target (repo, folder, account) is an Assumption, not a guess from memory.
- Constraints holds only limits the user stated. Success criteria must be observable by the user. Verify steps must be checkable before reporting.
- Body in the user's language, headings in English, 150 to 250 words typical, never drop a settled decision.
- Directive must say: "Work autonomously. Do not re-ask anything above. Ask only if blocked by something outside this brief."

Present the brief and wait for approval before starting the work.

| Hermes piece | How Claude does it |
|---|---|
| Tab in Desktop composer calls `/interrogate` | Claude asks the next rung as a chat message |
| Enter calls `/brief`, fills composer | Claude posts the brief and waits for "go" |
| `auxiliary.grill_tab` side model | Claude itself; no separate model |
| Deterministic local fallback brief | Not needed; Claude always writes the brief |

## Setup
None.

## Limits
- No keyboard integration: the user triggers the protocol by asking for it, not by pressing Tab.
- No fast cheap auxiliary model; each rung costs a normal Claude turn.
- Clicking a settled rung to edit it in place, Esc to restore the draft and the palette command (Cmd+Shift+G) are Desktop UI features with no equivalent.
- The plugin read bounded Hermes memories for phrasing context; Claude uses only the current conversation.

## Source
- Catalog entry (reviewed commit): https://github.com/thanhan-a17/grill-tab/tree/2630fe2c8f1eb4c2c3106e2ed21ef519852cc1a5
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/grill-tab.yaml
