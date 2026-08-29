#!/usr/bin/env python3
"""Fold the 8 Claude skills into thin shims that defer to the live constitution.

Preserves each skill's EXACT `name` + `description` frontmatter (so Claude's
auto-triggering is byte-for-byte unchanged) and replaces only the BODY with a
shim that points at rl://constitution. Reads the current SKILL.md files from your
skills dir so the descriptions are the authoritative ones you tuned.

Writes to out/claude-skills-folded/<worker>/SKILL.md — it does NOT touch your
live (synced) skills. Apply them yourself; see the printed note.

Usage:
  python3 compilers/fold_claude_skills.py [SKILLS_SRC_DIR]

SKILLS_SRC_DIR defaults to $RL_CLAUDE_SKILLS_DIR, else the synced plugin path.
"""
from __future__ import annotations

import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "out", "claude-skills-folded")

DEFAULT_SRC = os.environ.get(
    "RL_CLAUDE_SKILLS_DIR",
    os.path.expanduser(
        "~/.claude/skills/synced/64bea4f7-b31c-4267-9104-f3f96d81bb59_04158e1c-eb6d-4a92-b04d-8558f30a63bd"
    ),
)

FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _read_frontmatter(path: str) -> dict:
    with open(path) as f:
        m = FRONTMATTER.match(f.read())
    if not m:
        raise ValueError(f"no frontmatter in {path}")
    return yaml.safe_load(m.group(1))


def _shim_body(name: str, fm: dict, step: dict, worker: dict, version: str) -> str:
    desc = fm.get("description", "").strip()
    cond = "always, first" if step.get("always") else f"if {step.get('run_if','applicable')}"
    skip = f" (skip if {step['skip_if']})" if step.get("skip_if") else ""
    # description preserved VERBATIM so triggering is unchanged
    return f"""---
name: {name}
description: {desc}
---

# {name}  (constitution v{version} shim)

This worker's rules are defined in the **Stack Constitution** — the single source
of truth shared by every AI in the fleet. Do not follow a private copy; load the
live definition and apply it.

**Load live:** governance MCP resource `rl://constitution/worker/{name}`
(or the whole thing at `rl://constitution`). If the server is unreachable, apply
the summary below and flag that it may be a version behind.

- **Phase / order:** {step.get('phase','?')} / {step.get('order','?')}
- **Fires:** {cond}{skip}
- **Role:** {worker.get('role','')}
- **Note:** {step.get('note','')}

Apply the constitution's `hard_rules` plus this worker's entry under
`workers.{name}`. Use the shared output shape (per-claim TRUTH/FALSITY/IGNORANCE,
a DATA REQUEST on every IGNORANCE). Do not print the MODE classification unless asked.
"""


def main() -> int:
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    with open(os.path.join(ROOT, "constitution", "stack-constitution.yaml")) as f:
        c = yaml.safe_load(f)
    version = c["meta"]["version"]
    steps = {s["worker"]: s for s in c["pipeline"]}

    os.makedirs(OUT, exist_ok=True)
    made, fell_back = [], []
    for wid, worker in c["workers"].items():
        src_skill = os.path.join(src, wid, "SKILL.md")
        if os.path.exists(src_skill):
            fm = _read_frontmatter(src_skill)
        else:  # fall back to a constitution-derived description
            fm = {"name": wid, "description": f"Reticulative Logic governance worker: {worker.get('role','')}."}
            fell_back.append(wid)
        body = _shim_body(wid, fm, steps.get(wid, {}), worker, version)
        d = os.path.join(OUT, wid)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "SKILL.md"), "w") as f:
            f.write(body)
        made.append(wid)

    print(f"folded {len(made)} skills -> {OUT}")
    if fell_back:
        print(f"  (no source found for, used derived description: {', '.join(fell_back)})")
    print("\nTo apply (these are your SYNCED skills — a sync may overwrite the cache,")
    print("so prefer applying at your skills SOURCE / plugin repo, then re-sync):")
    print(f"  cp -r {OUT}/*  <your-skills-source>/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
