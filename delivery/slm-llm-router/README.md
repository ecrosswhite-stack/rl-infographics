# SLM + LLM Cascade Router (that proves its own savings)

A small model runs on your laptop and answers every query for **$0**. A local
verifier looks at each answer and decides whether to trust it. Only distrusted
answers escalate to an expensive hosted model. Then — the part almost nobody
ships — a **harness proves whether that routing was actually worth it**, by
measuring accuracy at a *matched routing rate* against random and oracle
controls, and drawing a deferral curve you can defend.

```
query -> small model (local, $0) -> verifier (3 local checks) --accept--> answer
                                            |
                                        escalate
                                            v
                                   large model (paid) -> answer
                              every outcome -> cost+accuracy ledger -> deferral curve
```

## The trap this is built around

Because the small tier is free, `savings% = 1 − (fraction sent to the large model)`.
That number says nothing about whether your product still works — a coin-flip
router "saves" exactly as much as a brilliant one. So the honest question is not
*"how much did I save?"* but **"at the same routing rate, is my router more
accurate than random?"** This harness answers that with three references:

| reference    | what it is                          | what it tells you        |
|--------------|-------------------------------------|--------------------------|
| **all-SLM**  | never escalate                      | the quality floor        |
| **random @ f** | escalate a random fraction f      | the line you must beat   |
| **oracle @ f** | escalate exactly the SLM's mistakes | the ceiling nobody passes |

Plot accuracy vs. routing rate and random traces a straight line between floor
and ceiling. A router with real judgement **bows above** that line. Moving your
threshold only slides you *along* the curve — it never lifts it off the line.
That gap (the shaded area, `area_above_random`) is the hard-to-fake deliverable.

## Do you have to use Groq? No.

Groq is only the *large tier* in the original write-up — just an OpenAI-compatible
endpoint with a per-token price. The large tier here sits behind a pluggable
adapter (`router/providers.py`). Pick any of:

| `LARGE_BACKEND`     | use for                                            |
|---------------------|----------------------------------------------------|
| `openai_compatible` | **Groq**, OpenAI, Together, OpenRouter, vLLM, LM Studio |
| `anthropic`         | **Claude** (Haiku as cheap tier, Sonnet/Opus as frontier) |
| `bedrock`           | Claude & others on **AWS** (uses your AWS creds)   |
| `ollama`            | a second, larger **local** model → fully offline, still $0 |

The small tier is Ollama (local) or `mock`. Set everything in `.env`
(see `.env.example`). Change **one config block** to swap providers; nothing
else in the codebase names a vendor.

## Offline by default

`ROUTER_MODE=mock` (the default) simulates both tiers deterministically — zero
network, no API keys, no Ollama — so the entire harness (verifier, matrix,
deferral curve, statistics, chart) runs anywhere. The mock large tier still
carries the real large-model price, so the cost math stays honest. Flip to
`ROUTER_MODE=live` when you're ready to run against real models.

## Quickstart

```bash
pip install -r requirements.txt        # numpy, matplotlib, rich, python-dotenv
python -m router.cli all               # offline: build matrix -> calibrate -> run -> chart
open out/deferral_curve.png
```

Going live:

```bash
cp .env.example .env                   # set ROUTER_MODE=live, pick LARGE_BACKEND, add keys
ollama pull qwen3.5:4b                 # small tier on your machine
ROUTER_MODE=live python -m router.cli all
```

## Commands

```
python -m router.cli eval           # (re)generate the eval set (--n 120)
python -m router.cli build-matrix   # run each question through both tiers + verifier, cache it
python -m router.cli calibrate      # check the SLM clears the accuracy floor
python -m router.cli run            # leaderboard + headline + statistics (auto-picks threshold)
python -m router.cli chart          # write out/deferral_curve.png
python -m router.cli all            # the whole pipeline
```

Useful flags: `--n`, `--target-rate 0.25` (routing budget → threshold),
`--threshold 0.4` (pin it), `--seed`, `--json`.

## How grading stays honest (no judge)

Every eval question has a checkable ground truth; grading is deterministic
normalization + match (`router/grading.py`). No LLM ever judges another — that
would be circular and cost money. This works identically for mock and real
outputs. Bring your own `data/eval.jsonl` (same schema) to grade real traffic.

## What the numbers mean

`run` prints, at a matched routing rate:
- **cascade accuracy** vs **random @ matched rate** → the lift your verifier bought
- **savings %** = fraction kept local
- a bootstrap **95% CI** on cascade accuracy and a paired **McNemar** test vs random
- **area above random** — the whole-curve number a threshold tweak can't fake

## Layout

```
router/
  config.py       tiers, prices, thresholds  <- swap providers here
  prices.py       cost math (the only place dollars are computed)
  providers.py    mock / ollama / openai_compatible / anthropic / bedrock
  cache.py        JSON disk cache so real calls happen at most once
  tiers.py        small/large wrappers + self-consistency sampling
  grading.py      judge-free deterministic grading
  evalset.py      reproducible checkable eval set (n=120)
  verifier.py     three local checks -> escalation score
  matrix.py       precomputed answer matrix (strategies replay it)
  strategies.py   cascade / all-slm / all-llm / random@f / oracle@f
  calibration.py  accuracy-floor gate + threshold picker
  deferral.py     the deferral curve + area above random
  stats.py        bootstrap CI + McNemar
  ledger.py       cost + accuracy aggregation
  scoring.py      leaderboard + headline
  report.py       rich tables + matplotlib chart
  cli.py          command line
tests/test_smoke.py   offline tests
```

## License

MIT — do what you like.
