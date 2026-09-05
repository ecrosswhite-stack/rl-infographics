"""Projection: the cascade router's tier + routing config, from the constitution.

Emits a JSON the router loads instead of its own hardcoded config, so model
choice and governance rules are one artifact. Secrets are NOT emitted — only the
env var NAMES the router should read at runtime.
"""
from __future__ import annotations

import json


def build_router_config(c: dict) -> dict:
    r = dict(c.get("router", {}))
    r["_constitution_version"] = c["meta"]["version"]
    # attach the shared rule preamble so the router injects governed rules per tier
    from projections.router_inject import build_inject
    r["_inject"] = build_inject(c)
    return r


def build_router_config_json(c: dict) -> str:
    return json.dumps(build_router_config(c), indent=2)
