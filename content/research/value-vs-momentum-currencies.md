---
title: "Value vs Momentum in Currencies: What the Research Shows"
slug: value-vs-momentum-currencies
date: 2026-06-23
updated: 2026-06-23
keyword: value and momentum forex
summary: Value and momentum are the two most studied return premia in currency markets — and they move in opposite directions. Understanding how they interact is the key to reading when a trend is sustainable and when it is overextended.
faq:
  - q: What is the value factor in currency markets?
    a: The currency value factor measures how cheap or expensive a currency is relative to a fundamental anchor — usually purchasing power parity (PPP) or the real effective exchange rate (REER). A cheap currency has positive value; an expensive one has negative value. Value strategies go long undervalued currencies and short overvalued ones.
  - q: What is the momentum factor in currency markets?
    a: The momentum factor in currencies measures how much a currency has risen or fallen over the past one to twelve months relative to other currencies. Strong recent performance is positive momentum; weak recent performance is negative momentum.
  - q: Are value and momentum negatively correlated in currencies?
    a: Yes. Asness, Moskowitz and Pedersen (2013) showed that value and momentum returns are negatively correlated across all major asset classes, including currencies. When momentum is working well, value tends to lag, and vice versa. This makes combining them a natural diversification.
  - q: Which works better in currencies — value or momentum?
    a: Momentum tends to work better at short to medium horizons (one to twelve months), while value is a long-horizon signal. PPP-based value signals can remain wrong for years before mean-reverting. In practice, the two are best used together — momentum for timing, value to avoid chasing overextended trends.
  - q: What is purchasing power parity (PPP) in forex?
    a: PPP is the theory that exchange rates should adjust so that identical goods cost the same across countries. If a basket of goods costs $100 in the US but the equivalent costs ¥12,000 in Japan, PPP suggests the fair USD/JPY rate is 120. In practice, currencies deviate from PPP for years — but tend to revert over multi-year horizons.
---

# Value vs Momentum in Currencies: What the Research Shows

Two systematic return premia have dominated quantitative currency research for thirty years: **value** and **momentum**. One bets that overvalued currencies will eventually revert; the other bets that trends will persist. Remarkably, they both work — and they work better together than apart.

A deep understanding of value and momentum in FX is the foundation of every rigorous multi-factor currency model, and it is the conceptual backbone behind the [PIPTHEORY Macro Currency Strength Meter](/). This post explains what each factor is, what the research actually shows, and how they interact.

<div class="pt-tldr">
<div class="pt-tldr-h">Key takeaways</div>
<ul>
<li><strong>Value in FX</strong> measures how cheap or expensive a currency is relative to PPP or REER — and earns returns as currencies mean-revert toward fair value over <em>years</em>.</li>
<li><strong>Momentum in FX</strong> earns a trend premium at horizons of one to twelve months — currencies rising recently tend to keep rising.</li>
<li>Value and momentum are <strong>negatively correlated</strong>: when momentum is hot, value currencies are often being left behind — until the trend reverses.</li>
<li>Combining them improves risk-adjusted returns because the two signals hedge each other during periods of stress.</li>
<li>The landmark paper is <a href="https://onlinelibrary.wiley.com/doi/10.1111/jofi.12021" target="_blank" rel="noopener">Asness, Moskowitz and Pedersen (2013)</a>, "Value and Momentum Everywhere," published in the <em>Journal of Finance</em>.</li>
</ul>
</div>

## What is the value factor in currency markets?

The currency value factor is the bet that **overvalued currencies will eventually fall and undervalued currencies will eventually rise**. The challenge is measuring "overvalued."

The most widely used anchor is **purchasing power parity (PPP)**. PPP says that exchange rates should, in the long run, equalise the cost of an identical basket of goods across countries. If a basket of goods costs $100 in the US and the equivalent costs ¥14,000 in Japan, the PPP-implied exchange rate is 140 yen per dollar. If the actual rate is 155, the yen is undervalued by PPP — and a value strategy would go long yen.

A more sophisticated measure is the **Real Effective Exchange Rate (REER)**, published monthly by the <a href="https://data.bis.org/topics/EER" target="_blank" rel="noopener">Bank for International Settlements</a>. The REER adjusts a currency's trade-weighted exchange rate for inflation differences, giving a picture of whether a currency is cheap or expensive relative to its own trading history. A REER substantially below its long-run average signals a potentially undervalued currency; a REER substantially above suggests overvaluation.

<div class="pt-callout info">
<span class="pt-callout-h">PPP vs REER: what's the difference?</span>
PPP compares the currency to a fixed basket of goods (like the Economist's Big Mac Index). REER compares the currency to its own historical trade-weighted level adjusted for inflation. Both are value measures; REER is more commonly used in institutional research because it incorporates trade weights and domestic price levels.
</div>

## What does the research actually show?

### Value in currencies

Academic research generally confirms that PPP-based value signals predict returns at long horizons. A currency that is very cheap relative to PPP tends to appreciate — but the time horizon can be three to five years or more, which makes pure value strategies uncomfortable to hold through extended trend periods.

The difficulty is that currencies can remain fundamentally cheap for a long time. The Japanese yen, for instance, has appeared cheap on PPP metrics for many years, yet it continued depreciating through 2022–2024 as the Bank of Japan maintained ultra-loose policy while other central banks hiked. Fundamental cheapness is a necessary condition for eventual appreciation, not a sufficient one for near-term appreciation.

<div class="pt-fig">
<svg viewBox="0 0 320 120" role="img" aria-label="Illustrative chart showing value and momentum return cycles: momentum positive while value negative, then reversing">
  <line class="ax" x1="6" y1="60" x2="314" y2="60" stroke-width="1" stroke-dasharray="3 3"/>
  <!-- Momentum line: rises then falls -->
  <path class="pt-draw" d="M6,80 C60,40 100,20 150,30 C190,40 230,70 314,90" pathLength="1" fill="none" stroke="#2563EB" stroke-width="2"/>
  <!-- Value line: falls then rises (negative correlation) -->
  <path class="pt-draw" d="M6,40 C60,80 100,95 150,80 C190,60 230,38 314,25" pathLength="1" fill="none" stroke="#7C3AED" stroke-width="2"/>
  <text class="tx" x="314" y="88" text-anchor="end">Momentum</text>
  <text class="tx" x="314" y="23" text-anchor="end">Value</text>
  <text class="tx" x="160" y="10">Negative correlation across the cycle (illustrative)</text>
</svg>
<div class="pt-fig-cap">Illustrative — value and momentum returns tend to run in opposite phases of the cycle, making them natural portfolio complements.</div>
</div>

### Momentum in currencies

As documented by <a href="https://www.sciencedirect.com/science/article/abs/pii/S0304405X12001353" target="_blank" rel="noopener">Menkhoff, Sarno, Schmeling and Schrimpf (2012)</a> in the *Journal of Financial Economics*, currency momentum earns a spread of up to 10% per annum between the top and bottom quintiles of currencies ranked by past 1–12 month return. The effect is robust across 48 currencies from 1976 to 2010 and is not explained by standard risk factors.

Momentum works at shorter horizons where value is noisy. The mechanism is slow information absorption — new fundamental data is not immediately priced in, so prices trend as the market gradually reprices.

### "Value and Momentum Everywhere" — the landmark paper

The most influential paper combining both factors is <a href="https://onlinelibrary.wiley.com/doi/10.1111/jofi.12021" target="_blank" rel="noopener">Asness, Moskowitz and Pedersen (2013), "Value and Momentum Everywhere,"</a> published in the *Journal of Finance* (volume 68, pages 929–985). Their key findings for currency specifically, and across asset classes more broadly:

<ol class="pt-steps">
<li><span class="pt-step-h">Both premia are real and consistent</span> Value and momentum generate significant positive returns across stocks (US, UK, Europe, Japan), stock indexes, government bonds, commodities, and currencies. The premia are not data-mined artefacts.</li>
<li><span class="pt-step-h">They are negatively correlated</span> Value and momentum are negatively correlated with each other, within and across asset classes. When momentum is working (trends running), value positions are typically losing money — and vice versa.</li>
<li><span class="pt-step-h">Cross-asset co-movement</span> Value returns correlate across asset classes, and momentum returns correlate across asset classes — suggesting both are driven by common systematic factors (perhaps global risk appetite cycles).</li>
<li><span class="pt-step-h">The combination diversifies</span> Because value and momentum are negatively correlated, combining them in a portfolio improves the Sharpe ratio relative to either alone. The negative correlation acts as a natural hedge.</li>
</ol>

<div class="pt-stats">
<div class="pt-stat"><div class="pt-stat-num pos">8</div><div class="pt-stat-lbl">Asset classes with significant value + momentum premia (Asness et al. 2013)</div></div>
<div class="pt-stat"><div class="pt-stat-num neg">−0.49</div><div class="pt-stat-lbl">Average correlation between value and momentum returns across asset classes (illustrative of the negative relationship)</div></div>
<div class="pt-stat"><div class="pt-stat-num pos">1–12</div><div class="pt-stat-lbl">Months: the horizon where momentum dominates; value works at 3–5 years</div></div>
</div>

## The intuition behind the negative correlation

Why are value and momentum negatively correlated? The mechanism is straightforward:

<div class="pt-flow">
<div class="pt-flow-step"><span class="h">Momentum phase</span>A strong currency keeps rising. Momentum traders buy more. The currency moves further above PPP fair value — it becomes <em>more expensive</em> on a value measure.</div>
<div class="pt-flow-arrow">→</div>
<div class="pt-flow-step"><span class="h">Overextension</span>The currency is now both high-momentum AND deeply overvalued by PPP/REER. These two signals directly conflict.</div>
<div class="pt-flow-arrow">→</div>
<div class="pt-flow-step"><span class="h">Reversal</span>Eventually fundamentals reassert — the overvalued currency corrects. Momentum flips negative; value turns positive. The transition is often rapid.</div>
</div>

This tension is exactly the signal that separates sustainable trends from overextended ones. A currency with strong momentum that is also cheap on REER is fundamentally credible — the trend may have room to run. A currency with strong momentum that is also deeply expensive on REER is fragile — the trend is running on sentiment, not fundamentals.

## Value vs momentum in the 8 major currencies

| Currency | Momentum signal | Value (REER) signal | Combined read |
|---|---|---|---|
| Strong momentum, cheap REER | Positive | Positive | Double-positive — trend has fundamental support |
| Strong momentum, expensive REER | Positive | Negative | Fragile trend — watch for reversal |
| Weak momentum, cheap REER | Negative | Positive | Potential value opportunity — but needs catalyst |
| Weak momentum, expensive REER | Negative | Negative | Double-negative — fundamental and trend headwinds |

The PIPTHEORY macro score incorporates the interest rate and growth factors that drive value, while the price behaviour of FX pairs reflects momentum. When the macro score is rising AND the actual exchange rate is appreciating, the two are aligned — the clearest signal. When they diverge, that divergence is itself information.

For REER data, the <a href="https://data.bis.org/topics/EER" target="_blank" rel="noopener">BIS effective exchange rate indices</a> are the institutional standard, updated monthly with data for all major currencies.

## How to use value and momentum together practically

<ol class="pt-steps">
<li><span class="pt-step-h">Check the macro score first</span> A strong PIPTHEORY score for a currency reflects fundamental drivers — interest rates, growth, positioning. This is the closest available approximation to the value + carry signal for the 8 majors. Visit the <a href="/">live meter</a> to see today's ranking.</li>
<li><span class="pt-step-h">Check REER for overextension</span> If a currency's score is high and its REER is near its historical peak, value is warning of potential mean reversion. The trend may be late stage.</li>
<li><span class="pt-step-h">Check price momentum</span> Is the actual exchange rate trending in the same direction as the macro score? Agreement strengthens the view; divergence raises a question worth answering before committing.</li>
<li><span class="pt-step-h">Watch for value + momentum alignment</span> When a currency scores well fundamentally AND has positive price momentum AND is not extended on REER, all three signals agree. These are the clearest macro setups.</li>
</ol>

<div class="pt-callout warn">
<span class="pt-callout-h">Value traps are real</span>
A cheap currency can stay cheap for years. The yen has been PPP-cheap by many measures for more than a decade. Value is a gravity — it eventually pulls, but it doesn't set a timetable. Always require a catalyst (policy shift, sentiment change) before acting on value alone.
</div>

## Related reading

The two signals explored here connect directly to the other posts in this cluster. For the mechanics behind carry — which is closely related to the value factor in currencies — see [The Carry Trade Explained: How It Works and Why It Crashes](/research/carry-trade-explained). For a focused look at momentum alone, see [Currency Momentum: Why Trends Persist in FX](/research/currency-momentum-explained). For the positioning data that tells you when momentum is crowded and near exhaustion, see [How to Read the COT Report for Currency Positioning](/research/how-to-read-cot-report-forex).

For a broader introduction to how macro factors combine into a currency strength score, the [About & Methodology page](/about) explains the PIPTHEORY model in full. And for the currency-by-currency view, the individual pages for [USD](/currency/usd), [EUR](/currency/eur), [GBP](/currency/gbp), [JPY](/currency/jpy), [CHF](/currency/chf), [AUD](/currency/aud), [NZD](/currency/nzd) and [CAD](/currency/cad) show live macro scores updated every four hours.

<div class="pt-cta">
<span class="pt-cta-txt">See value and momentum alignment across the 8 majors in one view.</span>
<a href="/">Open the live meter →</a>
</div>

*Educational macro context only — not investment advice.*
