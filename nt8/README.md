# nt8/

NinjaTrader 8 C# components — the execution side.

Planned components:

- `SignalConsumer/` — NT8 strategy that connects to the Python signal server, reads structured bias/setup signals, and either auto-executes (if user enables) or posts on-chart alerts for manual review
- `IndicatorPack/` — visual aids on charts: structural pullback markers, regime overlay, emergency-stop guides, agent-conviction labels
- `RiskOverlay/` — FTMO rule enforcement (daily loss limit, max drawdown, news-window trading restrictions)

Compiled artifacts (`*.dll`, `*.pdb`) are gitignored. Source `.cs` files are committed.
