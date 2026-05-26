/* piptheory dashboard JS — single file, branches by surface.

   The desktop and mobile templates share API surface (run, positions, chat)
   and a small set of common widgets (run-status banner, run-now button,
   run-picker dropdown). They diverge on container UI: desktop uses a
   slide-over panel and modals; mobile uses a bottom sheet. The dispatcher
   below routes to the right one. */

(function () {
  "use strict";

  const cfg = window.__APP_CONFIG__ || {};
  const surface = cfg.surface || "desktop";

  // ─── Tiny helpers ────────────────────────────────────────────────────

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.from((root || document).querySelectorAll(sel)); }
  function escapeHTML(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }
  function lightFormat(s) {
    return escapeHTML(s)
      .replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>")
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br>");
  }
  function fmtPnl(pct) {
    if (pct === null || pct === undefined) return "—";
    const sign = pct > 0 ? "+" : "";
    return `${sign}${pct.toFixed(2)}%`;
  }
  function fmtRelativeTime(isoStr) {
    if (!isoStr) return "—";
    const t = new Date(isoStr);
    const diffMin = Math.floor((new Date() - t) / 60000);
    if (diffMin < 1) return "just now";
    if (diffMin < 60) return diffMin + " min ago";
    const diffHr = Math.floor(diffMin / 60);
    if (diffHr < 24) return diffHr + " hr ago";
    const diffDays = Math.floor(diffHr / 24);
    return diffDays + " day" + (diffDays !== 1 ? "s" : "") + " ago";
  }

  // Auto-update any element with data-relative-time="<iso>" to show a
  // human-readable relative time. Used by the public-site sync badge +
  // footer.
  function updateRelativeTimes() {
    document.querySelectorAll("[data-relative-time]").forEach((el) => {
      const iso = el.getAttribute("data-relative-time");
      if (iso) el.textContent = fmtRelativeTime(iso);
    });
  }
  updateRelativeTimes();
  setInterval(updateRelativeTimes, 60000);

  // ─── Glossary tooltips ──────────────────────────────────────────────
  // One floating tooltip element shared across the page. Triggered by
  // hover on desktop and tap on mobile. Source of truth for definitions
  // is the GLOSSARY object below — to add a new term, just add a key and
  // mark the element in the template with data-term="key".

  const GLOSSARY = {
    // Bias / verdict / state
    "tradable_now": "<strong>Tradable now.</strong> Both the macro view and the chart say go: bias direction is firm, conviction is solid, and price is at a clean structural location (pullback to 20d SMA, not extended, no near-term blocking event).",
    "watch": "<strong>Watch.</strong> Macro view supports the trade, but the chart isn't ready — price is extended, mid-range, or there's a binary event in the next 1-5 days. Wait for a cleaner setup; don't chase.",
    "skip": "<strong>Skip — chart fights the macro.</strong> Macro view says go but the chart structure is broken or extreme late-chase. Pass on this entry; re-evaluate on a fresh setup.",
    "low_conviction": "<strong>Low conviction.</strong> Macro view isn't strong enough (under 5/10) to act on. Stand aside.",
    "no_view": "<strong>No view.</strong> The system has no clear directional read on this instrument today.",

    // Strength bands
    "strength": "<strong>Strength</strong> is how strongly the research panel thinks the directional read is right. 1-10 scale. <strong>8+</strong> rare/strong, <strong>6-7</strong> solid, <strong>5</strong> weak, under 5 is noise. Wobbles 1 point day-to-day from natural variance in the analytical process — only worry on 3+ point drops or direction flips.",
    "direction": "<strong>Direction.</strong> The system's view on which way this instrument is biased — long, short, or no view. Comes from the Council's Judge after the Bull and Bear cases are debated.",
    "state": "<strong>State.</strong> What the system thinks you should do with this instrument right now: Ready (green-lit), Wait (chart not ready), Skip (chart against), or Low conviction (macro too weak).",

    // Advisor verbs (open positions)
    "advisor_hold": "<strong>Hold.</strong> Default. Thesis intact, no action needed. Most days you'll see this on most positions.",
    "advisor_review": "<strong>Review.</strong> Soft alert — macro view still aligned with the trade, but the chart has lost its clean state. No action required; just glance. Only worry if it persists for several days while P&L deteriorates.",
    "advisor_trail_stop": "<strong>Trail stop.</strong> You're nicely in profit and the view still holds. Move your structural stop up to lock in part of the gain. Don't tighten so much that normal volatility takes you out.",
    "advisor_trim": "<strong>Trim.</strong> Take some risk off. The case has weakened — conviction has dropped 3+ points since you opened, or you're in significant profit and the thesis has slipped. Sell roughly half; let the rest run.",
    "advisor_close": "<strong>Close.</strong> The system has changed its mind. Either macro view has flipped against you at 6+/10, or chart structure has materially eroded. Get out and look for a cleaner re-entry later.",
    "advisor_emergency_close": "<strong>Emergency close.</strong> Your structural stop has been breached. Close right now per the pre-defined plan — the whole point of a structural stop is you don't get to vote when price is at the level.",

    // Event relevance
    "relevance_high": "<strong>HIGH relevance.</strong> Regime-defining event — the kind that resets cross-asset positioning for days. Examples: surprise tariff announcements, hot CPI prints, FOMC decisions, geopolitical escalations. The Strategist treats these as authoritative for short-term framing.",
    "relevance_medium": "<strong>MEDIUM relevance.</strong> Thematic — confirms or modifies an existing macro theme without redefining the regime. Examples: Fed-speaker hawkish tone, ECB hint at hike timing, OPEC commentary.",
    "relevance_low": "<strong>LOW relevance.</strong> Noteworthy for context but unlikely to move the bias. Logged for completeness rather than for trading.",

    // Other terms
    "structural_stop": "<strong>Structural / emergency stop.</strong> The price level where, if hit, your macro thesis would be invalidated. Wider than a tight technical stop on purpose — it's about the thesis, not the wiggle room. Set it once on entry, use it as the line you don't argue with.",
    "atr": "<strong>ATR (Average True Range).</strong> A measure of how much an instrument moves on a typical day, averaged over 14 days. The Filter uses it to detect 'extended' moves (recent range > 2× ATR = late-chase risk).",
    "fred": "<strong>FRED.</strong> The Federal Reserve Economic Data API — source for CPI, PCE, payrolls, yields, and other US macro data the Layer 1 specialists pull each morning.",
    "cot": "<strong>COT (Commitments of Traders).</strong> CFTC's weekly positioning report. Shows how leveraged funds vs. asset managers vs. dealers are positioned in each futures market. Lagged 3 days but useful for spotting crowded trades.",
    "pnl": "<strong>P&L (profit and loss).</strong> Percentage move from your entry price, sign-aware on direction. Positive = trade is in profit; negative = in loss. Computed off the most recent daily close.",
    "thesis_at_open": "<strong>Thesis at open.</strong> The macro narrative the Judge wrote at the moment you opened the trade. Frozen so the advisor can later detect 'thesis weakened' by comparing today's view against this baseline.",
    "macro_now": "<strong>System view today.</strong> The latest run's bias direction and conviction for this instrument. 'Aligned' means it still agrees with your trade direction; 'opposed' means it's flipped. Numeric delta shows how much conviction has moved since you opened the position.",
    "chart_now": "<strong>Chart check today.</strong> The Tradability Filter's structural read on the chart right now: green-lit (clean spot), watch (wait for pullback), ugly (chart against the macro view), or no chart check (macro too weak to gate on).",

    // History / trend
    "trend_history": "<strong>7-day trend.</strong> The conviction reading on this instrument across the last seven publications. Read in bands, not digits — wobble of ±1 is natural variance. A sustained drift of 2-3 points is a real macro shift. The arrow shows ↑ rising, ↓ falling, → stable; the badge says whether the readings are stable, oscillating, or trending.",
    "stability_stable": "<strong>Stable.</strong> All readings within a 1-point band over the window. The macro view hasn't materially changed — wobble is pure noise. Hold positions through this without flinching.",
    "stability_oscillating": "<strong>Oscillating.</strong> Readings span 2+ points but no clear direction. Could be natural variance on a thin macro signal, or genuine ambivalence in the data. Don't act on individual prints; wait for the band to consolidate.",
    "stability_trending": "<strong>Trending.</strong> Readings show a sustained directional drift — conviction is firming or fading. This is actual signal, not noise. If you're holding a position, the thesis is materially shifting; re-read the Judge's reasoning to confirm whether to stay in.",
    "stability_n/a": "<strong>Not enough history.</strong> Fewer than 3 runs recorded for this instrument so the trend pattern can't be classified yet.",
    "thesis_drivers": "<strong>Driver status.</strong> The reasons (themes from THEMES.md, specialist support) the Strategist gave for today's bias, compared against the most recent prior run. <em>Intact / modified</em> means the driver's still alive (modified = same theme, slightly rephrased). <em>New</em> means added today. <em>Dropped</em> means removed since yesterday — that's the signal that something has shifted in the macro picture, not just the integer score.",

    // Delta-since-last-run chips
    "delta_direction_flip": "<strong>Direction flipped.</strong> The bias direction (long ↔ short) has changed since the prior run. This is the strongest cross-run signal — the Bull and Bear cases have decisively reversed roles in the Council debate. If you have an open position in this instrument, the advisor's <em>Close</em> verdict is likely about to fire. Re-read the Judge's reasoning before you do anything.",
    "delta_conviction_jump": "<strong>Conviction strengthened.</strong> Today's score is 2+ points higher than yesterday's. Either new data confirmed the existing thesis, or a previously-weak theme firmed up. Worth a Why? click to see what specifically changed.",
    "delta_conviction_drop": "<strong>Conviction weakened.</strong> Today's score is 2+ points lower than yesterday's. The macro view is materially fading. If you have an open position with this direction, the advisor may be moving toward Trim. If you're considering a fresh entry, hold off and re-evaluate.",
    "delta_minor": "<strong>Minor change.</strong> 1-point conviction wobble — the noise band. Don't act on it alone.",
    "delta_stable": "<strong>Unchanged from last run.</strong>",

    // Regime anchor
    "regime_anchor": "<strong>Regime (data-classified).</strong> A code-computed regime tag from FRED indicators alone — Industrial Production, NFP, retail sales, claims, CPI, PCE, breakevens. Two axes: growth (rising/falling) and inflation (rising/falling). Updates only when data updates (monthly), so it doesn't drift run-to-run like LLM scores. Compare against the LLM's bias readings — disagreement is itself a signal that the LLM is confused or the macro is in transition.",
    "regime_reflation": "<strong>Reflation.</strong> Growth rising AND inflation rising. Risk-on regime: bullish equities (especially cyclicals), commodities, EM, weak dollar.",
    "regime_goldilocks": "<strong>Goldilocks.</strong> Growth rising AND inflation falling. The best regime for risk assets — bullish equities (especially long-duration tech), neutral dollar, soft gold.",
    "regime_stagflation": "<strong>Stagflation.</strong> Growth falling AND inflation rising. Bullish gold, bullish dollar (safe haven), bearish equities, supply-driven oil. Hardest regime to trade.",
    "regime_deflation": "<strong>Deflation.</strong> Growth falling AND inflation falling. Bullish bonds and gold (Fed-cut response), bullish dollar, bearish equities and commodities.",
    "regime_transition": "<strong>Transition.</strong> Growth or inflation indicators are mixed, no clear regime. The system has no strong directional bias from data alone.",

    // Trend health (for held positions)
    "trend_trend_healthy": "<strong>Trend healthy.</strong> Chart structure is intact and aligned with your position direction — recent and longer-term moves both support the trade. The trend you opened on is still alive.",
    "trend_fading": "<strong>Trend fading.</strong> The longer-term trend still favours your position but recent action is mixed or going against you. Momentum is slowing — watch for confirmation that the trend is still alive vs. about to reverse.",
    "trend_reversal_risk": "<strong>Reversal risk.</strong> Chart structure has flipped against your position. The trend you opened on is breaking down. Re-evaluate the thesis seriously — the chart is no longer supporting you.",
    "trend_unknown": "<strong>Trend health unknown.</strong> No fresh price context for this instrument right now.",

    // FTMO
    "ftmo_status": "<strong>FTMO status.</strong> Informational summary of trailing drawdown headroom, open unrealised P&amp;L, correlation warnings (when multiple positions express the same theme), weekend gap risk (Friday + commodity/USD positions), and estimated daily swap costs across held positions. The system never enforces sizing — these numbers help you exercise discipline.",

    // Architecture
    "macro_picture": "<strong>Macro picture.</strong> The current regime — what big-picture themes are in force, ranked by conviction. Updated by the user in <code>THEMES.md</code> based on observed data and central-bank communication. The agents reason from these themes downstream.",
    "council": "<strong>Bias Council.</strong> Per-instrument debate: a Bull advocate makes the strongest long case, a Bear advocate makes the strongest short case, then a Judge weighs both and decides direction + conviction. Runs only when the Strategist's initial conviction is 5/10 or higher.",
    "filter": "<strong>Tradability Filter.</strong> The chart-only structural review that decides whether the bias is actionable *right now* — looks at trend alignment, location quality, ATR, and blocking events. Produces the Tradable / Watch / Skip verdict.",
    "contrarian": "<strong>Contrarian agent.</strong> The red-team layer. Argues against the consensus bias on every instrument so the Council Judge has a steel-manned counter-case to weigh, not just confirmation bias.",
  };

  let _tipEl = null;
  let _tipFor = null;
  function getTip() {
    if (_tipEl) return _tipEl;
    _tipEl = document.createElement("div");
    _tipEl.id = "nh-tooltip";
    document.body.appendChild(_tipEl);
    return _tipEl;
  }
  function positionTip(tip, target) {
    const tipRect = tip.getBoundingClientRect();
    const tRect = target.getBoundingClientRect();
    const margin = 8;
    // Prefer above; flip below if there's no room.
    let top = tRect.top - tipRect.height - margin;
    if (top < 8) top = tRect.bottom + margin;
    let left = tRect.left + tRect.width / 2 - tipRect.width / 2;
    if (left < 8) left = 8;
    if (left + tipRect.width > window.innerWidth - 8) {
      left = window.innerWidth - tipRect.width - 8;
    }
    tip.style.top = top + "px";
    tip.style.left = left + "px";
  }
  function showTip(target) {
    const term = target.dataset.term;
    if (!term) return;
    const def = GLOSSARY[term];
    if (!def) return;
    const tip = getTip();
    tip.innerHTML = def;
    tip.classList.add("is-visible");
    _tipFor = target;
    // Position after render so we have correct dimensions
    requestAnimationFrame(() => positionTip(tip, target));
  }
  function hideTip() {
    if (_tipEl) _tipEl.classList.remove("is-visible");
    _tipFor = null;
  }

  // Desktop: hover. Mobile: tap to toggle.
  if (surface !== "mobile") {
    document.addEventListener("mouseover", (e) => {
      const t = e.target.closest("[data-term]");
      if (t) showTip(t);
    });
    document.addEventListener("mouseout", (e) => {
      if (e.target.closest("[data-term]")) hideTip();
    });
  } else {
    document.addEventListener("click", (e) => {
      const t = e.target.closest("[data-term]");
      if (t) {
        e.preventDefault();
        if (_tipFor === t) hideTip();
        else showTip(t);
      } else if (_tipFor) {
        hideTip();
      }
    });
  }
  // Hide on scroll/resize so it doesn't drift away from its anchor
  window.addEventListener("scroll", hideTip, true);
  window.addEventListener("resize", hideTip);
  // Esc dismisses
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") hideTip(); });

  // ─── Run-now button + status banner (shared across both surfaces) ────

  const runBtn = $("#run-now-btn");
  const banner = $("#run-status-banner");
  const stageEl = $("#run-stage");
  const elapsedEl = $("#run-elapsed");
  const pctEl = $("#run-pct");
  const barEl = $("#run-bar");
  const logEl = $("#run-log");
  const logToggle = $("#run-log-toggle");
  const lastUpdatedEl = $("#last-updated");
  let pollTimer = null;
  let logVisible = false;
  let wasRunning = false;
  let initialCompletedAt = null;

  function fmtElapsed(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
  }
  function setLastUpdated(latest) {
    if (!lastUpdatedEl) return;
    if (!latest || !latest.completed_at) {
      lastUpdatedEl.textContent = "—";
      return;
    }
    lastUpdatedEl.textContent = fmtRelativeTime(latest.completed_at);
  }
  function showRunningBanner(data) {
    if (!banner) return;
    banner.hidden = false;
    if (stageEl) stageEl.textContent = data.stage || "Running…";
    if (elapsedEl) elapsedEl.textContent = fmtElapsed(data.elapsed_seconds || 0);
    if (pctEl) pctEl.textContent = (data.estimated_pct || 0) + "%";
    if (barEl) barEl.style.width = (data.estimated_pct || 0) + "%";
  }
  function showCompletedBanner() {
    if (!banner) return;
    banner.classList.add("success");
    if (stageEl) stageEl.textContent = "✓ Pipeline finished — refreshing…";
    if (pctEl) pctEl.textContent = "100%";
    if (barEl) barEl.style.width = "100%";
    if (logToggle) logToggle.style.display = "none";
  }
  function hideBanner() { if (banner) banner.hidden = true; }
  function startPolling() {
    if (pollTimer) return;
    pollTimer = setInterval(checkStatus, 4000);
    checkStatus();
  }
  function stopPolling() {
    if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
  }
  async function fetchLog() {
    try {
      const r = await fetch("/api/run/log?lines=30");
      const data = await r.json();
      if (logEl) logEl.textContent = (data.lines || []).join("\n");
    } catch (e) { /* ignore */ }
  }
  async function checkStatus() {
    try {
      const r = await fetch("/api/run/status");
      const data = await r.json();
      setLastUpdated(data.latest);
      const completed = (data.latest && data.latest.completed_at) || null;
      if (initialCompletedAt === null && completed) initialCompletedAt = completed;
      if (data.running) {
        showRunningBanner(data);
        if (logVisible) fetchLog();
        if (runBtn) {
          runBtn.disabled = true;
          runBtn.textContent = "Running…";
        }
        if (!pollTimer) startPolling();
        wasRunning = true;
      } else {
        if (initialCompletedAt && completed && completed !== initialCompletedAt) {
          showCompletedBanner();
          setTimeout(() => location.reload(), 1500);
          stopPolling();
          return;
        }
        if (wasRunning) {
          showCompletedBanner();
          setTimeout(() => location.reload(), 1500);
          stopPolling();
        } else {
          stopPolling();
          hideBanner();
          if (runBtn && runBtn.disabled) {
            runBtn.disabled = false;
            runBtn.textContent = "▶ Run again";
          }
        }
      }
    } catch (e) { /* transient — keep polling */ }
  }
  if (logToggle) {
    logToggle.addEventListener("click", () => {
      logVisible = !logVisible;
      if (logEl) logEl.hidden = !logVisible;
      logToggle.textContent = logVisible ? "Hide log" : "Show log";
      if (logVisible) fetchLog();
    });
  }
  // Centralised run-trigger so both desktop button and mobile menu use
  // the same code path. Previously the mobile menu's "Run now" item
  // tried to .click() the desktop button, which doesn't exist on mobile —
  // silent no-op. Now both surfaces call this directly.
  async function triggerRunNow(opts) {
    opts = opts || {};
    const skipConfirm = opts.skipConfirm === true;
    if (!skipConfirm) {
      const ok = confirm("Run a fresh pipeline now?\n\n10-15 min · ~$0.20.\nOverwrites today's brief.");
      if (!ok) return;
    }
    if (runBtn) {
      runBtn.disabled = true;
      runBtn.textContent = "Starting…";
    }
    wasRunning = true;
    try {
      const r = await fetch("/api/run", { method: "POST" });
      if (r.ok) {
        startPolling();
      } else {
        const msg = "Could not start run: " + (await r.text());
        alert(msg);
        if (runBtn) {
          runBtn.disabled = false;
          runBtn.textContent = "▶ Run again";
        }
      }
    } catch (e) {
      alert("Could not start run: " + e.message);
      if (runBtn) {
        runBtn.disabled = false;
        runBtn.textContent = "▶ Run again";
      }
    }
  }

  if (runBtn) {
    runBtn.addEventListener("click", () => {
      if (runBtn.disabled) return;
      triggerRunNow();
    });
  }
  // Run-picker dropdown
  const picker = $("#run-picker");
  if (picker) {
    picker.addEventListener("change", (e) => {
      if (e.target.value) location.href = "/run/" + encodeURIComponent(e.target.value);
    });
  }
  // On load: pick up any run in flight, and refresh "last updated" every 30s
  checkStatus();
  setInterval(checkStatus, 30000);

  // ─── Surface-specific overlay/sheet/modal manager ───────────────────

  const overlay = $("#overlay");

  function openOverlay() { if (overlay) overlay.classList.add("is-open"); }
  function closeOverlay() { if (overlay) overlay.classList.remove("is-open"); }

  if (overlay) overlay.addEventListener("click", () => closeAll());

  function openSlideover(title, html) {
    const so = $("#slideover");
    if (!so) return;
    $("#slideover-title").textContent = title;
    $("#slideover-body").innerHTML = html;
    so.classList.add("is-open");
    so.setAttribute("aria-hidden", "false");
    openOverlay();
  }
  function closeSlideover() {
    const so = $("#slideover");
    if (so) { so.classList.remove("is-open"); so.setAttribute("aria-hidden", "true"); }
  }
  function openModal(id) {
    const m = document.getElementById(id);
    if (!m) return;
    m.classList.add("is-open");
    m.setAttribute("aria-hidden", "false");
    openOverlay();
  }
  function closeModal(id) {
    const m = document.getElementById(id);
    if (m) { m.classList.remove("is-open"); m.setAttribute("aria-hidden", "true"); }
  }
  function openSheet(title, html, footHtml) {
    const sh = $("#sheet");
    if (!sh) return;
    $("#sheet-title").textContent = title;
    $("#sheet-body").innerHTML = html;
    const foot = $("#sheet-foot");
    if (foot) {
      if (footHtml) { foot.innerHTML = footHtml; foot.hidden = false; }
      else { foot.innerHTML = ""; foot.hidden = true; }
    }
    sh.classList.add("is-open");
    sh.setAttribute("aria-hidden", "false");
    openOverlay();
  }
  function closeSheet() {
    const sh = $("#sheet");
    if (sh) { sh.classList.remove("is-open"); sh.setAttribute("aria-hidden", "true"); }
  }
  function closeAll() {
    closeSlideover();
    closeSheet();
    $$(".modal.is-open").forEach((m) => m.classList.remove("is-open"));
    closeOverlay();
  }
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeAll(); });

  // Universal: open / close detail container — picks based on surface
  function openDetail(title, html, footHtml) {
    if (surface === "mobile") openSheet(title, html, footHtml);
    else openSlideover(title, html);
  }

  // ─── "Why?" — show reasoning for an instrument ──────────────────────

  async function showInstrumentReasoning(symbol) {
    openDetail(`${symbol} — full reasoning`,
      `<p class="muted">Loading reasoning for ${symbol}…</p>`);
    try {
      const r = await fetch(`/api/reasoning/${encodeURIComponent(symbol)}`);
      const data = await r.json();
      const html = renderReasoningHtml(data);
      const body = surface === "mobile" ? $("#sheet-body") : $("#slideover-body");
      if (body) body.innerHTML = html;
    } catch (e) {
      const body = surface === "mobile" ? $("#sheet-body") : $("#slideover-body");
      if (body) body.innerHTML = `<p class="muted">Couldn't load reasoning: ${escapeHTML(e.message)}</p>`;
    }
  }

  function renderReasoningHtml(data) {
    if (!data) return "<p class='muted'>No data.</p>";
    let out = "";
    // Drivers up top — most actionable view
    if (data.thesis && data.thesis.drivers && data.thesis.drivers.length) {
      const items = data.thesis.drivers.map(d => {
        const cls = d.status === "intact" ? "chip-good"
                  : d.status === "modified" ? "chip-good"
                  : d.status === "new" ? "chip-brand"
                  : d.status === "dropped" ? "chip-warn"
                  : "chip-neutral";
        return `<li style="margin-bottom: 6px;"><span class="chip ${cls}" style="font-size: 10px; margin-right: 8px;">${d.status.toUpperCase()}</span>${escapeHTML(d.driver)}</li>`;
      }).join("");
      out += `<h4>Drivers <span class="muted" style="font-weight: 400; font-size: 12px;">(${escapeHTML(data.thesis.summary_label || "")})</span></h4><ul style="list-style: none; padding: 0;">${items}</ul>`;
    }
    // Score history
    if (data.history && data.history.entries && data.history.entries.length >= 2) {
      const e = data.history;
      out += `<h4>Conviction history</h4>
        <p>Last ${e.entries.length} runs: <strong>${e.convictions.join(" → ")}</strong>
        ${e.trend_arrow ? ` ${e.trend_arrow}` : ""}
        ${e.weighted_avg_3d != null ? ` &nbsp; <span class="muted">3-day avg ${e.weighted_avg_3d}</span>` : ""}
        ${e.stability && e.stability !== "n/a" ? ` &nbsp; <span class="chip ${e.stability === "stable" ? "chip-good" : e.stability === "trending" ? "chip-warn" : "chip-neutral"}" style="font-size: 11px;">${e.stability}</span>` : ""}
        </p>`;
    }
    if (data.strategist_md) {
      out += `<h4>Macro view (Strategist)</h4><div class="prose">${data.strategist_md_rendered || lightFormat(data.strategist_md)}</div>`;
    }
    if (data.judge_md) {
      out += `<h4>Final judgment (Judge)</h4><div class="prose">${data.judge_md_rendered || lightFormat(data.judge_md)}</div>`;
    }
    if (data.bull_md) {
      out += `<h4>Bull case</h4><details><summary class="muted" style="cursor:pointer;">Show</summary><div class="prose">${data.bull_md_rendered || lightFormat(data.bull_md)}</div></details>`;
    }
    if (data.bear_md) {
      out += `<h4>Bear case</h4><details><summary class="muted" style="cursor:pointer;">Show</summary><div class="prose">${data.bear_md_rendered || lightFormat(data.bear_md)}</div></details>`;
    }
    if (data.filter_md) {
      out += `<h4>Chart structural review</h4><div class="prose">${data.filter_md_rendered || lightFormat(data.filter_md)}</div>`;
    }
    return out || "<p class='muted'>No reasoning available for this instrument.</p>";
  }

  async function showPositionWhy(positionId) {
    openDetail("Why this advice",
      `<p class="muted">Loading…</p>`);
    try {
      const r = await fetch("/api/positions");
      const data = await r.json();
      const item = (data.active || []).find((it) => it.position && it.position.id === positionId);
      if (!item) {
        const body = surface === "mobile" ? $("#sheet-body") : $("#slideover-body");
        if (body) body.innerHTML = "<p class='muted'>Position not found.</p>";
        return;
      }
      const p = item.position;
      const adv = item.advice || {};
      const html = `
        <h4>${p.instrument} ${p.direction.toUpperCase()}</h4>
        <p><strong>Recommendation:</strong> ${escapeHTML(adv.action || "—")}.<br>
           ${escapeHTML(adv.reason || "—")}</p>
        <p>
          <button class="btn btn-sm" data-action="edit-position" data-id="${p.id}">Edit trade</button>
          <button class="btn btn-sm" data-action="close-position" data-id="${p.id}">Mark closed</button>
        </p>
        <h4>The numbers</h4>
        <ul>
          <li>Entry: ${p.entry_price} on ${p.entry_date}</li>
          <li>Current: ${item.current_price ?? "—"}</li>
          <li>Size: ${p.size_units ?? "—"}</li>
          <li>P&amp;L: ${fmtPnl(adv.pnl_pct)}</li>
          ${p.emergency_stop ? `<li>Stop: ${p.emergency_stop} (${adv.stop_distance_pct ? adv.stop_distance_pct.toFixed(1) + "% away" : "—"})</li>` : `<li>Stop: <em>not set</em></li>`}
        </ul>
        <h4>Macro since you opened</h4>
        <ul>
          <li>At open: ${p.bias_at_open || "—"} ${p.conviction_at_open}/10</li>
          <li>Now: ${adv.macro_aligned ? "still aligned" : "OPPOSED"} at ${adv.conviction_now}/10
              (${adv.conviction_delta > 0 ? "+" : ""}${adv.conviction_delta} change)</li>
          <li>Chart now: ${adv.filter_verdict_now || "—"}</li>
        </ul>
        ${p.thesis_at_open ? `<h4>Why you opened it</h4><p>${escapeHTML(p.thesis_at_open)}</p>` : ""}
        ${p.notes ? `<h4>Notes</h4><pre style="white-space:pre-wrap;font-family:inherit;">${escapeHTML(p.notes)}</pre>` : ""}
      `;
      const body = surface === "mobile" ? $("#sheet-body") : $("#slideover-body");
      if (body) body.innerHTML = html;
    } catch (e) {
      const body = surface === "mobile" ? $("#sheet-body") : $("#slideover-body");
      if (body) body.innerHTML = `<p class='muted'>Couldn't load: ${escapeHTML(e.message)}</p>`;
    }
  }

  // ─── New trade form ──────────────────────────────────────────────────

  function openNewTrade(prefill) {
    if (surface === "mobile") {
      const sym = (prefill && prefill.instrument) || (cfg.activeUniverse || [])[0] || "";
      const dir = (prefill && prefill.direction) || "long";
      const today = new Date().toISOString().slice(0, 10);
      const opts = (cfg.activeUniverse || []).map(s => `<option value="${s}" ${s === sym ? "selected" : ""}>${s}</option>`).join("");
      const html = `
        <form id="nt-form-mobile">
          <div class="field">
            <label for="ntm-instrument">Instrument</label>
            <select id="ntm-instrument" required>${opts}</select>
          </div>
          <div class="field-row">
            <div class="field">
              <label for="ntm-direction">Direction</label>
              <select id="ntm-direction" required>
                <option value="long" ${dir === "long" ? "selected" : ""}>Long</option>
                <option value="short" ${dir === "short" ? "selected" : ""}>Short</option>
              </select>
            </div>
            <div class="field">
              <label for="ntm-date">Entry date</label>
              <input type="date" id="ntm-date" value="${today}" required>
            </div>
          </div>
          <div class="field-row">
            <div class="field">
              <label for="ntm-price">Entry price</label>
              <input type="number" step="any" id="ntm-price" required>
            </div>
            <div class="field">
              <label for="ntm-stop">Stop level</label>
              <input type="number" step="any" id="ntm-stop">
            </div>
          </div>
          <div class="field">
            <label for="ntm-notes">Notes</label>
            <textarea id="ntm-notes" rows="2"></textarea>
          </div>
        </form>
      `;
      const foot = `
        <button class="btn btn-ghost" data-action="close-sheet">Cancel</button>
        <button class="btn btn-primary" data-action="submit-new-trade-mobile">Record</button>
      `;
      openSheet("Record a new trade", html, foot);
    } else {
      const today = new Date().toISOString().slice(0, 10);
      $("#nt-entry-date").value = today;
      if (prefill && prefill.instrument) $("#nt-instrument").value = prefill.instrument;
      if (prefill && prefill.direction) $("#nt-direction").value = prefill.direction;
      $("#nt-status").textContent = "";
      openModal("modal-new-trade");
    }
  }

  async function submitNewTrade(form) {
    const fd = (form === "mobile")
      ? {
          instrument: $("#ntm-instrument").value,
          direction: $("#ntm-direction").value,
          entry_date: $("#ntm-date").value,
          entry_price: parseFloat($("#ntm-price").value),
          emergency_stop: $("#ntm-stop").value ? parseFloat($("#ntm-stop").value) : null,
          notes: $("#ntm-notes").value,
        }
      : {
          instrument: $("#nt-instrument").value,
          direction: $("#nt-direction").value,
          entry_date: $("#nt-entry-date").value,
          entry_price: parseFloat($("#nt-entry-price").value),
          emergency_stop: $("#nt-stop").value ? parseFloat($("#nt-stop").value) : null,
          notes: $("#nt-notes").value,
        };
    if (!fd.entry_price || fd.entry_price <= 0) {
      alert("Entry price required.");
      return;
    }
    try {
      const r = await fetch("/api/positions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(fd),
      });
      if (r.ok) {
        closeAll();
        setTimeout(() => location.reload(), 200);
      } else {
        const err = await r.text();
        if (form === "mobile") alert("Failed: " + err);
        else $("#nt-status").textContent = "Failed: " + err;
      }
    } catch (e) {
      alert("Failed: " + e.message);
    }
  }

  // ─── Edit-position flow ────────────────────────────────────────────

  async function openEditTrade(positionId) {
    // Pull the current position data so the form can be pre-filled
    let data;
    try {
      const r = await fetch("/api/positions");
      const json = await r.json();
      const item = (json.active || []).find((it) => it.position && it.position.id === positionId);
      if (!item) {
        alert("Position not found.");
        return;
      }
      data = item.position;
    } catch (e) {
      alert("Couldn't load position: " + e.message);
      return;
    }

    if (surface === "mobile") {
      const html = `
        <p class="muted" style="margin-top: 0; font-size: 13px;">
          Correct typos or update size, stop, or notes. The bias and
          thesis snapshot from when you opened stay frozen.
        </p>
        <input type="hidden" id="etm-id" value="${data.id}">
        <div class="field-row">
          <div class="field">
            <label for="etm-date">Entry date</label>
            <input type="date" id="etm-date" value="${data.entry_date || ""}">
          </div>
          <div class="field">
            <label for="etm-price">Entry price</label>
            <input type="number" step="any" id="etm-price" value="${data.entry_price ?? ""}">
          </div>
        </div>
        <div class="field-row">
          <div class="field">
            <label for="etm-size">Size</label>
            <input type="number" step="any" id="etm-size" value="${data.size_units ?? ""}">
          </div>
          <div class="field">
            <label for="etm-stop">Stop level</label>
            <input type="number" step="any" id="etm-stop" value="${data.emergency_stop ?? ""}">
          </div>
        </div>
        <div class="field">
          <label for="etm-notes">Notes (replaces existing)</label>
          <textarea id="etm-notes" rows="3">${escapeHTML(data.notes || "")}</textarea>
        </div>
      `;
      const foot = `
        <button class="btn btn-ghost" data-action="close-sheet">Cancel</button>
        <button class="btn btn-primary" data-action="submit-edit-trade-mobile">Save</button>
      `;
      openSheet(`Edit ${data.instrument} ${data.direction.toUpperCase()}`, html, foot);
    } else {
      $("#et-id").value = data.id;
      $("#et-symbol-label").textContent = `${data.instrument} ${data.direction.toUpperCase()}`;
      $("#et-entry-date").value = data.entry_date || "";
      $("#et-entry-price").value = data.entry_price ?? "";
      $("#et-size").value = data.size_units ?? "";
      $("#et-stop").value = data.emergency_stop ?? "";
      $("#et-notes").value = data.notes || "";
      $("#et-status").textContent = "";
      openModal("modal-edit-trade");
    }
  }

  async function submitEditTrade(form) {
    const fd = (form === "mobile")
      ? {
          id: $("#etm-id").value,
          entry_date: $("#etm-date").value || null,
          entry_price: $("#etm-price").value ? parseFloat($("#etm-price").value) : null,
          size_units: $("#etm-size").value ? parseFloat($("#etm-size").value) : null,
          emergency_stop: $("#etm-stop").value ? parseFloat($("#etm-stop").value) : null,
          notes: $("#etm-notes").value,
        }
      : {
          id: $("#et-id").value,
          entry_date: $("#et-entry-date").value || null,
          entry_price: $("#et-entry-price").value ? parseFloat($("#et-entry-price").value) : null,
          size_units: $("#et-size").value ? parseFloat($("#et-size").value) : null,
          emergency_stop: $("#et-stop").value ? parseFloat($("#et-stop").value) : null,
          notes: $("#et-notes").value,
        };
    if (!fd.id) return;
    const id = fd.id;
    delete fd.id;
    // Strip empty/null fields so the server only updates what changed
    Object.keys(fd).forEach((k) => { if (fd[k] === null || fd[k] === "" || (typeof fd[k] === "number" && Number.isNaN(fd[k]))) delete fd[k]; });
    try {
      const r = await fetch(`/api/positions/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(fd),
      });
      if (r.ok) {
        closeAll();
        setTimeout(() => location.reload(), 200);
      } else {
        const err = await r.text();
        if (form === "mobile") alert("Edit failed: " + err);
        else $("#et-status").textContent = "Failed: " + err;
      }
    } catch (e) {
      alert("Edit failed: " + e.message);
    }
  }

  // ─── Close-position prompt ──────────────────────────────────────────

  async function closePosition(positionId) {
    const priceStr = prompt("Close price?");
    if (priceStr === null) return;
    const price = parseFloat(priceStr);
    if (!isFinite(price) || price <= 0) { alert("Invalid price."); return; }
    const reason = prompt("Reason (optional, e.g. 'stop hit', 'taking profit'):", "") || "";
    try {
      const r = await fetch(`/api/positions/${positionId}/close`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ close_price: price, close_reason: reason }),
      });
      if (r.ok) location.reload();
      else alert("Close failed: " + (await r.text()));
    } catch (e) { alert("Close failed: " + e.message); }
  }

  // ─── Closed trades journal ──────────────────────────────────────────

  async function showClosedTrades() {
    const renderList = (items) => {
      if (!items || items.length === 0) {
        return "<p class='muted' style='text-align:center;padding:20px 0;'>No closed trades yet.</p>";
      }
      return `<ul class="closed-list">` + items.map(p => {
        const sign = (p.pnl_pct || 0) >= 0 ? "pnl-pos" : "pnl-neg";
        return `<li>
          <span class="closed-symbol symbol">${p.instrument}</span>
          <span class="closed-dir dir">${p.direction.toUpperCase()}</span>
          <span class="closed-pnl pnl ${sign}">${fmtPnl(p.pnl_pct)}</span>
          <span class="closed-meta meta">${p.entry_date} → ${p.close_date || "—"}${p.close_reason ? " · " + escapeHTML(p.close_reason) : ""}</span>
        </li>`;
      }).join("") + `</ul>`;
    };
    if (surface === "mobile") {
      openSheet("Closed trades", "<p class='muted'>Loading…</p>");
    } else {
      openModal("modal-journal");
    }
    try {
      const r = await fetch("/api/positions");
      const data = await r.json();
      const closed = data.closed_recent || [];
      if (surface === "mobile") {
        $("#sheet-body").innerHTML = renderList(closed);
      } else {
        const list = $("#closed-list");
        const empty = $("#closed-empty");
        if (closed.length === 0) {
          if (list) list.innerHTML = "";
          if (empty) empty.style.display = "";
        } else {
          if (empty) empty.style.display = "none";
          if (list) list.innerHTML = closed.map(p => {
            const sign = (p.pnl_pct || 0) >= 0 ? "pnl-pos" : "pnl-neg";
            return `<li>
              <span class="closed-symbol">${p.instrument}</span>
              <span class="closed-dir">${p.direction.toUpperCase()}</span>
              <span class="closed-pnl ${sign}">${fmtPnl(p.pnl_pct)}</span>
              <span class="closed-meta">${p.entry_date} → ${p.close_date || "—"}${p.close_reason ? " · " + escapeHTML(p.close_reason) : ""}</span>
            </li>`;
          }).join("");
        }
      }
    } catch (e) {
      if (surface === "mobile") $("#sheet-body").innerHTML = "<p class='muted'>Couldn't load.</p>";
    }
  }

  // ─── Brief sheet (mobile) ───────────────────────────────────────────

  async function showBrief() {
    if (surface !== "mobile") return; // desktop has it inline
    openSheet("Today's brief", "<p class='muted'>Loading…</p>");
    try {
      const r = await fetch(`/api/brief?date=${encodeURIComponent(cfg.runDate)}`);
      const data = await r.json();
      $("#sheet-body").innerHTML = data.html
        ? `<div class="brief-sheet"><div class="prose">${data.html}</div></div>`
        : "<p class='muted'>No brief for this run.</p>";
    } catch (e) {
      $("#sheet-body").innerHTML = "<p class='muted'>Couldn't load brief.</p>";
    }
  }

  // ─── Ask (chat) ──────────────────────────────────────────────────────

  let askPersona = "default";
  function chatHistKey() { return `chat:${cfg.runDate}:${askPersona}`; }
  function loadChatHist() { try { return JSON.parse(localStorage.getItem(chatHistKey()) || "[]"); } catch (e) { return []; } }
  function saveChatHist(h) { try { localStorage.setItem(chatHistKey(), JSON.stringify(h)); } catch (e) {} }

  function renderChatHist() {
    const target = surface === "mobile"
      ? $("#sheet-body .chat-history")
      : $("#chat-history");
    if (!target) return;
    const h = loadChatHist();
    target.innerHTML = "";
    if (h.length === 0) {
      target.innerHTML = `<div class="muted" style="font-size:13px;padding:8px 0;">Ask anything about today's brief or your open trades.</div>`;
      return;
    }
    h.forEach(msg => {
      const el = document.createElement("div");
      el.className = "chat-msg " + msg.role;
      el.innerHTML = `<span class="role-label">${msg.role === "user" ? "You" : (msg.persona || "Assistant")}</span><div>${lightFormat(msg.content)}</div>`;
      target.appendChild(el);
    });
    target.scrollTop = target.scrollHeight;
  }

  function attachChatForm(formEl, inputEl, sendBtn, personaSel) {
    if (!formEl || !inputEl || !sendBtn) {
      console.warn("attachChatForm: missing element", { formEl, inputEl, sendBtn });
      return;
    }
    formEl.addEventListener("submit", async (e) => {
      e.preventDefault();
      const text = inputEl.value.trim();
      if (!text) return;
      const h = loadChatHist();
      h.push({ role: "user", content: text });
      saveChatHist(h);
      inputEl.value = "";
      renderChatHist();
      sendBtn.disabled = true;
      sendBtn.textContent = "Thinking…";
      try {
        const r = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ run_date: cfg.runDate, persona: askPersona, history: h }),
        });
        let data = null;
        try { data = await r.json(); } catch (parseErr) {
          // Server returned non-JSON (most likely an HTML error page or the
          // server died mid-stream). Show the raw text instead of swallowing.
          const text = await r.text().catch(() => "");
          throw new Error(`server returned ${r.status} ${r.statusText} (not JSON). ${text.slice(0, 200)}`);
        }
        if (r.ok) {
          const updated = loadChatHist();
          const personaLabel = personaSel
            ? personaSel.options[personaSel.selectedIndex].text
            : "Assistant";
          updated.push({ role: "assistant", content: data.content, persona: personaLabel === "Default analyst" ? "Assistant" : personaLabel });
          saveChatHist(updated);
          renderChatHist();
        } else {
          // Show actual server error rather than "unknown"
          const detail = data && (data.detail || data.error || data.message);
          alert(`Chat failed (${r.status}): ${detail || "see server log"}`);
        }
      } catch (err) {
        alert("Chat failed: " + (err.message || err));
        console.error("Chat error", err);
      }
      finally { sendBtn.disabled = false; sendBtn.textContent = "Send"; }
    });
  }

  function showAsk() {
    if (surface === "mobile") {
      const opts = (cfg.personas || []).map(p =>
        `<option value="${p.key}" ${p.key === askPersona ? "selected" : ""}>${p.label}</option>`
      ).join("");
      const html = `
        <div class="field">
          <label for="ask-persona-m">Voice</label>
          <select id="ask-persona-m">${opts}</select>
        </div>
        <div class="chat-history" aria-live="polite"></div>
        <form id="ask-form-m" class="chat-form">
          <textarea id="ask-input-m" placeholder="Ask anything…" rows="2"></textarea>
          <button type="submit" class="btn btn-primary" id="ask-send-m">Send</button>
        </form>
      `;
      openSheet("Ask", html);
      const personaSel = $("#ask-persona-m");
      personaSel.addEventListener("change", () => { askPersona = personaSel.value; renderChatHist(); });
      renderChatHist();
      attachChatForm($("#ask-form-m"), $("#ask-input-m"), $("#ask-send-m"), personaSel);
    } else {
      const personaSel = $("#ask-persona");
      askPersona = personaSel ? personaSel.value : "default";
      openModal("modal-ask");
      renderChatHist();
      if (personaSel) personaSel.addEventListener("change", () => { askPersona = personaSel.value; renderChatHist(); });
      const form = $("#chat-form");
      const input = $("#chat-input");
      const send = $("#chat-send");
      if (form && !form.dataset.bound) {
        attachChatForm(form, input, send, personaSel);
        form.dataset.bound = "1";
      }
    }
  }

  // ─── All instruments (mobile sheet) ─────────────────────────────────

  function showInstrumentsList() {
    if (surface !== "mobile") return;
    const items = (cfg.instruments || []).map(r => {
      const h = r.history || {};
      const arrow = h.trend_arrow || "";
      const avg = h.weighted_avg_3d != null ? `avg ${h.weighted_avg_3d}` : "";
      const stab = h.stability && h.stability !== "n/a" ? h.stability : "";
      const trendBits = [arrow, avg, stab].filter(Boolean).join(" · ");
      // Highlight cross-run deltas — same logic as the desktop chip
      const d = h.delta || {};
      let deltaChip = "";
      if (d.changed && d.kind !== "minor") {
        const cls = d.kind === "direction_flip" ? "chip-bad"
                  : d.kind === "conviction_drop" ? "chip-warn"
                  : d.kind === "conviction_jump" ? "chip-good"
                  : "chip-neutral";
        const icon = d.kind === "direction_flip" ? "⚡ " : "";
        deltaChip = `<span class="chip ${cls}" style="font-size: 10px; margin-top: 4px;">${icon}${d.summary}</span>`;
      }
      // Driver status from thesis tracker (already in r.thesis)
      const t = r.thesis || {};
      const driverNote = t.dropped_count > 0
        ? ` · <span style="color: var(--warn-text); font-size: 11px;">${t.dropped_count} driver${t.dropped_count !== 1 ? "s" : ""} dropped</span>`
        : "";
      return `
        <li class="${r.is_open_position ? "has-position" : ""}" data-symbol="${r.symbol}" data-action="why-instrument">
          <span class="symbol">${r.symbol}</span>
          <div class="meta">
            ${escapeHTML(r.direction_raw || "—")}<br>
            <span class="muted">${escapeHTML(r.state)}</span>${driverNote}
            ${trendBits ? `<br><span class="muted" style="font-size: 11px;">${trendBits}</span>` : ""}
            ${deltaChip ? `<br>${deltaChip}` : ""}
          </div>
          <span class="muted">${r.conviction}/10</span>
        </li>
      `;
    }).join("");
    openSheet("All instruments", `<ul class="instr-list-mobile">${items}</ul>`);
  }

  // ─── Past runs (mobile sheet — desktop uses dropdown) ───────────────

  function showPastRuns() {
    if (surface !== "mobile") return;
    const html = `<ul class="instr-list-mobile">` + (cfg.runs || []).map(r => `
      <li onclick="location.href='/run/${r}'">
        <span class="symbol">${r}</span>
        <span></span>
        <span class="arrow">→</span>
      </li>
    `).join("") + `</ul>`;
    openSheet("Past runs", html);
  }

  // ─── Mobile menu sheet ───────────────────────────────────────────────

  function showMenu() {
    const html = `
      <ul class="instr-list-mobile">
        <li data-action="run-now">
          <span class="symbol">▶</span><span class="meta">Run a fresh pipeline now</span><span></span>
        </li>
        <li data-action="open-past-runs">
          <span class="symbol">📅</span><span class="meta">Past runs</span><span class="arrow">→</span>
        </li>
        <li data-action="open-journal">
          <span class="symbol">📓</span><span class="meta">Closed trades journal</span><span class="arrow">→</span>
        </li>
        <li onclick="location.href='?view=desktop'">
          <span class="symbol">🖥</span><span class="meta">Switch to desktop view</span><span class="arrow">→</span>
        </li>
      </ul>
    `;
    openSheet("More", html);
  }

  // ─── Recent events log ───────────────────────────────────────────────

  function openAddEvent() {
    const today = new Date().toISOString().slice(0, 10);
    if (surface === "mobile") {
      const html = `
        <p class="muted" style="margin-top: 0; font-size: 13px;">
          The system has no news API — this is how news enters the pipeline.
          Tomorrow's run will read this log.
        </p>
        <form id="ae-form-m">
          <div class="field-row">
            <div class="field">
              <label for="aem-date">Date</label>
              <input type="date" id="aem-date" value="${today}" required>
            </div>
            <div class="field">
              <label for="aem-relevance">Relevance</label>
              <select id="aem-relevance">
                <option value="high">High</option>
                <option value="medium" selected>Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
          </div>
          <div class="field">
            <label for="aem-headline">Headline</label>
            <input type="text" id="aem-headline" maxlength="200" required
                   placeholder='e.g. "Trump tariff on Mexico"'>
          </div>
          <div class="field">
            <label for="aem-impact">Cross-asset impact (optional)</label>
            <input type="text" id="aem-impact"
                   placeholder='e.g. "Peso -3%, NQ -1.2%"'>
          </div>
          <div class="field">
            <label for="aem-notes">Your interpretation (optional)</label>
            <textarea id="aem-notes" rows="2"></textarea>
          </div>
          <div class="field">
            <label for="aem-affects">Affects (optional, comma-separated)</label>
            <input type="text" id="aem-affects" placeholder="e.g. USDMXN, NQ, GC">
          </div>
        </form>
      `;
      const foot = `
        <button class="btn btn-ghost" data-action="close-sheet">Cancel</button>
        <button class="btn btn-primary" data-action="submit-add-event-mobile">Save</button>
      `;
      openSheet("Log a recent event", html, foot);
    } else {
      $("#ae-date").value = today;
      $("#ae-headline").value = "";
      $("#ae-impact").value = "";
      $("#ae-notes").value = "";
      $("#ae-affects").value = "";
      $("#ae-relevance").value = "medium";
      $("#ae-status").textContent = "";
      openModal("modal-add-event");
    }
  }

  async function submitAddEvent(form) {
    const fd = (form === "mobile")
      ? {
          date: $("#aem-date").value,
          headline: $("#aem-headline").value.trim(),
          impact: $("#aem-impact").value.trim(),
          notes: $("#aem-notes").value.trim(),
          relevance: $("#aem-relevance").value,
          affects: $("#aem-affects").value.split(",").map(s => s.trim()).filter(Boolean),
        }
      : {
          date: $("#ae-date").value,
          headline: $("#ae-headline").value.trim(),
          impact: $("#ae-impact").value.trim(),
          notes: $("#ae-notes").value.trim(),
          relevance: $("#ae-relevance").value,
          affects: $("#ae-affects").value.split(",").map(s => s.trim()).filter(Boolean),
        };
    if (!fd.headline) { alert("Headline required."); return; }
    try {
      const r = await fetch("/api/recent-events", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(fd),
      });
      if (r.ok) {
        closeAll();
        setTimeout(() => location.reload(), 200);
      } else {
        const err = await r.text();
        if (form === "mobile") alert("Failed: " + err);
        else $("#ae-status").textContent = "Failed: " + err;
      }
    } catch (e) { alert("Failed: " + e.message); }
  }

  async function deleteEvent(date, headline) {
    if (!confirm(`Delete this event?\n\n${date}: ${headline}`)) return;
    try {
      const r = await fetch("/api/recent-events/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date, headline }),
      });
      if (r.ok) location.reload();
      else alert("Delete failed: " + (await r.text()));
    } catch (e) { alert("Delete failed: " + e.message); }
  }

  async function showEventsLog() {
    if (surface !== "mobile") return;
    openSheet("News log", "<p class='muted'>Loading…</p>",
      `<button class="btn btn-primary" style="flex:1;" data-action="open-add-event">+ Add event</button>`);
    try {
      const r = await fetch("/api/recent-events");
      const data = await r.json();
      const events = data.events || [];
      if (events.length === 0) {
        $("#sheet-body").innerHTML = `
          <p class="muted" style="text-align:center;padding:20px 0;">
            No events logged. Tap "+ Add event" below to add one.<br><br>
            <span style="font-size:12px;">Tomorrow's analysis run will read whatever you log here.</span>
          </p>`;
        return;
      }
      $("#sheet-body").innerHTML = events.map(e => `
        <article style="padding: 10px 12px; background: ${e.relevance === 'high' ? 'var(--bad-tint)' : 'var(--surface-soft)'};
                        border: 1px solid var(--border); border-radius: var(--radius-sm); margin-bottom: 6px;">
          <div style="display: flex; gap: 8px; align-items: baseline; flex-wrap: wrap; margin-bottom: 4px;">
            <span class="muted" style="font-family: var(--mono); font-size: 12px;">${e.date}</span>
            <span class="muted" style="font-size: 11px;">${e.days_ago}d ago</span>
            <span class="chip ${e.relevance === 'high' ? 'chip-bad' : (e.relevance === 'medium' ? 'chip-warn' : 'chip-neutral')}">${e.relevance.toUpperCase()}</span>
            <button class="btn btn-sm btn-ghost" style="margin-left:auto;" data-action="delete-event"
                    data-date="${e.date}" data-headline="${escapeHTML(e.headline)}">×</button>
          </div>
          <div style="font-weight: 500; margin-bottom: 4px;">${escapeHTML(e.headline)}</div>
          ${e.impact ? `<div class="muted" style="font-size: 12px;">Impact: ${escapeHTML(e.impact)}</div>` : ""}
          ${e.notes ? `<div class="muted" style="font-size: 12px;">Note: ${escapeHTML(e.notes)}</div>` : ""}
          ${e.affects && e.affects.length ? `<div class="muted" style="font-size: 12px;">Affects: ${e.affects.join(", ")}</div>` : ""}
        </article>
      `).join("");
    } catch (e) { $("#sheet-body").innerHTML = "<p class='muted'>Couldn't load.</p>"; }
  }

  // ─── Single click dispatcher ─────────────────────────────────────────

  document.addEventListener("click", async (e) => {
    const target = e.target.closest("[data-action]");
    if (!target) return;
    const action = target.dataset.action;
    const id = target.dataset.id;
    const sym = target.dataset.symbol;

    switch (action) {
      case "close-position":      e.preventDefault(); closePosition(id); break;
      case "edit-position":       e.preventDefault(); openEditTrade(id); break;
      case "submit-edit-trade":   e.preventDefault(); submitEditTrade("desktop"); break;
      case "submit-edit-trade-mobile": e.preventDefault(); submitEditTrade("mobile"); break;
      case "why-position":        e.preventDefault(); showPositionWhy(id); break;
      case "why-instrument":      e.preventDefault(); showInstrumentReasoning(sym); break;
      case "open-new-trade":      e.preventDefault(); openNewTrade(); break;
      case "record-trade":        e.preventDefault(); openNewTrade({ instrument: target.dataset.instrument, direction: target.dataset.direction }); break;
      case "submit-new-trade":    e.preventDefault(); submitNewTrade("desktop"); break;
      case "submit-new-trade-mobile": e.preventDefault(); submitNewTrade("mobile"); break;
      case "open-ask":            e.preventDefault(); showAsk(); break;
      case "open-journal":        e.preventDefault(); showClosedTrades(); break;
      case "open-brief":          e.preventDefault(); showBrief(); break;
      case "open-instruments-list": e.preventDefault(); showInstrumentsList(); break;
      case "open-past-runs":      e.preventDefault(); showPastRuns(); break;
      case "open-menu":           e.preventDefault(); showMenu(); break;
      case "close-slideover":     e.preventDefault(); closeAll(); break;
      case "close-sheet":         e.preventDefault(); closeAll(); break;
      case "close-modal":         e.preventDefault(); closeModal(target.dataset.target); closeOverlay(); break;
      case "scroll-top":          e.preventDefault(); window.scrollTo({ top: 0, behavior: "smooth" }); break;
      case "open-trade-detail":   e.preventDefault(); showPositionWhy(target.dataset.positionId); break;
      case "run-now":             e.preventDefault(); closeAll(); triggerRunNow(); break;
      case "open-add-event":      e.preventDefault(); openAddEvent(); break;
      case "submit-add-event":    e.preventDefault(); submitAddEvent("desktop"); break;
      case "submit-add-event-mobile": e.preventDefault(); submitAddEvent("mobile"); break;
      case "delete-event":        e.preventDefault(); deleteEvent(target.dataset.date, target.dataset.headline); break;
      case "open-events-log":     e.preventDefault(); showEventsLog(); break;
    }
  });

  // Clicking an instrument row in the desktop table opens its reasoning.
  $$(".instr-table tbody tr[data-symbol]").forEach((row) => {
    row.addEventListener("click", (e) => {
      // ignore if user clicked the explicit "Why?" link (handled by dispatcher)
      if (e.target.closest("[data-action]")) return;
      showInstrumentReasoning(row.dataset.symbol);
    });
  });

  // ─── Sparkline rendering ────────────────────────────────────────────
  // Each .sparkline carries a JSON array of conviction integers (oldest
  // first). Build a small inline SVG showing the trend as a polyline
  // with a highlighted dot for today's value.
  function renderSparkline(el) {
    let convs;
    try { convs = JSON.parse(el.dataset.convictions || "[]"); }
    catch (e) { return; }
    if (!convs.length) return;
    const W = 70, H = 18, PAD = 2;
    const minV = 0, maxV = 10;
    const stepX = convs.length > 1 ? (W - 2 * PAD) / (convs.length - 1) : 0;
    const points = convs.map((v, i) => {
      const x = PAD + i * stepX;
      // Invert Y because SVG origin is top-left
      const y = H - PAD - ((v - minV) / (maxV - minV)) * (H - 2 * PAD);
      return [x, y];
    });
    const lineD = points.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
    const dots = points.map(([x, y], i) => {
      const cls = (i === points.length - 1) ? "spark-dot spark-dot-last" : "spark-dot";
      const r = (i === points.length - 1) ? 2.5 : 1.5;
      return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r}" class="${cls}" />`;
    }).join("");
    el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
      <polyline class="spark-line" points="${lineD}" />
      ${dots}
    </svg>`;
  }
  $$(".sparkline").forEach(renderSparkline);
})();
