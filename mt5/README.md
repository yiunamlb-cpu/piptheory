# mt5/

MetaTrader 5 components — the execution side. FTMO-compatible (MT5 is one of FTMO's supported platforms).

## Planned components

- **`SignalConsumer/`** — MT5 EA written in MQL5 that connects to the Python signal server (via ZeroMQ or local file watcher), reads structured bias/setup signals, and either auto-executes (if user enables) or posts on-chart alerts for manual review. Manual is the default for FTMO accounts.
- **`IndicatorPack/`** — visual aids on charts: structural pullback markers, regime overlay (current quadrant from Layer 1 specialists), emergency-stop guides, agent-conviction labels overlaid on watchlist symbols.
- **`RiskOverlay/`** — FTMO rule enforcement at the EA level (daily loss limit, max drawdown, news-window trading restrictions, weekend close, consistency rule). The Risk Manager agent (Layer 5) enforces these in software; this overlay enforces them at the platform.

## Bridge architecture

Two-way communication between Python (research) and MT5 (execution):

- **Python → MT5 (commands, signals)**: ZeroMQ PUB from Python; SUB in MT5 EA. Or simpler: Python writes JSON files, MT5 EA polls. ZMQ for low-latency, files for robustness.
- **MT5 → Python (price ticks, account state, fills)**: Either the `MetaTrader5` Python package (direct API to local terminal) or ZeroMQ PUB from MT5 EA, SUB in Python.

Reference projects:
- `MetaTrader5` (official Python package by MetaQuotes) — the de facto standard
- `DWX_ZeroMQ_Connector` (Darwinex Labs) — robust ZMQ bridge

## FTMO-specific notes

- MT5 terminal must be the FTMO-provided build (or compatible)
- EA running in algo trading mode; EA must respect FTMO trading hours and news restrictions
- Compiled `.ex5` artifacts are gitignored; only `.mq5` source is committed
- Test all logic in FTMO demo before any challenge attempt

## Phase relevance

This folder is **Phase C work** — we don't build the bridge until the agent stack is producing value via markdown bias cards. Phase A and B output is human-read.
