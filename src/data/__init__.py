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
from src.data.recent_events import (
    RecentEvent,
    add_event as add_recent_event,
    delete_event as delete_recent_event,
    load_recent_events,
    recent_events_for_prompt,
    render_recent_events_block,
)
from src.data import regime, score_history, thesis_tracker  # noqa: F401

__all__ = [
    "FredClient", "MACRO_SERIES",
    "CotClient", "WATCHLIST_COT_CODES",
    "PriceClient", "SetupContext", "INSTRUMENT_TO_TICKER",
    "CalendarEvent", "load_events", "render_event_block", "upcoming_events",
    "RecentEvent",
    "add_recent_event", "delete_recent_event",
    "load_recent_events", "recent_events_for_prompt", "render_recent_events_block",
]
