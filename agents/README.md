# agents/

Agent persona prompts and configurations.

Organized by layer:

- `layer1_specialists/` — Fed-Watcher, ECB-Watcher, BoJ-Watcher, BoE-Watcher, PBOC, Geopolitical, Inflation, Growth, Positioning, Flow, Energy, Cross-Asset
- `layer2_strategists/` — FX, Rates, Equity, Commodity
- `layer3_redteam/` — Contrarian, Tail Risk, Positioning Reversal
- `layer4_council/` — Bull Advocate, Bear Advocate, Time-Horizon Council, Judge
- `layer5_pm/` — PM Agent, Risk Manager
- `layer6_execution/` — Setup Scanner, Trade Journal
- `layer7_meta/` — Weekly Review, Theme Maintenance, Calibration

Each agent is a markdown file: persona, tools allowed, model tier (cheap/frontier), output schema.
