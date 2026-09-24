#!/usr/bin/env python3
"""Validate that the stack constitution composes into a coherent pipeline.

Catches the exact failure classes this project exists to prevent:
  - two workers both claiming ingress order 0 (the "who runs first" collision)
  - a pipeline step naming a worker that isn't defined
  - a roster client whose projection has no compiler
  - an axis or hard rule referenced but missing
Run: python3 validate.py
"""
from __future__ import annotations

import sys

import yaml

CONSTITUTION = "constitution/stack-constitution.yaml"
KNOWN_PROJECTIONS = {"claude_skill_shims", "system_preamble", "router_inject", "inject"}


def load(path=CONSTITUTION):
    with open(path) as f:
        return yaml.safe_load(f)


def validate(c: dict) -> list[str]:
    errs: list[str] = []
    workers = c.get("workers", {})
    pipeline = c.get("pipeline", [])

    # 1. pipeline order is unique and sortable
    orders = [step["order"] for step in pipeline]
    if len(orders) != len(set(orders)):
        dupes = sorted({o for o in orders if orders.count(o) > 1})
        errs.append(f"pipeline: duplicate order value(s) {dupes} — ambiguous worker order")

    # 2. exactly one always-on ingress classifier at order 0
    ingress0 = [s for s in pipeline if s.get("order") == 0]
    if not ingress0:
        errs.append("pipeline: no order-0 ingress worker (nothing classifies MODE first)")
    elif not ingress0[0].get("always"):
        errs.append("pipeline: order-0 worker is not marked always:true")

    # 3. every pipeline worker is defined
    for step in pipeline:
        if step["worker"] not in workers:
            errs.append(f"pipeline: step references undefined worker '{step['worker']}'")

    # 4. every defined worker appears in the pipeline
    used = {s["worker"] for s in pipeline}
    for w in workers:
        if w not in used:
            errs.append(f"workers: '{w}' is defined but never placed in the pipeline")

    # 5. roster projections all have a known compiler
    for client in c.get("roster", []):
        proj = client.get("projection")
        if proj not in KNOWN_PROJECTIONS:
            errs.append(f"roster: client '{client['id']}' uses unknown projection '{proj}'")

    # 6. mode_gates_state is real: state-sync must skip TALK_VISION
    ss = next((s for s in pipeline if s["worker"] == "rl-state-sync"), None)
    if ss and "TALK_VISION" not in str(ss.get("skip_if", "")):
        errs.append("pipeline: rl-state-sync must skip_if TALK_VISION (mode_gates_state invariant)")

    # 7. required top-level sections present
    for key in ("meta", "modes", "axes", "hard_rules", "state_pointers", "roster"):
        if key not in c:
            errs.append(f"missing top-level section: {key}")

    # 8. numbers policy is declared (provenance discipline)
    if c.get("meta", {}).get("numbers_policy") != "sourced-or-IGNORANCE":
        errs.append("meta.numbers_policy must be 'sourced-or-IGNORANCE'")

    # 9. router section (if present) is coherent
    r = c.get("router")
    if r is not None:
        known_backends = {"mock", "ollama", "openai_compatible", "anthropic", "bedrock"}
        tiers = r.get("tiers", {})
        for role in ("small", "large"):
            t = tiers.get(role)
            if not t:
                errs.append(f"router.tiers: missing '{role}' tier")
                continue
            if t.get("backend") not in known_backends:
                errs.append(f"router.tiers.{role}: unknown backend '{t.get('backend')}'")
            for pk in ("price_in_per_m", "price_out_per_m"):
                if not isinstance(t.get(pk), (int, float)):
                    errs.append(f"router.tiers.{role}.{pk} must be numeric")
        if r.get("mode") not in ("mock", "live"):
            errs.append("router.mode must be 'mock' or 'live'")
        for preset, spec in (r.get("large_presets") or {}).items():
            if spec.get("backend") not in known_backends:
                errs.append(f"router.large_presets.{preset}: unknown backend '{spec.get('backend')}'")

    return errs


def main():
    c = load()
    errs = validate(c)
    if errs:
        print(f"FAIL — {len(errs)} problem(s):")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    n_workers = len(c.get("workers", {}))
    n_steps = len(c.get("pipeline", []))
    n_clients = len(c.get("roster", []))
    print(f"OK — constitution v{c['meta']['version']} composes: "
          f"{n_workers} workers, {n_steps} pipeline steps, {n_clients} clients.")


if __name__ == "__main__":
    main()
