# Architecture

A solo discretionary macro research desk built as a multi-layer agent stack. Modeled on a small 2018-era discretionary macro fund (5-10 humans wearing multiple specialist hats); scales the *process* without the headcount.

**Core principle:** OSS handles plumbing, we build the edge. The edge lives in three places — the playbook (curated frameworks), the personas (prompt engineering), and the calibration (feedback loop) — none of which any framework provides for free.

## The Seven Layers

### Layer 0 — Data Plane

The firm's databases. Structured, point-in-time, refreshed on schedule.

- FRED time series — `fredapi`
- COT positioning — `cot_reports`
- Economic calendar — `ecocal`
- Fed dot plot — `fed-dot-plot-scraper`
- Central bank statement embeddings — `central-bank-nlp` (fastText vectors trained on FOMC)
- Geopolitical event aggregation — `Crucix` (27 OSS feeds, 15-min refresh)
- GDELT events — `gdeltPyR`
- Sanctions monitoring — OpenSanctions API
- Document corpus (Fed minutes, BIS, IMF, hedge fund letters) — RAG via `PageIndex`
- Price data — OANDA (FX), IB (institutional), yfinance (futures/equities prototyping)

### Layer 1 — Specialist Analysts

Narrow-domain agents, each owns one input stream. ~12 agents at full build.

Central bank watch: Fed-Watcher, ECB-Watcher, BoJ-Watcher, BoE-Watcher, PBOC-Watcher.
Macro state: Inflation Tracker, Growth Tracker, Flow & Liquidity, Positioning Analyst.
Other: Geopolitical Risk, Energy/Commodity, Cross-Asset Confirmer.

Each specialist gets: persona prompt, tool allowlist, model tier (cheap vs. frontier), output schema, persistent memory block (Letta).

### Layer 2 — Asset-Class Strategists

Synthesize Layer 1 outputs into per-asset views. 4 agents.

- FX Strategist
- Rates Strategist
- Equity Strategist
- Commodity Strategist

### Layer 3 — Red Team (Mandatory)

Adversarial layer. Without this, the bias engine becomes a momentum-confirmation machine.

- Contrarian Agent — argues against the consensus from Layer 2
- Tail Risk Agent — what would break each thesis catastrophically
- Positioning Reversal — at what point does crowd unwind become THE trade

Uses `DMAD` (Diverse Multi-Agent Debate, ICLR 2025) to enforce reasoning-style diversity, plus `LiteLLM` to mix providers across red-team agents so they don't share priors.

### Layer 4 — Bias Council

Per-instrument debate. The decision-making layer.

- Bull Advocate · Bear Advocate (per instrument)
- Time-Horizon Council (tactical / swing / positional)
- Judge Agent — frontier model, scores debate, sets calibrated conviction

### Layer 5 — Portfolio Manager

CIO seat. Synthesizes biased instruments into a ranked, correlation-aware view.

- PM Agent — frontier model, Druckenmiller-style reasoning (reference: `ai-hedge-fund` PM agent)
- Risk Manager — encodes FTMO rules (daily loss limit, max DD, news-window restrictions, consistency)

### Layer 6 — Execution

Discretionary, not automated by default. Human pulls the trigger.

- Setup Scanner — given biased instruments, finds trend-pullback structure
- Trade Journal — logs every decision with full agent reasoning trail
- MT5 bridge — `MetaTrader5` Python package for data + ZeroMQ EA for signal delivery (FTMO-compatible)

### Layer 7 — Meta / Learning

The part that's almost always missing and where long-term edge compounds.

- Calibration Agent — `properscoring` Brier scores over journal data; flags drift
- Weekly Review — pattern-finds in wins/losses
- Theme Maintenance — keeps `THEMES.md` fresh as data shifts

## Cross-Cutting Infrastructure

| Concern | Tool |
|---|---|
| Orchestration substrate | `TradingAgents` (forked, customized for macro) on `LangGraph` |
| Daily scheduler | `Prefect` (cron-style, retries, alerts) |
| Model gateway & cost tracking | **OpenRouter** (one API for Claude / DeepSeek / GPT / Llama; server-side routing; per-call cost in response) |
| Observability | `Langfuse` (trace replay, prompt versioning, eval harness) |
| Cross-run memory | `Letta` (persistent agent state across days/weeks) |
| RAG | `PageIndex` (reasoning-based, no vector DB) |

`LiteLLM` is **optional** with OpenRouter — only needed if we later want local-fallback to specific providers, or use models OpenRouter doesn't proxy.

## Tiered Model Strategy

Token volume runs through cheap models; decision-critical synthesis runs through frontier.

| Workload | Tier |
|---|---|
| Data summarization, news ingestion, COT parsing | Cheap (DeepSeek class) |
| Per-instrument bias card drafting | Cheap |
| Bull/bear debate generation | Cheap |
| **Theme synthesis & conviction calibration** | **Frontier** |
| **Judge agent (Layer 4)** | **Frontier** |
| **PM synthesis (Layer 5)** | **Frontier** |
| Weekly journal review | Cheap |

Estimated cost: ~$15-30/month at MVP (Phase A), ~$50-100/month at full desk (Phase C). OpenRouter returns per-call cost in API responses for budget tracking; agent runner enforces caps.

## Honest Tradeoffs

1. **Correlated agents.** All agents share base LLM training. Diversity is illusory unless explicitly enforced via different personas + providers + tool subsets.
2. **Token cost scales linearly with layers.** Full desk is 3-4x MVP cost.
3. **Time to first signal.** A 30-agent run is 20-40 min end-to-end. Cron starts before market open.
4. **Maintenance burden.** 30 prompts is real ongoing work to tune and debug.
5. **Diminishing returns.** MVP → 12 agents is huge. 12 → 30 is meaningful but smaller. Beyond 30 is mostly negative for a solo operator.
6. **Memory drift risk.** Letta-style persistent memory has a habit of subtly drifting (agents start citing things that aren't quite true). Phase B introduces it cautiously; treat as advisory until calibration data validates it.

## What This Architecture Does NOT Provide

- **The MACRO_PLAYBOOK** — bespoke, lives in `playbook/`. Highest-value asset in the project.
- **Persona prompts** (Druckenmiller, Soros, Dalio, Marks) — bespoke, lives in `agents/`. ~30% of edge.
- **Calibrated conviction over time** — emerges from Layer 7 once journal data accumulates (2+ months minimum).
- **Edge in any single trade** — the engine enforces discipline; it doesn't manufacture alpha. Edge accrues from compounding correctly-sized, correctly-biased trades over hundreds of decisions.
