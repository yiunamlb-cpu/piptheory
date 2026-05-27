```yaml
instrument: GC
judge_direction: long
judge_conviction: 7

structural_checks:
  trend_alignment: long_aligned    # sideways trend is acceptable for swing bias
  location_quality: mid_range      # price $2,720 above entry zone $2,625–$2,650, not near a pullback to 20d SMA/50‑EMA
  compression_or_expansion: neutral  # 5d/20d ranges wide, ATR normal, not compressed
  atr_suitability: ok
  crowding_late_or_clean: clean     # 20d return -0.8%, 5d +2.0%, no late‑chase exhaustion
  invalidation_clarity: clear_level # weekly close below $2,480
  invalidation_level: 2480
  blocking_event_within_5d: true
  blocking_event_detail: "US CPI April, May 12 (in 3 days), HIGH – no auto‑downgrade for swing but binary event risk noted"

verdict: watch
verdict_reason: >
  Applied swing rules: sideways trend aligned, but price at $2,720 is mid‑range, above the favored pullback entry near $2,650/50‑day EMA.
  CPI in 3 days is a HIGH event with potential to force a hawkish repricing; waiting for a pullback to the entry zone and post‑CPI clarity 
  would upgrade the setup to tradable.
what_would_change_verdict: >
  A pullback to the $2,625–$2,650 zone and/or a CPI print that validates the reflation thesis (e.g., core MoM below 0.4%, TIPS yields 
  not spiking) without triggering the $2,480 invalidation would move the verdict to tradable_now.

human_review_notes: |
  Gold (GC) has a strong macro bullish bias (conviction 7/10) from energy‑driven reflation and PBoC buying, but the current price
  near $2,720 is above the preferred swing entry zone of $2,625–$2,650 (pullback toward the 50‑day EMA). The trend is sideways,
  positioning light, and the setup is not extended. The May 12 CPI release is a binary catalyst that could either validate the
  real‑yield compression thesis (supporting a push to $2,820+) or trigger a hawkish repricing (potential liquidation toward the
  $2,480 weekly close invalidation). If the pullback materializes and CPI passes without breaking the thesis, the setup becomes
  actionable. For now, it’s a watch‑and‑wait.
```