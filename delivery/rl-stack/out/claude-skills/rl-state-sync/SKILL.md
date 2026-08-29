---
name: rl-state-sync
description: Use when the turn depends on current state (corpus, gate, swarm, IP, commitments).
---

# rl-state-sync  (constitution v1.1.0 shim)

This worker is defined in the **Stack Constitution** — the single source of truth
shared by every AI in the fleet. Do not follow a private copy of these rules;
load the live version and apply them.

**Load live:** governance MCP resource `rl://constitution` (or
`rl://constitution/worker/rl-state-sync`). If unreachable, use the values below and flag
that they may be a version behind.

- **Phase / order:** ingress / 1
- **Fires:** if mode in [BUILD, FINAL_DIRECT, CONCEPTUAL] or turn references live state (skip if mode == TALK_VISION)
- **Role:** ingress state reconstruction
- **Note:** Reconstruct current state from live sources; never answer a version behind.

Apply the constitution's `hard_rules` and, for this worker, its entry under
`workers.rl-state-sync`. Report per the shared output shape (TRUTH/FALSITY/IGNORANCE +
data request on every IGNORANCE). Do not print the MODE classification unless asked.
