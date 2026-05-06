# Regime Identification

The master framework. Every agent in the stack conditions its reasoning on a regime classification — get this wrong and every layer below is reasoning in the wrong context. This document defines the framework, the decision rules, and the failure modes.

Primary sources distilled here: Ray Dalio's *How the Economic Machine Works* and *Principles for Navigating Big Debt Crises*; Bridgewater's quadrant framework as publicly described; Howard Marks on cycles; practitioner consensus on liquidity overlays.

## Why This Matters

A regime is the *context* in which all asset behavior is interpreted. The same headline (e.g., "stronger-than-expected jobs report") means different things in different regimes:

- In **Goldilocks**: confirms the bull thesis, equities rip, dollar firms.
- In **Stagflation**: tightens the screws further, bonds break, equities crack.
- In **Deflation**: meaningless noise — the deflation impulse dominates.

If an agent reasons about a data point without first establishing the regime, the reasoning is structurally flawed. Every Layer 1 specialist (Fed-Watcher, Inflation Tracker, etc.) must produce its analysis *conditional on the current regime read*.

## The Dalio Growth/Inflation Quadrant

The canonical framework. Two axes — direction of growth, direction of inflation — produce four quadrants, each with a default asset playbook.

```
                         INFLATION
                  Rising              Falling
              ┌─────────────────┬─────────────────┐
              │                 │                 │
       Rising │   REFLATION     │   GOLDILOCKS    │
              │                 │                 │
   GROWTH     ├─────────────────┼─────────────────┤
              │                 │                 │
      Falling │   STAGFLATION   │   DEFLATION     │
              │                 │                 │
              └─────────────────┴─────────────────┘
```

### Quadrant 1 — Reflation (Rising growth, rising inflation)

**Driver:** Recovery from prior weakness; demand rebuilding; commodities firm.
**What works:** Cyclicals (industrials, energy, financials), commodity currencies (AUD, CAD, NOK), inflation-linked bonds, gold (sometimes).
**What doesn't:** Long-duration bonds, defensives, tech (rate-sensitive), USD if Fed is behind.
**Recent examples:** 2003-2006, 2010-2011, 2021 reopening, late 2020 reflation trade.

### Quadrant 2 — Goldilocks (Rising growth, falling inflation)

**Driver:** Productivity gains, supply normalization, disinflation without recession.
**What works:** Risk assets broadly, especially long-duration equity (tech, growth), credit, EM. The "everything rally" regime.
**What doesn't:** Volatility (VIX shorts work), defensives, commodities (mixed).
**Recent examples:** Mid-1990s, 2017, parts of 2024-2025 (early AI capex era), classic late-cycle expansion.
**Watch for:** Goldilocks is the most psychologically dangerous regime because everything works and conviction grows complacent. Transitions OUT are sudden.

### Quadrant 3 — Stagflation (Falling growth, rising inflation)

**Driver:** Supply shocks (energy, geopolitical), policy mistakes, structural cost increases.
**What works:** Gold, energy commodities, USD (if Fed is most aggressive), short-duration bonds, defensive value.
**What doesn't:** Equities broadly, long-duration bonds, EM (capital flight), housing.
**Recent examples:** 1970s, 2022 (energy shock + rate hikes), arguably 2026 current setup with Iran oil shock.
**Watch for:** Central banks hate this regime — they will eventually break growth to kill inflation, which transitions us to Deflation.

### Quadrant 4 — Deflation (Falling growth, falling inflation)

**Driver:** Demand collapse, debt deleveraging, financial deleveraging.
**What works:** Long-duration bonds, USD (safe-haven), defensives (utilities, consumer staples), gold (sometimes — competing forces).
**What doesn't:** Equities, commodities, EM, credit, anything cyclical.
**Recent examples:** 2008-2009, March 2020 acute phase, ongoing China since ~2022.
**Watch for:** Deflation regimes often precipitate policy panic responses (QE, fiscal expansion) that transition violently to Reflation. Timing is brutal.

## How to Identify the Current Quadrant

Don't guess. Use a structured input set with explicit rules.

### Growth signals (use 3+ of these)

| Indicator | Bullish (rising) | Bearish (falling) |
|---|---|---|
| US ISM Manufacturing PMI | >50 and trending up | <50 or trending down |
| US Services PMI | >52 and trending up | <50 or trending down |
| Non-Farm Payrolls (3-month avg) | >150k | <100k or contracting |
| Atlanta Fed GDPNow | Above consensus, trending up | Below consensus, trending down |
| Citi Economic Surprise Index (US) | >+25 and rising | <-25 or rolling over |
| Conference Board LEI | Positive YoY, accelerating | Negative YoY, decelerating |

### Inflation signals (use 3+ of these)

| Indicator | Rising | Falling |
|---|---|---|
| Headline CPI YoY | Trending up over 3 months | Trending down |
| Core PCE YoY (Fed's preferred) | Trending up | Trending down |
| 5y5y Inflation Breakevens | >2.5% and rising | <2% or falling |
| 10y Inflation Breakevens | Rising | Falling |
| Commodity Index (CRB or Bloomberg) | Trending up over 3 months | Trending down |
| Average Hourly Earnings YoY | >4% or rising | <3.5% or falling |
| Sticky Price CPI (Atlanta Fed) | Rising | Falling |

### Decision rule

For each axis (growth, inflation):
- **3+ indicators directional** → take that direction with conviction
- **2 directional, 1+ ambiguous** → take that direction with moderate conviction
- **<2 directional or contradicting** → "uncertain" / "transition" — don't force a quadrant

### Lookback discipline

- Trends over **3 months** are credible. Single prints are noise — Fed and ECB both say this and they're right.
- Year-over-year > month-over-month for inflation. M/M is too noisy.
- Quarterly averages > monthly averages for sentiment surveys.

If the agents only react to the latest print, the regime classification will whipsaw. Encode the 3-month rule into prompts.

## Liquidity Overlay (The Hidden Master Variable)

The quadrant alone is incomplete. **Liquidity is the master variable that can override quadrant playbooks.** A correct regime read with the wrong liquidity overlay still produces wrong trades.

### Liquidity inputs

| Indicator | Easing | Neutral | Tightening |
|---|---|---|---|
| Fed balance sheet (SOMA) | Expanding | Flat | QT active, contracting |
| Reverse Repo (RRP) | Falling fast (cash entering markets) | Stable | Rising (cash exiting) |
| Bank reserves (Fed H.4.1) | Rising | Flat | Falling |
| Treasury General Account (TGA) | Falling (Treasury spending) | Stable | Rising (Treasury rebuilding) |
| Net liquidity (= Fed BS - TGA - RRP) | Rising | Flat | Falling |

### How liquidity modifies the quadrant playbook

- **Goldilocks + Easing liquidity** → maximum risk-on; the canonical environment for AI-2024 / 2017
- **Goldilocks + Tightening liquidity** → fragile; one shock cracks everything (think H2 2022 brief Goldilocks impulses crushed by QT)
- **Reflation + Easing** → commodities supercharged
- **Stagflation + Tightening** → the worst regime; everything except gold/energy struggles
- **Deflation + Easing** → eventually transitions to Reflation; the question is "when"
- **Deflation + Tightening** → debt-deflation spiral risk; the most dangerous combination

When in doubt, **trust liquidity over quadrant.** A regime classified as "Goldilocks" with rapidly tightening liquidity is more likely to break to the downside than to follow the Goldilocks playbook.

## Cross-Asset Confirmation

A regime read is only credible if multiple asset classes confirm it. If they don't, either:
1. The regime is genuinely in transition (highest probability)
2. The read is wrong
3. A specific instrument is being driven by an idiosyncratic factor (capital flow, intervention, technical squeeze)

### Confirmation signals per regime

| Regime | DXY | Bonds (10Y yield) | Equities | Gold | Credit Spreads |
|---|---|---|---|---|---|
| Reflation | Down (typically) | Up | Up (cyclicals lead) | Mixed | Tighter |
| Goldilocks | Down or stable | Down (or stable, low term premium) | Up (growth leads) | Down | Tighter |
| Stagflation | Up (if Fed leads) | Up | Down | Up | Wider |
| Deflation | Up (safe haven) | Down sharply | Down | Mixed (initially down, then up on policy response) | Wider sharply |

If you classify Goldilocks but credit spreads are widening and gold is making new highs, **the classification is wrong** or the regime is transitioning. Trust the cross-asset signal over the formal classification.

## Transition Signals (Lead Indicators)

Regimes don't change overnight — they shift gradually. The valuable trade is recognizing the transition before consensus does.

### Goldilocks → Reflation transition

- Commodity index turning up persistently (especially oil, copper)
- Inflation breakevens widening
- Yield curve steepening from belly outward
- Cyclicals starting to outperform tech/growth
- Wage growth re-accelerating

### Goldilocks → Stagflation transition

- Supply shock (energy, geopolitical) causing commodity spike
- Central bank language becoming defensive about inflation
- Yield curve flattening (front end up faster than long end)
- Equity volatility rising while equities still drift up (the "boiling frog" pattern)
- Defensives quietly outperforming growth

### Stagflation → Deflation transition

- Growth indicators rolling over (PMIs <50)
- Credit spreads widening
- Bank lending standards tightening (SLOOS survey)
- Commodity prices breaking down despite still-elevated CPI
- Consumer confidence cracking

### Deflation → Reflation transition

- Central banks shifting toward easing (rate cuts, QE)
- Fiscal stimulus announcements
- Liquidity measures expanding
- Equity bottoming (often with bad news that fails to push prices lower)
- Credit spreads peaking

### The "boring crash" pattern

Transitions FROM Goldilocks to Stagflation or Deflation are rarely dramatic events. They look like:
1. Vol creeps up while spot drifts up — agents should flag this divergence
2. Defensives quietly outperform growth — leadership rotation
3. Credit spreads widen modestly — bond market sees what equity doesn't yet
4. One narrative crack (e.g., a single AI capex guide-down, a single bank stress) — the spark

By the time equities crack visibly, the transition is already 60% done. Agents that wait for confirmation in the equity index are too late.

## Common Errors

1. **Recency bias.** Extrapolating the last regime forward is the #1 mistake. The market is always paid to *anticipate* transitions, not to confirm them. If you find yourself saying "we've been in Goldilocks for 18 months, why would it change now," that's the warning signal.
2. **Single-data-point reaction.** One CPI print doesn't change a regime. Three months of trend does. Encode this in agent prompts to prevent whipsaw.
3. **Ignoring liquidity.** The most common failure mode of pure quadrant classification. Always run the liquidity overlay.
4. **Forcing classification.** Sometimes "transition" or "uncertain" is the right answer. The Bias Council's Judge agent should accept "stand aside" as a valid output. Forcing a quadrant in genuinely ambiguous data leads to overconfident bad trades.
5. **Cross-asset blindness.** Reasoning about one asset in isolation. Always check that DXY/yields/equities/gold/credit confirm the read.
6. **Geopolitical denial.** Geopolitical shocks (war, sanctions, regime change) are not part of the quadrant framework — they're an *overlay*. They can override quadrant logic temporarily. The Geopolitical Risk Agent (Layer 1) feeds this overlay; the Cross-Asset Confirmer (Layer 1) integrates it.

## Decision Checklist (Agent-Facing)

Every regime-conditioning agent should produce output answering these in order:

1. **Growth direction:** rising / falling / uncertain (cite 3+ indicators)
2. **Inflation direction:** rising / falling / uncertain (cite 3+ indicators)
3. **Liquidity regime:** easing / neutral / tightening (cite 2+ indicators)
4. **Implied quadrant:** Reflation / Goldilocks / Stagflation / Deflation / Transition
5. **Cross-asset confirmation:** does DXY/yields/equities/gold/credit tell consistent story? Y/N + which signals dissent
6. **Geopolitical overlay:** any active shocks that override quadrant playbook?
7. **Conviction:** high / medium / low — based on signal alignment, not gut
8. **Invalidation:** what data print or price level would force a re-read?

This is the standardized output format. Every Layer 1 specialist consumes this; every Layer 2 strategist conditions on this.

## What This Framework Does NOT Do

- **Predict timing of regime shifts.** Identifies regimes; doesn't time them. That's the bias council + execution layer.
- **Account for geopolitical shocks intrinsically.** Treated as an overlay, not a fifth axis.
- **Substitute for primary-source reading.** The Fed-Watcher / ECB-Watcher / etc. still read the actual statements. This framework tells them what context to read in.
- **Provide trade entries.** Regime classification gives bias; the strategy mechanic (trend-pullback) gives entries.
- **Replace judgment.** The framework structures the input; the human (and judge agent) still makes the call when signals conflict.

## Calibration Note

This document is the canonical reference for regime classification. As the calibration agent (Layer 7) accumulates data on which classifications were correct vs. wrong, it will identify systematic errors in this framework's application. Update this file when those patterns emerge — but only after at least 6 months of journal data, not based on a hot week of bad calls.
