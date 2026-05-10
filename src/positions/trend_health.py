"""Trend-health classifier for an open swing position.

Audit feedback: the Tradability Filter is calibrated for entry timing
(is this a clean pullback right now?). For a position you're already
holding over weeks, the question shifts: is the trend still intact, is
it fading, or is the structure breaking down?

This module answers that — same SetupContext input the Filter uses,
but framed as a trend-health verdict: trend_healthy / fading /
reversal_risk. Surfaced on each open-position card so the user can see
at a glance whether their thesis-aligned move is still healthy without
wading into entry-timing language.

Logic uses simple structural rules from price action — SMA alignment,
distance from extremes, recent momentum vs longer trend. No LLM.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TrendHealth:
    verdict: str          # "trend_healthy" | "fading" | "reversal_risk" | "unknown"
    reason: str           # one-line explanation
    direction_aligned: bool


def assess_trend_health(direction: str, ctx: dict | None) -> TrendHealth:
    """Given a long/short position direction and a SetupContext dict,
    return a trend-health verdict.

    `direction` is "long" or "short" (the user's open position direction).
    `ctx` is the dict produced by SetupContext.to_dict(), or None if we
    don't have price context for this instrument.
    """
    if not ctx:
        return TrendHealth(
            verdict="unknown",
            reason="No price context available for this instrument.",
            direction_aligned=True,
        )

    is_long = direction.lower() == "long"
    price = float(ctx.get("current_price") or 0.0)
    sma20 = float(ctx.get("sma_20") or 0.0)
    sma50 = float(ctx.get("sma_50") or 0.0)
    chart_trend = (ctx.get("trend_direction") or "sideways").lower()
    pct_5d = float(ctx.get("pct_change_5d") or 0.0)
    pct_20d = float(ctx.get("pct_change_20d") or 0.0)
    dist_high = float(ctx.get("distance_from_20d_high_pct") or 0.0)
    dist_low = float(ctx.get("distance_from_20d_low_pct") or 0.0)

    if not price:
        return TrendHealth(
            verdict="unknown",
            reason="Price data missing from setup context.",
            direction_aligned=True,
        )

    # Direction alignment: chart trend matches position direction
    aligned = (
        (is_long and chart_trend == "up") or
        (not is_long and chart_trend == "down")
    )

    # Long position: ideal world is price > sma20 > sma50, making higher highs.
    # Short position: ideal world is price < sma20 < sma50, lower lows.
    if is_long:
        sma_stack_ok = price > sma20 > sma50 if (sma20 and sma50) else None
        recent_strong = pct_5d > 0
        longer_strong = pct_20d > 0
        near_high = dist_high <= 2.0     # within 2% of 20d high
        near_low = dist_low <= 2.0       # within 2% of 20d low
    else:
        sma_stack_ok = price < sma20 < sma50 if (sma20 and sma50) else None
        recent_strong = pct_5d < 0
        longer_strong = pct_20d < 0
        near_high = dist_high <= 2.0
        near_low = dist_low <= 2.0

    # Reversal risk: chart trend has flipped against the position
    if (is_long and chart_trend == "down") or (not is_long and chart_trend == "up"):
        if sma_stack_ok is False:
            return TrendHealth(
                verdict="reversal_risk",
                reason=(
                    f"Chart trend has turned {chart_trend} against your "
                    f"{'long' if is_long else 'short'}; SMA stack has flipped. "
                    f"5d move {pct_5d:+.1f}%, 20d move {pct_20d:+.1f}%."
                ),
                direction_aligned=False,
            )
        return TrendHealth(
            verdict="reversal_risk",
            reason=(
                f"Chart trend has turned {chart_trend} against your "
                f"{'long' if is_long else 'short'} position."
            ),
            direction_aligned=False,
        )

    # Fading: aligned with longer trend but recent action is mixed/against
    if longer_strong and not recent_strong:
        return TrendHealth(
            verdict="fading",
            reason=(
                f"20-day trend still in your favour ({pct_20d:+.1f}%) but "
                f"5-day move ({pct_5d:+.1f}%) is going the other way — momentum "
                f"is slowing. Watch for confirmation."
            ),
            direction_aligned=aligned,
        )

    # Healthy paths
    if recent_strong and longer_strong and (sma_stack_ok or aligned):
        # In profit and structure intact
        if (is_long and near_high) or (not is_long and near_low):
            extra = " Approaching the 20-day extreme; consider trailing stop."
        else:
            extra = ""
        return TrendHealth(
            verdict="trend_healthy",
            reason=(
                f"Structure intact: chart trend {chart_trend}, 5d {pct_5d:+.1f}%, "
                f"20d {pct_20d:+.1f}%, SMAs aligned with your "
                f"{'long' if is_long else 'short'}.{extra}"
            ),
            direction_aligned=True,
        )

    # Sideways / mixed structure
    return TrendHealth(
        verdict="fading",
        reason=(
            f"Chart is {chart_trend}, recent move {pct_5d:+.1f}% over 5d / "
            f"{pct_20d:+.1f}% over 20d — direction not strongly confirming "
            f"your {'long' if is_long else 'short'} thesis."
        ),
        direction_aligned=aligned,
    )
