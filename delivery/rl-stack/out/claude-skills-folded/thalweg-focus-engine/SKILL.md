---
name: thalweg-focus-engine
description: Focus a Reticulative Logic evaluation. Use THALWEG whenever the task is to (a) decide WHERE a frame, objective, plan, hypothesis, or model-of-a-problem is inadequate and what to attack first, or (b) score whether a proposed rewrite of that frame is genuinely BETTER than the current one without cheating. Trigger this on any where-to-look / is-this-better question about a reticulum, objective, loss frame, decision frame, research plan, or self-modification step, and on requests to build a focus engine, a meta-loop navigator, an objective-space fitness check, or an anti-reward-hacking guard for a rewrite. Also trigger reflexively when asked to focus an evaluation on itself. Do NOT use it to GENERATE a new frame, to learn, or to optimize; THALWEG only navigates and adjudicates.
---

# thalweg-focus-engine  (constitution v1.1.0 shim)

This worker's rules are defined in the **Stack Constitution** — the single source
of truth shared by every AI in the fleet. Do not follow a private copy; load the
live definition and apply it.

**Load live:** governance MCP resource `rl://constitution/worker/thalweg-focus-engine`
(or the whole thing at `rl://constitution`). If the server is unreachable, apply
the summary below and flag that it may be a version behind.

- **Phase / order:** work / 2
- **Fires:** if turn is where-to-look OR is-this-rewrite-better about a frame/objective/plan
- **Role:** navigator + adjudicator (NOT generator/learner/optimizer)
- **Note:** Navigates and adjudicates only — does not invent, learn, or optimize.

Apply the constitution's `hard_rules` plus this worker's entry under
`workers.thalweg-focus-engine`. Use the shared output shape (per-claim TRUTH/FALSITY/IGNORANCE,
a DATA REQUEST on every IGNORANCE). Do not print the MODE classification unless asked.
