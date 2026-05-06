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

      if (data.running) {
        showRunningBanner(data);
        if (logVisible) fetchLog();
        if (runBtn) {
          runBtn.disabled = true;
          runBtn.querySelector("span:last-child").textContent = "Running…";
        }
        wasRunning = true;
      } else {
        if (wasRunning) {
          showCompletedBanner();
          setTimeout(() => location.reload(), 1500);
          stopPolling();
        } else {
          stopPolling();
          hideBanner();
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
})();
