"""Projection: thin Claude skill shims that defer to the live constitution.

Instead of 8 hand-maintained SKILL.md files that drift from the source of truth,
each becomes a short shim whose body says: this worker's rules are defined in the
constitution; load the live version from the governance MCP resource, apply your
phase's rules. The trigger (`description`) is preserved so Claude still auto-fires
the right worker at the right time.
"""
from __future__ import annotations


def _trigger_for(worker_id: str) -> str:
    # kept terse; the authoritative triggers live in the constitution pipeline.
    return {
        "rl-mode-sentinel": "Use on ANY Reticulative Logic / Eris-facing turn, before writing. Classifies MODE.",
        "rl-state-sync": "Use when the turn depends on current state (corpus, gate, swarm, IP, commitments).",
        "thalweg-focus-engine": "Use for where-to-look / is-this-rewrite-better questions about a frame or objective.",
        "reticulative-data-gate": "Use when a checkable decision/forecast is made, an outcome arrives, or gate status is asked.",
        "rl-provenance-gate": "Use before emitting ANY number, date, hash, or quantity about RL / the corpus.",
        "rl-axis-firewall": "Use as a final pass before any decision-maker-facing (attorney/Pfizer/investor) output.",
        "rl-verdict-cast": "Use for decisions, forecasts, checkable claims, go/no-go calls (output shape).",
        "rl-resonance-in-gate": "Use ONLY for outward-facing persuasive pieces; never internal writing or aimed at Eris.",
    }.get(worker_id, "Reticulative Logic governance worker.")


def build_shims(c: dict) -> dict[str, str]:
    version = c["meta"]["version"]
    out: dict[str, str] = {}
    for step in sorted(c["pipeline"], key=lambda s: s["order"]):
        wid = step["worker"]
        w = c["workers"][wid]
        cond = "always, first" if step.get("always") else f"if {step.get('run_if','applicable')}"
        skip = f" (skip if {step['skip_if']})" if step.get("skip_if") else ""
        body = f"""---
name: {wid}
description: {_trigger_for(wid)}
---

# {wid}  (constitution v{version} shim)

This worker is defined in the **Stack Constitution** — the single source of truth
shared by every AI in the fleet. Do not follow a private copy of these rules;
load the live version and apply them.

**Load live:** governance MCP resource `rl://constitution` (or
`rl://constitution/worker/{wid}`). If unreachable, use the values below and flag
that they may be a version behind.

- **Phase / order:** {step['phase']} / {step['order']}
- **Fires:** {cond}{skip}
- **Role:** {w.get('role','')}
- **Note:** {step.get('note','')}

Apply the constitution's `hard_rules` and, for this worker, its entry under
`workers.{wid}`. Report per the shared output shape (TRUTH/FALSITY/IGNORANCE +
data request on every IGNORANCE). Do not print the MODE classification unless asked.
"""
        out[f"{wid}/SKILL.md"] = body
    return out
