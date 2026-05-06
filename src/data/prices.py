"""Price wrapper — daily OHLC + ATR + simple S/R for the active-universe
instruments (ES, NQ, GC). Uses yfinance for futures continuous contracts.

This is the data dependency for the Tradability Filter (Layer 4b). The filter
needs *structural* context — where is price, how volatile, where are the
recent levels — to decide whether a macro-aligned bias is currently tradable.

This wrapper does NOT supply tick data, real-time prices, or anything used
for execution. It supplies daily OHLC for daily-cadence structural review.
"""
from __future__ import annotations

import pickle
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import structlog
import yfinance as yf
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import STATE_DIR

log = structlog.get_logger(__name__)

_CACHE_DIR = STATE_DIR / "prices_cache"
_CACHE_DIR.mkdir(exist_ok=True)
_CACHE_TTL = timedelta(hours=6)

# Active universe → yfinance ticker. Continuous front-month futures.
# ES, NQ, GC = US500, NAS100, XAUUSD on FTMO/MT5 in symbol terms.
INSTRUMENT_TO_TICKER: dict[str, str] = {
    "ES": "ES=F",            # E-mini S&P 500 continuous
    "NQ": "NQ=F",            # E-mini Nasdaq 100 continuous
    "GC": "GC=F",            # Gold continuous
    "CL": "CL=F",            # WTI Crude continuous
    "ZN": "ZN=F",            # 10Y Treasury Note continuous
    "DXY": "DX-Y.NYB",       # ICE Dollar Index
    "EURUSD": "EURUSD=X",
    "USDJPY": "JPY=X",       # yfinance uses JPY=X for USD/JPY
    "GBPUSD": "GBPUSD=X",
    "AUDUSD": "AUDUSD=X",
}


@dataclass
class SetupContext:
    """Structural context for one instrument, suitable for the Tradability Filter."""
    instrument: str
    as_of: str
    current_price: float
    open_today: float
    high_today: float
    low_today: float
    atr_14: float
    atr_pct_of_price: float
    recent_5d_range: tuple[float, float]
    recent_20d_range: tuple[float, float]
    key_support_20d: float
    key_resistance_20d: float
    sma_20: float
    sma_50: float
    trend_direction: str         # "up" | "down" | "sideways"
    pct_change_5d: float
    pct_change_20d: float
    distance_from_20d_high_pct: float
    distance_from_20d_low_pct: float

    def to_dict(self) -> dict:
        return {
            "instrument": self.instrument,
            "as_of": self.as_of,
            "current_price": round(self.current_price, 4),
            "today": {
                "open": round(self.open_today, 4),
                "high": round(self.high_today, 4),
                "low": round(self.low_today, 4),
            },
            "atr_14": round(self.atr_14, 4),
            "atr_pct_of_price": round(self.atr_pct_of_price, 3),
            "ranges": {
                "5d": [round(self.recent_5d_range[0], 4), round(self.recent_5d_range[1], 4)],
                "20d": [round(self.recent_20d_range[0], 4), round(self.recent_20d_range[1], 4)],
            },
            "levels": {
                "support_20d": round(self.key_support_20d, 4),
                "resistance_20d": round(self.key_resistance_20d, 4),
                "sma_20": round(self.sma_20, 4),
                "sma_50": round(self.sma_50, 4),
            },
            "trend": {
                "direction": self.trend_direction,
                "pct_5d": round(self.pct_change_5d, 3),
                "pct_20d": round(self.pct_change_20d, 3),
                "distance_from_20d_high_pct": round(self.distance_from_20d_high_pct, 3),
                "distance_from_20d_low_pct": round(self.distance_from_20d_low_pct, 3),
            },
        }


class PriceClient:
    """Daily OHLC + structural context for the active universe."""

    def __init__(self, cache_ttl: timedelta = _CACHE_TTL):
        self._cache_ttl = cache_ttl

    def _cache_path(self, ticker: str) -> Path:
        safe = ticker.replace("=", "_").replace(".", "_")
        return _CACHE_DIR / f"{safe}.pkl"

    def _load_cache(self, ticker: str) -> pd.DataFrame | None:
        p = self._cache_path(ticker)
        if not p.exists():
            return None
        age = datetime.now() - datetime.fromtimestamp(p.stat().st_mtime)
        if age > self._cache_ttl:
            return None
        try:
            with p.open("rb") as f:
                return pickle.load(f)
        except (pickle.PickleError, EOFError):
            return None

    def _save_cache(self, ticker: str, df: pd.DataFrame) -> None:
        with self._cache_path(ticker).open("wb") as f:
            pickle.dump(df, f)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _fetch_remote(self, ticker: str, period: str) -> pd.DataFrame:
        log.info("yfinance_fetch", ticker=ticker, period=period)
        df = yf.download(
            ticker,
            period=period,
            interval="1d",
            progress=False,
            auto_adjust=False,
            multi_level_index=False,
        )
        if df is None or df.empty:
            raise RuntimeError(f"yfinance returned empty data for {ticker}")
        return df

    def get_ohlc(self, instrument: str, period: str = "90d") -> pd.DataFrame:
        ticker = INSTRUMENT_TO_TICKER.get(instrument)
        if not ticker:
            raise KeyError(f"No ticker mapping for instrument '{instrument}'. "
                           f"Known: {sorted(INSTRUMENT_TO_TICKER)}")
        cached = self._load_cache(ticker)
        if cached is not None:
            return cached
        df = self._fetch_remote(ticker, period)
        self._save_cache(ticker, df)
        return df

    @staticmethod
    def _atr(df: pd.DataFrame, period: int = 14) -> float:
        high_low = df["High"] - df["Low"]
        high_close_prev = (df["High"] - df["Close"].shift(1)).abs()
        low_close_prev = (df["Low"] - df["Close"].shift(1)).abs()
        tr = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
        return float(tr.rolling(period).mean().iloc[-1])

    def get_setup_context(self, instrument: str) -> SetupContext:
        df = self.get_ohlc(instrument, period="90d")
        if df.empty or len(df) < 21:
            raise RuntimeError(
                f"Insufficient OHLC data for {instrument}: {len(df)} rows"
            )

        last = df.iloc[-1]
        as_of = df.index[-1].date().isoformat()
        current = float(last["Close"])

        last_5 = df.tail(5)
        last_20 = df.tail(20)
        last_50 = df.tail(50) if len(df) >= 50 else df

        atr_14 = self._atr(df, 14)

        sma_20 = float(df["Close"].rolling(20).mean().iloc[-1])
        sma_50 = (
            float(df["Close"].rolling(50).mean().iloc[-1])
            if len(df) >= 50 else sma_20
        )

        if current > sma_20 > sma_50:
            trend = "up"
        elif current < sma_20 < sma_50:
            trend = "down"
        else:
            trend = "sideways"

        high_20 = float(last_20["High"].max())
        low_20 = float(last_20["Low"].min())

        pct_5d = float((current / df["Close"].iloc[-6] - 1.0) * 100) if len(df) >= 6 else 0.0
        pct_20d = float((current / df["Close"].iloc[-21] - 1.0) * 100) if len(df) >= 21 else 0.0
        dist_high = float((current / high_20 - 1.0) * 100)
        dist_low = float((current / low_20 - 1.0) * 100)

        return SetupContext(
            instrument=instrument,
            as_of=as_of,
            current_price=current,
            open_today=float(last["Open"]),
            high_today=float(last["High"]),
            low_today=float(last["Low"]),
            atr_14=atr_14,
            atr_pct_of_price=(atr_14 / current * 100) if current else 0.0,
            recent_5d_range=(float(last_5["Low"].min()), float(last_5["High"].max())),
            recent_20d_range=(low_20, high_20),
            key_support_20d=low_20,
            key_resistance_20d=high_20,
            sma_20=sma_20,
            sma_50=sma_50,
            trend_direction=trend,
            pct_change_5d=pct_5d,
            pct_change_20d=pct_20d,
            distance_from_20d_high_pct=dist_high,
            distance_from_20d_low_pct=dist_low,
        )
