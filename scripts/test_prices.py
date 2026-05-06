"""Smoke-test src/data/prices.py against the active universe (ES, NQ, GC)."""
from __future__ import annotations

import sys

ROOT = __file__.rsplit("\\", 2)[0] if "\\" in __file__ else __file__.rsplit("/", 2)[0]
sys.path.insert(0, ROOT)

import json

from src.data import PriceClient

prices = PriceClient()

for inst in ["ES", "NQ", "GC"]:
    try:
        ctx = prices.get_setup_context(inst)
    except Exception as e:
        print(f"\n=== {inst} ===\nFAILED: {e}")
        continue
    print(f"\n=== {inst} ===")
    print(json.dumps(ctx.to_dict(), indent=2, default=str))
