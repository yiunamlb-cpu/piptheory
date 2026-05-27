"""Reads bias_cards/{date}/ output from disk and structures it for the dashboard."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from src.config import BIAS_CARDS_DIR


# Human-readable names + MT5/FTMO platform symbol where it differs.
# Format kept short so it fits in card headers and selectboxes.
INSTRUMENT_DISPLAY: dict[str, dict[str, str]] = {
    "DXY":    {"name": "US Dollar Index",      "platform": "DXY"},
    "EURUSD": {"name": "Euro / US Dollar",     "platform": "EURUSD"},
    "USDJPY": {"name": "US Dollar / Yen",      "platform": "USDJPY"},
    "GBPUSD": {"name": "Pound / US Dollar",    "platform": "GBPUSD"},
    "AUDUSD": {"name": "Aussie / US Dollar",   "platform": "AUDUSD"},
    "ES":     {"name": "S&P 500",              "platform": "US500"},
    "NQ":     {"name": "Nasdaq 100",           "platform": "NAS100"},
    "GC":     {"name": "Gold",                 "platform": "XAUUSD"},
    "CL":     {"name": "WTI Crude Oil",        "platform": "USOIL"},
    "ZN":     {"name": "US 10Y Treasury Note", "platform": "USTNOTE"},
}


def display_name(symbol: str) -> str:
    """Return e.g. 'ES — S&P 500' or just the symbol if unknown."""
    info = INSTRUMENT_DISPLAY.get(symbol.upper())
    if not info:
        return symbol
    return f"{symbol} — {info['name']}"


def display_label(symbol: str) -> str:
    """Just the human-readable name (no symbol prefix), e.g. 'S&P 500'."""
    info = INSTRUMENT_DISPLAY.get(symbol.upper())
    return info["name"] if info else symbol


def platform_symbol(symbol: str) -> str:
    """Return the MT5/FTMO platform symbol if it differs (e.g. ES -> US500)."""
    info = INSTRUMENT_DISPLAY.get(symbol.upper())
    return info["platform"] if info else symbol


@dataclass
class InstrumentBias:
    """A single instrument's bias card extracted from the strategist output."""
    instrument: str
    bias: str = ""
    conviction: int = 0
    timeframe: str = ""
    priority: str = ""
    raw_section: str = ""


@dataclass
class CouncilOutput:
    """Bull / bear / judge outputs for an instrument."""
    instrument: str
    bull: str = ""
    bear: str = ""
    judge: str = ""
    judge_conviction: int = 0  # parsed from the judge card; authoritative when present
    judge_bias: str = ""       # parsed bias text from judge; authoritative when present


@dataclass
class TradabilityFilterCard:
    """One instrument's Tradability Filter (Layer 4b) output."""
    instrument: str
    verdict: str = "unparseable"  # tradable_now | watch | pass_despite_bias | skip_no_data | unparseable
    raw: str = ""


@dataclass
class Run:
    """All artifacts of one bias-engine run."""
    run_date: str
    layer1_inflation: str = ""
    layer1_positioning: str = ""
    layer1_fed: str = ""
    layer2_strategist: str = ""
    layer3_contrarian: str = ""
    layer5_pm_brief: str = ""
    council: dict[str, CouncilOutput] = field(default_factory=dict)
    tradability: dict[str, TradabilityFilterCard] = field(default_factory=dict)
    tradability_summary: dict = field(default_factory=dict)
    instrument_biases: list[InstrumentBias] = field(default_factory=list)
    run_summary: dict = field(default_factory=dict)


def list_runs() -> list[str]:
    """Return run dates (YYYY-MM-DD) sorted descending (most recent first)."""
    if not BIAS_CARDS_DIR.exists():
        return []
    out = []
    for p in BIAS_CARDS_DIR.iterdir():
        if p.is_dir():
            try:
                date.fromisoformat(p.name)
                out.append(p.name)
            except ValueError:
                continue
    return sorted(out, reverse=True)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


_FILTER_VERDICT_RE = re.compile(
    r"verdict\s*:\s*[\"']?"
    r"(tradable_now|watch|pass_despite_bias|skip_no_data|below_threshold)",
    re.IGNORECASE,
)


def _extract_filter_verdict(filter_md: str) -> str:
    m = _FILTER_VERDICT_RE.search(filter_md)
    return m.group(1).lower() if m else "unparseable"


# Per-instrument section in the strategist output. Newer LLM runs wrap
# the labels in markdown bold (`**INSTRUMENT:**`), so the regex tolerates
# any combination of `*` characters and whitespace between the label and
# the value. Older runs without bold still parse correctly because `\**`
# matches zero asterisks.
_INSTRUMENT_PATTERN = re.compile(
    r"INSTRUMENT:\**\s*\**\s*([A-Z][A-Z0-9]*)\b(.*?)(?=INSTRUMENT:\**\s*\**\s*[A-Z]|\Z)",
    re.DOTALL | re.IGNORECASE,
)
_CONVICTION_PATTERN = re.compile(r"CONVICTION[^\d]{0,30}(\d+)\s*/\s*10", re.IGNORECASE)
_BIAS_PATTERN = re.compile(r"BIAS:?\**\s*\**\s*([^\n*]+)", re.IGNORECASE)
_TIMEFRAME_PATTERN = re.compile(r"TIMEFRAME:?\**\s*\**\s*([^\n*]+)", re.IGNORECASE)
_PRIORITY_PATTERN = re.compile(r"PRIORITY:?\**\s*\**\s*([A-D][+\-]?)", re.IGNORECASE)


def parse_strategist(strategist_md: str) -> list[InstrumentBias]:
    """Extract per-instrument bias summaries from the strategist output."""
    if not strategist_md:
        return []
    biases: list[InstrumentBias] = []
    for m in _INSTRUMENT_PATTERN.finditer(strategist_md):
        instrument = m.group(1).strip().upper()
        section = m.group(2)
        bias = ""
        conviction = 0
        timeframe = ""
        priority = ""
        if bm := _BIAS_PATTERN.search(section):
            bias = bm.group(1).strip().rstrip("*").strip()
        if cm := _CONVICTION_PATTERN.search(section):
            conviction = int(cm.group(1))
        if tm := _TIMEFRAME_PATTERN.search(section):
            timeframe = tm.group(1).strip().rstrip("*").strip()
        if pm := _PRIORITY_PATTERN.search(section):
            priority = pm.group(1).strip().upper()
        biases.append(InstrumentBias(
            instrument=instrument,
            bias=bias,
            conviction=conviction,
            timeframe=timeframe,
            priority=priority,
            raw_section=f"INSTRUMENT: {instrument}{section}".strip(),
        ))
    return biases


def load_run(run_date: str) -> Run | None:
    """Load all artifacts for a run date. Returns None if no run exists."""
    base = BIAS_CARDS_DIR / run_date
    if not base.exists():
        return None

    run = Run(run_date=run_date)
    run.layer1_inflation = _read(base / "01_layer1_inflation.md")
    run.layer1_positioning = _read(base / "01_layer1_positioning.md")
    run.layer1_fed = _read(base / "01_layer1_fed.md")
    run.layer2_strategist = _read(base / "02_strategist.md")
    run.layer3_contrarian = _read(base / "03_contrarian.md")
    run.layer5_pm_brief = _read(base / "05_pm_brief.md")
    run.instrument_biases = parse_strategist(run.layer2_strategist)

    council_dir = base / "04_council"
    if council_dir.exists():
        # Group council files by instrument
        council: dict[str, CouncilOutput] = {}
        for f in council_dir.iterdir():
            if not f.is_file() or not f.name.endswith(".md"):
                continue
            stem = f.stem  # e.g. "EURUSD_bull"
            if "_" not in stem:
                continue
            instrument, role = stem.rsplit("_", 1)
            if role not in {"bull", "bear", "judge"}:
                continue
            entry = council.setdefault(instrument, CouncilOutput(instrument=instrument))
            setattr(entry, role, _read(f))
        # Parse judge conviction + bias (authoritative final values when present).
        # Bold-tolerant like the strategist patterns above.
        _JUDGE_BIAS_RE = re.compile(
            r"FINAL\s*BIAS:?\**\s*\**\s*([^\n*]+)", re.IGNORECASE,
        )
        for instrument, co in council.items():
            if co.judge:
                m = _CONVICTION_PATTERN.search(co.judge)
                if m:
                    co.judge_conviction = int(m.group(1))
                bm = _JUDGE_BIAS_RE.search(co.judge)
                if bm:
                    co.judge_bias = bm.group(1).strip().rstrip("*").strip()
        run.council = council

    # Layer 4b — Tradability Filter outputs
    filter_dir = base / "04b_tradability_filter"
    if filter_dir.exists():
        for f in filter_dir.iterdir():
            if not f.is_file() or not f.name.endswith(".md"):
                continue
            instrument = f.stem
            raw = _read(f)
            verdict = _extract_filter_verdict(raw)
            run.tradability[instrument] = TradabilityFilterCard(
                instrument=instrument, verdict=verdict, raw=raw,
            )
        summary_file = filter_dir / "_summary.json"
        if summary_file.exists():
            try:
                run.tradability_summary = json.loads(summary_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                run.tradability_summary = {}

    summary_path = base / "run_summary.json"
    if summary_path.exists():
        try:
            run.run_summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            run.run_summary = {}

    return run


def latest_run() -> Run | None:
    runs = list_runs()
    return load_run(runs[0]) if runs else None
