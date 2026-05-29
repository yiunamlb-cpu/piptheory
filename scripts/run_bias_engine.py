"""Run the full bias engine. Layer 1 → 2 → 3 → 4 → 5 against live data.

Output: bias_cards/YYYY-MM-DD/ with markdown bias cards per instrument.

Usage:
    python scripts/run_bias_engine.py              # full pipeline, conviction-filtered Layer 4
    python scripts/run_bias_engine.py --inst EURUSD AUDUSD GC   # only those at Layer 4
    python scripts/run_bias_engine.py --no-council              # Layer 1-3 + index only
    python scripts/run_bias_engine.py --date 2026-05-28        # backfill a past date
"""
from __future__ import annotations

import argparse
import sys

from rich.console import Console
from rich.panel import Panel

from src.config import settings
from src.llm import OpenRouterClient
from src.orchestration import BiasEngine

console = Console()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--inst",
        nargs="*",
        default=None,
        help="Override Layer 4 council instruments (default: conviction-filtered).",
    )
    p.add_argument(
        "--no-council",
        action="store_true",
        help="Skip Layer 4 + Layer 5. Useful for fast iteration on Layer 1-3.",
    )
    p.add_argument(
        "--date",
        default=None,
        help="Override run date (YYYY-MM-DD) for backfilling past days. Default: today.",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    console.print(Panel.fit(
        f"[cyan]Model:[/cyan] {settings.model_cheap}\n"
        f"[cyan]Daily budget:[/cyan] ${settings.daily_budget_usd:.2f}\n"
        f"[cyan]Date:[/cyan] {args.date or 'today'}\n"
        f"[cyan]Council mode:[/cyan] " +
        ("disabled (Layer 1-3 only)" if args.no_council else
         f"explicit ({args.inst})" if args.inst else "conviction-filtered"),
        title="Bias engine — full pipeline run",
    ))

    client = OpenRouterClient()
    engine = BiasEngine(client=client)

    council = [] if args.no_council else (args.inst if args.inst else None)
    result = engine.run(council_instruments=council, override_date=args.date)

    out_dir = engine.output_dir(result.run_date)
    console.rule("[green]Run complete[/green]")
    console.print(f"[green]Output dir:[/green] {out_dir}")
    console.print(f"[green]Council instruments:[/green] "
                  f"{list(result.layer4_council) or '(none)'}")
    console.print(f"[green]Total spent today:[/green] ${result.total_cost_usd:.4f}")
    console.print(f"[green]Budget remaining:[/green] ${client.budget.remaining_today():.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
