---
title: "Currency Correlations in Forex: Which Pairs Move Together and Why"
slug: currency-correlations-forex
date: 2026-08-30
updated: 2026-08-30
keyword: forex currency correlation
summary: "Forex currency correlation measures how two pairs move together, from +1 (perfect alignment) to -1 (exact opposite). EUR/USD and USD/CHF are nearly perfect inverses; AUD and NZD move almost in lockstep. Understanding why — and when correlations break — can prevent invisible over-exposure."
faq:
  - q: "What is forex currency correlation?"
    a: "Forex currency correlation is a statistical measure of how similarly two currency pairs move, expressed from +1 (they move in perfect lockstep) through 0 (no relationship) to -1 (they move in exactly opposite directions). A high positive correlation means buying both pairs gives roughly double the same exposure."
  - q: "Why do EUR/USD and USD/CHF move in opposite directions?"
    a: "Both pairs share a USD leg. When the dollar strengthens, it pushes EUR/USD down (dollar in the denominator rises) and USD/CHF up (dollar in the numerator rises). The opposing direction of the USD in each pair creates a near-perfect inverse correlation, historically in the range of -0.85 to -1."
  - q: "Why do AUD/USD and NZD/USD move together?"
    a: "Australia and New Zealand have similar commodity-export economies, closely tied trading relationships (especially with China), and similar monetary policy cycles. Both are classified as risk currencies that gain in risk-on environments and fall in risk-off periods. Their correlation typically runs between +0.86 and +0.99."
  - q: "Are currency correlations stable?"
    a: "No. Correlations are regime-dependent and can break down sharply. A pair that was strongly correlated during a commodity boom may decouple if one country's central bank diverges in policy. Correlations observed over a 3-month window can look very different from those over a 1-year window."
  - q: "What is the practical risk of correlated trades?"
    a: "If a trader is long EUR/USD and long GBP/USD simultaneously, and both pairs have a high positive correlation, the portfolio has roughly twice the USD-short exposure of either position alone. Without accounting for this, position sizes can look controlled but the true risk is concentrated."
---

# Currency Correlations in Forex: Which Pairs Move Together and Why

**Forex currency correlation** measures the degree to which two currency pairs move together. On a scale from **+1** (they move in perfect lockstep) through **0** (no relationship) to **−1** (they move in exactly opposite directions), correlation tells you whether two positions in your portfolio are genuinely independent or secretly stacked on top of each other.

Understanding correlations is not an exotic pursuit — it is basic risk management. A trader who is long EUR/USD, long GBP/USD, and long AUD/USD simultaneously may believe they hold three separate trades, but if those pairs are all strongly correlated (they frequently are, especially in USD-trending environments), the actual exposure is effectively three times a single dollar short with some currency diversification at the margins.

<div class="pt-tldr">
<div class="pt-tldr-h">Key takeaways</div>
<ul>
<li>Correlation runs from +1 (same direction, same magnitude) to −1 (exactly opposite), with 0 = no relationship.</li>
<li><strong>EUR/USD vs USD/CHF</strong>: near-perfect inverse correlation (−0.85 to −1) because the shared USD leg runs in opposite directions.</li>
<li><strong>AUD/USD vs NZD/USD</strong>: near-perfect positive correlation (+0.86 to +0.99) — the commodity bloc twins.</li>
<li>Three root causes: a shared USD leg, risk-on/risk-off sentiment, and commodity-bloc membership.</li>
<li>Correlations are <strong>unstable and regime-dependent</strong>: they can break, reverse, or compress during policy divergences.</li>
<li>Stacking correlated trades without adjusting position size multiplies hidden risk.</li>
</ul>
</div>

## What Correlation Means in Forex: A Plain Reading

Correlation is a statistical number, but its practical interpretation is straightforward:

- **+0.9 to +1.0**: The two pairs almost always move in the same direction by similar amounts. Holding both is nearly identical to doubling the size of one.
- **+0.5 to +0.8**: The pairs tend to move together but not reliably. Partial diversification exists.
- **0**: No systematic relationship — one pair's move tells you nothing about the other.
- **−0.5 to −0.8**: The pairs tend to move in opposite directions. One can partially hedge the other.
- **−0.9 to −1.0**: Near-perfect inverse. A long in one is essentially a short in the other.

Correlations are calculated over a rolling window — 1 month, 3 months, 1 year — and the choice of window matters. Short-term correlations capture current regime dynamics; longer-term correlations reflect more structural relationships. Neither is "right" — they answer different questions.

## EUR/USD and USD/CHF: The Classic Inverse Pair

The most reliably negative correlation in major FX is between EUR/USD and USD/CHF, historically ranging from about **−0.85 to −1.00**. The reason is arithmetic rather than economic: the US dollar is in the denominator of EUR/USD and in the numerator of USD/CHF.

When the dollar strengthens against everything:
- EUR/USD **falls** (a stronger dollar lowers the ratio)
- USD/CHF **rises** (a stronger dollar raises the ratio)

Both moves reflect the same underlying event — dollar appreciation — but they appear in opposite directions on a chart. If you are long EUR/USD and long USD/CHF, you are — in dollar terms — partially flat, because one position profits from dollar weakness and the other profits from dollar strength.

<figure class="pt-chart" data-chart='{"type":"line","x":["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],"series":[{"name":"EUR/USD (rebased to 100)","color":"#0D9488","data":[100,101,98,96,94,91,90,87,84,86,89,91]},{"name":"USD/CHF (rebased to 100)","color":"#CA8A04","data":[100,99,103,105,106,110,112,116,119,115,113,111]}],"alt":"Illustrative EUR/USD and USD/CHF moving in near-perfect inverse directions during a dollar-strengthening episode"}'>
<figcaption>Illustrative — EUR/USD and USD/CHF moving inversely as the dollar strengthens. Both series rebased to 100 at start. Real data: <a href="https://fred.stlouisfed.org/" target="_blank" rel="noopener">FRED</a>.</figcaption>
</figure>

There is also an economic dimension: both the euro and the Swiss franc are European currencies that often attract or repel similar capital flows (European risk perception, ECB policy spillovers, eurozone crises). This amplifies the mathematical dollar effect. See the [dollar-gold correlation explainer](/research/dollar-gold-correlation) and [stocks and the dollar](/research/stocks-and-the-dollar) for related intermarket dynamics.

## AUD/USD and NZD/USD: The Commodity Bloc Twins

At the positive extreme sits AUD/USD vs NZD/USD, where correlations regularly run **+0.86 to +0.99** — almost indistinguishable for practical risk purposes. The reasons are structural:

**Similar economies.** Australia and New Zealand are both commodity-export economies in the Asia-Pacific region. Both export primary goods — iron ore, coal, and agricultural products from Australia; dairy, meat, and timber from New Zealand — whose prices are driven by the same global demand cycle, and especially by <a href="https://www.bis.org/statistics/eer.htm" target="_blank" rel="noopener">Chinese industrial activity</a>.

**Tightly linked trading relationships.** China is the largest export destination for both countries. When Chinese growth accelerates, both the Australian and New Zealand dollars tend to strengthen simultaneously. When Chinese growth disappoints, both tend to weaken. See the [AUD as a China proxy](/research/aud-china-proxy) explainer for the detailed mechanism.

**Monetary policy alignment.** The Reserve Bank of Australia (RBA) and the Reserve Bank of New Zealand (RBNZ) face similar inflation and growth cycles, leading to broadly similar rate paths. Their divergences are real but usually modest relative to the G3.

**Risk currency classification.** Both are considered "risk-on" currencies — they tend to gain when global risk appetite is high and investors reach for yield. This creates a common factor that moves them together regardless of commodity prices. For more on this, see the [risk-on risk-off currencies](/research/risk-on-risk-off-currencies) explainer.

<div class="pt-stats">
<div class="pt-stat"><div class="pt-stat-num pos">+0.86–0.99</div><div class="pt-stat-lbl">AUD/USD vs NZD/USD correlation range</div></div>
<div class="pt-stat"><div class="pt-stat-num neg">−0.85–−1.00</div><div class="pt-stat-lbl">EUR/USD vs USD/CHF correlation range</div></div>
<div class="pt-stat"><div class="pt-stat-num pos">+0.75–0.90</div><div class="pt-stat-lbl">EUR/USD vs GBP/USD (typical range)</div></div>
</div>

## The Three Root Causes of FX Correlation

Most currency correlations trace back to one of three mechanisms:

<ol class="pt-steps">
<li><span class="pt-step-h">Shared currency leg</span> Any two pairs containing the same currency will tend to correlate — in the same direction if the shared currency is in the same position (both as base or both as quote), or inversely if it is in opposite positions. EUR/USD and GBP/USD are both "dollar pairs" — they share a dollar-short exposure, producing positive correlation. EUR/USD and USD/CHF are dollar pairs with the dollar on opposite sides, producing negative correlation.</li>
<li><span class="pt-step-h">Risk-on / risk-off sentiment</span> A broad risk-off event — a recession scare, geopolitical shock, financial stress — tends to strengthen safe-haven currencies (JPY, CHF, USD in crises) and weaken risk currencies (AUD, NZD, CAD, emerging markets) simultaneously. In these episodes, pairs that share a "risk" or "safe-haven" character move together regardless of their underlying fundamentals.</li>
<li><span class="pt-step-h">Commodity-bloc membership</span> AUD, CAD, and NZD are all positively correlated with commodity prices. Oil drives CAD via the Canada-energy link (see [oil and the Canadian dollar](/research/oil-and-canadian-dollar)); iron ore and agricultural commodities drive AUD and NZD. When commodity prices rally broadly — as in 2021–2022 — the whole bloc moves together.</li>
</ol>

<div class="pt-callout info">
<span class="pt-callout-h">The commodity bloc in a risk-off shock</span>
In a sharp risk-off episode, AUD, NZD, and CAD can all fall simultaneously even though they are driven by different commodities in normal times. Risk sentiment can override commodity-specific factors, temporarily making the bloc act as one. This is when traders holding long AUD/USD and long NZD/USD as "separate" ideas discover they are really one position.
</div>

## Why Correlations Are Unstable: Regime Dependency

The biggest practical danger with correlation analysis is treating historical averages as permanent features. Correlations are **regime-dependent**: they shift when the underlying drivers change.

Consider the AUD/USD and NZD/USD pairing. During periods of smooth global growth with stable Chinese demand, the two move almost identically. But if the RBNZ surprises with an aggressive rate hike while the RBA stays on hold, the monetary policy divergence can temporarily decouple the pair — NZD strengthens independently of AUD on the rate differential story.

<figure class="pt-chart" data-chart='{"type":"line","x":["Q1","Q2","Q3","Q4","Q1","Q2","Q3","Q4"],"series":[{"name":"AUD/NZD correlation with AUD/USD (3-month rolling)","color":"#DB2777","data":[0.94,0.96,0.91,0.87,0.92,0.78,0.63,0.71]},{"name":"Stable-regime average","color":"#CA8A04","data":[0.90,0.90,0.90,0.90,0.90,0.90,0.90,0.90]}],"alt":"Illustrative rolling correlation between NZD/USD and AUD/USD showing a dip during policy divergence","annotations":[{"xi":5,"text":"RBNZ diverges"}]}'>
<figcaption>Illustrative — rolling 3-month correlation between NZD/USD and AUD/USD, showing a dip when monetary policy diverges. Real correlations vary. <a href="https://www.bis.org/statistics/eer.htm" target="_blank" rel="noopener">BIS EER data</a>.</figcaption>
</figure>

Similarly, EUR/USD and USD/CHF are nearly perfectly inversely correlated in normal times — but in a eurozone-specific crisis (like the 2010–2012 sovereign debt crisis), the euro can weaken sharply while the franc is simultaneously strengthening as a safe haven. Both moved against the dollar in the same direction temporarily, breaking the usual inverse relationship.

**Key implication**: historical correlations are a starting point, not a guarantee. Short-window rolling correlations (1–3 months) are more reliable for current regime assessment than long-run averages.

## The Risk of Stacking Correlated Trades

The most dangerous practical consequence of ignoring correlation is **invisible concentration**. Traders who believe they are diversified because they hold multiple currency pairs may actually be amplifying a single macro bet.

<div class="pt-callout warn">
<span class="pt-callout-h">The hidden USD short</span>
In a broadly USD-weakening environment, a trader might be long EUR/USD, long GBP/USD, long AUD/USD, and long NZD/USD — four "separate" positions. In a USD-trending market, these four can correlate at 0.7–0.9, meaning the portfolio effectively holds 3–4x a single dollar-short bet. If the dollar reverses, all four positions suffer simultaneously.
</div>

A simple framework for managing correlation risk:

- **Group trades by their primary dollar exposure.** All USD-as-quote pairs (EUR/USD, GBP/USD, AUD/USD, NZD/USD) cluster around a common USD factor in trending USD environments.
- **Separate by other fundamentals.** Within the USD-quote cluster, pair-specific drivers (rate differentials, commodity prices, risk) still differentiate performance — but only if the USD trend is neutral.
- **Size down when stacking.** If you hold two pairs with a 0.85 correlation, reduce the combined position to roughly 1.0x–1.2x the risk of a single position, not 2x.

| Pair group | Shared exposure | Correlation direction |
|---|---|---|
| EUR/USD, GBP/USD, AUD/USD, NZD/USD | USD-short | Positive in USD-trend environments |
| EUR/USD, USD/CHF | USD (opposite legs) | Negative (near -1) |
| AUD/USD, NZD/USD | Commodity + China + risk-on | Strongly positive |
| USD/CAD, AUD/USD | Oil/commodity exposure (partial) | Moderate positive |
| USD/JPY, EUR/USD | Risk sentiment (partial) | Moderate negative in risk-off |

For the full picture of how sentiment drives these groupings, see [risk-on risk-off currencies](/research/risk-on-risk-off-currencies). For the commodity connection, [oil and the Canadian dollar](/research/oil-and-canadian-dollar) covers the CAD-energy link, and [the Aussie as a China proxy](/research/aud-china-proxy) covers AUD-iron ore dynamics.

## Putting Correlation Into a Macro Framework

A currency strength meter naturally surfaces correlations in action: when the macro scores for EUR and GBP are both rising while USD is falling, EUR/USD and GBP/USD will tend to move together because the shared driver (dollar weakness) is dominant. Checking whether two pairs share a dominant driver is more useful than mechanically measuring a correlation coefficient — because it tells you whether the correlation is likely to hold or break.

The [PIPTHEORY live meter](/) scores each currency independently on its own fundamental factors. If EUR and GBP scores are both elevated for the same reason (say, dollar weakness), the meter highlights the shared driver. If they diverge — GBP strengthens on a Bank of England surprise while EUR stays flat — the meter surfaces that difference too.

<div class="pt-callout key">
<span class="pt-callout-h">The key insight</span>
Correlation is not a property of a currency pair — it is a property of the current macro regime. Track the drivers (USD trend, risk sentiment, commodity prices), and the correlations follow naturally. When the drivers shift, expect the correlations to shift with them.
</div>

<div class="pt-cta">
<span class="pt-cta-txt">See macro scores for all eight major currencies — spot the common drivers before they show up in correlations.</span>
<a href="/">Open the live meter →</a>
</div>

*Educational macro context only — not investment advice.*
