"""The bias engine pipeline. Runs Layer 1 → 2 → 3 → 4 → 5 against live data.

Phase A scope:
  Layer 1: Inflation Tracker + Positioning Analyst + Fed-Watcher (rates-only)
  Layer 2: FX + Cross-Asset Strategist (combined for Phase A)
  Layer 3: Contrarian
  Layer 4: Bull, Bear, Judge per instrument (only for instruments with conviction >= 5/10)
  Layer 5: PM Brief

Outputs written to bias_cards/YYYY-MM-DD/.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import structlog

import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.agents import run_agent
from src.config import BIAS_CARDS_DIR
from src.data import CotClient, FredClient, PriceClient, render_event_block, upcoming_events
from src.llm import OpenRouterClient
from src.orchestration.context import (
    bear_advocate_input,
    bull_advocate_input,
    contrarian_input,
    fed_watcher_input,
    inflation_tracker_input,
    judge_input,
    load_themes,
    pm_brief_input,
    positioning_analyst_input,
    setup_filter_input,
    strategist_input,
)

log = structlog.get_logger(__name__)

# Watchlist for Layer 2 strategist coverage (still produces context bias cards
# for all of these so the human can see the wider macro picture).
FULL_WATCHLIST = ["DXY", "EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "ES", "NQ", "GC", "CL", "ZN"]

# Focus list: instruments that go through Layer 4 council + Layer 4b filter.
# Expanded to the full watchlist per user direction. Council still requires
# conviction >= COUNCIL_CONVICTION_THRESHOLD before it runs, so on quiet days
# the council fires on a small subset; on high-conviction days it can run
# on most of the universe. Cost scales accordingly.
ACTIVE_UNIVERSE = list(FULL_WATCHLIST)

# Subset with COT positioning data.
COT_INSTRUMENTS = ["EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "GC", "CL", "ZN"]

# Layer 4 council runs only for ACTIVE_UNIVERSE instruments where Layer 2
# conviction >= this threshold.
COUNCIL_CONVICTION_THRESHOLD = 5


@dataclass
class PipelineResult:
    """Aggregate result of one pipeline run."""
    run_date: str
    layer1: dict[str, str] = field(default_factory=dict)
    layer2_strategist: str = ""
    layer3_contrarian: str = ""
    layer4_council: dict[str, dict[str, str]] = field(default_factory=dict)
    layer5_pm_brief: str = ""
    total_cost_usd: float = 0.0
    total_input_tokens: int = 0
    total_output_tokens: int = 0


class BiasEngine:
    """Runs the full bias pipeline. Single entry: `run()`."""

    def __init__(self, client: OpenRouterClient | None = None):
        self.client = client or OpenRouterClient()
        self.fred = FredClient()
        self.cot = CotClient(lookback_years=3)
        self.prices = PriceClient()

    # --- Layer 1 ---

    def run_inflation_tracker(self) -> str:
        log.info("layer1_inflation_start")
        snapshot = self.fred.snapshot([
            "cpi_headline", "cpi_core", "pce_core",
            "sticky_cpi", "breakeven_5y5y", "breakeven_10y", "ahe_level",
        ])
        # Compute YoY for the level series
        yoy = {}
        for name in ["cpi_headline", "cpi_core", "pce_core"]:
            try:
                series = self.fred.yoy(name, periods=12).dropna()
                if not series.empty:
                    yoy[f"{name}_yoy"] = float(series.iloc[-1])
            except Exception as e:
                log.warning("yoy_calc_failed", name=name, error=str(e))
        user_msg = inflation_tracker_input(snapshot, yoy)
        result = run_agent("layer1_specialists/inflation_tracker", user_msg, client=self.client)
        return result.content

    def run_positioning_analyst(self) -> str:
        log.info("layer1_positioning_start")
        summaries = []
        for instrument in COT_INSTRUMENTS:
            try:
                s = self.cot.summary(instrument)
                if s.get("status") == "ok":
                    summaries.append(s)
            except Exception as e:
                log.warning("cot_summary_failed", instrument=instrument, error=str(e))
        user_msg = positioning_analyst_input(summaries)
        result = run_agent("layer1_specialists/positioning_analyst", user_msg, client=self.client)
        return result.content

    def run_fed_watcher(self) -> str:
        log.info("layer1_fed_start")
        snapshot = self.fred.snapshot([
            "ffr_effective", "ffr_target_upper",
            "ust_2y", "ust_10y", "ust_30y", "real_10y",
            "breakeven_5y5y", "breakeven_10y",
        ])
        user_msg = fed_watcher_input(snapshot)
        result = run_agent("layer1_specialists/fed_watcher", user_msg, client=self.client)
        return result.content

    def run_layer1_parallel(self) -> dict[str, str]:
        """Run the three Layer 1 specialists concurrently.

        Each reads its own data sources and produces an independent output;
        no cross-specialist dependencies. Three threads, OpenRouter calls
        block on network I/O, GIL-friendly.
        """
        log.info("layer1_parallel_start")
        with ThreadPoolExecutor(max_workers=3, thread_name_prefix="L1") as ex:
            futures = {
                "inflation": ex.submit(self.run_inflation_tracker),
                "positioning": ex.submit(self.run_positioning_analyst),
                "fed": ex.submit(self.run_fed_watcher),
            }
            outputs: dict[str, str] = {}
            for key, fut in futures.items():
                try:
                    outputs[key] = fut.result()
                except Exception as e:
                    log.error("layer1_parallel_failed", specialist=key, error=str(e))
                    outputs[key] = f"(specialist failed: {e})"
        log.info("layer1_parallel_complete")
        return outputs

    # --- Layer 2 ---

    def run_strategist(self, layer1_outputs: dict[str, str], themes: str) -> str:
        log.info("layer2_strategist_start")
        user_msg = strategist_input(layer1_outputs, themes)
        result = run_agent("layer2_strategists/fx_cross_asset", user_msg, client=self.client)
        return result.content

    # --- Layer 3 ---

    def run_contrarian(self, strategist_output: str, themes: str) -> str:
        log.info("layer3_contrarian_start")
        user_msg = contrarian_input(strategist_output, themes)
        result = run_agent("layer3_redteam/contrarian", user_msg, client=self.client)
        return result.content

    # --- Layer 4 ---

    def _extract_per_instrument_section(self, output: str, instrument: str) -> str:
        """Crude extraction of an instrument's section from a multi-instrument output.

        Strategist and Contrarian produce concatenated outputs across many
        instruments; for Layer 4 advocates we only need the relevant section.
        Falls back to the full output if extraction is uncertain.
        """
        # Try to find INSTRUMENT: <name> markers
        pattern = re.compile(
            rf"INSTRUMENT:\s*{re.escape(instrument)}\b(.*?)(?=INSTRUMENT:\s*\w+|$)",
            re.DOTALL | re.IGNORECASE,
        )
        match = pattern.search(output)
        if match:
            return f"INSTRUMENT: {instrument}{match.group(1).rstrip()}"
        return output  # fallback — agent gets the full strategist/contrarian doc

    def _extract_conviction(self, instrument_section: str) -> int:
        """Extract conviction score from a strategist bias card. Returns 0 if unparseable.

        Tolerates markdown-formatted lines like ``**CONVICTION:** 8/10``.
        """
        # Permissive: any non-digit chars between "CONVICTION" and the digit
        # (covers `:`, `**`, whitespace, smart quotes, etc.). Cap to 30 chars
        # of slack so we don't eat past the line.
        m = re.search(r"CONVICTION[^\d]{0,30}(\d+)\s*/\s*10", instrument_section, re.IGNORECASE)
        return int(m.group(1)) if m else 0

    def run_council_for_instrument(
        self,
        instrument: str,
        strategist_output: str,
        contrarian_output: str,
        themes: str,
    ) -> dict[str, str]:
        log.info("layer4_council_start", instrument=instrument)
        strategist_section = self._extract_per_instrument_section(strategist_output, instrument)
        contrarian_section = self._extract_per_instrument_section(contrarian_output, instrument)

        bull_msg = bull_advocate_input(instrument, strategist_section, contrarian_section, themes)
        bull_result = run_agent("layer4_council/bull_advocate", bull_msg, client=self.client)

        bear_msg = bear_advocate_input(
            instrument, strategist_section, contrarian_section, bull_result.content, themes
        )
        bear_result = run_agent("layer4_council/bear_advocate", bear_msg, client=self.client)

        judge_msg = judge_input(
            instrument, strategist_section, contrarian_section,
            bull_result.content, bear_result.content, themes,
        )
        # Judge runs at temperature 0 — synthesis quality benefits from less
        # stochasticity. See consistency discussion in conversation logs.
        judge_result = run_agent(
            "layer4_council/judge", judge_msg, client=self.client, temperature=0.0,
        )

        return {
            "bull": bull_result.content,
            "bear": bear_result.content,
            "judge": judge_result.content,
        }

    # --- Layer 4b — Tradability Filter ---

    def run_setup_filter(
        self,
        instrument: str,
        judge_card: str,
        themes: str,
    ) -> dict:
        """Run the Tradability Filter for a single instrument.

        Returns a dict including the agent's full output and a parsed verdict
        (best-effort). Falls back to verdict='unparseable' if extraction fails.
        """
        log.info("layer4b_filter_start", instrument=instrument)
        try:
            ctx = self.prices.get_setup_context(instrument).to_dict()
        except Exception as e:
            log.warning("price_context_unavailable", instrument=instrument, error=str(e))
            return {
                "instrument": instrument,
                "verdict": "skip_no_data",
                "verdict_reason": f"Price/setup context unavailable: {e}",
                "agent_output": "",
            }

        # Inject ground-truth event calendar so the Filter doesn't have to
        # rely on the model's memory of release dates.
        events = upcoming_events(days_ahead=7, affects_instrument=instrument,
                                 min_severity="medium")
        events_block = render_event_block(events)

        user_msg = setup_filter_input(instrument, judge_card, ctx, themes,
                                      events_block=events_block)
        # Filter runs at temperature 0 — categorical decisions (tradable/watch/pass)
        # should not flip between runs given identical inputs.
        result = run_agent(
            "layer4b_tradability/setup_filter", user_msg, client=self.client,
            temperature=0.0,
        )

        verdict = self._extract_verdict(result.content)
        return {
            "instrument": instrument,
            "verdict": verdict,
            "agent_output": result.content,
            "setup_context": ctx,
        }

    @staticmethod
    def _extract_verdict(filter_output: str) -> str:
        """Best-effort extraction of the verdict from the filter agent's output."""
        m = re.search(
            r"verdict\s*:\s*[\"']?(tradable_now|watch|pass_despite_bias|skip_no_data)",
            filter_output,
            re.IGNORECASE,
        )
        return m.group(1).lower() if m else "unparseable"

    # --- Layer 5 ---

    def run_pm_brief(
        self,
        judge_outputs: dict[str, str],
        themes: str,
        filter_results: dict[str, dict] | None = None,
    ) -> str:
        log.info("layer5_pm_start")
        user_msg = pm_brief_input(judge_outputs, themes, filter_results=filter_results)
        # PM brief runs at temperature 0 — final synthesis. Some prose
        # variation is fine but the rankings and recommendations themselves
        # should be stable.
        result = run_agent(
            "layer5_pm/pm_druckenmiller", user_msg, client=self.client, temperature=0.0,
        )
        return result.content

    # --- Orchestration ---

    def run(self, council_instruments: list[str] | None = None) -> PipelineResult:
        """Run the full pipeline.

        Args:
            council_instruments: Override which instruments go through Layer 4.
                If None, runs Layer 4 for instruments with strategist conviction
                >= COUNCIL_CONVICTION_THRESHOLD.
        """
        run_date = datetime.now().date().isoformat()
        out_dir = BIAS_CARDS_DIR / run_date
        out_dir.mkdir(parents=True, exist_ok=True)

        result = PipelineResult(run_date=run_date)
        themes = load_themes()

        # Layer 1 — three specialists run in parallel (independent data sources)
        layer1 = self.run_layer1_parallel()
        result.layer1 = layer1
        (out_dir / "01_layer1_inflation.md").write_text(layer1.get("inflation", ""), encoding="utf-8")
        (out_dir / "01_layer1_positioning.md").write_text(layer1.get("positioning", ""), encoding="utf-8")
        (out_dir / "01_layer1_fed.md").write_text(layer1.get("fed", ""), encoding="utf-8")

        # Layer 2
        result.layer2_strategist = self.run_strategist(result.layer1, themes)
        (out_dir / "02_strategist.md").write_text(result.layer2_strategist, encoding="utf-8")

        # Layer 3
        result.layer3_contrarian = self.run_contrarian(result.layer2_strategist, themes)
        (out_dir / "03_contrarian.md").write_text(result.layer3_contrarian, encoding="utf-8")

        # Layer 4 — selective by conviction threshold AND active universe
        if council_instruments is None:
            council_instruments = []
            for inst in FULL_WATCHLIST:
                if inst not in ACTIVE_UNIVERSE:
                    continue
                section = self._extract_per_instrument_section(result.layer2_strategist, inst)
                conviction = self._extract_conviction(section)
                if conviction >= COUNCIL_CONVICTION_THRESHOLD:
                    council_instruments.append(inst)
            log.info(
                "council_filter",
                threshold=COUNCIL_CONVICTION_THRESHOLD,
                active_universe=ACTIVE_UNIVERSE,
                selected=council_instruments,
            )
        else:
            # Explicit override: still respect active universe to avoid drift
            council_instruments = [i for i in council_instruments if i in ACTIVE_UNIVERSE]

        council_dir = out_dir / "04_council"
        council_dir.mkdir(exist_ok=True)
        for instrument in council_instruments:
            outputs = self.run_council_for_instrument(
                instrument, result.layer2_strategist, result.layer3_contrarian, themes,
            )
            result.layer4_council[instrument] = outputs
            (council_dir / f"{instrument}_bull.md").write_text(outputs["bull"], encoding="utf-8")
            (council_dir / f"{instrument}_bear.md").write_text(outputs["bear"], encoding="utf-8")
            (council_dir / f"{instrument}_judge.md").write_text(outputs["judge"], encoding="utf-8")

        # Layer 4b — Tradability Filter (per instrument that cleared council)
        filter_dir = out_dir / "04b_tradability_filter"
        filter_dir.mkdir(exist_ok=True)
        filter_results: dict[str, dict] = {}
        for instrument in council_instruments:
            judge_card = result.layer4_council[instrument]["judge"]
            filter_card = self.run_setup_filter(instrument, judge_card, themes)
            filter_results[instrument] = filter_card
            (filter_dir / f"{instrument}.md").write_text(
                filter_card.get("agent_output") or "_no output_", encoding="utf-8"
            )
        if filter_results:
            (filter_dir / "_summary.json").write_text(
                json.dumps(
                    {i: {"verdict": v.get("verdict")} for i, v in filter_results.items()},
                    indent=2,
                ),
                encoding="utf-8",
            )

        # Layer 5 — only feed PM the judge cards for instruments that have a
        # verdict (any category); PM organises by tradable_now / watch / pass.
        judge_outputs = {inst: outputs["judge"] for inst, outputs in result.layer4_council.items()}
        if judge_outputs:
            result.layer5_pm_brief = self.run_pm_brief(
                judge_outputs, themes, filter_results=filter_results
            )
            (out_dir / "05_pm_brief.md").write_text(result.layer5_pm_brief, encoding="utf-8")
        else:
            result.layer5_pm_brief = (
                "No active-universe instruments met council threshold; no PM brief produced. "
                "This is the expected output on most days — the system is selective by design."
            )

        # Cost summary
        result.total_cost_usd = self.client.budget.spent_today()

        # Write summary index
        index_md = (
            f"# Bias Engine Run — {run_date}\n\n"
            f"## Files\n\n"
            f"- `01_layer1_inflation.md` — Inflation Tracker\n"
            f"- `01_layer1_positioning.md` — Positioning Analyst\n"
            f"- `01_layer1_fed.md` — Fed-Watcher (rates-only mode)\n"
            f"- `02_strategist.md` — Cross-Asset Strategist (per-instrument bias cards)\n"
            f"- `03_contrarian.md` — Contrarian challenge\n"
            f"- `04_council/{{inst}}_{{bull,bear,judge}}.md` — per-instrument debate\n"
            f"- `05_pm_brief.md` — PM Brief\n\n"
            f"## Council instruments\n\n"
            f"{', '.join(council_instruments) if council_instruments else 'none above threshold'}\n\n"
            f"## Cost\n\n"
            f"Total spend today: ${result.total_cost_usd:.4f}\n"
        )
        (out_dir / "00_index.md").write_text(index_md, encoding="utf-8")

        # Persist as JSON too for programmatic access
        run_summary = {
            "run_date": run_date,
            "council_instruments": council_instruments,
            "total_cost_usd": result.total_cost_usd,
            "spent_today": self.client.budget.spent_today(),
        }
        (out_dir / "run_summary.json").write_text(
            json.dumps(run_summary, indent=2), encoding="utf-8"
        )

        return result

    def output_dir(self, run_date: str | None = None) -> Path:
        run_date = run_date or datetime.now().date().isoformat()
        return BIAS_CARDS_DIR / run_date
