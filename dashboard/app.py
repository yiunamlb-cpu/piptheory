"""nam-hedgefund dashboard.

Single-page-first: opens to today's brief with a status hero + active universe
(ES / NQ / GC) status cards. Less tab-driven, more glanceable. Deep-dive
content (full watchlist, specialists, raw outputs) lives behind a single
'Inspect' tab so the daily flow is uncluttered.

Run:
    streamlit run dashboard/app.py
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.loader import (
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
from dashboard.style import inject_css, status_pill

# Active universe (matches ACTIVE_UNIVERSE in src/orchestration/pipeline.py)
ACTIVE_UNIVERSE = ["ES", "NQ", "GC"]


st.set_page_config(
    page_title="nam-hedgefund",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()


# ========================== Sidebar ==========================

with st.sidebar:
    st.markdown(
        '<div class="brand">nam-hedgefund'
        '<span class="meta">discretionary macro · decision support</span></div>',
        unsafe_allow_html=True,
    )

    runs = list_runs()
    if not runs:
        st.markdown(
            '<div class="empty-state">No runs yet.<br>'
            'Execute <code>scripts/run_bias_engine.py</code> to populate.</div>',
            unsafe_allow_html=True,
        )
        st.stop()

    selected_date = st.selectbox(
        "Run date",
        runs,
        index=0,
        label_visibility="collapsed",
    )

    st.markdown(
        '<p style="font-size:12px; color: var(--text-tertiary); margin-top: 24px; line-height: 1.5;">'
        'This is a decision-support tool. It does not place orders, size positions, '
        'or manage trades. Read the brief, decide, trade manually.</p>',
        unsafe_allow_html=True,
    )


# ========================== Run loading ==========================

run: Run | None = load_run(selected_date)
if run is None:
    st.markdown('<div class="empty-state">Could not load run.</div>',
                unsafe_allow_html=True)
    st.stop()


# ========================== Helpers ==========================

def _bias_for(instrument: str) -> InstrumentBias | None:
    return next((b for b in run.instrument_biases if b.instrument == instrument), None)


def _filter_status(verdict: str) -> str:
    """Map filter verdict to status pill class."""
    return {
        "tradable_now": "tradable",
        "watch": "watch",
        "pass_despite_bias": "pass",
    }.get(verdict, "neutral")


def _verdict_label(verdict: str) -> str:
    return {
        "tradable_now": "Tradable now",
        "watch": "Watch",
        "pass_despite_bias": "Passed",
        "skip_no_data": "No data",
        "unparseable": "Unparseable",
    }.get(verdict, verdict)


# Compute today's status
tradable = [c for c in run.tradability.values() if c.verdict == "tradable_now"]
watching = [c for c in run.tradability.values() if c.verdict == "watch"]
passed = [c for c in run.tradability.values() if c.verdict == "pass_despite_bias"]


# ========================== Hero status ==========================

# Run meta strip
cost = run.run_summary.get("total_cost_usd")
council_count = len(run.council)
meta_parts = [f"📅 {selected_date}"]
if cost is not None:
    meta_parts.append(f"${cost:.4f}")
if council_count:
    meta_parts.append(f"{council_count} council debates")
if run.tradability:
    meta_parts.append(f"{len(run.tradability)} filtered")

st.markdown(
    f'<div class="run-meta">{" · ".join(meta_parts)}</div>',
    unsafe_allow_html=True,
)

# Hero card content depends on whether anything is tradable_now
if tradable:
    n = len(tradable)
    # Show "GC (Gold), NQ (Nasdaq 100)" rather than just "GC, NQ"
    insts = ", ".join(f"{c.instrument} ({display_label(c.instrument)})" for c in tradable)
    hero_html = (
        f'<div class="hero tradable">'
        f'<div class="hero-eyebrow">Today\'s brief</div>'
        f'<div class="hero-headline">{n} setup{"s" if n > 1 else ""} ready: {insts}</div>'
        f'<div class="hero-subline">'
        f'These have cleared structural review. The macro view is supported and the '
        f'price location is favorable. Your call on whether to take any of them. '
        f'See the cards below for direction, levels, and invalidation.'
        f'</div></div>'
    )
elif run.tradability:
    hero_html = (
        f'<div class="hero standby">'
        f'<div class="hero-eyebrow">Today\'s brief</div>'
        f'<div class="hero-headline">Stand aside — no setups at clean locations</div>'
        f'<div class="hero-subline">'
        f'{len(watching)} on watch · {len(passed)} passed despite bias. '
        f'No instrument in the active universe is currently at a tradable price location. '
        f'This is the expected outcome on most days. Cash is a position.'
        f'</div></div>'
    )
elif run.layer5_pm_brief:
    hero_html = (
        f'<div class="hero standby">'
        f'<div class="hero-eyebrow">Today\'s brief</div>'
        f'<div class="hero-headline">PM brief available — no Tradability Filter</div>'
        f'<div class="hero-subline">'
        f'This run completed without Tradability Filter outputs. Read the brief below.'
        f'</div></div>'
    )
else:
    hero_html = (
        f'<div class="hero standby">'
        f'<div class="hero-eyebrow">Today\'s brief</div>'
        f'<div class="hero-headline">No actionable setups in the active universe</div>'
        f'<div class="hero-subline">'
        f'No instrument met the conviction threshold today. Stand aside. '
        f'Use the Inspect tab if you want to see the underlying analysis.'
        f'</div></div>'
    )

st.markdown(hero_html, unsafe_allow_html=True)


# ========================== Active universe row ==========================

st.markdown('<div class="section-title">Active universe</div>',
            unsafe_allow_html=True)

cols = st.columns(len(ACTIVE_UNIVERSE))
for col, instrument in zip(cols, ACTIVE_UNIVERSE):
    with col:
        bias = _bias_for(instrument)
        filter_card: TradabilityFilterCard | None = run.tradability.get(instrument)

        if filter_card:
            verdict = filter_card.verdict
            verdict_class = _filter_status(verdict)
        elif bias and bias.conviction:
            verdict = "context_only"
            verdict_class = "neutral"
        else:
            verdict = "no_data"
            verdict_class = "neutral"

        direction = (bias.bias if bias else "").lower() or "no bias yet"
        conviction = bias.conviction if bias else 0
        label = display_label(instrument)
        platform = platform_symbol(instrument)
        sub_label = f"{label} · MT5: {platform}" if platform != instrument else label

        rows_html = ""
        if bias and bias.conviction:
            rows_html += (
                f'<div class="inst-card-row"><span class="label">Conviction</span>'
                f'<span class="value">{bias.conviction}/10</span></div>'
            )
        if bias and bias.timeframe:
            rows_html += (
                f'<div class="inst-card-row"><span class="label">Timeframe</span>'
                f'<span class="value">{bias.timeframe}</span></div>'
            )
        if bias and bias.priority:
            rows_html += (
                f'<div class="inst-card-row"><span class="label">Priority</span>'
                f'<span class="value">{bias.priority}</span></div>'
            )

        st.markdown(
            f'<div class="inst-card {verdict_class}">'
            f'<div class="inst-card-header">'
            f'<div>'
            f'<div class="inst-card-symbol">{instrument} <span style="font-weight:400; '
            f'color: var(--text-secondary); font-size:14px; margin-left:6px;">{label}</span></div>'
            f'<div class="inst-card-direction">{sub_label} · {direction}</div>'
            f'</div>'
            f'{status_pill(_verdict_label(verdict) if filter_card else "no filter", verdict_class)}'
            f'</div>'
            f'{rows_html}'
            f'</div>',
            unsafe_allow_html=True,
        )


# ========================== Tabs (small, focused) ==========================

tab_brief, tab_filter, tab_inspect = st.tabs(["PM Brief", "Tradability detail", "Inspect"])


# ---- PM Brief ----
with tab_brief:
    if run.layer5_pm_brief:
        st.markdown('<div class="surface-card">', unsafe_allow_html=True)
        st.markdown(run.layer5_pm_brief)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="empty-state">No PM brief generated for this run.<br>'
            '<span style="font-size:12px;">Layer 5 only runs when at least one '
            'active-universe instrument passes the council threshold.</span></div>',
            unsafe_allow_html=True,
        )


# ---- Tradability detail ----
with tab_filter:
    if not run.tradability:
        st.markdown(
            '<div class="empty-state">No Tradability Filter outputs in this run.</div>',
            unsafe_allow_html=True,
        )
    else:
        if tradable:
            st.markdown('<div class="section-title">Tradable now</div>',
                        unsafe_allow_html=True)
            for card in tradable:
                with st.expander(f"{display_name(card.instrument)} — {_verdict_label(card.verdict)}",
                                 expanded=True):
                    st.markdown(card.raw)

        if watching:
            st.markdown('<div class="section-title">Watch — bias supported, location not yet tradable</div>',
                        unsafe_allow_html=True)
            for card in watching:
                with st.expander(f"{display_name(card.instrument)} — Watch", expanded=False):
                    st.markdown(card.raw)

        if passed:
            st.markdown('<div class="section-title">Passed — macro-aligned but structurally unfavorable</div>',
                        unsafe_allow_html=True)
            for card in passed:
                with st.expander(f"{display_name(card.instrument)} — Passed", expanded=False):
                    st.markdown(card.raw)


# ---- Inspect (deep-dive: everything else) ----
with tab_inspect:
    sub_tabs = st.tabs([
        "Watchlist (full)", "Per-instrument", "Specialists",
        "Strategist", "Contrarian", "Council debates",
    ])

    with sub_tabs[0]:
        if not run.instrument_biases:
            st.markdown('<div class="empty-state">Strategist output not parsed.</div>',
                        unsafe_allow_html=True)
        else:
            priority_rank = {"A+": 0, "A": 1, "B": 2, "C": 3, "": 4}
            biases_sorted = sorted(
                run.instrument_biases,
                key=lambda b: (priority_rank.get(b.priority, 4), -b.conviction),
            )
            for b in biases_sorted:
                in_active = b.instrument in ACTIVE_UNIVERSE
                badge = '<span class="status-pill neutral">Active</span>' if in_active else ""
                full_name = display_label(b.instrument)
                plat = platform_symbol(b.instrument)
                plat_part = f' · MT5: {plat}' if plat != b.instrument else ''
                st.markdown(
                    f'<div class="surface-card">'
                    f'<div style="display:flex; justify-content:space-between; align-items:center;">'
                    f'<div>'
                    f'<span style="font-size:16px; font-weight:600;">{b.instrument}</span> '
                    f'<span style="color: var(--text-secondary); font-size:13px; margin-left: 8px;">{full_name}{plat_part}</span>'
                    f'<div style="color: var(--text-secondary); font-size:14px; margin-top:4px;">{b.bias}</div>'
                    f'</div>'
                    f'<div style="display:flex; gap:8px; align-items:center;">'
                    f'<span style="font-family: var(--font-mono); font-size:13px; color: var(--text-tertiary);">'
                    f'{b.conviction}/10 · {b.priority or "—"}</span>'
                    f'{badge}'
                    f'</div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    with sub_tabs[1]:
        instruments = [b.instrument for b in run.instrument_biases]
        if not instruments:
            st.markdown('<div class="empty-state">No instruments parsed.</div>',
                        unsafe_allow_html=True)
        else:
            pick = st.selectbox(
                "Instrument",
                instruments,
                key="detail_pick",
                label_visibility="collapsed",
                format_func=display_name,
            )
            bias = _bias_for(pick)
            if bias:
                with st.expander("Strategist bias card", expanded=True):
                    st.markdown(bias.raw_section)
            co = run.council.get(pick)
            if co:
                with st.expander("Bull Advocate", expanded=False):
                    st.markdown(co.bull or "_no output_")
                with st.expander("Bear Advocate", expanded=False):
                    st.markdown(co.bear or "_no output_")
                with st.expander("Judge — final bias", expanded=False):
                    st.markdown(co.judge or "_no output_")
            tf = run.tradability.get(pick)
            if tf:
                with st.expander(f"Tradability Filter — {_verdict_label(tf.verdict)}",
                                 expanded=False):
                    st.markdown(tf.raw)

    with sub_tabs[2]:
        with st.expander("Inflation Tracker", expanded=False):
            st.markdown(run.layer1_inflation or "_no output_")
        with st.expander("Positioning Analyst", expanded=False):
            st.markdown(run.layer1_positioning or "_no output_")
        with st.expander("Fed-Watcher", expanded=False):
            st.markdown(run.layer1_fed or "_no output_")

    with sub_tabs[3]:
        if run.layer2_strategist:
            st.markdown(run.layer2_strategist)
        else:
            st.markdown('<div class="empty-state">No strategist output.</div>',
                        unsafe_allow_html=True)

    with sub_tabs[4]:
        if run.layer3_contrarian:
            st.markdown(run.layer3_contrarian)
        else:
            st.markdown('<div class="empty-state">No contrarian output.</div>',
                        unsafe_allow_html=True)

    with sub_tabs[5]:
        if not run.council:
            st.markdown('<div class="empty-state">No council debates in this run.</div>',
                        unsafe_allow_html=True)
        else:
            for instrument, co in run.council.items():
                st.markdown(f"### {display_name(instrument)}")
                with st.expander("Bull", expanded=False):
                    st.markdown(co.bull or "_no output_")
                with st.expander("Bear", expanded=False):
                    st.markdown(co.bear or "_no output_")
                with st.expander("Judge", expanded=False):
                    st.markdown(co.judge or "_no output_")


# ========================== Footer ==========================

st.markdown(
    f'<p style="text-align: center; color: var(--text-tertiary); font-size: 12px; '
    f'margin-top: 64px;">'
    f'Rendered {datetime.now().strftime("%H:%M:%S")} · private research · '
    f'not investment advice</p>',
    unsafe_allow_html=True,
)
