```yaml
instrument: EURUSD
judge_direction: slight_long
judge_conviction: 5

structural_checks:
  trend_alignment: mixed         # sideways trend, not counter but not supportive
  location_quality: mid_range    # price 1.1769, well above pullback zone (1.1250-1.1350), inside 20d range
  compression_or_expansion: neutral
  atr_suitability: ok
  crowding_late_or_clean: clean
  invalidation_clarity: clear_level
  invalidation_level: 1.1000
  blocking_event_within_5d: false
  blocking_event_detail: "HIGH US CPI on 2026-05-12 (4 days away); swing timeframe note only, not auto-downgrade"

verdict: watch
verdict_reason: "Swing bias intact but price is mid-range, well above the pullback entry zone (1.1250-1.1350) identified by the Judge; waiting for retracement toward 20d SMA (1.1735) or lower; CPI in 4 days adds binary risk."
what_would_change_verdict: "A pullback to below 1.1735 (20d SMA) or a clean break above 1.1850 (20d resistance) post-CPI would improve location and justify a tradable_now review."

human_review_notes: |
  EURUSD is trading at 1.1769, near the top of its recent range, above both the 20- and 50-day SMA. The macro case (ECB hiking, Fed on hold) supports a bullish lean, but the optimal entry zone for a swing long is 1.1250–1.1350. Currently, price is above the target zone in the bias card, suggesting the initial move has already occurred. The 20d high at 1.1851 is the next resistance, while support sits at 1.1656 and the SMAs at 1.1735. US CPI on Tuesday is the dominant catalyst; waiting for a post-CPI pullback to build a position is prudent. Invalidation remains a daily close below 1.1000.
```