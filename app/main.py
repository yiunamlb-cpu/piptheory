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
from src.llm import OpenRouterClient  # noqa: E402

app = FastAPI(title="nam-hedgefund")
templates = Jinja2Templates(directory=str(APP_ROOT / "templates"))
app.mount("/static", StaticFiles(directory=str(APP_ROOT / "static")), name="static")

ACTIVE_UNIVERSE = ["ES", "NQ", "GC"]
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
        "unparseable": "Unparseable",
    }.get(verdict, verdict)


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

    by_verdict = _categorise_filter(run)
    hero = _hero_state(run, by_verdict)

    # Active universe cards
    active_cards = []
    for inst in ACTIVE_UNIVERSE:
        bias = _bias_for(run, inst)
        filter_card = run.tradability.get(inst)
        active_cards.append({
            "symbol": inst,
            "name": display_label(inst),
            "platform": platform_symbol(inst),
            "platform_differs": platform_symbol(inst) != inst,
            "bias": (bias.bias if bias else "no bias yet").lower(),
            "conviction": bias.conviction if bias else 0,
            "conviction_class": _conviction_class(bias.conviction if bias else 0),
            "priority": bias.priority if bias else "",
            "priority_class": _priority_class(bias.priority if bias else ""),
            "timeframe": bias.timeframe if bias else "",
            "verdict": filter_card.verdict if filter_card else "",
            "verdict_class": {
                "tradable_now": "tradable",
                "watch": "watch",
                "pass_despite_bias": "passed",
            }.get(filter_card.verdict if filter_card else "", "neutral"),
            "verdict_label": _verdict_label(filter_card.verdict) if filter_card else "no filter",
        })

    # Wider watchlist split by conviction
    context = sorted(
        [b for b in run.instrument_biases if b.instrument not in ACTIVE_UNIVERSE],
        key=lambda b: -b.conviction,
    )
    high_conv = [b for b in context if b.conviction >= CONTEXT_CONVICTION_THRESHOLD]
    low_conv = [b for b in context if b.conviction < CONTEXT_CONVICTION_THRESHOLD]

    def _ctx_card(b: InstrumentBias) -> dict:
        plat = platform_symbol(b.instrument)
        return {
            "symbol": b.instrument,
            "name": display_label(b.instrument),
            "platform": plat,
            "platform_differs": plat != b.instrument,
            "bias": b.bias,
            "conviction": b.conviction,
            "conviction_class": _conviction_class(b.conviction),
        }

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "run_date": date,
            "runs": runs,
            "run": run,
            "hero": hero,
            "active_cards": active_cards,
            "context_high": [_ctx_card(b) for b in high_conv],
            "context_low": [_ctx_card(b) for b in low_conv],
            "context_low_summary": " · ".join(
                f"{b.instrument} {b.conviction}/10" for b in low_conv
            ),
            "by_verdict": {
                "tradable": [
                    {
                        "symbol": c.instrument,
                        "name": display_label(c.instrument),
                        "raw": c.raw,
                    }
                    for c in by_verdict["tradable"]
                ],
                "watch": [
                    {
                        "symbol": c.instrument,
                        "name": display_label(c.instrument),
                        "raw": c.raw,
                    }
                    for c in by_verdict["watch"]
                ],
                "passed": [
                    {
                        "symbol": c.instrument,
                        "name": display_label(c.instrument),
                        "raw": c.raw,
                    }
                    for c in by_verdict["passed"]
                ],
            },
            "council_instruments": sorted(run.council.keys()),
            "instrument_biases": sorted(
                run.instrument_biases,
                key=lambda b: ({"A+": 0, "A": 1, "B": 2, "C": 3}.get(b.priority, 4),
                               -b.conviction),
            ),
            "personas": [
                {"key": "default", "label": "Default analyst"},
                {"key": "druckenmiller", "label": "Stanley Druckenmiller"},
                {"key": "dalio", "label": "Ray Dalio"},
                {"key": "soros", "label": "George Soros"},
                {"key": "marks", "label": "Howard Marks"},
                {"key": "buffett", "label": "Warren Buffett"},
            ],
            "active_universe": ACTIVE_UNIVERSE,
            "render_time": datetime.now().strftime("%H:%M:%S"),
            "_display_helpers": {
                "display_name": display_name,
                "display_label": display_label,
                "platform_symbol": platform_symbol,
            },
        },
    )


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
        "\n## Tradability Filter results\n",
    ])
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


# ---------- API: manual run trigger ----------

@app.post("/api/run")
async def api_run():
    if _is_run_alive(_run_state["pid"]):
        return JSONResponse({
            "status": "already_running",
            "pid": _run_state["pid"],
            "started_at": _run_state["started_at"].isoformat() if _run_state["started_at"] else None,
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
    """Find the most recent stage start line in the log."""
    stage_label = "Starting…"
    instrument: str | None = None
    agent: str | None = None
    last_event_line: str | None = None
    # walk backward through log; first matching event wins
    for ln in reversed(log_tail):
        if not last_event_line and "[info" in ln:
            last_event_line = ln
        for marker, label in _STAGES:
            if marker in ln:
                stage_label = label
                # try pull instrument= from same line
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
    pid = _run_state["pid"]
    started = _run_state["started_at"]

    # Always include "latest completed run" so the UI can show timestamp
    latest = _latest_run_meta()

    if not pid:
        return JSONResponse({"running": False, "latest": latest})

    alive = _is_run_alive(pid)
    if not alive:
        _run_state["pid"] = None
        return JSONResponse({"running": False, "pid": pid, "latest": latest})

    elapsed_s = int((datetime.now() - started).total_seconds()) if started else 0
    stage_info = _detect_current_stage(_read_log_tail(200))

    # Estimate progress (rough). Pipeline avg ~12 min = 720s.
    est_total = 900
    pct = min(95, int(elapsed_s / est_total * 100))

    return JSONResponse({
        "running": True,
        "pid": pid,
        "started_at": started.isoformat() if started else None,
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
    _md.reset()
    return _md.convert(text)


templates.env.filters["markdown"] = _render_markdown
