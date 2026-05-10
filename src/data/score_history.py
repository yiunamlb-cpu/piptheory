"""Per-instrument conviction history.

The bias engine is stateless across runs. Each pipeline run produces a
fresh conviction integer per instrument; LLM noise causes 1-point
wobble between runs even on identical macro data. For a swing trader
holding positions over days to weeks, that wobble — surfaced as a
single number on the dashboard — erodes trust in the signal.

This module persists a small history of conviction readings per
instrument so the dashboard can show:

  - The raw point estimate today (still useful)
  - A 3-day weighted average (smooths noise without lag)
  - A trend arrow (↑ ↓ →) computed from the last 3-5 runs
  - A stability classification (stable / oscillating / drifting)
  - A sparkline visualisation

Storage: state/score_history.json. Append-only per (date, instrument),
keeps last 60 entries per instrument (~3 months of daily runs).
Thread-safe via re-entrant lock on the writer side.

Pipeline calls record_run() after Layer 4 council finishes for each
instrument that produced a Judge bias. The dashboard calls history_for()
on render to fetch the last N entries.
"""
from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from src.config import STATE_DIR

_PATH = STATE_DIR / "score_history.json"
_LOCK = threading.RLock()
_MAX_ENTRIES_PER_INSTRUMENT = 60  # ~3 months daily


@dataclass
class HistoryEntry:
    date: str               # ISO date "YYYY-MM-DD"
    bias: str               # "long" / "short" / "no view"
    conviction: int         # 0-10
    source: str             # "judge" (post-council) or "strategist" (pre-council)

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date,
            "bias": self.bias,
            "conviction": self.conviction,
            "source": self.source,
        }


def _normalise_bias(raw: str) -> str:
    """Map a free-form bias string ("bullish", "slight long", etc.) to one
    of the three stable categories. Used so direction-flip detection works
    against a finite vocabulary."""
    s = (raw or "").lower()
    if any(w in s for w in ("long", "bull")):
        return "long"
    if any(w in s for w in ("short", "bear")):
        return "short"
    return "no view"


def _read() -> dict[str, list[dict[str, Any]]]:
    if not _PATH.exists():
        return {}
    try:
        return json.loads(_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _write(data: dict[str, list[dict[str, Any]]]) -> None:
    """Atomic write — tmp file then rename."""
    _PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = _PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(_PATH)


def record_run(
    *,
    run_date: str,
    instrument: str,
    bias: str,
    conviction: int,
    source: str = "judge",
) -> None:
    """Append (or replace, if same run_date already exists) a history entry.

    Re-running the same date — e.g. via the dashboard's "Run again"
    button — replaces that day's entry rather than appending a duplicate,
    so the sparkline stays one-point-per-day.
    """
    with _LOCK:
        data = _read()
        entries = data.setdefault(instrument.upper(), [])
        # Remove existing entry for this date so re-runs don't double up
        entries = [e for e in entries if e.get("date") != run_date]
        entries.append({
            "date": run_date,
            "bias": _normalise_bias(bias),
            "conviction": int(conviction),
            "source": source,
        })
        # Keep newest first; trim
        entries.sort(key=lambda e: e.get("date", ""), reverse=True)
        entries = entries[:_MAX_ENTRIES_PER_INSTRUMENT]
        data[instrument.upper()] = entries
        _write(data)


def history_for(instrument: str, n: int = 7) -> list[HistoryEntry]:
    """Return the last `n` entries for an instrument, oldest-first.

    Oldest-first ordering is what the sparkline renderer wants — visually
    left-to-right is past-to-present.
    """
    data = _read()
    raw = data.get(instrument.upper(), [])
    # Stored newest-first; take the slice and reverse
    take = list(raw[:n])
    take.reverse()
    return [HistoryEntry(
        date=e.get("date", ""),
        bias=str(e.get("bias", "no view")),
        conviction=int(e.get("conviction", 0)),
        source=str(e.get("source", "judge")),
    ) for e in take]


def all_instruments() -> list[str]:
    """List symbols that have any history."""
    return sorted(_read().keys())


# ─── Derived statistics for the dashboard ──────────────────────────────────

def trend_arrow(entries: list[HistoryEntry]) -> str:
    """↑ if conviction has risen 2+ across the window, ↓ if fallen 2+,
    → if flat or drifting within ±1.

    Compares the average of the first half vs. the second half — more
    robust to a single noisy spike than first-vs-last."""
    if len(entries) < 2:
        return "→"
    mid = len(entries) // 2
    first_half = entries[:mid] if mid > 0 else entries[:1]
    second_half = entries[mid:]
    avg_first = sum(e.conviction for e in first_half) / len(first_half)
    avg_second = sum(e.conviction for e in second_half) / len(second_half)
    delta = avg_second - avg_first
    if delta >= 1.5:
        return "↑"
    if delta <= -1.5:
        return "↓"
    return "→"


def weighted_average(entries: list[HistoryEntry], window: int = 3) -> float | None:
    """Weighted average of the last `window` entries — most-recent gets
    the highest weight. Reduces the visual impact of single-day spikes
    without lagging like a simple moving average.

    Weights for window=3: most-recent 3, mid 2, oldest 1 (sums to 6).
    """
    if not entries:
        return None
    take = entries[-window:]
    n = len(take)
    weights = list(range(1, n + 1))  # oldest=1, newest=n
    total_w = sum(weights)
    return sum(e.conviction * w for e, w in zip(take, weights)) / total_w


def stability(entries: list[HistoryEntry]) -> str:
    """Classify the run-to-run pattern.

    - "stable":      all readings within a 1-point band over the window
    - "oscillating": readings span 2+ points but not trending
    - "trending":    readings span 2+ points AND show a directional move
                     (i.e. trend_arrow says ↑ or ↓)
    - "n/a":         not enough data (fewer than 3 entries)
    """
    if len(entries) < 3:
        return "n/a"
    convictions = [e.conviction for e in entries]
    span = max(convictions) - min(convictions)
    if span <= 1:
        return "stable"
    if trend_arrow(entries) in ("↑", "↓"):
        return "trending"
    return "oscillating"


def direction_flips(entries: list[HistoryEntry]) -> int:
    """Count how many times the bias direction flipped over the window.
    A direction-flip is a meaningful event — distinct from conviction
    wobble. 0 means stable direction.
    """
    flips = 0
    prev = None
    for e in entries:
        if e.bias == "no view":
            continue
        if prev is not None and prev != e.bias:
            flips += 1
        prev = e.bias
    return flips


def delta_since_last_run(entries: list[HistoryEntry]) -> dict[str, Any]:
    """Compare the most-recent entry vs the prior entry — the 'what
    changed since yesterday' summary the audit asked for.

    Returns:
      changed: bool — true if anything material moved
      kind:    "direction_flip" | "conviction_jump" | "conviction_drop" |
               "minor" | "stable"
      summary: short user-facing string
      delta:   {bias_today, bias_prior, conviction_today, conviction_prior,
                conviction_change}
    """
    if len(entries) < 2:
        return {
            "changed": False,
            "kind": "stable",
            "summary": "no prior run",
            "delta": {},
        }
    today = entries[-1]
    prior = entries[-2]
    delta = {
        "bias_today": today.bias,
        "bias_prior": prior.bias,
        "conviction_today": today.conviction,
        "conviction_prior": prior.conviction,
        "conviction_change": today.conviction - prior.conviction,
    }
    # Direction flip is the big signal
    if today.bias != prior.bias and today.bias != "no view" and prior.bias != "no view":
        return {
            "changed": True,
            "kind": "direction_flip",
            "summary": f"flipped {prior.bias.upper()} → {today.bias.upper()}",
            "delta": delta,
        }
    # Big conviction jumps
    diff = today.conviction - prior.conviction
    if diff >= 2:
        return {
            "changed": True,
            "kind": "conviction_jump",
            "summary": f"strengthened {prior.conviction} → {today.conviction}",
            "delta": delta,
        }
    if diff <= -2:
        return {
            "changed": True,
            "kind": "conviction_drop",
            "summary": f"weakened {prior.conviction} → {today.conviction}",
            "delta": delta,
        }
    if diff != 0:
        return {
            "changed": True,
            "kind": "minor",
            "summary": f"{prior.conviction} → {today.conviction}",
            "delta": delta,
        }
    return {
        "changed": False,
        "kind": "stable",
        "summary": "unchanged",
        "delta": delta,
    }


def summary_for(instrument: str, n: int = 7) -> dict[str, Any]:
    """Bundle everything the dashboard needs for one instrument."""
    entries = history_for(instrument, n)
    return {
        "entries": [e.to_dict() for e in entries],
        "convictions": [e.conviction for e in entries],
        "current": entries[-1].conviction if entries else None,
        "weighted_avg_3d": (
            round(weighted_average(entries, window=3), 1)
            if entries else None
        ),
        "trend_arrow": trend_arrow(entries),
        "stability": stability(entries),
        "direction_flips": direction_flips(entries),
        "n_entries": len(entries),
        "delta": delta_since_last_run(entries),
    }
