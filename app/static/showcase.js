/* nam-hedgefund — showcase surface enhancements (MiroFish-style edition).
   Loads after app.js. Adds:
     - Animated count-up on hero stat numbers
     - SVG polyline points for matrix sparklines (.sc-spark)
     - Subtle row hover (table tr underline-on-hover via JS not needed —
       CSS handles it)
*/

(function () {
  "use strict";

  // ─── Count-up animation for hero stats ────────────────────────────
  document.querySelectorAll("[data-counter]").forEach((el) => {
    const target = parseFloat(el.dataset.counter || "0");
    if (!isFinite(target) || target <= 0) return;
    const duration = 900;
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

  // ─── Matrix sparkline polylines ───────────────────────────────────
  document.querySelectorAll(".sc-spark").forEach((svg) => {
    let convs;
    try { convs = JSON.parse(svg.dataset.convictions || "[]"); }
    catch (e) { return; }
    if (!convs || convs.length < 2) return;
    const W = 100, H = 28, PAD = 2;
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
})();
