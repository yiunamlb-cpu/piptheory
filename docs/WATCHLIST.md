# Watchlist

Nine instruments. Cover every macro theme; minimize redundancy; all FTMO-tradeable; all deeply liquid.

Composition: ~55% FX, 22% indices, 22% commodities. FX-weighted because FX is the most analytically tractable asset class for a solo operator with LLM agents — cleaner driver set, two-sided macro plays, COT data is rich, central bank communication is the master variable.

**Note on rates:** ZN (10Y Treasury Note) was previously on the watchlist as the rates expression. It was removed in May 2026 because FTMO doesn't offer it as a tradable. The rates view is still actively tracked — Fed-Watcher (Layer 1) consumes UST 2Y/10Y/30Y from FRED and the Strategist uses that to inform USDJPY, gold, and equity bias cards. We just don't produce a "tradable" verdict for an instrument we can't actually trade.

## Focus list (formerly "active universe")

The user-facing dashboard term is **focus list** — instruments that go through the full pipeline (Layer 1 macro → Layer 2 strategist → Layer 3 contrarian → Layer 4 council debate → Layer 4b Tradability Filter → Layer 5 PM brief). The internal code constant is still `ACTIVE_UNIVERSE` in `src/orchestration/pipeline.py`.

**Current focus list: all 9 instruments** (DXY, EURUSD, USDJPY, GBPUSD, AUDUSD, ES, NQ, GC, CL).

The focus list started as the 3 most-tradeable on FTMO (ES, NQ, GC) per the architectural review's "keep the universe small while we refine" guidance. It was later expanded to the full FTMO-eligible set once the pipeline was producing reliable output.

**What "in the focus list" means concretely:**
- The Layer 4 council (Bull / Bear / Judge) runs for the instrument when its Strategist conviction meets the threshold (currently 5/10).
- The Layer 4b Tradability Filter runs after the Judge, producing a structural-review verdict: `tradable_now`, `watch`, or `pass_despite_bias`.
- The PM brief categorizes setups in this instrument by filter verdict.

Instruments outside the focus list (currently none) would still get Layer 1-3 analysis as wider macro context, but no chart-level review and no PM-brief categorization.

**Cost trade-off**: full focus-list coverage runs ~$0.80-1.20 per pipeline run vs ~$0.30 with the original three. Daily cost ~$25-35/month at the expanded universe.

## FX (5)

### DXY — US Dollar Index
**Theme expressions:** Fed-watch, US growth differential, global liquidity proxy.
**Why:** The single most important macro instrument. Reads as a referendum on US relative growth and Fed path. Every other instrument's bias is partly derived from a DXY view.
**Caveats:** Index weights are stale (heavy euro tilt). Cross-check with Bloomberg Dollar Index (BBDXY) when conviction matters.

### EURUSD
**Theme expressions:** Fed-ECB rate differential, Eurozone growth, periphery/banking risk.
**Why:** Cleanest two-sided macro pair. ECB hawkish pivot vs. Fed-stuck = bullish setup. ECB dovish vs. Fed hawkish = bearish setup. Highly liquid, tight spreads.

### USDJPY
**Theme expressions:** Real rate differential, Japan policy normalization, risk-on/off via JPY safe-haven role.
**Why:** Most reactive to US yields. JPY weakness is the cleanest expression of "US growth + high rates" theme.
**Caveats:** **Intervention risk is real and continuous** when above ~155. Cap size on long USDJPY when MoF/BoJ rhetoric heats up. Risk Manager agent flags this automatically.

### GBPUSD
**Theme expressions:** BoE policy, UK growth, GBP carry differential.
**Why:** Diversifier vs. EURUSD when ECB and BoE diverge. Less liquid; wider spreads than EURUSD.

### AUDUSD
**Theme expressions:** China demand (commodities channel), RBA policy, risk sentiment proxy.
**Why:** Cleanest proxy for "China growth" and "commodity supercycle." When China-deflation and commodity-strength themes collide, AUD is the expression vehicle.
**Caveats:** Cross-currents make pair selection tricky — sometimes prefer AUD/JPY for cleaner risk-on read.

## Indices (2)

### ES — S&P 500 Futures
**Theme expressions:** Risk-on/off, Fed-pivot expectations, US earnings cycle, AI capex.
**Why:** Most liquid risk-on/off vehicle. AI capex theme expresses through here.
**Caveats:** Long-bias regime; short side requires specific catalyst. Earnings-season distortions; gap risk Sunday opens.

### NQ — Nasdaq 100 Futures
**Theme expressions:** AI capex theme directly. Higher beta to liquidity changes than ES.
**Why:** Cleaner AI-theme expression than ES. Preferred over ES when AI is the dominant macro narrative.
**Caveats:** Mega-cap concentration means single-stock event risk (earnings prints) leaks into NQ.

## Commodities (2)

### GC — Gold Futures
**Theme expressions:** Real rates, USD direction, geopolitical risk, central bank reserve diversification, China household demand.
**Why:** The most cross-asset-confirmable macro instrument. Gold strength validates inflation regime, dollar weakness, geopolitical premium, EM CB demand simultaneously. Rare instrument that benefits from multiple macro vectors at once.

### CL — Crude Oil Futures
**Theme expressions:** Geopolitical risk, global growth, OPEC supply discipline.
**Why:** Direct expression of energy-shock theme. Iran/Middle East premium prices through here.
**Caveats:** **Geopolitical whipsaw risk** — a ceasefire can wipe out a position in hours. Cap size; use options-equivalent thinking on stop placement.

## What's Deliberately NOT On The List

- **ZN / Treasury futures** — not offered on FTMO. Rates view still tracked from FRED but not as a tradable instrument.
- **Single equities** — earnings idiosyncrasy + gap risk violates emergency-stop framework
- **Crypto** — different vol/liquidity regime; different analytical toolkit; not a clean macro expression
- **EM FX** — illiquid, intervention risk, prop firms often restrict
- **European indices (DAX, FTSE)** — analytically worse than US (more variables, harder positioning data); correlation high during regime moves so "diversification" is illusory
- **Non-USD commodity pairs** — adds complexity without information

## Rules for Adding/Removing

**Bar to add:** Must express a macro theme that the existing 9 don't capture cleanly, AND must be FTMO-tradeable with reasonable spreads. Example: if a "China stimulus actually working" regime emerges, copper or HG might earn a temporary slot.

**Bar to remove:** Instrument that hasn't produced a tradeable setup in 6+ months OR has structurally changed (delisting, prop-firm restriction, structural liquidity collapse).

Don't add or remove based on a single losing trade or a hot week. Watchlist changes are reviewed quarterly.
