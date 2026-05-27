# PIPTHEORY — Project Instructions

> This file is the single source of truth for all AI coding assistants and human contributors.
> Tool-specific files (CLAUDE.md, .cursorrules, .github/copilot-instructions.md) reference this.

## CRITICAL: Multi-Device Workflow

This project is worked on from **multiple devices and locations**. Before doing ANY work:

1. **Pull first**: `git pull origin main` — always sync before making changes
2. **Work**: make your changes
3. **Commit + push**: commit with clear messages and `git push origin main` when done
4. **Never leave uncommitted work** — another device may start a session at any time

If there are merge conflicts, resolve them carefully and never discard remote changes without checking.

## Project Overview

**PIPTHEORY** (piptheory.com) is a free, public-facing daily macro research website.

- **Stack**: Python 3.11, FastAPI, Jinja2 templates, vanilla JS, CSS custom properties
- **Hosting**: Render.com (free tier), auto-deploys from GitHub on push
- **Keep-alive**: GitHub Actions pings every 10 min to prevent cold starts
- **Pipeline**: Runs locally, generates analysis data → `scripts/push_state.ps1` pushes state to GitHub → triggers Render redeploy
- **Repo**: github.com/yiunamlb-cpu/piptheory (main branch)

## Architecture

```
app/
  main.py              — FastAPI routes, template rendering (~1500 lines)
  templates/
    dashboard_tv.html  — Main public dashboard (TradingView-style)
    admin_login.html   — Admin auth page
    admin_dashboard.html — Admin manual sync panel
    about.html         — /about methodology page
    base.html          — Base template for non-dashboard pages
  static/
    dashboard.css      — All styles (light/dark theme, responsive breakpoints)
    favicon.svg        — Vector favicon
    logo-text.png      — Full logo with text
src/
  data/score_history.py — Score history storage (state/score_history.json)
  data/thesis_tracker.py — Thesis tracking (state/thesis_tracker.json)
  config.py            — STATE_DIR, ROOT paths
agents/                — LLM agent prompt templates
scripts/
  push_state.ps1       — Post-pipeline: commits safe state files + pushes to GitHub
state/                 — Runtime data (gitignored except score_history.json, thesis_tracker.json)
```

## Key Design Decisions

- **Public site is READ-ONLY** — no user accounts, no manual analytics, no personal data
- **Never expose model names** on any public-facing surface
- **Never mention AI or agents** in public copy — say "structured debate", "multi-round analysis" etc.
- **Color palette**: Bull `#3BE8B0`, Bear `#FD636B`, Accent `#1BAFD0`, Amber `#FFB900`
- **Dark theme**: Uses `[data-theme="dark"]` CSS selector, toggled via JS
- **Charts**: JS-rendered SVG (not server-side) to avoid scaling distortion
- **Mobile**: Dedicated breakpoints at 767px (tablet portrait) and 479px (phone)
- **Ads**: Placeholder slots ready for AdSense — leaderboard 728x90, in-feed native, mobile 320x50
- **Admin access**: Protected by ADMIN_TOKEN env var, not available to public

## Environment Variables (on Render)

- `ADMIN_TOKEN` — Password for /admin panel
- `GA_MEASUREMENT_ID` — Google Analytics 4 ID (e.g. G-XXXXXXXXXX)
- `OPENROUTER_API_KEY` — Only if running pipeline on Render (currently runs locally)
- `FRED_API_KEY` — Only if running pipeline on Render

## State Files

The dashboard reads from `state/` directory:
- `score_history.json` — Conviction scores per instrument (max 60 entries each, ~54KB)
- `thesis_tracker.json` — Thesis status tracking

These are the only state files committed to the repo (via .gitignore exceptions).
Sensitive files (`admin_token.txt`, `positions.json`, `daily_spend.json`) remain gitignored.

## Launch Checklist

See `TODO.md` for the current launch status and remaining manual steps.
