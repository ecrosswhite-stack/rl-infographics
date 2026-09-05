---
name: rl-provenance-gate
description: Use before emitting ANY number, date, hash, or quantity about RL / the corpus.
---

# rl-provenance-gate  (constitution v1.1.0 shim)

This worker is defined in the **Stack Constitution** — the single source of truth
shared by every AI in the fleet. Do not follow a private copy of these rules;
load the live version and apply them.

**Load live:** governance MCP resource `rl://constitution` (or
`rl://constitution/worker/rl-provenance-gate`). If unreachable, use the values below and flag
that they may be a version behind.

- **Phase / order:** egress / 4
- **Fires:** if the output is about to emit ANY number, date, hash, or quantity
- **Role:** egress number gate
- **Note:** Last place an unsourced number can enter the corpus. Sourced or IGNORANCE.

Apply the constitution's `hard_rules` and, for this worker, its entry under
`workers.rl-provenance-gate`. Report per the shared output shape (TRUTH/FALSITY/IGNORANCE +
data request on every IGNORANCE). Do not print the MODE classification unless asked.
