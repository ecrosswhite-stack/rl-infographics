# Reticulative Logic — Stack Constitution

One source of truth for **worker order + rules**, served live from your governance
MCP, so **every AI in the fleet sees the same structure** — Claude, ChatGPT, Kimi,
Gemini, Grok, Hermes swarm workers, and the SLM+LLM cascade router.

## The problem this fixes

Your governance lived as 8 Claude-only skills with **no declared order** (a flat
`manifest.json`), and two of them both claimed "run first." So:
- the worker order existed only as prose, never as structure;
- only Claude could see the rules — the rest of your fleet couldn't;
- the rules were advice-per-turn, not a contract the stack enforces.

## The fix: one constitution, many renderings

```
        constitution/stack-constitution.yaml   (THE source of truth)
                          │
        served live as an MCP resource:  rl://constitution
                          │
   ┌──────────────┬───────┴────────┬─────────────────┐
   ▼              ▼                ▼                 ▼
 Claude       system_preamble   router_inject     Hermes swarm
 skill shims  (GPT/Kimi/Gemini  (every cascade    (fetch live at
 (defer to    /Grok)            tier)             task start)
  the live
  resource)
```

Edit the YAML once → every client moves together. Numbers are **never** baked in;
live state (versions, test counts, gate readings) is fetched by pointer.

## Canonical worker order (ingress → work → egress)

The collision ("who runs first") is resolved: **MODE gates STATE**, because a
`TALK_VISION` turn needs no sync.

| # | phase | worker | fires |
|---|---|---|---|
| 0 | ingress | `rl-mode-sentinel` | always, first |
| 1 | ingress | `rl-state-sync` | BUILD/FINAL/CONCEPTUAL or state-dependent (skip VISION) |
| 2 | work | `thalweg-focus-engine` | where-to-look / is-this-rewrite-better |
| 3 | work | `reticulative-data-gate` | checkable decision, outcome, or gate status |
| 4 | egress | `rl-provenance-gate` | any number about to leave |
| 5 | egress | `rl-axis-firewall` | decision-maker-facing (final pass) |
| 6 | egress | `rl-verdict-cast` | decisions/forecasts (output shape) |
| 7 | egress ∥ | `rl-resonance-in-gate` | outward persuasive pieces only |

Full definitions, MODE table, independent axes, and hard rules live in
`constitution/stack-constitution.yaml`.

## Layout

```
constitution/stack-constitution.yaml   source of truth (edit this) — governance + router tiers
validate.py                            checks the pipeline composes (no order collisions, router tiers, etc.)
compilers/compile.py                   YAML -> all projections in out/
compilers/projections/                 system_preamble / claude_skill_shims / router_inject / router_config
server/constitution_resource.py        serve rl://constitution as an MCP resource
server/rl_mcp_server.example.py        reference governance server with register(mcp) wired in
router_adapter/from_constitution.py    drop-in so the cascade router reads its tiers from here
router_adapter/PATCH-config.md         the exact 2-step router wiring
out/                                    generated projections (regenerate; don't hand-edit)
```

## The router is one governed lane

The SLM+LLM cascade's tier selection, prices, and routing knobs now live in the
constitution under `router:`. The router reads `out/router_config.json` (compiled
from the YAML) via `router_adapter/from_constitution.py`, so **model choice and
governance rules are one artifact**. Swapping the large tier (Groq → Claude →
Kimi → Grok → Bedrock → local) is: copy a `large_presets` entry into
`router.tiers.large`, recompile, rerun — no router code changes. Verified
end-to-end: swapping to the `anthropic` preset flips the router's pricing to
$1/$5 per 1M with zero code edits. Secrets never enter the config — each tier
names an env var. See `router_adapter/PATCH-config.md`.

## Use it

```bash
pip install pyyaml            # tooling
python3 validate.py          # OK — constitution vX composes: ...
python3 compilers/compile.py # writes out/system_preamble.md, router_inject.txt, claude-skills/, STRUCTURE.md
```

### Serve it live from your governance MCP (recommended)

Your `rl_mcp_server.py` is stdlib / hand-rolled JSON-RPC, so the constitution is
added as MCP **resources** (not FastMCP). Two files in `server/` do it:

- `server/rl_mcp_server.py` — your server with the resource layer added (STILLING
  tools byte-for-byte unchanged; adds `resources/list`, `resources/templates/list`,
  `resources/read`, and a `resources` capability).
- `server/constitution_stdlib.py` — serves the compiled files verbatim (stdlib
  `json` only; no YAML in the trust root).

```bash
cp server/rl_mcp_server.py server/constitution_stdlib.py  /path/to/your/governance/
export RL_CONSTITUTION_DIR=/path/to/rl-stack && python3 compilers/compile.py
python3 rl_mcp_server.py test     # your self-test, now with resource checks
```

Clients then read:
```
rl://constitution              raw YAML (source of truth)
rl://constitution/json         parsed
rl://constitution/preamble     compiled preamble for non-Claude clients
rl://constitution/structure    human-readable pipeline + roster
rl://constitution/router       compiled cascade-router tier config
rl://constitution/worker/{id}  one worker's definition
```

Rules and gate readings now come from **one** server, enforced together. Full
diff and install steps: `server/INTEGRATION.md`. (A FastMCP variant,
`server/constitution_resource.py`, exists only for a future SDK migration.)

### Point each client at it

- **Claude**: replace the 8 hand-written skills with the generated shims in
  `out/claude-skills/` — each defers to the live `rl://constitution`.
- **ChatGPT / Kimi / Gemini / Grok**: seed `out/system_preamble.md` into the
  system prompt (or have them fetch `rl://constitution/preamble` if MCP-capable).
- **Hermes swarm workers**: fetch `rl://constitution` at task start.
- **Cascade router**: prepend `out/router_inject.txt` to every tier's prompt.

## Migration (safe, reversible)

1. `validate.py` green, `compile.py` runs.
2. Serve the resource from the governance MCP; confirm one non-Claude client reads it.
3. Swap Claude's 8 skills for the shims; confirm behavior unchanged.
4. Add the preamble to the other clients one at a time.
5. From then on: **edit the YAML, bump `meta.version`, recompile** — never edit a
   projection by hand (they're regenerated).

## Guardrails kept from your own protocol

- Constitution stores **rules**, not numbers — live state by pointer (`rl-provenance-gate`, `rl-state-sync`).
- `validate.py` refuses a pipeline with a duplicate order or an undefined worker.
- Independent axes are declared once and shared, so `rl-axis-firewall` means the
  same thing to every AI.
