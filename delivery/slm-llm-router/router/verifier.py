"""The verifier: three local checks that decide whether to escalate.

You cannot know in advance which queries are hard, but you CAN look at the
answer once you have it. Every check runs locally, so the verifier itself is
free. It produces a continuous escalation score in [0, 1]; a threshold turns
that into a yes/no. Sweeping the threshold traces the deferral curve.

The three signals:
  format          - does the answer have the expected shape? (empty / wrong type)
  hedging         - does it hedge? ("not sure", "maybe", "I think"...)
  self-consistency- resample k times; disagreement means the model is unstable.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from . import config, grading, tiers
from .grading import _norm

HEDGE_PATTERNS = [
    r"\bnot (entirely )?sure\b",
    r"\bi think\b",
    r"\bmaybe\b",
    r"\bpossibly\b",
    r"\bmight be\b",
    r"\bi guess\b",
    r"\bprobably\b",
    r"\bcould be\b",
    r"\bunsure\b",
]
_HEDGE_RE = re.compile("|".join(HEDGE_PATTERNS), re.IGNORECASE)


@dataclass
class VerifierSignals:
    format_bad: float        # 0..1
    hedging: float           # 0..1
    inconsistency: float     # 0..1
    score: float             # combined escalation score 0..1

    def escalate(self, threshold: float | None = None) -> bool:
        thr = config.VERIFIER_THRESHOLD if threshold is None else threshold
        return self.score >= thr


def _format_check(kind: str, answer_text: str) -> float:
    if not answer_text.strip():
        return 1.0
    if kind in ("arithmetic", "count", "numeric"):
        return 0.0 if re.search(r"-?\d", answer_text) else 1.0
    # for classify/extract/factual, a very long answer is a bad sign
    tokens = _norm(answer_text).split()
    return 0.0 if 0 < len(tokens) <= 8 else 0.4


def _hedge_check(answer_text: str) -> float:
    return 1.0 if _HEDGE_RE.search(answer_text) else 0.0


def _consistency_check(prompt: str, meta: dict, k: int) -> float:
    if k <= 1:
        return 0.0
    samples = tiers.small_samples(prompt, meta, k)
    norms = [_norm(s.text) for s in samples]
    counts = Counter(norms)
    top = counts.most_common(1)[0][1]
    agreement = top / len(norms)
    return round(1.0 - agreement, 4)  # 0 = all agree, ->1 = all disagree


def verify(prompt: str, meta: dict, answer_text: str, k: int | None = None) -> VerifierSignals:
    kind = meta.get("kind", "factual")
    k = config.SELF_CONSISTENCY_K if k is None else k
    fmt = _format_check(kind, answer_text)
    hedge = _hedge_check(answer_text)
    incons = _consistency_check(prompt, meta, k)
    # Weighted blend spanning [0, 1]. Format problems are decisive; instability
    # and hedging each push toward escalation. Weights sum to 1 so a single
    # maxed-out signal can, on its own, carry the score into escalate range.
    score = min(1.0, 0.5 * fmt + 0.3 * hedge + 0.7 * incons)
    return VerifierSignals(fmt, hedge, incons, round(score, 4))
