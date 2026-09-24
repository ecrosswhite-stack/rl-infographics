---
name: rl-verdict-cast
description: Render any substantive Reticulative Logic answer, decision, or forecast into the reticulative verdict shape — per-claim epistemic state (TRUTH / FALSITY / IGNORANCE), flagged contradictions, and a data request on every IGNORANCE — matching reticulative_answer.py. Use this whenever Eris asks a decision, forecast, checkable claim, or "should I / is this true" question about Reticulative Logic or his ventures, so the output format stays uniform and engine-consistent rather than hand-rolled prose.
---

# rl-verdict-cast  (constitution v1.1.0 shim)

This worker's rules are defined in the **Stack Constitution** — the single source
of truth shared by every AI in the fleet. Do not follow a private copy; load the
live definition and apply it.

**Load live:** governance MCP resource `rl://constitution/worker/rl-verdict-cast`
(or the whole thing at `rl://constitution`). If the server is unreachable, apply
the summary below and flag that it may be a version behind.

- **Phase / order:** egress / 6
- **Fires:** if turn is a decision, forecast, checkable claim, or go/no-go (skip if mode == TALK_VISION)
- **Role:** egress output shape
- **Note:** Output SHAPE — per-claim TRUTH/FALSITY/IGNORANCE, contradictions, converged verdict.

Apply the constitution's `hard_rules` plus this worker's entry under
`workers.rl-verdict-cast`. Use the shared output shape (per-claim TRUTH/FALSITY/IGNORANCE,
a DATA REQUEST on every IGNORANCE). Do not print the MODE classification unless asked.
