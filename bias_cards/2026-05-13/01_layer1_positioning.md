## Positioning Analyst Report
**Report date:** 2026-05-13  
**COT observation date:** 2026-05-05 (Tuesday) → released 2026-05-08  
**Data age:** 5 days — *recent* (not stale, but 5-day lag in a fast market can matter)  
**Missing instruments:** ES, NQ, DXY (no COT data provided); ETF flows and dealer gamma not supplied.  

---

### Per-instrument structured output

#### EURUSD
**INSTRUMENT:** EURUSD  
**DATE:** 2026-05-05  
**DATA AGE:** 5 days  
**Freshness tag:** `[recent · obs 2026-05-05 · released 2026-05-08 · 5d old]`  

**POSITIONING (Lev Money, primary):**  
  - Net position: +11,846 contracts  
  - 3-year percentile: 52.0th  
  - Direction: **neutral**  
  - Trend (4-week change): decreasing long (−13,536)  

**POSITIONING (Asset Managers):** Not available  
**DEALER GAMMA (ES/NQ only):** N/A  
**ETF FLOWS:** Not available  

**CROWDED TRADE ASSESSMENT:**  
  - Crowded? **No** — percentile inside the neutral band  

**CONTRA-SIGNAL STRENGTH:** None  
**INVALIDATION:** A move to >80th or <20th percentile with multi-week persistence would shift the read.  
**NEXT UPDATE:** Next Friday COT release (2026-05-15).  

---

#### USDJPY (read as Leveraged Funds position on JPY futures)
**INSTRUMENT:** USDJPY (via JPY futures)  
**DATE:** 2026-05-05  
**DATA AGE:** 5 days  
**Freshness tag:** `[recent · obs 2026-05-05 · released 2026-05-08 · 5d old]`  

**POSITIONING (Lev Money, primary):**  
  - Net position: −52,897 contracts (short JPY, i.e. long USDJPY)  
  - 3-year percentile: 33.7th  
  - Direction: **neutral** (slightly bearish JPY, bull USDJPY, but not stretched)  
  - Trend (4-week change): increasing long USDJPY (+1,548 contracts)  

**POSITIONING (Asset Managers):** Not available  
**DEALER GAMMA:** N/A  
**ETF FLOWS:** Not available  

**CROWDED TRADE ASSESSMENT:**  
  - Crowded? **No**  

**CONTRA-SIGNAL STRENGTH:** None  
**INVALIDATION:** A sustained push above 80th percentile (extreme short JPY) would flag a crowded USDJPY long.  
**NEXT UPDATE:** Next COT.  

---

#### GBPUSD
**INSTRUMENT:** GBPUSD  
**DATE:** 2026-05-05  
**DATA AGE:** 5 days  
**Freshness tag:** `[recent · obs 2026-05-05 · released 2026-05-08 · 5d old]`  

**POSITIONING (Lev Money, primary):**  
  - Net position: +26,049 contracts  
  - 3-year percentile: 32.6th  
  - Direction: **neutral**  
  - Trend (4-week change): increasing long (+3,718)  

**CROWDED TRADE ASSESSMENT:**  
  - Crowded? **No**  

**CONTRA-SIGNAL STRENGTH:** None  

---

#### AUDUSD
**INSTRUMENT:** AUDUSD  
**DATE:** 2026-05-05  
**DATA AGE:** 5 days  
**Freshness tag:** `[recent · obs 2026-05-05 · released 2026-05-08 · 5d old]`  

**POSITIONING (Lev Money, primary):**  
  - Net position: +56,600 contracts  
  - 3-year percentile: **97.1st**  
  - Direction: **extreme long**  
  - Trend (4-week change): rapidly increasing long (+12,958)  
  - Weeks at extreme in last 6: **6/6**  

**CROWDED TRADE ASSESSMENT:**  
  - **Crowded? YES** — metric tightly meets the persistence rule: >95th percentile, plus ≥4 of last 6 weeks at >90th (here, 6 of 6).  
  - Persistence: 6 of last 6 weeks. The position has been elevated beyond simple noise; it’s a deep, durable long.  
  - Stage of unwind: **Unable to assess** (no price/vol data provided). Without price context, a precise stage (1-5) cannot be assigned. The mere extreme suggests early distribution risk, but a liquidating trigger is absent in this snapshot.  
  - Contra-signal strength: **moderate** — extreme positioning (97th %ile) with full persistence generates a structural caution flag for AUDUSD longs. However, the signal is weakened by the lack of cross‑confirmation (no dealer gamma, ETF flows, price action), and by the freshness being recent (5 days old) but stale relative to any new moves since Friday 2026-05-08.  

**INVALIDATION:** A 4‑week retreat in percentile back below 80th without a price collapse would dilute the contra-signal. A sharp price break with declining open interest would validate the unwind.  

---

#### GC (Gold)
**INSTRUMENT:** GC (Gold futures)  
**DATE:** 2026-05-05  
**DATA AGE:** 5 days  
**Freshness tag:** `[recent · obs 2026-05-05 · released 2026-05-08 · 5d old]`  

**POSITIONING (Managed Money, primary):**  
  - Net position: +635 contracts  
  - 3-year percentile: **14.9th**  
  - Direction: **stretched short** (very low long positioning relative to history)  
  - Trend (4-week change): essentially flat (+57)  

**CROWDED TRADE ASSESSMENT:**  
  - Crowded? **No** — 14.9th percentile is above the 5th percentile threshold for “extreme short”. Its brief dip into extreme territory (1 week in last 6) does not meet the persistence criterion. However, the position lies near the low-end zone (5-20th), so it merits watching.  

**CONTRA-SIGNAL STRENGTH:** **weak** — low percentile is intriguing but not actionable without persistence and price confirmation. The flat trend adds little urgency.  

**INVALIDATION:** A drop below the 5th percentile for several weeks would upgrade to extreme‑short crowded status (bullish contra-signal).  

---

#### CL (Crude Oil)
**INSTRUMENT:** CL (WTI Crude Oil futures)  
**DATE:** 2026-05-05  
**DATA AGE:** 5 days  
**Freshness tag:** `[recent · obs 2026-05-05 · released 2026-05-08 · 5d old]`  

**POSITIONING (Managed Money, primary):**  
  - Net position: +70,791 contracts  
  - 3-year percentile: **20.0th**  
  - Direction: **stretched short** (low net long relative to history)  
  - Trend (4-week change): decreasing long (−27,577)  

**CROWDED TRADE ASSESSMENT:**  
  - Crowded? **No**  

**CONTRA-SIGNAL STRENGTH:** **none** — the 20th percentile is not extreme, and the trend toward reducing longs might simply reflect fundamental caution, not a crowded unwind.  

---

### Summary of Extremes
**AUDUSD Leveraged Funds net long sits at the 97.1st percentile, crowded for 6 consecutive weeks — the only extreme, persistent positioning across the watchlist.** Gold’s 14.9th percentile is low but lacks persistence; no other instrument touches the tails. Without price or flow confirmation, the AUDUSD crowded-long flag carries moderate contra-signal strength, warranting a close watch for any liquidation triggers.