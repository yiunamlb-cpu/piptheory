"""Smoke test the unified watchlist build."""
from __future__ import annotations
import sys
ROOT = __file__.rsplit("\\", 2)[0] if "\\" in __file__ else __file__.rsplit("/", 2)[0]
sys.path.insert(0, ROOT)

from dashboard.loader import load_run, list_runs
from app.main import _build_unified_watchlist

runs = list_runs()
r = load_run(runs[0])
print(f"Run: {runs[0]}, council instruments: {list(r.council)}")
for inst, co in r.council.items():
    print(f"  {inst}: judge_conviction={co.judge_conviction}")

print()
print("Unified watchlist (sorted by tier, then conviction desc):")
print(f"  {'tier':4s} {'sym':7s} {'bias':35s} {'conv':5s} {'src':10s} {'verdict':18s}")
for row in _build_unified_watchlist(r):
    print(f"  {row['tier']:<4} {row['symbol']:<7} {row['bias'][:35]:<35} "
          f"{row['conviction']:>2}/10 {row['conviction_source']:<10} "
          f"{row['verdict'] or '-':<18}")
