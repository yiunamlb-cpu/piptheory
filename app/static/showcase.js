/* nam-hedgefund — showcase surface enhancements.
   Loads after app.js so it can hook into elements the main app already
   rendered. Adds:
     - Animated count-up on hero stat numbers
     - SVG polyline points for the tile sparklines (the elements ship as
       empty <polyline> in markup; we set the points attr on load)
     - Subtle hover-tilt on tiles (CSS handles the basics; we add a
       small mouse-position-aware highlight overlay)
*/

(function () {
  "use strict";

  // ─── Count-up animation for hero stats ────────────────────────────
  document.querySelectorAll("[data-counter]").forEach((el) => {
    const target = parseFloat(el.dataset.counter || "0");
    if (!isFinite(target) || target <= 0) return;
    const duration = 800;
    const start = performance.now();
    function tick(now) {
      const t = Math.min(1, (now - start) / duration);
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - t, 3);
      const value = Math.round(target * eased);
      el.textContent = String(value);
      if (t < 1) requestAnimationFrame(tick);
      else el.textContent = String(target);
    }
    el.textContent = "0";
    requestAnimationFrame(tick);
  });

  // ─── Tile sparkline polylines ─────────────────────────────────────
  document.querySelectorAll(".sc-tile-spark").forEach((svg) => {
    let convs;
    try { convs = JSON.parse(svg.dataset.convictions || "[]"); }
    catch (e) { return; }
    if (!convs || convs.length < 2) return;
    const W = 100, H = 32, PAD = 2;
    const minV = 0, maxV = 10;
    const stepX = (W - 2 * PAD) / (convs.length - 1);
    const pts = convs.map((v, i) => {
      const x = PAD + i * stepX;
      const y = H - PAD - ((v - minV) / (maxV - minV)) * (H - 2 * PAD);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(" ");
    const line = svg.querySelector("polyline.line");
    if (line) line.setAttribute("points", pts);
  });

  // ─── Tile hover light effect (mouse-position aware glow) ──────────
  document.querySelectorAll(".sc-tile, .sc-pos").forEach((tile) => {
    tile.addEventListener("mousemove", (e) => {
      const rect = tile.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      tile.style.background = `radial-gradient(circle at ${x}% ${y}%, rgba(255,255,255,0.04), rgba(20,22,32,0.65) 50%)`;
    });
    tile.addEventListener("mouseleave", () => {
      tile.style.background = "";
    });
  });
})();
