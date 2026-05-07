"""Position advisor — given a position, the latest pipeline run, and the
current price, returns an action recommendation with a one-sentence reason.

The advisor is decision-support, not execution. It produces a categorical
verdict and prose; the user looks at it on the dashboard and decides
whether to actually close, trim, or trail their FTMO position.

Action ladder (most urgent first):
  emergency_close — emergency stop level breached. Macro thesis is moot;
    the structural invalidation has triggered. Get out.
  close          — macro thesis flipped against position with conviction,
    or chart structure has materially turned (filter says
    pass_despite_bias for a position in the same direction as
    the bias was when opened).
  trim           — thesis is weakening — current conviction is materially
    below open-time conviction, OR position is in significant
    profit and the case for full size has weakened.
  trail_stop     — position is comfortably in profit and the macro thesis
    is intact. Consider raising the emergency stop to lock
    in some of the gain.
  review         — soft alert: chart suggests near-term pullback risk
    even though macro view stands. Consider sizing.
  hold           — thesis intact, no action needed.

Inputs:
  position         — Position dataclass
  current_price    — float, latest available price for the instrument
  latest_run       — dashboard.loader.Run for the most recent pipeline run

The advisor is deliberately rule-based, not LLM-based, because:
  1. Decisions on open positions need to be deterministic and auditable.
  2. The relevant signals (bias direction, conviction delta, filter verdict,
     stop level) are all already structured outputs from upstream layers.
  3. Cost: an LLM call per active position per page-load is wasteful for
     what is essentially a comparison of numbers.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.positions.store import Position


# Thresholds — kept here so they're tweakable without touching logic
CONVICTION_FLIP_THRESHOLD = 6   # if opposite bias has conviction >= this, urgent close
CONVICTION_WEAKEN_DELTA = 3     # if conviction has dropped this much, trim
TRAIL_PROFIT_PCT = 5.0          # at what % gain to start suggesting trail
TRIM_PROFIT_PCT = 10.0          # at what % gain to start suggesting trim


@dataclass
class Advice:
    action: str               # see ladder above
    urgency: str              # "low" | "med" | "high"
    reason: str               # one sentence
    pnl_pct: Optional[float] = None
    macro_aligned: bool = True       # latest bias direction matches position direction
    conviction_now: int = 0
    conviction_delta: int = 0        # current - at_open (negative = weakened)
    filter_verdict_now: str = ""
    stop_distance_pct: Optional[float] = None  # how far is price from emergency stop

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "urgency": self.urgency,
            "reason": self.reason,
            "pnl_pct": self.pnl_pct,
            "macro_aligned": self.macro_aligned,
            "conviction_now": self.conviction_now,
            "conviction_delta": self.conviction_delta,
            "filter_verdict_now": self.filter_verdict_now,
            "stop_distance_pct": self.stop_distance_pct,
        }


def _pnl_pct(position: Position, current_price: float) -> float:
    sign = 1.0 if position.direction == "long" else -1.0
    return round(
        sign * (current_price - position.entry_price) / position.entry_price * 100,
        2,
    )


def _stop_breached(position: Position, current_price: float) -> bool:
    """True iff price has crossed the emergency stop in the *adverse* direction.
    For a long, that means current_price <= stop. For a short, current_price >= stop.
    """
    if position.emergency_stop is None:
        return False
    if position.direction == "long":
        return current_price <= position.emergency_stop
    return current_price >= position.emergency_stop


def _stop_distance_pct(position: Position, current_price: float) -> Optional[float]:
    if position.emergency_stop is None:
        return None
    return round(
        abs(current_price - position.emergency_stop) / current_price * 100,
        2,
    )


def _normalise_bias(bias: str) -> str:
    """Map 'slight long' / 'bullish (pullback)' / 'long' to canonical 'long' or 'short'."""
    b = (bias or "").lower()
    if "long" in b or "bull" in b:
        return "long"
    if "short" in b or "bear" in b:
        return "short"
    return "neutral"


def advise_position(
    position: Position,
    current_price: float,
    latest_run,  # dashboard.loader.Run; typed loosely to avoid a circular import
) -> Advice:
    """Produce an advisory verdict for one active position.

    Reads the latest run's bias card and (if present) Tradability Filter card
    for the position's instrument, then walks the rule ladder top-down.
    """
    pnl = _pnl_pct(position, current_price)
    stop_dist_pct = _stop_distance_pct(position, current_price)

    # --- Latest macro state for this instrument ---
    inst = position.instrument
    bias_obj = next((b for b in latest_run.instrument_biases
                     if b.instrument == inst), None) if latest_run else None
    council = (latest_run.council.get(inst)
               if latest_run else None) if latest_run else None
    filter_card = (latest_run.tradability.get(inst)
                   if latest_run else None) if latest_run else None

    # Authoritative current-conviction: Judge if available, else Strategist
    if council and council.judge_conviction:
        conv_now = council.judge_conviction
        bias_now_raw = council.judge_bias or (bias_obj.bias if bias_obj else "")
    elif bias_obj:
        conv_now = bias_obj.conviction
        bias_now_raw = bias_obj.bias
    else:
        conv_now = 0
        bias_now_raw = ""

    bias_now = _normalise_bias(bias_now_raw)
    macro_aligned = (bias_now == position.direction)
    conv_delta = conv_now - position.conviction_at_open

    filter_verdict = filter_card.verdict if filter_card else ""

    # ===== Rule ladder — first match wins =====

    # 1. EMERGENCY: stop breached
    if _stop_breached(position, current_price):
        return Advice(
            action="emergency_close",
            urgency="high",
            reason=(
                f"Emergency stop {position.emergency_stop:.4f} breached "
                f"(current {current_price:.4f}). Structural invalidation level hit; "
                f"close per pre-defined plan, do not deliberate."
            ),
            pnl_pct=pnl,
            macro_aligned=macro_aligned,
            conviction_now=conv_now,
            conviction_delta=conv_delta,
            filter_verdict_now=filter_verdict,
            stop_distance_pct=stop_dist_pct,
        )

    # 2. CLOSE: macro thesis flipped against position with real conviction
    if not macro_aligned and bias_now != "neutral" and conv_now >= CONVICTION_FLIP_THRESHOLD:
        return Advice(
            action="close",
            urgency="high",
            reason=(
                f"Macro view has flipped to {bias_now} at {conv_now}/10 conviction; "
                f"position direction ({position.direction}) is now opposed by the system's "
                f"primary thesis. Continuing to hold is fighting your own analysis."
            ),
            pnl_pct=pnl,
            macro_aligned=False,
            conviction_now=conv_now,
            conviction_delta=conv_delta,
            filter_verdict_now=filter_verdict,
            stop_distance_pct=stop_dist_pct,
        )

    # 3. CLOSE: chart materially against you per filter
    #    Only triggers if the filter ran AND said pass_despite_bias for an
    #    instrument where the bias still aligns — i.e., the chart structure
    #    has turned against the entry even though macro view holds.
    if (filter_verdict == "pass_despite_bias"
            and macro_aligned and conv_now >= 5):
        return Advice(
            action="close",
            urgency="med",
            reason=(
                "Chart structure has turned against the position (filter verdict: "
                "pass_despite_bias). The macro view still holds but the structural "
                "case for this entry has eroded — re-enter on a cleaner setup."
            ),
            pnl_pct=pnl,
            macro_aligned=macro_aligned,
            conviction_now=conv_now,
            conviction_delta=conv_delta,
            filter_verdict_now=filter_verdict,
            stop_distance_pct=stop_dist_pct,
        )

    # 4. TRIM: thesis weakened materially since open
    if (position.conviction_at_open > 0
            and conv_delta <= -CONVICTION_WEAKEN_DELTA):
        return Advice(
            action="trim",
            urgency="med",
            reason=(
                f"Conviction has dropped {abs(conv_delta)} points since open "
                f"({position.conviction_at_open} → {conv_now}). Take some risk off; "
                f"keep a residual on for the case where the thesis re-firms."
            ),
            pnl_pct=pnl,
            macro_aligned=macro_aligned,
            conviction_now=conv_now,
            conviction_delta=conv_delta,
            filter_verdict_now=filter_verdict,
            stop_distance_pct=stop_dist_pct,
        )

    # 5. TRIM: meaningful profit and conviction has slipped at all
    if pnl >= TRIM_PROFIT_PCT and conv_delta < 0:
        return Advice(
            action="trim",
            urgency="low",
            reason=(
                f"Position is up {pnl:.1f}% and conviction has eased "
                f"({position.conviction_at_open} → {conv_now}). Consider banking some, "
                f"keep a runner for the original thesis."
            ),
            pnl_pct=pnl,
            macro_aligned=macro_aligned,
            conviction_now=conv_now,
            conviction_delta=conv_delta,
            filter_verdict_now=filter_verdict,
            stop_distance_pct=stop_dist_pct,
        )

    # 6. TRAIL_STOP: in profit with macro intact
    if pnl >= TRAIL_PROFIT_PCT and macro_aligned and conv_now >= 6:
        return Advice(
            action="trail_stop",
            urgency="low",
            reason=(
                f"Up {pnl:.1f}% with macro thesis still {bias_now} at {conv_now}/10. "
                f"Consider raising the emergency stop to protect a portion of gains; "
                f"do not tighten so much that normal volatility takes you out."
            ),
            pnl_pct=pnl,
            macro_aligned=macro_aligned,
            conviction_now=conv_now,
            conviction_delta=conv_delta,
            filter_verdict_now=filter_verdict,
            stop_distance_pct=stop_dist_pct,
        )

    # 7. REVIEW: soft alert based on filter
    if filter_verdict == "watch" and macro_aligned:
        return Advice(
            action="review",
            urgency="low",
            reason=(
                "Macro view still supports the position, but the chart is on Watch "
                "rather than green-lit — implies a near-term pullback or hesitation. "
                "No action required, just be aware."
            ),
            pnl_pct=pnl,
            macro_aligned=macro_aligned,
            conviction_now=conv_now,
            conviction_delta=conv_delta,
            filter_verdict_now=filter_verdict,
            stop_distance_pct=stop_dist_pct,
        )

    # 8. HOLD: default
    if macro_aligned and conv_now > 0:
        reason = (
            f"Thesis intact: {bias_now} at {conv_now}/10. "
            f"P&L {pnl:+.1f}%."
        )
    elif bias_now == "neutral" or conv_now == 0:
        reason = (
            f"No fresh macro view in the latest run for {inst} (instrument dropped "
            f"out of council below threshold). Position pre-dates this softening; "
            f"holding by inertia. P&L {pnl:+.1f}%."
        )
    else:
        # macro misaligned but below the conviction threshold for a forced close
        reason = (
            f"Macro view leans {bias_now} at {conv_now}/10 — opposed to the "
            f"position but not strongly enough to force action. P&L {pnl:+.1f}%; "
            f"watch for further conviction build."
        )
    return Advice(
        action="hold",
        urgency="low",
        reason=reason,
        pnl_pct=pnl,
        macro_aligned=macro_aligned,
        conviction_now=conv_now,
        conviction_delta=conv_delta,
        filter_verdict_now=filter_verdict,
        stop_distance_pct=stop_dist_pct,
    )
