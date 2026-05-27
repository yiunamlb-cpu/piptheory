```yaml
instrument: GC
judge_direction: long
judge_conviction: 6

structural_checks:
  trend_alignment: mixed                          # trend is sideways, price slightly above 20/50 SMA, no clear swing directional alignment
  location_quality: mid_range                     # 4720 vs 20d range 4512-4880, no anchor nearby
  compression_or_expansion: expanding             # 5d range ~224 vs ATR 75.8 (~3x ATR), elevated volatility
  atr_suitability: ok                             # 1.6% ATR is acceptable for swing holding
  crowding_late_or_clean: clean                   # -0.9% 20d, -3.3% from 20d high, no chase signal
  invalidation_clarity: clear_level               # judge provides 3050 as daily-close invalidation (far below, but a specific level)
  invalidation_level: 3050                        # note: level is stale vs current 4720 price; PM will need a nearer tactical invalidation
  blocking_event_within_5d: true                  # US CPI in 2 days (HIGH severity, direct gold impact)
  blocking_event_detail: "2026-05-12 US CPI — master catalyst for reflation/stagflation thesis; binary for gold"

verdict: watch
verdict_reason: "Swing bias long supported by macro themes, but mid-range location with no nearby support and binary CPI 2 days away makes immediate entry risky; prefer post‑event confirmation or a pullback to SMA20 (4,695). Applied swing rules: event ≤2 days blocks tradable_now, location mid‑range reinforces watch."
what_would_change_verdict: "A pullback to the SMA20 (~4,695) with CPI past, or a break above 4,880 resistance on post‑CPI momentum, would upgrade to tradable_now."

human_review_notes: |
  Gold sits at 4,720, mid‑range and sideways, just above the 20‑ and 50‑day SMAs. The macro bias remains long, but the chart offers no clean pullback entry ahead of CPI. The judge’s 3,050 invalidation level is stale relative to the actual gold price — consider a nearer tactical stop below the 20‑day low (4,512) or below 4,550 for swing risk management. A cleaner entry would be a dip toward 4,695 (SMA20) or waiting until May 13 to see how the binary plays out.
```