"""The calibration gate.

Before trusting the cascade, confirm the small tier clears a minimum accuracy
on its own. If the SLM is below the floor, no verifier can save you: you would
escalate everything and pay full price. The gate is a go/no-go check, run on a
holdout split so it does not peek at the questions used to tune the threshold.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import config


@dataclass
class Calibration:
    slm_accuracy: float
    llm_accuracy: float
    floor: float
    passed: bool
    n_holdout: int


def pick_threshold(matrix: list[dict], target_rate: float = 0.25) -> float:
    """Choose the verifier threshold whose routing rate is closest to a budget.

    This is how you set the dial honestly: pick the routing rate you can afford,
    then let the data choose the threshold that hits it. The accuracy you then
    report is compared against random AT THAT SAME rate.
    """
    import numpy as np

    from . import strategies
    from .ledger import summarize

    thresholds = [round(t, 3) for t in np.linspace(0.0, 1.0001, 41)]
    best_thr, best_gap = config.VERIFIER_THRESHOLD, 1e9
    for thr in thresholds:
        rate = summarize(strategies.cascade(matrix, threshold=thr)).routing_rate
        gap = abs(rate - target_rate)
        if gap < best_gap:
            best_gap, best_thr = gap, thr
    return best_thr


def check(matrix: list[dict], holdout_frac: float = 0.3, floor: float | None = None) -> Calibration:
    floor = config.CALIBRATION_MIN_SLM_ACC if floor is None else floor
    n = len(matrix)
    cut = int(n * (1 - holdout_frac))
    holdout = matrix[cut:] or matrix
    slm = sum(1 for r in holdout if r["slm_correct"]) / len(holdout)
    llm = sum(1 for r in holdout if r["llm_correct"]) / len(holdout)
    return Calibration(
        slm_accuracy=round(slm, 4),
        llm_accuracy=round(llm, 4),
        floor=floor,
        passed=slm >= floor,
        n_holdout=len(holdout),
    )
