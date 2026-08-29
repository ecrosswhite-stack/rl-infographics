"""The deferral curve: accuracy as a function of routing rate.

This is the deliverable. For each reference we trace accuracy vs. the fraction
of queries sent to the large model:

  random  - a straight line from the all-SLM floor to the all-LLM ceiling
  oracle  - escalate SLM mistakes first: the concave ceiling nobody can pass
  cascade - sweep the verifier threshold; each threshold is one (rate, acc) point

A router with real judgement bows ABOVE the random line. The gap between the
cascade curve and the random line, integrated over routing rate, is what the
router actually bought. Moving your threshold only slides you ALONG the curve.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import strategies
from .ledger import summarize


@dataclass
class Curve:
    name: str
    rates: list[float]
    accs: list[float]

    def area(self) -> float:
        if len(self.rates) < 2:
            return 0.0
        order = np.argsort(self.rates)
        x = np.array(self.rates)[order]
        y = np.array(self.accs)[order]
        return float(np.trapezoid(y, x))


@dataclass
class Deferral:
    random: Curve
    oracle: Curve
    cascade: Curve
    cascade_points: list[tuple[float, float, float]] = field(default_factory=list)  # (thr, rate, acc)

    def area_above_random(self) -> float:
        """Integral of (cascade - random) over the routing rates the cascade
        actually reaches. Positive means the cascade beat the coin flip."""
        rnd = self.random
        pts = sorted(zip(self.cascade.rates, self.cascade.accs))
        if len(pts) < 2:
            return 0.0
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        base = np.interp(xs, rnd.rates, rnd.accs)
        return float(np.trapezoid(np.array(ys) - base, xs))


def _acc(outcomes) -> float:
    return summarize(outcomes).accuracy


def random_curve(matrix, steps: int = 21, seed: int = 7) -> Curve:
    rates, accs = [], []
    for i in range(steps):
        f = i / (steps - 1)
        # average a few seeds to smooth the coin flip
        vals = [_acc(strategies.random_at(matrix, f, seed=seed + s)) for s in range(5)]
        rates.append(f)
        accs.append(sum(vals) / len(vals))
    return Curve("random", rates, accs)


def oracle_curve(matrix, steps: int = 21) -> Curve:
    rates, accs = [], []
    for i in range(steps):
        f = i / (steps - 1)
        out = strategies.oracle_at(matrix, f)
        led = summarize(out)
        rates.append(led.routing_rate)
        accs.append(led.accuracy)
    return Curve("oracle", rates, accs)


def cascade_curve(matrix, thresholds: list[float] | None = None) -> tuple[Curve, list]:
    if thresholds is None:
        thresholds = [round(t, 3) for t in np.linspace(0.0, 1.0001, 26)]
    seen = {}
    points = []
    for thr in thresholds:
        out = strategies.cascade(matrix, threshold=thr)
        led = summarize(out)
        points.append((thr, led.routing_rate, led.accuracy))
        # keep best accuracy seen at each routing rate (deduplicate the sweep)
        seen[round(led.routing_rate, 4)] = max(seen.get(round(led.routing_rate, 4), 0.0), led.accuracy)
    rates = sorted(seen)
    accs = [seen[r] for r in rates]
    return Curve("cascade", rates, accs), points


def compute(matrix, steps: int = 21, seed: int = 7) -> Deferral:
    rnd = random_curve(matrix, steps=steps, seed=seed)
    ora = oracle_curve(matrix, steps=steps)
    cas, pts = cascade_curve(matrix)
    return Deferral(random=rnd, oracle=ora, cascade=cas, cascade_points=pts)
