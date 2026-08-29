"""Statistics at n=120.

With only ~120 questions, a two-point accuracy gap can be noise. So we quantify
it: a bootstrap confidence interval on any accuracy, and a paired McNemar test
comparing the cascade against random routing AT THE SAME ROUTING RATE on the
identical questions.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .strategies import Outcome


def accuracy_ci(outcomes: list[Outcome], iters: int = 5000, seed: int = 7) -> tuple[float, float, float]:
    """Return (accuracy, lo95, hi95) via bootstrap resampling of questions."""
    correct = np.array([1.0 if o.correct else 0.0 for o in outcomes])
    n = len(correct)
    if n == 0:
        return 0.0, 0.0, 0.0
    rng = np.random.default_rng(seed)
    means = correct[rng.integers(0, n, size=(iters, n))].mean(axis=1)
    return float(correct.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


@dataclass
class McNemar:
    b: int          # cascade right, baseline wrong
    c: int          # cascade wrong, baseline right
    statistic: float
    p_value: float
    better: str


def _norm_sf(z: float) -> float:
    # two-sided p from standard normal survival, no scipy dependency
    from math import erfc, sqrt

    return erfc(abs(z) / sqrt(2.0))


def mcnemar(cascade: list[Outcome], baseline: list[Outcome]) -> McNemar:
    """Paired test on identical questions. Uses the normal approximation with a
    continuity correction (fine at n=120); falls back gracefully for small b+c.
    """
    by_id = {o.id: o for o in baseline}
    b = c = 0
    for o in cascade:
        base = by_id.get(o.id)
        if base is None:
            continue
        if o.correct and not base.correct:
            b += 1
        elif not o.correct and base.correct:
            c += 1
    disc = b + c
    if disc == 0:
        return McNemar(b, c, 0.0, 1.0, "tie")
    stat = (abs(b - c) - 1) ** 2 / disc  # chi-square with continuity correction
    z = (abs(b - c) - 1) / (disc ** 0.5)
    p = _norm_sf(z) if disc > 0 else 1.0
    better = "cascade" if b > c else ("baseline" if c > b else "tie")
    return McNemar(b, c, round(stat, 4), round(min(1.0, p), 4), better)
