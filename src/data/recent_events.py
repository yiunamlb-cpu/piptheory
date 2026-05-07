"""Recent events log loader and writer.

The companion to data/events.yaml (scheduled events). This file holds
*things that already happened* — news, tariff announcements, surprise
data, central-bank speakers — that the Strategist should factor into
today's analysis.

The system has no news API. This file is the user's only channel for
encoding news context into the pipeline. The Strategist reads
`recent_events_block(...)` as Layer 0 input, alongside the FRED rate
snapshot and the THEMES.md regime tracker.

Concurrency: writes use a single per-process re-entrant lock plus an
atomic-replace pattern (write to .tmp, then rename). Single-process
uvicorn means this is sufficient.
"""
from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

from src.config import ROOT

_RECENT_PATH = ROOT / "data" / "recent_events.yaml"
_LOCK = threading.RLock()

# How many days of history feed into the Strategist prompt. Older entries
# stay in the file for the user's own reference but aren't shipped to the
# model — the agents care about *what's recently relevant*, not 6 months
# of stale headlines.
_PROMPT_WINDOW_DAYS = 30


@dataclass
class RecentEvent:
    date: date
    headline: str
    impact: str = ""
    notes: str = ""
    relevance: str = "medium"   # high | medium | low
    affects: list[str] | None = None

    @property
    def days_ago(self) -> int:
        return (date.today() - self.date).days

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "date": self.date.isoformat(),
            "headline": self.headline,
        }
        if self.impact: out["impact"] = self.impact
        if self.notes: out["notes"] = self.notes
        if self.relevance != "medium": out["relevance"] = self.relevance
        if self.affects: out["affects"] = list(self.affects)
        return out


def _read_raw() -> dict[str, Any]:
    if not _RECENT_PATH.exists():
        return {"events": []}
    with _RECENT_PATH.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        return {"events": []}
    if "events" not in data or data["events"] is None:
        data["events"] = []
    return data


def _write_raw(data: dict[str, Any]) -> None:
    """Atomic write. Preserves the file's leading comment block by
    inserting it before the YAML body."""
    body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True,
                          default_flow_style=False)
    # Try to keep the user's comment header if present
    header = ""
    if _RECENT_PATH.exists():
        existing = _RECENT_PATH.read_text(encoding="utf-8")
        # Header is everything up to the first non-comment, non-blank line
        kept_lines: list[str] = []
        for line in existing.splitlines():
            stripped = line.strip()
            if stripped == "" or stripped.startswith("#"):
                kept_lines.append(line)
            else:
                break
        if kept_lines:
            header = "\n".join(kept_lines).rstrip() + "\n\n"
    tmp = _RECENT_PATH.with_suffix(".tmp")
    tmp.write_text(header + body, encoding="utf-8")
    tmp.replace(_RECENT_PATH)


def load_recent_events() -> list[RecentEvent]:
    """Return all events, sorted most-recent first."""
    with _LOCK:
        raw = _read_raw()
    out: list[RecentEvent] = []
    for r in raw.get("events", []) or []:
        try:
            d = r["date"]
            if isinstance(d, str):
                d = date.fromisoformat(d)
            out.append(RecentEvent(
                date=d,
                headline=str(r.get("headline", "")).strip(),
                impact=str(r.get("impact", "") or "").strip(),
                notes=str(r.get("notes", "") or "").strip(),
                relevance=str(r.get("relevance", "medium")).lower(),
                affects=list(r.get("affects") or []) or None,
            ))
        except Exception:
            continue
    out.sort(key=lambda e: e.date, reverse=True)
    return out


def add_event(
    *,
    date_: date | str | None = None,
    headline: str,
    impact: str = "",
    notes: str = "",
    relevance: str = "medium",
    affects: list[str] | None = None,
) -> RecentEvent:
    """Append a new event. Returns the saved RecentEvent."""
    if isinstance(date_, str):
        d = date.fromisoformat(date_)
    elif isinstance(date_, date):
        d = date_
    else:
        d = date.today()
    headline = (headline or "").strip()
    if not headline:
        raise ValueError("headline is required")
    if relevance not in ("high", "medium", "low"):
        relevance = "medium"
    ev = RecentEvent(
        date=d,
        headline=headline,
        impact=(impact or "").strip(),
        notes=(notes or "").strip(),
        relevance=relevance,
        affects=[a.upper() for a in (affects or []) if a],
    )
    with _LOCK:
        raw = _read_raw()
        raw.setdefault("events", []).append(ev.to_dict())
        # Keep the file sorted newest-first for human readability when
        # editing manually.
        raw["events"].sort(
            key=lambda r: str(r.get("date", "")), reverse=True,
        )
        _write_raw(raw)
    return ev


def delete_event(date_iso: str, headline: str) -> bool:
    """Remove an event by exact date+headline match."""
    with _LOCK:
        raw = _read_raw()
        before = len(raw.get("events", []))
        raw["events"] = [
            r for r in raw.get("events", [])
            if not (str(r.get("date", "")) == date_iso
                    and str(r.get("headline", "")).strip() == headline.strip())
        ]
        if len(raw["events"]) == before:
            return False
        _write_raw(raw)
        return True


def recent_events_for_prompt(window_days: int = _PROMPT_WINDOW_DAYS) -> list[RecentEvent]:
    """Subset of recent events that should be shipped to the Strategist
    on each run. Filters to the last `window_days` calendar days, with
    high-relevance events prioritised.
    """
    cutoff = date.today() - timedelta(days=window_days)
    return [e for e in load_recent_events() if e.date >= cutoff]


def render_recent_events_block(events: list[RecentEvent] | None = None) -> str:
    """Format events as a compact prose block for inclusion in agent prompts.

    Output looks like:

        Recent regime-relevant events (last 30 days, you-encoded):
        - 2026-05-06 (1d ago, HIGH) — Trump announces 25% Mexico tariff.
            Impact: peso -3%, NQ -1.2%, gold +0.8%.
            Note: confirms trade-war regime; gold catching safe-haven bid.
            Affects: USDMXN, NQ, GC.
        - 2026-05-04 (3d ago, MEDIUM) — ECB Kazimir reiterates June hike likely.

    Returns "(no recent events logged)" if empty so the Strategist knows
    to rely solely on FRED + THEMES.md context.
    """
    if events is None:
        events = recent_events_for_prompt()
    if not events:
        return (
            "Recent regime-relevant events: (none logged in the last 30 days). "
            "Rely on FRED data and the THEMES.md regime tracker for narrative "
            "context."
        )
    lines = [f"Recent regime-relevant events (last 30 days, user-encoded):"]
    for e in events:
        days = e.days_ago
        days_str = "today" if days == 0 else f"{days}d ago"
        rel = e.relevance.upper()
        head = f"- {e.date.isoformat()} ({days_str}, {rel}) — {e.headline}"
        if not head.endswith((".", "!", "?")):
            head += "."
        lines.append(head)
        if e.impact:
            lines.append(f"    Impact: {e.impact}")
        if e.notes:
            lines.append(f"    Note: {e.notes}")
        if e.affects:
            lines.append(f"    Affects: {', '.join(e.affects)}")
    return "\n".join(lines)
