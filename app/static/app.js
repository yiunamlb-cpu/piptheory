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
  let pollTimer = null;

  function showBanner(msg, kind) {
    if (!banner) return;
    banner.textContent = msg;
    banner.className = "run-banner" + (kind ? " " + kind : "");
    banner.hidden = false;
  }
  function hideBanner() {
    if (!banner) return;
    banner.hidden = true;
  }

  function startPolling() {
    if (pollTimer) return;
    pollTimer = setInterval(checkStatus, 5000);
    checkStatus();
  }
  function stopPolling() {
    if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
  }

  async function checkStatus() {
    try {
      const r = await fetch("/api/run/status");
      const data = await r.json();
      if (data.running) {
        const m = Math.floor(data.elapsed_seconds / 60);
        const s = data.elapsed_seconds % 60;
        const mm = String(m).padStart(2, "0");
        const ss = String(s).padStart(2, "0");
        showBanner(`⏳ Pipeline running · PID ${data.pid} · ${mm}:${ss} elapsed · refresh page when complete`, null);
        if (runBtn) {
          runBtn.disabled = true;
          runBtn.querySelector("span:last-child").textContent = "Running…";
        }
      } else {
        if (runBtn && runBtn.disabled) {
          // Just finished
          showBanner("✓ Pipeline finished. Refresh to load the new run.", null);
          setTimeout(() => location.reload(), 1500);
          stopPolling();
        } else {
          stopPolling();
          hideBanner();
        }
      }
    } catch (e) {
      // ignore transient
    }
  }

  if (runBtn) {
    runBtn.addEventListener("click", async () => {
      if (runBtn.disabled) return;
      runBtn.disabled = true;
      runBtn.querySelector("span:last-child").textContent = "Starting…";
      try {
        const r = await fetch("/api/run", { method: "POST" });
        const data = await r.json();
        if (r.ok) {
          showBanner("⏳ Pipeline started · PID " + data.pid, null);
          startPolling();
        } else {
          showBanner("Could not start: " + (data.detail || "unknown"), "error");
          runBtn.disabled = false;
          runBtn.querySelector("span:last-child").textContent = "Run analysis";
        }
      } catch (e) {
        showBanner("Could not start: " + e.message, "error");
        runBtn.disabled = false;
        runBtn.querySelector("span:last-child").textContent = "Run analysis";
      }
    });

    // Check on load — maybe a run is already in progress
    checkStatus();
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
