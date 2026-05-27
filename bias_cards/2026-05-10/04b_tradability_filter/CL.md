```yaml
instrument: CL
judge_direction: slight long
judge_conviction: 5

structural_checks:
  trend_alignment: long_aligned       # sideways trend allowed under tactical rules
  location_quality: mid_range         # price near 95.42, no anchor at nearby support
  compression_or_expansion: expanding # ATR 7.39%, recent 5d range 88.66–107.46
  atr_suitability: too_wide           # ATR >3% of price; stops would be disproportionately large
  crowding_late_or_clean: clean       # no late-chase signal (20d change only -1.2%)
  invalidation_clarity: fuzzy         # “pre‑conflict support” not a specific price level
  invalidation_level: null
  blocking_event_within_5d: false
  blocking_event_detail: null

verdict: watch
verdict_reason: >
  Applied tactical rules: location is mid‑range with no nearby support to anchor a long,
  ATR at 7.4% of price makes tight stop placement impractical, and the invalidation level
  (“pre‑conflict support”) lacks a specific price. Wait for a defined pullback to a clear
  support zone before considering entry.
what_would_change_verdict: >
  A pullback to a specific, named support (e.g., the pre‑conflict range floor or the
  5‑day low near 88.66) with a clear invalidation close and volatility contracting.

human_review_notes: |
  CL bias is slightly long, but today’s structure doesn’t offer a clean tactical entry.
  Price at 95.42 sits in the middle of a wide 5‑day range (88.66–107.46) after a volatile
  week, and ATR is elevated at ~7.4%. The invalidation level the Judge describes — a close
  below pre‑conflict support — hasn’t been pinned to a specific number, making it hard to
  construct a well‑defined tactical stop. Watch for a test of the 5‑day low (88.66 area) or
  a clearer support level that can serve as both entry zone and invalidation line. If the
  pullback materializes with lower ATR and a specific trigger, the setup becomes tradable;
  until then, size‑cap constraints and an undefined stop argue for patience.
```