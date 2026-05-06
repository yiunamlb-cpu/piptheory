"""Data plane — wrappers around FRED, CFTC, etc. Returns clean pandas DataFrames."""

from src.data.fred import FredClient, MACRO_SERIES
from src.data.cot import CotClient, WATCHLIST_COT_CODES

__all__ = ["FredClient", "MACRO_SERIES", "CotClient", "WATCHLIST_COT_CODES"]
