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

## To do (manual steps)

- [ ] Sign up at [render.com](https://render.com) and connect GitHub account
- [ ] Create Web Service — select `nam-hedgefund` repo (auto-detects render.yaml)
- [ ] Set Render env var: `ADMIN_TOKEN` (pick a strong password for /admin panel)
- [ ] Add custom domain in Render — Settings > Custom Domains > `piptheory.com`
- [ ] Point DNS — set CNAME record at domain registrar to the value Render gives you
- [ ] Sign up for [Google Analytics](https://analytics.google.com) — create property for piptheory.com
- [ ] Set Render env var: `GA_MEASUREMENT_ID` = your GA4 `G-XXXXXXXXXX` ID
- [ ] Run local pipeline then push state: `.\scripts\push_state.ps1`
- [ ] Verify site is live at piptheory.com
- [ ] Apply for [AdSense](https://adsense.google.com) once you have traffic
- [ ] Replace placeholder ad slots with real AdSense code
- [ ] (Optional) Rename GitHub repo from `nam-hedgefund` to `piptheory`
