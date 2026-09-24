# Wiring the constitution into your governance server

Your `rl_mcp_server.py` is **pure stdlib, hand-rolled JSON-RPC** (not FastMCP), and
deliberately dependency-free. So the integration is NOT `register(mcp)` — it adds
MCP **resources** the same way you added tools: a static list + a read dispatch,
serving the *compiled* constitution files verbatim (stdlib `json` only, no YAML in
the trust root).

## What's in this folder

- **`rl_mcp_server.py`** — your file with the resource layer added. Diff vs. yours:
  1. imports `constitution_stdlib` (guarded; server still runs if it's absent);
  2. `initialize` advertises a `resources` capability when available;
  3. `handle()` gains `resources/list`, `resources/templates/list`, `resources/read`;
  4. `_tests()` gains 5 resource checks (skipped if the files aren't present).
  Everything else — the STILLING tools, ledger, persistence, wire protocol — is byte-for-byte yours.
- **`constitution_stdlib.py`** — the resource module (stdlib only). Serves the
  compiled files under `RL_CONSTITUTION_DIR`.

## Install

```bash
# 1. put both files next to stilling.py (constitution_stdlib.py beside rl_mcp_server.py)
cp server/rl_mcp_server.py server/constitution_stdlib.py  /path/to/your/governance/

# 2. point at your rl-stack checkout and compile once so out/ exists
export RL_CONSTITUTION_DIR=/path/to/rl-stack
python3 /path/to/rl-stack/compilers/compile.py

# 3. run your existing self-test — now includes the resource checks
python3 rl_mcp_server.py test
# ... PASS resources_list_has_constitution / resources_read_constitution / resources_read_worker ...
```

If `RL_CONSTITUTION_DIR` is unset or `out/` is missing, the server runs exactly as
before and simply advertises no resources — nothing breaks.

## What clients get

Any MCP client on this server (Hermes, Vellum, Claude via MCP) can now
`resources/read`:

```
rl://constitution              source-of-truth worker order + rules (YAML)
rl://constitution/json         parsed
rl://constitution/preamble     rules preamble for non-Claude clients
rl://constitution/structure    human-readable pipeline + roster
rl://constitution/router       compiled cascade-router tier config
rl://constitution/worker/{id}  one worker's definition
```

Rules and gate readings now come from the **same server** — the fleet reads one
structure, and STILLING adjudicates, exactly as your header describes.

## Refresh on edit

The server serves files, so after editing `stack-constitution.yaml`:
`python3 compilers/compile.py` (rewrites `out/`). Clients see the new version on
their next `resources/read` — no server restart needed (files are read per request).

## Alternative: FastMCP

If you ever move the governance server to the official SDK, `constitution_resource.py`
exposes the same resources via FastMCP (`register(mcp)`). Not needed for your
current stdlib server — it's there only for that future.
