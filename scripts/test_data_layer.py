"""Verify the data layer: FRED snapshot + COT positioning summary.

Usage:
    python scripts/test_data_layer.py
"""
from __future__ import annotations

import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.data import CotClient, FredClient

console = Console()


def test_fred() -> None:
    console.rule("[cyan]FRED — macro snapshot[/cyan]")
    fred = FredClient()
    # Test individual fetch + a small snapshot
    date, value = fred.latest("cpi_headline")
    console.print(f"[green]OK[/green] CPI headline (CPIAUCSL): latest {value:.2f} on {date.date()}")
    date, value = fred.latest("ust_10y")
    console.print(f"[green]OK[/green] UST 10Y (DGS10): latest {value:.3f}% on {date.date()}")
    date, value = fred.latest("ffr_target_upper")
    console.print(f"[green]OK[/green] Fed funds target upper (DFEDTARU): latest {value:.2f}% on {date.date()}")

    # Snapshot of inflation group
    snap = fred.snapshot(["cpi_headline", "cpi_core", "pce_core", "breakeven_5y5y", "ust_10y"])
    console.print()
    table = Table(title="Inflation + rates snapshot")
    for col in snap.columns:
        table.add_column(col)
    for _, row in snap.iterrows():
        table.add_row(*[str(v) for v in row.tolist()])
    console.print(table)


def test_cot() -> None:
    console.rule("[cyan]COT — positioning summary[/cyan]")
    cot = CotClient(lookback_years=3)
    table = Table(title="COT summary (3-year lookback)")
    cols = ["instrument", "status", "report_date", "data_age", "net", "pct_3y", "trend_4w", "extreme_6w"]
    for c in cols:
        table.add_column(c)
    for instrument in ["EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "GC", "CL"]:
        try:
            s = cot.summary(instrument)
        except Exception as e:
            table.add_row(instrument, "error", "", "", "", "", "", "")
            console.print(f"[red]Error for {instrument}: {e}[/red]")
            continue
        if s.get("status") == "ok":
            table.add_row(
                instrument,
                "ok",
                str(s.get("report_date") or ""),
                f"{s.get('data_age_days', 0)}d",
                f"{s['net_position']:,}",
                f"{s['percentile_3yr']:.0f}",
                f"{s['trend_4week']:+,}",
                f"{s['weeks_at_extreme_in_last_6']}/6",
            )
        else:
            table.add_row(instrument, str(s.get("status")), "", "", "", "", "", "")
    console.print(table)


def main() -> int:
    console.print(Panel.fit("Testing FRED + COT data layer", title="data layer test"))
    try:
        test_fred()
    except Exception as e:
        console.print(f"[red]FRED test failed: {e}[/red]")
    try:
        test_cot()
    except Exception as e:
        console.print(f"[red]COT test failed: {e}[/red]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
