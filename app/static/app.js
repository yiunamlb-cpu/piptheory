/* nam-hedgefund dashboard JS — vanilla, no framework. */

(function () {
  "use strict";

  const cfg = window.__APP_CONFIG__ || {};

  // ----- Tabs -----
  const tabs = document.querySelectorAll(".tab");
  const panels = document.querySelectorAll(".tab-panel");
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const target = tab.dataset.tab;
      tabs.forEach((t) => t.classList.toggle("is-active", t === tab));
      panels.forEach((p) => {
        const isActive = p.id === "tab-" + target;
        p.classList.toggle("is-active", isActive);
        p.hidden = !isActive;
      });
    });
  });

  // ----- Run picker (date dropdown) -----
  const picker = document.getElementById("run-picker");
  if (picker) {
    picker.addEventListener("change", (e) => {
      const date = e.target.value;
      if (date) window.location.href = "/run/" + encodeURIComponent(date);
    });
  }

  // ----- Run-now button + status banner -----
  const runBtn = document.getElementById("run-now-btn");
  const banner = document.getElementById("run-status-banner");
  const stageEl = document.getElementById("run-stage");
  const elapsedEl = document.getElementById("run-elapsed");
  const pctEl = document.getElementById("run-pct");
  const pidEl = document.getElementById("run-pid");
  const barEl = document.getElementById("run-bar");
  const logEl = document.getElementById("run-log");
  const logToggle = document.getElementById("run-log-toggle");
  const lastUpdatedEl = document.getElementById("last-updated");

  let pollTimer = null;
  let logVisible = false;
  let wasRunning = false;
  // Latest completion timestamp at page load — used to detect 'a new run
  // finished' even if it was started outside this browser tab (cron task,
  // terminal, server restart, etc.)
  let initialCompletedAt = null;

  function setBannerKind(kind) {
    banner.className = "run-banner" + (kind ? " " + kind : "");
  }

  function fmtElapsed(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
  }

  function fmtRelativeTime(isoStr) {
    if (!isoStr) return "—";
    const t = new Date(isoStr);
    const now = new Date();
    const diffMs = now - t;
    const diffMin = Math.floor(diffMs / 60000);
    if (diffMin < 1) return "just now";
    if (diffMin < 60) return diffMin + " min ago";
    const diffHr = Math.floor(diffMin / 60);
    if (diffHr < 24) return diffHr + " hr ago";
    const diffDays = Math.floor(diffHr / 24);
    return diffDays + " day" + (diffDays !== 1 ? "s" : "") + " ago";
  }

  function setLastUpdated(latest) {
    if (!lastUpdatedEl) return;
    if (!latest || !latest.completed_at) {
      lastUpdatedEl.textContent = "—";
      return;
    }
    const t = new Date(latest.completed_at);
    const local = t.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    lastUpdatedEl.textContent = `${local} (${fmtRelativeTime(latest.completed_at)})`;
  }

  function showRunningBanner(data) {
    setBannerKind(null);
    banner.hidden = false;
    if (stageEl) stageEl.textContent = data.stage || "Running…";
    if (elapsedEl) elapsedEl.textContent = fmtElapsed(data.elapsed_seconds || 0);
    if (pctEl) pctEl.textContent = (data.estimated_pct || 0) + "%";
    if (pidEl) pidEl.textContent = "PID " + (data.pid || "?");
    if (barEl) barEl.style.width = (data.estimated_pct || 0) + "%";
  }

  function showCompletedBanner() {
    setBannerKind("success");
    if (stageEl) stageEl.textContent = "✓ Pipeline finished — refreshing to load the new brief…";
    if (pctEl) pctEl.textContent = "100%";
    if (barEl) barEl.style.width = "100%";
    if (logToggle) logToggle.style.display = "none";
  }

  function hideBanner() {
    banner.hidden = true;
  }

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

      // Capture the initial completion timestamp the first time we see one.
      const completed = (data.latest && data.latest.completed_at) || null;
      if (initialCompletedAt === null && completed) {
        initialCompletedAt = completed;
      }

      if (data.running) {
        showRunningBanner(data);
        if (logVisible) fetchLog();
        if (runBtn) {
          runBtn.disabled = true;
          runBtn.querySelector("span:last-child").textContent = "Running…";
        }
        // Start polling if we hit a running state from a static page load
        if (!pollTimer) startPolling();
        wasRunning = true;
      } else {
        // A run completed since this page loaded — pickup new data.
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
            runBtn.querySelector("span:last-child").textContent = "Run again";
          }
        }
      }
    } catch (e) {
      // transient — keep polling
    }
  }

  if (logToggle) {
    logToggle.addEventListener("click", () => {
      logVisible = !logVisible;
      if (logEl) logEl.hidden = !logVisible;
      logToggle.textContent = logVisible ? "Hide log" : "Show log";
      if (logVisible) fetchLog();
    });
  }

  if (runBtn) {
    runBtn.addEventListener("click", async () => {
      if (runBtn.disabled) return;
      const ok = confirm(
        "Run a fresh pipeline now?\n\n" +
        "This takes 10-15 minutes and ~$0.20.\n" +
        "It overwrites today's existing brief — only one run per date is kept.\n\n" +
        "Continue?"
      );
      if (!ok) return;
      runBtn.disabled = true;
      runBtn.querySelector("span:last-child").textContent = "Starting…";
      wasRunning = true;
      try {
        const r = await fetch("/api/run", { method: "POST" });
        const data = await r.json();
        if (r.ok) {
          startPolling();
        } else {
          banner.hidden = false;
          setBannerKind("error");
          stageEl.textContent = "Could not start: " + (data.detail || "unknown");
          runBtn.disabled = false;
          runBtn.querySelector("span:last-child").textContent = "Run analysis";
        }
      } catch (e) {
        banner.hidden = false;
        setBannerKind("error");
        stageEl.textContent = "Could not start: " + e.message;
        runBtn.disabled = false;
        runBtn.querySelector("span:last-child").textContent = "Run analysis";
      }
    });

    // Check on load — picks up an in-progress run started elsewhere (e.g. cron)
    checkStatus();
    // Light polling regardless — every 30s we refresh the "last updated"
    setInterval(checkStatus, 30000);
  }

  // ----- Ask (chat) -----
  const personaSelect = document.getElementById("persona-select");
  const askHelp = document.getElementById("ask-help");
  const chatHistory = document.getElementById("chat-history");
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const chatSend = document.getElementById("chat-send");
  const askClear = document.getElementById("ask-clear");

  // History stored per (run, persona) in localStorage
  function historyKey() {
    const persona = personaSelect ? personaSelect.value : "default";
    return "chat:" + cfg.runDate + ":" + persona;
  }
  function loadHistory() {
    try {
      const raw = localStorage.getItem(historyKey());
      return raw ? JSON.parse(raw) : [];
    } catch (e) { return []; }
  }
  function saveHistory(hist) {
    try { localStorage.setItem(historyKey(), JSON.stringify(hist)); } catch (e) {}
  }

  function escapeHTML(s) {
    return s
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }
  // very minimal markdown-ish rendering for chat (preserve newlines, code blocks)
  function lightFormat(s) {
    const escaped = escapeHTML(s);
    return escaped
      .replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>")
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br>");
  }

  function renderHistory() {
    if (!chatHistory) return;
    const hist = loadHistory();
    chatHistory.innerHTML = "";
    if (hist.length === 0) {
      const persona = personaSelect ? personaSelect.options[personaSelect.selectedIndex].text : "Default";
      const empty = document.createElement("div");
      empty.className = "muted";
      empty.style.fontSize = "13px";
      empty.style.padding = "16px 0";
      empty.textContent = "No questions yet. Ask " + persona + " anything about today's brief.";
      chatHistory.appendChild(empty);
      return;
    }
    hist.forEach((msg) => {
      const el = document.createElement("div");
      el.className = "chat-msg " + msg.role;
      const lbl = document.createElement("span");
      lbl.className = "role-label";
      lbl.textContent = msg.role === "user" ? "You" : (msg.persona || "Assistant");
      const body = document.createElement("div");
      body.innerHTML = lightFormat(msg.content);
      el.appendChild(lbl);
      el.appendChild(body);
      chatHistory.appendChild(el);
    });
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }

  function updateAskHelp() {
    if (!askHelp || !personaSelect) return;
    const personaKey = personaSelect.value;
    const personaLabel = personaSelect.options[personaSelect.selectedIndex].text;
    if (personaKey === "default") {
      askHelp.textContent = "Same context as the brief. Ask any question.";
    } else {
      askHelp.innerHTML = "Asking as <strong>" + personaLabel + "</strong>. Same context, different reasoning lens.";
    }
  }

  if (personaSelect) {
    personaSelect.addEventListener("change", () => {
      updateAskHelp();
      renderHistory();
    });
    updateAskHelp();
    renderHistory();
  }

  if (askClear) {
    askClear.addEventListener("click", () => {
      localStorage.removeItem(historyKey());
      renderHistory();
    });
  }

  if (chatForm) {
    chatForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!chatInput) return;
      const text = chatInput.value.trim();
      if (!text) return;

      const hist = loadHistory();
      hist.push({ role: "user", content: text });
      saveHistory(hist);
      chatInput.value = "";
      renderHistory();

      chatSend.disabled = true;
      chatSend.textContent = "Thinking…";

      try {
        const r = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            run_date: cfg.runDate,
            persona: personaSelect ? personaSelect.value : "default",
            history: hist,
          }),
        });
        const data = await r.json();
        if (r.ok) {
          const personaLabel = personaSelect ? personaSelect.options[personaSelect.selectedIndex].text : "Assistant";
          const updated = loadHistory();
          updated.push({
            role: "assistant",
            content: data.content,
            persona: personaLabel === "Default analyst" ? "Assistant" : personaLabel,
          });
          saveHistory(updated);
          renderHistory();
        } else {
          alert("Chat failed: " + (data.detail || "unknown"));
        }
      } catch (e) {
        alert("Chat failed: " + e.message);
      } finally {
        chatSend.disabled = false;
        chatSend.textContent = "Send";
      }
    });

    // Submit with Cmd/Ctrl+Enter
    chatInput.addEventListener("keydown", (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        chatForm.requestSubmit();
      }
    });
  }

  // ----- Positions -----
  // The active list and the closed journal are both rendered from a single
  // GET /api/positions call. We refresh on tab activation, after any
  // mutation (open/close/delete), and once on page load if the tab badge
  // would have a non-zero count.

  const positionsActive = document.getElementById("positions-active");
  const positionsBadge = document.getElementById("positions-badge");
  const positionsClosedList = document.getElementById("positions-closed-list");
  const positionsClosedSummary = document.getElementById("positions-closed-summary");
  const openForm = document.getElementById("open-position-form");
  const openStatus = document.getElementById("open-position-status");

  // Default the entry-date field to today.
  const entryDateInput = document.getElementById("pos-entry-date");
  if (entryDateInput) {
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, "0");
    const dd = String(today.getDate()).padStart(2, "0");
    entryDateInput.value = `${yyyy}-${mm}-${dd}`;
  }

  function fmtPnl(pct) {
    if (pct === null || pct === undefined) return "—";
    const sign = pct > 0 ? "+" : "";
    return `${sign}${pct.toFixed(2)}%`;
  }

  function actionLabel(action) {
    return {
      emergency_close: "EMERGENCY CLOSE",
      close: "Close",
      trim: "Trim",
      trail_stop: "Trail stop",
      review: "Review",
      hold: "Hold",
    }[action] || action;
  }

  function actionClass(action, urgency) {
    if (action === "emergency_close") return "pos-action-emergency";
    if (action === "close") return "pos-action-close";
    if (action === "trim") return "pos-action-trim";
    if (action === "trail_stop") return "pos-action-trail";
    if (action === "review") return "pos-action-review";
    return "pos-action-hold";
  }

  function buildPositionCard(item) {
    const p = item.position;
    const adv = item.advice;
    const cur = item.current_price;
    const pnl = adv ? adv.pnl_pct : null;
    const card = document.createElement("article");
    card.className = "card pos-card " + actionClass(adv && adv.action, adv && adv.urgency);
    card.dataset.positionId = p.id;

    // Header
    const head = document.createElement("header");
    head.className = "card-head";
    head.innerHTML = `
      <div class="card-id">
        <div class="card-symbol">${p.instrument}
          <span class="card-name">${p.direction.toUpperCase()} · entry ${p.entry_price}</span>
        </div>
      </div>
      <span class="pill pos-pill ${actionClass(adv && adv.action)}">
        ${actionLabel(adv && adv.action)}
      </span>
    `;
    card.appendChild(head);

    // Body
    const body = document.createElement("div");
    body.className = "card-body";
    // Build the metadata strip in plain language. Each line answers one
    // simple question the user might ask while glancing at the card:
    //   1. Where's my stop, and how close is price to it?
    //   2. Does the system still agree with the direction of my trade?
    //   3. Is the chart green-lit, on watch, or ugly today?
    //   4. (Reminder) why did I open this?
    const stopLine = p.emergency_stop
      ? `Stop level: ${p.emergency_stop}` + (adv && adv.stop_distance_pct !== null
          ? ` (price is ${adv.stop_distance_pct.toFixed(1)}% away)` : "")
      : "Stop level: not set";
    let macroLine;
    if (adv && adv.conviction_now) {
      const dir = adv.macro_aligned ? "still agrees with your trade" : "now LEANS THE OTHER WAY";
      let deltaText = "no change since you opened";
      if (adv.conviction_delta > 0) deltaText = `up ${adv.conviction_delta} since you opened`;
      else if (adv.conviction_delta < 0) deltaText = `down ${Math.abs(adv.conviction_delta)} since you opened`;
      macroLine = `System view today: ${dir} at ${adv.conviction_now}/10 confidence (${deltaText})`;
    } else {
      macroLine = "System view today: no fresh view (instrument fell below the council threshold this run)";
    }
    const filterLabels = {
      tradable_now: "green-lit (chart is at a clean spot)",
      watch: "on watch (wait for a cleaner spot before adding)",
      pass_despite_bias: "ugly (chart is fighting the trade)",
      below_threshold: "no chart check (system view too weak)",
      skip_no_data: "no chart data available",
      unparseable: "(chart check unavailable)",
    };
    const filterLine = adv && adv.filter_verdict_now
      ? `Chart check today: ${filterLabels[adv.filter_verdict_now] || adv.filter_verdict_now}`
      : "";
    body.innerHTML = `
      <div class="pos-stats">
        <div><span class="muted">Profit / loss</span> <strong>${fmtPnl(pnl)}</strong></div>
        <div><span class="muted">Price now</span> <strong>${cur ?? "—"}</strong></div>
        <div><span class="muted">Days open</span> <strong>${daysHeldFromEntry(p.entry_date)}</strong></div>
      </div>
      <p class="pos-advice"><strong>${actionLabel(adv && adv.action)}.</strong> ${escapeHTML(adv && adv.reason || "—")}</p>
      <div class="pos-meta">
        <div>${stopLine}</div>
        <div>${macroLine}</div>
        ${filterLine ? `<div>${filterLine}</div>` : ""}
        ${p.thesis_at_open ? `<div class="pos-thesis"><span class="muted">Why you opened it:</span> ${escapeHTML(p.thesis_at_open)}</div>` : ""}
        ${p.notes ? `<details class="pos-notes-block"><summary>Notes</summary><pre>${escapeHTML(p.notes)}</pre></details>` : ""}
      </div>
      <div class="pos-actions">
        <button type="button" class="btn btn-secondary btn-sm pos-close-btn" data-id="${p.id}">Mark closed</button>
        <button type="button" class="btn btn-secondary btn-sm pos-note-btn" data-id="${p.id}">Add note</button>
        ${p.emergency_stop !== null
            ? `<button type="button" class="btn btn-secondary btn-sm pos-stop-btn" data-id="${p.id}">Move stop</button>`
            : `<button type="button" class="btn btn-secondary btn-sm pos-stop-btn" data-id="${p.id}">Set stop</button>`}
        <button type="button" class="btn btn-ghost btn-sm pos-delete-btn" data-id="${p.id}">Delete</button>
      </div>
    `;
    card.appendChild(body);
    return card;
  }

  function daysHeldFromEntry(entryDate) {
    if (!entryDate) return 0;
    const d = new Date(entryDate);
    if (isNaN(d.getTime())) return 0;
    const ms = Date.now() - d.getTime();
    return Math.max(0, Math.floor(ms / 86400000));
  }

  function buildClosedRow(p) {
    const li = document.createElement("li");
    li.className = "pos-closed-row";
    const sign = (p.pnl_pct || 0) >= 0 ? "pos-win" : "pos-loss";
    li.innerHTML = `
      <div class="pos-closed-row-head">
        <span class="pos-closed-symbol">${p.instrument}</span>
        <span class="pos-closed-dir">${p.direction.toUpperCase()}</span>
        <span class="pos-closed-pnl ${sign}">${fmtPnl(p.pnl_pct)}</span>
        <span class="muted pos-closed-dates">${p.entry_date} → ${p.close_date || "—"}</span>
      </div>
      <div class="pos-closed-prices muted">
        Entry ${p.entry_price} → Close ${p.close_price ?? "—"}
        ${p.close_reason ? ` · ${escapeHTML(p.close_reason)}` : ""}
      </div>
    `;
    return li;
  }

  async function refreshPositions() {
    if (!positionsActive) return;
    try {
      const r = await fetch("/api/positions");
      const data = await r.json();
      const active = data.active || [];
      const closed = data.closed_recent || [];

      // Active list
      positionsActive.innerHTML = "";
      if (active.length === 0) {
        positionsActive.innerHTML = `
          <div class="positions-empty-card">
            <p class="muted" style="margin-top: 0;">
              You have no open trades recorded yet. Once you take a trade on
              FTMO and fill in the form below, it'll show up here as a card
              that tells you what the system thinks you should do with it.
            </p>
            <details class="collapse">
              <summary style="font-size: 13px;">See an example of what a trade card looks like</summary>
              <article class="card pos-card pos-action-hold" style="margin-top: 10px;">
                <header class="card-head">
                  <div class="card-id">
                    <div class="card-symbol">GC <span class="card-name">LONG · entry 4500</span></div>
                  </div>
                  <span class="pill pos-pill pos-action-hold">Hold</span>
                </header>
                <div class="card-body">
                  <div class="pos-stats">
                    <div><span class="muted">Profit / loss</span> <strong>+4.4%</strong></div>
                    <div><span class="muted">Price now</span> <strong>4697.40</strong></div>
                    <div><span class="muted">Days open</span> <strong>3</strong></div>
                  </div>
                  <p class="pos-advice">
                    <strong>Hold.</strong> Trade is on track — system still
                    leans long at 6/10, same as when you opened. Up 4.4%.
                  </p>
                  <div class="pos-meta">
                    <div>Stop level: 4400 (price is 6.3% above it)</div>
                    <div>System view today: still long, 6/10 confidence (no change since open)</div>
                    <div>Chart check today: "watch" — wait for cleaner pullback if adding</div>
                    <div class="pos-thesis"><span class="muted">Why you opened it:</span> Central bank buying and stagflation backdrop make gold a directional long for the next few months.</div>
                  </div>
                </div>
              </article>
              <p class="muted" style="font-size: 12px; margin-top: 10px;">
                Above is what a healthy trade looks like. The coloured pill in
                the top-right is the system's suggestion — read the help section
                up top for what each colour and word means.
              </p>
            </details>
          </div>
        `;
      } else {
        active.forEach((item) => positionsActive.appendChild(buildPositionCard(item)));
      }

      // Tab badge
      if (positionsBadge) {
        positionsBadge.textContent = String(active.length);
        positionsBadge.hidden = active.length === 0;
        // Highlight if any position has high-urgency advice
        const hasUrgent = active.some((it) => it.advice && it.advice.urgency === "high");
        positionsBadge.classList.toggle("tab-badge-urgent", hasUrgent);
      }

      // Closed journal
      if (positionsClosedList) {
        positionsClosedList.innerHTML = "";
        closed.forEach((p) => positionsClosedList.appendChild(buildClosedRow(p)));
      }
      if (positionsClosedSummary) {
        if (closed.length === 0) {
          positionsClosedSummary.textContent = " (no closed trades yet)";
        } else {
          const wins = closed.filter((p) => (p.pnl_pct || 0) >= 0).length;
          const total = closed.length;
          positionsClosedSummary.textContent =
            ` · ${total} trade${total !== 1 ? "s" : ""} · ${wins}W ${total - wins}L`;
        }
      }
    } catch (e) {
      console.error("Failed to load positions", e);
    }
  }

  // Hook up form submission
  if (openForm) {
    openForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fd = new FormData(openForm);
      const payload = {
        instrument: fd.get("instrument"),
        direction: fd.get("direction"),
        entry_price: parseFloat(fd.get("entry_price")),
        entry_date: fd.get("entry_date") || null,
        size_units: fd.get("size_units") ? parseFloat(fd.get("size_units")) : null,
        emergency_stop: fd.get("emergency_stop") ? parseFloat(fd.get("emergency_stop")) : null,
        notes: fd.get("notes") || "",
        snapshot_run_date: fd.get("snapshot_run_date") || null,
      };
      if (openStatus) openStatus.textContent = "Saving…";
      try {
        const r = await fetch("/api/positions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await r.json();
        if (r.ok) {
          if (openStatus) openStatus.textContent = "Saved.";
          openForm.reset();
          if (entryDateInput) {
            const t = new Date();
            entryDateInput.value =
              `${t.getFullYear()}-${String(t.getMonth() + 1).padStart(2, "0")}-${String(t.getDate()).padStart(2, "0")}`;
          }
          // Collapse the form panel
          const formDetails = openForm.closest("details");
          if (formDetails) formDetails.open = false;
          await refreshPositions();
        } else {
          if (openStatus) openStatus.textContent = "Failed: " + (data.detail || "unknown");
        }
      } catch (e) {
        if (openStatus) openStatus.textContent = "Failed: " + e.message;
      }
    });
  }

  // Action button handler — delegated from the active list container so
  // dynamically rendered cards work without per-card listener wiring.
  if (positionsActive) {
    positionsActive.addEventListener("click", async (e) => {
      const btn = e.target.closest("button");
      if (!btn) return;
      const id = btn.dataset.id;
      if (!id) return;

      if (btn.classList.contains("pos-close-btn")) {
        const priceStr = prompt("Close price?");
        if (priceStr === null) return;
        const price = parseFloat(priceStr);
        if (!isFinite(price) || price <= 0) {
          alert("Invalid price");
          return;
        }
        const reason = prompt("Close reason (optional — e.g. 'macro flipped', 'stop hit', 'taking profit'):", "") || "";
        const r = await fetch(`/api/positions/${id}/close`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ close_price: price, close_reason: reason }),
        });
        if (r.ok) refreshPositions();
        else alert("Close failed: " + (await r.text()));
        return;
      }

      if (btn.classList.contains("pos-note-btn")) {
        const note = prompt("Add a note (timestamped):");
        if (!note) return;
        const r = await fetch(`/api/positions/${id}/note`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ note }),
        });
        if (r.ok) refreshPositions();
        return;
      }

      if (btn.classList.contains("pos-stop-btn")) {
        const lvl = prompt("New emergency stop level:");
        if (lvl === null) return;
        const v = parseFloat(lvl);
        if (!isFinite(v) || v <= 0) { alert("Invalid level"); return; }
        const r = await fetch(`/api/positions/${id}/stop`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ emergency_stop: v }),
        });
        if (r.ok) refreshPositions();
        return;
      }

      if (btn.classList.contains("pos-delete-btn")) {
        const ok = confirm(
          "Delete this position record?\n\n" +
          "Use this only if it was opened by mistake. " +
          "If you actually closed the trade, use 'Mark closed' instead so it goes to the journal."
        );
        if (!ok) return;
        const r = await fetch(`/api/positions/${id}`, { method: "DELETE" });
        if (r.ok) refreshPositions();
      }
    });
  }

  // Refresh when the Positions tab is activated; also once on page load
  // so the tab badge reflects state without requiring a click first.
  document.querySelectorAll('.tab[data-tab="positions"]').forEach((t) => {
    t.addEventListener("click", refreshPositions);
  });

  // The hero "Review →" link in the position alert banner — clicking it
  // should jump to the Positions tab without navigating away.
  document.querySelectorAll('[data-tab-jump]').forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const target = link.dataset.tabJump;
      const targetTab = document.querySelector(`.tab[data-tab="${target}"]`);
      if (targetTab) targetTab.click();
      const panel = document.getElementById("tab-" + target);
      if (panel) panel.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  refreshPositions();
})();
