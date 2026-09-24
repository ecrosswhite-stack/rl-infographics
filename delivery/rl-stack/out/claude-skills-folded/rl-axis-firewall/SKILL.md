---
name: rl-axis-firewall
description: Before ANY Reticulative Logic output that will reach a decision-maker (patent attorney, Pfizer contact, investor, or external evaluator), scan for axis-conflation — one axis of status leaking into another and inflating the claim. Use this whenever drafting or reviewing attorney/Pfizer/investor-facing material, or any claim about the patent, trademark, tests, expert panels, data gate, or system maturity, or any sentence a skeptic could read as "this is proven." This is the single conflation that could sink the project with a decision-maker. Run it as a final pass before the text leaves.
---

# rl-axis-firewall  (constitution v1.1.0 shim)

This worker's rules are defined in the **Stack Constitution** — the single source
of truth shared by every AI in the fleet. Do not follow a private copy; load the
live definition and apply it.

**Load live:** governance MCP resource `rl://constitution/worker/rl-axis-firewall`
(or the whole thing at `rl://constitution`). If the server is unreachable, apply
the summary below and flag that it may be a version behind.

- **Phase / order:** egress / 5
- **Fires:** if mode == FINAL_DIRECT or output reaches a decision-maker
- **Role:** egress axis-separation gate (decision-maker-facing)
- **Note:** Final pass. Any axis borrowing another's authority is a FALSITY the moment it ships.

Apply the constitution's `hard_rules` plus this worker's entry under
`workers.rl-axis-firewall`. Use the shared output shape (per-claim TRUTH/FALSITY/IGNORANCE,
a DATA REQUEST on every IGNORANCE). Do not print the MODE classification unless asked.
