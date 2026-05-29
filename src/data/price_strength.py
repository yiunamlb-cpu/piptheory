"""Price-based relative currency strength — the "Currency Performance" chart.

Deliberately DIFFERENT from the fundamental meter: this is purely what PRICES
did. For each major currency we build its value-vs-USD index at daily and
4-hour resolution; the frontend rebases to the selected window's start and
subtracts the cross-sectional mean, so the lines fan out from a common point
(relative performance vs the basket).

Deterministic, free (Yahoo Finance), no LLM.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pandas as pd
import structlog
import yfinance as yf

from src.config import STATE_DIR

log = structlog.get_logger(__name__)

_PATH = STATE_DIR / "price_strength.json"

# currency -> (Yahoo ticker, invert) for its value-vs-USD series. USD is flat.
_PAIRS = {
    "EUR": ("EURUSD=X", False), "GBP": ("GBPUSD=X", False),
    "AUD": ("AUDUSD=X", False), "NZD": ("NZDUSD=X", False),
    "JPY": ("JPY=X", True), "CAD": ("USDCAD=X", True), "CHF": ("USDCHF=X", True),
}
CCYS = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD"]


def _fetch(ticker: str, period: str, interval: str) -> pd.Series | None:
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False,
                         auto_adjust=False, multi_level_index=False)
        if df is None or df.empty:
            return None
        s = df["Close"].dropna()
        s.index = pd.to_datetime(s.index)
        return s if not s.empty else None
    except Exception as e:
        log.warning("ps_fetch_failed", ticker=ticker, error=str(e)[:80])
        return None


def _build(period: str, interval: str, resample: str | None = None) -> dict | None:
    cols: dict[str, pd.Series] = {}
    for ccy, (tk, inv) in _PAIRS.items():
        s = _fetch(tk, period, interval)
        if s is None:
            continue
        if resample:
            s = s.resample(resample).last().dropna()
        cols[ccy] = (1.0 / s) if inv else s
    if not cols:
        return None
    df = pd.DataFrame(cols).sort_index().ffill().dropna()
    if df.empty or len(df) < 5:
        return None
    df["USD"] = 1.0
    df = df[[c for c in CCYS if c in df.columns]]
    fmt = "%Y-%m-%d" if interval == "1d" else "%Y-%m-%dT%H:%M"
    return {
        "t": [d.strftime(fmt) for d in df.index],
        "ix": {c: [round(float(v), 6) for v in df[c].values] for c in df.columns},
    }


def compute_price_strength(*, persist: bool = True) -> dict:
    out = {
        "1d": _build("2y", "1d"),
        "4h": _build("3mo", "1h", resample="4h"),
    }
    if persist:
        _save(out)
    return out


def _save(out: dict) -> None:
    _PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(_PATH.parent), suffix=".tmp")
    try:
        with open(fd, "w", encoding="utf-8") as f:
            json.dump(out, f, separators=(",", ":"))
        Path(tmp).replace(_PATH)
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise


def load_price_strength() -> dict | None:
    if not _PATH.exists():
        return None
    try:
        return json.loads(_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


if __name__ == "__main__":
    import sys
    r = compute_price_strength(persist="--persist" in sys.argv)
    for k in ("1d", "4h"):
        d = r.get(k)
        print(f"{k}: {len(d['t']) if d else 0} points, ccys={list(d['ix'].keys()) if d else []}"
              f"{', ' + d['t'][0] + '..' + d['t'][-1] if d else ''}")
