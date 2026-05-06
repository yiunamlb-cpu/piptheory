# Build Phases

Three phases over ~10-12 weeks. Each delivers something usable; commit to the next phase only after the current one earns its keep.

## Phase A — MVP Research Desk

**Target:** ~12 agents producing daily bias cards on the watchlist.
**Duration:** 2-3 weeks.
**Goal:** Prove that an agent stack adds enough value to justify continuing. If it doesn't, kill the project here cheaply.

### Build order

1. **Data plane** — wire up `fredapi`, `cot_reports`, `ecocal`, `fed-dot-plot-scraper`, OANDA price feeds
2. **PageIndex corpus** — ingest 5-10 highest-value source documents (Dalio's Big Debt Crises, recent BIS quarterly, latest FOMC minutes, recent Druckenmiller transcripts)
3. **Layer 1 specialists (4 only):** Fed-Watcher, Inflation Tracker, Positioning Analyst, Geopolitical Risk
4. **Layer 2 strategist:** combined FX + Cross-Asset Strategist (one agent, not four)
5. **Layer 3:** one Contrarian agent
6. **Layer 4:** simplified Bias Council — bull advocate + bear advocate + judge per instrument
7. **Layer 5:** PM agent (Druckenmiller-style)
8. **Manual journal** — markdown file, no automation
9. **No NT8 bridge yet** — agent outputs read by human, traded manually

### Phase A deliverables in this repo

- `playbook/regime_identification.md`
- `playbook/central_bank_reading.md`
- `playbook/positioning.md`
- `agents/layer1_specialists/*` (4 prompts)
- `agents/layer2_strategists/fx_cross_asset.md`
- `agents/layer3_redteam/contrarian.md`
- `agents/layer4_council/*` (3 prompts)
- `agents/layer5_pm/pm_druckenmiller.md`
- `src/data/`, `src/rag/`, `src/agents/`, `src/orchestration/`

### Run cadence

Once daily, manually triggered, ~6 AM London. Output: `bias_cards/YYYY-MM-DD.md` per instrument.

### Phase A success criteria

After 4-6 weeks of running, decide go/no-go on Phase B based on:

1. Did the bias cards correctly identify at least one regime shift you would have missed unaided?
2. Did the contrarian agent flag at least one consensus trap that turned out to matter?
3. Was at least one trade decision improved by an agent insight (entry, sizing, or skip)?

If yes to all three: proceed to Phase B. If not: simplify, re-prompt, or kill.

## Phase B — Specialist Expansion

**Target:** ~20 agents, deeper coverage where MVP felt thin.
**Duration:** +3-4 weeks.
**Trigger:** Phase A success criteria met AND specific gaps identified during MVP runs.

### Adds

- **Layer 1 expansion:** ECB-Watcher, BoJ-Watcher, PBOC-Watcher, Growth Tracker, Flow & Liquidity, Energy
- **Layer 2 expansion:** split FX/Rates/Equity/Commodity into separate strategists
- **Layer 3:** add Tail Risk Agent
- **Layer 4:** add Time-Horizon Council
- **Layer 5:** add Risk Manager with FTMO rule encoding
- **Letta integration** — cross-run memory across all agents
- **DMAD framework** for Layer 3 to enforce reasoning diversity
- **Prefect orchestration** — daily scheduled runs, retries, alerting
- **Langfuse observability** — replay agent traces when output is weird

### Phase B success criteria

- Does cross-run memory (Letta) measurably improve continuity vs. fresh-context runs?
- Does provider/persona diversity in Layer 3 produce meaningfully different reasoning vs. same-model agents?
- Is the system stable enough to trust unattended for a week?

## Phase C — Full Desk + Meta Learning

**Target:** ~30 agents + Layer 7 (calibration, weekly review, theme maintenance).
**Duration:** +3-4 weeks.
**Trigger:** 2+ months of journal data exists (minimum threshold for calibration to be meaningful).

### Adds

- **Layer 6:** NT8 bridge via `CSharpNinja-Python` connector + custom signal server
- **Layer 7:** calibration agent (`properscoring` Brier scores), weekly review agent, theme maintenance agent
- **Persona library expansion:** Soros (reflexivity), Marks (cycles), Tudor Jones (price action overlay)
- **Cost throttling** and budget caps per agent run via LiteLLM
- **Backup/disaster recovery** for memory and journal data

### Phase C success criteria

- Brier score over the previous quarter is genuinely calibrated (within 0.05 of optimal)
- Weekly review identifies at least one actionable behavioral pattern per month
- The system runs unattended for a month without manual intervention

## What's Deferred Past Phase C (Maybe Forever)

- **Engine backtesting** — replaying the full agent stack on historical data. Real, valuable, expensive. Most solo macro traders never do this and trade fine without it.
- **Auto-execution** — the agents *recommend*, the human *decides*. Removing the human is its own multi-month project with significant risk; the upside is marginal for a solo operator.
- **Multi-strategy diversification** — if trend-pullback proves out, considered later. Don't fragment focus during the build.
- **Equities or crypto extension** — different analytical toolkit; treat as separate project if ever pursued.

## Anti-goals

- Building all 30 agents on day one
- Treating the architecture as fixed — refactor freely as you learn what's actually load-bearing
- Adding LLM features (newer models, fancier RAG, more memory tiers) faster than you're using the existing ones
- Mistaking sophistication for edge — they correlate weakly
