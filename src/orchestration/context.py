"""Helpers for assembling per-agent input messages from data + previous outputs."""
from __future__ import annotations

import json
from datetime import datetime

import pandas as pd

from src.config import DOCS_DIR


def load_themes() -> str:
    """Return the current THEMES.md content (used by Layer 2/3/4/5 agents)."""
    path = DOCS_DIR / "THEMES.md"
    if not path.exists():
        return "(THEMES.md not found)"
    return path.read_text(encoding="utf-8")


def fred_snapshot_to_text(snapshot: pd.DataFrame) -> str:
    """Render FRED snapshot DataFrame as a readable text block."""
    lines = ["FRED snapshot (latest available values):"]
    for _, row in snapshot.iterrows():
        if pd.isna(row["value"]):
            lines.append(f"  {row['series']:24s} ({row['fred_id']}): no data")
        else:
            lines.append(
                f"  {row['series']:24s} ({row['fred_id']:14s}): "
                f"{row['value']:>10.3f}  as of {row['date']}"
            )
    return "\n".join(lines)


def cot_summaries_to_text(summaries: list[dict]) -> str:
    """Render COT summaries as JSON for agent consumption."""
    return json.dumps(summaries, indent=2, default=str)


def inflation_tracker_input(snapshot: pd.DataFrame, yoy_data: dict[str, float]) -> str:
    today = datetime.now().date().isoformat()
    return (
        f"# Inflation Tracker — Live Data, {today}\n\n"
        f"Apply the methodology in your prompt against this data.\n"
        f"Produce the structured output schema specified in your prompt.\n\n"
        f"## Latest FRED prints\n\n{fred_snapshot_to_text(snapshot)}\n\n"
        f"## Year-over-year computed values\n\n"
        + "\n".join(f"  {k:30s}: {v:+.2f}%" for k, v in yoy_data.items())
        + "\n"
    )


def positioning_analyst_input(summaries: list[dict]) -> str:
    today = datetime.now().date().isoformat()
    return (
        f"# Positioning Analyst — Live COT Data, {today}\n\n"
        f"Apply your methodology (positioning.md). Produce per-instrument structured "
        f"output, then a 1-2 line summary identifying the most extreme positioning.\n\n"
        f"## COT data\n\n```json\n{cot_summaries_to_text(summaries)}\n```\n"
    )


def fed_watcher_input(rate_snapshot: pd.DataFrame) -> str:
    today = datetime.now().date().isoformat()
    return (
        f"# Fed-Watcher — Live Rate Data, {today}\n\n"
        f"NOTE: FOMC statement text is not yet wired in (Phase B). For this run, "
        f"reason from rate path data alone — Fed funds target, market pricing "
        f"via Treasury yields, breakevens. Produce your structured output schema, "
        f"explicitly noting where you'd refine if statement text were available.\n\n"
        f"## Rate snapshot\n\n{fred_snapshot_to_text(rate_snapshot)}\n"
    )


def strategist_input(layer1_outputs: dict[str, str], themes: str) -> str:
    today = datetime.now().date().isoformat()
    parts = [
        f"# FX + Cross-Asset Strategist — Synthesis, {today}",
        "",
        "Synthesize the Layer 1 specialist outputs into per-instrument bias cards "
        "for the watchlist (DXY, EURUSD, USDJPY, GBPUSD, AUDUSD, ES, NQ, GC, CL, ZN). "
        "Apply your methodology. Produce one bias card per instrument plus the "
        "summary table, exactly per your output schema.",
        "",
        "## Active themes (from docs/THEMES.md)",
        "",
        themes,
        "",
        "## Layer 1 specialist outputs",
        "",
    ]
    for name, output in layer1_outputs.items():
        parts.extend([f"### {name}", "", output, ""])
    return "\n".join(parts)


def contrarian_input(strategist_output: str, themes: str) -> str:
    today = datetime.now().date().isoformat()
    return (
        f"# Contrarian — Adversarial Review, {today}\n\n"
        f"Below are the Layer 2 Strategist's bias cards. For EACH instrument, "
        f"produce your contrarian challenge per your output schema. Be specific "
        f"with positioning percentiles, narrative-fragility points, and probability "
        f"estimates. Don't fade unless you have substance.\n\n"
        f"## THEMES.md (current)\n\n{themes}\n\n"
        f"## Layer 2 Strategist output\n\n{strategist_output}\n"
    )


def bull_advocate_input(
    instrument: str,
    strategist_card: str,
    contrarian_challenge: str,
    themes: str,
) -> str:
    return (
        f"# Bull Advocate — {instrument}\n\n"
        f"Construct the strongest case for being LONG {instrument}, per your "
        f"output schema. Engage with the contrarian challenge. Be specific.\n\n"
        f"## THEMES.md\n{themes}\n\n"
        f"## Strategist's bias card for {instrument}\n{strategist_card}\n\n"
        f"## Contrarian challenge\n{contrarian_challenge}\n"
    )


def bear_advocate_input(
    instrument: str,
    strategist_card: str,
    contrarian_challenge: str,
    bull_case: str,
    themes: str,
) -> str:
    return (
        f"# Bear Advocate — {instrument}\n\n"
        f"Construct the strongest case for being SHORT {instrument}, per your "
        f"output schema. Engage with the bull case. Be specific.\n\n"
        f"## THEMES.md\n{themes}\n\n"
        f"## Strategist's bias card\n{strategist_card}\n\n"
        f"## Contrarian challenge\n{contrarian_challenge}\n\n"
        f"## Bull Advocate's case (engage with this)\n{bull_case}\n"
    )


def judge_input(
    instrument: str,
    strategist_card: str,
    contrarian_challenge: str,
    bull_case: str,
    bear_case: str,
    themes: str,
) -> str:
    return (
        f"# Judge — {instrument}\n\n"
        f"Synthesize bull, bear, contrarian, and strategist into a final bias "
        f"card per your output schema. Be calibrated, not advocational.\n\n"
        f"## THEMES.md\n{themes}\n\n"
        f"## Strategist's bias card\n{strategist_card}\n\n"
        f"## Contrarian challenge\n{contrarian_challenge}\n\n"
        f"## Bull Advocate\n{bull_case}\n\n"
        f"## Bear Advocate\n{bear_case}\n"
    )


def pm_brief_input(judge_outputs: dict[str, str], themes: str) -> str:
    today = datetime.now().date().isoformat()
    parts = [
        f"# PM Brief — {today}",
        "",
        "Synthesize the Judge final bias cards into a daily PM brief per your "
        "output schema. Rank the watchlist, identify 1-3 highest-priority "
        "setups, recommend action or no-action. Druckenmiller principles.",
        "",
        "## THEMES.md",
        "",
        themes,
        "",
        "## Judge final bias cards",
        "",
    ]
    for instrument, output in judge_outputs.items():
        parts.extend([f"### {instrument}", "", output, ""])
    return "\n".join(parts)
