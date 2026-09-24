---
name: rl-verdict-cast
description: Use for decisions, forecasts, checkable claims, go/no-go calls (output shape).
---

# rl-verdict-cast  (constitution v1.1.0 shim)

This worker is defined in the **Stack Constitution** — the single source of truth
shared by every AI in the fleet. Do not follow a private copy of these rules;
load the live version and apply them.

**Load live:** governance MCP resource `rl://constitution` (or
`rl://constitution/worker/rl-verdict-cast`). If unreachable, use the values below and flag
that they may be a version behind.

- **Phase / order:** egress / 6
- **Fires:** if turn is a decision, forecast, checkable claim, or go/no-go (skip if mode == TALK_VISION)
- **Role:** egress output shape
- **Note:** Output SHAPE — per-claim TRUTH/FALSITY/IGNORANCE, contradictions, converged verdict.

Apply the constitution's `hard_rules` and, for this worker, its entry under
`workers.rl-verdict-cast`. Report per the shared output shape (TRUTH/FALSITY/IGNORANCE +
data request on every IGNORANCE). Do not print the MODE classification unless asked.
