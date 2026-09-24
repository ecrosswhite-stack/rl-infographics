---
name: reticulative-data-gate
description: Capture real, labeled decision cases for Reticulative Logic v27.5 and gauge whether a decision class's DATA GATE may open. Use whenever the user makes a checkable forecast/decision, whenever a real-world outcome for a prior case becomes known, or when asked for gate status.
---

# reticulative-data-gate  (constitution v1.1.0 shim)

This worker's rules are defined in the **Stack Constitution** — the single source
of truth shared by every AI in the fleet. Do not follow a private copy; load the
live definition and apply it.

**Load live:** governance MCP resource `rl://constitution/worker/reticulative-data-gate`
(or the whole thing at `rl://constitution`). If the server is unreachable, apply
the summary below and flag that it may be a version behind.

- **Phase / order:** work / 3
- **Fires:** if a checkable prediction/decision is made, OR an outcome arrives, OR gate status asked
- **Role:** STILLING capture harness
- **Note:** Capture harness. Never the judge of correctness — the world is.

Apply the constitution's `hard_rules` plus this worker's entry under
`workers.reticulative-data-gate`. Use the shared output shape (per-claim TRUTH/FALSITY/IGNORANCE,
a DATA REQUEST on every IGNORANCE). Do not print the MODE classification unless asked.
