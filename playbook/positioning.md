# Positioning

How to read who's already in the trade. Positioning is one of the most underused inputs in retail macro and one of the most reliable contra-indicators at extremes. The principle is simple: when everyone is on the same side, the next move is the unwind, not the continuation.

This document is the canonical reference for the Positioning Analyst (Layer 1) and feeds directly into the Contrarian Agent (Layer 3) and Positioning Reversal Agent (Layer 3).

## Why Positioning Matters

Markets are ultimately the sum of all positions. When positioning becomes one-sided:

1. **The marginal buyer disappears.** Everyone who wanted to be long is already long. New buying can't come from existing holders.
2. **The unwind becomes the trade.** Crowded longs unwinding produce the largest moves, not new shorts entering.
3. **Liquidity is asymmetric.** Crowded markets have plenty of supply on the bid (everyone wants out at the same time) and thin demand. Moves can be brutal.
4. **Sentiment and price diverge late.** Position extremes can persist for weeks or months before unwinding. Positioning is a *condition*, not a *trigger*.

### The contra-indicator nature

Positioning at extremes works as a *contra-indicator*: extreme long positioning is bearish for the asset; extreme short positioning is bullish. But timing the unwind is where most positioning trades fail — extremes can persist.

The job of the Positioning Analyst is to **identify when positioning is at an extreme worth respecting**, not to predict when the unwind triggers.

## The Commitment of Traders Report (COT)

The CFTC publishes weekly futures positioning data every Friday for the prior Tuesday close. This is the most rigorous public positioning data available.

### Three report formats

| Format | Categories | Use for |
|---|---|---|
| **Legacy** | Commercial / Non-Commercial / Non-Reportable | FX, gold, simple commodities |
| **Disaggregated** | Producer/Merchant / Swap Dealers / Managed Money / Other | Energy, agricultural commodities |
| **Traders in Financial Futures (TFF)** | Dealer/Intermediary / Asset Manager / Leveraged Funds / Other | Treasuries, equity indices, currency futures |

### The categories that matter for macro

For our 10-instrument watchlist, the high-signal categories are:

- **Leveraged Funds** (TFF) — hedge funds, CTAs. The "smart money" that follows trends and is fast to unwind. Their positioning is the most useful contra-indicator at extremes.
- **Asset Managers** (TFF) — long-only mutual funds, pension funds. Slower to move, more "real money." Their positioning is more about flow than tactical bets.
- **Dealer/Intermediary** (TFF) — banks, market makers. Often inverse to client flow; less directional but reveals what flow they're warehousing.
- **Non-Commercial** (Legacy) — speculators broadly. Used for FX where TFF doesn't apply.
- **Commercial** (Legacy) — hedgers (oil producers, gold miners, exporters). NOT a contra-indicator; commercials hedge production, not sentiment.

### What's NOT in the COT

- **Spot FX positioning** (off-exchange, not reported)
- **OTC derivatives** (swaps, options outside listed)
- **Real-money flows** (pension allocations, sovereign wealth)
- **ETF positioning** (separate data source)

So COT is a *partial* read on positioning, but for futures-traded instruments (which is most of our watchlist) it's the cleanest.

## How to Identify Positioning Extremes

Don't use absolute levels. Use **percentiles over rolling lookback windows.**

### The methodology

1. Pull weekly COT data for the relevant category (e.g., Leveraged Funds net position for EUR futures)
2. Calculate **net position** = longs − shorts
3. Compute **rolling 3-year percentile** of net position
4. Flag extremes:
   - **>95th percentile** = extreme long positioning (bearish contra-signal)
   - **<5th percentile** = extreme short positioning (bullish contra-signal)
   - **80-95th** = stretched long, watch
   - **5-20th** = stretched short, watch

### Why percentiles, not z-scores

Net position distributions are often non-normal — fat tails, skewed. Z-scores assume normality and miss true extremes. Percentile rank is robust to distribution shape.

### Why 3-year lookback

- **Too short (1 year)** — extremes get smoothed away in trending regimes
- **Too long (10 years)** — captures different regime structures, dilutes signal
- **3 years** — captures one full economic cycle, balances regime change vs. statistical power

For instruments with structural shifts (e.g., gold's positioning regime changed post-2020 with central bank buying), shorten lookback to 2 years.

## Per-Instrument Positioning Read

| Instrument | Primary COT category | Notable quirks |
|---|---|---|
| **EUR (EURUSD futures)** | Leveraged Funds net | Persistent skews — Asset Managers structurally long, Leveraged Funds tactical |
| **JPY (USDJPY futures)** | Leveraged Funds net (note: JPY futures sign is inverse of USDJPY) | Carry-trade dynamic — short JPY = long USDJPY = popular trade for years; unwinds violent |
| **GBP** | Leveraged Funds net | Lower liquidity; positioning data noisier |
| **AUD** | Leveraged Funds net | China-sensitive — shifts often lead China-narrative shifts |
| **GC (Gold)** | Managed Money net | Central bank buying off-COT; positioning understates true flow |
| **CL (Oil)** | Managed Money + Producer/Merchant | Watch divergence — when speculators long while producers hedging short = extension top risk |
| **ZN (10Y Treasury)** | Leveraged Funds vs. Asset Managers | Asset Managers often structurally long duration; Leveraged Funds tactical |
| **ES (S&P)** | Leveraged Funds + Asset Managers | Positioning less informative for indices than for FX/commodities |
| **NQ (Nasdaq)** | Leveraged Funds | Often correlated with ES; small differential signal |
| **DXY** | Aggregate of FX components | Use weighted aggregate of EUR, JPY, GBP, CAD, AUD positioning |

## Dealer Gamma (Equity Options)

For ES and NQ specifically, dealer gamma exposure is a key positioning input that COT doesn't capture.

### The mechanism

- Market makers / dealers are typically **net short gamma** when puts are heavily owned by clients (defensive flows)
- Net short gamma means dealers must **sell as price falls** and **buy as price rises** to maintain delta neutrality — this **amplifies** moves
- Dealers are typically **net long gamma** when calls are heavily owned (chase flows)
- Net long gamma means dealers **buy as price falls** and **sell as price rises** — this **dampens** moves

### Signal extraction

- **Net long gamma regime** → low realized vol, mean-reverting price action
- **Net short gamma regime** → high realized vol, trending price action
- **Gamma flip points** → key technical levels where regime can change

The Positioning Analyst should track approximate dealer gamma using the SPX Gamma Exposure repo or equivalent. Output: current gamma regime, distance to flip point.

## ETF Flows

A second positioning lens for equities and credit specifically.

### What to track

- **SPY / QQQ daily creations/redemptions** — direction of retail/institutional flow into US equity
- **HYG / JNK flows** — high-yield credit appetite (proxy for risk-on/off)
- **TLT flows** — duration appetite
- **GLD / IAU flows** — physical gold demand (separate from futures positioning)
- **EM ETFs (EEM, VWO)** — EM appetite shifts

### Limitations

- ETF flows can be flow-driven (allocator rebalancing) rather than directional bets
- One-day flow spikes are noise; 5-day net flow is the signal
- Use as confirmation of futures positioning, not primary signal

## Sentiment Surveys (Lower Priority)

| Survey | Frequency | Use |
|---|---|---|
| AAII Investor Sentiment | Weekly | Retail equity sentiment; useful at extremes only |
| Investors Intelligence | Weekly | Newsletter writer sentiment; longer-cycle indicator |
| BoFA Fund Manager Survey | Monthly | Institutional positioning; high-signal but lagged |
| Conference Board Consumer Confidence | Monthly | Macro sentiment, slower-moving |

Sentiment surveys are **complementary** to COT, not primary. They confirm positioning extremes but rarely lead them.

## Crowded Trade Dynamics

When positioning is at extreme and the trade unwinds, the unwind has predictable patterns. Knowing them prevents getting caught on the wrong side.

### How crowded longs unwind

1. **Stage 1 — Distribution.** Smart money quietly trims while news flow stays positive. Price stays in range.
2. **Stage 2 — Lower highs.** Each rally fails to make new high; weak hands start exiting.
3. **Stage 3 — Trigger event.** Some news (often minor) prompts cascade. Stops trigger stops.
4. **Stage 4 — Capitulation.** Volume spikes; price overshoots fair value to the downside.
5. **Stage 5 — Reset.** Price stabilizes; positioning resets to neutral.

The Positioning Reversal Agent (Layer 3) is specifically tuned to flag Stage 1-2 transitions.

### How crowded shorts unwind (squeeze)

Symmetric pattern, but typically faster and more violent. Short squeezes are concentrated in time because cover demand is finite (the short interest, plus stops above).

### Common unwind catalysts

- **Surprise central bank shift** — crowded carry trades vs. CB pivot
- **Major data miss** — crowded growth bets vs. recession data
- **Geopolitical shock** — crowded risk-on vs. event
- **Quarter-end / month-end rebalancing** — mechanical, predictable timing

## Common Errors

1. **Confusing commercials with smart money.** Commercials hedge production. Their positioning is mechanical, not directional. Don't fade commercial extremes.
2. **Reading absolute levels instead of percentiles.** A net long EUR position of +200k contracts means nothing without context (is that 95th percentile or 50th?).
3. **Trading positioning as a trigger.** Extreme positioning is a *condition* — it predisposes the market to a reversal. The trigger comes from price action, news, or central bank shift. Don't short just because positioning is extreme.
4. **Ignoring dealer gamma in equities.** COT alone misses the most important positioning input for ES/NQ.
5. **Data freshness.** COT data is reported Tuesday-close, released Friday. By Monday, the data is 6 days stale. In fast-moving regimes, positioning may have already shifted.
6. **Confusing flow with sentiment.** ETF inflows can be allocator rebalancing (zero directional info). Always distinguish discretionary flow from mechanical flow.
7. **Single-week signal.** COT extremes that persist 4+ weeks are real. One-week spikes can be noise from a single large fund.

## Output Schema (Agent-Facing)

The Positioning Analyst produces this structured output, refreshed weekly post-COT release:

```
INSTRUMENT: [DXY | EURUSD | USDJPY | etc.]
DATE: YYYY-MM-DD (Tuesday-close of latest COT)
DATA AGE: [N] days (current date - Tuesday close)

POSITIONING (Leveraged Funds, primary):
  Net position: [contracts]
  3-year percentile: [N]th
  Direction: [extreme long | stretched long | neutral | stretched short | extreme short]
  Trend (4-week change): [increasing long | decreasing long | flat | etc.]

POSITIONING (Asset Managers, supplementary):
  3-year percentile: [N]th
  Notable divergence vs. Lev Funds: [Y/N + interpretation]

DEALER GAMMA (ES/NQ only):
  Regime: [net long gamma | net short gamma]
  Distance to flip: [percent]

ETF FLOWS (5-day net, where relevant):
  [SPY/QQQ/HYG/TLT/GLD]: [+/- $M, direction]

CROWDED TRADE ASSESSMENT:
  Is this position crowded? [Y/N + reasoning]
  Stage of unwind (if extreme): [N/A | Stage 1 | Stage 2 | etc.]

CONTRA-SIGNAL STRENGTH: [strong | moderate | weak | none]
  Rationale: [percentile + persistence + cross-confirmation]

INVALIDATION: [what would shift this read — e.g., positioning normalizing, new ATH in price]
NEXT UPDATE: [next Friday COT release date]
```

This output feeds the FX Strategist (Layer 2), the Bias Council (Layer 4), and especially the Contrarian Agent (Layer 3).

## What This Framework Does NOT Do

- **Time the unwind.** Identifies extremes; doesn't predict trigger date.
- **Replace cross-asset confirmation.** A positioning extreme without confirming price action is a *condition*, not a trade.
- **Capture all positioning.** OTC, real-money flows, EM positioning largely off-book.
- **Work in low-liquidity instruments.** COT data is noisy for thinly traded futures.

## Calibration

The Calibration Agent (Layer 7) tracks whether positioning extremes flagged by this framework subsequently produced the expected reversals. After 6+ months of journal data, refine the percentile thresholds (95/5 may be too tight or too loose for specific instruments) and the per-instrument primary-category choices.
