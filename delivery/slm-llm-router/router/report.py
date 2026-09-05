"""Rendering: the leaderboard table and the deferral-curve chart."""
from __future__ import annotations

import os

from rich.console import Console
from rich.table import Table

from . import config
from .calibration import Calibration
from .deferral import Deferral
from .scoring import Row

console = Console()


def print_calibration(cal: Calibration) -> None:
    status = "[bold green]PASS[/]" if cal.passed else "[bold red]FAIL[/]"
    console.print(
        f"\n[bold]Calibration gate[/] ({cal.n_holdout} holdout): "
        f"SLM acc={cal.slm_accuracy:.1%}  LLM acc={cal.llm_accuracy:.1%}  "
        f"floor={cal.floor:.0%}  ->  {status}"
    )
    if not cal.passed:
        console.print("  [yellow]SLM below floor: the cascade will escalate too much to be worth it.[/]")


def print_leaderboard(rows: list[Row]) -> None:
    t = Table(title="Leaderboard (same questions, matched routing rate)", header_style="bold")
    t.add_column("strategy")
    t.add_column("accuracy", justify="right")
    t.add_column("routing rate", justify="right")
    t.add_column("savings", justify="right")
    t.add_column("$/1k queries", justify="right")
    t.add_column("note", style="dim")
    for r in rows:
        style = "bold cyan" if r.name == "cascade" else ""
        t.add_row(
            r.name,
            f"{r.accuracy:.1%}",
            f"{r.routing_rate:.1%}",
            f"{r.savings_pct:.1%}",
            f"${r.avg_cost * 1000:.4f}",
            r.note,
            style=style,
        )
    console.print(t)


def print_headline(h: dict) -> None:
    lift = h["lift_over_random"]
    color = "green" if lift > 0 else "red"
    console.print("\n[bold underline]Headline[/]")
    console.print(f"  routing rate            {h['routing_rate']:.1%}")
    console.print(f"  savings vs all-LLM      {h['savings_pct']:.1%}")
    console.print(f"  cascade accuracy        {h['cascade_accuracy']:.1%}")
    console.print(f"  random @ matched rate   {h['random_accuracy_matched']:.1%}")
    console.print(f"  [bold {color}]lift over random        {lift:+.1%}[/]")
    console.print(f"  area above random       {h['area_above_random']:+.4f}   [dim](the hard-to-fake number)[/]")


def print_stats(acc_ci, mc) -> None:
    console.print("\n[bold]Statistics (n at eval size)[/]")
    console.print(f"  cascade accuracy 95% CI: {acc_ci[0]:.1%}  [{acc_ci[1]:.1%}, {acc_ci[2]:.1%}]")
    console.print(
        f"  McNemar vs random@matched: b={mc.b} c={mc.c}  "
        f"chi2={mc.statistic}  p={mc.p_value}  -> favors [bold]{mc.better}[/]"
    )


def save_chart(d: Deferral, path: str | None = None, headline: dict | None = None) -> str:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    path = path or os.path.join(config.OUT_DIR, "deferral_curve.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=130)
    ax.plot(d.random.rates, [a * 100 for a in d.random.accs], "--", color="#8a8a8a",
            label=f"random (area={d.random.area()*100:.1f})")
    ax.plot(d.oracle.rates, [a * 100 for a in d.oracle.accs], color="#1a7f37",
            label=f"oracle (area={d.oracle.area()*100:.1f})")
    ax.plot(d.cascade.rates, [a * 100 for a in d.cascade.accs], "o-", color="#0969da",
            label=f"cascade (area={d.cascade.area()*100:.1f})")

    ax.fill_between(
        d.cascade.rates,
        [a * 100 for a in d.cascade.accs],
        __import__("numpy").interp(d.cascade.rates, d.random.rates, [a * 100 for a in d.random.accs]),
        color="#0969da", alpha=0.12,
    )

    ax.set_xlabel("routing rate (fraction sent to large model)")
    ax.set_ylabel("accuracy (%)")
    title = "Deferral curve: accuracy vs. routing rate"
    if headline:
        title += f"\narea above random = {headline['area_above_random']:+.4f}"
    ax.set_title(title)
    ax.set_xlim(0, 1)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return path
