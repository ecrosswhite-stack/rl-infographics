"""Projection: a compact rule block to inject into every tier of the cascade router.

The SLM+LLM router runs several models per query. Each tier gets the same rule
preamble so the small local model and the large hosted model are governed
identically — the constitution rides inside the cascade, not bolted beside it.
"""
from __future__ import annotations


def build_inject(c: dict) -> str:
    v = c["meta"]["version"]
    hard = c["hard_rules"]
    key_rules = ["numbers_from_record", "axis_separation", "no_pfizer_data", "answer_first"]
    lines = [f"[RL stack v{v}] You are one tier in a governed cascade. Shared rules:"]
    for k in key_rules:
        if k in hard:
            lines.append(f"- {hard[k]}")
    lines.append("- Any quantity you cannot source -> [IGNORANCE] + data request; never invent numbers.")
    lines.append("- Decisions/forecasts: per-claim TRUTH/FALSITY/IGNORANCE, every IGNORANCE carries a data request.")
    return "\n".join(lines) + "\n"
