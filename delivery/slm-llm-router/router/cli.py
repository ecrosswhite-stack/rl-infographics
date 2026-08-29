"""Command line for the cascade router harness.

Commands:
  eval          regenerate the eval set (n questions)
  build-matrix  run each question through both tiers + verifier, store the matrix
  calibrate     check the SLM clears the accuracy floor
  run           score the leaderboard + headline + stats at the current threshold
  chart         write the deferral-curve PNG
  all           build-matrix -> calibrate -> run -> chart  (the whole thing)

Global:
  ROUTER_MODE=mock (default, offline) or ROUTER_MODE=live
  --n, --threshold, --seed override config.
"""
from __future__ import annotations

import argparse
import json

from . import (
    calibration,
    config,
    deferral as deferral_mod,
    evalset,
    matrix as matrix_mod,
    report,
    scoring,
    stats,
    strategies,
)


def _mode_banner() -> None:
    s, l = config.small_tier(), config.large_tier()
    report.console.print(
        f"[dim]mode=[bold]{config.ROUTER_MODE}[/bold]  "
        f"small=[bold]{s.name}[/]({s.backend})  "
        f"large=[bold]{l.name}[/]({l.backend}) "
        f"${l.price_in_per_m:g}/${l.price_out_per_m:g} per 1M[/]"
    )


def cmd_eval(args):
    rows = evalset.generate(args.n, seed=args.seed)
    evalset.save(rows)
    report.console.print(f"wrote {len(rows)} questions -> {config.EVAL_PATH}")


def cmd_build_matrix(args):
    _mode_banner()
    rows = evalset.load_or_build(args.n, seed=args.seed)
    mat = matrix_mod.build(rows, k=args.sc_k)
    matrix_mod.save(mat)
    report.console.print(f"wrote answer matrix ({len(mat)} rows) -> {config.MATRIX_PATH}")


def cmd_calibrate(args):
    mat = matrix_mod.load()
    cal = calibration.check(mat)
    report.print_calibration(cal)
    return cal


def _resolve_threshold(args, mat) -> float:
    if args.threshold is not None:
        return args.threshold
    thr = calibration.pick_threshold(mat, target_rate=args.target_rate)
    report.console.print(
        f"[dim]auto-picked threshold={thr:g} for target routing rate ~{args.target_rate:.0%}[/]"
    )
    return thr


def cmd_run(args):
    _mode_banner()
    mat = matrix_mod.load()
    cal = calibration.check(mat)
    report.print_calibration(cal)

    thr = _resolve_threshold(args, mat)
    d = deferral_mod.compute(mat, seed=args.seed)
    rows = scoring.leaderboard(mat, d, threshold=thr)
    report.print_leaderboard(rows)

    h = scoring.headline(mat, d, threshold=thr)
    report.print_headline(h)

    cas = strategies.cascade(mat, thr)
    rnd = strategies.random_at(mat, sum(1 for o in cas if o.escalated) / len(cas), seed=7)
    acc_ci = stats.accuracy_ci(cas)
    mc = stats.mcnemar(cas, rnd)
    report.print_stats(acc_ci, mc)

    if args.json:
        print(json.dumps({"headline": h, "calibration": cal.__dict__,
                          "accuracy_ci": acc_ci, "mcnemar": mc.__dict__}, indent=2))
    return h


def cmd_chart(args):
    mat = matrix_mod.load()
    thr = _resolve_threshold(args, mat)
    d = deferral_mod.compute(mat, seed=args.seed)
    h = scoring.headline(mat, d, threshold=thr)
    path = report.save_chart(d, headline=h)
    report.console.print(f"wrote chart -> {path}")


def cmd_all(args):
    cmd_build_matrix(args)
    cmd_run(args)
    cmd_chart(args)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="router", description="SLM+LLM cascade router harness")
    p.add_argument("--n", type=int, default=config.EVAL_SIZE)
    p.add_argument("--threshold", type=float, default=None,
                   help="verifier escalation threshold; if omitted, auto-picked from --target-rate")
    p.add_argument("--target-rate", type=float, default=config.DEFAULT_TARGET_RATE,
                   help="routing budget used to auto-pick the threshold (default 0.25)")
    p.add_argument("--seed", type=int, default=config.DEFAULT_SEED)
    p.add_argument("--sc-k", type=int, default=config.SELF_CONSISTENCY_K)
    p.add_argument("--json", action="store_true", help="also emit machine-readable JSON")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn in [
        ("eval", cmd_eval),
        ("build-matrix", cmd_build_matrix),
        ("calibrate", cmd_calibrate),
        ("run", cmd_run),
        ("chart", cmd_chart),
        ("all", cmd_all),
    ]:
        sp = sub.add_parser(name)
        sp.set_defaults(func=fn)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
