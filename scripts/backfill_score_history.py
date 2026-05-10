"""Backfill state/score_history.json from existing bias_cards/{date}/ runs.

Run once after introducing the score history feature. The pipeline writes
history going forward, but the user has historic runs from before this
change — we want those readings on the sparkline too rather than starting
from zero.

Usage:
    .venv/Scripts/python.exe scripts/backfill_score_history.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.config import BIAS_CARDS_DIR
from src.data import score_history
from dashboard.loader import list_runs, load_run


def main() -> None:
    runs = list_runs()
    if not runs:
        print("No runs found.")
        return
    runs_chrono = sorted(runs)  # oldest first
    n_recorded = 0
    for run_date in runs_chrono:
        run = load_run(run_date)
        if not run:
            continue
        # Council outputs first (Judge supersedes Strategist for that
        # instrument)
        recorded_in_run: set[str] = set()
        for inst, co in run.council.items():
            if co and co.judge:
                conv = co.judge_conviction
                bias = co.judge_bias or ""
                if conv:
                    score_history.record_run(
                        run_date=run_date,
                        instrument=inst,
                        bias=bias,
                        conviction=conv,
                        source="judge",
                    )
                    recorded_in_run.add(inst)
                    n_recorded += 1
        # Strategist-only entries for instruments without a council
        for b in run.instrument_biases:
            if b.instrument in recorded_in_run:
                continue
            score_history.record_run(
                run_date=run_date,
                instrument=b.instrument,
                bias=b.bias,
                conviction=b.conviction,
                source="strategist",
            )
            n_recorded += 1
        print(f"Backfilled {run_date}")
    print(f"\nDone. {n_recorded} entries recorded across {len(runs_chrono)} runs.")
    print(f"State file: {REPO / 'state' / 'score_history.json'}")


if __name__ == "__main__":
    main()
