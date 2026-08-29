"""Cost + accuracy ledger. Turns a list of Outcomes into the numbers you defend.

savings% is defined exactly as in the write-up: since the small tier is local
and free, savings is 1 minus the fraction of queries sent to the large model.
That is a property of the routing rate, which is why accuracy at a MATCHED
routing rate (not savings) is the real measure of a router.
"""
from __future__ import annotations

from dataclasses import dataclass

from .strategies import Outcome


@dataclass
class Ledger:
    n: int
    escalated: int
    correct: int
    total_cost: float

    @property
    def routing_rate(self) -> float:
        return self.escalated / self.n if self.n else 0.0

    @property
    def accuracy(self) -> float:
        return self.correct / self.n if self.n else 0.0

    @property
    def savings_pct(self) -> float:
        # vs. all-LLM baseline: local SLM is free, so savings == fraction kept local.
        return 1.0 - self.routing_rate

    @property
    def avg_cost(self) -> float:
        return self.total_cost / self.n if self.n else 0.0


def summarize(outcomes: list[Outcome]) -> Ledger:
    n = len(outcomes)
    return Ledger(
        n=n,
        escalated=sum(1 for o in outcomes if o.escalated),
        correct=sum(1 for o in outcomes if o.correct),
        total_cost=sum(o.cost for o in outcomes),
    )
