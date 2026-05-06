# mt5/

MetaTrader 5 components — **chart visualization only**. FTMO-compatible (MT5 is one of FTMO's supported platforms).

## Decision-support boundary

This folder does not place, modify, or cancel orders. Ever.

The system is a research desk that produces markdown bias briefs and structured filter outputs. Trade decisions, sizing, entry, and trade management are the human's responsibility, executed manually in MT5.

The MT5 layer's only role is making the agent's reasoning visible on charts where the human is already trading — so context comes to the trader, the trader doesn't context-switch to a separate dashboard while a setup is unfolding.

## Planned components (all read-only with respect to orders)

- **`ChartOverlay/`** — MT5 indicator (MQL5) that reads JSON written by the Python pipeline and renders structural markers on charts: trend-pullback zones, agent-supplied invalidation levels, regime quadrant label, conviction tier, freshness state of underlying data. Visual aid only.
- **`AlertPoster/`** — MT5 EA that watches the bias-card directory and posts platform alerts ("EURUSD setup_filter: tradable_now") to MT5's alert system. The alert prompts the human to review the brief; it does not place orders.
- **`RiskHud/`** — Heads-up display showing live FTMO state (daily loss vs limit, max DD vs trailing limit, news-window status, consistency rule status) so the human is aware of constraints before clicking. No automatic enforcement of orders.

What you will NOT find here:
- ❌ Order placement code
- ❌ Position sizing logic
- ❌ Stop-management automation
- ❌ "Auto-trade if conviction > N" gates of any kind, behind any flag

## Data flow

One direction only: **Python → MT5 (read-only signals for display)**.

- Python pipeline writes structured JSON to `bias_cards/{date}/` after each run
- MT5 indicator/EA polls the directory (or reads via local file watcher) and renders annotations
- Optional: ZeroMQ pub/sub if file polling latency becomes a problem (it won't, given the daily run cadence)

MT5 → Python is **not** wired in this design. We don't need MT5's order/account state because the system never reasons about live positions. If price/tick data is needed for the Tradability Filter, it comes from a separate market-data source (yfinance, OANDA, etc.), not from the FTMO terminal.

## FTMO-specific notes

- The MT5 terminal must be the FTMO-provided build (or compatible)
- EAs and indicators here are for visual aid; they don't trip FTMO's automation rules because they don't transact
- Compiled `.ex5` artifacts are gitignored; only `.mq5` source is committed
- Test all visualizations in FTMO demo before live use

## Phase relevance

This folder is **Phase C work**, optional. Phase A and B output is consumed via the Streamlit dashboard and markdown files. The MT5 layer is a convenience for putting the brief next to the chart — useful, not essential.
