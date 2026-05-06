"""Data plane — wrappers around FRED, CFTC, prices, etc. Returns clean pandas DataFrames."""

from src.data.fred import FredClient, MACRO_SERIES
from src.data.cot import CotClient, WATCHLIST_COT_CODES
from src.data.prices import PriceClient, SetupContext, INSTRUMENT_TO_TICKER
from src.data.events import (
    CalendarEvent,
    load_events,
    render_event_block,
    upcoming_events,
)

__all__ = [
    "FredClient", "MACRO_SERIES",
    "CotClient", "WATCHLIST_COT_CODES",
    "PriceClient", "SetupContext", "INSTRUMENT_TO_TICKER",
    "CalendarEvent", "load_events", "render_event_block", "upcoming_events",
]
