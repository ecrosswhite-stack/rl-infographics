"""Grading without a judge.

We never ask a model whether an answer is right. Every eval question has a
checkable ground truth, and grading is deterministic normalization + match.
This is what keeps the whole pipeline honest and free: no LLM-judge, no cost,
no circularity. It works identically for mock and real model outputs.
"""
from __future__ import annotations

import re


def _norm(s: str) -> str:
    s = s.strip().lower()
    # drop trailing hedges/parentheticals the model may add
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"[^a-z0-9\.\- ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _first_number(s: str):
    m = re.search(r"-?\d+(?:\.\d+)?", s.replace(",", ""))
    return m.group(0) if m else None


def grade(kind: str, prediction: str, truth: str) -> bool:
    """Return True if `prediction` matches `truth` for a question of `kind`."""
    p, t = _norm(prediction), _norm(truth)
    if kind in ("arithmetic", "count", "numeric"):
        pn, tn = _first_number(p), _first_number(t)
        if pn is None or tn is None:
            return False
        try:
            return abs(float(pn) - float(tn)) < 1e-6
        except ValueError:
            return False
    if kind in ("classify", "extract", "factual", "boolean"):
        if p == t:
            return True
        # accept the truth appearing as a standalone token in the prediction
        return bool(re.search(rf"\b{re.escape(t)}\b", p))
    return p == t
