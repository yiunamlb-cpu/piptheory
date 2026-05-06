# Tooling Survey

Open-source projects evaluated for the stack, organized by role. Compiled from two Explore-agent surveys (broad + specialist deep-dive, May 2026).

**Calibration note:** Star counts and last-commit dates from agent reports were not always reliable — verify each before depending on it. The *projects identified* are real and worth taking seriously regardless of exact popularity numbers.

## Selection principles

1. **OSS for plumbing, custom for edge.** Use libraries for solved problems (data ingestion, orchestration, observability); build the actual reasoning agents and playbook ourselves.
2. **Maintained > popular.** A 200-star repo with active commits beats a 5k-star repo abandoned 18 months ago.
3. **License-aware.** Apache 2.0 / MIT preferred; AGPL acceptable for personal use; avoid commercial-only.
4. **Pin versions aggressively.** Wrap each dependency behind a thin local interface so swaps are local changes.

## Data Ingestion

| Project | Role | License | Notes |
|---|---|---|---|
| `fredapi` | FRED time series wrapper | MIT | Standard. Handles vintage/revision data correctly. |
| `cot_reports` | CFTC Commitment of Traders parser | Apache 2.0 | Covers all CFTC formats (legacy, disaggregated, TFF). |
| `ecocal` | Economic calendar scraper | MIT | Light but functional. NFP, CPI, central bank meetings with estimates/actuals. |
| `fed-dot-plot-scraper` | FOMC dot plot extraction from Fed PDFs | MIT | Reliable; watch for PDF format changes (~2x/year). |
| `central-bank-nlp` | fastText vectors trained on FOMC statements | MIT | Use for hawkish/dovish scoring without LLM cost. |

## Geopolitical & News Intelligence

| Project | Role | License | Notes |
|---|---|---|---|
| `Crucix` | Aggregates 27 OSS feeds (GDELT, ACLED, OpenSky, NASA FIRMS, sanctions, ReliefWeb) every 15 min | MIT | Biggest pleasant surprise. Runs locally, outputs deltas. |
| `gdeltPyR` | Python wrapper for GDELT 1.0/2.0 | MIT | For backfill/research, not real-time. |
| OpenSanctions API | Sanctions/PEP/entities data | Free for non-commercial | 332 sources integrated. |

## Document Corpus / RAG

| Project | Role | License | Notes |
|---|---|---|---|
| `PageIndex` | Reasoning-based RAG, no vector DB | MIT | 98.7% on FinanceBench. Use for Fed minutes, BIS, hedge fund letters. Newer/smaller community — fallback would be FAISS+embeddings. |

## Multi-Agent Orchestration

| Project | Role | License | Notes |
|---|---|---|---|
| `TradingAgents` | Multi-agent debate framework on LangGraph | Apache 2.0 | The orchestration substrate. Equity-focused out-of-box; we customize agents to macro. Multi-LLM provider support is essential for tiered model strategy. |
| `ai-hedge-fund` | Multi-agent fund sim with Druckenmiller PM agent | MIT | **Reference, not runtime dependency.** We steal prompt patterns and adapt into our PM agent inside TradingAgents. |
| `DMAD` (Diverse Multi-Agent Debate) | Forces distinct reasoning perspectives across agents | MIT | ICLR 2025 paper. Implementation maturity unclear — may need to reimplement following paper. Use in Layer 3 to enforce reasoning diversity. |
| `LangGraph` | State-machine orchestration for multi-step agent flows | MIT | What TradingAgents is built on. Genuinely well-suited to debate flows. |
| `LiteLLM` | Provider abstraction across 100+ LLMs, with cost tracking | MIT | Essential for tiered model strategy. Built-in budget caps. |

## Memory

| Project | Role | License | Notes |
|---|---|---|---|
| `Letta` (formerly MemGPT) | Stateful agent memory across sessions | MIT (self-hosted) / commercial (cloud) | Closes the cross-run amnesia gap. Self-host for solo use. **Watch for memory drift** — treat as advisory until calibrated. |
| `Zep` | Production-grade memory server with summarization, entity extraction | AGPL + commercial | Higher LongMemEval scores than Mem0. AGPL requires care if monetized. |
| `Mem0` | Plug-and-play memory extraction/retrieval | MIT | Simplest integration. Less powerful for multi-day tracking; use for short-term. |

## Calibration & Forecast Evaluation

| Project | Role | License | Notes |
|---|---|---|---|
| `properscoring` | Brier, CRPS, log-loss with reliability/resolution decomposition | Apache 2.0 | Reference library. Use for Layer 7 calibration audits. |
| `scoringrules` | Faster compute alternative for high-volume eval | MIT | Less mature; use for prototyping. |

## Workflow Orchestration (Daily Agent Runs)

| Project | Role | License | Notes |
|---|---|---|---|
| `Prefect` | Python-first scheduler, dynamic flows, retries, alerts | Apache 2.0 | Use for the morning bias-engine cron. Self-hosted is production-ready. |
| `LangGraph` | In-flow agent orchestration (already listed above) | MIT | Pair *within* Prefect tasks, not as top-level scheduler. |
| Apache Airflow | Battle-tested but enterprise-scale | Apache 2.0 | Overkill for solo. Migrate only if scaling beyond solo use. |

## Sentiment / Narrative Tracking

| Project | Role | License | Notes |
|---|---|---|---|
| `FinBERT` | Pre-trained financial sentiment (BERT) | Apache 2.0 | Works on earnings transcripts, financial press. Weak signal alone — use as input to multi-signal aggregator. |
| `FinGPT` | Open-source financial LLM, RAG-augmented | MIT | More powerful than FinBERT, higher compute. Use for weekly narrative summaries. |

## Observability

| Project | Role | License | Notes |
|---|---|---|---|
| `Langfuse` | LLM observability, trace replay, prompt versioning, evals | Apache 2.0 (self-hosted) | Without observability, debugging 30 agents is impossible. Self-host to avoid SaaS costs. |

## Backtesting

| Project | Role | License | Notes |
|---|---|---|---|
| `backtesting.py` | Vectorized backtesting, intuitive API | AGPL-3.0 | For validating trend-pullback logic. AGPL: review if monetized. |
| `finmarketpy` | Macro-focused backtesting, FX-aware | Apache 2.0 | Built by macro practitioner. Steeper learning curve. |
| `NautilusTrader` | Rust-native event-driven, deterministic | LGPL-3.0 | Overkill unless we go fully systematic. |
| `vectorbt` | High-performance parameter sweeps | Apache 2.0 (Pro is paid) | For research, not live execution. |

## Execution Bridge (NinjaTrader 8)

| Project | Role | License | Notes |
|---|---|---|---|
| `CSharpNinja-Python-NinjaTrader8` | Drag-and-drop EA + socket bridge | Active | Saves writing socket plumbing. **Verify works in current NT8 version before depending.** |
| `ninja-socket` | Lower-level WebSocket example for NT8 | Active | If we want to roll our own. |

## Data / Brokers

| Project | Role | License | Notes |
|---|---|---|---|
| `oandapyV20` | OANDA REST API wrapper | Official | For FX live data. |
| `ib_insync` | Interactive Brokers Python, async | MIT | Production-grade. If/when IB account is opened. |
| `yfinance` | Yahoo Finance | MIT | Prototyping only. Flaky for intraday FX; fine for futures/equities. |

## Critical Gaps (Things OSS Does Not Solve)

These are NOT failures of the survey — they're failures of the OSS ecosystem to address them. We build these ourselves.

1. **Persona libraries** (Druckenmiller/Soros/Dalio/Marks reasoning styles as deployable prompts). No library does this. ~30% of edge.
2. **The MACRO_PLAYBOOK itself.** Reading + distillation of primary sources into structured frameworks. Bespoke.
3. **Central bank statement diff tool** (FOMC vs. last meeting language change). `central-bank-nlp` gives vectors; the diff layer is custom.
4. **Conviction calibration over time** wired into agents' priors. `properscoring` provides math; integration is custom.
5. **Beyond-COT positioning data** (dealer gamma, FX intervention indicators, FRA-OIS, term premium decomposition). Confirmed no good OSS.
6. **Engine-level backtesting** (replaying the full agent stack on historical data). Real research project; defer past Phase C.
7. **NT8 trade journal feedback loop.** Pure glue code, ~300 LOC.
8. **FTMO/prop-specific risk rules** in the Risk Manager agent. Small custom prompt, mandatory.
9. **Cost throttling enforcement** beyond LiteLLM budgets. Few hours of work.

## Things to Avoid

- Repos with <50 stars and >12 months no commits unless extremely high quality
- "AI trading bot" repos with high stars but no real code (hype, not substance)
- SaaS wrappers requiring paid API keys (defeats OSS purpose)
- Projects claiming 100% accuracy on live trading (scam flag)
- Crypto-only frameworks (different vol/liquidity regime than what we trade)
- Building our own backtester (six-month yak-shave that ends with a worse vectorbt)
