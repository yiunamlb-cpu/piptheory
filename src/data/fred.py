"""FRED wrapper — curated macro time series for the watchlist.

Wraps fredapi with retry, simple file caching, and a curated dictionary of
the FRED IDs we actually use. Agents and the data pipeline call this; nothing
calls fredapi directly.
"""
from __future__ import annotations

import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

import pandas as pd
import structlog
from fredapi import Fred
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import STATE_DIR, settings

log = structlog.get_logger(__name__)

# Cache on disk so we don't hammer FRED. Series are revised infrequently;
# fetching at most once per day per series is plenty.
_CACHE_DIR = STATE_DIR / "fred_cache"
_CACHE_DIR.mkdir(exist_ok=True)
_DEFAULT_CACHE_TTL = timedelta(hours=12)


# Curated series — the FRED IDs that actually feed our macro reasoning.
# Grouped semantically. Reference: https://fred.stlouisfed.org
MACRO_SERIES: dict[str, dict[str, str]] = {
    "inflation": {
        "cpi_headline": "CPIAUCSL",          # CPI All Urban, SA
        "cpi_core": "CPILFESL",              # CPI ex food & energy, SA
        "pce_headline": "PCEPI",
        "pce_core": "PCEPILFE",
        "sticky_cpi": "CORESTICKM158SFRBATL",  # Atlanta Fed sticky CPI YoY
        "breakeven_5y5y": "T5YIFR",
        "breakeven_10y": "T10YIE",
        "ahe_yoy": "CES0500000008",          # Avg Hourly Earnings, all employees, total private (level — convert to YoY)
    },
    "growth": {
        "real_gdp": "GDPC1",
        "nfp_total": "PAYEMS",
        "unrate": "UNRATE",
        "ism_pmi_proxy": "INDPRO",            # Industrial Production (ISM is paywalled)
        "retail_sales": "RSXFS",
        "claims_initial": "ICSA",
    },
    "rates": {
        "ffr_effective": "DFF",
        "ffr_target_upper": "DFEDTARU",
        "ust_2y": "DGS2",
        "ust_10y": "DGS10",
        "ust_30y": "DGS30",
        "real_10y": "DFII10",                 # 10y TIPS yield
    },
    "fx": {
        "dxy_broad": "DTWEXBGS",              # broad trade-weighted dollar
        "dxy_advanced": "DTWEXAFEGS",         # advanced foreign econ trade-weighted
    },
    "liquidity": {
        "fed_balance_sheet": "WALCL",         # All Federal Reserve banks total assets
        "rrp_outstanding": "RRPONTSYD",       # Overnight Reverse Repo
        "tga": "WTREGEN",                     # Treasury General Account
        "bank_reserves": "WRESBAL",           # Reserve balances at Federal Reserve banks
    },
    "credit": {
        "hy_oas": "BAMLH0A0HYM2",             # ICE BofA US High Yield OAS
        "ig_oas": "BAMLC0A0CM",               # ICE BofA US Corporate OAS
    },
}


def all_series_ids() -> dict[str, str]:
    """Flatten MACRO_SERIES into {short_name: fred_id}."""
    flat: dict[str, str] = {}
    for group in MACRO_SERIES.values():
        flat.update(group)
    return flat


class FredClient:
    """Curated FRED wrapper. Use `series('cpi_headline')` for known names
    or `raw_series('CPIAUCSL')` for arbitrary FRED IDs."""

    def __init__(self, api_key: str | None = None, cache_ttl: timedelta = _DEFAULT_CACHE_TTL):
        key = api_key or settings.fred_api_key
        if not key:
            raise RuntimeError(
                "FRED_API_KEY missing. Set it in .env (get one free at "
                "https://fred.stlouisfed.org/docs/api/api_key.html)"
            )
        self._fred = Fred(api_key=key)
        self._cache_ttl = cache_ttl
        self._name_to_id = all_series_ids()

    def _cache_path(self, series_id: str) -> Path:
        return _CACHE_DIR / f"{series_id}.pkl"

    def _load_cache(self, series_id: str) -> pd.Series | None:
        path = self._cache_path(series_id)
        if not path.exists():
            return None
        age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
        if age > self._cache_ttl:
            return None
        try:
            with path.open("rb") as f:
                return pickle.load(f)
        except (pickle.PickleError, EOFError):
            return None

    def _save_cache(self, series_id: str, data: pd.Series) -> None:
        with self._cache_path(series_id).open("wb") as f:
            pickle.dump(data, f)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _fetch_remote(self, series_id: str, **kwargs) -> pd.Series:
        log.info("fred_fetch", series_id=series_id)
        return self._fred.get_series(series_id, **kwargs)

    def raw_series(
        self,
        series_id: str,
        *,
        observation_start: str | None = None,
        use_cache: bool = True,
    ) -> pd.Series:
        """Fetch a FRED series by raw FRED ID. Cached for cache_ttl."""
        if use_cache:
            cached = self._load_cache(series_id)
            if cached is not None:
                return cached

        data = self._fetch_remote(series_id, observation_start=observation_start)
        self._save_cache(series_id, data)
        return data

    def series(
        self,
        name: str,
        *,
        observation_start: str | None = None,
        use_cache: bool = True,
    ) -> pd.Series:
        """Fetch a series by curated short name (e.g. 'cpi_headline')."""
        if name not in self._name_to_id:
            raise KeyError(
                f"Unknown series name '{name}'. Known: {sorted(self._name_to_id)}"
            )
        return self.raw_series(
            self._name_to_id[name],
            observation_start=observation_start,
            use_cache=use_cache,
        )

    def latest(self, name: str) -> tuple[pd.Timestamp, float]:
        """Return (last_date, last_value) for a curated series."""
        s = self.series(name)
        s = s.dropna()
        return s.index[-1], float(s.iloc[-1])

    def yoy(self, name: str, periods: int = 12) -> pd.Series:
        """Year-over-year percent change. Defaults to 12 monthly periods.

        Use `periods=4` for quarterly series, `periods=52` for weekly.
        """
        s = self.series(name).dropna()
        return (s / s.shift(periods) - 1.0) * 100.0

    def snapshot(self, names: Iterable[str] | None = None) -> pd.DataFrame:
        """Return a snapshot DataFrame with the latest value of each series.

        Useful for handing the agent a 'state of macro right now' summary.
        """
        names = list(names) if names else list(self._name_to_id)
        rows = []
        for name in names:
            try:
                d, v = self.latest(name)
                rows.append({"series": name, "fred_id": self._name_to_id[name],
                             "date": d.date().isoformat(), "value": v})
            except Exception as e:
                log.warning("snapshot_failed", series=name, error=str(e))
                rows.append({"series": name, "fred_id": self._name_to_id[name],
                             "date": None, "value": None})
        return pd.DataFrame(rows)
