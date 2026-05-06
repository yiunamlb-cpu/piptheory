"""Dashboard CSS injection.

Aesthetic: light, friendly, decision-support oriented. Uses purposeful color
for verdict status (green/amber/gray) so categorisation is glanceable. Card-
heavy layout with soft shadows. Inter for type. Aimed at being readable and
fast to scan, not clinical or playful.

Color philosophy: most surfaces are neutral warm-gray. Accent color appears
only where status matters: tradable_now (emerald), watch (amber), pass
(stone). Conviction and priority stay neutral.
"""
from __future__ import annotations

import streamlit as st


CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
:root {
  /* === Surfaces === */
  --bg: #FAFAF9;
  --surface: #FFFFFF;
  --surface-muted: #F5F5F4;
  --border: #E7E5E4;
  --border-strong: #D6D3D1;

  /* === Text === */
  --text-primary: #0C0A09;
  --text-secondary: #57534E;
  --text-tertiary: #A8A29E;

  /* === Brand accent (used persistently across the UI) === */
  --brand: #0D9488;                    /* teal 600 — distinctive, finance-friendly */
  --brand-tint: #F0FDFA;               /* teal 50 */
  --brand-border: #99F6E4;             /* teal 200 */
  --brand-strong: #115E59;             /* teal 800 */

  /* === Status accents (verdict-coded; used sparingly) === */
  --status-tradable: #059669;          /* emerald 600 */
  --status-tradable-tint: #ECFDF5;     /* emerald 50 */
  --status-tradable-border: #A7F3D0;   /* emerald 200 */

  --status-watch: #D97706;             /* amber 600 */
  --status-watch-tint: #FFFBEB;        /* amber 50 */
  --status-watch-border: #FCD34D;      /* amber 300 */

  --status-pass: #78716C;              /* stone 500 */
  --status-pass-tint: #F5F5F4;         /* stone 100 */
  --status-pass-border: #D6D3D1;       /* stone 300 */

  /* === Priority colors (for A+ / A / B / C badges) === */
  --priority-aplus: #0D9488;           /* teal — top tier */
  --priority-aplus-tint: #F0FDFA;
  --priority-a: #059669;               /* emerald */
  --priority-a-tint: #ECFDF5;
  --priority-b: #D97706;               /* amber */
  --priority-b-tint: #FFFBEB;
  --priority-c: #78716C;               /* stone */
  --priority-c-tint: #F5F5F4;

  /* === Type === */
  --font-sans: 'Inter', ui-sans-serif, system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;

  /* === Sizing === */
  --radius-card: 12px;
  --radius-input: 8px;
  --radius-pill: 9999px;
  --radius-sm: 6px;

  --shadow-sm: 0 1px 2px rgba(12, 10, 9, 0.04);
  --shadow-md: 0 1px 3px rgba(12, 10, 9, 0.04), 0 4px 12px rgba(12, 10, 9, 0.04);

  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
}

/* === Base === */

html, body, [class*="css"], [data-testid="stAppViewContainer"], .main {
  font-family: var(--font-sans) !important;
  color: var(--text-primary);
  background: var(--bg) !important;
  -webkit-font-smoothing: antialiased;
  /* Prevent horizontal page scroll on mobile from any one rogue element */
  overflow-x: hidden !important;
}

/* Force long content to wrap rather than overflow horizontally */
.surface-card, .stMarkdown, [data-testid="stMarkdownContainer"],
.hero, .inst-card, .empty-state {
  word-wrap: break-word;
  overflow-wrap: break-word;
  word-break: break-word;
  max-width: 100%;
}

/* Tables and pre/code blocks: scroll horizontally inside their own container
   instead of pushing the page wide */
.stDataFrame, [data-testid="stTable"], pre {
  overflow-x: auto !important;
  max-width: 100% !important;
}

.block-container {
  padding-top: var(--space-6) !important;
  padding-bottom: var(--space-12) !important;
  max-width: 1200px !important;
}

[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] .block-container {
  padding-top: var(--space-6);
}

h1, h2, h3, h4, h5 {
  font-family: var(--font-sans) !important;
  color: var(--text-primary) !important;
  font-weight: 600 !important;
  letter-spacing: -0.015em;
  margin: 0;
}

h1 { font-size: 28px !important; line-height: 1.25 !important; }
h2 { font-size: 20px !important; line-height: 1.35 !important; margin-top: var(--space-8) !important; margin-bottom: var(--space-3) !important; }
h3 { font-size: 16px !important; line-height: 1.4 !important; font-weight: 600 !important; margin-top: var(--space-4) !important; margin-bottom: var(--space-2) !important; }
h4 { font-size: 14px !important; line-height: 1.4 !important; font-weight: 500 !important; }

p, li, .stMarkdown {
  font-size: 15px !important;
  line-height: 1.6 !important;
  color: var(--text-primary);
}

a, a:visited, .stMarkdown a, [data-testid="stMarkdownContainer"] a {
  color: var(--text-primary) !important;
  text-decoration: underline !important;
  text-underline-offset: 3px !important;
  text-decoration-color: var(--border-strong) !important;
}
a:hover { text-decoration-color: var(--text-primary) !important; }

code, pre {
  font-family: var(--font-mono) !important;
  font-size: 13px !important;
  background: var(--surface-muted) !important;
  border-radius: var(--radius-sm) !important;
}

pre {
  padding: var(--space-3) !important;
  border: 1px solid var(--border) !important;
}

/* === Streamlit chrome === */

#MainMenu, footer { visibility: hidden !important; }
[data-testid="stDeployButton"], .stDeployButton, [data-testid="stStatusWidget"] {
  display: none !important;
}
header[data-testid="stHeader"] {
  background: transparent !important;
  height: auto !important;
}

/* Sidebar collapse / expand controls — must stay visible regardless of state.
   Streamlit changes selectors across versions and on mobile, so we cast a
   wide net. */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
button[kind="header"],
button[data-testid*="ollapse"],
button[data-testid*="ollapsed"],
[data-testid*="SidebarNav"] button {
  visibility: visible !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  color: var(--text-primary) !important;
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  padding: 6px !important;
  box-shadow: var(--shadow-sm);
  z-index: 9999 !important;
  opacity: 1 !important;
}
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapseButton"] svg,
button[kind="header"] svg {
  fill: var(--text-primary) !important;
  stroke: var(--text-primary) !important;
  width: 18px !important;
  height: 18px !important;
}

/* Mobile: ensure the sidebar collapse handle is anchored top-left and tappable */
@media (max-width: 768px) {
  [data-testid="collapsedControl"] {
    position: fixed !important;
    top: 8px !important;
    left: 8px !important;
    width: 36px !important;
    height: 36px !important;
    z-index: 10000 !important;
  }
}

/* === Buttons === */

.stButton > button {
  border-radius: var(--radius-input) !important;
  background: var(--text-primary) !important;
  color: var(--surface) !important;
  border: none !important;
  font-family: var(--font-sans) !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  padding: 8px 14px !important;
  box-shadow: var(--shadow-sm);
  transition: opacity 0.15s ease;
}
.stButton > button:hover { opacity: 0.92; }

.stButton > button[kind="secondary"] {
  background: var(--surface) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-strong) !important;
}

/* === Inputs === */

[data-testid="stSelectbox"] > div > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stTextInput"] input {
  border-radius: var(--radius-input) !important;
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  color: var(--text-primary) !important;
  font-size: 14px !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within > div {
  border-color: var(--text-primary) !important;
  box-shadow: 0 0 0 3px rgba(12, 10, 9, 0.06) !important;
}

*:focus-visible {
  outline: 2px solid var(--text-primary) !important;
  outline-offset: 2px !important;
}

/* === Tabs === */

[data-baseweb="tab-list"] {
  gap: var(--space-1) !important;
  border-bottom: 1px solid var(--border) !important;
  padding-bottom: 0 !important;
  background: transparent !important;
}
[data-baseweb="tab"] {
  background: transparent !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0 !important;
  padding: 10px 16px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
}
[data-baseweb="tab"], [data-baseweb="tab"] *,
[data-baseweb="tab"] p, [data-baseweb="tab"] span {
  color: var(--text-secondary) !important;
}
[data-baseweb="tab"]:hover {
  background: var(--surface-muted) !important;
}
[data-baseweb="tab"][aria-selected="true"] {
  border-bottom-color: var(--text-primary) !important;
}
[data-baseweb="tab"][aria-selected="true"], [data-baseweb="tab"][aria-selected="true"] *,
[data-baseweb="tab"][aria-selected="true"] p, [data-baseweb="tab"][aria-selected="true"] span {
  color: var(--text-primary) !important;
}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {
  display: none !important;
}

/* === Tables === */

[data-testid="stTable"] table, .stDataFrame table {
  font-family: var(--font-sans) !important;
  font-size: 14px !important;
  border-radius: var(--radius-card) !important;
  overflow: hidden;
}
[data-testid="stTable"] th, .stDataFrame th {
  background: var(--surface-muted) !important;
  color: var(--text-secondary) !important;
  font-weight: 500 !important;
  text-align: left !important;
  border-bottom: 1px solid var(--border) !important;
  font-size: 13px !important;
}
[data-testid="stTable"] td, .stDataFrame td {
  border-bottom: 1px solid var(--border) !important;
  color: var(--text-primary) !important;
}

/* === Expanders === */

[data-testid="stExpander"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-card) !important;
  background: var(--surface) !important;
  margin-bottom: var(--space-2) !important;
  box-shadow: var(--shadow-sm);
}
[data-testid="stExpander"] summary {
  padding: var(--space-3) var(--space-4) !important;
  font-weight: 500 !important;
  font-size: 14px !important;
}

/* ============================================
   CUSTOM COMPONENTS
   ============================================ */

.brand {
  font-family: var(--font-sans);
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: var(--text-primary);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--border);
  margin-bottom: var(--space-4);
  position: relative;
}
.brand::before {
  content: "";
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 2px;
  background: var(--brand);
  margin-right: 8px;
  transform: translateY(-2px);
}
.brand .meta {
  display: block;
  font-size: 12px;
  color: var(--text-tertiary);
  font-weight: 400;
  margin-top: 4px;
  margin-left: 16px;
  letter-spacing: 0;
}

.section-title {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--brand);
  font-weight: 600;
  margin: var(--space-6) 0 var(--space-3) 0;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.section-title::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--border);
  display: block;
  width: 40px;
}

/* === Hero status card === */
.hero {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-card);
  padding: var(--space-6);
  box-shadow: var(--shadow-md);
  margin-bottom: var(--space-6);
}
.hero-eyebrow {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--brand);
  margin-bottom: var(--space-2);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.hero-eyebrow::before {
  content: "";
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--brand);
}
.hero-headline {
  font-size: 28px;
  line-height: 1.2;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}
.hero-subline {
  font-size: 15px;
  color: var(--text-secondary);
  line-height: 1.5;
}
.hero.tradable {
  border-left: 4px solid var(--status-tradable);
  background: linear-gradient(to right, var(--status-tradable-tint), var(--surface) 60%);
}
.hero.standby {
  border-left: 4px solid var(--brand);
  background: linear-gradient(to right, var(--brand-tint), var(--surface) 60%);
}

/* === Status pill === */
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.01em;
  border: 1px solid;
}
.status-pill::before {
  content: "";
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}
.status-pill.tradable {
  color: var(--status-tradable);
  background: var(--status-tradable-tint);
  border-color: var(--status-tradable-border);
}
.status-pill.watch {
  color: var(--status-watch);
  background: var(--status-watch-tint);
  border-color: var(--status-watch-border);
}
.status-pill.pass {
  color: var(--status-pass);
  background: var(--status-pass-tint);
  border-color: var(--status-pass-border);
}
.status-pill.neutral {
  color: var(--text-secondary);
  background: var(--surface-muted);
  border-color: var(--border);
}

/* === Instrument card === */
.inst-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-card);
  padding: var(--space-4);
  box-shadow: var(--shadow-sm);
  height: 100%;
  transition: box-shadow 0.15s ease;
}
.inst-card:hover {
  box-shadow: var(--shadow-md);
}
.inst-card.tradable { border-color: var(--status-tradable-border); }
.inst-card.watch { border-color: var(--status-watch-border); }
.inst-card.pass { border-color: var(--status-pass-border); }

.inst-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}
.inst-card-symbol {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--text-primary);
}
.inst-card-direction {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
  text-transform: capitalize;
}
.inst-card-conviction {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--text-tertiary);
}
.inst-card-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-top: 1px solid var(--border);
  font-size: 13px;
}
.inst-card-row .label {
  color: var(--text-tertiary);
}
.inst-card-row .value {
  font-family: var(--font-mono);
  color: var(--text-primary);
  font-weight: 500;
}

/* === Generic surface card === */
.surface-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-card);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-3);
}

/* === Empty state === */
.empty-state {
  padding: var(--space-8);
  text-align: center;
  color: var(--text-tertiary);
  font-size: 14px;
  border: 1px dashed var(--border);
  border-radius: var(--radius-card);
  background: var(--surface);
}

/* ============================================
   MOBILE / SMALL-SCREEN OPTIMIZATIONS
   ============================================ */
@media (max-width: 768px) {
  .block-container {
    padding-left: var(--space-3) !important;
    padding-right: var(--space-3) !important;
    padding-top: var(--space-3) !important;
  }

  h1 { font-size: 22px !important; line-height: 1.2 !important; }
  h2 { font-size: 17px !important; margin-top: var(--space-5) !important; }
  h3 { font-size: 15px !important; }
  p, li, .stMarkdown { font-size: 14px !important; }

  /* Hero card — slimmer */
  .hero {
    padding: var(--space-4);
    margin-bottom: var(--space-4);
  }
  .hero-headline { font-size: 20px; line-height: 1.25; }
  .hero-subline { font-size: 14px; }
  .hero-eyebrow { font-size: 10px; letter-spacing: 0.1em; }

  /* Section titles — keep short trail */
  .section-title { font-size: 10px; }
  .section-title::after { width: 24px; }

  /* Active universe cards — stacked by Streamlit default; tighten spacing */
  .inst-card {
    padding: var(--space-3);
    margin-bottom: var(--space-2);
  }
  .inst-card-symbol { font-size: 16px; }
  .inst-card-direction { font-size: 12px; }
  .inst-card-header {
    flex-wrap: wrap;
    gap: 6px;
  }
  .inst-card-row { font-size: 12px; padding: 5px 0; }

  /* Tabs — bigger tap targets, smaller font */
  [data-baseweb="tab"] {
    padding: 10px 12px !important;
    font-size: 13px !important;
  }
  [data-baseweb="tab-list"] {
    overflow-x: auto !important;
    flex-wrap: nowrap !important;
    -webkit-overflow-scrolling: touch;
  }

  /* Status pills — slightly larger to be tappable */
  .status-pill {
    font-size: 11px;
    padding: 5px 10px;
  }

  .priority-badge {
    font-size: 10px;
    padding: 3px 7px;
  }

  /* Surface card padding */
  .surface-card { padding: var(--space-4); }

  /* Run meta strip — compact */
  .run-meta {
    font-size: 11px;
    padding: 5px 10px;
  }

  /* Sidebar — keep narrow when expanded on phone */
  [data-testid="stSidebar"] {
    min-width: 240px !important;
  }

  /* Brand mark — slightly smaller */
  .brand { font-size: 15px; }

  /* Empty states should stay readable */
  .empty-state {
    padding: var(--space-5);
    font-size: 13px;
  }

  /* Tables get hard to read on phones; ensure they wrap */
  [data-testid="stTable"], .stDataFrame {
    font-size: 12px !important;
  }

  /* Make pre/code blocks scroll horizontally rather than overflow */
  pre {
    overflow-x: auto !important;
    font-size: 11px !important;
  }
}

/* Very small phones (<= 400px wide) — hero takes more breathing room */
@media (max-width: 400px) {
  .hero-headline { font-size: 18px; }
  h1 { font-size: 20px !important; }
  .inst-card-header {
    flex-direction: column !important;
    align-items: flex-start !important;
  }
}

/* === Run meta strip === */
.run-meta {
  display: inline-flex;
  align-items: center;
  gap: var(--space-3);
  font-size: 12px;
  color: var(--brand-strong);
  padding: 6px 14px;
  background: var(--brand-tint);
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-pill);
  font-family: var(--font-mono);
  margin-bottom: var(--space-4);
  font-weight: 500;
}

/* === Priority badges (color-coded by tier) === */
.priority-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
  font-family: var(--font-mono);
  border: 1px solid;
}
.priority-badge.aplus {
  color: var(--priority-aplus);
  background: var(--priority-aplus-tint);
  border-color: var(--priority-aplus);
}
.priority-badge.a {
  color: var(--priority-a);
  background: var(--priority-a-tint);
  border-color: var(--priority-a);
}
.priority-badge.b {
  color: var(--priority-b);
  background: var(--priority-b-tint);
  border-color: var(--priority-b);
}
.priority-badge.c {
  color: var(--priority-c);
  background: var(--priority-c-tint);
  border-color: var(--priority-c);
}

/* === Conviction indicator (subtle color by intensity) === */
.conviction {
  font-family: var(--font-mono);
  font-weight: 600;
  font-size: 13px;
}
.conviction.high { color: var(--brand-strong); }    /* 7-10 */
.conviction.med  { color: var(--text-secondary); }   /* 4-6 */
.conviction.low  { color: var(--text-tertiary); }    /* 1-3 */
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def status_pill(text: str, status: str) -> str:
    """Return HTML for a status pill. status: tradable | watch | pass | neutral."""
    cls = status if status in ("tradable", "watch", "pass", "neutral") else "neutral"
    return f'<span class="status-pill {cls}">{text}</span>'
