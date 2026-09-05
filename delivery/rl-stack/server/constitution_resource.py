"""Serve the stack constitution as a live MCP resource.

This is how "all AI can see the structure" at runtime: any MCP-capable client
reads `rl://constitution` and gets the current rules; non-MCP clients read the
compiled `rl://constitution/preamble`. One source, fetched live, so an edit to
the YAML moves the whole fleet at once.

Two ways to use it:

  A) Standalone (quick start):
       pip install "mcp[cli]" pyyaml
       python3 server/constitution_resource.py
     Exposes resources over stdio for any MCP client.

  B) Register onto your existing governance server (recommended):
     In rl_mcp_server.py (the one running stilling.py), do:
         from server.constitution_resource import register
         register(mcp)                      # mcp = your FastMCP instance
     Now the constitution rides alongside the stilling_* tools, enforced from the
     same place, and clients get rules + gate readings from one server.

Resources exposed:
  rl://constitution              -> raw YAML (source of truth)
  rl://constitution/json         -> parsed JSON
  rl://constitution/preamble     -> compiled system preamble (non-Claude clients)
  rl://constitution/structure    -> human-readable pipeline + roster
  rl://constitution/worker/{id}  -> one worker's definition
"""
from __future__ import annotations

import json
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "compilers"))
CONSTITUTION = os.path.join(ROOT, "constitution", "stack-constitution.yaml")


def load_yaml_text() -> str:
    with open(CONSTITUTION) as f:
        return f.read()


def load() -> dict:
    return yaml.safe_load(load_yaml_text())


def preamble() -> str:
    from projections.system_preamble import build_preamble
    return build_preamble(load())


def worker(worker_id: str) -> str:
    c = load()
    w = c.get("workers", {}).get(worker_id)
    if not w:
        return json.dumps({"error": f"unknown worker '{worker_id}'"})
    step = next((s for s in c["pipeline"] if s["worker"] == worker_id), {})
    return json.dumps({"id": worker_id, "definition": w, "pipeline": step,
                       "hard_rules": c["hard_rules"], "version": c["meta"]["version"]}, indent=2)


def structure() -> str:
    from compile import _structure_md  # type: ignore
    return _structure_md(load())


def register(mcp) -> None:
    """Attach the constitution resources to an existing FastMCP server."""

    @mcp.resource("rl://constitution")
    def _raw() -> str:
        return load_yaml_text()

    @mcp.resource("rl://constitution/json")
    def _json() -> str:
        return json.dumps(load(), indent=2)

    @mcp.resource("rl://constitution/preamble")
    def _preamble() -> str:
        return preamble()

    @mcp.resource("rl://constitution/structure")
    def _structure() -> str:
        return structure()

    @mcp.resource("rl://constitution/worker/{worker_id}")
    def _worker(worker_id: str) -> str:
        return worker(worker_id)


def _standalone() -> None:
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception:
        print("Standalone mode needs the MCP SDK:  pip install \"mcp[cli]\"", file=sys.stderr)
        print("Or register(mcp) onto your existing governance server instead.", file=sys.stderr)
        sys.exit(1)
    mcp = FastMCP("reticulative-constitution")
    register(mcp)
    mcp.run()


if __name__ == "__main__":
    _standalone()
