"""Determinism + sanity test for the currency-strength engine.

1. DETERMINISM: run compute_strength() twice; assert the scoring core is
   byte-for-byte identical (the user's key requirement — it must never
   contradict itself on the same data).
2. SANITY: ranks are 1..8 unique, composites within [-100, 100], and the
   risk pillar respects the risk regime (havens vs high-beta).
"""
from __future__ import annotations

import json
import sys

from src.data.currency_strength import CURRENCIES, compute_strength


def _core(out: dict) -> str:
    """Deterministic core (everything except the wall-clock as_of stamp)."""
    return json.dumps(out["currencies"], sort_keys=True)


def main() -> int:
    a = compute_strength(persist=False)
    b = compute_strength(persist=False)  # warm cache => same inputs

    ok = True

    # 1. Determinism
    if _core(a) == _core(b):
        print("PASS  determinism: identical output on re-run")
    else:
        ok = False
        print("FAIL  determinism: output changed on re-run!")

    cur = a["currencies"]

    # 2a. ranks unique 1..8
    ranks = sorted(d["rank"] for d in cur.values())
    if ranks == list(range(1, len(CURRENCIES) + 1)):
        print(f"PASS  ranks unique 1..{len(CURRENCIES)}")
    else:
        ok = False
        print(f"FAIL  ranks: {ranks}")

    # 2b. composites in range
    bad = [c for c, d in cur.items() if not (-100.0 <= d["composite"] <= 100.0)]
    print("PASS  composites within [-100,100]" if not bad else f"FAIL  out of range: {bad}")
    ok = ok and not bad

    # 2c. risk regime coherence: havens and high-beta move opposite on risk
    ri = a["risk_intensity"]
    usd_risk = cur["USD"]["pillars"].get("risk", 0.0)
    aud_risk = cur["AUD"]["pillars"].get("risk", 0.0)
    coherent = (usd_risk * aud_risk <= 0) or ri == 0  # opposite signs (haven vs beta)
    print(f"{'PASS' if coherent else 'FAIL'}  risk regime: intensity={ri:+.2f} "
          f"USD_risk={usd_risk:+.0f} AUD_risk={aud_risk:+.0f}")
    ok = ok and coherent

    print("\n--- meter ---")
    for code, d in cur.items():
        pills = " ".join(f"{p[:4]}={v:+.0f}" for p, v in d["pillars"].items())
        print(f"  #{d['rank']} {code} {d['composite']:+6.1f} {d['label']:16s} [{pills}]")

    print("\nRESULT:", "ALL PASS" if ok else "FAILURES ABOVE")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
