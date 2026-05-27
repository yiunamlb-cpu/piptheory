**Data Freshness Note:** All COT data is from the May 19 observation (released May 22), now 5 days old. This is "recent" — not stale enough to ignore, but stale enough that fast moves in the last week could have shifted positioning. Conviction is capped at **medium** for directional reads.

---

## Per-Instrument Structured Output

### EURUSD
```
INSTRUMENT: EURUSD
DATE: 2026-05-19
DATA AGE: 5d

POSITIONING (Leveraged Funds, primary):
  Net position: +16,317 contracts
  3-year percentile: 66.7th
  Direction: neutral
  Trend (4-week change): +4,723 (increasing long)

POSITIONING (Asset Managers, supplementary):
  Not provided in this dataset — no divergence assessment possible.

CROWDED TRADE ASSESSMENT:
  Crowded? N — 66.7th percentile is firmly neutral.
  Persistence: N/A
  Stage of unwind: N/A

CONTRA-SIGNAL STRENGTH: none
  Rationale: Neutral percentile, no extreme.

INVALIDATION: N/A
NEXT UPDATE: next Friday
```

### USDJPY
```
INSTRUMENT: USDJPY
DATE: 2026-05-19
DATA AGE: 5d

POSITIONING (Leveraged Funds, primary):
  Net position: -64,945 contracts (short JPY = long USDJPY)
  3-year percentile: 18.6th
  Direction: stretched short (watch)
  Trend (4-week change): +10,857 (decreasing short — covering)

POSITIONING (Asset Managers, supplementary):
  Not provided.

CROWDED TRADE ASSESSMENT:
  Crowded? N — 18.6th percentile is stretched but not extreme (<5th required for extreme short flag).
  Persistence: 0 of last 6 weeks at extreme.
  Stage of unwind: N/A

CONTRA-SIGNAL STRENGTH: weak
  Rationale: Below 20th percentile suggests short JPY positioning is stretched, but not extreme. The covering trend (+10.9k in 4 weeks) suggests the unwind is already underway — less explosive potential.

INVALIDATION: A drop below 5th percentile would upgrade to extreme.
NEXT UPDATE: next Friday
```

### GBPUSD
```
INSTRUMENT: GBPUSD
DATE: 2026-05-19
DATA AGE: 5d

POSITIONING (Leveraged Funds, primary):
  Net position: +31,369 contracts
  3-year percentile: 48.6th
  Direction: neutral
  Trend (4-week change): +2,487 (flat)

CROWDED TRADE ASSESSMENT:
  Crowded? N
  Stage of unwind: N/A

CONTRA-SIGNAL STRENGTH: none
  Rationale: Dead center of 3-year range.

INVALIDATION: N/A
NEXT UPDATE: next Friday
```

### AUDUSD
```
INSTRUMENT: AUDUSD
DATE: 2026-05-19
DATA AGE: 5d

POSITIONING (Leveraged Funds, primary):
  Net position: +61,178 contracts
  3-year percentile: 97.7th
  Direction: extreme long (bearish contra-signal)
  Trend (4-week change): +13,323 (increasing long — still adding)

POSITIONING (Asset Managers, supplementary):
  Not provided.

CROWDED TRADE ASSESSMENT:
  Crowded? YES
  Persistence: 6 of last 6 weeks at extreme (>95th) — maximum persistence.
  Stage of unwind: Stage 1 (Distribution) — positioning is still at peak and still adding, but price action needs checking. If AUDUSD is still making highs, this is still Stage 1 accumulation. If price is stalling while positioning peaks, Stage 1 distribution has begun.

CONTRA-SIGNAL STRENGTH: strong
  Rationale: 97.7th percentile + 6/6 weeks at extreme = textbook crowded long. Leveraged Funds are massively long AUD at levels not seen in 3 years. The 4-week trend is still adding, which means the unwind hasn't started yet — but the risk of a reversal is elevated. This is the most extreme positioning in the watchlist.

INVALIDATION: A break above recent highs with continued long accumulation would invalidate the contra-signal. A drop below 90th percentile would signal unwind has begun.
NEXT UPDATE: next Friday
```

### GC (Gold)
```
INSTRUMENT: GC
DATE: 2026-05-19
DATA AGE: 5d

POSITIONING (Managed Money, primary):
  Net position: -422 contracts
  3-year percentile: 2.9th
  Direction: extreme short (bullish contra-signal)
  Trend (4-week change): -953 (increasing short)

POSITIONING (Producer/Merchant, supplementary):
  Not provided — but Commercials are typically short gold as hedgers. If they're reducing shorts while Managed Money adds shorts, that's a bullish divergence.

CROWDED TRADE ASSESSMENT:
  Crowded? CONDITIONAL — 2.9th percentile is extreme, but persistence is only 1 of last 6 weeks. This fails the persistence rule (need 4 of 6 weeks at <10th percentile). This is a *new* extreme, not a *crowded* one.
  Persistence: 1 of last 6 weeks at extreme.
  Stage of unwind: N/A — not yet crowded.

CONTRA-SIGNAL STRENGTH: moderate
  Rationale: The percentile (2.9th) is extreme, but the lack of persistence means this could be a one-week capitulation spike rather than a structural extreme. Managed Money is short gold at levels not seen in 3 years, but they've only been here for one week. If next week's COT shows them still short at <5th percentile, upgrade to strong.

INVALIDATION: A move back above 10th percentile next week would invalidate the extreme.
NEXT UPDATE: next Friday
```

### CL (Crude Oil)
```
INSTRUMENT: CL
DATE: 2026-05-19
DATA AGE: 5d

POSITIONING (Managed Money, primary):
  Net position: +98,219 contracts
  3-year percentile: 37.3rd
  Direction: neutral
  Trend (4-week change): +17,888 (increasing long)

POSITIONING (Producer/Merchant, supplementary):
  Not provided — but Commercials are typically short crude as hedgers. If they're adding shorts while Managed Money adds longs, that's a normal hedging dynamic.

CROWDED TRADE ASSESSMENT:
  Crowded? N — 37.3rd percentile is neutral.
  Stage of unwind: N/A

CONTRA-SIGNAL STRENGTH: none
  Rationale: Neutral percentile.

INVALIDATION: N/A
NEXT UPDATE: next Friday
```

---

## Summary: Most Extreme Positioning

**AUDUSD** is the standout — Leveraged Funds are at the **97.7th percentile** with **6 consecutive weeks** at extreme. This is the most crowded long in the watchlist. The contra-signal is **strong**, but the 5-day data staleness means we can't confirm whether the unwind has started in the last week. **Gold (GC)** at the 2.9th percentile is notable but lacks persistence — watch next week for confirmation.