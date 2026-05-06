# Central Bank Reading

How to parse central bank communication into actionable intelligence. This is the highest-signal data source in macro, and the one most often misread by retail. The Fed/ECB/BoJ/BoE/PBOC don't surprise markets randomly — they telegraph through language, and the language has structure.

This document is the canonical reference for the Fed-Watcher, ECB-Watcher, BoJ-Watcher, BoE-Watcher, and PBOC-Watcher agents.

## Why This Is The Master Variable

For FX, rates, and (increasingly) equities, central bank policy paths drive cross-asset flows more than any other input. Specifically:

- **Rate differentials** drive FX. A 25bp hike priced in vs. priced out is the difference between a 200-pip rally and a 200-pip dump.
- **Forward guidance** prices the curve. The shape of OIS forward rates is a direct readout of what the market thinks the central bank will do.
- **Language drift** is the leading indicator of policy shifts. By the time a hike or cut happens, it's usually been telegraphed for 1-3 meetings.

The job of the Watcher agents is **not** to predict what the central bank should do. It's to **track what the central bank is signaling and what's priced**, then identify the gap.

## The Hierarchy of Communication

Each source has different information density and different reaction lag. Read them in this order of priority:

| Source | Frequency | Information density | When it moves markets |
|---|---|---|---|
| **Policy statement** | Per meeting (8/yr Fed) | Highest per word | Immediately on release |
| **Press conference** | Per meeting (Fed, ECB) | High but unstructured | First 30 min of presser |
| **Minutes** | 3 weeks after meeting | Medium — context, dissents, debate | On release if they shift narrative |
| **Speeches by voting members** | Continuous | Variable — depends on speaker | If the speaker is a swing voter |
| **Speeches by non-voters** | Continuous | Low | Mostly noise |
| **Dot plot / projections** | Quarterly (Fed) | Highest single artifact | Major repricing event |
| **Q&A in testimony** | 2x/year (Powell to Congress) | Medium — political theater filter | When chair makes new commitment |

**Practical rule:** Statement and dot plot are events. Everything else is *atmosphere* that helps interpret the events.

## Parsing a FOMC Statement

The Fed statement has a consistent structure. Each paragraph signals a specific input. Comparing the new statement to the previous one — paragraph by paragraph, sentence by sentence — is the core analytical activity.

### Standard FOMC statement structure

1. **Opening paragraph** — current economic assessment (growth, employment, inflation)
2. **Risk balance** — risks to outlook (typically a single sentence)
3. **Decision** — what they did (held, hiked, cut) and dissents
4. **Forward guidance** — what they plan / data dependence language
5. **Balance sheet** — QT/QE specifics
6. **Vote** — who voted yes/no, dissents named

### What to track meeting-over-meeting

| What changed | Signal |
|---|---|
| "Inflation remains somewhat elevated" → "Inflation is elevated" | Hawkish drift (current case) |
| "Inflation has eased substantially" → "Inflation continues to ease" | Dovish drift |
| "Risks to outlook are roughly balanced" → "Risks to inflation outlook have intensified" | Hawkish risk shift |
| Adding "patience" | Dovish — slowing pace of moves |
| Removing "patience" | Hawkish — readying for action |
| "Data-dependent" → "Will need to see further evidence" | Slight dovish lean (raises bar for action) |
| "Will need to see further evidence" → "Data-dependent" | Slight hawkish lean (lowers bar) |
| Number of dissents going from 1 → 4 | Major signal — committee is fracturing |

**Apply this rule:** A statement that is 90% identical to the previous one but adds *one new word* in a key sentence is communicating that change deliberately. The Fed does not casually rewrite paragraphs.

## The Dot Plot (Quarterly)

The Summary of Economic Projections is the single most-information-dense Fed artifact. Released March/June/September/December.

### What to extract

- **Median dot for end-of-year** — the headline number
- **Distribution of dots** — tight cluster vs. wide spread tells you committee consensus
- **Movement of median vs. last release** — the directional signal
- **Movement of dots in 2-year forward and longer-run** — terminal rate signal
- **Long-run neutral rate** — Fed's view of where rates settle

### What it doesn't tell you

- Who put which dot (anonymous)
- How conditional each dot is (extreme dots may be conditional on tail-risk scenarios)
- The path between now and end-of-year (just endpoints)

### How to use it

Compare market pricing (Fed funds futures, OIS) to the median dot. The gap is the trade. If the dot says 3.50% end-of-year and the market is pricing 3.00%, market is more dovish than Fed — typical setup that resolves either by Fed becoming dovish (rare without growth slowdown) or by market repricing higher (more common).

## Language Drift Analysis

The single highest-value daily activity for a macro watcher: comparing today's central bank communication to last meeting's, line by line, looking for change.

### Methodology

1. **Pull current statement and previous statement** as plain text
2. **Diff them** at the sentence level (not word level — too noisy)
3. **For each changed sentence**, classify:
   - Pure stylistic change (no signal)
   - Same meaning different words (no signal)
   - Genuine shift in meaning (signal)
4. **For genuine shifts**, score on hawkish/dovish axis:
   - Strong hawkish: −2 (clear acceleration, removed dovish hedge)
   - Mild hawkish: −1 (subtle harder language, removed easing language)
   - Neutral / stylistic: 0
   - Mild dovish: +1
   - Strong dovish: +2
5. **Sum the scores** — net direction of the meeting

### Why score and not just summarize

Scoring forces explicit calibration. "The statement was more hawkish" is a useless agent output. "Net −3 on the language drift score" can be tracked over time, correlated with subsequent policy moves, calibrated.

The Calibration Agent (Layer 7) checks whether language drift scores correctly predicted subsequent policy. If a +2 dovish drift was followed by a hike, that's calibration data — refine the scoring rubric.

## Per-Central-Bank Specifics

Each central bank has its own communication style and idiosyncrasies. Watchers must internalize these.

### Federal Reserve (Fed)

- **Most transparent** of major CBs. Statements, minutes, dots, speeches all standard.
- **Chair's press conference** is high-signal — Powell's tone often more dovish/hawkish than statement.
- **Watch the sequence:** speech → statement → presser → minutes. Inconsistency between any two is a meaningful tell.
- **Dissents matter.** 4+ dissents (current case) = committee deeply split, future moves uncertain.
- **Calendar:** 8 meetings/year, dots in March/June/Sept/Dec.

### European Central Bank (ECB)

- **Less transparent than Fed.** No dot plot equivalent until recently. Press conferences run by Lagarde are key.
- **Watch the Q&A more than the statement.** Lagarde drops new information in answers.
- **National central bank governors** speak frequently and can have outsized influence (Lane is dovish reference, Schnabel hawkish, Kazimir hawkish).
- **The "Three Criteria"** (inflation outlook, underlying inflation, transmission) framework — watch how ECB discusses each.
- **Calendar:** 8 meetings/year, no dot plot, but staff projections in March/June/Sept/Dec.

### Bank of Japan (BoJ)

- **Most opaque** of major CBs. Statement is short and ambiguous; key signals are in the *Outlook Report* (quarterly).
- **Yield Curve Control** (YCC) tweaks are the actionable events — band widening signals normalization.
- **Watch Ueda's tone** — historically academic and cautious, deviations are signals.
- **JPY intervention** is a separate channel — Ministry of Finance, not BoJ. Track MoF officials (Vice Minister of Finance for International Affairs) for verbal intervention.
- **Calendar:** 8 meetings/year, Outlook Report quarterly.

### Bank of England (BoE)

- **Most academic** in tone. Inflation Reports are dense, useful.
- **Vote split is critical** — MPC publishes individual votes, not just majority. 5-4 vs. 7-2 is meaningful difference for next meeting.
- **Bailey's tone** can be hawkish in writing, dovish in tone — watch the pressers.
- **Calendar:** 8 meetings/year, Inflation Report quarterly.

### People's Bank of China (PBOC)

- **Least transparent** of the major CBs. Communication is indirect — through state media (Caixin, Xinhua, People's Daily) and official commentary.
- **Look at the operational tools:** RRR cuts, MLF rates, PBOC OMOs, daily fix on USD/CNY. These are how PBOC actually communicates intent.
- **The Politburo statements** (quarterly economic readouts) are higher-signal than PBOC pressers themselves.
- **No fixed calendar** for PBOC — moves can come anytime. RRR cuts often pre-holiday or pre-Politburo.

### Reserve Bank of Australia (RBA)

- **Policy statement** is short and structured. Quarterly Statement on Monetary Policy is the dense version.
- **Watch the housing sector references** — RBA is uniquely housing-sensitive.
- **Calendar:** 11 meetings/year (more frequent than other majors), SoMP quarterly.

## Pricing The Path (OIS / Fed Funds Futures)

What the central bank is signaling is half the story. What the market is pricing is the other half.

### Key reads

- **Fed funds futures** for next meeting → probability of hike/hold/cut
- **SOFR/OIS curves** for 6m, 12m, 24m forward → policy path expectations
- **5y5y inflation breakevens** → long-run inflation expectations (Fed cares about these)
- **Real yields (10y TIPS)** → real-rate stance the Fed is enforcing

### The trade

The actionable insight is almost always the *gap* between central bank signaling and market pricing.

- CB hawkish + market priced dovish = **short bonds, long currency** opportunity
- CB dovish + market priced hawkish = **long bonds, short currency** opportunity
- CB and market aligned = **wait for divergence**

The Fed-Watcher's job ends with delivering this gap, not with predicting which side wins.

## Common Interpretation Errors

1. **Reading politely written = dovish.** Central bankers write in measured language always. "Some firmness" is not dovish — context determines whether it's hawkish or dovish.
2. **Single-speaker amplification.** A single Fed speaker (especially a non-voter) does not move policy. Don't overweight one-off speeches unless from the Chair, Vice-Chair, or NY Fed President.
3. **Linear extrapolation.** "They've cut 3 times, they'll cut again" assumes path continues. Central banks reverse direction; cycles end.
4. **Ignoring data dependence.** A "data-dependent" stance means the next meeting depends on what data prints between now and then. Watcher agents must condition forward views on upcoming data, not just current statement.
5. **Confusing tone with substance.** A press conference can sound hawkish while the statement is dovish (or vice versa). Sometimes this is a deliberate communication strategy — chair speaking to one audience while statement targets another.
6. **Geographic blind spot.** Most retail watches Fed, ignores ECB/BoJ/PBOC. The differential is what drives FX. Watcher agents must read all relevant CBs, not just the home one.

## Output Schema (Agent-Facing)

Every central bank watcher agent must produce structured output in this format:

```
CENTRAL_BANK: [Fed | ECB | BoJ | BoE | PBOC | RBA]
DATE: YYYY-MM-DD (most recent communication parsed)

LANGUAGE_DRIFT_SCORE: [-2 to +2] (negative = hawkish, positive = dovish)
KEY_LANGUAGE_CHANGES:
  - [removed phrase]: [interpretation]
  - [added phrase]: [interpretation]

POLICY_STANCE_NOW: [hawkish hold | hawkish hike | neutral hold | dovish hold | dovish cut | etc.]
NEXT_MEETING_BIAS: [hike | hold | cut] with [high|medium|low] conviction

MARKET_PRICING (OIS / futures):
  Next meeting: [P(hike), P(hold), P(cut)]
  6m forward: [implied terminal rate]
  12m forward: [implied terminal rate]

GAP (CB signal vs. market pricing):
  [CB more hawkish than market | aligned | CB more dovish than market]
  Trade implication: [direction for currency, direction for bonds]

DISSENTS: [number, names if known, hawkish/dovish split]
NEXT_CATALYST: [date and event that could shift this read]
INVALIDATION: [what data print or speech would force re-read]

CONVICTION: [high | medium | low]
```

This output is consumed by the FX Strategist (Layer 2) and the Bias Council (Layer 4).

## Calibration

The Calibration Agent (Layer 7) tracks whether language drift scores correctly predicted subsequent policy moves, and whether the "gap" trades worked. After 6+ months of data, refine the scoring rubric and per-bank specifics based on what actually played out.
