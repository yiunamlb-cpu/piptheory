"""CSS injection for the dashboard. Implements the design tokens from
design MDS/ — Perplexity-style monochromatic light theme.

Key tokens (from design MDS/DESIGN.md):
  - Inkwell #000000 — primary text, active states
  - Paper White #FFFFFF — page background
  - Parchment #FAF8F5 — interactive surfaces (search, active nav)
  - Graphite #27251E — secondary text, borders (note: source had #27251 typo)
  - Faded Stone #92918B — placeholder text, low contrast
  - Dusk Gray #72706B — tertiary text, dividers
  - Font: pplxSans (Inter as substitute), 400/500, 12/14/16px
  - Radii: cards 16px, inputs 8px, buttons 9999px (pill), nav 8px
  - Spacing: 4px base, compact density
"""
from __future__ import annotations

import streamlit as st


CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
:root {
  --color-inkwell: #000000;
  --color-paper-white: #FFFFFF;
  --color-parchment: #FAF8F5;
  --color-graphite: #27251E;
  --color-faded-stone: #92918B;
  --color-dusk-gray: #72706B;
  --color-divider: #EDEAE5;

  --font-sans: 'Inter', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;

  --text-caption: 12px;
  --text-body-sm: 14px;
  --text-body: 16px;
  --leading: 1.5;

  --radius-card: 16px;
  --radius-input: 8px;
  --radius-pill: 9999px;
  --radius-nav: 8px;

  --space-4: 4px;
  --space-8: 8px;
  --space-12: 12px;
  --space-16: 16px;
  --space-32: 32px;
}

html, body, [class*="css"] {
  font-family: var(--font-sans) !important;
  color: var(--color-inkwell);
  background: var(--color-paper-white);
}

.main, .block-container, [data-testid="stAppViewContainer"] {
  background: var(--color-paper-white);
}

[data-testid="stSidebar"] {
  background: var(--color-paper-white);
  border-right: 1px solid var(--color-divider);
}

[data-testid="stSidebar"] .block-container {
  padding-top: var(--space-32);
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-sans) !important;
  color: var(--color-inkwell) !important;
  font-weight: 500 !important;
  letter-spacing: -0.01em;
}

h1 { font-size: 24px !important; line-height: 1.3 !important; margin: 0 0 var(--space-16) 0 !important; }
h2 { font-size: 18px !important; line-height: 1.4 !important; margin: var(--space-32) 0 var(--space-16) 0 !important; }
h3 { font-size: 16px !important; line-height: 1.5 !important; margin: var(--space-16) 0 var(--space-8) 0 !important; }
h4 { font-size: 14px !important; line-height: 1.5 !important; }

p, li, .stMarkdown {
  font-size: var(--text-body) !important;
  line-height: var(--leading) !important;
  color: var(--color-inkwell);
}

.caption { font-size: var(--text-caption); color: var(--color-faded-stone); }
.body-sm { font-size: var(--text-body-sm); }

/* Streamlit's default link color is bright blue. Force monochrome. */
a, a:visited,
.stMarkdown a, .stMarkdown a:visited,
[data-testid="stMarkdownContainer"] a {
  color: var(--color-inkwell) !important;
  text-decoration: underline !important;
  text-underline-offset: 2px !important;
}
a:hover { text-decoration-thickness: 2px !important; }

code, pre, .stCode {
  font-family: var(--font-mono) !important;
  font-size: var(--text-body-sm) !important;
  background: var(--color-parchment) !important;
  border-radius: var(--radius-input) !important;
}

pre {
  padding: var(--space-12) !important;
  border: 1px solid var(--color-divider);
}

/* === Streamlit overrides === */

button, .stButton > button {
  border-radius: var(--radius-pill) !important;
  background: var(--color-graphite) !important;
  color: var(--color-paper-white) !important;
  border: none !important;
  font-family: var(--font-sans) !important;
  font-size: var(--text-body-sm) !important;
  font-weight: 400 !important;
  padding: 6px 16px !important;
  transition: opacity 0.15s ease;
}

.stButton > button:hover {
  background: var(--color-inkwell) !important;
  opacity: 0.95;
}

.stButton > button[kind="secondary"] {
  background: transparent !important;
  color: var(--color-faded-stone) !important;
  border: 1px solid var(--color-divider) !important;
}

[data-testid="stSelectbox"] > div > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  border-radius: var(--radius-input) !important;
  background: var(--color-parchment) !important;
  border: 1px solid var(--color-divider) !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within > div,
[data-testid="stSelectbox"] [aria-expanded="true"] {
  border-color: var(--color-inkwell) !important;
  box-shadow: none !important;
}

[data-baseweb="popover"] [role="option"][aria-selected="true"] {
  background: var(--color-parchment) !important;
  color: var(--color-inkwell) !important;
}

/* Focus rings: Streamlit defaults to blue */
*:focus-visible {
  outline: 1px solid var(--color-inkwell) !important;
  outline-offset: 2px !important;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
  border-radius: var(--radius-input) !important;
  background: var(--color-parchment) !important;
  border: 1px solid var(--color-divider) !important;
  color: var(--color-inkwell) !important;
}

/* Tabs: pill-style. Streamlit's BaseWeb tabs render text in nested <p>/<span>
   elements, so we have to drill down. */
[data-baseweb="tab-list"] {
  gap: var(--space-4) !important;
  border-bottom: none !important;
  background: transparent !important;
}

[data-baseweb="tab"] {
  border-radius: var(--radius-pill) !important;
  padding: 6px 16px !important;
  background: transparent !important;
  font-size: var(--text-body-sm) !important;
  font-weight: 400 !important;
  border: none !important;
  margin: 0 !important;
}

[data-baseweb="tab"]:hover {
  background: var(--color-parchment) !important;
}

[data-baseweb="tab"], [data-baseweb="tab"] *,
[data-baseweb="tab"] p, [data-baseweb="tab"] span {
  color: var(--color-faded-stone) !important;
  text-decoration: none !important;
}

[data-baseweb="tab"][aria-selected="true"] {
  background: var(--color-graphite) !important;
}

[data-baseweb="tab"][aria-selected="true"],
[data-baseweb="tab"][aria-selected="true"] *,
[data-baseweb="tab"][aria-selected="true"] p,
[data-baseweb="tab"][aria-selected="true"] span {
  color: var(--color-paper-white) !important;
}

[data-baseweb="tab-highlight"] {
  background: transparent !important;
  height: 0 !important;
  display: none !important;
}

[data-baseweb="tab-border"] {
  background: transparent !important;
  display: none !important;
}

[data-testid="stTabsContent"] {
  padding-top: var(--space-16) !important;
}

/* Tables */
[data-testid="stTable"] table, .stDataFrame table {
  font-family: var(--font-sans) !important;
  font-size: var(--text-body-sm) !important;
}

[data-testid="stTable"] th, .stDataFrame th {
  background: var(--color-parchment) !important;
  color: var(--color-graphite) !important;
  font-weight: 500 !important;
  text-align: left !important;
  border-bottom: 1px solid var(--color-divider) !important;
}

[data-testid="stTable"] td, .stDataFrame td {
  border-bottom: 1px solid var(--color-divider) !important;
  color: var(--color-inkwell) !important;
}

/* Expander */
[data-testid="stExpander"] {
  border: 1px solid var(--color-divider) !important;
  border-radius: var(--radius-card) !important;
  background: var(--color-paper-white) !important;
  margin-bottom: var(--space-8) !important;
}

[data-testid="stExpander"] summary {
  padding: var(--space-12) !important;
  font-weight: 500 !important;
}

/* Streamlit chrome — hide the deploy/share/menu items, but KEEP the sidebar
   collapse control so the user can re-open the sidebar after hiding it. */
#MainMenu, footer { visibility: hidden !important; }
[data-testid="stDeployButton"], .stDeployButton { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
header[data-testid="stHeader"] {
  background: transparent !important;
  height: auto !important;
}

/* Sidebar collapse / expand chevron — must remain visible.
   Style it to fit the monochrome design. */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"] {
  visibility: visible !important;
  display: flex !important;
  color: var(--color-inkwell) !important;
  background: var(--color-paper-white) !important;
  border: 1px solid var(--color-divider) !important;
  border-radius: var(--radius-input) !important;
  padding: 4px !important;
  z-index: 999 !important;
}

[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarCollapsedControl"] svg {
  fill: var(--color-inkwell) !important;
  color: var(--color-inkwell) !important;
}

[data-testid="collapsedControl"]:hover,
[data-testid="stSidebarCollapseButton"]:hover,
[data-testid="stSidebarCollapsedControl"]:hover {
  background: var(--color-parchment) !important;
}

/* === Custom components === */

.brand {
  font-family: var(--font-sans);
  font-size: 18px;
  font-weight: 500;
  letter-spacing: -0.02em;
  color: var(--color-inkwell);
  padding-bottom: var(--space-32);
  border-bottom: 1px solid var(--color-divider);
  margin-bottom: var(--space-16);
}

.brand .meta {
  display: block;
  font-size: var(--text-caption);
  color: var(--color-faded-stone);
  font-weight: 400;
  margin-top: 4px;
}

.bias-card {
  background: var(--color-paper-white);
  border: 1px solid var(--color-divider);
  border-radius: var(--radius-card);
  padding: var(--space-16);
  margin-bottom: var(--space-12);
}

.bias-card.priority-aplus { border-left: 2px solid var(--color-inkwell); }
.bias-card.priority-a { border-left: 2px solid var(--color-graphite); }
.bias-card.priority-b { border-left: 2px solid var(--color-faded-stone); }
.bias-card.priority-c { border-left: 2px solid var(--color-divider); }

.instrument {
  font-size: var(--text-body);
  font-weight: 500;
  color: var(--color-inkwell);
  display: inline-block;
}

.bias-direction {
  font-size: var(--text-body-sm);
  color: var(--color-graphite);
  margin-left: var(--space-12);
}

.chip {
  display: inline-block;
  background: var(--color-parchment);
  color: var(--color-graphite);
  border-radius: var(--radius-pill);
  padding: 2px 12px;
  font-size: var(--text-caption);
  font-weight: 400;
  margin-right: var(--space-4);
}

.chip-strong { background: var(--color-graphite); color: var(--color-paper-white); }
.chip-muted  { background: var(--color-paper-white); color: var(--color-faded-stone); border: 1px solid var(--color-divider); }

.run-meta {
  font-size: var(--text-caption);
  color: var(--color-faded-stone);
  padding: var(--space-8) var(--space-12);
  background: var(--color-parchment);
  border-radius: var(--radius-input);
  display: inline-block;
}

.section-title {
  font-size: var(--text-caption);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-faded-stone);
  font-weight: 500;
  margin: var(--space-32) 0 var(--space-8) 0;
}

.empty-state {
  padding: var(--space-32);
  text-align: center;
  color: var(--color-faded-stone);
  font-size: var(--text-body-sm);
  border: 1px dashed var(--color-divider);
  border-radius: var(--radius-card);
}
</style>
"""


def inject_css() -> None:
    """Call once at the top of the Streamlit app to apply the design system."""
    st.markdown(CSS, unsafe_allow_html=True)


def chip(text: str, variant: str = "default") -> str:
    """Return HTML for a pill chip. variant: default | strong | muted."""
    cls = {"default": "chip", "strong": "chip chip-strong", "muted": "chip chip-muted"}[variant]
    return f'<span class="{cls}">{text}</span>'
