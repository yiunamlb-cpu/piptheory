```yaml
instrument: EURUSD
judge_direction: long
judge_conviction: 6

structural_checks:
  trend_alignment: long_aligned
  location_quality: good_pullback
  compression_or_expansion: neutral
  atr_suitability: ok
  crowding_late_or_clean: clean
  invalidation_clarity: clear_level
  invalidation_level: 1.1250
  blocking_event_within_5d: true
  blocking_event_detail: "US CPI April (HIGH) on 2026-05-12, 1 day away – within 2-day swing blocking window"

verdict: watch
verdict_reason: "Applied swing rules: trend aligned, pullback to SMA20, clear invalidation at 1.1250, but US CPI in 1 day is a blocking event within 2 days, downgrading to watch."
what_would_change_verdict: "CPI clears without invalidating the bull thesis (e.g., headline ≤3.5% and Fed maintains easing bias), then setup becomes tradable_now."

human_review_notes: |
  EURUSD is at 1.1765, just above the 20-day SMA (1.1738) after a modest pullback from the 1.1809 high. The structural long bias is intact with a clean invalidation at 1.1250. The immediate obstacle is tomorrow’s US CPI – a hot print could force a Fed hawkish shift and break the rate-differential story. Wait for the CPI dust to settle; a daily close above 1.1800 after the event would confirm the pullback buy. Invalidation remains a multi-day close below 1.1250.
```