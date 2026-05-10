"""Deterministic macro regime classifier.

Audit feedback: the LLM agents do all the regime reasoning today, which
means it can drift run-to-run as the LLM rephrases its read of the same
data. A code-classified regime tag from FRED indicators alone serves as
an anchor — it changes only when *data* changes, not when the LLM
changes its mind. The dashboard shows it alongside the LLM bias so
disagreement (data says Goldilocks, LLM says No View) is itself
information.

Methodology — derived from playbook/regime_identification.md:

  Two axes, four cells:
                     Inflation rising   Inflation falling
    Growth rising    REFLATION          GOLDILOCKS
    Growth falling   STAGFLATION        DEFLATION

  Each axis is a count of indicators trending in one direction over the
  recent observation window. Tie / mixed → label as "TRANSITION".

Indicators used:
  Growth (4):
    - INDPRO (industrial production) MoM positive over last 3 months
    - PAYEMS (NFP) net positive over 3-month average
    - RSXFS (retail sales) MoM positive over last 3 months
    - ICSA (initial claims) trending DOWN (lower is better; inverted)
  Inflation (4):
    - CPIAUCSL YoY > 2.0% AND rising MoM over last 3 months
    - CPILFESL (core CPI) YoY > 2.0% AND rising MoM over last 3 months
    - PCEPILFE (core PCE) YoY > 2.0% AND rising MoM over last 3 months
    - T10YIE (10y breakeven) > 2.3% (above Fed target)

A simple majority on each axis classifies the cell. Ties classified as
TRANSITION (the regime is in motion).

Implications per regime are derived from the same playbook. They're
hard-coded directional biases, not LLM-generated, so they don't drift.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.data.fred import FredClient


@dataclass
class IndicatorRead:
    """One indicator's read: the value, the direction, and a short note."""
    name: str
    direction: int  # +1 = supportive of axis, -1 = opposite, 0 = neutral
    note: str


@dataclass
class RegimeRead:
    label: str                    # REFLATION | GOLDILOCKS | STAGFLATION | DEFLATION | TRANSITION
    growth_score: int             # net direction count (-N..+N)
    inflation_score: int
    growth_indicators: list[IndicatorRead]
    inflation_indicators: list[IndicatorRead]
    implications: dict[str, str]  # per-instrument bias string

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "growth_score": self.growth_score,
            "inflation_score": self.inflation_score,
            "growth_indicators": [
                {"name": i.name, "direction": i.direction, "note": i.note}
                for i in self.growth_indicators
            ],
            "inflation_indicators": [
                {"name": i.name, "direction": i.direction, "note": i.note}
                for i in self.inflation_indicators
            ],
            "implications": dict(self.implications),
        }


# Regime → directional bias per instrument. Hard-coded from the playbook.
# These are starting points the LLM can refine; the regime anchor's value
# is *stability*, so they intentionally don't change run-to-run.
_IMPLICATIONS: dict[str, dict[str, str]] = {
    "REFLATION": {
        "DXY":    "neutral / soft",
        "EURUSD": "bullish",
        "USDJPY": "bullish (yields up)",
        "GBPUSD": "bullish",
        "AUDUSD": "bullish (commodity demand)",
        "ES":     "bullish (earnings + nominal growth)",
        "NQ":     "bullish (with caveat — long-duration tech vulnerable)",
        "GC":     "bullish (real-yield ambiguous; stagflation-lite hedge)",
        "CL":     "bullish (demand + supply premium)",
    },
    "GOLDILOCKS": {
        "DXY":    "neutral",
        "EURUSD": "neutral / mildly bullish",
        "USDJPY": "neutral",
        "GBPUSD": "mildly bullish",
        "AUDUSD": "bullish",
        "ES":     "bullish (P/E expansion)",
        "NQ":     "very bullish",
        "GC":     "neutral / soft (real yields rise)",
        "CL":     "neutral",
    },
    "STAGFLATION": {
        "DXY":    "bullish (safe haven)",
        "EURUSD": "bearish",
        "USDJPY": "two-way (carry vs intervention)",
        "GBPUSD": "bearish",
        "AUDUSD": "bearish (China growth + risk-off)",
        "ES":     "bearish (earnings + multiple compression)",
        "NQ":     "bearish (long-duration hit)",
        "GC":     "very bullish",
        "CL":     "bullish (supply-driven)",
    },
    "DEFLATION": {
        "DXY":    "bullish",
        "EURUSD": "bearish",
        "USDJPY": "bearish (JPY safe-haven)",
        "GBPUSD": "bearish",
        "AUDUSD": "bearish",
        "ES":     "bearish",
        "NQ":     "bearish (early); bullish later (Fed cut bid)",
        "GC":     "bullish (Fed cut → real yields fall)",
        "CL":     "bearish",
    },
    "TRANSITION": {
        "DXY":    "no clear bias",
        "EURUSD": "no clear bias",
        "USDJPY": "no clear bias",
        "GBPUSD": "no clear bias",
        "AUDUSD": "no clear bias",
        "ES":     "no clear bias",
        "NQ":     "no clear bias",
        "GC":     "no clear bias",
        "CL":     "no clear bias",
    },
}


def _direction_from_recent(values: list[float], months: int = 3) -> int:
    """Did the series move net positive (+1) or negative (-1) over the
    last `months` observations? 0 if flat or insufficient data."""
    if not values or len(values) < 2:
        return 0
    take = values[-(months + 1):] if len(values) > months else values
    if len(take) < 2:
        return 0
    deltas = [take[i] - take[i - 1] for i in range(1, len(take))]
    pos = sum(1 for d in deltas if d > 0)
    neg = sum(1 for d in deltas if d < 0)
    if pos > neg: return 1
    if neg > pos: return -1
    return 0


def _classify(growth: int, inflation: int) -> str:
    if growth > 0 and inflation > 0: return "REFLATION"
    if growth > 0 and inflation < 0: return "GOLDILOCKS"
    if growth < 0 and inflation > 0: return "STAGFLATION"
    if growth < 0 and inflation < 0: return "DEFLATION"
    return "TRANSITION"


def classify_regime(fred: FredClient | None = None) -> RegimeRead:
    """Build a fresh regime read from current FRED data.

    Falls back to a defensive 'TRANSITION' read if FRED calls fail —
    we don't want a transient API hiccup to change the user-visible
    regime label.
    """
    fred = fred or FredClient()
    g_inds: list[IndicatorRead] = []
    i_inds: list[IndicatorRead] = []

    # Growth — last 6 months of monthly observations
    growth_specs = [
        ("ism_pmi_proxy", "Industrial Production", False),
        ("nfp_total",     "Nonfarm Payrolls",      False),
        ("retail_sales",  "Retail Sales",          False),
        ("claims_initial", "Initial Claims",       True),  # inverted: down = good
    ]
    for short, label, invert in growth_specs:
        try:
            s = fred.series(short).dropna()
            vals = s.iloc[-6:].tolist() if len(s) >= 2 else s.tolist()
            d = _direction_from_recent(vals, months=3)
            if invert:
                d = -d
            note = f"{label}: {'rising' if d > 0 else 'falling' if d < 0 else 'flat'}"
            g_inds.append(IndicatorRead(name=label, direction=d, note=note))
        except Exception as e:
            g_inds.append(IndicatorRead(name=label, direction=0, note=f"unavailable ({type(e).__name__})"))

    # Inflation — needs YoY computation to gauge level vs trend
    inflation_specs = [
        ("cpi_headline", "CPI Headline (YoY)",  2.0),
        ("cpi_core",     "CPI Core (YoY)",      2.0),
        ("pce_core",     "Core PCE (YoY)",      2.0),
    ]
    for short, label, threshold in inflation_specs:
        try:
            yoy = fred.yoy(short, periods=12).dropna()
            recent_vals = yoy.iloc[-6:].tolist() if len(yoy) >= 2 else yoy.tolist()
            current = recent_vals[-1] if recent_vals else None
            trend = _direction_from_recent(recent_vals, months=3)
            # Inflation is "rising" only if both above threshold AND trending up
            if current is None:
                d = 0
                note = f"{label}: data unavailable"
            elif current > threshold and trend > 0:
                d = 1
                note = f"{label}: {current:.2f}% (above {threshold}, rising)"
            elif current < threshold and trend < 0:
                d = -1
                note = f"{label}: {current:.2f}% (below {threshold}, falling)"
            else:
                d = 0
                note = f"{label}: {current:.2f}% (mixed)"
            i_inds.append(IndicatorRead(name=label, direction=d, note=note))
        except Exception as e:
            i_inds.append(IndicatorRead(name=label, direction=0, note=f"unavailable ({type(e).__name__})"))

    # Breakeven inflation expectations
    try:
        s = fred.series("breakeven_10y").dropna()
        if len(s) >= 1:
            current = float(s.iloc[-1])
            d = 1 if current > 2.3 else (-1 if current < 1.8 else 0)
            note = f"10y breakeven: {current:.2f}%"
            i_inds.append(IndicatorRead(name="10y Breakeven", direction=d, note=note))
    except Exception as e:
        i_inds.append(IndicatorRead(name="10y Breakeven", direction=0, note=f"unavailable ({type(e).__name__})"))

    growth_score = sum(i.direction for i in g_inds)
    inflation_score = sum(i.direction for i in i_inds)
    label = _classify(growth_score, inflation_score)

    return RegimeRead(
        label=label,
        growth_score=growth_score,
        inflation_score=inflation_score,
        growth_indicators=g_inds,
        inflation_indicators=i_inds,
        implications=_IMPLICATIONS.get(label, _IMPLICATIONS["TRANSITION"]),
    )
