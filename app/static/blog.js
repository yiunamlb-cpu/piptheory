/* ============================================================
   blog.js — declarative SVG chart renderer for research posts.
   Authors write a <figure class="pt-chart" data-chart='{...}'> and
   this renders a clean, consistent, theme-aware chart with proper
   margins (no label/line overlap), axes, gridlines, point markers,
   an HTML legend, optional annotations, and a draw-in animation.
   Renders client-side (works on the static build); the <figcaption>
   stays as the no-JS fallback. No dependencies.
   ============================================================ */
(function () {
  "use strict";
  var PAL = { USD:"#2563EB", EUR:"#0D9488", GBP:"#7C3AED", JPY:"#E11D48",
              CHF:"#CA8A04", CAD:"#16A34A", AUD:"#DB2777", NZD:"#0891B2",
              gold:"#CA8A04", oil:"#16A34A", up:"#12A150", down:"#E23636",
              a:"#2563EB", b:"#CA8A04", c:"#0D9488", d:"#7C3AED" };
  function css(v, f){ var x=getComputedStyle(document.documentElement).getPropertyValue(v).trim(); return x||f; }
  function niceMax(v){ if(v<=0) return 1; var p=Math.pow(10,Math.floor(Math.log10(v))); var f=v/p;
    var n=f<=1?1:f<=2?2:f<=2.5?2.5:f<=5?5:10; return n*p; }
  function niceNum(range, round){ if(range<=0) return 1; var e=Math.floor(Math.log10(range)); var f=range/Math.pow(10,e);
    var nf = round ? (f<1.5?1:f<3?2:f<7?5:10) : (f<=1?1:f<=2?2:f<=5?5:10); return nf*Math.pow(10,e); }
  function fmt(n){ var a=Math.abs(n); if(a>=1000) return (n/1000).toFixed(a>=10000?0:1)+"k";
    return (Math.round(n*100)/100).toString(); }
  function esc(s){ return String(s).replace(/[&<>]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;"}[c];}); }

  function render(fig){
    var spec; try { spec = JSON.parse(fig.getAttribute("data-chart")); } catch(e){ return; }
    var type = spec.type || "line";
    var W = 640, H = spec.height || 320;
    var m = { l: 50, r: type==="hbar" ? 16 : 54, t: 16, b: 34 };
    var grid = css("--border-2","#e5e7eb"), axis = css("--border-3","#c0c6ce"),
        txt = css("--text-faint","#8a93a3"), bg = css("--bg-1","#fff"), ink = css("--text","#1a1d26");
    var pw = W - m.l - m.r, ph = H - m.t - m.b;
    var svg = ['<svg viewBox="0 0 '+W+' '+H+'" role="img" preserveAspectRatio="xMidYMid meet" aria-label="'+esc(spec.alt||spec.caption||"chart")+'">'];
    var defs = '';

    var series = spec.series || [];
    series.forEach(function(s,i){ if(!s.color) s.color = PAL[s.name] || [PAL.a,PAL.b,PAL.c,PAL.d][i%4]; });

    if (type === "bar" || type === "hbar") {
      // ---- BAR ----
      var cats = spec.x || series.map(function(s){return s.name;});
      var vals = (type==="bar"||type==="hbar") && series.length===1 ? series[0].data
                 : cats.map(function(_,i){ return series[0] ? series[0].data[i] : 0; });
      var mx = niceMax(Math.max.apply(null, vals.map(Math.abs)));
      if (type === "hbar") {
        var bh = ph / cats.length;
        for (var t=0;t<=4;t++){ var gx=m.l+pw*t/4; svg.push('<line x1="'+gx+'" y1="'+m.t+'" x2="'+gx+'" y2="'+(m.t+ph)+'" stroke="'+grid+'" stroke-width="1"/>');
          svg.push('<text x="'+gx+'" y="'+(H-12)+'" fill="'+txt+'" font-size="11" font-family="monospace" text-anchor="middle">'+fmt(mx*t/4)+(spec.suffix||'')+'</text>'); }
        cats.forEach(function(c,i){ var v=vals[i], y=m.t+bh*i+bh*0.2, w=Math.max(1,Math.abs(v)/mx*pw), h=bh*0.6;
          var col = v<0?css("--bear",PAL.down):series[0].color;
          svg.push('<rect x="'+m.l+'" y="'+y+'" width="0" height="'+h+'" fill="'+col+'"><animate attributeName="width" from="0" to="'+w+'" dur="0.8s" fill="freeze"/></rect>');
          svg.push('<text x="'+(m.l-8)+'" y="'+(y+h/2+4)+'" fill="'+ink+'" font-size="12" text-anchor="end">'+esc(c)+'</text>');
          svg.push('<text x="'+(m.l+w+6)+'" y="'+(y+h/2+4)+'" fill="'+txt+'" font-size="11" font-family="monospace">'+fmt(v)+(spec.suffix||'')+'</text>'); });
      } else {
        var bw = pw / cats.length;
        for (var t2=0;t2<=4;t2++){ var gy=m.t+ph*t2/4; svg.push('<line x1="'+m.l+'" y1="'+gy+'" x2="'+(m.l+pw)+'" y2="'+gy+'" stroke="'+grid+'" stroke-width="1"/>');
          svg.push('<text x="'+(m.l-8)+'" y="'+(gy+4)+'" fill="'+txt+'" font-size="11" font-family="monospace" text-anchor="end">'+fmt(mx*(1-t2/4))+(spec.suffix||'')+'</text>'); }
        cats.forEach(function(c,i){ var v=vals[i], h=Math.max(1,Math.abs(v)/mx*ph), x=m.l+bw*i+bw*0.18, w=bw*0.64, y=m.t+ph-h;
          var col = v<0?css("--bear",PAL.down):series[0].color;
          svg.push('<rect x="'+x+'" y="'+(m.t+ph)+'" width="'+w+'" height="0" fill="'+col+'"><animate attributeName="height" from="0" to="'+h+'" dur="0.8s" fill="freeze"/><animate attributeName="y" from="'+(m.t+ph)+'" to="'+y+'" dur="0.8s" fill="freeze"/></rect>');
          svg.push('<text x="'+(x+w/2)+'" y="'+(H-12)+'" fill="'+ink+'" font-size="11" text-anchor="middle">'+esc(c)+'</text>'); });
      }
    } else {
      // ---- LINE / AREA (multi-series) ----
      var n = (series[0] && series[0].data.length) || 0;
      var all = []; series.forEach(function(s){ s.data.forEach(function(v){ all.push(v); }); });
      var dmin = Math.min.apply(null, all), dmax = Math.max.apply(null, all);
      if (spec.baseline === 0 || (dmin > 0 && dmin < dmax*0.4)) dmin = Math.min(0, dmin);
      var step = niceNum((((dmax - dmin)) || 1)/4, true);
      var lo = Math.floor(dmin/step)*step, hi = Math.ceil(dmax/step)*step; if (hi <= lo) hi = lo + step;
      function X(i){ return m.l + (n<=1?pw/2:pw*i/(n-1)); }
      function Y(v){ return m.t + ph - (v-lo)/(hi-lo)*ph; }
      // y gridlines + labels (nice round ticks)
      for (var gv=lo; gv <= hi + step*0.001; gv += step){ var gy=Y(gv);
        svg.push('<line x1="'+m.l+'" y1="'+gy.toFixed(1)+'" x2="'+(m.l+pw)+'" y2="'+gy.toFixed(1)+'" stroke="'+grid+'" stroke-width="1"/>');
        svg.push('<text x="'+(m.l-8)+'" y="'+(gy+4).toFixed(1)+'" fill="'+txt+'" font-size="11" font-family="monospace" text-anchor="end">'+fmt(gv)+(spec.suffix||'')+'</text>'); }
      // baseline at 0 if in range
      if (lo<0 && hi>0){ var z=Y(0); svg.push('<line x1="'+m.l+'" y1="'+z+'" x2="'+(m.l+pw)+'" y2="'+z+'" stroke="'+axis+'" stroke-width="1"/>'); }
      // x labels (thin to ~6)
      var xl = spec.x || []; var step = Math.max(1, Math.ceil(n/6));
      for (var xi=0; xi<n; xi+=step){ if(!xl[xi]) continue;
        svg.push('<text x="'+X(xi)+'" y="'+(H-12)+'" fill="'+txt+'" font-size="11" font-family="monospace" text-anchor="'+(xi===0?'start':xi>=n-step?'end':'middle')+'">'+esc(xl[xi])+'</text>'); }
      // annotations (vertical event markers)
      (spec.annotations||[]).forEach(function(a){ var ax=X(a.xi);
        svg.push('<line x1="'+ax+'" y1="'+m.t+'" x2="'+ax+'" y2="'+(m.t+ph)+'" stroke="'+axis+'" stroke-width="1" stroke-dasharray="4 3"/>');
        svg.push('<text x="'+ax+'" y="'+(m.t-4)+'" fill="'+txt+'" font-size="10" text-anchor="middle">'+esc(a.text)+'</text>'); });
      // clip so lines never spill into the margins/labels
      defs += '<clipPath id="pclip"><rect x="'+m.l+'" y="'+(m.t-2)+'" width="'+pw+'" height="'+(ph+4)+'"/></clipPath>';
      series.forEach(function(s,si){
        var d=''; s.data.forEach(function(v,i){ d+=(i?'L':'M')+X(i).toFixed(1)+','+Y(v).toFixed(1)+' '; });
        if (type==="area"){ var gid='pg'+si; defs+='<linearGradient id="'+gid+'" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="'+s.color+'" stop-opacity="0.22"/><stop offset="1" stop-color="'+s.color+'" stop-opacity="0"/></linearGradient>';
          svg.push('<path d="'+d+'L'+X(n-1)+','+(m.t+ph)+' L'+X(0)+','+(m.t+ph)+' Z" fill="url(#'+gid+')" clip-path="url(#pclip)"/>'); }
        svg.push('<path d="'+d+'" fill="none" stroke="'+s.color+'" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round" clip-path="url(#pclip)" pathLength="1" class="pt-cdraw" style="animation-delay:'+(si*0.15)+'s"/>');
        // end marker
        svg.push('<circle cx="'+X(n-1)+'" cy="'+Y(s.data[n-1])+'" r="3.2" fill="'+s.color+'" stroke="'+bg+'" stroke-width="1.5"/>');
      });
    }
    // axes frame
    svg.push('<line x1="'+m.l+'" y1="'+m.t+'" x2="'+m.l+'" y2="'+(m.t+ph)+'" stroke="'+axis+'" stroke-width="1"/>');
    svg.push('<line x1="'+m.l+'" y1="'+(m.t+ph)+'" x2="'+(m.l+pw)+'" y2="'+(m.t+ph)+'" stroke="'+axis+'" stroke-width="1"/>');
    svg.unshift('<defs>'+defs+'</defs>'); svg.push('</svg>');

    // legend chips (HTML, below the svg — never overlaps the plot)
    var leg='';
    if (type!=="hbar" && type!=="bar" && series.length){ leg='<div class="pt-chart-legend">'+series.map(function(s){
      return '<span class="pt-chart-key"><span class="pt-chart-dot" style="background:'+s.color+'"></span>'+esc(s.name)+'</span>'; }).join('')+'</div>'; }

    var holder = document.createElement('div'); holder.className='pt-chart-svg'; holder.innerHTML = svg.join('');
    var legEl=null; if(leg){ legEl=document.createElement('div'); legEl.innerHTML=leg; legEl=legEl.firstChild; }
    var cap = fig.querySelector('figcaption');
    fig.insertBefore(holder, cap || null);
    if (legEl) fig.insertBefore(legEl, cap || null);
    fig.setAttribute('data-rendered','1');
  }

  function init(){ document.querySelectorAll('figure.pt-chart:not([data-rendered])').forEach(render); }
  if (document.readyState==='loading') document.addEventListener('DOMContentLoaded', init); else init();
  // re-render on theme toggle so colors refresh
  var tb=document.getElementById('themeToggle');
  if (tb) tb.addEventListener('click', function(){ setTimeout(function(){
    document.querySelectorAll('figure.pt-chart[data-rendered]').forEach(function(f){
      f.querySelectorAll('.pt-chart-svg,.pt-chart-legend').forEach(function(e){e.remove();}); f.removeAttribute('data-rendered'); render(f);
    }); },0); });
})();
