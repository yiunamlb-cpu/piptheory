---
title: "Inflation, Real Yields and FX: Why Real Rates Rule"
slug: real-yields-and-currencies
date: 2026-06-25
updated: 2026-06-25
keyword: real yields and currencies
summary: "Real yields — nominal interest rates minus inflation — are the single most powerful driver of currency strength. This guide explains the real-rate mechanism, why it trumps nominal rates, and how to use it as macro context."
faq:
  - q: "What is the relationship between real yields and currencies?"
    a: "When a country's real yield rises — either because nominal rates increase or inflation falls — its currency tends to strengthen as global capital flows in seeking better inflation-adjusted returns. When real yields fall, the currency typically weakens."
  - q: "Why do real rates matter more than nominal rates for FX?"
    a: "Nominal rates show the headline return, but real rates show what investors actually earn after inflation erodes purchasing power. A 5% nominal yield with 6% inflation is a real loss; a 3% yield with 1% inflation is a real gain. Capital flows chase real returns, so real yields drive exchange rates more reliably than nominal rates alone."
  - q: "What happens to a currency when inflation rises unexpectedly?"
    a: "Unexpected inflation compresses real yields by eroding the value of fixed-rate returns. That typically weakens the currency unless the central bank quickly raises nominal rates by more than the inflation surprise — which is rare. The 2021-2022 US dollar paradox (inflation surge but eventually a strong dollar) resolved only once the Fed signalled aggressive hikes that lifted real yields into positive territory."
  - q: "How do TIPS yields relate to the US dollar?"
    a: "TIPS (Treasury Inflation-Protected Securities) yields are the market's direct read on US real rates. Research and market observation consistently show that when TIPS yields rise, the dollar tends to strengthen, and when TIPS yields fall — as in 2020-2021 during massive Fed QE — the dollar weakens. FRED publishes the 10-year TIPS yield series (DFII10) daily."
  - q: "What is the Fisher effect in foreign exchange?"
    a: "The Fisher effect says that in the long run, nominal interest rates adjust to reflect expected inflation, leaving real rates similar across countries. In practice, real rates diverge significantly in the short and medium term, and those divergences are what move exchange rates. The international Fisher effect predicts that currencies with higher nominal rates will depreciate to offset the rate advantage, but this holds only roughly and over long horizons."
---

# Inflation, Real Yields and FX: Why Real Rates Rule

**Real yields** — nominal interest rates minus inflation — are the single most powerful macro driver of currency strength over months to years. When a country's real yield rises relative to peers, global capital flows in for the better inflation-adjusted return, and its currency strengthens. When real yields fall, the currency weakens. Everything else equal, follow the real rate.

<div class="pt-tldr">
<div class="pt-tldr-h">Key takeaways</div>
<ul>
<li><strong>Real yield = nominal rate − inflation.</strong> Capital chases real returns, not headline ones.</li>
<li>Rising real yields attract foreign capital → currency strengthens. Falling real yields repel it → currency weakens.</li>
<li>TIPS yields (DFII10 on FRED) are the market's live read on US real rates and closely track USD strength.</li>
<li>The Fisher effect says nominal rates absorb expected inflation in the long run, but short-run divergences are large and exploitable.</li>
<li>Real-rate differentials between two countries explain a large share of bilateral exchange-rate moves over 6–24-month horizons.</li>
</ul>
</div>

## What is a real yield, and why does it dominate FX?

A **real yield** strips out what inflation eats away. If a government bond pays 4% nominal and inflation is running at 3%, the real yield is approximately 1%. An investor holding that bond earns 1% after prices have been accounted for. If inflation jumps to 5% while the nominal rate stays at 4%, the real yield turns negative — the bond loses purchasing power every year.

Because currency traders and institutional investors compare returns globally, they care about *real* returns. A 6% nominal yield in a country suffering 7% inflation is worse than a 2% yield in a country with 0.5% inflation. The capital flows follow the real rate — and exchange rates follow the capital.

<div class="pt-flow">
<div class="pt-flow-step"><span class="h">Driver</span><strong>Real yield rises</strong> (rates up or inflation falls)</div>
<div class="pt-flow-arrow">→</div>
<div class="pt-flow-step"><span class="h">Response</span><strong>Foreign capital flows in</strong> seeking better real returns</div>
<div class="pt-flow-arrow">→</div>
<div class="pt-flow-step"><span class="h">Outcome</span><strong>Currency strengthens</strong> as demand for it rises</div>
</div>

The reverse is equally important. When a central bank keeps nominal rates low while inflation surges, real yields collapse — sometimes deeply negative — and the currency comes under sustained selling pressure. This is precisely why the US dollar weakened sharply in 2020–2021 as the Federal Reserve held rates near zero while consumer prices accelerated.

## Nominal vs. real: why the distinction matters

A common beginner mistake is to equate "high interest rates" with "strong currency." Sometimes that holds, but it frequently fails — because it ignores the inflation side.

| Scenario | Nominal rate | Inflation | Real yield | Currency signal |
|---|---|---|---|---|
| A: Hawkish hike | 5.5% | 2.0% | +3.5% | Strongly bullish |
| B: Hike but hot CPI | 5.5% | 6.0% | −0.5% | Bearish despite high nominal rate |
| C: Low rate, low inflation | 1.5% | 0.2% | +1.3% | Modestly bullish (CHF/JPY dynamic) |
| D: Rate cut, deflation | 0.0% | −1.0% | +1.0% | Counter-intuitively supportive |

Scenario B is the trap: headline-focused traders buy the high-rate story; real-rate-aware traders notice the currency's purchasing power is being eroded faster than the yield compensates, and sell accordingly.

<div class="pt-callout warn">
<span class="pt-callout-h">Inflation surprises are the most dangerous</span>
A surprise CPI print that exceeds forecasts compresses real yields instantly, even before any central-bank response. These moments can move exchange rates sharply in the minutes after the data release. The move often overshoots and partly reverses once markets price in the policy response — so understanding the full chain (CPI → real yield → expected policy → terminal rate) is more valuable than reacting to the headline.
</div>

## TIPS yields: the market's live real-rate gauge for the USD

In the US, the Treasury market offers a direct read on real yields through **Treasury Inflation-Protected Securities (TIPS)**. Unlike nominal Treasuries, TIPS principal adjusts with CPI, so their yield is already a real yield — no arithmetic required. The <a href="https://fred.stlouisfed.org/series/DFII10" target="_blank" rel="noopener">10-year TIPS yield (DFII10)</a> published daily by the Federal Reserve Bank of St. Louis is one of the most closely watched signals in FX.

<figure class="pt-chart" data-chart='{"type":"line","x":["Jan 2021","Apr 2021","Jul 2021","Oct 2021","Jan 2022","Apr 2022","Jul 2022","Oct 2022","Jan 2023","Apr 2023","Jul 2023","Oct 2023"],"baseline":0,"annotations":[{"xi":4,"text":"Fed pivot — hike cycle starts"}],"series":[{"name":"USD broad index (indexed)","color":"#2563EB","data":[100,98,101,97,99,106,110,113,108,105,109,107]},{"name":"US 10-yr TIPS yield (%)","color":"#E11D48","data":[-1.0,-0.9,-1.1,-1.2,-0.5,0.3,0.8,1.7,1.5,1.2,1.9,2.1]}],"alt":"Illustrative USD index and 10-year TIPS real yield from 2021 to 2023: both rise sharply from early 2022 as the Fed begins hiking"}'>
<figcaption>Illustrative — indexed USD broad index and US 10-year TIPS real yield (%). When the Fed began hiking in early 2022, real yields rose from deeply negative to positive and the dollar surged in parallel. Real data: <a href="https://fred.stlouisfed.org/series/DFII10" target="_blank" rel="noopener">FRED DFII10 (TIPS yield)</a> &amp; <a href="https://fred.stlouisfed.org/series/DTWEXBGS" target="_blank" rel="noopener">FRED DTWEXBGS (broad dollar)</a>.</figcaption>
</figure>

During the 2020–2021 period of near-zero interest rates and expanding Fed balance sheet, 10-year TIPS yields fell to around −1.1%, a historic low. The dollar weakened materially. When the Fed then began its rate-hike cycle in March 2022, real yields surged toward positive territory and the <a href="https://fred.stlouisfed.org/series/DTWEXBGS" target="_blank" rel="noopener">broad dollar index</a> hit 20-year highs by late 2022, according to Federal Reserve data. The co-movement was stark — and it was the real yield, not the nominal rate alone, that explained the timing.

## Real-rate differentials drive bilateral exchange rates

It is not the absolute level of real yields that matters for a currency pair — it is the **differential** between the two countries. If the US real yield is +2% and the eurozone real yield is −0.5%, that +2.5 percentage-point advantage pulls capital toward the dollar and away from the euro.

<div class="pt-stats">
<div class="pt-stat"><div class="pt-stat-num pos">+2.5 pp</div><div class="pt-stat-lbl">Illustrative US–Eurozone real-yield differential → USD bullish vs EUR</div></div>
<div class="pt-stat"><div class="pt-stat-num neg">−1.8 pp</div><div class="pt-stat-lbl">Illustrative Japan–US real-yield differential → JPY bearish vs USD</div></div>
</div>

The bilateral differential is tracked across the major economies on the [PIPTHEORY Macro Currency Strength Meter](/). The "rates" pillar of the score incorporates the real-rate standing of each currency versus its peers, which is why currency pairs often trend for months in line with diverging central-bank cycles — the real-rate gap widens slowly as one central bank hikes and another holds.

The <a href="https://www.bis.org/publ/work919.htm" target="_blank" rel="noopener">Bank for International Settlements</a> and academic literature (including the influential Lustig–Roussanov–Verdelhan 2011 work on currency risk premia) document that real interest-rate differentials explain a substantial fraction of currency excess returns across countries. The relationship is not mechanical — markets are forward-looking — but it is the most robust single macro predictor over medium-term horizons.

## The Fisher effect and its limits

The **Fisher effect**, articulated by economist Irving Fisher, holds that nominal interest rates will, over time, fully reflect expected inflation: if markets expect 3% inflation, nominal rates should incorporate that 3%, leaving the real rate unchanged. In theory, if every country's real rate converges, there is no free lunch from high-nominal-rate currencies — and Covered Interest Parity (CIP) and the international Fisher effect both predict that high-nominal-rate currencies should depreciate by the rate differential.

<div class="pt-callout info">
<span class="pt-callout-h">International Fisher Effect in practice</span>
The international Fisher effect predicts that a currency with a 3% higher nominal rate will depreciate by roughly 3% against a lower-rate currency, leaving the real return equal. This holds approximately over very long horizons (10+ years) but breaks down dramatically at shorter horizons — which is why carry trades (borrowing cheap-rate currencies to buy high-rate ones) are profitable on average, as documented by <a href="https://www.nber.org/papers/w14473" target="_blank" rel="noopener">Brunnermeier, Nagel and Pedersen (2008)</a>. See also the full <a href="/research/carry-trade-explained">carry trade explainer</a>.
</div>

In practice, two forces mean real rates diverge significantly across countries and remain diverged for years:

1. **Sticky inflation:** Price levels adjust slowly, so a central bank can keep nominal rates high (or low) for extended periods while inflation is still catching up — keeping real rates elevated (or depressed) longer than theory suggests.
2. **Imperfect capital mobility:** In the short run, capital does not instantly arbitrage away real-rate differentials, especially across currencies with different risk profiles, transaction costs, or regulatory barriers.

These two frictions are precisely where the FX opportunity lies. The [interest rate differentials explainer](/research/interest-rate-differentials-forex) on this site covers the nominal side of the rate story in depth, and the [what makes a currency strong](/research/what-makes-a-currency-strong) post places real yields within the full five-factor framework.

## Real yields and the major currencies

The real-rate story plays out differently across the eight majors, partly because of structural inflation differences:

<div class="pt-bars">
<div class="pt-bar-row"><span class="pt-bar-lbl">USD</span><span class="pt-bar-track"><span class="pt-bar-fill pos" style="width:70%"></span></span><span class="pt-bar-val">Higher real yield → historically a positive carry currency</span></div>
<div class="pt-bar-row"><span class="pt-bar-lbl">EUR</span><span class="pt-bar-track"><span class="pt-bar-fill pos" style="width:42%"></span></span><span class="pt-bar-val">Real yields typically below USD; ECB historically slow to hike</span></div>
<div class="pt-bar-row"><span class="pt-bar-lbl">JPY</span><span class="pt-bar-track"><span class="pt-bar-fill neg" style="width:65%"></span></span><span class="pt-bar-val">Persistent near-zero nominal rates → real yield depends on whether Japan is in deflation or mild inflation</span></div>
<div class="pt-bar-row"><span class="pt-bar-lbl">CHF</span><span class="pt-bar-track"><span class="pt-bar-fill pos" style="width:30%"></span></span><span class="pt-bar-val">Low nominal rates, low inflation — real yield modest but stable (safe-haven premium dominates)</span></div>
<div class="pt-bar-row"><span class="pt-bar-lbl">GBP</span><span class="pt-bar-track"><span class="pt-bar-fill pos" style="width:55%"></span></span><span class="pt-bar-val">Volatile — UK inflation surges can rapidly compress real yields despite BoE hikes</span></div>
</div>

The labels above are indicative of structural tendencies, not current readings. For live real-rate comparisons across the [US dollar](/currency/usd), [euro](/currency/eur), [Japanese yen](/currency/jpy) and peers, the macro score on the [PIPTHEORY meter](/) updates the rates factor every four hours using the latest central-bank policy rates and CPI data.

## How real yields fit into a macro trading framework

Real yields are necessary but not sufficient. A high real yield attracts capital and supports the currency — but that support can be overwhelmed by:

- **Risk-off positioning:** In a flight to safety, the yen and Swiss franc often strengthen despite low or negative real yields, because safe-haven demand trumps carry considerations.
- **Already-priced cycles:** If everyone expects the Fed to hike aggressively, the dollar may peak before the hikes even happen — because markets are forward-looking.
- **Current-account deterioration:** A country running a large and widening current-account deficit may see its currency weaken despite high real yields if the deficit signals future financing risk.

<ol class="pt-steps">
<li><span class="pt-step-h">Check the real yield level</span> Is the country's real yield positive or negative? A persistently negative real yield (nominal rate below inflation) is a structural headwind for the currency.</li>
<li><span class="pt-step-h">Check the direction</span> Is the real yield rising or falling? The trend matters more than the level — a currency moving from −1% to 0% real yield is strengthening its fundamental case even if it is still in negative territory.</li>
<li><span class="pt-step-h">Check the differential</span> Compare the real yield to the currency's main trading partners. A widening positive differential means the macro tide is turning in the currency's favour.</li>
<li><span class="pt-step-h">Cross-check with the meter</span> The <a href="/">PIPTHEORY macro score</a> blends the real-rate signal with growth, positioning, risk mood and commodities — giving a multi-factor view that avoids over-relying on any single input.</li>
</ol>

Understanding real yields is foundational to reading why the [REER (real effective exchange rate)](/research/real-effective-exchange-rate-explained) and [central-bank policy](/research/how-central-banks-move-currencies) influence exchange rates the way they do — those posts extend the framework from the single-factor to the full macro picture.

<div class="pt-cta">
<span class="pt-cta-txt">See which currencies have the strongest real-rate backdrop right now.</span>
<a href="/">Open the live meter →</a>
</div>

*Educational macro context only — not investment advice.*
