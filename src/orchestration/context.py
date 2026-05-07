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


# Block prepended to every agent input message that consumes data carrying
# freshness tags. Keep short - the rule is the value, not the wording.
FRESHNESS_INSTRUCTION = (
    "Each datum below carries a freshness tag in the form "
    "[fresh|recent|stale · obs DATE · released DATE · Nd old]. Treat stale data "
    "with caution: do NOT state high-confidence directional conclusions when the "
    "primary supporting evidence is `stale`. Reduce confidence at least one level "
    "(high→medium, medium→low) when reasoning leans on stale-tagged inputs. "
    "Note this freshness consideration explicitly in your output."
)


def fred_snapshot_to_text(snapshot: pd.DataFrame) -> str:
    """Render FRED snapshot DataFrame as a readable text block with freshness tags."""
    lines = ["FRED snapshot (latest values, with freshness tags):"]
    for _, row in snapshot.iterrows():
        if pd.isna(row["value"]):
            lines.append(f"  {row['series']:24s} ({row['fred_id']}): no data")
            continue
        delta = ""
        if row.get("change") is not None and not pd.isna(row.get("change")):
            arrow = "+" if row["change"] >= 0 else ""
            delta = f"  Δ {arrow}{row['change']:.3f}"
        tag = row.get("freshness_tag", "")
        lines.append(
            f"  {row['series']:24s} ({row['fred_id']:14s}): "
            f"{row['value']:>10.3f}{delta}  {tag}"
        )
    return "\n".join(lines)


def cot_summaries_to_text(summaries: list[dict]) -> str:
    """Render COT summaries as JSON for agent consumption.

    Each summary already carries freshness_label and freshness_tag fields
    (see src/data/cot.py).
    """
    return json.dumps(summaries, indent=2, default=str)


def inflation_tracker_input(snapshot: pd.DataFrame, yoy_data: dict[str, float]) -> str:
    today = datetime.now().date().isoformat()
    return (
        f"# Inflation Tracker — Live Data, {today}\n\n"
        f"{FRESHNESS_INSTRUCTION}\n\n"
        f"Apply the methodology in your prompt against this data. "
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
        f"{FRESHNESS_INSTRUCTION}\n\n"
        f"Apply your methodology (positioning.md). Produce per-instrument structured "
        f"output, then a 1-2 line summary identifying the most extreme positioning. "
        f"Each summary in the JSON below has a `freshness_label` and `freshness_tag` "
        f"field — surface these in your reasoning and conviction calibration.\n\n"
        f"## COT data\n\n```json\n{cot_summaries_to_text(summaries)}\n```\n"
    )


def fed_watcher_input(rate_snapshot: pd.DataFrame) -> str:
    today = datetime.now().date().isoformat()
    return (
        f"# Fed-Watcher — Live Rate Data, {today}\n\n"
        f"{FRESHNESS_INSTRUCTION}\n\n"
        f"NOTE: FOMC statement text is not yet wired in (Phase B). For this run, "
        f"reason from rate path data alone — Fed funds target, market pricing "
        f"via Treasury yields, breakevens. Produce your structured output schema, "
        f"explicitly noting where you'd refine if statement text were available.\n\n"
        f"## Rate snapshot\n\n{fred_snapshot_to_text(rate_snapshot)}\n"
    )


def strategist_input(layer1_outputs: dict[str, str], themes: str) -> str:
    today = datetime.now().date().isoformat()

    # Pull the user-maintained recent events log. The system has no news
    # API — this is the only channel by which Trump-era headlines, surprise
    # tariff announcements, or off-cycle Fed-speaker comments enter the
    # pipeline. Treat it as authoritative ground-truth news context.
    try:
        from src.data import render_recent_events_block
        recent_events_text = render_recent_events_block()
    except Exception as e:
        recent_events_text = f"(recent_events.yaml unavailable: {e})"

    parts = [
        f"# FX + Cross-Asset Strategist — Synthesis, {today}",
        "",
        "Synthesize the Layer 1 specialist outputs into per-instrument bias cards "
        "for the watchlist. Apply your methodology. Produce one bias card per "
        "instrument plus the summary table, exactly per your output schema.",
        "",
        "**Freshness note:** Layer 1 specialists were instructed to flag the "
        "freshness of their underlying inputs (`fresh` / `recent` / `stale`). "
        "Respect those assessments. Do not upgrade conviction beyond what the "
        "freshest supporting evidence justifies. Note where stale data is "
        "doing load-bearing work in your synthesis.",
        "",
        "**News note:** The block titled 'Recent regime-relevant events' below "
        "is the user-maintained log of off-cycle news (tariff announcements, "
        "Fed-speaker pivots, geopolitical events). The system has no news scraper, "
        "so this is your only source of unstructured news context. Respect it: "
        "if a HIGH-relevance event there contradicts a Layer 1 specialist's tone, "
        "the news event wins for short-term framing. If the log is empty, the "
        "user has flagged no material news in the last 30 days — reason from "
        "FRED data and THEMES.md alone.",
        "",
        "## Active themes (from docs/THEMES.md)",
        "",
        themes,
        "",
        "## Recent regime-relevant events (from data/recent_events.yaml)",
        "",
        recent_events_text,
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


def setup_filter_input(
    instrument: str,
    judge_card: str,
    setup_context: dict,
    themes: str,
    events_block: str = "",
) -> str:
    """Build the user message for the Tradability Filter (Layer 4b)."""
    events_section = (
        f"## Upcoming scheduled events (next 7 days)\n\n"
        f"This is the ground-truth event calendar from data/events.yaml. "
        f"Use this as the authoritative source for the `blocking_event_within_5d` "
        f"check — do NOT rely on memory. If the list is empty, set "
        f"`blocking_event_within_5d: false`.\n\n"
        f"{events_block}\n\n"
        if events_block
        else ""
    )
    return (
        f"# Tradability Filter — {instrument}\n\n"
        f"The Judge has produced a final bias for this instrument. Apply your "
        f"structural checks (trend alignment, location quality, ATR suitability, "
        f"invalidation clarity, crowding, blocking events) and produce a "
        f"verdict per your output schema.\n\n"
        f"You are filtering what reaches the human reviewer. Default to a more "
        f"restrictive verdict when checks conflict.\n\n"
        f"## Active themes (condensed)\n\n{themes}\n\n"
        f"{events_section}"
        f"## Judge bias card\n\n{judge_card}\n\n"
        f"## Setup context (live, daily OHLC + derived levels)\n\n"
        f"```json\n{json.dumps(setup_context, indent=2, default=str)}\n```\n"
    )


def pm_brief_input(
    judge_outputs: dict[str, str],
    themes: str,
    *,
    filter_results: dict[str, dict] | None = None,
) -> str:
    """Build the user message for the PM brief (Layer 5).

    If filter_results is provided, the PM is instructed to organize the brief
    by tradability category (tradable_now / watch / pass) so the human reviewer
    sees actionable setups separated from watchlist items.
    """
    today = datetime.now().date().isoformat()
    filter_results = filter_results or {}

    parts = [
        f"# PM Brief — {today}",
        "",
        "Synthesize the Judge final bias cards into a daily PM brief per your "
        "output schema. Your role is to brief the human, not to act for them. "
        "Use review language ('setup at 20d SMA on pullback'), not execution "
        "language ('enter here').",
        "",
    ]

    if filter_results:
        # Categorize instruments
        tradable_now = [i for i, f in filter_results.items() if f.get("verdict") == "tradable_now"]
        watch = [i for i, f in filter_results.items() if f.get("verdict") == "watch"]
        passed = [i for i, f in filter_results.items() if f.get("verdict") == "pass_despite_bias"]

        parts.extend([
            "**Tradability Filter has run.** Organize your brief into three sections, "
            "in this order:",
            "",
            "1. **Setups for review (`tradable_now`)** — these have cleared structural "
            "checks. Present clearly: bias direction, key level to act around, "
            "invalidation level, primary themes. The human decides whether to trade. "
            "Do not state position sizes, dollar risk, or execution actions.",
            "2. **Watch list (`watch`)** — bias is supported but location is not yet "
            "tradable. State explicitly what would change the verdict.",
            "3. **Passed despite bias (`pass_despite_bias`)** — macro-aligned but "
            "structurally unfavorable. Note briefly why the filter passed each.",
            "",
            f"Tradable now: {tradable_now or 'none'}",
            f"Watch: {watch or 'none'}",
            f"Passed: {passed or 'none'}",
            "",
            "If tradable_now is empty, the brief should be honest: today has no "
            "setups passing structural review. That is a valid output and most days "
            "should look like this.",
            "",
        ])

    parts.extend(["## THEMES.md", "", themes, ""])

    if filter_results:
        parts.extend(["## Filter results (per instrument)", ""])
        for instrument, fr in filter_results.items():
            parts.extend([f"### {instrument}", "",
                          f"```json\n{json.dumps(fr, indent=2, default=str)}\n```", ""])

    parts.extend(["## Judge final bias cards", ""])
    for instrument, output in judge_outputs.items():
        parts.extend([f"### {instrument}", "", output, ""])

    return "\n".join(parts)
