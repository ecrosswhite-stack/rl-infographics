"""Strategies and the three controls, all replaying the answer matrix.

A strategy decides, per question, whether to escalate. It never re-calls a
model; it reads the stored small/large answers. Each returns a list of Outcome.

  cascade(threshold)  - escalate when the verifier score crosses the threshold
  all_slm             - never escalate            (quality floor)
  all_llm             - always escalate           (quality ceiling on cost)
  random_at(f)        - escalate a random fraction f   (the line to beat)
  oracle_at(f)        - escalate exactly the SLM's mistakes, within budget f
                        (the ceiling nobody can pass)
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from . import config, prices


@dataclass
class Outcome:
    id: str
    escalated: bool
    correct: bool
    cost: float


def _llm_cost(row: dict) -> float:
    return prices.token_cost(config.large_tier(), row["llm_in"], row["llm_out"])


def _outcome(row: dict, escalate: bool) -> Outcome:
    if escalate:
        return Outcome(row["id"], True, bool(row["llm_correct"]), _llm_cost(row))
    return Outcome(row["id"], False, bool(row["slm_correct"]), 0.0)  # local SLM = $0


def all_slm(matrix: list[dict]) -> list[Outcome]:
    return [_outcome(r, False) for r in matrix]


def all_llm(matrix: list[dict]) -> list[Outcome]:
    return [_outcome(r, True) for r in matrix]


def cascade(matrix: list[dict], threshold: float | None = None) -> list[Outcome]:
    thr = config.VERIFIER_THRESHOLD if threshold is None else threshold
    return [_outcome(r, r["v_score"] >= thr) for r in matrix]


def random_at(matrix: list[dict], f: float, seed: int = 0) -> list[Outcome]:
    """Escalate a random fraction f, chosen without looking at the answer."""
    n = len(matrix)
    k = round(f * n)
    idx = list(range(n))
    random.Random(seed).shuffle(idx)
    escalate = set(idx[:k])
    return [_outcome(r, i in escalate) for i, r in enumerate(matrix)]


def oracle_at(matrix: list[dict], f: float) -> list[Outcome]:
    """Escalate exactly the questions the SLM got wrong, within budget f.

    This is the best any router could do at routing rate f: spend the budget
    only on genuine SLM mistakes. Nobody can beat it, because it cheats by
    reading the ground truth.
    """
    n = len(matrix)
    budget = round(f * n)
    wrong = [i for i, r in enumerate(matrix) if not r["slm_correct"]]
    right = [i for i, r in enumerate(matrix) if r["slm_correct"]]
    # Spend the budget on SLM mistakes first; once they're exhausted, any extra
    # routing is wasted on already-correct queries (accuracy plateaus at the
    # ceiling), so the curve spans the full [0, 1] routing range.
    chosen = wrong[:budget] + right[: max(0, budget - len(wrong))]
    escalate = set(chosen)
    return [_outcome(r, i in escalate) for i, r in enumerate(matrix)]
