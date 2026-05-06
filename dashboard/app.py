"""nam-hedgefund dashboard. Streamlit, Perplexity-style design system.

Run:
    streamlit run dashboard/app.py
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import streamlit as st

# Make `src` importable when launched via `streamlit run dashboard/app.py`
import sys
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.loader import (
    InstrumentBias,
    Run,
    list_runs,
    load_run,
)
from dashboard.style import chip, inject_css

st.set_page_config(
    page_title="nam-hedgefund",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()


# ---------------------- Sidebar ----------------------

with st.sidebar:
    st.markdown(
        '<div class="brand">nam-hedgefund'
        '<span class="meta">discretionary macro · agent stack</span></div>',
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

    st.markdown('<div class="section-title">Sections</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="caption" style="color: var(--color-faded-stone)">'
        'Use the tabs in the main panel to navigate the run.</p>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">Watchlist</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="caption" style="color: var(--color-faded-stone)">'
        'DXY · EURUSD · USDJPY · GBPUSD · AUDUSD<br>'
        'ES · NQ · GC · CL · ZN</p>',
        unsafe_allow_html=True,
    )


# ---------------------- Run loading ----------------------

run: Run | None = load_run(selected_date)
if run is None:
    st.markdown(
        '<div class="empty-state">Could not load run.</div>',
        unsafe_allow_html=True,
    )
    st.stop()


# ---------------------- Header ----------------------

cost = run.run_summary.get("total_cost_usd")
council_list = run.run_summary.get("council_instruments", []) or list(run.council.keys())

header_meta_parts: list[str] = [f"{selected_date}"]
if cost is not None:
    header_meta_parts.append(f"${cost:.4f} run cost")
if council_list:
    header_meta_parts.append(f"{len(council_list)} council instruments")

st.markdown(
    f'<div class="run-meta">{" &nbsp;·&nbsp; ".join(header_meta_parts)}</div>',
    unsafe_allow_html=True,
)
st.markdown("# Daily bias")


# ---------------------- Tabs ----------------------

tab_brief, tab_filter, tab_watchlist, tab_detail, tab_layer1, tab_raw = st.tabs(
    ["PM Brief", "Tradability", "Watchlist", "Per-instrument", "Specialists", "Raw outputs"]
)


# ---- PM Brief ----
with tab_brief:
    if run.layer5_pm_brief:
        st.markdown(run.layer5_pm_brief)
    else:
        st.markdown(
            '<div class="empty-state">No PM brief generated.<br>'
            '<span class="caption">Layer 5 only runs when at least one '
            'instrument passes the council threshold.</span></div>',
            unsafe_allow_html=True,
        )


# ---- Tradability Filter ----
with tab_filter:
    if not run.tradability:
        st.markdown(
            '<div class="empty-state">No Tradability Filter outputs yet.<br>'
            '<span class="caption">Layer 4b runs only on active-universe instruments '
            '(ES / NQ / GC) that cleared the council threshold.</span></div>',
            unsafe_allow_html=True,
        )
    else:
        # Group by verdict
        by_verdict = {"tradable_now": [], "watch": [], "pass_despite_bias": [], "other": []}
        for inst, card in run.tradability.items():
            v = card.verdict if card.verdict in by_verdict else "other"
            by_verdict[v].append(card)

        st.markdown('<div class="section-title">Setups for review</div>',
                    unsafe_allow_html=True)
        if by_verdict["tradable_now"]:
            for card in by_verdict["tradable_now"]:
                st.markdown(
                    f'<div class="bias-card priority-aplus">'
                    f'<span class="instrument">{card.instrument}</span>'
                    f'<span class="bias-direction">tradable_now — cleared structural review</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                with st.expander(f"{card.instrument} — filter detail", expanded=False):
                    st.markdown(card.raw)
        else:
            st.markdown(
                '<p class="caption" style="color: var(--color-faded-stone);">'
                'No setups are at a clean tradable location today. This is the '
                'expected output most days.</p>',
                unsafe_allow_html=True,
            )

        if by_verdict["watch"]:
            st.markdown('<div class="section-title">Watch — bias supported, location not yet tradable</div>',
                        unsafe_allow_html=True)
            for card in by_verdict["watch"]:
                with st.expander(f"{card.instrument} — watch", expanded=False):
                    st.markdown(card.raw)

        if by_verdict["pass_despite_bias"]:
            st.markdown('<div class="section-title">Passed — macro-aligned but structurally unfavorable</div>',
                        unsafe_allow_html=True)
            for card in by_verdict["pass_despite_bias"]:
                with st.expander(f"{card.instrument} — passed", expanded=False):
                    st.markdown(card.raw)

        if by_verdict["other"]:
            st.markdown('<div class="section-title">Other / unparseable</div>',
                        unsafe_allow_html=True)
            for card in by_verdict["other"]:
                with st.expander(f"{card.instrument} — {card.verdict}", expanded=False):
                    st.markdown(card.raw)


# ---- Watchlist ----
with tab_watchlist:
    if not run.instrument_biases:
        st.markdown(
            '<div class="empty-state">Strategist output not parsed.</div>',
            unsafe_allow_html=True,
        )
    else:
        # Sort by conviction descending, then priority A+ first
        priority_rank = {"A+": 0, "A": 1, "B": 2, "C": 3, "": 4}
        biases_sorted = sorted(
            run.instrument_biases,
            key=lambda b: (priority_rank.get(b.priority, 4), -b.conviction),
        )

        def priority_class(p: str) -> str:
            return {"A+": "priority-aplus", "A": "priority-a", "B": "priority-b", "C": "priority-c"}.get(p, "")

        for b in biases_sorted:
            chips_html = ""
            if b.priority:
                chips_html += chip(f"Priority {b.priority}", "strong" if b.priority in ("A+", "A") else "muted")
            if b.conviction:
                chips_html += chip(f"{b.conviction}/10")
            if b.timeframe:
                chips_html += chip(b.timeframe, "muted")

            st.markdown(
                f'<div class="bias-card {priority_class(b.priority)}">'
                f'<div><span class="instrument">{b.instrument}</span>'
                f'<span class="bias-direction">{b.bias}</span></div>'
                f'<div style="margin-top: 8px;">{chips_html}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ---- Per-instrument detail ----
with tab_detail:
    instruments = [b.instrument for b in run.instrument_biases]
    council_only = sorted(run.council.keys())
    union = list(dict.fromkeys(instruments + council_only))

    if not union:
        st.markdown(
            '<div class="empty-state">No instruments in this run.</div>',
            unsafe_allow_html=True,
        )
    else:
        col_pick, _ = st.columns([1, 3])
        with col_pick:
            pick = st.selectbox("Instrument", union, label_visibility="collapsed")

        bias_for_pick: InstrumentBias | None = next(
            (b for b in run.instrument_biases if b.instrument == pick), None
        )
        if bias_for_pick:
            chips_html = ""
            if bias_for_pick.priority:
                chips_html += chip(f"Priority {bias_for_pick.priority}",
                                   "strong" if bias_for_pick.priority in ("A+", "A") else "muted")
            if bias_for_pick.conviction:
                chips_html += chip(f"Conviction {bias_for_pick.conviction}/10")
            if bias_for_pick.timeframe:
                chips_html += chip(bias_for_pick.timeframe, "muted")

            st.markdown(
                f'<div class="bias-card">'
                f'<div><span class="instrument">{pick}</span>'
                f'<span class="bias-direction">{bias_for_pick.bias}</span></div>'
                f'<div style="margin-top: 8px;">{chips_html}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            with st.expander("Strategist bias card (raw)", expanded=False):
                st.markdown(bias_for_pick.raw_section)

        # Council debate
        co = run.council.get(pick)
        if co:
            st.markdown('<div class="section-title">Bias Council debate</div>',
                        unsafe_allow_html=True)
            with st.expander("Bull Advocate", expanded=False):
                st.markdown(co.bull or "_no output_")
            with st.expander("Bear Advocate", expanded=False):
                st.markdown(co.bear or "_no output_")
            with st.expander("Judge — final bias", expanded=True):
                st.markdown(co.judge or "_no output_")
        else:
            st.markdown(
                '<p class="caption" style="color: var(--color-faded-stone); margin-top: 16px;">'
                'No Bias Council debate for this instrument '
                '(below conviction threshold or excluded from the run).</p>',
                unsafe_allow_html=True,
            )


# ---- Specialists ----
with tab_layer1:
    with st.expander("Inflation Tracker", expanded=False):
        st.markdown(run.layer1_inflation or "_no output_")
    with st.expander("Positioning Analyst", expanded=False):
        st.markdown(run.layer1_positioning or "_no output_")
    with st.expander("Fed-Watcher", expanded=False):
        st.markdown(run.layer1_fed or "_no output_")


# ---- Raw outputs ----
with tab_raw:
    st.markdown('<div class="section-title">Layer 2 — Strategist (full)</div>',
                unsafe_allow_html=True)
    with st.expander("Open", expanded=False):
        st.markdown(run.layer2_strategist or "_no output_")

    st.markdown('<div class="section-title">Layer 3 — Contrarian (full)</div>',
                unsafe_allow_html=True)
    with st.expander("Open", expanded=False):
        st.markdown(run.layer3_contrarian or "_no output_")

    if run.run_summary:
        st.markdown('<div class="section-title">Run summary</div>',
                    unsafe_allow_html=True)
        st.json(run.run_summary)


# ---------------------- Footer ----------------------

st.markdown(
    f'<p class="caption" style="text-align: center; '
    f'color: var(--color-faded-stone); margin-top: 64px;">'
    f'Rendered {datetime.now().strftime("%H:%M:%S")} · '
    f'private research · not investment advice</p>',
    unsafe_allow_html=True,
)
