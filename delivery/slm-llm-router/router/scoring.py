"""Scoring and the leaderboard.

Every strategy is scored on the same questions: accuracy, routing rate,
savings, average cost. The cascade is additionally credited with the area it
bows above the random line - the one number that cannot be faked by moving a
threshold.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import ledger, strategies
from .config import VERIFIER_THRESHOLD
from .deferral import Deferral


@dataclass
class Row:
    name: str
    accuracy: float
    routing_rate: float
    savings_pct: float
    avg_cost: float
    note: str = ""


def leaderboard(matrix: list[dict], deferral: Deferral, threshold: float = VERIFIER_THRESHOLD) -> list[Row]:
    cas = ledger.summarize(strategies.cascade(matrix, threshold))
    rows = [
        Row("cascade", cas.accuracy, cas.routing_rate, cas.savings_pct, cas.avg_cost,
            note=f"threshold={threshold:g}"),
    ]

    # random and oracle evaluated AT THE CASCADE'S routing rate (matched rate)
    f = cas.routing_rate
    rnd = ledger.summarize(strategies.random_at(matrix, f, seed=7))
    ora = ledger.summarize(strategies.oracle_at(matrix, f))
    rows.append(Row("random @ matched", rnd.accuracy, rnd.routing_rate, rnd.savings_pct, rnd.avg_cost,
                    note="the line to beat"))
    rows.append(Row("oracle @ matched", ora.accuracy, ora.routing_rate, ora.savings_pct, ora.avg_cost,
                    note="ceiling nobody passes"))

    all_slm = ledger.summarize(strategies.all_slm(matrix))
    all_llm = ledger.summarize(strategies.all_llm(matrix))
    rows.append(Row("all-SLM", all_slm.accuracy, 0.0, 1.0, 0.0, note="quality floor"))
    rows.append(Row("all-LLM", all_llm.accuracy, 1.0, 0.0, all_llm.avg_cost, note="quality ceiling"))
    return rows


def headline(matrix, deferral: Deferral, threshold: float = VERIFIER_THRESHOLD) -> dict:
    cas = ledger.summarize(strategies.cascade(matrix, threshold))
    f = cas.routing_rate
    rnd = ledger.summarize(strategies.random_at(matrix, f, seed=7))
    return {
        "cascade_accuracy": cas.accuracy,
        "random_accuracy_matched": rnd.accuracy,
        "lift_over_random": round(cas.accuracy - rnd.accuracy, 4),
        "routing_rate": f,
        "savings_pct": cas.savings_pct,
        "area_above_random": round(deferral.area_above_random(), 5),
    }
