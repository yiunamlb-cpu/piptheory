"""Debug script: parse the 2026-05-06 strategist output and print structured bias cards."""
from __future__ import annotations

import sys

ROOT = __file__.rsplit("\\", 2)[0] if "\\" in __file__ else __file__.rsplit("/", 2)[0]
sys.path.insert(0, ROOT)

from dashboard.loader import load_run, list_runs

print("Available runs:", list_runs())
for d in list_runs():
    r = load_run(d)
    if r is None:
        print(f"  {d}: could not load")
        continue
    print(f"\n=== {d} ===")
    print(f"  layer1 inflation:   {len(r.layer1_inflation):>6} chars")
    print(f"  layer1 positioning: {len(r.layer1_positioning):>6} chars")
    print(f"  layer1 fed:         {len(r.layer1_fed):>6} chars")
    print(f"  layer2 strategist:  {len(r.layer2_strategist):>6} chars")
    print(f"  layer3 contrarian:  {len(r.layer3_contrarian):>6} chars")
    print(f"  layer5 PM brief:    {len(r.layer5_pm_brief):>6} chars")
    print(f"  council instruments: {list(r.council)}")
    print(f"  parsed instrument biases: {len(r.instrument_biases)}")
    for b in r.instrument_biases:
        print(f"    {b.instrument:8s}  bias={b.bias[:35]:37s}  conv={b.conviction}/10  pri={b.priority!r:>5}")
