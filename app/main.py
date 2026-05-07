"""FastAPI dashboard for nam-hedgefund.

Routes:
  GET  /                         dashboard, latest run
  GET  /run/{date}               specific run (e.g. 2026-05-07)
  POST /api/chat                 chat completion (JSON in/out)
  POST /api/run                  trigger pipeline; returns PID
  GET  /api/run/status           is a manual run currently in progress?
  GET  /static/*                 css/js
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Make src/ importable
APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.loader import (  # noqa: E402
    INSTRUMENT_DISPLAY,
    InstrumentBias,
    Run,
    TradabilityFilterCard,
    display_label,
    display_name,
    list_runs,
    load_run,
    platform_symbol,
)
from src.config import ROOT  # noqa: E402
from src.data import upcoming_events  # noqa: E402
from src.data.prices import INSTRUMENT_TO_TICKER, PriceClient  # noqa: E402
from src.llm import OpenRouterClient  # noqa: E402
from src.orchestration.pipeline import ACTIVE_UNIVERSE  # noqa: E402  single source of truth
from src.positions import PositionStore, advise_position  # noqa: E402

app = FastAPI(title="nam-hedgefund")
templates = Jinja2Templates(directory=str(APP_ROOT / "templates"))
app.mount("/static", StaticFiles(directory=str(APP_ROOT / "static")), name="static")

# Module-level singletons. Each is cheap to keep around: PositionStore is a
# file-backed CRUD shell, PriceClient holds nothing but a TTL config.
_positions = PositionStore()
_prices = PriceClient()

CONTEXT_CONVICTION_THRESHOLD = 7


# ---------- run state for manual triggers ----------

_run_state: dict = {"pid": None, "started_at": None}


def _is_run_alive(pid: int | None) -> bool:
    if pid is None:
        return False
    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"],
            capture_output=True, text=True, timeout=5,
        )
        return str(pid) in result.stdout
    except Exception:
        return False


# ---------- helpers for templates ----------

def _categorise_filter(run: Run) -> dict:
    return {
        "tradable": [c for c in run.tradability.values() if c.verdict == "tradable_now"],
        "watch": [c for c in run.tradability.values() if c.verdict == "watch"],
        "passed": [c for c in run.tradability.values() if c.verdict == "pass_despite_bias"],
    }


def _hero_position_alerts(run: Run) -> list[dict]:
    """For each active position, run the advisor against the current run and
    return any urgent / high-priority alerts (close, emergency_close, trim
    when conviction has cratered, or trail_stop on a big winner).

    Used to inject position-aware warnings into the hero subline. Returns
    [] if there are no active positions or none have urgent advice.
    """
    try:
        positions = _positions.list_active()
    except Exception:
        return []
    if not positions:
        return []
    alerts = []
    for pos in positions:
        cur = _prices.get_latest_close(pos.instrument)
        if cur is None:
            continue
        adv = advise_position(pos, cur, run)
        if adv.urgency == "high" or adv.action in ("close", "emergency_close", "trim"):
            alerts.append({
                "instrument": pos.instrument,
                "direction": pos.direction,
                "action": adv.action,
                "urgency": adv.urgency,
                "reason": adv.reason,
                "pnl_pct": adv.pnl_pct,
            })
    return alerts


def _hero_state(run: Run, by_verdict: dict) -> dict:
    """Returns hero card content + status class."""
    if by_verdict["tradable"]:
        n = len(by_verdict["tradable"])
        names = ", ".join(
            f"{c.instrument} ({display_label(c.instrument)})"
            for c in by_verdict["tradable"]
        )
        return {
            "status": "tradable",
            "eyebrow": "Today's brief",
            "headline": f"{n} setup{'s' if n != 1 else ''} ready: {names}",
            "subline": (
                "These have cleared structural review. The macro view is supported "
                "and the price location is favorable. Your call on whether to take "
                "any of them. See cards below for direction, levels, and invalidation."
            ),
        }
    if run.tradability:
        n_w = len(by_verdict["watch"])
        n_p = len(by_verdict["passed"])
        return {
            "status": "standby",
            "eyebrow": "Today's brief",
            "headline": "Stand aside — no setups at clean locations",
            "subline": (
                f"{n_w} on watch · {n_p} passed despite bias. "
                "No instrument in the active universe is at a tradable price location. "
                "This is the expected outcome on most days. Cash is a position."
            ),
        }
    if run.layer5_pm_brief:
        return {
            "status": "standby",
            "eyebrow": "Today's brief",
            "headline": "PM brief available — no Tradability Filter",
            "subline": "This run completed without Tradability Filter outputs. Read the brief below.",
        }
    return {
        "status": "standby",
        "eyebrow": "Today's brief",
        "headline": "No actionable setups in the active universe",
        "subline": (
            "No instrument met the conviction threshold today. Stand aside. "
            "Use the Inspect tab to see the underlying analysis."
        ),
    }


def _bias_for(run: Run, instrument: str) -> InstrumentBias | None:
    return next((b for b in run.instrument_biases if b.instrument == instrument), None)


def _conviction_class(conviction: int) -> str:
    if conviction >= 7:
        return "high"
    if conviction >= 4:
        return "med"
    return "low"


def _priority_class(priority: str) -> str:
    return {"A+": "aplus", "A": "a", "B": "b", "C": "c"}.get(priority, "")


def _verdict_label(verdict: str) -> str:
    return {
        "tradable_now": "Tradable now",
        "watch": "Watch",
        "pass_despite_bias": "Passed",
        "skip_no_data": "No data",
        "below_threshold": "Below threshold",
        "unparseable": "Unparseable",
    }.get(verdict, verdict)


import yaml as _yaml

_FILTER_YAML_BLOCK_RE = re.compile(
    r"```ya?ml\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE,
)

# Fallback regexes if the agent didn't wrap output in a yaml fence.
# The first form catches plain `verdict_reason: text` (single line, possibly
# quoted). The folded `verdict_reason: >` and literal `|` block scalars are
# handled by the YAML parser path; if that fails we still try a multi-line
# regex fallback that tolerates indented continuation lines.
_VERDICT_REASON_PLAIN_RE = re.compile(
    r"verdict_reason:\s*[\"']([^\"'\n]+)[\"']", re.IGNORECASE,
)
# Inline unquoted bare scalar — value continues to end-of-line. Used when the
# agent emits `verdict_reason: Applied swing rules: price...` without quotes.
# Such input fails YAML's mapping parser (the colon in the value looks like a
# nested mapping), so we need a regex that doesn't depend on YAML.
# The negative lookahead `(?![>|\s\n])` excludes the folded/literal markers
# `>` and `|` and empty values — those use the multi-line block path.
_VERDICT_REASON_INLINE_RE = re.compile(
    r"verdict_reason:[ \t]+(?![>|\s\n])([^\n]+)", re.IGNORECASE,
)
_VERDICT_REASON_BLOCK_RE = re.compile(
    r"verdict_reason:\s*[>|]?\s*\n((?:[ \t]+[^\n]+\n?)+)", re.IGNORECASE,
)
_HUMAN_NOTES_RE = re.compile(
    r"human_review_notes:\s*\|?\s*\n((?:[ \t]+[^\n]*\n?)+)", re.IGNORECASE,
)


def _parse_filter_yaml(filter_md: str) -> dict:
    """Best-effort: extract the YAML block from a filter card and parse it.

    The Filter agent's prompt asks for a fenced ```yaml block. Most outputs
    follow that. Some don't, so we fall back gracefully — caller checks
    for an empty dict.
    """
    if not filter_md:
        return {}
    m = _FILTER_YAML_BLOCK_RE.search(filter_md)
    if not m:
        return {}
    try:
        data = _yaml.safe_load(m.group(1))
        return data if isinstance(data, dict) else {}
    except _yaml.YAMLError:
        return {}


def _filter_field(filter_md: str, key: str) -> str:
    """Extract a single field from a filter card. Tries YAML parse first,
    then plain-text regex, then block-scalar regex. Returns trimmed string
    or empty."""
    parsed = _parse_filter_yaml(filter_md)
    if parsed and isinstance(parsed.get(key), str):
        return parsed[key].strip()
    if key == "verdict_reason":
        # Try quoted single-line first (cleanest), then unquoted inline,
        # then folded/literal block scalar.
        m = _VERDICT_REASON_PLAIN_RE.search(filter_md or "")
        if m:
            return m.group(1).strip()
        m = _VERDICT_REASON_INLINE_RE.search(filter_md or "")
        if m:
            return m.group(1).strip()
        m = _VERDICT_REASON_BLOCK_RE.search(filter_md or "")
        if m:
            return " ".join(ln.strip() for ln in m.group(1).strip().splitlines()).strip()
    if key == "human_review_notes":
        m = _HUMAN_NOTES_RE.search(filter_md or "")
        if m:
            return " ".join(ln.strip() for ln in m.group(1).strip().splitlines()).strip()
    return ""
_STRATEGIST_NOTES_RE = re.compile(
    r"NOTES?:?\**\s*([^\n*]+(?:\n(?!#|\*\*)[^\n]+)*)", re.IGNORECASE,
)
# Judge's "JUDGMENT REASONING (3-5 sentences):" block — the substantive macro
# story explaining WHY the bias is what it is. Captures the lines that follow
# the heading until a blank line or the next ALL-CAPS section header.
# Tolerates markdown emphasis (**JUDGMENT REASONING:**), trailing spaces,
# and parenthetical asides ("(3-5 sentences)") between the label and colon.
_JUDGE_REASONING_RE = re.compile(
    r"\**\s*JUDGMENT\s+REASONING[^\n:]*:\**\s*\n+"
    r"((?:.+?\n?)+?)(?=\n\s*\n|\n\**\s*[A-Z][A-Z ]+(?:[:(]|\s*\n)|\Z)",
    re.IGNORECASE,
)
_JUDGE_PRIMARY_THEME_RE = re.compile(
    r"PRIMARY\s*THEME[^:]*:\s*([^\n]+)", re.IGNORECASE,
)
_STRATEGIST_PRIMARY_RE = re.compile(
    r"Primary[\s:\-]+([^\n]+)", re.IGNORECASE,
)
_DRIVING_THEMES_RE = re.compile(
    r"DRIVING\s*THEMES?[^\n]*\n((?:[^\n]*\n){1,4})", re.IGNORECASE,
)


def _first_sentence(text: str, max_chars: int = 240) -> str:
    """First sentence of a paragraph, truncated to max_chars.

    Sentences end at `. ` or `.<newline>` or end-of-text. Em/en dashes inside
    a sentence don't count as terminators. If the first 'sentence' is longer
    than max_chars, hard-truncate at a word boundary.
    """
    text = re.sub(r"\s+", " ", text).strip()
    # First sentence: up to first period followed by space or end-of-string.
    m = re.search(r"^(.+?\.)(?:\s|$)", text)
    if m:
        first = m.group(1).strip()
    else:
        first = text
    if len(first) > max_chars:
        cut = first[:max_chars].rsplit(" ", 1)[0]
        first = cut + "…"
    return first


def _extract_macro_summary(b: InstrumentBias, co) -> str:
    """One-sentence macro driver summary: why is the bias what it is?

    Priority (best content first):
      1. Judge's JUDGMENT REASONING first sentence — substantive macro story
      2. Judge's PRIMARY THEME line (label only — fallback when reasoning
         block can't be extracted)
      3. Strategist's first 'Primary:' theme line
      4. Strategist DRIVING THEMES block (first line)
      5. Bias direction + conviction (composed fallback)
    """
    if co and co.judge:
        m = _JUDGE_REASONING_RE.search(co.judge)
        if m:
            block = m.group(1).strip()
            # Drop leading bullet/numbering noise and markdown emphasis chars
            block = re.sub(r"^[-*#>•\s]+", "", block).lstrip()
            block = block.replace("**", "").replace("*", "")
            first = _first_sentence(block, max_chars=260)
            if 30 <= len(first) <= 260:
                return f"Macro: {first}"

        m = _JUDGE_PRIMARY_THEME_RE.search(co.judge)
        if m:
            theme = m.group(1).strip().strip("[]").rstrip(".")
            if 5 <= len(theme) <= 200:
                return f"Macro: {theme}."

    if b.raw_section:
        m = _STRATEGIST_PRIMARY_RE.search(b.raw_section)
        if m:
            theme = m.group(1).strip().strip("*").rstrip(".")
            if 5 <= len(theme) <= 200:
                return f"Macro: {theme}."
        m = _DRIVING_THEMES_RE.search(b.raw_section)
        if m:
            first = m.group(1).strip().split("\n")[0].strip()
            first = re.sub(r"^[-*•\s]+", "", first).rstrip(".")
            if 5 <= len(first) <= 200:
                return f"Macro: {first}."

    return f"Macro: {b.bias.capitalize()} bias at {b.conviction}/10."


def _extract_chart_summary(filter_card, has_council: bool) -> str:
    """One-sentence chart status: what did structural review say?

    Priority:
      1. Filter's verdict_reason (when filter ran) — via YAML parser, with
         regex fallbacks for unfenced or malformed output
      2. Filter's human_review_notes first sentence
      3. 'Council ran but no filter' (transitional state)
      4. 'Below council threshold' (no review at all)
    """
    if filter_card and filter_card.raw:
        reason = _filter_field(filter_card.raw, "verdict_reason")
        if reason:
            return f"Chart: {reason.rstrip('.')}."
        notes = _filter_field(filter_card.raw, "human_review_notes")
        if notes:
            first = notes.split(". ")[0].strip().rstrip(".")
            if first and len(first) < 240:
                return f"Chart: {first}."
        # Sub-threshold instruments produce a `note:` field instead of a
        # verdict — surface that rather than "unparseable" if it's there.
        note = _filter_field(filter_card.raw, "note")
        if note:
            first = note.split(". ")[0].strip().rstrip(".")
            if first and len(first) < 240:
                return f"Chart: {first}."
        return "Chart: filter output unparseable."

    if has_council:
        return "Chart: structural review pending for this run."
    return "Chart: not reviewed (conviction below council threshold)."


def _summarise_card(b: InstrumentBias, filter_card, in_active: bool, council_output=None) -> str:
    """Two-part 'macro + chart' summary. Macro always comes first because
    it's the primary signal source (chart only gates timing)."""
    macro = _extract_macro_summary(b, council_output)
    chart = _extract_chart_summary(filter_card, has_council=council_output is not None)
    return f"{macro} {chart}"


def _build_unified_watchlist(run: Run) -> list[dict]:
    """One ranked list of all instruments. Authoritative conviction = Judge if
    available, else Strategist. Each row carries a single answer per field."""
    rows: list[dict] = []
    for b in run.instrument_biases:
        co = run.council.get(b.instrument)
        if co and co.judge_conviction:
            final_conv = co.judge_conviction
            final_bias = (co.judge_bias or b.bias).lower() or "no view"
        else:
            final_conv = b.conviction
            final_bias = b.bias.lower() or "no view"

        in_active = b.instrument in ACTIVE_UNIVERSE
        filter_card = run.tradability.get(b.instrument)
        verdict = filter_card.verdict if filter_card else None

        # Actionability tier.
        # Two principles:
        #   (a) Filter verdict ALWAYS wins over conviction — if structural
        #       review said skip, it's collapsed regardless of macro conviction.
        #   (b) Conviction < 5 ALWAYS collapses, even if Filter said watch.
        #       This is the defensive layer in case the pipeline lets a
        #       sub-threshold case slip through to the Filter agent.
        # Visibility: tiers 0-2 visible (cards), 3-4 collapsed (compact list).
        if final_conv < 5 and verdict not in ("tradable_now",):
            # Sub-threshold conviction — collapse regardless of Filter verdict.
            # tradable_now is the one carve-out: if the Filter genuinely thinks
            # the chart is so clean that conviction can be revisited, surface it.
            tier, tier_label = 4, "low_conv"
        elif verdict == "tradable_now":
            tier, tier_label = 0, "tradable_now"
        elif verdict == "watch":
            tier, tier_label = 1, "watch"
        elif verdict == "pass_despite_bias":
            tier, tier_label = 3, "passed"
        elif verdict == "below_threshold":
            tier, tier_label = 4, "low_conv"
        elif final_conv >= 6:
            tier, tier_label = 2, "high_conv_no_filter"  # high conv but no filter ran
        else:
            tier, tier_label = 4, "low_conv"

        # Single pill label (plain English).
        # Sub-threshold conviction (<5) is the dominant fact; the Filter
        # verdict is suppressed in the pill because the structural review
        # shouldn't have been treated as authoritative on a thin macro view.
        # tradable_now is the carve-out — if the chart is exceptionally clean
        # we still surface it.
        if verdict == "tradable_now":
            pill_text = "Tradable now"
            pill_class = "tradable"
        elif final_conv < 5:
            pill_text = "Low conviction"
            pill_class = "neutral"
        elif verdict == "watch":
            pill_text = "Watch"
            pill_class = "watch"
        elif verdict == "pass_despite_bias":
            pill_text = "Skip"
            pill_class = "passed"
        elif final_conv >= 6:
            pill_text = "Worth a look"
            pill_class = "watch"
        else:
            pill_text = "Low conviction"
            pill_class = "neutral"

        # Short one-line explanation for the compact 'Other' row.
        # Priority:
        #   1. Filter's verdict_reason — if a structural review happened,
        #      use what it concluded (informative regardless of verdict).
        #   2. Sub-threshold conviction message
        #   3. Generic per-verdict fallback
        simple_summary = ""
        if filter_card and filter_card.raw:
            reason = _filter_field(filter_card.raw, "verdict_reason")
            if reason:
                simple_summary = reason.rstrip(".") + "."
        if not simple_summary:
            if final_conv < 5:
                simple_summary = (
                    f"Low conviction ({final_conv}/10). Macro signal isn't "
                    f"strong enough to justify a structural review."
                )
            elif verdict == "pass_despite_bias":
                simple_summary = (
                    "Macro view supports this, but the chart is against it "
                    "right now (counter-trend, fuzzy invalidation, or blocking event)."
                )
            else:
                simple_summary = f"{final_bias.capitalize()}, but no clear setup yet."

        rows.append({
            "symbol": b.instrument,
            "name": display_label(b.instrument),
            "platform": platform_symbol(b.instrument),
            "platform_differs": platform_symbol(b.instrument) != b.instrument,
            "bias": final_bias,
            "conviction": final_conv,
            "conviction_class": _conviction_class(final_conv),
            "summary": _summarise_card(b, filter_card, in_active, council_output=co),
            "simple_summary": simple_summary,
            "in_active": in_active,
            "has_council": co is not None,
            "has_filter": filter_card is not None,
            "verdict": verdict or "",
            "pill_text": pill_text,
            "pill_class": pill_class,
            "tier": tier,
            "tier_label": tier_label,
        })

    rows.sort(key=lambda r: (r["tier"], -r["conviction"], r["symbol"]))
    return rows


# ===========================================================================
# NEW HOME-VIEW CONTEXT BUILDERS
# Used by the redesigned single-page dashboard (desktop + mobile surfaces).
# Each builder returns plain-dict data — templates do display only, no logic.
# ===========================================================================

# Strength label for an integer conviction. Bands, not digits — the UI shows
# "moderate" for a 6 and a 7 because they're the same band; numeric value is
# also shown for users who want it.
def _strength_band(conviction: int) -> str:
    if conviction >= 8: return "strong"
    if conviction >= 6: return "moderate"
    if conviction >= 5: return "weak"
    return "trash"


def _strength_label(conviction: int) -> str:
    return {
        "strong": "Strong",
        "moderate": "Moderate",
        "weak": "Weak",
        "trash": "Very weak",
    }.get(_strength_band(conviction), "Unknown")


def _normalise_dir_word(bias: str) -> str:
    b = (bias or "").lower()
    if "long" in b or "bull" in b: return "long"
    if "short" in b or "bear" in b: return "short"
    return "no view"


# ─── TODAY: actions + ideas ─────────────────────────────────────────────────

def _build_today_block(run: Run) -> dict:
    """The 'TODAY' panel: bubble up open-trade actions that need attention,
    plus surface fresh trade ideas.

    Returns a dict with two lists:
      actions: open positions where the advisor says trim/close/emergency/trail_stop
      ideas:   setups (not already open as trades) — tradable_now first,
               then high-conviction watches
    """
    actions: list[dict] = []
    ideas: list[dict] = []

    # ----- ACTIONS: open positions needing action -----
    try:
        positions = _positions.list_active()
    except Exception:
        positions = []

    open_instruments: set[str] = {p.instrument for p in positions}
    for pos in positions:
        cur = _prices.get_latest_close(pos.instrument)
        if cur is None:
            continue
        adv = advise_position(pos, cur, run)
        # Only the urgency-meaningful actions go to TODAY. Hold and Review are
        # not actions; they show up in the trades strip but don't bubble.
        if adv.action in ("emergency_close", "close", "trim", "trail_stop"):
            actions.append({
                "kind": "position_action",
                "position_id": pos.id,
                "instrument": pos.instrument,
                "name": display_label(pos.instrument),
                "direction": pos.direction,
                "action": adv.action,
                "action_label": _action_word(adv.action),
                "urgency": adv.urgency,
                "reason": adv.reason,
                "pnl_pct": adv.pnl_pct,
            })
    # Sort by urgency: high → med → low
    urgency_rank = {"high": 0, "med": 1, "low": 2}
    actions.sort(key=lambda a: urgency_rank.get(a["urgency"], 9))

    # ----- IDEAS: fresh setups -----
    candidates: list[dict] = []
    for b in run.instrument_biases:
        if b.instrument in open_instruments:
            continue  # already a trade — don't re-suggest
        co = run.council.get(b.instrument)
        fc = run.tradability.get(b.instrument)
        # Authoritative conviction
        if co and co.judge_conviction:
            conv = co.judge_conviction
            bias_raw = co.judge_bias or b.bias
        else:
            conv = b.conviction
            bias_raw = b.bias
        direction = _normalise_dir_word(bias_raw)
        if direction == "no view" or conv < 5:
            continue
        verdict = fc.verdict if fc else ""
        if verdict == "tradable_now":
            tier = 0
        elif verdict == "watch" and conv >= 6:
            tier = 1
        else:
            continue

        macro_summary = _extract_macro_summary(b, co).removeprefix("Macro: ").strip()
        chart_summary = _extract_chart_summary(fc, has_council=co is not None).removeprefix("Chart: ").strip()
        invalidation = _filter_field(fc.raw, "invalidation_level") if fc else ""
        candidates.append({
            "kind": "idea",
            "instrument": b.instrument,
            "name": display_label(b.instrument),
            "direction": direction,
            "conviction": conv,
            "strength_band": _strength_band(conv),
            "strength_label": _strength_label(conv),
            "verdict": verdict,
            "verdict_label": "Ready" if verdict == "tradable_now" else "Watch",
            "macro_summary": macro_summary,
            "chart_summary": chart_summary,
            "invalidation": invalidation,
            "tier": tier,
        })
    candidates.sort(key=lambda c: (c["tier"], -c["conviction"], c["instrument"]))
    ideas = candidates[:3]  # show top 3 max

    return {"actions": actions, "ideas": ideas}


def _action_word(action: str) -> str:
    return {
        "hold": "Hold",
        "review": "Review",
        "trim": "Trim",
        "trail_stop": "Trail stop",
        "close": "Close",
        "emergency_close": "Emergency close",
    }.get(action, action.title())


def _action_class(action: str) -> str:
    """Return 'urgent' (red), 'attention' (amber), or '' for the action."""
    if action in ("emergency_close", "close"): return "urgent"
    if action in ("trim", "trail_stop", "review"): return "attention"
    return ""


# ─── MACRO PICTURE ──────────────────────────────────────────────────────────

_THEME_HEADING_RE = re.compile(
    r"^###\s+\d+\.\s+(.+?)\s+[—–-]\s+Conviction\s+(\d+)\s*/\s*10",
    re.MULTILINE,
)
_REGIME_HEADER_RE = re.compile(
    r"##\s*Regime\s*Snapshot\s*\n+\*\*([^*]+)\*\*",
    re.IGNORECASE,
)


def _build_macro_block() -> dict:
    """Parse THEMES.md into a structured block: regime headline + ranked theme
    list + next catalyst.
    """
    themes_path = PROJECT_ROOT / "docs" / "THEMES.md"
    if not themes_path.exists():
        return {"regime": "", "themes": [], "next_catalyst": "", "days_to_catalyst": None}
    text = themes_path.read_text(encoding="utf-8")

    # Regime headline
    regime = ""
    m = _REGIME_HEADER_RE.search(text)
    if m:
        regime = m.group(1).strip().rstrip(".")
        # Trim long regime lines to one sentence for the panel
        regime = regime.split(". ")[0].rstrip(".") + "."

    # Themes
    themes = []
    for tm in _THEME_HEADING_RE.finditer(text):
        name = tm.group(1).strip()
        conv = int(tm.group(2))
        themes.append({"name": name, "conviction": conv, "pct": conv * 10})
    themes.sort(key=lambda t: -t["conviction"])

    # Next catalyst from events.yaml — first HIGH-severity event in next 14 days
    try:
        events = upcoming_events(days_ahead=14, min_severity="high")
    except Exception:
        events = []
    next_catalyst = ""
    days_to_catalyst = None
    if events:
        ev = events[0]
        days_to_catalyst = ev.days_from_today
        date_str = ev.date.strftime("%b %d")
        next_catalyst = f"{date_str} — {ev.name}".strip(" —")
    return {
        "regime": regime,
        "themes": themes[:6],
        "next_catalyst": next_catalyst,
        "days_to_catalyst": days_to_catalyst,
    }


# ─── OPEN TRADES STRIP ──────────────────────────────────────────────────────

def _build_open_trades_block(run: Run) -> list[dict]:
    """One row per open position. Includes pnl, current price, advisor verdict."""
    try:
        positions = _positions.list_active()
    except Exception:
        return []
    rows: list[dict] = []
    for pos in positions:
        cur = _prices.get_latest_close(pos.instrument)
        adv = advise_position(pos, cur or pos.entry_price, run)
        rows.append({
            "id": pos.id,
            "instrument": pos.instrument,
            "name": display_label(pos.instrument),
            "direction": pos.direction,
            "entry_price": pos.entry_price,
            "current_price": cur,
            "pnl_pct": adv.pnl_pct,
            "action": adv.action,
            "action_label": _action_word(adv.action),
            "action_class": _action_class(adv.action),
            "urgency": adv.urgency,
            "reason": adv.reason,
            "macro_aligned": adv.macro_aligned,
            "conviction_now": adv.conviction_now,
            "conviction_at_open": pos.conviction_at_open,
            "thesis_at_open": pos.thesis_at_open,
            "emergency_stop": pos.emergency_stop,
            "stop_distance_pct": adv.stop_distance_pct,
            "filter_verdict_now": adv.filter_verdict_now,
            "notes": pos.notes,
        })
    return rows


# ─── ALL INSTRUMENTS TABLE ──────────────────────────────────────────────────

def _build_instruments_table(run: Run, open_instruments: set[str]) -> list[dict]:
    """One row per instrument. Always shows everything in the universe."""
    rows: list[dict] = []
    for b in run.instrument_biases:
        co = run.council.get(b.instrument)
        fc = run.tradability.get(b.instrument)
        if co and co.judge_conviction:
            conv = co.judge_conviction
            bias_raw = co.judge_bias or b.bias
        else:
            conv = b.conviction
            bias_raw = b.bias
        direction = _normalise_dir_word(bias_raw)

        verdict = fc.verdict if fc else ""
        # State word in plain language
        if conv < 5 or verdict == "below_threshold":
            state, state_class = "Macro view too weak to act", "neutral"
        elif verdict == "tradable_now":
            state, state_class = "Ready — chart is at a clean spot", "good"
        elif verdict == "watch":
            state, state_class = "Wait for cleaner pullback", "warn"
        elif verdict == "pass_despite_bias":
            state, state_class = "Skip — chart fighting the macro view", "bad"
        elif verdict == "" and conv >= 5:
            state, state_class = "Macro lean only", "neutral"
        else:
            state, state_class = "—", "neutral"

        rows.append({
            "symbol": b.instrument,
            "name": display_label(b.instrument),
            "direction_raw": bias_raw,
            "direction": direction,
            "conviction": conv,
            "strength_band": _strength_band(conv),
            "strength_label": _strength_label(conv),
            "state": state,
            "state_class": state_class,
            "verdict": verdict,
            "is_open_position": b.instrument in open_instruments,
        })
    rows.sort(key=lambda r: (
        0 if r["is_open_position"] else (1 if r["state_class"] == "good" else
                                          2 if r["state_class"] == "warn" else 3),
        -r["conviction"], r["symbol"],
    ))
    return rows


# ─── HOME CONTEXT (the whole page) ──────────────────────────────────────────

def _detect_surface(request: Request) -> str:
    """Return 'mobile' or 'desktop'. Order of precedence:
      1. ?view=mobile|desktop query param (manual override; sticky via cookie)
      2. user-agent detection (mobile UAs → mobile)
      3. desktop default
    """
    override = request.query_params.get("view")
    if override in ("mobile", "desktop"):
        return override
    cookie = request.cookies.get("nam_view")
    if cookie in ("mobile", "desktop"):
        return cookie
    ua = (request.headers.get("user-agent") or "").lower()
    mobile_markers = ("iphone", "android", "ipod", "mobile safari", "windows phone")
    if any(m in ua for m in mobile_markers):
        return "mobile"
    return "desktop"


def _build_home_context(run: Run, runs: list[str], date: str, surface: str) -> dict:
    today = _build_today_block(run)
    macro = _build_macro_block()
    trades = _build_open_trades_block(run)
    open_instruments = {t["instrument"] for t in trades}
    instruments = _build_instruments_table(run, open_instruments)

    return {
        "surface": surface,
        "run_date": date,
        "runs": runs,
        "today": today,
        "macro": macro,
        "trades": trades,
        "instruments": instruments,
        "brief_md": run.layer5_pm_brief or "",
        "personas": [
            {"key": "default", "label": "Default analyst"},
            {"key": "druckenmiller", "label": "Stanley Druckenmiller"},
            {"key": "dalio", "label": "Ray Dalio"},
            {"key": "soros", "label": "George Soros"},
            {"key": "marks", "label": "Howard Marks"},
            {"key": "buffett", "label": "Warren Buffett"},
        ],
        # Per-instrument reasoning data — used by the "Why?" slide-over
        "reasoning_by_symbol": {
            b.instrument: {
                "symbol": b.instrument,
                "name": display_label(b.instrument),
                "strategist_md": b.raw_section,
                "council": run.council.get(b.instrument),
                "filter_card": run.tradability.get(b.instrument),
            }
            for b in run.instrument_biases
        },
        "instruments_known": sorted(INSTRUMENT_TO_TICKER.keys()),
        "active_universe": ACTIVE_UNIVERSE,
        "render_time": datetime.now().strftime("%H:%M:%S"),
    }


# ---------- routes ----------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    runs = list_runs()
    if not runs:
        return templates.TemplateResponse(
            request, "empty.html", {"message": "No runs yet."}
        )
    return RedirectResponse(url=f"/run/{runs[0]}")


@app.get("/run/{date}", response_class=HTMLResponse)
async def run_page(request: Request, date: str):
    runs = list_runs()
    if date not in runs:
        raise HTTPException(404, f"No run for date {date}")
    run = load_run(date)
    if not run:
        raise HTTPException(500, f"Failed to load run {date}")

    surface = _detect_surface(request)
    ctx = _build_home_context(run, runs, date, surface)
    template = "dashboard_mobile.html" if surface == "mobile" else "dashboard_desktop.html"

    response = templates.TemplateResponse(request, template, ctx)
    # Sticky-set the override cookie so a manual ?view= choice persists.
    override = request.query_params.get("view")
    if override in ("mobile", "desktop"):
        response.set_cookie("nam_view", override, max_age=60 * 60 * 24 * 30, samesite="lax")
    return response


# ---------- API: reasoning + brief (used by slide-over / sheet) ----------

@app.get("/api/reasoning/{symbol}")
async def api_reasoning(symbol: str, date: str | None = None):
    """Return all agent outputs for an instrument so the dashboard can
    render the 'Why?' detail panel without baking everything into the
    initial page render.
    """
    runs = list_runs()
    target = date if date and date in runs else (runs[0] if runs else None)
    if not target:
        raise HTTPException(404, "No runs available")
    run = load_run(target)
    if not run:
        raise HTTPException(500, "Could not load run")
    sym = symbol.upper()
    bias_obj = next((b for b in run.instrument_biases if b.instrument == sym), None)
    co = run.council.get(sym)
    fc = run.tradability.get(sym)
    return JSONResponse({
        "symbol": sym,
        "name": display_label(sym),
        "strategist_md": bias_obj.raw_section if bias_obj else "",
        "strategist_md_rendered": _render_markdown(bias_obj.raw_section) if bias_obj else "",
        "judge_md": co.judge if co else "",
        "judge_md_rendered": _render_markdown(co.judge) if co else "",
        "bull_md": co.bull if co else "",
        "bull_md_rendered": _render_markdown(co.bull) if co else "",
        "bear_md": co.bear if co else "",
        "bear_md_rendered": _render_markdown(co.bear) if co else "",
        "filter_md": fc.raw if fc else "",
        "filter_md_rendered": _render_markdown(fc.raw) if fc else "",
    })


@app.get("/api/brief")
async def api_brief(date: str | None = None):
    """Return the rendered PM brief for a run. Used by the mobile brief sheet."""
    runs = list_runs()
    target = date if date and date in runs else (runs[0] if runs else None)
    if not target:
        return JSONResponse({"html": ""})
    run = load_run(target)
    return JSONResponse({"html": _render_markdown(run.layer5_pm_brief) if run and run.layer5_pm_brief else ""})


# ---------- API: chat ----------

class ChatRequest(BaseModel):
    run_date: str
    persona: str = "default"
    history: list[dict]  # [{"role": "user|assistant", "content": str}]


@app.post("/api/chat")
async def api_chat(req: ChatRequest):
    run = load_run(req.run_date)
    if not run:
        raise HTTPException(404, "Run not found")

    # Build system prompt
    parts: list[str] = []
    if req.persona and req.persona != "default":
        ppath = PROJECT_ROOT / "agents" / "personas" / f"{req.persona}.md"
        if ppath.exists():
            parts.append(ppath.read_text(encoding="utf-8"))
            parts.append("\n---\n")
            parts.append(
                "Stay in this persona. Ground every answer in the run context "
                "below. Do not invent data.\n"
            )
    else:
        parts.append(
            "You are an analyst helping the user understand today's bias-engine brief. "
            "Stay grounded in the content provided — do not invent. If the brief doesn't "
            "address what's asked, say so directly.\n"
        )

    themes_path = PROJECT_ROOT / "docs" / "THEMES.md"
    themes_text = themes_path.read_text(encoding="utf-8") if themes_path.exists() else ""

    parts.extend([
        f"\n# Run context: {req.run_date}\n",
        "## Active themes (THEMES.md)\n",
        themes_text[:8000],
        "\n## PM Brief\n",
        run.layer5_pm_brief or "(no PM brief)",
    ])

    # Inject open positions so persona chats can answer "should I close GC?"
    # questions with full state. Each position carries its open-time macro
    # snapshot, current price, P&L, and the latest advisor verdict.
    try:
        active_positions = _positions.list_active()
    except Exception:
        active_positions = []
    if active_positions:
        parts.append("\n## Open positions (the user's current FTMO trades)\n")
        parts.append(
            "Each position shows the macro view at the time of opening, the "
            "current price, the system's latest advisory verdict, and any user "
            "notes. When the user asks about hold/close/trim, ground your answer "
            "in this state. Do not invent prices or P&L numbers.\n\n"
        )
        for pos in active_positions:
            cur = _prices.get_latest_close(pos.instrument)
            adv = advise_position(pos, cur or pos.entry_price, run)
            parts.append(
                f"### {pos.instrument} {pos.direction.upper()} "
                f"(opened {pos.entry_date} at {pos.entry_price})\n"
                f"- Bias at open: {pos.bias_at_open} {pos.conviction_at_open}/10 "
                f"({pos.timeframe_at_open or 'unspecified timeframe'})\n"
                f"- Thesis at open: {pos.thesis_at_open}\n"
                f"- Emergency stop: {pos.emergency_stop or 'not set'}\n"
                f"- Current price: {cur}\n"
                f"- P&L: {adv.pnl_pct}%\n"
                f"- Macro now: bias {'aligned' if adv.macro_aligned else 'OPPOSED'}, "
                f"conviction {adv.conviction_now}/10 "
                f"(Δ {adv.conviction_delta:+d} since open)\n"
                f"- Filter verdict now: {adv.filter_verdict_now or 'n/a'}\n"
                f"- Advisor recommends: **{adv.action}** ({adv.urgency} urgency) — {adv.reason}\n"
                f"- Notes: {pos.notes or '(none)'}\n\n"
            )

    parts.append("\n## Tradability Filter results\n")
    for inst, card in run.tradability.items():
        parts.append(f"\n### {inst} — {card.verdict}\n")
        parts.append(card.raw[:3000])
    parts.extend([
        "\n## Strategist (excerpt)\n",
        run.layer2_strategist[:12000] if run.layer2_strategist else "(none)",
        "\n## Layer 1 specialists\n",
        "\n### Inflation Tracker\n",
        run.layer1_inflation[:3000] if run.layer1_inflation else "(none)",
        "\n### Positioning Analyst\n",
        run.layer1_positioning[:3000] if run.layer1_positioning else "(none)",
        "\n### Fed-Watcher\n",
        run.layer1_fed[:3000] if run.layer1_fed else "(none)",
    ])
    system_prompt = "\n".join(parts)

    user_msg = "\n\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in req.history[-12:]
    )

    try:
        client = OpenRouterClient()
        result = client.complete(
            system=system_prompt,
            user=user_msg,
            tier="cheap",
            temperature=0.4 if req.persona != "default" else 0.3,
        )
        return JSONResponse({
            "content": result.content,
            "tokens_in": result.input_tokens,
            "tokens_out": result.output_tokens,
            "cost_usd": result.cost_usd,
        })
    except Exception as e:
        raise HTTPException(500, f"Chat failed: {e}")


# ---------- API: positions ----------
#
# All positions endpoints are decision-support only: open/close marks state
# changes the user has *already made* (or intends to make) on FTMO. The
# system never executes; it only records and advises.

class OpenPositionRequest(BaseModel):
    instrument: str
    direction: str                  # "long" | "short"
    entry_price: float
    entry_date: str | None = None    # ISO date; defaults to today server-side
    size_units: float | None = None
    emergency_stop: float | None = None
    notes: str = ""
    snapshot_run_date: str | None = None  # which run's macro snapshot to freeze


class ClosePositionRequest(BaseModel):
    close_price: float
    close_reason: str = ""
    close_date: str | None = None


class NoteRequest(BaseModel):
    note: str


class StopRequest(BaseModel):
    emergency_stop: float


def _macro_snapshot(run, instrument: str) -> dict:
    """Freeze the macro state for an instrument at the moment a position opens.

    Used so the advisor can later detect "thesis weakened" by comparing
    current conviction against what it was when the trade was put on.
    """
    if not run:
        return {
            "bias_at_open": "",
            "conviction_at_open": 0,
            "timeframe_at_open": "",
            "thesis_at_open": "",
        }
    bias_obj = next((b for b in run.instrument_biases
                     if b.instrument == instrument), None)
    co = run.council.get(instrument)
    # Authoritative conviction: Judge if available, else Strategist
    if co and co.judge_conviction:
        conv = co.judge_conviction
        bias = co.judge_bias or (bias_obj.bias if bias_obj else "")
    elif bias_obj:
        conv = bias_obj.conviction
        bias = bias_obj.bias
    else:
        conv = 0
        bias = ""
    # Direction snapshot — normalise to long/short/no_view
    bl = (bias or "").lower()
    if "long" in bl or "bull" in bl:
        bias_norm = "long"
    elif "short" in bl or "bear" in bl:
        bias_norm = "short"
    else:
        bias_norm = "no_view"
    # Timeframe (best-effort from strategist card text)
    tf = ""
    if bias_obj and bias_obj.timeframe:
        tf_lower = bias_obj.timeframe.lower()
        if "tactical" in tf_lower:
            tf = "tactical"
        elif "swing" in tf_lower:
            tf = "swing"
        elif "positional" in tf_lower or "month" in tf_lower:
            tf = "positional"
    # Thesis: try first sentence of Judge's reasoning, else strategist excerpt
    thesis = ""
    if co and co.judge:
        thesis = _extract_macro_summary(bias_obj, co)
        thesis = thesis.removeprefix("Macro: ").strip()
    elif bias_obj and bias_obj.raw_section:
        thesis = bias_obj.raw_section[:300].strip()
    return {
        "bias_at_open": bias_norm,
        "conviction_at_open": int(conv),
        "timeframe_at_open": tf,
        "thesis_at_open": thesis[:400],
    }


@app.get("/api/positions")
async def api_positions_list():
    """Return active positions (with current price, P&L, advice) and recent
    closed positions (with P&L). The advice block is regenerated on every
    request because it depends on the latest run's state.
    """
    runs = list_runs()
    latest_run = load_run(runs[0]) if runs else None
    active = _positions.list_active()
    closed = _positions.list_closed_recent()

    active_out = []
    for pos in active:
        current_price = _prices.get_latest_close(pos.instrument)
        if current_price is None:
            # No price means we can't compute P&L or advise — return the
            # position raw with a placeholder. User still sees it on the page.
            active_out.append({
                "position": pos.to_dict(),
                "current_price": None,
                "advice": {
                    "action": "review",
                    "urgency": "low",
                    "reason": (f"Could not fetch latest price for {pos.instrument}. "
                               f"Manually verify before any action."),
                },
            })
            continue
        advice = advise_position(pos, current_price, latest_run)
        active_out.append({
            "position": pos.to_dict(),
            "current_price": round(current_price, 4),
            "advice": advice.to_dict(),
        })

    return JSONResponse({
        "active": active_out,
        "closed_recent": [pos.to_dict() for pos in closed],
        "latest_run_date": latest_run.run_date if latest_run else None,
        "instruments_known": sorted(INSTRUMENT_TO_TICKER.keys()),
    })


@app.post("/api/positions")
async def api_positions_open(req: OpenPositionRequest):
    inst = req.instrument.upper().strip()
    if inst not in INSTRUMENT_TO_TICKER:
        raise HTTPException(
            400, f"Unknown instrument {inst!r}. "
            f"Supported: {sorted(INSTRUMENT_TO_TICKER.keys())}",
        )
    if req.direction not in ("long", "short"):
        raise HTTPException(400, "direction must be 'long' or 'short'")
    if req.entry_price <= 0:
        raise HTTPException(400, "entry_price must be positive")

    # Snapshot macro state — use the requested run if specified, else latest
    snap_run = None
    if req.snapshot_run_date:
        snap_run = load_run(req.snapshot_run_date)
    if snap_run is None:
        runs = list_runs()
        if runs:
            snap_run = load_run(runs[0])
    snapshot = _macro_snapshot(snap_run, inst)

    pos = _positions.open(
        instrument=inst,
        direction=req.direction,
        entry_price=req.entry_price,
        entry_date=req.entry_date,
        size_units=req.size_units,
        emergency_stop=req.emergency_stop,
        notes=req.notes,
        **snapshot,
    )
    return JSONResponse({"position": pos.to_dict()}, status_code=201)


@app.post("/api/positions/{position_id}/close")
async def api_positions_close(position_id: str, req: ClosePositionRequest):
    pos = _positions.close(
        position_id=position_id,
        close_price=req.close_price,
        close_reason=req.close_reason,
        close_date=req.close_date,
    )
    if pos is None:
        raise HTTPException(404, f"No active position with id {position_id!r}")
    return JSONResponse({"position": pos.to_dict()})


@app.post("/api/positions/{position_id}/note")
async def api_positions_add_note(position_id: str, req: NoteRequest):
    pos = _positions.add_note(position_id, req.note)
    if pos is None:
        raise HTTPException(404, f"No position with id {position_id!r}")
    return JSONResponse({"position": pos.to_dict()})


@app.post("/api/positions/{position_id}/stop")
async def api_positions_update_stop(position_id: str, req: StopRequest):
    pos = _positions.update_emergency_stop(position_id, req.emergency_stop)
    if pos is None:
        raise HTTPException(
            404, f"No active position with id {position_id!r}",
        )
    return JSONResponse({"position": pos.to_dict()})


@app.delete("/api/positions/{position_id}")
async def api_positions_delete(position_id: str):
    """Hard-delete a position. Use only for mistakes; closed trades should be
    closed via /close so they go to the journal.
    """
    if not _positions.delete(position_id):
        raise HTTPException(404, f"No position with id {position_id!r}")
    return JSONResponse({"deleted": position_id})


# ---------- API: manual run trigger ----------

@app.post("/api/run")
async def api_run():
    # Don't start a second run if one is already going (whether internally
    # tracked or detected from the log/process state).
    detected = _detect_running_pipeline()
    if detected:
        return JSONResponse({
            "status": "already_running",
            "pid": detected.get("pid"),
            "source": detected.get("source"),
            "started_at": detected.get("started_at"),
        })
    bat = PROJECT_ROOT / "scripts" / "run_daily.bat"
    if not bat.exists():
        raise HTTPException(500, f"Script not found: {bat}")
    proc = subprocess.Popen(
        [str(bat)],
        cwd=str(PROJECT_ROOT),
        shell=True,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )
    _run_state["pid"] = proc.pid
    _run_state["started_at"] = datetime.now()
    return JSONResponse({
        "status": "started",
        "pid": proc.pid,
        "started_at": _run_state["started_at"].isoformat(),
    })


_LOG_PATH = PROJECT_ROOT / "logs" / "bias_engine.log"

# Matches the timestamp written by run_daily.bat's "Run started DATE TIME"
# header line, which uses Windows "DD/MM/YYYY  H:MM:SS.cc" format.
_LOG_RUN_STARTED_RE = re.compile(
    r"Run started\s+(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}:\d{2})"
)


def _find_recent_run_start(tail: list[str]) -> datetime | None:
    """Walk a log tail backward for the most recent 'Run started' line.

    Used when we're rendering an in-progress run that this uvicorn instance
    didn't launch — e.g., the user clicked Run, server got restarted, the
    pipeline kept going. We can still time it by reading the start timestamp
    from the log header that run_daily.bat writes.
    """
    for ln in reversed(tail):
        m = _LOG_RUN_STARTED_RE.search(ln)
        if not m:
            continue
        date_str, time_str = m.groups()
        for fmt in ("%d/%m/%Y %H:%M:%S", "%m/%d/%Y %H:%M:%S"):
            try:
                return datetime.strptime(f"{date_str} {time_str}", fmt)
            except ValueError:
                continue
    return None


def _detect_running_pipeline() -> dict | None:
    """Return run-in-progress info if a pipeline is currently running.

    Two detection paths:
      1. Internal — _run_state['pid'] is alive. Cheap, exact start time.
      2. Log-based — log file modified within last 5 min AND the tail
         doesn't show a 'Run finished'. Catches runs the server didn't
         start (cron task, terminal, or pre-restart). 5-minute threshold
         is wide enough that slow agent calls (DeepSeek can take 3 min)
         don't false-negative.
    """
    # 1. Internal
    pid = _run_state.get("pid")
    if pid and _is_run_alive(pid):
        started = _run_state.get("started_at")
        return {
            "pid": pid,
            "started_at": started.isoformat() if started else None,
            "source": "internal",
        }

    # 2. Log-based
    if not _LOG_PATH.exists():
        return None
    mtime = datetime.fromtimestamp(_LOG_PATH.stat().st_mtime)
    age_seconds = (datetime.now() - mtime).total_seconds()
    if age_seconds > 300:
        return None
    tail = _read_log_tail(30)
    # Most-recent 'Run finished' line means we're past the run, not in it.
    if any("Run finished" in ln for ln in tail[-10:]):
        return None
    # An agent call must be in flight (or some layer activity)
    if not any(
        ("openrouter_call_start" in ln or "run_agent_start" in ln or "layer" in ln)
        for ln in tail
    ):
        return None
    start_time = _find_recent_run_start(_read_log_tail(800))
    return {
        "pid": None,
        "started_at": start_time.isoformat() if start_time else None,
        "source": "external",
    }


# Pipeline stages, in order, with friendly labels. Used to render progress.
_STAGES = [
    ("layer1_inflation_start", "Layer 1 — Inflation Tracker"),
    ("layer1_positioning_start", "Layer 1 — Positioning Analyst"),
    ("layer1_fed_start", "Layer 1 — Fed-Watcher"),
    ("layer2_strategist_start", "Layer 2 — Strategist (synthesis)"),
    ("layer3_contrarian_start", "Layer 3 — Contrarian (red team)"),
    ("layer4_council_start", "Layer 4 — Bias Council debate"),
    ("layer4b_filter_start", "Layer 4b — Tradability Filter"),
    ("layer5_pm_start", "Layer 5 — PM Brief"),
]


def _read_log_tail(n: int = 50) -> list[str]:
    if not _LOG_PATH.exists():
        return []
    try:
        with _LOG_PATH.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        return [ln.rstrip("\n") for ln in lines[-n:]]
    except Exception:
        return []


def _detect_current_stage(log_tail: list[str]) -> dict:
    """Find the most recent stage start line in the log.

    Parallel-aware: if a parallel layer is in flight (start logged, complete
    not yet logged), report it as a single coherent stage with an in-flight
    count rather than the most recent individual agent (which jumps between
    threads under parallel mode).
    """
    last_event_line = next((ln for ln in reversed(log_tail) if "[info" in ln), None)

    # ---- Parallel-block detection ----
    parallel_blocks = [
        ("layer1_parallel_start", "layer1_parallel_complete",
         "Layer 1 — Specialists (3 in parallel)"),
        ("layer4_parallel_start", "layer4_parallel_complete",
         "Layer 4 + 4b — Council & Filter (parallel)"),
    ]
    for start_marker, end_marker, label in parallel_blocks:
        # Most recent occurrence of start, with no following complete
        last_start_idx = -1
        last_end_idx = -1
        for i, ln in enumerate(log_tail):
            if start_marker in ln:
                last_start_idx = i
            if end_marker in ln:
                last_end_idx = i
        if last_start_idx >= 0 and last_end_idx < last_start_idx:
            # In flight. Count agent_start minus agent_complete since the
            # parallel block started — gives the user a real progress feel.
            since_start = log_tail[last_start_idx:]
            starts = sum(1 for ln in since_start if "run_agent_start" in ln)
            completes = sum(1 for ln in since_start if "run_agent_complete" in ln)
            in_flight = max(0, starts - completes)
            stage = f"{label} · {completes} done · {in_flight} in flight"
            return {"stage": stage, "last_event_line": last_event_line}

    # ---- Fallback: serial-stage detection ----
    stage_label = "Starting…"
    instrument: str | None = None
    agent: str | None = None
    for ln in reversed(log_tail):
        for marker, label in _STAGES:
            if marker in ln:
                stage_label = label
                if "instrument=" in ln:
                    try:
                        instrument = ln.split("instrument=")[1].split()[0]
                    except Exception:
                        pass
                if "agent=" in ln:
                    try:
                        agent = ln.split("agent=")[1].split()[0]
                    except Exception:
                        pass
                if instrument:
                    stage_label = f"{stage_label} · {instrument}"
                if agent and "agent_start" in ln:
                    stage_label = f"{stage_label} ({agent})"
                return {"stage": stage_label, "last_event_line": last_event_line}
    return {"stage": stage_label, "last_event_line": last_event_line}


def _latest_run_meta() -> dict | None:
    """Read most recent completed run's summary."""
    runs = list_runs()
    if not runs:
        return None
    summary_path = PROJECT_ROOT / "bias_cards" / runs[0] / "run_summary.json"
    if not summary_path.exists():
        return {"run_date": runs[0], "completed_at": None, "cost_usd": None}
    try:
        data = json.loads(summary_path.read_text(encoding="utf-8"))
        mtime = datetime.fromtimestamp(summary_path.stat().st_mtime)
        return {
            "run_date": data.get("run_date", runs[0]),
            "completed_at": mtime.isoformat(timespec="seconds"),
            "cost_usd": data.get("total_cost_usd"),
        }
    except Exception:
        return {"run_date": runs[0], "completed_at": None, "cost_usd": None}


@app.get("/api/run/status")
async def api_run_status():
    latest = _latest_run_meta()

    detected = _detect_running_pipeline()
    if not detected:
        # No internal PID and no log activity — clear the stale internal state
        # so a future button-press doesn't think a run is already going.
        if _run_state.get("pid"):
            _run_state["pid"] = None
            _run_state["started_at"] = None
        return JSONResponse({"running": False, "latest": latest})

    started_iso = detected.get("started_at")
    started_dt: datetime | None = None
    if started_iso:
        try:
            started_dt = datetime.fromisoformat(started_iso)
        except ValueError:
            started_dt = None
    elapsed_s = (
        int((datetime.now() - started_dt).total_seconds())
        if started_dt else 0
    )
    est_total = 900
    pct = min(95, int(elapsed_s / est_total * 100)) if elapsed_s else 0
    stage_info = _detect_current_stage(_read_log_tail(200))

    return JSONResponse({
        "running": True,
        "pid": detected.get("pid"),
        "source": detected.get("source"),
        "started_at": started_iso,
        "elapsed_seconds": elapsed_s,
        "estimated_total_seconds": est_total,
        "estimated_pct": pct,
        "stage": stage_info["stage"],
        "last_event_line": stage_info["last_event_line"],
        "latest": latest,
    })


@app.get("/api/run/log")
async def api_run_log(lines: int = 30):
    return JSONResponse({"lines": _read_log_tail(lines)})


# ---------- markdown rendering helper for templates ----------

import markdown as md_lib  # noqa: E402

_md = md_lib.Markdown(extensions=["fenced_code", "tables", "nl2br", "sane_lists"])


def _render_markdown(text: str) -> str:
    if not text:
        return ""
    stripped = text.strip()
    # Defensive: if the whole content is wrapped in a single code fence
    # (LLMs sometimes do this even when not asked), peel it. Otherwise
    # markdown renders the entire brief as one <pre> block that doesn't
    # wrap on mobile.
    if stripped.startswith("```") and stripped.rstrip().endswith("```"):
        lines = stripped.split("\n")
        if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].strip() == "```":
            stripped = "\n".join(lines[1:-1])
    _md.reset()
    return _md.convert(stripped)


templates.env.filters["markdown"] = _render_markdown
