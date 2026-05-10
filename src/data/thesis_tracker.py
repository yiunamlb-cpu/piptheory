"""Per-instrument thesis tracker.

The bias engine is stateless across runs. The score_history module gives
us conviction-over-time but doesn't tell us *why* the conviction is
where it is, or whether the original *reasons* are still intact.

For a swing trader holding a position over days to weeks, "why" matters
more than "how strong" — when you're long EURUSD because of "ECB
hawkish + Fed stuck", you want to know each morning whether THAT case
is still alive, not just today's integer score.

This module extracts the **driving themes** from each Strategist bias
card after the run, persists them, and on subsequent runs detects which
drivers are intact (still listed today), weakened (mentioned but with
softer language), or dropped (no longer in the card).

Storage: state/thesis_tracker.json. Per instrument: latest snapshot of
drivers + recent history of driver-set changes.

Display contract:
  - Per instrument: list of {driver, status, since_date}
  - Status: intact / weakening / dropped / new
  - Used in dashboard alongside the score history sparkline
"""
from __future__ import annotations

import json
import re
import threading
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from src.config import STATE_DIR

_PATH = STATE_DIR / "thesis_tracker.json"
_LOCK = threading.RLock()
_MAX_HISTORY = 30  # ~1 month of daily snapshots


# ─── Driver extraction from a Strategist bias card ──────────────────────────

# Strategist outputs include a "DRIVING THEMES" section that lists the
# themes from THEMES.md that justify the bias, often as bullet points.
# Format varies somewhat run-to-run; this regex catches the common shapes.
_DRIVING_THEMES_BLOCK_RE = re.compile(
    r"DRIVING\s*THEMES?[^\n]*\n+((?:[ \t]*[-•*··]?\s*[^\n]+\n?){1,12})",
    re.IGNORECASE,
)

# Each driver line typically starts with a bullet and may have a
# "Primary:"/"Secondary:" prefix. Strip those for canonical form.
_DRIVER_LINE_PREFIX_RE = re.compile(
    r"^[\s\-•*··]*(?:primary|secondary|tertiary|core|aux|supporting)?[\s:\-]*",
    re.IGNORECASE,
)


_NON_DRIVER_RE = re.compile(
    r"^(specialist\s*support|cross\s*asset|invalidation|notes?|risks?|"
    r"key\s*levels?|catalyst|conviction|direction|bias|invalidation\s*conditions)"
    r"\b",
    re.IGNORECASE,
)


def extract_drivers(strategist_section: str) -> list[str]:
    """Return a list of driver strings extracted from one instrument's
    Strategist bias card. Each driver is a one-line distillation of a
    theme/reason — long enough to be specific (e.g. "Theme 2 — ECB
    hawkish vs Fed stuck") but short enough to track day-to-day.
    """
    if not strategist_section:
        return []
    m = _DRIVING_THEMES_BLOCK_RE.search(strategist_section)
    if not m:
        return []
    block = m.group(1)
    drivers: list[str] = []
    for line in block.splitlines():
        s = line.strip()
        if not s:
            continue
        # Stop at the next ALL-CAPS / titled section header — the regex
        # block can over-grab into adjacent sections like SPECIALIST SUPPORT.
        if re.match(r"^[\s\-*•·]*\**\s*[A-Z][A-Z\s]{4,}[:\*]+", s):
            break
        # Skip continuation indentation that's not a bullet
        if not (s.startswith(("-", "•", "*", "·")) or
                re.match(r"^(primary|secondary|tertiary)\b", s, re.IGNORECASE)):
            # Could still be a driver if it's the first line with text;
            # but we only accept it if previous accepted ended with `:`
            if drivers and drivers[-1].endswith(":"):
                drivers[-1] = (drivers[-1].rstrip(":") + " " + s).strip()
            continue
        cleaned = _DRIVER_LINE_PREFIX_RE.sub("", s).strip()
        cleaned = cleaned.rstrip(".,;:")
        # Strip leading/trailing markdown bold markers
        cleaned = re.sub(r"^\*+|\*+$", "", cleaned).strip()
        # Reject section headers that snuck into the block
        if _NON_DRIVER_RE.match(cleaned):
            continue
        # Reject lines ending in a colon (those are sub-section labels)
        if cleaned.endswith(":") and len(cleaned) < 30:
            continue
        # Trim to reasonable length
        if len(cleaned) > 220:
            cleaned = cleaned[:217].rsplit(" ", 1)[0] + "…"
        if 6 <= len(cleaned) <= 240:
            drivers.append(cleaned)
    # Dedupe while preserving order
    seen: set[str] = set()
    out: list[str] = []
    for d in drivers:
        key = d.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(d)
    return out[:6]  # cap so cards stay readable


# ─── Storage ────────────────────────────────────────────────────────────────

@dataclass
class DriverSnapshot:
    """One day's set of drivers for one instrument."""
    date: str
    drivers: list[str] = field(default_factory=list)


def _read() -> dict[str, Any]:
    if not _PATH.exists():
        return {}
    try:
        return json.loads(_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _write(data: dict[str, Any]) -> None:
    _PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = _PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(_PATH)


def record_snapshot(*, run_date: str, instrument: str, drivers: list[str]) -> None:
    """Append (or replace, on same date) a daily driver snapshot."""
    if not drivers:
        return  # Don't pollute the log with empty snapshots
    with _LOCK:
        data = _read()
        per_instr = data.setdefault(instrument.upper(), {})
        history = per_instr.setdefault("history", [])
        # Replace same-date entry rather than appending duplicates
        history = [h for h in history if h.get("date") != run_date]
        history.append({"date": run_date, "drivers": list(drivers)})
        history.sort(key=lambda h: h.get("date", ""), reverse=True)
        per_instr["history"] = history[:_MAX_HISTORY]
        _write(data)


def latest(instrument: str) -> DriverSnapshot | None:
    data = _read()
    history = data.get(instrument.upper(), {}).get("history", [])
    if not history:
        return None
    h = history[0]
    return DriverSnapshot(date=h.get("date", ""), drivers=h.get("drivers", []) or [])


def history(instrument: str, n: int = 7) -> list[DriverSnapshot]:
    data = _read()
    raw = data.get(instrument.upper(), {}).get("history", [])
    return [DriverSnapshot(date=h.get("date", ""), drivers=h.get("drivers", []) or [])
            for h in raw[:n]]


# ─── Driver-state classification ────────────────────────────────────────────

def _norm(s: str) -> str:
    """Normalise a driver string for similarity comparison."""
    out = s.lower()
    out = re.sub(r"[^\w\s]", " ", out)
    out = re.sub(r"\s+", " ", out).strip()
    return out


def _similar(a: str, b: str) -> bool:
    """True if two drivers refer to the same underlying theme.

    Heuristic: word overlap. We intentionally keep this loose because LLM
    rephrasing day-to-day will produce slightly different wording for the
    same theme ("ECB hawkish vs Fed stuck" / "ECB hawkish pivot, Fed stuck"
    / "rate-differential favours EUR via ECB hike path").
    """
    aw = set(_norm(a).split())
    bw = set(_norm(b).split())
    if not aw or not bw:
        return False
    # Drop tiny words that don't carry meaning
    stop = {"the", "and", "of", "to", "a", "is", "in", "on", "for", "by",
            "with", "vs", "via", "as", "at", "or"}
    aw -= stop
    bw -= stop
    if not aw or not bw:
        return False
    overlap = aw & bw
    smaller = min(len(aw), len(bw))
    return len(overlap) / smaller >= 0.55


@dataclass
class DriverStatus:
    driver: str
    status: str          # "intact" | "new" | "dropped" | "modified"
    since_date: str = ""  # date the driver was first seen (for intact / modified)


def compare_drivers(today: list[str], yesterday: list[str]) -> list[DriverStatus]:
    """Compare today's drivers vs the most-recent prior snapshot.

    Returns a list covering BOTH today's drivers (each with intact/new/
    modified status) AND yesterday's drivers that disappeared today
    (status='dropped'). For dashboard display.
    """
    out: list[DriverStatus] = []
    matched_yesterday: set[int] = set()
    for d in today:
        match_idx = next((i for i, y in enumerate(yesterday)
                          if i not in matched_yesterday and _similar(d, y)), -1)
        if match_idx >= 0:
            matched_yesterday.add(match_idx)
            # Same wording = intact; rephrased = modified
            if _norm(d) == _norm(yesterday[match_idx]):
                out.append(DriverStatus(driver=d, status="intact"))
            else:
                out.append(DriverStatus(driver=d, status="modified"))
        else:
            out.append(DriverStatus(driver=d, status="new"))
    for i, y in enumerate(yesterday):
        if i in matched_yesterday:
            continue
        out.append(DriverStatus(driver=y, status="dropped"))
    return out


def status_for(instrument: str) -> dict[str, Any]:
    """Bundle for the dashboard: today's drivers + status vs yesterday +
    summary counts.

    Note: the dashboard treats `intact + modified` as "still alive."
    The two are distinguishable in the per-driver list (so the user can
    see if a driver was rephrased) but for the summary count they roll
    up. LLMs rephrase regularly even when the underlying theme is
    unchanged; we shouldn't punish that as if the driver had been
    dropped.
    """
    h = history(instrument, n=7)
    if not h:
        return {
            "drivers": [],
            "intact_count": 0,
            "alive_count": 0,
            "new_count": 0,
            "dropped_count": 0,
            "modified_count": 0,
            "snapshot_date": None,
            "prior_date": None,
            "summary_label": "no data",
        }
    today = h[0].drivers
    yesterday = h[1].drivers if len(h) > 1 else []
    statuses = compare_drivers(today, yesterday)
    intact = sum(1 for s in statuses if s.status == "intact")
    modified = sum(1 for s in statuses if s.status == "modified")
    new = sum(1 for s in statuses if s.status == "new")
    dropped = sum(1 for s in statuses if s.status == "dropped")
    alive = intact + modified

    # Compact one-line summary for table display
    if not yesterday:
        summary = f"{len(today)} driver{'s' if len(today) != 1 else ''} (no prior)"
    elif dropped == 0 and new == 0:
        summary = f"{alive} drivers, all intact"
    else:
        bits = []
        if alive: bits.append(f"{alive} alive")
        if new: bits.append(f"{new} new")
        if dropped: bits.append(f"{dropped} dropped")
        summary = ", ".join(bits)

    return {
        "drivers": [{"driver": s.driver, "status": s.status} for s in statuses],
        "intact_count": intact,
        "modified_count": modified,
        "alive_count": alive,           # intact + modified
        "new_count": new,
        "dropped_count": dropped,
        "snapshot_date": h[0].date,
        "prior_date": h[1].date if len(h) > 1 else None,
        "summary_label": summary,
    }
