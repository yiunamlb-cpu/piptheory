"""Economic event calendar reader.

Reads `data/events.yaml` (manually maintained), filters to events within a
configurable lookahead window, and returns structured records the
Tradability Filter agent can use as ground truth.

This is the stopgap version of Commit C. A future iteration could replace
the YAML with a real calendar API; the interface stays the same.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import yaml

from src.config import ROOT


@dataclass
class CalendarEvent:
    date: date
    time: str
    name: str
    severity: str       # high | medium | low
    category: str
    affects: list[str]
    notes: str

    @property
    def days_from_today(self) -> int:
        return (self.date - date.today()).days

    def to_dict(self) -> dict:
        return {
            "date": self.date.isoformat(),
            "time": self.time,
            "name": self.name,
            "severity": self.severity,
            "category": self.category,
            "affects": self.affects,
            "notes": self.notes,
            "days_from_today": self.days_from_today,
        }


_EVENTS_PATH = ROOT / "data" / "events.yaml"


def load_events(path: Path | None = None) -> list[CalendarEvent]:
    """Load all events from data/events.yaml, sorted by date ascending."""
    p = path or _EVENTS_PATH
    if not p.exists():
        return []
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    raw = data.get("events", []) or []
    out: list[CalendarEvent] = []
    for r in raw:
        try:
            d = r["date"]
            if isinstance(d, str):
                d = date.fromisoformat(d)
            out.append(CalendarEvent(
                date=d,
                time=str(r.get("time", "")),
                name=str(r.get("name", "")),
                severity=str(r.get("severity", "low")).lower(),
                category=str(r.get("category", "other")),
                affects=list(r.get("affects", []) or []),
                notes=str(r.get("notes", "")),
            ))
        except Exception:
            continue
    out.sort(key=lambda e: e.date)
    return out


def upcoming_events(
    *,
    days_ahead: int = 7,
    affects_instrument: str | None = None,
    min_severity: str = "low",
) -> list[CalendarEvent]:
    """Return events within `days_ahead` calendar days, filtered.

    Args:
        days_ahead: Lookahead window. 7 days is the standard 'within 5 trading days'
            window with a calendar buffer.
        affects_instrument: If provided, only return events whose `affects` list
            contains this symbol (case-insensitive).
        min_severity: Lower bound on severity. Order: high > medium > low.
    """
    severity_rank = {"high": 3, "medium": 2, "low": 1}
    threshold = severity_rank.get(min_severity.lower(), 1)

    cutoff = date.today() + timedelta(days=days_ahead)
    events = [e for e in load_events()
              if date.today() <= e.date <= cutoff
              and severity_rank.get(e.severity, 0) >= threshold]
    if affects_instrument:
        sym = affects_instrument.upper()
        events = [e for e in events if sym in [s.upper() for s in e.affects]]
    return events


def render_event_block(events: list[CalendarEvent]) -> str:
    """Format events as a compact text block for inclusion in agent prompts."""
    if not events:
        return "No major scheduled events in the lookahead window."
    lines = []
    for e in events:
        days = e.days_from_today
        when = "today" if days == 0 else f"in {days} day{'s' if days != 1 else ''}"
        sev = e.severity.upper()
        affects = ", ".join(e.affects) if e.affects else "—"
        line = f"- [{sev}] {e.date.isoformat()} ({when}) · {e.name} · {e.time} · affects: {affects}"
        if e.notes:
            line += f"\n    note: {e.notes}"
        lines.append(line)
    return "\n".join(lines)
