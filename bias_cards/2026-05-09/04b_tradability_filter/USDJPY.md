```yaml
instrument: USDJPY
judge_direction: long
judge_conviction: 5

structural_checks:
  trend_alignment: counter
  location_quality: good_pullback
  compression_or_expansion: neutral
  atr_suitability: ok
  crowding_late_or_clean: clean
  invalidation_clarity: clear_level
  invalidation_level: 150.00
  blocking_event_within_5d: true
  blocking_event_detail: "US CPI April on 2026-05-12 (in 3 days) — high severity; for swing timeframe, does not auto‑downgrade but warrants note."

verdict: watch
verdict_reason: "Applied swing rules: counter-trend long near 20d support (155.05) but price (156.62) slightly above ideal zone; CPI in 3 days is a high‑severity event — swing trades can hold through, but entry before the print adds binary risk; waiting for a clearer support test or post‑CPI conviction."
what_would_change_verdict: "A bullish daily close above SMA20 (≈158.64) after CPI, or a definitive bounce from the 155.00 area with increased momentum, would upgrade setup to tradable_now."

human_review_notes: |
  USDJPY is holding just above the 20‑day low (155.05) within the Judge’s entry zone of 154–156.  
  The trend is down, but swing‑timeframe longs near this support fit the bias — interest‑rate differential remains supportive, and the pullback is not a late chase.  
  The May 12 CPI print is the immediate catalyst; a soft number could break the 155 support, while a hot print would likely re‑energize the long.  
  Invalidation is a daily close below 150.00; until then, waiting for a reaction at support or post‑CPI resolution is the prudent path.
```