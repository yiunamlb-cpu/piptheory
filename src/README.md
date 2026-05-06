# src/

Python source.

Planned modules:

- `data/` — wrappers around fredapi, cot_reports, ecocal, Crucix, central-bank scrapers, OANDA/IB price data
- `rag/` — PageIndex setup, document corpus management (Fed minutes, BIS, hedge fund letters)
- `memory/` — Letta integration for cross-run agent state
- `orchestration/` — Prefect flows for daily bias-engine runs; LangGraph in-flow agent wiring
- `agents/` — Python-side agent runner (loads prompts from `../agents/`, dispatches via LiteLLM)
- `calibration/` — properscoring wrappers, Brier-score tracking over journal data
- `bridge/` — NT8 ↔ Python signal server (socket-based)
- `journal/` — trade ingestion, post-trade analysis
