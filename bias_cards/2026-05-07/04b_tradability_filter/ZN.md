```yaml
instrument: ZN
judge_direction: short
judge_conviction: 5

structural_checks:
  trend_alignment: short_aligned
  location_quality: mid_range
  compression_or_expansion: neutral
  atr_suitability: ok
  crowding_late_or_clean: clean
  invalidation_clarity: clear_level
  invalidation_level: 111.00
  blocking_event_within_5d: false
  blocking_event_detail: "CPI data is intra-position noise per positional rules; trade may be sized smaller ahead of release."

verdict: watch
verdict_reason: "Conviction 5/10 is below the 6/10 threshold for positional tradability, reflecting binary CPI risk and extreme short positioning, despite intact macro thesis and clear invalidation."
what_would_change_verdict: "Resolution of the CPI binary (catalyst pass) or a rally to the 110-00 entry zone would likely upgrade to tradable_now."

human_review_notes: |
  The bearish bonds thesis is well-supported by the reflation theme and the downtrend is intact. ZN price at 110-26 offers a favorable risk/reward if the macro trend continues — invalidation at 111-00 is close and target toward 107-00 provides ~3.5 points of potential. However, the approaching CPI release and an extremely crowded short base introduce two-way risk that could trigger a sharp squeeze. Consider waiting for either a better entry on a rally to 110-00 or after the May 12 data clears. Sizing should be conservative until the binary risk is out of the way.
```