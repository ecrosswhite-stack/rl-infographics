"""Offline smoke tests. Run: python -m pytest -q  (or python tests/test_smoke.py)"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from router import (  # noqa: E402
    calibration,
    deferral as deferral_mod,
    evalset,
    grading,
    matrix as matrix_mod,
    scoring,
    stats,
    strategies,
)


def _matrix(n=120):
    rows = evalset.generate(n, seed=7)
    return matrix_mod.build(rows, show_progress=False)


def test_grading_judge_free():
    assert grading.grade("arithmetic", "The answer is 115.", "115")
    assert grading.grade("classify", "positive", "positive")
    assert not grading.grade("arithmetic", "116", "115")


def test_matrix_shape():
    mat = _matrix(60)
    assert len(mat) == 60
    for r in mat:
        assert 0.0 <= r["v_score"] <= 1.0
        assert isinstance(r["slm_correct"], bool)


def test_savings_identity():
    mat = _matrix()
    from router.ledger import summarize

    cas = summarize(strategies.cascade(mat))
    assert abs(cas.savings_pct - (1 - cas.routing_rate)) < 1e-9


def test_cascade_beats_random_at_matched_rate():
    mat = _matrix()
    d = deferral_mod.compute(mat)
    thr = calibration.pick_threshold(mat, target_rate=0.25)
    h = scoring.headline(mat, d, threshold=thr)
    # a real verifier should not be worse than a coin flip at the same rate,
    # and the whole-curve area above random must be positive
    assert h["routing_rate"] > 0.0
    assert h["lift_over_random"] >= 0.0
    assert h["area_above_random"] > 0.0


def test_oracle_is_ceiling():
    mat = _matrix()
    from router.ledger import summarize

    for f in (0.1, 0.3, 0.5):
        ora = summarize(strategies.oracle_at(mat, f)).accuracy
        rnd = summarize(strategies.random_at(mat, f, seed=7)).accuracy
        assert ora >= rnd - 1e-9


def test_stats_run():
    mat = _matrix()
    cas = strategies.cascade(mat)
    ci = stats.accuracy_ci(cas)
    assert ci[1] <= ci[0] <= ci[2]


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("ok", name)
    print("all smoke tests passed")
