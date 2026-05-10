/* nam-hedgefund — showcase surface (graph dashboard).

   Loads after app.js. Builds the force-directed instrument↔theme
   graph, renders into #sc-graph, wires hover/click selection,
   updates the floating detail panel, and tails /api/run/log into the
   bottom terminal strip.

   Force simulation: lightweight Verlet-style with three forces:
     - Spring on every edge (link length × 1.0)
     - Coulomb-like repulsion on every node pair (decays with 1/r²)
     - Gentle gravity toward viewport center
   Runs at 60fps for ~2s on load to settle, then switches to a
   low-energy drift. Mouse-drag pans the graph. */

(function () {
  "use strict";

  const cfg = window.__APP_CONFIG__ || {};
  const surface = cfg.surface || "desktop";
  if (surface !== "showcase") return;
  const graphData = cfg.graph || { nodes: [], edges: [] };

  // ─── Count-up animation for hero stats ────────────────────────────
  document.querySelectorAll("[data-counter]").forEach((el) => {
    const target = parseFloat(el.dataset.counter || "0");
    if (!isFinite(target) || target <= 0) return;
    const duration = 700;
    const start = performance.now();
    function tick(now) {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      el.textContent = String(Math.round(target * eased));
      if (t < 1) requestAnimationFrame(tick);
      else el.textContent = String(target);
    }
    el.textContent = "0";
    requestAnimationFrame(tick);
  });

  // ─── Graph rendering ──────────────────────────────────────────────
  const svg = document.getElementById("sc-graph");
  const edgesG = document.getElementById("gn-edges");
  const nodesG = document.getElementById("gn-nodes");
  const detail = document.getElementById("sc-graph-detail");
  if (!svg || !graphData.nodes.length) return;

  // Color helpers
  const nodeColor = (n) => {
    if (n.type === "theme") return getComputedStyle(document.documentElement).getPropertyValue("--node-theme").trim() || "#c2410c";
    if (n.kind === "long")  return getComputedStyle(document.documentElement).getPropertyValue("--node-long").trim()  || "#0d9488";
    if (n.kind === "short") return getComputedStyle(document.documentElement).getPropertyValue("--node-short").trim() || "#dc2626";
    return getComputedStyle(document.documentElement).getPropertyValue("--node-neutral").trim() || "#78716c";
  };

  // Initialise positions in a spiral so simulation starts in a non-degenerate state
  const W = svg.clientWidth || 800;
  const H = svg.clientHeight || 600;
  const nodes = graphData.nodes.map((n, i) => {
    const angle = (i / graphData.nodes.length) * Math.PI * 2;
    const r = (i % 2 === 0 ? 180 : 240);
    return {
      ...n,
      x: W / 2 + r * Math.cos(angle),
      y: H / 2 + r * Math.sin(angle),
      vx: 0, vy: 0,
      pinned: false,
    };
  });
  const nodesById = new Map(nodes.map(n => [n.id, n]));
  // Filter edges to only those whose endpoints both exist (defensive)
  const edges = graphData.edges
    .map((e) => ({
      source: nodesById.get(e.source),
      target: nodesById.get(e.target),
      weight: e.weight || 1,
    }))
    .filter((e) => e.source && e.target);

  // Compute neighbour set for hover-highlight
  const neighbours = new Map(); // node.id -> Set of neighbour ids
  nodes.forEach(n => neighbours.set(n.id, new Set()));
  edges.forEach(e => {
    neighbours.get(e.source.id).add(e.target.id);
    neighbours.get(e.target.id).add(e.source.id);
  });

  // ─── Force simulation ────────────────────────────────────────────
  // Tunable parameters — keep gentle so the graph drifts slowly.
  const REPULSION = 1800;          // pairwise inverse-square
  const SPRING_K = 0.025;          // edge spring stiffness
  const SPRING_REST = 110;         // rest length per edge
  const GRAVITY = 0.018;           // pull toward center
  const FRICTION_HOT = 0.78;       // drag during settling
  const FRICTION_COOL = 0.92;      // drag after settling
  const HOT_FRAMES = 200;          // initial settling frames
  const MAX_VEL = 12;

  let frame = 0;

  function simulate() {
    const friction = frame < HOT_FRAMES ? FRICTION_HOT : FRICTION_COOL;
    const cx = svg.clientWidth / 2;
    const cy = svg.clientHeight / 2;

    // Gravity
    for (const n of nodes) {
      n.vx += (cx - n.x) * GRAVITY;
      n.vy += (cy - n.y) * GRAVITY;
    }

    // Repulsion (O(n²) — fine for ~20 nodes)
    for (let i = 0; i < nodes.length; i++) {
      const a = nodes[i];
      for (let j = i + 1; j < nodes.length; j++) {
        const b = nodes[j];
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const distSq = Math.max(40, dx * dx + dy * dy);
        const force = REPULSION / distSq;
        const d = Math.sqrt(distSq);
        const fx = (dx / d) * force;
        const fy = (dy / d) * force;
        a.vx += fx; a.vy += fy;
        b.vx -= fx; b.vy -= fy;
      }
    }

    // Spring on edges
    for (const e of edges) {
      const dx = e.target.x - e.source.x;
      const dy = e.target.y - e.source.y;
      const d = Math.sqrt(dx * dx + dy * dy) || 0.0001;
      const f = SPRING_K * (d - SPRING_REST);
      const fx = (dx / d) * f;
      const fy = (dy / d) * f;
      e.source.vx += fx; e.source.vy += fy;
      e.target.vx -= fx; e.target.vy -= fy;
    }

    // Integrate
    for (const n of nodes) {
      if (n.pinned) continue;
      n.vx = Math.max(-MAX_VEL, Math.min(MAX_VEL, n.vx));
      n.vy = Math.max(-MAX_VEL, Math.min(MAX_VEL, n.vy));
      n.x += n.vx;
      n.y += n.vy;
      n.vx *= friction;
      n.vy *= friction;
      // Soft viewport bounds
      const margin = 60;
      n.x = Math.max(margin, Math.min(svg.clientWidth - margin, n.x));
      n.y = Math.max(margin, Math.min(svg.clientHeight - margin, n.y));
    }

    frame++;
  }

  // ─── DOM construction ───────────────────────────────────────────
  // Edges as quadratic-bezier paths (curved) for the MiroFish look
  const edgeEls = edges.map((e) => {
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("class", "gn-edge");
    edgesG.appendChild(path);
    return { e, path };
  });

  const nodeEls = nodes.map((n) => {
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    g.setAttribute("class", `gn-node-group ${n.type}${n.is_open_position ? " position" : ""}`);
    g.setAttribute("data-id", n.id);

    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("class", "gn-node-circle");
    circle.setAttribute("r", n.size);
    circle.setAttribute("fill", nodeColor(n));
    g.appendChild(circle);

    // Label only for instrument nodes (themes are too verbose)
    if (n.type === "instrument") {
      const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
      text.setAttribute("class", "gn-node-label");
      text.setAttribute("dy", n.size + 14);
      text.textContent = n.label;
      g.appendChild(text);
    } else {
      const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
      text.setAttribute("class", "gn-node-label");
      text.setAttribute("dy", n.size + 14);
      // Truncate theme labels
      text.textContent = n.label.length > 30 ? n.label.slice(0, 28) + "…" : n.label;
      text.style.fontSize = "9px";
      g.appendChild(text);
    }

    nodesG.appendChild(g);
    return { n, g, circle };
  });

  // ─── Render loop ────────────────────────────────────────────────
  function render() {
    // Reposition edges
    for (const { e, path } of edgeEls) {
      const mx = (e.source.x + e.target.x) / 2;
      const my = (e.source.y + e.target.y) / 2;
      // Curve offset perpendicular to the line for the "fanned" look
      const dx = e.target.x - e.source.x;
      const dy = e.target.y - e.source.y;
      const len = Math.sqrt(dx * dx + dy * dy) || 1;
      const px = -dy / len * 16;  // perpendicular offset
      const py = dx / len * 16;
      const cx = mx + px;
      const cy = my + py;
      path.setAttribute("d", `M ${e.source.x.toFixed(1)} ${e.source.y.toFixed(1)} Q ${cx.toFixed(1)} ${cy.toFixed(1)} ${e.target.x.toFixed(1)} ${e.target.y.toFixed(1)}`);
    }
    // Reposition nodes
    for (const { n, g } of nodeEls) {
      g.setAttribute("transform", `translate(${n.x.toFixed(1)}, ${n.y.toFixed(1)})`);
    }
  }

  function loop() {
    simulate();
    render();
    requestAnimationFrame(loop);
  }
  loop();

  // ─── Resize handler — reset center and viewBox ──────────────────
  function fitSvg() {
    svg.setAttribute("viewBox", `0 0 ${svg.clientWidth} ${svg.clientHeight}`);
  }
  fitSvg();
  window.addEventListener("resize", fitSvg);

  // ─── Selection / hover / detail panel ───────────────────────────
  let selectedId = null;
  let hoveredId = null;

  function applyHighlight() {
    const active = hoveredId || selectedId;
    if (!active) {
      nodeEls.forEach(({ g }) => g.classList.remove("dimmed", "active"));
      edgeEls.forEach(({ path }) => path.classList.remove("active"));
      return;
    }
    const nbr = neighbours.get(active) || new Set();
    nodeEls.forEach(({ n, g }) => {
      g.classList.toggle("active", n.id === active);
      g.classList.toggle("dimmed", n.id !== active && !nbr.has(n.id));
    });
    edgeEls.forEach(({ e, path }) => {
      const involved = e.source.id === active || e.target.id === active;
      path.classList.toggle("active", involved);
    });
  }

  function showDetail(node) {
    detail.classList.remove("hidden");
    const kind = document.getElementById("sc-detail-kind");
    const conn = document.getElementById("sc-detail-conn");
    const title = document.getElementById("sc-detail-title");
    const sub = document.getElementById("sc-detail-sub");
    const rows = document.getElementById("sc-detail-rows");
    const actions = document.getElementById("sc-detail-actions");
    const why = document.getElementById("sc-detail-why");

    const nbrCount = (neighbours.get(node.id) || new Set()).size;
    kind.textContent = node.type === "theme" ? "MACRO THEME" : "INSTRUMENT";
    conn.textContent = `${nbrCount} link${nbrCount !== 1 ? "s" : ""}`;
    title.textContent = node.label;
    sub.textContent = node.subtitle || (node.type === "theme" ? "active theme" : "");

    let html = "";
    if (node.type === "instrument") {
      html += `<div class="sc-detail-row"><span class="lbl">Direction</span><span class="val">${node.kind.toUpperCase()}</span></div>`;
      html += `<div class="sc-detail-row"><span class="lbl">Conviction</span><span class="val">${node.conviction}/10</span></div>`;
      if (node.is_open_position) {
        html += `<div class="sc-detail-row"><span class="lbl">Position</span><span class="val" style="color: var(--accent);">● OPEN</span></div>`;
      }
    } else {
      html += `<div class="sc-detail-row"><span class="lbl">Conviction</span><span class="val">${node.conviction}/10</span></div>`;
      html += `<div class="sc-detail-row"><span class="lbl">Linked instruments</span><span class="val">${nbrCount}</span></div>`;
    }
    rows.innerHTML = html;

    if (node.type === "instrument") {
      actions.hidden = false;
      why.dataset.symbol = node.label;
    } else {
      actions.hidden = true;
    }
  }

  function hideDetail() { detail.classList.add("hidden"); }

  // Hover handlers
  nodeEls.forEach(({ n, g }) => {
    g.addEventListener("mouseenter", () => {
      hoveredId = n.id;
      applyHighlight();
    });
    g.addEventListener("mouseleave", () => {
      hoveredId = null;
      applyHighlight();
    });
    g.addEventListener("click", (e) => {
      e.stopPropagation();
      if (selectedId === n.id) {
        selectedId = null;
        hideDetail();
        applyHighlight();
      } else {
        selectedId = n.id;
        showDetail(n);
        applyHighlight();
      }
    });
  });

  // Click empty SVG to clear
  svg.addEventListener("click", () => {
    selectedId = null;
    hideDetail();
    applyHighlight();
  });

  // Graph controls
  document.querySelectorAll("[data-action='graph-reheat']").forEach(btn => {
    btn.addEventListener("click", () => {
      frame = 0;
      // Add small random kick to all nodes
      for (const n of nodes) {
        n.vx += (Math.random() - 0.5) * 8;
        n.vy += (Math.random() - 0.5) * 8;
      }
    });
  });
  document.querySelectorAll("[data-action='graph-reset']").forEach(btn => {
    btn.addEventListener("click", () => {
      selectedId = null;
      hoveredId = null;
      hideDetail();
      applyHighlight();
    });
  });

  // ─── Live log ticker ───────────────────────────────────────────
  // Polls /api/run/log periodically and prepends new lines to the
  // terminal strip. Format-detects [info/warn/error] markers and
  // colorises accordingly.

  const termBody = document.getElementById("sc-term-body");
  const termMeta = document.getElementById("sc-term-meta");
  let lastSeen = new Set();

  function formatLogLine(line) {
    // Try to parse the structlog format: "<ts> [<level>     ] <event>"
    let cls = "";
    if (/\[error/i.test(line)) cls = "error";
    else if (/\[warning/i.test(line)) cls = "warn";

    // Highlight key=value pairs
    const formatted = line
      .replace(/^([\d\-: ]+)/, '<span class="ts">$1</span>')
      .replace(/(\b[a-z_]+)=/g, '<span class="key">$1</span>=');
    return { cls, html: formatted };
  }

  async function pollLog() {
    try {
      const r = await fetch("/api/run/log?lines=50");
      const data = await r.json();
      const lines = data.lines || [];
      // Find which lines are new (we stringify-set whole lines as keys)
      const newLines = lines.filter((l) => !lastSeen.has(l));
      if (newLines.length === 0) return;
      lastSeen = new Set(lines.slice(-100));
      // Render: we want newest at the bottom (terminal-like)
      termBody.innerHTML = "";
      lines.slice(-30).forEach((line) => {
        const { cls, html } = formatLogLine(line);
        const span = document.createElement("span");
        span.className = "sc-term-line" + (cls ? " " + cls : "");
        span.innerHTML = html;
        termBody.appendChild(span);
      });
      termBody.scrollTop = termBody.scrollHeight;
      if (termMeta) termMeta.textContent = `${lines.length} lines · live`;
    } catch (e) {
      // Quietly ignore — banner already surfaces if dashboard's down
    }
  }
  pollLog();
  setInterval(pollLog, 5000);
})();
