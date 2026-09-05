"""The two tiers, as thin wrappers over providers.

Small tier: answers locally, returns answer + token counts (cost $0).
Large tier: the fallback, billed per token.
Also exposes self-consistency sampling used by the verifier.
"""
from __future__ import annotations

from . import config, providers
from .providers import Answer


def ask_small(prompt: str, meta: dict, temperature: float = 0.0, sample: int = 0) -> Answer:
    return providers.complete(
        config.small_tier(), prompt, role="small", sample=sample, temperature=temperature, meta=meta
    )


def ask_large(prompt: str, meta: dict, temperature: float = 0.0) -> Answer:
    return providers.complete(
        config.large_tier(), prompt, role="large", sample=0, temperature=temperature, meta=meta
    )


def small_samples(prompt: str, meta: dict, k: int) -> list[Answer]:
    """k samples from the small tier for self-consistency (temp > 0)."""
    return [ask_small(prompt, meta, temperature=0.7, sample=s) for s in range(k)]
