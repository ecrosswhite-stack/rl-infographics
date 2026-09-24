# Wiring the router to the constitution

Two small changes make the SLM+LLM router read its tiers from the one source of truth.

### 1. Copy the adapter into the router package
```
cp rl-stack/router_adapter/from_constitution.py  slm-llm-router/router/from_constitution.py
```

### 2. Make the constitution config available to the router
Compile it, then point the router at the JSON (or fetch it live from the MCP):
```
python3 rl-stack/compilers/compile.py
export RL_ROUTER_CONFIG=$PWD/rl-stack/out/router_config.json
```

### 3. Have `router/config.py` prefer the constitution when present
At the very end of `slm-llm-router/router/config.py`, append:

```python
# --- Constitution override (optional) --------------------------------------
# If a compiled constitution config is available, source tiers + routing knobs
# from it so governance rules and model choice stay one artifact.
try:
    from . import from_constitution as _con  # noqa: E402

    ROUTER_MODE = _con.MODE
    DEFAULT_TARGET_RATE = _con.TARGET_RATE
    CALIBRATION_MIN_SLM_ACC = _con.CALIBRATION_MIN_SLM_ACC
    SELF_CONSISTENCY_K = _con.SELF_CONSISTENCY_K
    EVAL_SIZE = _con.EVAL_SIZE
    if _con.VERIFIER_THRESHOLD is not None:
        VERIFIER_THRESHOLD = float(_con.VERIFIER_THRESHOLD)

    def small_tier():   # noqa: F811  (override module-level definition)
        return _con.small_tier()

    def large_tier():   # noqa: F811
        return _con.large_tier()
except Exception:
    pass  # no constitution present -> router uses its own .env/config as before
```

That's it. `python -m router.cli all` now runs with tiers chosen by the
constitution. To switch the large tier (e.g. Groq -> Claude -> Kimi), copy a
`large_presets` entry into `router.tiers.large` in the YAML, recompile, rerun —
no router code changes.

### Optional: inject governed rules into every tier prompt
`_con.INJECT` carries the compiled rule preamble. Prepend it to each tier's
prompt in `router/providers.py` so both the local SLM and the hosted LLM answer
under the same governance.
```python
from .from_constitution import INJECT
prompt = INJECT + "\n\n" + prompt   # inside complete() for live backends
```
