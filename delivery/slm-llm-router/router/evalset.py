"""The eval set: checkable questions with ground truth and a difficulty score.

Every question is judge-free gradable (see grading.py). Difficulty drives how
often a weak model gets it right; it is metadata for honest simulation and for
sorting the oracle, never shown to the models.

The set is generated deterministically so n=120 is reproducible and self
contained. Swap in your own JSONL (same schema) to grade real traffic.
"""
from __future__ import annotations

import json
import os
import random

from .config import EVAL_PATH


def _q(id, kind, prompt, answer, difficulty, distractor=""):
    return {
        "id": id,
        "kind": kind,
        "prompt": prompt,
        "answer": str(answer),
        "difficulty": round(float(difficulty), 3),
        "distractor": str(distractor),
    }


def generate(n: int, seed: int = 7) -> list[dict]:
    r = random.Random(seed)
    out: list[dict] = []
    i = 0

    def add(q):
        nonlocal i
        out.append(q)
        i += 1

    while len(out) < n:
        pick = r.random()
        if pick < 0.30:  # easy arithmetic
            a, b = r.randint(2, 99), r.randint(2, 99)
            add(_q(f"ari{i}", "arithmetic", f"What is {a} + {b}? Answer with just the number.", a + b, 0.15))
        elif pick < 0.45:  # harder arithmetic (multi-step)
            a, b, c = r.randint(3, 40), r.randint(3, 40), r.randint(2, 9)
            add(_q(f"ari{i}", "arithmetic", f"Compute ({a} + {b}) * {c}. Answer with just the number.", (a + b) * c, 0.7))
        elif pick < 0.60:  # sentiment classify (easy)
            pos = r.random() < 0.5
            txt = r.choice(["I love this product", "Absolutely fantastic experience", "This made my day"]) if pos \
                else r.choice(["This is terrible", "Worst purchase ever", "I hate it"])
            ans = "positive" if pos else "negative"
            add(_q(f"cls{i}", "classify", f"Sentiment (positive or negative): '{txt}'. One word.", ans, 0.2,
                   distractor="negative" if pos else "positive"))
        elif pick < 0.72:  # extraction (easy-med)
            num = r.randint(1000, 9999)
            add(_q(f"ext{i}", "extract", f"Extract the order number: 'Order #{num} has shipped today.' Just the number.",
                   num, 0.35))
        elif pick < 0.85:  # unit conversion / counting (med)
            wk = r.randint(2, 6)
            add(_q(f"cnt{i}", "count", f"How many days are in {wk} weeks? Just the number.", wk * 7, 0.45))
        else:  # trickier factual / boolean (hard)
            n1, n2 = r.randint(10, 99), r.randint(10, 99)
            bigger = max(n1, n2)
            add(_q(f"fac{i}", "factual", f"Which is larger, {n1} or {n2}? Answer with the number itself.",
                   bigger, 0.8, distractor=str(min(n1, n2))))
    return out[:n]


def load_or_build(n: int, seed: int = 7, path: str = EVAL_PATH) -> list[dict]:
    if os.path.exists(path):
        with open(path) as f:
            rows = [json.loads(line) for line in f if line.strip()]
        if len(rows) >= n:
            return rows[:n]
    rows = generate(n, seed)
    save(rows, path)
    return rows


def save(rows: list[dict], path: str = EVAL_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
