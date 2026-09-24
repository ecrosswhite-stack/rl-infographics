#!/usr/bin/env python3
"""Compile the stack constitution into every client projection.

One source of truth (constitution/stack-constitution.yaml) ->
  out/system_preamble.md        (Kimi, ChatGPT, Gemini, Grok, Hermes workers)
  out/router_inject.txt         (SLM+LLM cascade tiers)
  out/claude-skills/<w>/SKILL.md (Claude shims that defer to the live constitution)
  out/STRUCTURE.md              (human-readable pipeline, so people see it too)

Run: python3 compilers/compile.py
"""
from __future__ import annotations

import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from projections.claude_skill_shims import build_shims  # noqa: E402
from projections.router_config import build_router_config_json  # noqa: E402
from projections.router_inject import build_inject  # noqa: E402
from projections.system_preamble import build_preamble  # noqa: E402

CONSTITUTION = os.path.join(ROOT, "constitution", "stack-constitution.yaml")
OUT = os.path.join(ROOT, "out")


def _structure_md(c: dict) -> str:
    v = c["meta"]["version"]
    lines = [f"# Stack structure (constitution v{v})", "",
             "Every AI in the fleet reads a projection of one file. Order below is authoritative.", ""]
    lines.append("## Pipeline")
    lines.append("```")
    for step in sorted(c["pipeline"], key=lambda s: s["order"]):
        cond = "ALWAYS" if step.get("always") else f"if {step.get('run_if','')}"
        skip = f"  [skip if {step['skip_if']}]" if step.get("skip_if") else ""
        lines.append(f"{step['order']}  {step['phase']:<15} {step['worker']:<24} {cond}{skip}")
    lines.append("```")
    lines.append("")
    lines.append("## Roster (who reads it, and how)")
    lines.append("| client | kind | reads via | projection |")
    lines.append("|---|---|---|---|")
    for r in c["roster"]:
        lines.append(f"| {r['id']} | {r['kind']} | `{r['read']}` | {r['projection']} |")
    lines.append("")
    lines.append("## Independent axes (never conflate)")
    for ax in c["axes"]:
        lines.append(f"- **{ax['id']}** — establishes *{ax['establishes']}*; NOT *{ax['does_not_establish']}*")
    return "\n".join(lines) + "\n"


def main():
    with open(CONSTITUTION) as f:
        c = yaml.safe_load(f)
    os.makedirs(OUT, exist_ok=True)

    with open(os.path.join(OUT, "system_preamble.md"), "w") as f:
        f.write(build_preamble(c))

    with open(os.path.join(OUT, "router_inject.txt"), "w") as f:
        f.write(build_inject(c))

    with open(os.path.join(OUT, "router_config.json"), "w") as f:
        f.write(build_router_config_json(c))

    # full parsed constitution as JSON, so a stdlib-only server can serve it
    # (json/worker views) without a YAML dependency in its trust root.
    with open(os.path.join(OUT, "constitution.json"), "w") as f:
        json.dump(c, f, indent=2)

    shims = build_shims(c)
    for rel, body in shims.items():
        p = os.path.join(OUT, "claude-skills", rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(body)

    with open(os.path.join(OUT, "STRUCTURE.md"), "w") as f:
        f.write(_structure_md(c))

    print(f"compiled constitution v{c['meta']['version']} ->")
    print(f"  out/system_preamble.md      ({len(build_preamble(c))} bytes)")
    print(f"  out/router_inject.txt")
    print(f"  out/router_config.json")
    print(f"  out/claude-skills/         ({len(shims)} shims)")
    print(f"  out/STRUCTURE.md")


if __name__ == "__main__":
    main()
