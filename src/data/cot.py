"""COT report wrapper — CFTC Commitment of Traders data, weekly.

Wraps `cot_reports` to fetch positioning data per watchlist instrument, with
the CFTC market codes mapped to our instrument names. Adds 3-year percentile
calculation per `playbook/positioning.md`.
"""
from __future__ import annotations

import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

import pandas as pd
import structlog

from src.config import STATE_DIR
from src.data.freshness import Freshness

log = structlog.get_logger(__name__)

_CACHE_DIR = STATE_DIR / "cot_cache"
_CACHE_DIR.mkdir(exist_ok=True)
_CACHE_TTL = timedelta(days=3)  # CFTC publishes weekly; refresh aggressively but not constantly


# CFTC Market Codes for our watchlist instruments.
# Sourced from CFTC contract specs. Format: "Name in CFTC report → friendly name"
WATCHLIST_COT_CODES: dict[str, dict[str, str]] = {
    "EURUSD": {
        "cftc_market": "EURO FX - CHICAGO MERCANTILE EXCHANGE",
        "report_type": "TFF",  # Traders in Financial Futures
    },
    "USDJPY": {
        "cftc_market": "JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE",
        "report_type": "TFF",
    },
    "GBPUSD": {
        "cftc_market": "BRITISH POUND - CHICAGO MERCANTILE EXCHANGE",
        "report_type": "TFF",
    },
    "AUDUSD": {
        "cftc_market": "AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE",
        "report_type": "TFF",
    },
    # --- Added for the currency-strength meter (8 majors) ---
    "USDCAD": {
        "cftc_market": "CANADIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE",
        "report_type": "TFF",
    },
    "USDCHF": {
        "cftc_market": "SWISS FRANC - CHICAGO MERCANTILE EXCHANGE",
        "report_type": "TFF",
    },
    "NZDUSD": {
        "cftc_market": "NZ DOLLAR - CHICAGO MERCANTILE EXCHANGE",
        "report_type": "TFF",
    },
    "GC": {
        "cftc_market": "GOLD - COMMODITY EXCHANGE INC.",
        "report_type": "Disaggregated",
    },
    "CL": {
        "cftc_market": "WTI-PHYSICAL - NEW YORK MERCANTILE EXCHANGE",
        "report_type": "Disaggregated",
    },
    "ZN": {
        "cftc_market": "UST 10Y NOTE - CHICAGO BOARD OF TRADE",
        "report_type": "TFF",
    },
    "ES": {
        "cftc_market": "E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE",
        "report_type": "TFF",
    },
    "NQ": {
        "cftc_market": "NASDAQ-100 E-MINI - CHICAGO MERCANTILE EXCHANGE",
        "report_type": "TFF",
    },
    "DXY": {
        # Note: ICE Dollar Index is on a separate report (ICE futures)
        # cot_reports may or may not cover this — fallback to weighted EUR/JPY/GBP positioning
        "cftc_market": "USD INDEX - ICE FUTURES U.S.",
        "report_type": "Legacy",
    },
}

ReportType = Literal["TFF", "Disaggregated", "Legacy"]


def _fetch_cot_reports(report_type: ReportType, year: int) -> pd.DataFrame:
    """Fetch the full annual COT report from CFTC for a given report type and year.

    Uses the cot_reports library. Cached for _CACHE_TTL.
    """
    cache_key = f"{report_type}_{year}"
    cache_path = _CACHE_DIR / f"{cache_key}.pkl"

    if cache_path.exists():
        age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        if age < _CACHE_TTL:
            with cache_path.open("rb") as f:
                return pickle.load(f)

    try:
        import cot_reports as cr
    except ImportError as e:
        raise ImportError(
            "cot_reports not installed. pip install cot-reports"
        ) from e

    log.info("cot_fetch", report_type=report_type, year=year)
    type_map = {
        "TFF": "traders_in_financial_futures_fut",
        "Disaggregated": "disaggregated_fut",
        "Legacy": "legacy_fut",
    }
    df = cr.cot_year(year=year, cot_report_type=type_map[report_type])

    with cache_path.open("wb") as f:
        pickle.dump(df, f)

    return df


class CotClient:
    """Fetches COT data for our watchlist with 3-year percentile calculations."""

    def __init__(self, lookback_years: int = 3):
        self.lookback_years = lookback_years

    def _fetch_history(self, report_type: ReportType) -> pd.DataFrame:
        """Fetch the last N years for a given report type, concatenated."""
        current = datetime.now().year
        years = list(range(current - self.lookback_years, current + 1))
        frames = []
        for y in years:
            try:
                df = _fetch_cot_reports(report_type, y)
                frames.append(df)
            except Exception as e:
                log.warning("cot_year_fetch_failed", report_type=report_type, year=y, error=str(e))
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True)

    def for_instrument(self, instrument: str) -> pd.DataFrame:
        """Return raw weekly COT history for an instrument over the lookback window."""
        if instrument not in WATCHLIST_COT_CODES:
            raise KeyError(
                f"Unknown instrument '{instrument}'. Known: {sorted(WATCHLIST_COT_CODES)}"
            )
        meta = WATCHLIST_COT_CODES[instrument]
        report_type = meta["report_type"]
        market = meta["cftc_market"]

        df = self._fetch_history(report_type)  # type: ignore[arg-type]
        if df.empty:
            return df

        # Column names vary by report; the market description column is consistent
        market_col_candidates = [
            "Market_and_Exchange_Names",
            "market_and_exchange_names",
            "Market and Exchange Names",
        ]
        market_col = next((c for c in market_col_candidates if c in df.columns), None)
        if market_col is None:
            log.warning("cot_market_col_not_found", columns=list(df.columns)[:10])
            return pd.DataFrame()

        filtered = df[df[market_col].str.upper().str.contains(market.upper(), na=False)].copy()
        # Date column also varies
        date_col_candidates = ["Report_Date_as_YYYY-MM-DD", "report_date_as_yyyy-mm-dd",
                               "As_of_Date_In_Form_YYMMDD", "as_of_date_in_form_yymmdd"]
        date_col = next((c for c in date_col_candidates if c in filtered.columns), None)
        if date_col:
            filtered = filtered.rename(columns={date_col: "report_date"})
            filtered["report_date"] = pd.to_datetime(filtered["report_date"], errors="coerce")
            filtered = filtered.sort_values("report_date").reset_index(drop=True)

        return filtered

    def summary(self, instrument: str, as_of=None) -> dict:
        """Return a structured positioning summary for an instrument.

        Output matches the schema fed into the Positioning Analyst agent.

        `as_of` (a datetime.date): if given, only consider reports up to and
        including that date — used by the strength-meter historical backfill
        so percentile/trend reflect what was knowable then.
        """
        df = self.for_instrument(instrument)
        if df.empty:
            return {
                "instrument": instrument,
                "status": "no_data",
                "note": "COT data not available for this instrument or report type.",
            }

        if as_of is not None and "report_date" in df.columns:
            df = df[df["report_date"].dt.date <= as_of].copy()
            if df.empty:
                return {"instrument": instrument, "status": "no_data",
                        "note": f"No COT reports on/before {as_of}."}

        # Try common column names for "Leveraged Funds" net position
        # TFF format: "Lev_Money_Positions_Long_All", "Lev_Money_Positions_Short_All"
        # Disaggregated: "M_Money_Positions_Long_All", "M_Money_Positions_Short_All"
        long_col = next((c for c in df.columns if "Lev_Money_Positions_Long" in c
                         or "M_Money_Positions_Long" in c
                         or "NonComm_Positions_Long_All" in c), None)
        short_col = next((c for c in df.columns if "Lev_Money_Positions_Short" in c
                          or "M_Money_Positions_Short" in c
                          or "NonComm_Positions_Short_All" in c), None)

        if not long_col or not short_col:
            return {
                "instrument": instrument,
                "status": "schema_unrecognized",
                "available_columns_sample": [c for c in df.columns if "Position" in c][:10],
            }

        df = df.copy()
        df["net"] = pd.to_numeric(df[long_col], errors="coerce") - pd.to_numeric(df[short_col], errors="coerce")
        df = df.dropna(subset=["net"])
        if df.empty:
            return {"instrument": instrument, "status": "all_nan"}

        latest_net = float(df["net"].iloc[-1])
        latest_date = df["report_date"].iloc[-1] if "report_date" in df else None

        # 3-year percentile of latest value
        pct = float((df["net"] < latest_net).mean() * 100)

        # 4-week trend in net
        trend_4w = float(df["net"].iloc[-1] - df["net"].iloc[-4]) if len(df) >= 4 else 0.0

        # Persistence: how many of the last 6 weeks were >90th or <10th percentile
        if len(df) >= 6:
            recent_pcts = df["net"].rolling(window=len(df), min_periods=1).apply(
                lambda x: (x < x.iloc[-1]).mean() * 100, raw=False
            ).iloc[-6:]
            extreme_weeks = int(((recent_pcts > 90) | (recent_pcts < 10)).sum())
        else:
            extreme_weeks = 0

        # Freshness: COT publishes Friday for Tuesday close. Use report_date
        # as the observation_date and approximate release_date as +3 days.
        if latest_date is not None and not pd.isna(latest_date):
            obs_date = latest_date.date() if hasattr(latest_date, "date") else latest_date
            from datetime import timedelta
            release_date = obs_date + timedelta(days=3)
            fresh = Freshness.from_observation(obs_date, release_date=release_date)
            freshness_label = fresh.label
            freshness_tag = fresh.render()
            data_age_days = fresh.age_days
        else:
            freshness_label = "stale"
            freshness_tag = "[unavailable]"
            data_age_days = None

        return {
            "instrument": instrument,
            "status": "ok",
            "report_date": latest_date.isoformat() if latest_date is not None and not pd.isna(latest_date) else None,
            "data_age_days": data_age_days,
            "freshness_label": freshness_label,
            "freshness_tag": freshness_tag,
            "primary_category": long_col.replace("_Positions_Long_All", "").replace("_Long_All", ""),
            "net_position": int(latest_net),
            "percentile_3yr": round(pct, 1),
            "trend_4week": int(trend_4w),
            "weeks_at_extreme_in_last_6": extreme_weeks,
            "long_col": long_col,
            "short_col": short_col,
        }
