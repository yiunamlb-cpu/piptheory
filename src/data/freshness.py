"""Data freshness labeling. One small helper that every data wrapper uses
to attach a freshness signal to surfaced data points.

Agents are instructed (via context.py) to downweight conclusions derived
primarily from `stale` data. The labels are intentionally coarse:

  fresh   - released ≤ 2 calendar days ago, OR a daily series (rates, breakevens)
  recent  - released ≤ 14 days ago (typical weekly series)
  stale   - released > 14 days ago (monthly series past their freshness window)

Series-specific overrides are supported because, e.g., a "stale" daily-rate
print would be wrong: daily series are by definition fresh on the latest obs.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Literal

FreshnessLabel = Literal["fresh", "recent", "stale"]


# Series whose cadence is daily/intraday — never label "stale" if we have a
# value within the last 5 calendar days.
_DAILY_CADENCE_FRED_IDS = {
    "DFF", "DFEDTARU", "DGS2", "DGS10", "DGS30", "DFII10",
    "T5YIFR", "T10YIE", "DTWEXBGS", "DTWEXAFEGS",
    "BAMLH0A0HYM2", "BAMLC0A0CM",
}


def _to_date(d: date | datetime | str) -> date:
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, str):
        return date.fromisoformat(d[:10])
    return d


def label_for_release(
    release_date: date | datetime | str,
    *,
    today: date | None = None,
    series_id: str | None = None,
) -> FreshnessLabel:
    """Coarse freshness label based on release age.

    Args:
        release_date: when the data point was published (or observation date
            if release date is not separately tracked).
        today: override for testing; defaults to today's UTC date.
        series_id: optional FRED ID for cadence-aware override.
    """
    today = today or date.today()
    rd = _to_date(release_date)
    age_days = (today - rd).days

    if series_id and series_id in _DAILY_CADENCE_FRED_IDS:
        # Daily series: fresh up to 5 days, recent up to 10, then stale.
        if age_days <= 5:
            return "fresh"
        if age_days <= 10:
            return "recent"
        return "stale"

    if age_days <= 2:
        return "fresh"
    if age_days <= 14:
        return "recent"
    return "stale"


@dataclass(frozen=True)
class Freshness:
    """Bundle the metadata an agent needs to weigh a single data point."""
    observation_date: date            # the date the value is for
    release_date: date | None         # when it was published; falls back to obs date
    label: FreshnessLabel
    age_days: int
    note: str = ""                    # optional human-readable hint

    @classmethod
    def from_observation(
        cls,
        observation_date: date | datetime | str,
        *,
        release_date: date | datetime | str | None = None,
        today: date | None = None,
        series_id: str | None = None,
        note: str = "",
    ) -> "Freshness":
        today = today or date.today()
        obs = _to_date(observation_date)
        rd = _to_date(release_date) if release_date is not None else obs
        return cls(
            observation_date=obs,
            release_date=rd,
            label=label_for_release(rd, today=today, series_id=series_id),
            age_days=(today - rd).days,
            note=note,
        )

    def render(self) -> str:
        """One-line tag for inclusion in agent input messages."""
        rd_part = f"released {self.release_date.isoformat()}" if self.release_date else ""
        return f"[{self.label} · obs {self.observation_date.isoformat()} · {rd_part} · {self.age_days}d old]"
