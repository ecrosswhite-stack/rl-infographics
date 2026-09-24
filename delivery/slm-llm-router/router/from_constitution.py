"""Drop-in adapter: make the cascade router read its tiers from the constitution.

Copy this file into the router package as `router/from_constitution.py`, then
apply the small patch shown in router_adapter/PATCH-config.md. After that, the
router's model choice, prices, and routing knobs come from the ONE source of
truth (out/router_config.json, compiled from stack-constitution.yaml) — or from
the live MCP resource if you point RL_ROUTER_CONFIG at a fetched copy.

Secrets never live in the config: each tier names an env var (api_key_env /
base_url_env) that this adapter resolves at runtime.
"""
from __future__ import annotations

import json
import os

from .config import ModelSpec  # the router's own dataclass

# Where the compiled config lives. Point at out/router_config.json, or at a file
# you fetched from rl://constitution/json (then read its ["router"] block).
CONFIG_PATH = os.environ.get("RL_ROUTER_CONFIG", "router_config.json")


def _load() -> dict:
    with open(CONFIG_PATH) as f:
        data = json.load(f)
    # accept either the router block directly, or a full constitution json
    return data.get("router", data)


def _spec(tier: dict) -> ModelSpec:
    base_url = tier.get("base_url", "")
    if not base_url and tier.get("base_url_env"):
        base_url = os.environ.get(tier["base_url_env"], "")
    extra = {}
    if tier.get("region"):
        extra["region"] = tier["region"]
    return ModelSpec(
        name=tier.get("name", tier.get("backend", "")),
        backend=tier["backend"],
        model=tier.get("name", ""),
        price_in_per_m=float(tier.get("price_in_per_m", 0.0)),
        price_out_per_m=float(tier.get("price_out_per_m", 0.0)),
        base_url=base_url,
        api_key_env=tier.get("api_key_env", ""),
        extra=extra,
    )


_cfg = _load()
MODE = _cfg.get("mode", "mock")


def small_tier() -> ModelSpec:
    if MODE == "mock":
        return ModelSpec(name="mock-slm", backend="mock")
    return _spec(_cfg["tiers"]["small"])


def large_tier() -> ModelSpec:
    large = _spec(_cfg["tiers"]["large"])
    if MODE == "mock":
        # keep the real price so cost math stays honest offline
        return ModelSpec(name="mock-llm", backend="mock",
                         price_in_per_m=large.price_in_per_m,
                         price_out_per_m=large.price_out_per_m)
    return large


# routing knobs, sourced from the constitution
TARGET_RATE = float(_cfg.get("target_routing_rate", 0.25))
VERIFIER_THRESHOLD = _cfg.get("verifier_threshold")  # None => auto-pick
CALIBRATION_MIN_SLM_ACC = float(_cfg.get("calibration_floor", 0.55))
SELF_CONSISTENCY_K = int(_cfg.get("self_consistency_k", 3))
EVAL_SIZE = int(_cfg.get("eval_size", 120))
INJECT = _cfg.get("_inject", "")
