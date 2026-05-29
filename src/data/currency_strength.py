"""Mechanical currency-strength engine — the spine of the PIPTHEORY meter.

PURELY DETERMINISTIC. No LLM, no randomness, no sampling. The same inputs
produce byte-identical output, every time. Strength is a transparent weighted
sum of standardised macro factors across the 8 majors:

    composite = Σ_p  weight_p · pillar_score_p        (over AVAILABLE pillars)

Five pillars:
    Monetary    — short rate, 10y bond, rate trajectory   (carry + policy)
    Growth      — unemployment level + trajectory          (inverted)
    Positioning — COT 3yr percentile + 4-week trend         (what funds do)
    Risk        — safe-haven tilt × VIX risk-off intensity  (flight to quality)
    Commodity   — terms-of-trade exposure × price momentum  (commodity ccys)

Design notes
------------
* Strength is RELATIVE — every factor is standardised cross-sectionally
  across the 8 currencies that day ("strong vs the basket right now").
* CONTEXT comes from: rate/unemployment trajectories, the COT 3-yr percentile,
  commodity momentum vs its own year, and the trend computed from stored
  history. Day-to-day noise is damped because a single move barely shifts a
  z-score, and slow inputs (GDP/COT) only change weekly.
* FRESHNESS-GATED — a factor only counts if its data is recent enough; stale
  inputs (e.g. FRED's discontinued non-US CPI) are excluded and the weights
  renormalise across what's available. Everything is still shown with an
  "as of" date for transparency.
* Pairs are derived: pair_score = ccy1_composite - ccy2_composite.
"""
from __future__ import annotations

import json
import math
import statistics
import tempfile
import threading
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
import structlog

from src.config import STATE_DIR
from src.data.cot import CotClient
from src.data.fred import FredClient
from src.data.prices import PriceClient

log = structlog.get_logger(__name__)

_PATH = STATE_DIR / "currency_strength.json"
_LOCK = threading.RLock()
_MAX_HISTORY = 400  # ~13 months of daily snapshots

COMPOSITE_SCALE = 45.0  # maps weighted-avg z (~±2) onto the ±100 display range

# Default pillar weights (DISCLOSED + tunable). Renormalised per currency
# across whichever pillars have fresh data.
PILLAR_WEIGHTS: dict[str, float] = {
    "monetary": 0.30,
    "growth": 0.20,
    "positioning": 0.20,
    "risk": 0.15,
    "commodity": 0.15,
}

# Max age (days) before a factor's data is considered stale and excluded.
MAX_AGE = {
    "rate": 150,     # OECD monthly rate proxies lag ~1-2 months
    "bond": 150,
    "unrate": 220,   # monthly or quarterly
    "cot": 30,        # weekly
    "price": 14,      # daily
}


@dataclass
class CurrencyConfig:
    code: str
    name: str
    rate_short: str          # FRED curated name — short/policy rate
    bond_10y: str            # FRED curated name — 10y govt bond
    unrate: str | None       # FRED curated name — unemployment (None if unavailable)
    cot: str | None          # WATCHLIST_COT_CODES key (None => USD, derived)
    safe_haven: float        # risk pillar tilt: + haven, - high-beta
    commodity: dict[str, float] = field(default_factory=dict)  # ticker -> exposure


# The 8 majors. FRED names reference src/data/fred.py MACRO_SERIES (verified).
CURRENCIES: dict[str, CurrencyConfig] = {
    "USD": CurrencyConfig("USD", "US Dollar", "ffr_effective", "ust_10y", "unrate", None, +0.6),
    "EUR": CurrencyConfig("EUR", "Euro", "estr_proxy", "bund_10y", "ezn_unrate", "EURUSD", 0.0),
    "GBP": CurrencyConfig("GBP", "British Pound", "uk_bank_rate_proxy", "gilt_10y", "uk_unrate", "GBPUSD", -0.2),
    "JPY": CurrencyConfig("JPY", "Japanese Yen", "jp_call_rate_proxy", "jgb_10y", None, "USDJPY", +1.0),
    "CHF": CurrencyConfig("CHF", "Swiss Franc", "ch_rate_3m_proxy", "ch_bond_10y", "ch_unrate", "USDCHF", +1.0),
    "CAD": CurrencyConfig("CAD", "Canadian Dollar", "ca_rate_3m_proxy", "ca_bond_10y", "ca_unrate", "USDCAD", -0.6,
                          {"CL": 1.0}),
    "AUD": CurrencyConfig("AUD", "Australian Dollar", "au_rate_3m_proxy", "au_bond_10y", "au_unrate", "AUDUSD", -1.0,
                          {"COPPER": 0.6, "COMMOD_BROAD": 0.4}),
    "NZD": CurrencyConfig("NZD", "New Zealand Dollar", "nz_rate_3m_proxy", "nz_bond_10y", "nz_unrate", "NZDUSD", -1.0,
                          {"COMMOD_BROAD": 0.8}),
}


# ── small numeric helpers (all pure) ──────────────────────────────────────

def _clip(x: float, lo: float = -3.0, hi: float = 3.0) -> float:
    return max(lo, min(hi, x))


def _age_days(d: date, ref: date | None = None) -> int:
    """Age of an observation relative to `ref` (default today). For historical
    backfill, ref = the as-of date so freshness is judged as-of THEN."""
    return ((ref or date.today()) - d).days


def _slice(s: pd.Series | None, as_of: date | None) -> pd.Series | None:
    """Restrict a series to observations on/before as_of (no-op if None)."""
    if s is None or as_of is None:
        return s
    return s[s.index <= pd.Timestamp(as_of)]


def _fred_series(fred: FredClient, name: str, *, yoy: bool = False, periods: int = 12) -> pd.Series | None:
    try:
        s = (fred.yoy(name, periods=periods) if yoy else fred.series(name)).dropna()
        return s if not s.empty else None
    except Exception as e:  # unknown id, network, etc.
        log.warning("cs_fred_failed", name=name, error=str(e)[:80])
        return None


def _latest(s: pd.Series | None) -> tuple[float, date] | None:
    if s is None or s.empty:
        return None
    return float(s.iloc[-1]), s.index[-1].date()


def _change_over(s: pd.Series | None, days: int = 90) -> float | None:
    """Change in level over the trailing `days` (date-based, frequency-agnostic)."""
    if s is None or s.empty:
        return None
    cutoff = s.index[-1] - pd.Timedelta(days=days)
    past = s[s.index <= cutoff]
    if past.empty:
        return None
    return float(s.iloc[-1] - past.iloc[-1])


def _momentum_z(closes: pd.Series, window: int = 63) -> float | None:
    """Z-score of the latest `window`-day % change vs its trailing-year distribution."""
    closes = closes.dropna()
    if len(closes) < window + 20:
        return None
    chg = closes.pct_change(window).dropna()
    if chg.empty:
        return None
    mu, sd = chg.mean(), chg.std()
    if sd == 0 or math.isnan(sd):
        return 0.0
    return _clip(float((chg.iloc[-1] - mu) / sd))


def _level_z(s: pd.Series, window: int = 252) -> float:
    """Z-score of the latest level vs its trailing `window` observations."""
    s = s.dropna().tail(window)
    if len(s) < 30:
        return 0.0
    mu, sd = s.mean(), s.std()
    if sd == 0 or math.isnan(sd):
        return 0.0
    return _clip(float((s.iloc[-1] - mu) / sd))


def _xsection_z(values: dict[str, float]) -> dict[str, float]:
    """Cross-sectional z-score across currencies (population stdev)."""
    xs = list(values.values())
    if len(xs) < 2:
        return {k: 0.0 for k in values}
    mu = statistics.mean(xs)
    sd = statistics.pstdev(xs)
    if sd == 0:
        return {k: 0.0 for k in values}
    return {k: _clip((v - mu) / sd) for k, v in values.items()}


# ── data gathering ────────────────────────────────────────────────────────

def _gather(fred: FredClient, cot: CotClient, prices: PriceClient,
            *, as_of: date | None = None, price_period: str = "1y") -> dict[str, dict]:
    """Collect raw, freshness-gated factor inputs per currency.

    Returns {ccy: {factor_key: {"value": float, "as_of": iso|None, "stale": bool}}}.
    Cross-sectional standardisation happens later in compute_strength().

    `as_of` slices every source to that date (and judges freshness relative to
    it) so the SAME logic computes historical snapshots for the backfill.
    """
    raw: dict[str, dict] = {c: {} for c in CURRENCIES}

    for code, cfg in CURRENCIES.items():
        # --- Monetary: short rate level + trajectory, 10y bond level ---
        rs = _slice(_fred_series(fred, cfg.rate_short), as_of)
        lt = _latest(rs)
        if lt and _age_days(lt[1], as_of) <= MAX_AGE["rate"]:
            raw[code]["rate_level"] = {"value": lt[0], "as_of": lt[1].isoformat(), "stale": False}
            chg = _change_over(rs, 90)
            if chg is not None:
                raw[code]["rate_traj"] = {"value": chg, "as_of": lt[1].isoformat(), "stale": False}

        bd = _slice(_fred_series(fred, cfg.bond_10y), as_of)
        lt = _latest(bd)
        if lt and _age_days(lt[1], as_of) <= MAX_AGE["bond"]:
            raw[code]["bond_level"] = {"value": lt[0], "as_of": lt[1].isoformat(), "stale": False}

        # --- Growth: unemployment level (inverted) + trajectory (inverted) ---
        if cfg.unrate:
            ur = _slice(_fred_series(fred, cfg.unrate), as_of)
            lt = _latest(ur)
            if lt and _age_days(lt[1], as_of) <= MAX_AGE["unrate"]:
                raw[code]["unrate_level"] = {"value": -lt[0], "as_of": lt[1].isoformat(), "stale": False}
                chg = _change_over(ur, 180)
                if chg is not None:
                    raw[code]["unrate_traj"] = {"value": -chg, "as_of": lt[1].isoformat(), "stale": False}

        # --- Positioning: COT percentile + 4-week trend (USD derived later) ---
        if cfg.cot:
            try:
                s = cot.summary(cfg.cot, as_of=as_of)
                if s.get("status") == "ok" and s.get("data_age_days") is not None \
                        and s["data_age_days"] <= MAX_AGE["cot"]:
                    raw[code]["cot_pctile"] = {"value": float(s["percentile_3yr"]) - 50.0,
                                               "as_of": s.get("report_date"), "stale": False}
                    raw[code]["cot_trend"] = {"value": float(s.get("trend_4week", 0.0)),
                                              "as_of": s.get("report_date"), "stale": False}
            except Exception as e:
                log.warning("cs_cot_failed", ccy=code, error=str(e)[:80])

        # --- Commodity: exposure-weighted basket momentum ---
        if cfg.commodity:
            mom = 0.0
            ok = False
            asof = None
            for ticker, weight in cfg.commodity.items():
                try:
                    closes = _slice(prices.get_ohlc(ticker, period=price_period)["Close"], as_of)
                    z = _momentum_z(closes)
                    if z is not None:
                        mom += weight * z
                        ok = True
                        asof = closes.dropna().index[-1].date().isoformat()
                except Exception as e:
                    log.warning("cs_commod_failed", ccy=code, ticker=ticker, error=str(e)[:60])
            if ok:
                raw[code]["commodity"] = {"value": mom, "as_of": asof, "stale": False}

    return raw


def _risk_intensity(prices: PriceClient, *, as_of: date | None = None,
                    price_period: str = "1y") -> float:
    """Risk-off intensity: +z when VIX is elevated vs its trailing year."""
    try:
        vix = _slice(prices.get_ohlc("VIX", period=price_period)["Close"], as_of)
        return _level_z(vix)
    except Exception as e:
        log.warning("cs_vix_failed", error=str(e)[:80])
        return 0.0


# ── core computation ──────────────────────────────────────────────────────

def compute_strength(*, persist: bool = True, as_of: date | None = None,
                     price_period: str = "1y") -> dict:
    """Compute strength for all 8 majors. Pure + deterministic.

    `as_of` computes a HISTORICAL snapshot (all sources sliced to that date,
    freshness judged as-of then) — used by the backfill. `price_period` should
    be long enough (e.g. "3y") when backfilling so momentum windows have data.
    """
    fred = FredClient()
    cot = CotClient()
    prices = PriceClient()

    raw = _gather(fred, cot, prices, as_of=as_of, price_period=price_period)
    risk_intensity = _risk_intensity(prices, as_of=as_of, price_period=price_period)

    # USD positioning is derived: inverse of the average foreign COT percentile.
    foreign_pctiles = [raw[c]["cot_pctile"]["value"] for c in raw
                       if c != "USD" and "cot_pctile" in raw[c]]
    if foreign_pctiles:
        raw["USD"]["cot_pctile"] = {"value": -statistics.mean(foreign_pctiles),
                                    "as_of": "derived", "stale": False}

    # Cross-sectionally standardise each factor across currencies that have it.
    factor_keys = ["rate_level", "rate_traj", "bond_level", "unrate_level",
                   "unrate_traj", "cot_pctile", "cot_trend"]
    z: dict[str, dict[str, float]] = {c: {} for c in CURRENCIES}
    for fk in factor_keys:
        present = {c: raw[c][fk]["value"] for c in CURRENCIES if fk in raw[c]}
        for c, zc in _xsection_z(present).items():
            z[c][fk] = zc

    # Risk + Commodity pillars are absolute (already in z-units), NOT
    # cross-sectional — risk = tilt × intensity; commodity = the
    # exposure-weighted momentum z computed vs each commodity's own history.
    for c, cfg in CURRENCIES.items():
        z[c]["risk"] = _clip(cfg.safe_haven * risk_intensity)
        if "commodity" in raw[c]:
            z[c]["commodity"] = _clip(raw[c]["commodity"]["value"])

    # Assemble pillars per currency.
    pillar_map = {
        "monetary": ["rate_level", "bond_level", "rate_traj"],
        "growth": ["unrate_level", "unrate_traj"],
        "positioning": ["cot_pctile", "cot_trend"],
        "risk": ["risk"],
        "commodity": ["commodity"],
    }

    results: dict[str, dict] = {}
    for code, cfg in CURRENCIES.items():
        pillar_scores: dict[str, float] = {}
        for pillar, keys in pillar_map.items():
            vals = [z[code][k] for k in keys if k in z[code]]
            if pillar == "risk":  # always present (0 when calm / neutral tilt)
                pillar_scores[pillar] = round(z[code]["risk"], 3)
            elif vals:
                pillar_scores[pillar] = round(sum(vals) / len(vals), 3)

        # Composite = weight-renormalised average of available pillars.
        wsum = sum(PILLAR_WEIGHTS[p] for p in pillar_scores)
        comp_z = (sum(PILLAR_WEIGHTS[p] * s for p, s in pillar_scores.items()) / wsum) if wsum else 0.0
        composite = round(max(-100.0, min(100.0, comp_z * COMPOSITE_SCALE)), 1)

        results[code] = {
            "code": code,
            "name": cfg.name,
            "composite": composite,
            "pillars": {p: round(s * COMPOSITE_SCALE, 1) for p, s in pillar_scores.items()},
            "available_pillars": sorted(pillar_scores.keys()),
            "indicators": {k: raw[code][k] for k in raw[code]},
        }

    # Rank (1 = strongest) and label.
    ordered = sorted(results, key=lambda c: results[c]["composite"], reverse=True)
    for rank, code in enumerate(ordered, start=1):
        results[code]["rank"] = rank
        results[code]["label"] = _label(results[code]["composite"])

    # Trend from stored history.
    hist = _load()
    for code in results:
        results[code]["trend"] = _trend(hist.get(code, []), results[code]["composite"])

    out = {
        "as_of": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "run_date": date.today().isoformat(),
        "weights": PILLAR_WEIGHTS,
        "risk_intensity": round(risk_intensity, 3),
        "currencies": {c: results[c] for c in ordered},
    }
    if persist:
        _append_snapshot(out)
    return out


def _label(composite: float) -> str:
    if composite >= 50:
        return "Strong"
    if composite >= 15:
        return "Slightly Strong"
    if composite > -15:
        return "Neutral"
    if composite > -50:
        return "Slightly Weak"
    return "Weak"


def _trend(history: list[dict], current: float) -> dict:
    """Trend vs the trailing average of stored composites."""
    if len(history) < 3:
        return {"change": 0.0, "label": "new"}
    recent = [h["composite"] for h in history[-20:]]
    baseline = sum(recent) / len(recent)
    change = round(current - baseline, 1)
    label = "strengthening" if change > 5 else "weakening" if change < -5 else "stable"
    return {"change": change, "label": label}


# ── storage (atomic, deterministic ordering) ──────────────────────────────

def _load() -> dict[str, list[dict]]:
    if not _PATH.exists():
        return {}
    try:
        return json.loads(_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: dict) -> None:
    _PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(_PATH.parent), suffix=".tmp")
    try:
        with open(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        Path(tmp).replace(_PATH)
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise


def _append_snapshot(out: dict) -> None:
    """Append today's composite + pillars to each currency's history."""
    with _LOCK:
        hist = _load()
        run_date = out["run_date"]
        for code, data in out["currencies"].items():
            entries = hist.setdefault(code, [])
            entries = [e for e in entries if e.get("date") != run_date]  # replace same-day
            entries.append({
                "date": run_date,
                "composite": data["composite"],
                "rank": data["rank"],
                "pillars": data["pillars"],
            })
            hist[code] = entries[-_MAX_HISTORY:]
        _save(hist)


def load_history(code: str, n: int | None = None) -> list[dict]:
    """Return stored daily snapshots for a currency (oldest first)."""
    entries = _load().get(code, [])
    return entries[-n:] if n else entries


if __name__ == "__main__":
    import sys
    res = compute_strength(persist="--persist" in sys.argv)
    print(f"as_of {res['as_of']}  risk_intensity={res['risk_intensity']}")
    for code, d in res["currencies"].items():
        pillars = " ".join(f"{p[:4]}={v:+.0f}" for p, v in d["pillars"].items())
        print(f"  #{d['rank']} {code} {d['composite']:+6.1f} {d['label']:16s} [{pillars}]")
