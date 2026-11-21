---
name: jekyll-hyde
description: Periodic completion-gap self-audit modeled on the Hermes jekyll-hyde plugin. Use when a user asks Claude to "audit your own progress", "check whether you actually finished what I asked", "stop spreading work across turns", "give me the smallest verified next action", or wants a Jekyll-Hyde style evidence review every few turns of a long agentic session. The hook-driven, multi-clone auxiliary LLM machinery of the original is not reproducible; only the audit procedure is.
---
# Jekyll-Hyde (completion-gap audit)

**Hermes original:** https://github.com/jnorthrup/hermes-jekyl-hyde @ 10149e5 · tier: community · category: general · license: no LICENSE file found
**Port class:** C · the audit procedure can be followed as instructions; the core (three Hermes hooks, out-of-band `auxiliary_client.call_llm` clones, transcript tombstoning, `/hyde` command, persisted state) depends on the Hermes runtime.

## What the Hermes plugin does
Registers hooks `pre_llm_call`, `transform_llm_output`, `post_llm_call` and a `/hyde` slash command; no tools. Every N-th non-trivial user turn (default 7) it runs disposable audit roles out of band: an Auditor writes an evidence review (verified work, gap, status, smallest next action), an Advocate turns it into the smallest concrete continuation or names an external blocker, and an Arbiter labels the evidence `genuine`, `sandbagged` or `uncertain`. Depending on mode (`arena`, `silent`, `mandate`, `heuristic`, `old-testament`, `full`) it injects nothing, a directive, both plans, or replaces the transcript with a compression tombstone. State lives under `$HERMES_HOME/jekyll-hyde/`.

## Equivalent in Claude
Reproduce the audit as a self-check Claude performs in the main conversation (no second model, no hidden context):
1. Count non-trivial user turns (ignore greetings, acknowledgements, slash-like commands, messages under about 12 characters). Every `ratio` turns (default 7, or the number the user sets), run the audit before answering.
2. Evidence review: list (a) work verified by tool output (tests run, files written, commands executed), (b) the gap between what was requested and what exists, (c) status in one line, (d) the smallest next action that closes part of the gap.
3. Continuation: either perform that smallest action now with tools, or name the concrete external blocker (missing credential, decision needed from the user).
4. Verdict on your own evidence: `genuine` (artifacts and tool evidence match the claims), `sandbagged` (claims outrun evidence), or `uncertain` (not enough evidence). Insufficient evidence is `uncertain`, never an accusation.
5. Mode handling: in "mandate" style, show only the resulting technical directive; in "arena" style, show the review and the continuation; in "offer" style, present an audit-informed plan and a plain baseline plan and let the user choose.
Escalate language only when the previous assistant message itself combined placation, a promise, and a goal shift; otherwise stay neutral and evidence-first.

| Hermes piece | Claude equivalent |
|---|---|
| `pre_llm_call` gate + clones | Steps 1 to 4 done inline |
| `mandate` extractor | Step 5, directive only |
| `/hyde status`, `/hyde ratio N`, `/hyde mode` | Keep the counter and mode in the conversation; the user changes them by asking |
| `transform_llm_output` tombstone, `excuse_pool.json`, `activations.jsonl` | Not reproduced |

## Setup
None. Optionally the user states a ratio and mode at the start of the session (the plugin read `JEKYLL_HYDE_RATIO`, `JEKYLL_HYDE_MODE`, `JEKYLL_HYDE_HEURISTIC_ACTION`, `JEKYLL_HYDE_CORPUS`; here they are just conversation settings).

## Limits
- No independent auditor: the same model audits itself, so the "disposable clone" isolation the README relies on is absent.
- No transcript rewriting, no persisted state across sessions, no slash command.
- No LICENSE file in the repository, so no prompt text is copied; the procedure above is a summary.
- The upstream README's claims about RLHF-induced sandbagging are the author's thesis, not verified facts.

## Source
- Catalog entry (reviewed commit): https://github.com/jnorthrup/hermes-jekyl-hyde/tree/10149e57ec2cf47a0184d475ca4d5cb797b54c2d
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/jekyll-hyde.yaml
