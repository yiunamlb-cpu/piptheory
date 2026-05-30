# PIPTHEORY — Blog Author Brief (read before writing any post)

This is the build spec for every research/blog post. Follow it exactly so all 50 posts are
consistent, on-brand, SEO + GEO optimized, factually correct, and richly visual.

**Read first:** `docs/seo-strategy.md` (strategy, keyword map, rules) and the exemplar
`content/research/2026-05-30-what-is-a-currency-strength-meter.md` (copy its structure/quality).
Component styles live in `app/static/blog.css`.

---

## Output

- One markdown file per post at `content/research/<slug>.md` (slug = kebab-case of the title).
- **YAML front matter** (exact keys):

```
---
title: "Exact Post Title"
slug: post-slug-here
date: 2099-12-31            # placeholder — the editor assigns the real drip date later
updated: 2099-12-31
keyword: primary target keyword
summary: 1-2 sentence meta description (~150 chars) containing the keyword + a hook.
faq:
  - q: "A natural question someone searches?"
    a: "A direct, self-contained 1-3 sentence answer."
  - q: "Second question?"
    a: "Answer."
  - q: "Third question?"
    a: "Answer."
---
```

- **CRITICAL — quote your YAML strings.** ALWAYS wrap every `faq` `q:`/`a:` value, and the
  `summary`, in **double quotes**. An unquoted value containing a colon-space (e.g. `the CME: EUR`,
  `note: this`, a ratio like `2: 1`) silently breaks the whole front matter. When in doubt, quote it.
- Use `date: 2099-12-31` for ALL posts (keeps them hidden until scheduled — do not invent dates).
- The FAQ goes in **front matter only** (the template renders it + emits FAQ structured data). 3–5 Q&As.

## Specs (non-negotiable)

- **1,500–2,000 words** of real, substantive prose (graphics don't count toward the word goal).
- **SEO:** primary keyword in title, H1 (`# Title`), first ~100 words, and ≥2 `##` headings;
  long-tail variants in subheads. Don't keyword-stuff.
- **GEO (rank in AI answers):** open the post AND each major `##` with a concise, self-contained,
  quotable answer (1–3 sentences) before elaborating. Where natural, phrase an H2 as the literal
  question ("What is the carry trade?") with the answer directly under it. Use specific, sourced
  facts. Each section must stand alone (no "as we saw above").
- **Never a wall of text:** insert a visual / table / callout / list every ~2–3 paragraphs.
- Close with a **`<div class="pt-cta">`** linking the live meter.

## Fact-checking (mandatory)

- Verify every date, figure, name, event and quote via web search BEFORE writing; cite the source
  with an inline link. No fabricated stats, quotes, or attributions. If approximate, say "about".
- Case studies & trader bios are high-risk — double-check (e.g., GBP Sep 1992, CHF 15 Jan 2015,
  Plaza Accord Sep 1985, yen carry unwind Aug 2024, Asian crisis 1997, Brexit 23 Jun 2016).

## Hyperlinks

- **Link to** (descriptive anchor text): academic papers, central banks (Fed/ECB/BoJ/BoE/etc.),
  primary data (BIS, CFTC, IMF, FRED), Reuters/Wikipedia, named experts' public work, and — for
  funding/business topics — prop firms and brokers. External links: `<a href="..." target="_blank" rel="noopener">`.
  Use `rel="nofollow noopener"` for promotional prop-firm/broker links.
- **NEVER link to** currency-strength-meter competitors: BabyPips/MarketMilk, LogikFx, Myfxbook,
  OANDA's strength tool, FXSSI, Mataf, LiveCharts, FX Blue, or exact-match meter domains. Discuss
  concepts without linking the rival tool.
- **Internal links (use 3–6 per post):** the live meter `/`; `/about`; relevant currency pages
  `/currency/usd` `/eur` `/gbp` `/jpy` `/chf` `/cad` `/aud` `/nzd`; relevant pair pages
  `/pair/eurusd` etc. (28 canonical: base order EUR,GBP,AUD,NZD,USD,CAD,CHF,JPY); and 2–3 sibling
  posts by their slug `/research/<slug>` from the pipeline.

---

## Visual component kit (copy-paste; classes are defined in blog.css)

RULES FOR GRAPHICS:
- Wrap every graphic in a block-level `<div class="pt-...">` starting at **column 0**, with a
  **blank line before and after** (so the markdown renderer passes it through verbatim).
- Inline SVG: keep camelCase attributes EXACTLY (`viewBox`, `pathLength`) — never lowercase them.
  Always include `viewBox` + `role="img"` + `aria-label`; never set fixed pixel width/height
  (the CSS makes them responsive). Use the palette below.
- Any illustrative numbers must be labelled "illustrative" in the caption. Real data must be sourced.
- Each post should use **4–7 different** graphics (mix types; don't repeat the same one).

Palette (theme tokens via classes, or these hexes for SVG strokes):
USD `#2563EB` · EUR `#0D9488` · GBP `#7C3AED` · JPY `#E11D48` · CHF `#CA8A04` · CAD `#16A34A`
· AUD `#DB2777` · NZD `#0891B2`. Use `var(--bull)` green / `var(--bear)` red for up/down.

**Key takeaways / TL;DR** (put near the top):
```
<div class="pt-tldr">
<div class="pt-tldr-h">Key takeaways</div>
<ul>
<li>Point one.</li>
<li>Point two.</li>
</ul>
</div>
```

**Callout** (variants: `info`, `key`, `warn`):
```
<div class="pt-callout warn">
<span class="pt-callout-h">Watch out</span>
The caution text goes here.
</div>
```

**Pull quote** (only with a REAL, sourced quote — else use a callout):
```
<div class="pt-quote">
The quotable sentence.
<cite>Attribution</cite>
</div>
```

**Stat cards:**
```
<div class="pt-stats">
<div class="pt-stat"><div class="pt-stat-num pos">+58</div><div class="pt-stat-lbl">What it measures</div></div>
<div class="pt-stat"><div class="pt-stat-num neg">−12%</div><div class="pt-stat-lbl">Label</div></div>
</div>
```

**Numbered steps:**
```
<ol class="pt-steps">
<li><span class="pt-step-h">Step title</span> Step description.</li>
<li><span class="pt-step-h">Step title</span> Step description.</li>
</ol>
```

**Cause → effect flow** (use `pt-flow-arrow` text like `→` or `+`):
```
<div class="pt-flow">
<div class="pt-flow-step"><span class="h">Cause</span>Rates rise.</div>
<div class="pt-flow-arrow">→</div>
<div class="pt-flow-step"><span class="h">Effect</span>Capital flows in.</div>
</div>
```

**Timeline** (for case studies):
```
<div class="pt-timeline">
<div class="pt-tl"><div class="pt-tl-date">16 Sep 1992</div><div class="pt-tl-h">Headline event</div>One-line detail.</div>
<div class="pt-tl"><div class="pt-tl-date">Next date</div><div class="pt-tl-h">Headline</div>Detail.</div>
</div>
```

**Data charts — use the `pt-chart` component. DO NOT hand-draw chart SVGs.** For any line/area/
bar chart, write a `<figure>` with a `data-chart` JSON spec; `blog.js` renders a clean,
axis-labelled, gridded, legend'd, animated chart with proper margins (no label/line overlap).
Illustrative data is fine — label it in the caption. Keep the JSON on ONE line.
```
<figure class="pt-chart" data-chart='{"type":"line","x":["Jan","Feb","Mar","Apr","May","Jun"],"series":[{"name":"USD","color":"#2563EB","data":[100,101,102.5,104,105,107]},{"name":"JPY","color":"#E11D48","data":[100,99,97,95,94,92]}],"suffix":"","alt":"short description for screen readers"}'>
<figcaption>Illustrative — short caption. Real data: <a href="https://fred.stlouisfed.org/..." target="_blank" rel="noopener">source</a>.</figcaption>
</figure>
```
- `type`: `"line"`, `"area"`, `"bar"` (vertical) or `"hbar"` (horizontal). `x`: x-axis labels.
  `series`: `[{name,color,data:[...]}]` (colors = palette hexes). Optional: `"suffix":"%"`,
  `"baseline":0` (force axis through zero), `"annotations":[{"xi":3,"text":"Event"}]` (dashed marker),
  `"height":320`.
- If two series have very different scales (an index ~100 vs a price ~2000), **index both to 100**
  at the start so they share one axis. Escape apostrophes inside labels.

**Raw inline `<svg>` is ONLY for genuine schematic diagrams** (e.g. a labelled cycle), and even
then prefer the CSS components (`pt-flow`, `pt-timeline`, `pt-stats`). **NEVER** hand-draw squiggly
"line charts" with floating `<text>` labels — they overlap, clip, and look amateur. Use `pt-chart`.

**Animated CSS bar chart** (set `width:%`; `pos`=green, `neg`=red; bars grow on load):
```
<div class="pt-bars">
<div class="pt-bar-row"><span class="pt-bar-lbl">USD</span><span class="pt-bar-track"><span class="pt-bar-fill pos" style="width:72%"></span></span><span class="pt-bar-val">+58</span></div>
<div class="pt-bar-row"><span class="pt-bar-lbl">JPY</span><span class="pt-bar-track"><span class="pt-bar-fill neg" style="width:40%"></span></span><span class="pt-bar-val">−30</span></div>
</div>
```

**Comparison table** — plain markdown (do NOT wrap in a div; it scrolls on mobile automatically):
```
| | Column A | Column B |
|---|---|---|
| Row | value | value |
```

**Closing CTA** (always include, linking the meter):
```
<div class="pt-cta">
<span class="pt-cta-txt">One-line hook tied to the article.</span>
<a href="/">Open the live meter →</a>
</div>
```

End the article with the line: `*Educational macro context only — not investment advice.*`

---

## Pre-submit checklist
- [ ] 1,500–2,000 words, primary keyword placed correctly, answer-first sections
- [ ] 4–7 varied graphics, each wrapped in a col-0 `<div>` with blank lines; SVG camelCase intact
- [ ] 3–5 FAQ in front matter; summary has keyword + hook; date `2099-12-31`
- [ ] 3–6 internal links (meter / about / currency / pair / sibling posts)
- [ ] Authoritative outbound links only — ZERO competitor links
- [ ] Every fact verified + sourced; no fabricated quotes/stats
- [ ] Ends with CTA + the disclaimer line
