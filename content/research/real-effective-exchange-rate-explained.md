---
title: "Real Effective Exchange Rate (REER): Is a Currency Cheap or Expensive?"
slug: real-effective-exchange-rate-explained
date: 2026-06-15
updated: 2026-06-15
keyword: real effective exchange rate
summary: "The real effective exchange rate (REER) is the standard measure of whether a currency is fundamentally cheap or expensive relative to history. This guide explains what REER is, how the BIS calculates it, and why it matters for macro traders."
faq:
  - q: "What is the real effective exchange rate (REER)?"
    a: "The REER is a trade-weighted average of a currency's value against a basket of partner currencies, adjusted for relative inflation differentials. When a country's REER is above 100 (its base-period average), its exports have become more expensive and less competitive; below 100, they are cheaper and more competitive. The Bank for International Settlements (BIS) publishes REER indices for 60-plus economies."
  - q: "What is the difference between NEER and REER?"
    a: "The NEER (Nominal Effective Exchange Rate) is a trade-weighted average of bilateral exchange rates with no inflation adjustment. The REER adjusts the NEER for relative consumer price levels between countries, making it the better measure of true competitiveness and purchasing-power-adjusted valuation."
  - q: "Where can I find REER data?"
    a: "The BIS publishes monthly REER and NEER indices for 60-plus economies at data.bis.org/topics/EER. FRED (the St. Louis Fed data platform) re-hosts the BIS series and adds US-specific trade-weighted dollar indices. The IMF's International Financial Statistics also contains REER series."
  - q: "Does a high REER mean a currency will depreciate?"
    a: "A high REER signals the currency is expensive in purchasing-power terms relative to its history, which tends to act as a drag on growth (via weaker export competitiveness) and can precede depreciation — but the timing is highly uncertain. Currencies can stay overvalued for years, especially if supported by capital inflows, high real yields, or safe-haven demand."
  - q: "How does REER relate to the PIPTHEORY macro score?"
    a: "REER is a valuation input in the PIPTHEORY framework. An extreme REER (very high or very low versus historical norms) can signal mean-reversion pressure, complementing shorter-run signals like interest-rate differentials and positioning. A currency that is both fundamentally cheap on REER and picking up positive rate momentum has a compounding tailwind."
---

# Real Effective Exchange Rate (REER): Is a Currency Cheap or Expensive?

The **real effective exchange rate (REER)** is the institutional benchmark for answering one question: *is this currency fundamentally cheap or expensive right now relative to its own history?* Published monthly by the <a href="https://data.bis.org/topics/EER" target="_blank" rel="noopener">Bank for International Settlements (BIS)</a> for more than 60 economies, the REER adjusts a trade-weighted basket of bilateral exchange rates for differences in consumer prices across countries — giving a single number that reflects true purchasing-power competitiveness.

<div class="pt-tldr">
<div class="pt-tldr-h">Key takeaways</div>
<ul>
<li>REER = trade-weighted basket of bilateral rates, adjusted for relative inflation between trading partners.</li>
<li>REER > 100 (its base year) means the currency has become more expensive; exports lose competitiveness.</li>
<li>REER < 100 means the currency is cheaper in real terms; exports gain competitiveness.</li>
<li>The BIS publishes REER monthly for 60+ economies at <a href="https://data.bis.org/topics/EER" target="_blank" rel="noopener">data.bis.org</a>; FRED re-hosts the series.</li>
<li>Extreme REER readings signal mean-reversion pressure, but timing is unreliable — currencies can stay misaligned for years.</li>
</ul>
</div>

## What is the real effective exchange rate?

The REER builds up in three steps. First, pick the relevant trading partners (the BIS uses up to 26 or 61 economies depending on the dataset). Second, compute the **NEER (Nominal Effective Exchange Rate)** — a geometric average of bilateral rates, weighted by each partner's share of trade. Third, adjust the NEER for **relative price levels**: if domestic inflation has been running faster than a trading partner's, the nominal exchange rate overstates competitiveness, so a CPI-ratio adjustment brings it back to a real comparison.

<ol class="pt-steps">
<li><span class="pt-step-h">Pick trading partners</span> The BIS weights each bilateral rate by the partner country's share of the home country's merchandise trade (exports plus imports), updated periodically.</li>
<li><span class="pt-step-h">Build the NEER</span> Take the geometric weighted average of bilateral nominal exchange rates versus the chosen basket. This is already useful but ignores inflation differences.</li>
<li><span class="pt-step-h">Adjust for relative prices</span> Divide by the ratio of domestic CPI to a trade-weighted average of partners' CPIs. The result is the REER — a real purchasing-power comparison.</li>
<li><span class="pt-step-h">Index to a base year</span> The series is set to 100 in a reference period (typically a recent average year). A reading above 100 means the currency has appreciated in real terms since the base; below 100 means real depreciation.</li>
</ol>

<div class="pt-callout info">
<span class="pt-callout-h">BIS methodology note</span>
The BIS publishes two REER series: a "narrow" one covering 26 economies (the most traded currencies) and a "broad" one covering 61. For the eight major currencies (USD, EUR, GBP, JPY, CHF, CAD, AUD, NZD), both series are available. The BIS updates the data monthly, typically with a six-week lag. You can download the full dataset at <a href="https://data.bis.org/topics/EER" target="_blank" rel="noopener">data.bis.org/topics/EER</a>.
</div>

## NEER vs. REER: why the real adjustment changes everything

The NEER is the raw, unadjusted trade-weighted rate. The REER is the one that actually matters for competitiveness and valuation — because a nominal depreciation can be fully offset by faster domestic inflation, leaving real trade competitiveness unchanged.

| | NEER | REER |
|---|---|---|
| **Definition** | Trade-weighted average of nominal bilateral rates | NEER adjusted for relative consumer-price levels |
| **Inflation-adjusted?** | No | Yes |
| **Best answers** | "Has the exchange rate moved?" | "Is the currency cheap or expensive in real terms?" |
| **Used by** | Central banks for FX monitoring | Economists, IMF, BIS for competitiveness assessment |
| **Limitation** | Ignores domestic vs. foreign inflation | Lags — CPI data is monthly, not daily |

For macro traders, the REER is what matters for medium-to-long-term positioning. A country running 5% inflation while its trading partners average 2% will see its REER appreciate by about 3 percentage points per year even if its nominal exchange rate is flat — gradually eroding export competitiveness and creating a valuation headwind.

## How to read a REER chart: overvalued and undervalued signals

<figure class="pt-chart" data-chart='{"type":"line","x":["2014","2015","2016","2017","2018","2019","2020","2021","2022","2023","2024","2025"],"baseline":100,"annotations":[{"xi":0,"text":"Overvalued zone"},{"xi":8,"text":"Undervalued zone"}],"series":[{"name":"REER (base = 100)","color":"#0D9488","data":[112,118,115,108,104,99,97,100,93,88,91,95]}],"alt":"Illustrative REER index for a currency: starts overvalued above 100, falls through base and becomes undervalued below 100, then begins mean-reversion"}'>
<figcaption>Illustrative REER index — above 100 (base year) the currency is expensive in real terms and exports lose competitiveness; below 100 it is cheap and competitive. Both extremes tend to mean-revert, but timing is unpredictable. Real data: <a href="https://data.bis.org/topics/EER" target="_blank" rel="noopener">BIS effective exchange rates</a>.</figcaption>
</figure>

When a REER moves significantly above its long-run average, three things tend to follow — though the timing is unpredictable:

1. **Export weakness.** Domestic goods and services become expensive for foreign buyers, reducing export volumes.
2. **Import surge.** Foreign goods look cheap to domestic consumers, widening the current account deficit.
3. **Growth headwind.** If trade is a meaningful share of GDP, the drag on net exports slows growth, eventually reducing rate-hike expectations and weakening the currency.

The reverse holds for an undervalued REER. The <a href="https://www.imf.org/en/Publications/WP/Issues/2016/12/31/Revisiting-the-Empirical-Evidence-on-Firm-Investment-and-Exchange-Rates-25021" target="_blank" rel="noopener">IMF's research on REER misalignment</a> and competitiveness effects is extensive; the organisation publishes annual REER-based "external balance assessments" for its major members.

<div class="pt-callout warn">
<span class="pt-callout-h">REER overvaluation is not a trading signal</span>
The US dollar REER was elevated above its long-run average for much of 2015–2016, 2022–2023, and various stretches before that. Each time, the fundamental argument for USD weakness was sound — but the dollar stayed expensive for longer than many expected, because high real yields, safe-haven demand and capital inflows kept funding the overvaluation. Use REER as a context-layer, not a trigger.
</div>

## REER in action: four major-currency examples

### USD — the world's "perennially overvalued" reserve currency

The US dollar has traded above its long-run REER average for extended periods, partly because reserve-currency demand from central banks and institutions creates structural buying that is not driven by competitiveness. The <a href="https://fred.stlouisfed.org/series/RBUSBIS" target="_blank" rel="noopener">BIS broad REER for the USD (RBUSBIS)</a>, available on FRED, shows the dollar hit multi-decade REER highs around 2022. This overvaluation is a core reason why some economists — including those at the Brookings Institution — argue the dollar's reserve-currency role effectively taxes US manufacturers and exporters. See also the [reserve currencies explainer](/research/reserve-currencies-explained) for why this structural demand persists.

### JPY — from chronically weak to extreme undervaluation

The Japanese yen spent much of 2022–2024 at historically cheap REER levels, reflecting near-zero Bank of Japan policy rates against rising global rates. Academic and institutional economists flagged the yen's REER as deeply undervalued — at points the cheapest since the early 1970s on some measures. That undervaluation eventually contributed to import-cost inflation in Japan, which in turn pushed the Bank of Japan toward policy normalisation. You can track the [Japanese yen macro score](/currency/jpy) on the PIPTHEORY meter.

### EUR — structurally close to fair value, cyclically volatile

The euro REER has historically tracked close to its base-period average, reflecting the eurozone's large and balanced external trade position. It dips when growth diverges sharply between the eurozone and the US, and recovers when ECB policy tightens. The [euro currency page](/currency/eur) on this site shows the current macro-factor breakdown.

### GBP — post-Brexit REER reset

Sterling's REER fell sharply after the June 2016 Brexit referendum and remained below pre-referendum levels for years. That structural cheapening improved UK export competitiveness but raised import prices, feeding inflation — a classic REER trade-off. The [pound currency page](/currency/gbp) tracks GBP's current macro standing.

## Where REER data lives: primary sources

<div class="pt-stats">
<div class="pt-stat"><div class="pt-stat-num pos">60+</div><div class="pt-stat-lbl">Economies covered by BIS REER (broad series)</div></div>
<div class="pt-stat"><div class="pt-stat-num pos">1964</div><div class="pt-stat-lbl">Earliest year in BIS historical REER dataset</div></div>
<div class="pt-stat"><div class="pt-stat-num pos">Monthly</div><div class="pt-stat-lbl">BIS publication frequency (~6-week lag)</div></div>
</div>

The authoritative sources for REER data are:

- **BIS** — <a href="https://data.bis.org/topics/EER" target="_blank" rel="noopener">data.bis.org/topics/EER</a> — the primary source; download narrow and broad REER for all 60+ economies.
- **FRED (St. Louis Fed)** — <a href="https://fred.stlouisfed.org/release?rid=319" target="_blank" rel="noopener">fred.stlouisfed.org (release 319)</a> — re-hosts the BIS series with easy charting tools and additional US-specific trade-weighted dollar indices.
- **IMF IFS** — the <a href="https://data.imf.org/" target="_blank" rel="noopener">IMF's International Financial Statistics</a> includes REER series and the IMF's own "equilibrium REER" estimates from its external balance assessments.

## REER and the PIPTHEORY macro score

The REER enters the PIPTHEORY framework as a valuation signal. A currency trading far above its historical REER average has a valuation headwind — even if its real yields are attractive, the macro tailwind is partly already in the price. Conversely, a currency with a deeply depressed REER has potential mean-reversion tailwinds if other factors (rate momentum, improving current account) start to align.

The interaction between REER valuation and [real yields](/research/real-yields-and-currencies) is particularly telling: a currency that is cheap on REER *and* seeing rising real yields is in a compounding positive scenario — it is both undervalued and attracting new capital. That combination shows up clearly in the rates and growth pillars of the [live macro score](/).

| | **REER cheap** (below long-run avg) | **REER expensive** (above long-run avg) |
|---|---|---|
| **Real yields rising** | Strongest tailwind — undervalued and attracting capital | Overvalued but bid — yield pull may sustain it short-term |
| **Real yields falling** | Value trap risk — cheap but no catalyst yet | Structural headwind — overvalued and losing yield appeal |

*Illustrative — the strongest multi-factor setups sit in the top-left quadrant: cheap REER with rising real yields.*

Understanding REER also puts [carry trade](/research/carry-trade-explained) dynamics in sharper relief: a carry trade that sells a low-yielding, REER-overvalued currency against a high-yielding, REER-cheap one has valuation *and* yield carry working in the same direction — a much more robust position than yield differential alone.

<div class="pt-cta">
<span class="pt-cta-txt">See where each major currency sits on the macro scale — rates, growth, positioning and more.</span>
<a href="/">Open the live meter →</a>
</div>

*Educational macro context only — not investment advice.*
