```yaml
instrument: NQ
judge_direction: long
judge_conviction: 5

structural_checks:
  trend_alignment: long_aligned   # trend is up, aligned with long bias
  location_quality: extended       # ~0% from 20d high, +12% in 20d
  compression_or_expansion: expanding  # strong trend, wide ranges
  atr_suitability: ok              # 1.54% ATR is reasonable for NQ
  crowding_late_or_clean: late_chase  # pct_20d >5% and at 20d high
  invalidation_clarity: clear_level  # weekly close below 19,200 (Judge)
  invalidation_level: 19200
  blocking_event_within_5d: false
  blocking_event_detail: null

verdict: pass_despite_bias
verdict_reason: "Applied swing rules: price at extreme of a 20-day +12% rally with no pullback, and Judge’s bias-supporting entry zone (20,000–20,500) is far below current 29,708; entering here is a late chase against exhaustion risk."
what_would_change_verdict: "A deep pullback toward the 20‑day SMA (~27,970) or into the bias‑supporting zone would allow reassessment, provided macro thesis remains intact and a nearby invalidation level can be defined."

human_review_notes: |
  The current price (29,707) is far above the Judge’s assumed level (~20,600) and the bias‑supporting entry zone of 20,000–20,500, rendering the setup structurally untradable. NQ has rallied 12% in 20 days and is within 0.03% of its 20‑day high — this is a late chase. The Judge’s invalidation (weekly close below 19,200) is ~35% away and offers no practical stop for a swing entry from current levels. Even with the AI capex anchor, the location is hostile. A pullback to at least the 20‑day SMA near 28,000 would be required to bring the setup into tradable territory. Recommend revisiting the macro‑price alignment; if the bias is to be acted upon, the entry zone in the Judge card must be updated to reflect current market structure.
```