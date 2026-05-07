/* nam-hedgefund dashboard JS — single file, branches by surface.

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
  if (runBtn) {
    runBtn.addEventListener("click", async () => {
      if (runBtn.disabled) return;
      const ok = confirm("Run a fresh pipeline now?\n\n10-15 min · ~$0.20.\nOverwrites today's brief.");
      if (!ok) return;
      runBtn.disabled = true;
      runBtn.textContent = "Starting…";
      wasRunning = true;
      try {
        const r = await fetch("/api/run", { method: "POST" });
        if (r.ok) startPolling();
        else {
          alert("Could not start run: " + (await r.text()));
          runBtn.disabled = false;
          runBtn.textContent = "▶ Run again";
        }
      } catch (e) {
        alert("Could not start run: " + e.message);
        runBtn.disabled = false;
        runBtn.textContent = "▶ Run again";
      }
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
        <h4>The numbers</h4>
        <ul>
          <li>Entry: ${p.entry_price} on ${p.entry_date}</li>
          <li>Current: ${item.current_price ?? "—"}</li>
          <li>P&amp;L: ${fmtPnl(adv.pnl_pct)}</li>
          ${p.emergency_stop ? `<li>Stop: ${p.emergency_stop} (${adv.stop_distance_pct ? adv.stop_distance_pct.toFixed(1) + "% away" : "—"})</li>` : ""}
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
        const data = await r.json();
        if (r.ok) {
          const updated = loadChatHist();
          const personaLabel = personaSel
            ? personaSel.options[personaSel.selectedIndex].text
            : "Assistant";
          updated.push({ role: "assistant", content: data.content, persona: personaLabel === "Default analyst" ? "Assistant" : personaLabel });
          saveChatHist(updated);
          renderChatHist();
        } else {
          alert("Chat failed: " + (data.detail || "unknown"));
        }
      } catch (err) { alert("Chat failed: " + err.message); }
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
    const items = (cfg.instruments || []).map(r => `
      <li class="${r.is_open_position ? "has-position" : ""}" data-symbol="${r.symbol}" data-action="why-instrument">
        <span class="symbol">${r.symbol}</span>
        <div class="meta">
          ${escapeHTML(r.direction_raw || "—")}<br>
          <span class="muted">${escapeHTML(r.state)}</span>
        </div>
        <span class="muted">${r.conviction}/10</span>
      </li>
    `).join("");
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
      case "run-now":             e.preventDefault(); closeAll(); if (runBtn) runBtn.click(); break;
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
})();
