"""Sanity backtest for the currency-strength meter.

Question: when the meter says A is stronger than B, does A tend to OUTPERFORM
B over the following weeks? This is a coherence check, not a trading system.

Method (pairwise, all 28 currency pairs, over the backfilled weekly history):
  * strength_diff = score_A(D) - score_B(D)
  * fwd_return   = log return of A vs USD minus B vs USD over [D, D+H]
                   ( = the A/B cross-rate return)
  * HIT = sign(strength_diff) == sign(fwd_return)

We report the hit-rate (overall + when the meter has a *strong* view,
|diff|>=15) and the Pearson correlation, for a few horizons. Honest notes:
windows overlap (so treat significance loosely) and history is pro-forma.

Run:  .venv\\Scripts\\python.exe -m scripts.validate_strength
"""
from __future__ import annotations

import json
import math
from datetime import date, timedelta
from itertools import combinations

import pandas as pd

from src.data.currency_strength import CURRENCIES, _PATH
from src.data.prices import PriceClient

# currency -> (price instrument, invert?) to build a "value vs USD" index
PAIR = {
    "EUR": ("EURUSD", False), "GBP": ("GBPUSD", False),
    "AUD": ("AUDUSD", False), "NZD": ("NZDUSD", False),
    "JPY": ("USDJPY", True), "CAD": ("USDCAD", True), "CHF": ("USDCHF", True),
}
HORIZONS = [21, 42, 63]  # ~3, 6, 9 weeks forward
STRONG_VIEW = 15.0       # composite points => "the meter has a clear view"


def _indices(pc: PriceClient) -> dict[str, pd.Series]:
    idx: dict[str, pd.Series] = {}
    for ccy, (inst, inv) in PAIR.items():
        s = pc.get_ohlc(inst, period="2y")["Close"].dropna()
        s.index = pd.to_datetime(s.index)
        idx[ccy] = (1.0 / s) if inv else s
    union = sorted(set().union(*[set(v.index) for v in idx.values()]))
    idx["USD"] = pd.Series(1.0, index=pd.DatetimeIndex(union))
    return idx


def _asof(s: pd.Series, d) -> float | None:
    sub = s[s.index <= pd.Timestamp(d)]
    return float(sub.iloc[-1]) if len(sub) else None


def _logret(s: pd.Series, d0, d1) -> float | None:
    a, b = _asof(s, d0), _asof(s, d1)
    if a is None or b is None or a <= 0 or b <= 0:
        return None
    return math.log(b / a)


def _pearson(xs, ys) -> float:
    n = len(xs)
    if n < 3:
        return float("nan")
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    return cov / math.sqrt(vx * vy) if vx > 0 and vy > 0 else float("nan")


def main() -> int:
    hist = json.loads(_PATH.read_text(encoding="utf-8"))
    scores = {c: {e["date"]: e["composite"] for e in hist[c]} for c in CURRENCIES}
    snap_dates = sorted({d for c in CURRENCIES for d in scores[c]})

    pc = PriceClient()
    idx = _indices(pc)
    last_price = min(v.index.max() for v in idx.values())

    print(f"Snapshots: {len(snap_dates)} ({snap_dates[0]}..{snap_dates[-1]})  "
          f"price data to {last_price.date()}\n")
    print(f"{'H(days)':>7} {'n':>6} {'hit%':>6} {'hit%|strong':>12} {'pearson':>8}")

    for H in HORIZONS:
        sds, rds = [], []
        hits = tot = hits_s = tot_s = 0
        for d in snap_dates:
            d0 = date.fromisoformat(d)
            d1 = d0 + timedelta(days=H)
            if pd.Timestamp(d1) > last_price:
                continue
            ret = {c: _logret(idx[c], d0, d1) for c in CURRENCIES}
            for a, b in combinations(sorted(CURRENCIES), 2):
                if d not in scores[a] or d not in scores[b]:
                    continue
                if ret[a] is None or ret[b] is None:
                    continue
                sd = scores[a][d] - scores[b][d]
                rd = ret[a] - ret[b]
                sds.append(sd)
                rds.append(rd)
                if sd != 0:
                    agree = (sd > 0) == (rd > 0)
                    tot += 1
                    hits += agree
                    if abs(sd) >= STRONG_VIEW:
                        tot_s += 1
                        hits_s += agree
        hr = 100 * hits / tot if tot else float("nan")
        hrs = 100 * hits_s / tot_s if tot_s else float("nan")
        print(f"{H:>7} {tot:>6} {hr:>6.1f} {hrs:>12.1f} {_pearson(sds, rds):>8.3f}")

    print("\nReading: hit% > 50 means the stronger-scored currency tended to "
          "outperform.\n~50 = no edge (still a coherent snapshot); <45 would be "
          "a red flag.\nOverlapping windows => treat as directional sanity, not "
          "statistical proof.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
