```yaml
instrument: GC
judge_direction: long
judge_conviction: 7

structural_checks:
  trend_alignment: mixed               # sideways below SMA20; positional timeframe accepts this
  location_quality: good_pullback      # 0.13 ATR from 20-day SMA, within bias-accumulation zone
  compression_or_expansion: neutral
  atr_suitability: ok                  # 1.56% ATR, normal for gold
  crowding_late_or_clean: clean        # 20d change -3%, well off the high
  invalidation_clarity: fuzzy          # Judge’s price invalidation (2400) absent from actual chart; macro thesis invalidation is clear (ceasefire + oil drop + CPI)
  invalidation_level: null             # disconnected from current price scale
  blocking_event_within_5d: false
  blocking_event_detail: null

verdict: tradable_now
verdict_reason: |
  Applied positional rules: macro thesis intact, location is a clean pullback to the 20‑day SMA (0.13 ATR), ATR normal, no blocking events. Invalidation clarity is fuzzy on price but well‑defined on macro conditions; acceptable for multi‑month position.

human_review_notes: |
  Gold is pulling back to the 20‑day SMA near 4685 after a 3% decline from recent highs, offering a structurally clean location for a multi‑month long on the stagflation/PBoC thesis. ATR at 1.6% is normal, no crowded long extremes. Note that the Judge’s bias card references levels around 2500, which do not correspond to the actual contract price (4677) — structural checks are based on the real market data. Invalidation would be a macro‑thesis breakdown (Iran ceasefire, oil below $60, CPI <2.5%) or a Fed shift to an explicit hike signal; no tight price‑level invalidation on the current chart.

what_would_change_verdict:                # omitted – not required for tradable_now
```