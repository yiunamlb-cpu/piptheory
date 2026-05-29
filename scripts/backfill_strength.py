"""Backfill historical currency strength so trend charts have depth at launch.

Replays the SAME deterministic engine weekly over the past N weeks (each date
computed as-of itself: all sources sliced to that date, freshness judged then).
Then runs one live snapshot for today.

CAVEAT (honest): this uses today's *revised* FRED data, not the vintage that
was published in real time, so the backfilled history is pro-forma — slightly
"smarter" than a live meter could have been. Good enough for chart context;
not a claim about real-time historical calls.

Run:  .venv\\Scripts\\python.exe -m scripts.backfill_strength [weeks]
"""
from __future__ import annotations

import sys
from datetime import date, timedelta

from src.data.currency_strength import (
    CURRENCIES, _MAX_HISTORY, _load, _save, compute_strength,
)


def main() -> int:
    weeks = int(sys.argv[1]) if len(sys.argv) > 1 else 52
    today = date.today()
    # Oldest -> newest, weekly, excluding today (today done by the live run below).
    dates = [today - timedelta(days=7 * i) for i in range(weeks, 0, -1)]

    print(f"Backfilling {len(dates)} weekly snapshots "
          f"({dates[0]} .. {dates[-1]})  +1 live (today)\n")

    collected: dict[str, list[dict]] = {c: [] for c in CURRENCIES}
    for i, d in enumerate(dates, 1):
        try:
            out = compute_strength(persist=False, as_of=d, price_period="3y")
        except Exception as e:
            print(f"  [{i:2d}/{len(dates)}] {d}  SKIP ({type(e).__name__}: {str(e)[:50]})")
            continue
        for code, data in out["currencies"].items():
            collected[code].append({
                "date": d.isoformat(),
                "composite": data["composite"],
                "rank": data["rank"],
                "pillars": data["pillars"],
            })
        top = next(iter(out["currencies"]))
        bot = list(out["currencies"])[-1]
        print(f"  [{i:2d}/{len(dates)}] {d}  strongest={top}  weakest={bot}")

    # Merge into any existing history (backfill dates win for their dates).
    existing = _load()
    for code in CURRENCIES:
        by_date = {e["date"]: e for e in existing.get(code, [])}
        for entry in collected[code]:
            by_date[entry["date"]] = entry
        existing[code] = sorted(by_date.values(), key=lambda e: e["date"])[-_MAX_HISTORY:]
    _save(existing)
    print(f"\nWrote backfilled history for {len(CURRENCIES)} currencies.")

    # One live snapshot for today (trend now computed from the backfilled history).
    live = compute_strength(persist=True, price_period="1y")
    print(f"\nLive snapshot {live['run_date']}:")
    for code, d in live["currencies"].items():
        t = d["trend"]
        print(f"  #{d['rank']} {code} {d['composite']:+6.1f} {d['label']:16s} "
              f"trend={t['label']}({t['change']:+.1f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
