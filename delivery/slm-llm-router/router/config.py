"""Central configuration for the SLM+LLM cascade router.

Everything provider-specific lives here. To swap the large tier away from Groq,
change LARGE_TIER below. Nothing else in the codebase names a provider.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

try:  # optional; the project runs fine offline without it
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is optional
    pass


@dataclass
class ModelSpec:
    """One tier: which backend answers, and what it costs per 1M tokens.

    backend is one of: "mock", "ollama", "openai_compatible", "anthropic",
    "bedrock". A local backend (mock/ollama) has price 0.0 and is billed as $0.
    """

    name: str
    backend: str
    model: str = ""
    price_in_per_m: float = 0.0   # USD per 1M input tokens
    price_out_per_m: float = 0.0  # USD per 1M output tokens
    # backend-specific connection details, read from env by default
    base_url: str = ""
    api_key_env: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def is_local(self) -> bool:
        return self.backend in ("mock", "ollama")


# ---------------------------------------------------------------------------
# Pick your tiers here.
#
# ROUTER_MODE controls the whole run:
#   "mock" -> both tiers are simulated, zero network, fully offline (default).
#   "live" -> use the real SMALL_TIER / LARGE_TIER specs below.
# Override with:  ROUTER_MODE=live python -m router.cli ...
# ---------------------------------------------------------------------------
ROUTER_MODE = os.environ.get("ROUTER_MODE", "mock").lower()


# The small model. On your laptop this is Ollama. Offline it is mocked.
SMALL_TIER_LIVE = ModelSpec(
    name="qwen3.5:4b",
    backend="ollama",
    model=os.environ.get("SMALL_MODEL", "qwen3.5:4b"),
    price_in_per_m=0.0,
    price_out_per_m=0.0,
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
)

# The large model. This is the ONE place Groq is named. Swap the block for any
# of the alternatives in prices.py / providers.py. Prices are USD per 1M tokens.
_LARGE_BACKEND = os.environ.get("LARGE_BACKEND", "openai_compatible")

_LARGE_PRESETS = {
    # OpenAI-compatible endpoints (Groq, OpenAI, Together, OpenRouter, vLLM...)
    "openai_compatible": ModelSpec(
        name=os.environ.get("LARGE_MODEL", "openai/gpt-oss-120b"),
        backend="openai_compatible",
        model=os.environ.get("LARGE_MODEL", "openai/gpt-oss-120b"),
        price_in_per_m=float(os.environ.get("LARGE_PRICE_IN", "0.15")),
        price_out_per_m=float(os.environ.get("LARGE_PRICE_OUT", "0.60")),
        base_url=os.environ.get("LARGE_BASE_URL", "https://api.groq.com/openai/v1"),
        api_key_env=os.environ.get("LARGE_API_KEY_ENV", "GROQ_API_KEY"),
    ),
    # Anthropic Claude as the large tier (native SDK). A natural Groq swap.
    "anthropic": ModelSpec(
        name=os.environ.get("LARGE_MODEL", "claude-haiku-4-5-20251001"),
        backend="anthropic",
        model=os.environ.get("LARGE_MODEL", "claude-haiku-4-5-20251001"),
        # Claude Haiku 4.5 list price (USD / 1M). Edit if you use Sonnet/Opus.
        price_in_per_m=float(os.environ.get("LARGE_PRICE_IN", "1.00")),
        price_out_per_m=float(os.environ.get("LARGE_PRICE_OUT", "5.00")),
        base_url=os.environ.get("ANTHROPIC_BASE_URL", ""),
        api_key_env="ANTHROPIC_API_KEY",
    ),
    # Amazon Bedrock (uses your AWS credentials via boto3).
    "bedrock": ModelSpec(
        name=os.environ.get("LARGE_MODEL", "anthropic.claude-3-5-haiku-20241022-v1:0"),
        backend="bedrock",
        model=os.environ.get("LARGE_MODEL", "anthropic.claude-3-5-haiku-20241022-v1:0"),
        price_in_per_m=float(os.environ.get("LARGE_PRICE_IN", "0.80")),
        price_out_per_m=float(os.environ.get("LARGE_PRICE_OUT", "4.00")),
        extra={"region": os.environ.get("AWS_REGION", "us-east-1")},
    ),
    # A second, larger local model via Ollama -> fully offline, still $0.
    "ollama": ModelSpec(
        name=os.environ.get("LARGE_MODEL", "qwen3.5:32b"),
        backend="ollama",
        model=os.environ.get("LARGE_MODEL", "qwen3.5:32b"),
        price_in_per_m=0.0,
        price_out_per_m=0.0,
        base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
    ),
}

LARGE_TIER_LIVE = _LARGE_PRESETS.get(_LARGE_BACKEND, _LARGE_PRESETS["openai_compatible"])


# Mock tiers used when ROUTER_MODE=mock. The large mock carries the same
# price as whatever live large tier you configured, so the cost math is real.
SMALL_TIER_MOCK = ModelSpec(name="mock-slm", backend="mock", price_in_per_m=0.0, price_out_per_m=0.0)
LARGE_TIER_MOCK = ModelSpec(
    name="mock-llm",
    backend="mock",
    price_in_per_m=LARGE_TIER_LIVE.price_in_per_m,
    price_out_per_m=LARGE_TIER_LIVE.price_out_per_m,
)


def small_tier() -> ModelSpec:
    return SMALL_TIER_MOCK if ROUTER_MODE == "mock" else SMALL_TIER_LIVE


def large_tier() -> ModelSpec:
    return LARGE_TIER_MOCK if ROUTER_MODE == "mock" else LARGE_TIER_LIVE


# ---- Harness knobs --------------------------------------------------------
EVAL_SIZE = int(os.environ.get("EVAL_SIZE", "120"))         # n
SELF_CONSISTENCY_K = int(os.environ.get("SC_K", "3"))       # samples for self-consistency
CALIBRATION_MIN_SLM_ACC = float(os.environ.get("CAL_MIN_ACC", "0.55"))  # gate floor
DEFAULT_SEED = int(os.environ.get("SEED", "7"))

# Verifier escalation threshold (0..1). Higher -> escalate more.
VERIFIER_THRESHOLD = float(os.environ.get("VERIFIER_THRESHOLD", "0.5"))
# Routing budget used to auto-pick the threshold when none is given.
DEFAULT_TARGET_RATE = float(os.environ.get("TARGET_RATE", "0.25"))

# Paths
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
OUT_DIR = os.path.join(ROOT, "out")
CACHE_PATH = os.path.join(DATA_DIR, "cache.json")
EVAL_PATH = os.path.join(DATA_DIR, "eval.jsonl")
MATRIX_PATH = os.path.join(DATA_DIR, "matrix.jsonl")

# --- Constitution override (optional) --------------------------------------
try:
    from . import from_constitution as _con  # noqa: E402

    ROUTER_MODE = _con.MODE
    DEFAULT_TARGET_RATE = _con.TARGET_RATE
    CALIBRATION_MIN_SLM_ACC = _con.CALIBRATION_MIN_SLM_ACC
    SELF_CONSISTENCY_K = _con.SELF_CONSISTENCY_K
    EVAL_SIZE = _con.EVAL_SIZE
    if _con.VERIFIER_THRESHOLD is not None:
        VERIFIER_THRESHOLD = float(_con.VERIFIER_THRESHOLD)

    def small_tier():   # noqa: F811
        return _con.small_tier()

    def large_tier():   # noqa: F811
        return _con.large_tier()
except Exception:
    pass
