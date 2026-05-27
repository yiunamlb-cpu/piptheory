# PIPTHEORY Launch Checklist

## Done (code side)
- [x] Dashboard rebuilt as research-desk design
- [x] Mobile-first responsive (phone / tablet / desktop)
- [x] Dark/light theme
- [x] JS charts with touch interaction
- [x] SVG favicon
- [x] Ad slot infrastructure (leaderboard, in-feed, mobile 320x50)
- [x] Adblock soft-wall detection
- [x] GA4 analytics wiring (env-var controlled)
- [x] Admin panel (login + manual sync)
- [x] Render deployment config (render.yaml, runtime.txt)
- [x] GitHub Actions keep-alive ping (every 10 min)
- [x] State sync script (scripts/push_state.ps1)
- [x] All code pushed to GitHub

## To do (manual steps) — updated 27 May 2026

- [x] Sign up at [render.com](https://render.com) and connect GitHub account
- [x] Create Web Service — select `piptheory` repo (auto-detects render.yaml)
- [ ] Set Render env var: `PIPTHEORY_ADMIN_TOKEN` (note: code uses this name, not ADMIN_TOKEN — auto-generates if not set)
- [x] Add custom domain in Render — Settings > Custom Domains > `piptheory.com` ✅ + `www.piptheory.com` redirect
- [x] Point DNS — A record `@` → `216.24.57.1` (Render IP), CNAME `www` → `@`
- [ ] Sign up for [Google Analytics](https://analytics.google.com) — create property for piptheory.com
- [ ] Set Render env var: `GA_MEASUREMENT_ID` = your GA4 `G-XXXXXXXXXX` ID
- [x] Run local pipeline then push state: `.\scripts\push_state.ps1`
- [x] Verify site is live at piptheory.com ✅ (HTTP 200, SSL issued)
- [ ] Apply for [AdSense](https://adsense.google.com) once you have traffic
- [ ] Replace placeholder ad slots with real AdSense code
- [x] Rename GitHub repo from `nam-hedgefund` to `piptheory`
- [x] GitHub Actions keep-alive cron (`*/10 * * * *`) running ✅
