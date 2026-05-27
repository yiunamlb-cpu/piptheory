```yaml
instrument: EURUSD
judge_direction: long
judge_conviction: 5

structural_checks:
  trend_alignment: long_aligned
  location_quality: good_pullback
  compression_or_expansion: neutral
  atr_suitability: ok
  crowding_late_or_clean: clean
  invalidation_clarity: clear_level
  invalidation_level: 1.0500
  blocking_event_within_5d: false
  blocking_event_detail: null

verdict: watch
verdict_reason: "Applied swing rules: sideways trend is acceptable, location near 20d low is a pullback, but price (1.1673) remains well above the Judge’s intended entry zone (1.0720–1.0800); waiting for a deeper retracement or a range breakout would provide a cleaner structural entry."
what_would_change_verdict: "A pullback into the 1.0720–1.0800 zone, or a daily close above 1.1851 with expanding range, would upgrade to tradable_now."

human_review_notes: |
  EURUSD is at 1.1673, near the bottom of its 20-day range (1.1656–1.1851) and just above the 20-day low. The macro bias is bullish on ECB hawkishness, but the Judge’s preferred entry zone is much lower (1.0720–1.0800). The current level is a potential support, but the pullback may not be deep enough to offer a favorable risk/reward given the sideways trend and the distance to invalidation (1.0500). Watch for a test of 1.1656 or a move into the 1.08 area before considering entry. Invalidation remains a weekly close below 1.0500.
```