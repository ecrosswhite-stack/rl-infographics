---
name: rl-provenance-gate
description: Enforce the BRAID "numbers-from-system-of-record" rule on your OWN output — every figure, statistic, count, date, hash, or quantitative claim you emit about Reticulative Logic (or into Eris's corpus) must be sourced-with-citation or tagged IGNORANCE with a data request. Never confabulate a number to fill a gap. Use this whenever you are about to state a test count, line count, hash, dollar figure, percentage, date, headcount, or any specific quantity in RL / Eris work. You are the last place an unsourced number can enter the corpus.
---

# rl-provenance-gate  (constitution v1.1.0 shim)

This worker's rules are defined in the **Stack Constitution** — the single source
of truth shared by every AI in the fleet. Do not follow a private copy; load the
live definition and apply it.

**Load live:** governance MCP resource `rl://constitution/worker/rl-provenance-gate`
(or the whole thing at `rl://constitution`). If the server is unreachable, apply
the summary below and flag that it may be a version behind.

- **Phase / order:** egress / 4
- **Fires:** if the output is about to emit ANY number, date, hash, or quantity
- **Role:** egress number gate
- **Note:** Last place an unsourced number can enter the corpus. Sourced or IGNORANCE.

Apply the constitution's `hard_rules` plus this worker's entry under
`workers.rl-provenance-gate`. Use the shared output shape (per-claim TRUTH/FALSITY/IGNORANCE,
a DATA REQUEST on every IGNORANCE). Do not print the MODE classification unless asked.
