"""The answer matrix.

For every eval question we compute, once:
  - the small-tier answer, its token counts, and whether it is correct
  - the verifier's signals and escalation score for that answer
  - the large-tier answer, its token counts, and whether it is correct

Every strategy and control then REPLAYS these stored rows instead of calling
models again. That is what makes random@f and oracle@f free and fair: they see
the exact same answers the cascade saw.
"""
from __future__ import annotations

import json
import os

from rich.progress import track

from . import config, grading, tiers, verifier
from .config import MATRIX_PATH


def build(eval_rows: list[dict], k: int | None = None, show_progress: bool = True) -> list[dict]:
    rows = []
    iterator = track(eval_rows, description="Building answer matrix") if show_progress else eval_rows
    for q in iterator:
        meta = q
        prompt = q["prompt"]
        kind = q["kind"]
        truth = q["answer"]

        s = tiers.ask_small(prompt, meta)
        s_correct = grading.grade(kind, s.text, truth)
        sig = verifier.verify(prompt, meta, s.text, k=k)

        l = tiers.ask_large(prompt, meta)
        l_correct = grading.grade(kind, l.text, truth)

        rows.append(
            {
                "id": q["id"],
                "kind": kind,
                "difficulty": q["difficulty"],
                "slm_text": s.text,
                "slm_in": s.input_tokens,
                "slm_out": s.output_tokens,
                "slm_correct": s_correct,
                "llm_text": l.text,
                "llm_in": l.input_tokens,
                "llm_out": l.output_tokens,
                "llm_correct": l_correct,
                "v_format": sig.format_bad,
                "v_hedge": sig.hedging,
                "v_inconsistency": sig.inconsistency,
                "v_score": sig.score,
            }
        )
    return rows


def save(rows: list[dict], path: str = MATRIX_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def load(path: str = MATRIX_PATH) -> list[dict]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"no matrix at {path}; run `build-matrix` first")
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]
