/* SVG chart + icon helpers. Everything is drawn from data at runtime. */
(function () {
  const P = {
    user: '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>',
    clipboard: '<rect x="5" y="4" width="14" height="17" rx="3"/><path d="M9 4.5h6M9 10h6M9 14h6M9 18h3"/>',
    bars: '<path d="M5 20V11M12 20V4M19 20v-6"/>',
    logout: '<path d="M10 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h4M15 8l4 4-4 4M19 12H9"/>',
    camera: '<path d="M4 8.5A2.5 2.5 0 0 1 6.5 6h1.2l1.3-2h6l1.3 2h1.2A2.5 2.5 0 0 1 20 8.5v8a2.5 2.5 0 0 1-2.5 2.5h-11A2.5 2.5 0 0 1 4 16.5z"/><circle cx="12" cy="12.5" r="3.5"/>',
    image: '<rect x="4" y="5" width="16" height="14" rx="3"/><circle cx="9" cy="10" r="1.6"/><path d="m5 17 4.5-4.5 3.5 3.5 2.5-2.5L20 16"/>',
    sliders: '<path d="M5 7h8M17 7h2M5 17h2M11 17h8"/><circle cx="15" cy="7" r="2"/><circle cx="9" cy="17" r="2"/>',
    check: '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    up: '<path d="M12 19V5M6 11l6-6 6 6"/>',
    down: '<path d="M12 5v14M6 13l6 6 6-6"/>',
    minus: '<path d="M6 12h12"/>',
    chev: '<path d="m9 6 6 6-6 6"/>',
    chevL: '<path d="m15 6-6 6 6 6"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    x: '<path d="M6 6l12 12M18 6 6 18"/>',
    sparkle: '<path d="M12 3.5 13.9 9l5.6 1.9-5.6 1.9L12 18.5l-1.9-5.7L4.5 10.9 10.1 9z"/><path d="M19 16v4M17 18h4"/>',
    star: '<path d="m12 4 2.4 5 5.4.7-4 3.8 1 5.4-4.8-2.7-4.8 2.7 1-5.4-4-3.8 5.4-.7z"/>',
    trend: '<path d="m4 16 5-5 4 3 7-8"/><path d="M15 6h5v5"/>',
    flag: '<path d="M6 20V4M6 5h11l-2.5 3.5L17 12H6"/>',
    ball: '<circle cx="12" cy="12" r="8.5"/><path d="m12 8 3.5 2.5-1.3 4h-4.4l-1.3-4zM12 8V3.6M15.5 10.5l4-1.4M14.2 14.5l2.5 3.6M9.8 14.5l-2.5 3.6M8.5 10.5l-4-1.4"/>',
    card: '<rect x="7" y="4" width="10" height="16" rx="2"/>',
    swap: '<path d="M7 7h11l-3-3M17 17H6l3 3"/>',
    pin: '<path d="m14.5 4 5.5 5.5-3 .7-3.6 3.6.2 3.8-1.5 1.5-3.4-3.4L5 20.5M9.7 9.7 8.5 11l4.5 4.5"/>',
    pencil: '<path d="M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16z"/><path d="m13.5 6.5 4 4"/>',
    bolt: '<path d="M13 3 5 13.5h5.5L10 21l8-10.5h-5.5z"/>',
    refresh: '<path d="M20 11a8 8 0 0 0-14-4L4 9M4 4v5h5M4 13a8 8 0 0 0 14 4l2-2M20 20v-5h-5"/>',
    info: '<circle cx="12" cy="12" r="8.5"/><path d="M12 11v5M12 8h.01"/>',
    dumbbell: '<path d="M6.5 7v10M17.5 7v10M3.5 9.5v5M20.5 9.5v5M6.5 12h11"/>',
    clock: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    moon: '<path d="M19 14.5A7.5 7.5 0 0 1 9.5 5a7.5 7.5 0 1 0 9.5 9.5z"/>',
    target: '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.5"/><path d="M12 12h.01"/>',
    shield: '<path d="M12 3.5 5 6v5.5c0 4.2 2.8 7.4 7 9 4.2-1.6 7-4.8 7-9V6z"/>',
    play: '<path d="M8 5.5v13l11-6.5z"/>',
    calendar: '<rect x="4" y="5.5" width="16" height="14.5" rx="3"/><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4"/>',
    pause: '<path d="M8.5 5.5v13M15.5 5.5v13"/>',
    binoc: '<circle cx="7" cy="15.5" r="3.5"/><circle cx="17" cy="15.5" r="3.5"/><path d="M10.5 15.5h3M4.2 13 6.5 5h3l1 8.5M19.8 13 17.5 5h-3l-1 8.5"/>',
    lock: '<rect x="5" y="11" width="14" height="9" rx="3"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>'
  };
  function icon(n, cls) { return '<svg class="i ' + (cls || '') + '" viewBox="0 0 24 24" aria-hidden="true">' + (P[n] || '') + '</svg>'; }

  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const nf = (n, d) => Number(n).toLocaleString("en-US", { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0 });
  function delta(n, d, inv) {
    const v = Number(n);
    if (!isFinite(v) || v === 0) return '<span class="delta flat">' + icon("minus", "sm") + " 0</span>";
    const good = inv ? v < 0 : v > 0;
    return '<span class="delta ' + (good ? "up" : "down") + '">' + icon(v > 0 ? "up" : "down", "sm") + " " + (v > 0 ? "+" : "") + nf(v, d || 0) + "</span>";
  }
  function rateClass(v) { return v >= 7.5 ? "hi" : v >= 6.9 ? "mid" : v < 6.8 ? "lo" : ""; }

  /* ---------- pitch ---------- */
  function pitchLines(half) {
    const l = 'fill="none" stroke="var(--pitch-line)" stroke-width="0.35"';
    let s = "";
    s += '<rect x="0.2" y="0.2" width="104.6" height="67.6" ' + l + "/>";
    s += '<path d="M52.5 0.2v67.6" ' + l + "/>";
    s += '<circle cx="52.5" cy="34" r="9.15" ' + l + "/>";
    s += '<circle cx="52.5" cy="34" r="0.5" fill="var(--pitch-line)"/>';
    [0, 1].forEach((side) => {
      const f = side ? (x) => 105 - x : (x) => x;
      const sx = side ? -1 : 1;
      s += '<path d="M' + f(0.2) + " 13.84H" + f(16.5) + "V54.16H" + f(0.2) + '" ' + l + "/>";
      s += '<path d="M' + f(0.2) + " 24.84H" + f(5.5) + "V43.16H" + f(0.2) + '" ' + l + "/>";
      s += '<circle cx="' + f(11) + '" cy="34" r="0.5" fill="var(--pitch-line)"/>';
      s += '<path d="M' + f(16.5) + " 26.7A9.15 9.15 0 0 " + (side ? 0 : 1) + " " + f(16.5) + ' 41.3" ' + l + "/>";
    });
    return s;
  }
  function pitch(inner, o) {
    o = o || {};
    const vb = o.half ? "64 6 41 56" : "0 0 105 68";
    return '<div class="pitch-box"' + (o.half ? ' style="max-width:460px"' : "") + '><svg class="pitch" viewBox="' + vb + '" role="img" aria-label="' + esc(o.label || "Pitch") + '"><rect x="-5" y="-5" width="115" height="78" fill="var(--pitch)"/>' + pitchLines(o.half) + (inner || "") + "</svg></div>";
  }

  /* ---------- radar ---------- */
  function radar(labels, series, o) {
    o = o || {};
    const n = labels.length, cx = 150, cy = 150, R = 104;
    const lo = 0, sc = (v) => Math.max(0, (v - lo) / (100 - lo));   /* categories are 0-100 percentiles */
    const pt = (i, v) => { const a = -Math.PI / 2 + (i * 2 * Math.PI) / n; return [cx + Math.cos(a) * R * sc(v), cy + Math.sin(a) * R * sc(v)]; };
    let s = "";
    [25, 50, 75, 100].forEach((r) => { s += '<polygon fill="none" class="grid" points="' + labels.map((_, i) => pt(i, r).join(",")).join(" ") + '"/>'; });
    labels.forEach((_, i) => { const p = pt(i, 100); s += '<line class="grid" x1="' + cx + '" y1="' + cy + '" x2="' + p[0] + '" y2="' + p[1] + '"/>'; });
    series.forEach((se) => {
      const pts = se.vals.map((v, i) => pt(i, v).join(",")).join(" ");
      s += '<polygon points="' + pts + '" fill="' + se.fill + '" stroke="' + se.color + '" stroke-width="' + (se.w || 2.5) + '" stroke-linejoin="round"' + (se.dash ? ' stroke-dasharray="5 4"' : "") + "/>";
      if (se.dots) se.vals.forEach((v, i) => { const p = pt(i, v); s += '<circle cx="' + p[0] + '" cy="' + p[1] + '" r="4.5" fill="' + se.color + '" stroke="var(--card)" stroke-width="2" data-tip="' + esc(labels[i] + ": " + v) + '"/>'; });
    });
    labels.forEach((t, i) => {
      const a = -Math.PI / 2 + (i * 2 * Math.PI) / n, x = cx + Math.cos(a) * (R + 24), y = cy + Math.sin(a) * (R + 22);
      const anc = Math.abs(Math.cos(a)) < 0.2 ? "middle" : Math.cos(a) > 0 ? "start" : "end";
      s += '<text x="' + x + '" y="' + (y + 4) + '" text-anchor="' + anc + '" class="strong" style="font-size:13px">' + esc(t) + "</text>";
    });
    return '<svg class="chart" viewBox="-30 0 360 300" role="img" aria-label="' + esc(o.label || "Radar chart") + '">' + s + "</svg>";
  }

  /* ---------- line chart ---------- */
  function line(o) {
    const W = 680, H = o.h || 280, m = { l: 44, r: 20, t: 20, b: 40 };
    const n = o.xs.length, iw = W - m.l - m.r, ih = H - m.t - m.b;
    const all = o.series.flatMap((s) => s.vals).concat(o.ref != null ? [o.ref] : []);
    let lo = o.min != null ? o.min : Math.min(...all), hi = o.max != null ? o.max : Math.max(...all);
    const pad = (hi - lo) * 0.12 || 1; if (o.min == null) lo -= pad; if (o.max == null) hi += pad;
    const X = (i) => m.l + (n === 1 ? iw / 2 : (i * iw) / (n - 1)), Y = (v) => m.t + ih - ((v - lo) / (hi - lo)) * ih;
    let s = "";
    const ticks = 4;
    for (let t = 0; t <= ticks; t++) {
      const v = lo + ((hi - lo) * t) / ticks, y = Y(v);
      s += '<line class="grid" x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + y + '" y2="' + y + '"/><text x="' + (m.l - 10) + '" y="' + (y + 4) + '" text-anchor="end">' + nf(v, o.dec != null ? o.dec : 1) + "</text>";
    }
    o.xs.forEach((x, i) => { if (!o.skip || i % o.skip === 0 || i === n - 1) s += '<text x="' + X(i) + '" y="' + (H - 12) + '" text-anchor="middle">' + esc(x) + "</text>"; });
    if (o.ref != null) s += '<line x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + Y(o.ref) + '" y2="' + Y(o.ref) + '" stroke="var(--ink-3)" stroke-dasharray="5 5" stroke-width="1.5"/><text x="' + (W - m.r) + '" y="' + (Y(o.ref) - 8) + '" text-anchor="end">' + esc(o.refLabel || "") + "</text>";
    o.series.forEach((se) => {
      const d = se.vals.map((v, i) => (i ? "L" : "M") + X(i) + " " + Y(v)).join(" ");
      if (se.area) s += '<path d="' + d + " L" + X(n - 1) + " " + (m.t + ih) + " L" + X(0) + " " + (m.t + ih) + 'Z" fill="' + se.color + '" opacity="0.12"/>';
      s += '<path d="' + d + '" fill="none" stroke="' + se.color + '" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>';
      se.vals.forEach((v, i) => { s += '<circle cx="' + X(i) + '" cy="' + Y(v) + '" r="' + (i === n - 1 ? 6 : 4.2) + '" fill="' + (i === n - 1 ? se.color : "var(--card)") + '" stroke="' + se.color + '" stroke-width="2.5" data-tip="' + esc((se.name ? se.name + " · " : "") + o.xs[i] + ": " + nf(v, o.dec != null ? o.dec : 1)) + '"/>'; });
      const li = n - 1; s += '<text x="' + X(li) + '" y="' + (Y(se.vals[li]) - 14) + '" text-anchor="middle" class="strong" style="font-size:14px">' + nf(se.vals[li], o.dec != null ? o.dec : 1) + "</text>";
    });
    (o.notes || []).forEach((a) => {
      const x = X(a.i), y = Y(o.series[0].vals[a.i]), bx = Math.min(W - 66, Math.max(m.l + 66, x));
      s += '<line x1="' + x + '" x2="' + x + '" y1="' + (y + 10) + '" y2="' + (m.t + ih) + '" stroke="var(--amber)" stroke-width="2" stroke-dasharray="2 4"/><rect x="' + (bx - 62) + '" y="' + (m.t + ih - 30) + '" width="124" height="24" rx="12" fill="var(--amber-bg)"/><text x="' + bx + '" y="' + (m.t + ih - 14) + '" text-anchor="middle" style="fill:var(--amber-d);font-weight:700">' + esc(a.t) + "</text>";
    });
    return '<div class="chart-scroll"><svg class="chart" viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="' + esc(o.label || "Line chart") + '">' + s + "</svg></div>";
  }

  /* ---------- scatter ---------- */
  function scatter(o) {
    const W = 640, H = 340, m = { l: 56, r: 24, t: 20, b: 52 };
    const iw = W - m.l - m.r, ih = H - m.t - m.b;
    const xs = o.pts.map((p) => p.x), ys = o.pts.map((p) => p.y);
    const xl = Math.min(...xs) - (o.xpad || 0.2), xh = Math.max(...xs) + (o.xpad || 0.2), yl = Math.min(...ys) - (o.ypad || 0.2), yh = Math.max(...ys) + (o.ypad || 0.2);
    const X = (v) => m.l + ((v - xl) / (xh - xl)) * iw, Y = (v) => m.t + ih - ((v - yl) / (yh - yl)) * ih;
    let s = "";
    for (let t = 0; t <= 4; t++) {
      const yv = yl + ((yh - yl) * t) / 4, xv = xl + ((xh - xl) * t) / 4;
      s += '<line class="grid" x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + Y(yv) + '" y2="' + Y(yv) + '"/><text x="' + (m.l - 10) + '" y="' + (Y(yv) + 4) + '" text-anchor="end">' + nf(yv, o.ydec != null ? o.ydec : 1) + "</text>";
      s += '<text x="' + X(xv) + '" y="' + (H - 28) + '" text-anchor="middle">' + nf(xv, o.xdec != null ? o.xdec : 1) + "</text>";
    }
    s += '<text x="' + (m.l + iw / 2) + '" y="' + (H - 6) + '" text-anchor="middle" class="strong">' + esc(o.xl) + '</text><text transform="translate(14 ' + (m.t + ih / 2) + ') rotate(-90)" text-anchor="middle" class="strong">' + esc(o.yl) + "</text>";
    if (o.fit) { const f = o.fit; s += '<line x1="' + X(xl) + '" y1="' + Y(f.a + f.b * xl) + '" x2="' + X(xh) + '" y2="' + Y(f.a + f.b * xh) + '" stroke="var(--ink-3)" stroke-width="1.5" stroke-dasharray="6 5"/>'; }
    o.pts.forEach((p) => {
      const me = p.me;
      s += '<circle cx="' + X(p.x) + '" cy="' + Y(p.y) + '" r="' + (me ? 10 : 7.5) + '" fill="' + (me ? "var(--red)" : "var(--teal)") + '" fill-opacity="' + (me ? 1 : 0.8) + '" stroke="var(--card)" stroke-width="2.5" data-tip="' + esc(p.tip) + '"/>';
      s += '<text x="' + (X(p.x) + 13) + '" y="' + (Y(p.y) + 4) + '" class="' + (me ? "strong" : "") + '" style="font-size:12px">' + esc(p.name) + "</text>";
    });
    return '<div class="chart-scroll"><svg class="chart" viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="' + esc(o.label || "Scatter chart") + '">' + s + "</svg></div>";
  }

  /* ---------- heatmap on pitch ---------- */
  function heat(cells, cols, rows) {
    const w = 105 / cols, h = 68 / rows;
    const mx = Math.max(...cells) || 1;
    let s = "";
    cells.forEach((v, i) => {
      if (v < mx * 0.06) return;
      const c = i % cols, r = Math.floor(i / cols), t = v / mx;
      s += '<rect x="' + c * w + '" y="' + r * h + '" width="' + (w + 0.4) + '" height="' + (h + 0.4) + '" fill="#5fd38d" fill-opacity="' + (0.1 + t * 0.85).toFixed(2) + '"/>';
    });
    return '<defs><filter id="hb" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="1.6"/></filter></defs><g filter="url(#hb)">' + s + "</g>";
  }

  /* ---------- banner presets ---------- */
  const BANNERS = [
    { id: "pitch", name: "Pitch lines" }, { id: "floodlight", name: "Floodlight" }, { id: "stripes", name: "Mowing stripes" },
    { id: "dusk", name: "Red dusk" }, { id: "tactics", name: "Tactics board" }, { id: "tide", name: "Teal tide" }
  ];
  function bannerSVG(id, u) {
    u = u || "b";
    const open = '<svg viewBox="0 0 1200 260" preserveAspectRatio="xMidYMid slice" aria-hidden="true">';
    if (id === "pitch") return open + '<rect width="1200" height="260" fill="#0f0f10"/><g fill="none" stroke="var(--card)" stroke-opacity=".16" stroke-width="3"><circle cx="760" cy="130" r="120"/><path d="M760 -10v280M1210 40H980v180h230M-10 40h230v180H-10"/><circle cx="760" cy="130" r="5" fill="#fff"/></g><circle cx="200" cy="60" r="150" fill="#1f8f4e" fill-opacity=".9"/></svg>';
    if (id === "floodlight") return open + '<defs><radialGradient id="' + u + 'f" cx="30%" cy="0%" r="90%"><stop offset="0" stop-color="#5fd38d" stop-opacity=".55"/><stop offset=".55" stop-color="#1f8f4e" stop-opacity=".35"/><stop offset="1" stop-color="#0f0f10" stop-opacity="0"/></radialGradient></defs><rect width="1200" height="260" fill="#0f0f10"/><rect width="1200" height="260" fill="url(#' + u + 'f)"/><g fill="none" stroke="#5fd38d" stroke-opacity=".28" stroke-width="2"><circle cx="360" cy="-20" r="140"/><circle cx="360" cy="-20" r="220"/><circle cx="360" cy="-20" r="300"/><circle cx="360" cy="-20" r="380"/></g><circle cx="1010" cy="180" r="70" fill="#f0a500"/></svg>';
    if (id === "stripes") { let r = ""; for (let i = 0; i < 12; i++) r += '<rect x="' + i * 100 + '" width="100" height="260" fill="' + (i % 2 ? "#245a6b" : "#1f8f4e") + '"/>'; return open + r + '<g fill="none" stroke="var(--card)" stroke-opacity=".5" stroke-width="3"><circle cx="600" cy="130" r="80"/><path d="M600 0v260"/></g></svg>'; }
    if (id === "dusk") return open + '<rect width="1200" height="260" fill="#19191a"/><circle cx="900" cy="250" r="230" fill="#1f8f4e"/><circle cx="900" cy="250" r="150" fill="#f0a500"/><circle cx="900" cy="250" r="74" fill="#f5f5f6"/><path d="M0 220 280 150 540 210 820 140 1200 230V260H0Z" fill="#0f0f10"/></svg>';
    if (id === "tactics") { let d = ""; for (let x = 40; x < 1200; x += 60) for (let y = 30; y < 260; y += 60) d += '<circle cx="' + x + '" cy="' + y + '" r="2.2" fill="#5fd38d" fill-opacity=".35"/>'; return open + '<rect width="1200" height="260" fill="#19191a"/>' + d + '<g fill="none" stroke-width="5" stroke-linecap="round"><circle cx="300" cy="90" r="16" stroke="#5fd38d"/><circle cx="520" cy="170" r="16" stroke="#5fd38d"/><path d="M640 60l30 30M670 60l-30 30" stroke="#f0a500"/><path d="M860 150l30 30M890 150l-30 30" stroke="#f0a500"/><path d="M330 100C400 120 440 150 495 165" stroke="var(--card)" stroke-dasharray="2 12"/><path d="M545 165C600 150 650 120 700 100 780 90 830 120 850 150" stroke="#f0a500" stroke-opacity=".95"/></g></svg>'; }
    return open + '<rect width="1200" height="260" fill="#1f8f4e"/><path d="M0 170C180 110 330 230 520 170S860 90 1200 160V260H0Z" fill="#5fd38d"/><path d="M0 210C200 160 360 260 560 210S900 150 1200 210V260H0Z" fill="#0f0f10" fill-opacity=".85"/><circle cx="1010" cy="70" r="46" fill="#f0a500"/></svg>';
  }

  window.C = { icon, esc, nf, delta, rateClass, pitch, radar, line, scatter, heat, bannerSVG, BANNERS };
})();
