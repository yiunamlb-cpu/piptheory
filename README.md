# piptheory

A solo discretionary macro research desk, augmented by LLM agents.

Modeled on a small (2018-era) discretionary macro fund: layered specialist agents synthesize macro themes into instrument-level bias; human takes trade decisions; trend-pullback execution on prop-firm capital (FTMO-style).

## Status

Foundation phase. Architecture drafted, scaffold initialized. Agents and data pipelines not yet implemented.

## Layout

- `docs/` — architecture, themes, watchlist, build phases, tooling survey
- `playbook/` — macro frameworks distilled from primary sources (Dalio, Soros, Druckenmiller, central bank reading guides)
- `agents/` — agent persona prompts and configs
- `src/` — Python: data pipelines, agent runners, MT5 bridge
- `mt5/` — MetaTrader 5 EAs and indicators (signal consumers, FTMO execution)

## Universe

9 instruments: DXY, EURUSD, USDJPY, GBPUSD, AUDUSD, ES, NQ, GC, CL. (ZN was removed in May 2026 — FTMO doesn't offer Treasury futures; rates view still tracked from FRED.)

## Strategy

Discretionary trend-pullback. Wide structural stops, position sizing off the emergency stop, multi-timeframe trend filter, regime-aware sizing. Agents produce daily bias and setup alerts; human decides.

## License

Private. All rights reserved.
