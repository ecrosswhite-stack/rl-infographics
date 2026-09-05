---
name: rl-state-sync
description: At the start of any substantive Reticulative Logic turn, reconstruct current project state before answering, so you never respond a version behind. Use this whenever Eris references "the corpus", "the gate", "current status", a module, the swarm, the patent/trademark, the Pfizer pilot, Asha's deliverables, or picks up a thread from a prior session. Pull live state from the swarm and prior chats rather than assuming the numbers in your head are current. Answering from stale state is a top operator-drift failure.
---

# rl-state-sync  (constitution v1.1.0 shim)

This worker's rules are defined in the **Stack Constitution** — the single source
of truth shared by every AI in the fleet. Do not follow a private copy; load the
live definition and apply it.

**Load live:** governance MCP resource `rl://constitution/worker/rl-state-sync`
(or the whole thing at `rl://constitution`). If the server is unreachable, apply
the summary below and flag that it may be a version behind.

- **Phase / order:** ingress / 1
- **Fires:** if mode in [BUILD, FINAL_DIRECT, CONCEPTUAL] or turn references live state (skip if mode == TALK_VISION)
- **Role:** ingress state reconstruction
- **Note:** Reconstruct current state from live sources; never answer a version behind.

Apply the constitution's `hard_rules` plus this worker's entry under
`workers.rl-state-sync`. Use the shared output shape (per-claim TRUTH/FALSITY/IGNORANCE,
a DATA REQUEST on every IGNORANCE). Do not print the MODE classification unless asked.
