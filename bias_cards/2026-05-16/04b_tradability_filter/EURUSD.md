```yaml
instrument: EURUSD
judge_direction: long
judge_conviction: 7
judge_timeframe: swing-to-positional (weeks to months)

structural_checks:
  trend_alignment: counter  # price below both SMA20 and SMA50 in a sideways tape
  location_quality: good_pullback  # near 20d low and support (1.1621), ATR distance small
  compression_or_expansion: neutral
  atr_suitability: ok  # 0.585% ATR is typical for EURUSD
  crowding_late_or_clean: clean  # -1.3% over 20d, not chasing a rally
  invalidation_clarity: clear_level  # daily close below 1.0650 (May swing low)
  invalidation_level: 1.0650
  blocking_event_within_5d: false
  blocking_event_detail: null

verdict: tradable_now
verdict_reason: >-
  Applied positional rules (swing-to-positional timeframe). Macro thesis
  (ECB hawkish pivot, rate‑differential compression) intact at conviction 7/10.
  Price is at the 20‑day low / support near 1.1621, offering a clean pullback
  location. Invalidation is a precise daily close below 1.0650. ATR is ordinary,
  no late‑chase signal, and no blocking events in the next 5 days.

human_review_notes: |
  The EURUSD long bias is supported by the ECB’s expected June hike and
  Fed‑ECB rate‑differential compression. Current price (1.1631) has pulled
  back to the May range lows, just above the 20‑day support at 1.1621. The
  50‑day SMA (1.1645) and 20‑day SMA (1.1723) are overhead, but a positional
  long can be built at this support. 

  Key level to hold: a daily close above 1.1621 would keep the pullback intact.
  Invalidation is a daily close below 1.0650 – far away, so risk can be
  managed with a wide stop. Upside target on a theme‑driven run is 1.14–1.15.
```