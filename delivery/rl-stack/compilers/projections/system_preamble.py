"""Projection: a compact system-prompt preamble for any non-Claude client.

Kimi, ChatGPT, Gemini, Grok, Hermes workers — none can load Claude skills, so
they get this generated block seeded into their system prompt (or fetched live
from the governance MCP resource). It is a rendering of the constitution, never
a hand-written second copy of the rules.
"""
from __future__ import annotations


def build_preamble(c: dict) -> str:
    meta = c["meta"]
    lines: list[str] = []
    a = lines.append

    a(f"# {meta['name']} — v{meta['version']} (loaded {meta['updated']})")
    a("You operate inside a governed AI stack. These rules are shared by every AI")
    a("in the fleet and are served live from the governance MCP. Follow them exactly.")
    a("")

    a("## 1. Classify the turn FIRST (MODE), before writing anything")
    for mode, spec in c["modes"].items():
        bits = []
        if spec.get("honesty_apparatus") is not None:
            bits.append(f"apparatus={spec['honesty_apparatus']}")
        if spec.get("disclaimer_load"):
            bits.append(f"disclaimers={spec['disclaimer_load']}")
        if spec.get("scrutiny"):
            bits.append(f"scrutiny={spec['scrutiny']}")
        aka = ", ".join(spec.get("aka", []))
        a(f"- **{mode}** ({aka}): " + "; ".join(bits))
    a("MODE gates everything downstream. Misclassifying the turn is worse than any single wrong fact.")
    a("")

    a("## 2. Worker order (ingress -> work -> egress)")
    for step in sorted(c["pipeline"], key=lambda s: s["order"]):
        cond = ""
        if step.get("always"):
            cond = "ALWAYS"
        elif step.get("run_if"):
            cond = f"if {step['run_if']}"
        skip = f"  (skip if {step['skip_if']})" if step.get("skip_if") else ""
        a(f"{step['order']}. [{step['phase']}] **{step['worker']}** — {cond}{skip}")
        a(f"     {step.get('note','')}")
    a("")

    a("## 3. Keep these axes strictly separate (a win on one is NOT a win on another)")
    for ax in c["axes"]:
        a(f"- **{ax['id']}**: establishes \"{ax['establishes']}\" — does NOT establish \"{ax['does_not_establish']}\".")
    a("")

    a("## 4. Hard rules — no MODE relaxes these")
    for rid, text in c["hard_rules"].items():
        a(f"- **{rid}**: {text}")
    a("")

    a("## 5. Live state — never remember it, fetch it")
    sp = c["state_pointers"]["corpus_and_gate"]
    a(f"- Current versions / test counts / gate status: fetch from {', '.join(sp['sources'])}.")
    a(f"- If unreachable: {sp['fallback']}.")
    a("- Any quantity you cannot source right now -> tag [IGNORANCE] + a data request. Never invent a number.")
    a("")

    a("## 6. Output shape for decisions/forecasts")
    a("Per load-bearing claim: [TRUTH]/[FALSITY]/[IGNORANCE] + one-line basis; every IGNORANCE carries a DATA REQUEST;")
    a("flag CONTRADICTIONs; close with => converged verdict. Grounding/vision is non-propositional (states, not %).")

    return "\n".join(lines) + "\n"
