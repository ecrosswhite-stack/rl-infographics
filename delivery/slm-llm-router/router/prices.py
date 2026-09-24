"""Cost math. The only place dollars are computed.

A claim about money needs an arithmetic trail, so every cost flows through here.
Local tiers (mock/ollama) cost $0. The large tier is billed per token, input and
output separately, matching how hosted APIs bill.
"""
from __future__ import annotations

from .config import ModelSpec


def token_cost(spec: ModelSpec, input_tokens: int, output_tokens: int) -> float:
    """USD cost for one call to `spec`.

    Billed straight from the price fields: a local tier (ollama) carries price 0
    and so costs nothing, while the mock large tier carries the real large-model
    price so the savings math is honest even in an offline run.
    """
    return (
        input_tokens / 1_000_000.0 * spec.price_in_per_m
        + output_tokens / 1_000_000.0 * spec.price_out_per_m
    )


# Reference price table (USD per 1M tokens), for documentation and quick swaps.
# These are list prices as of the versions pinned in README; verify before you
# quote savings to anyone.
REFERENCE_PRICES = {
    # provider/model               (in,     out)
    "groq/openai/gpt-oss-120b":    (0.15,   0.60),
    "openai/gpt-4o-mini":          (0.15,   0.60),
    "anthropic/claude-haiku-4-5":  (1.00,   5.00),
    "anthropic/claude-sonnet":     (3.00,  15.00),
    "together/llama-3.3-70b":      (0.88,   0.88),
    "local/ollama":                (0.00,   0.00),
}
