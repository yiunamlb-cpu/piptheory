"""Run Positioning Analyst against LIVE COT data. First real-data agent run.

Pulls today's COT summary for all relevant watchlist instruments, hands it to
the Positioning Analyst agent, prints the output. If the output is sensibly
structured per positioning.md, we have green light for the full pipeline.

Usage:
    python scripts/run_positioning_real.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from src.agents import run_agent
from src.data import CotClient
from src.llm import OpenRouterClient

console = Console()

# Instruments with COT coverage (DXY uses ICE futures, often unavailable in CFTC TFF)
COT_INSTRUMENTS = ["EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "GC", "CL"]


def build_user_message(summaries: list[dict]) -> str:
    today = datetime.now().date().isoformat()
    return (
        f"# COT Data — Live Pull, {today}\n\n"
        f"Below is structured COT positioning data for the watchlist instruments, "
        f"freshly pulled from CFTC. Apply the methodology in your prompt "
        f"(positioning.md) to produce a structured output for EACH instrument.\n\n"
        f"For each instrument, produce the full output schema specified in "
        f"positioning.md. Be concise but complete — no filler text between "
        f"instruments. After the per-instrument analysis, produce a 1-2 line "
        f"summary identifying the most extreme positioning(s) flagged.\n\n"
        f"Data:\n```json\n{json.dumps(summaries, indent=2, default=str)}\n```\n"
    )


def main() -> int:
    console.print(Panel.fit(
        "Pulling live COT data and running Positioning Analyst",
        title="real-data agent run",
    ))

    cot = CotClient(lookback_years=3)
    summaries: list[dict] = []
    for instrument in COT_INSTRUMENTS:
        try:
            s = cot.summary(instrument)
        except Exception as e:
            console.print(f"[yellow]Skipping {instrument}: {e}[/yellow]")
            continue
        if s.get("status") == "ok":
            summaries.append(s)
            console.print(
                f"[dim]{instrument}: net {s['net_position']:>10,}  "
                f"pct {s['percentile_3yr']:>5.1f}  "
                f"trend {s['trend_4week']:>+10,}  "
                f"extreme {s['weeks_at_extreme_in_last_6']}/6[/dim]"
            )
        else:
            console.print(f"[yellow]{instrument}: {s.get('status')}[/yellow]")

    if not summaries:
        console.print("[red]No COT data available; cannot run agent.[/red]")
        return 1

    user_message = build_user_message(summaries)

    console.rule("[cyan]Running Positioning Analyst[/cyan]")
    client = OpenRouterClient()
    result = run_agent("layer1_specialists/positioning_analyst", user_message, client=client)

    console.rule("[green]Agent output[/green]")
    console.print(Panel(Markdown(result.content), border_style="green"))

    console.rule("[dim]Run stats[/dim]")
    console.print(
        f"[dim]model: {result.model}  |  "
        f"tokens: {result.input_tokens} in / {result.output_tokens} out  |  "
        f"cost: ${result.cost_usd:.6f}  |  "
        f"spent today: ${client.budget.spent_today():.6f}[/dim]"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
