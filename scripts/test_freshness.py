"""Verify freshness metadata flows through FRED and COT wrappers + context formatters."""
from __future__ import annotations

import sys

ROOT = __file__.rsplit("\\", 2)[0] if "\\" in __file__ else __file__.rsplit("/", 2)[0]
sys.path.insert(0, ROOT)

from src.data import CotClient, FredClient
from src.orchestration.context import (
    FRESHNESS_INSTRUCTION,
    cot_summaries_to_text,
    fred_snapshot_to_text,
)

print("=== FRED snapshot with freshness ===")
fred = FredClient()
snap = fred.snapshot([
    "cpi_headline", "cpi_core", "pce_core",
    "ust_10y", "ffr_target_upper", "breakeven_5y5y",
])
print(fred_snapshot_to_text(snap))

print()
print("=== COT summary with freshness ===")
cot = CotClient(lookback_years=3)
for inst in ["EURUSD", "GC", "AUDUSD"]:
    s = cot.summary(inst)
    if s.get("status") == "ok":
        print(f"  {inst:8s} label={s['freshness_label']:7s} age={s['data_age_days']}d  pct={s['percentile_3yr']}  tag={s['freshness_tag']}")
    else:
        print(f"  {inst}: {s.get('status')}")

print()
print("=== Freshness instruction prepended to agent inputs ===")
print(FRESHNESS_INSTRUCTION)
