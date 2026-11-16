/* Earth Worked Out: deterministic canvas renderer. renderAt(T) draws the frame for global time T (seconds); the same T
   always gives the same pixels. Episode content comes from window.EP (data.js). Visual system: field notebook on warm
   paper, ink lines, earth-tone accents, Lato. Deliberately unlike Under Test (dark, terminal panels, Noto Sans). */
"use strict";
const W = 1920, H = 1080;
const C = { bg: "#f3ede2", paper2: "#ebe3d4", grid: "#e2d8c6", ink: "#1f2a30", dim: "#6b6458", faint: "#a99f8e",
            sea: "#1f6f8b", seaLight: "#9cc5d3", deep: "#0f3f52", ember: "#d9552c", leaf: "#3f8a4f", sun: "#e0a030", rock: "#8a7a63", land: "#c9b48f" };
const SANS = '"Lato", sans-serif', MONO = '"DejaVu Sans Mono", monospace';
let ctx;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ease = (x) => { x = clamp(x); return x * x * (3 - 2 * x); };
const prog = (t, a, b) => clamp((t - a) / (b - a));
const lerp = (a, b, x) => a + (b - a) * x;
const fadeIn = (t, at, d = 0.5) => ease(prog(t, at, at + d));
const fmt = (n) => Math.round(n).toLocaleString("en-US");
function font(px, family = SANS, weight = 400) { ctx.font = `${weight} ${px}px ${family}`; }
function text(s, x, y, o = {}) {
  font(o.px || 40, o.mono ? MONO : SANS, o.weight || 400);
  ctx.fillStyle = o.color || C.ink; ctx.textAlign = o.align || "left"; ctx.textBaseline = "alphabetic";
  ctx.fillText(s, x, y);
}
function measure(s, px, mono, weight) { font(px, mono ? MONO : SANS, weight || 400); return ctx.measureText(s).width; }
function rect(x, y, w, h, fill, r = 0, stroke = null, lw = 2) {
  ctx.beginPath(); ctx.roundRect(x, y, w, h, r); if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.stroke(); }
}
function card(x, y, w, h, label) {          // a pinned note card: paper, thin ink border, a tab label
  ctx.save(); ctx.shadowColor = "rgba(60,45,20,0.18)"; ctx.shadowBlur = 18; ctx.shadowOffsetY = 6; rect(x, y, w, h, "#fbf8f1", 6); ctx.restore();
  rect(x, y, w, h, null, 6, C.ink, 2);
  if (label) { const lw = measure(label, 24, false, 700) + 36; rect(x + 24, y - 18, lw, 36, C.ink, 4); text(label, x + 42, y + 8, { px: 24, weight: 700, color: "#fbf8f1" }); }
}
function line(pts, col, lw = 4, dash) { ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.setLineDash(dash || []); ctx.beginPath(); pts.forEach(([a, b], i) => i ? ctx.lineTo(a, b) : ctx.moveTo(a, b)); ctx.stroke(); ctx.setLineDash([]); }
function arrow(x1, y1, x2, y2, color, lw = 4) {
  ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = lw; ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
  const a = Math.atan2(y2 - y1, x2 - x1), s = 16; ctx.beginPath(); ctx.moveTo(x2, y2);
  ctx.lineTo(x2 - s * Math.cos(a - 0.4), y2 - s * Math.sin(a - 0.4)); ctx.lineTo(x2 - s * Math.cos(a + 0.4), y2 - s * Math.sin(a + 0.4)); ctx.closePath(); ctx.fill();
}
function underline(x, y, w, col, g) { ctx.strokeStyle = col; ctx.lineWidth = 6; ctx.lineCap = "round"; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + w * g, y + 2 * Math.sin(g * 6)); ctx.stroke(); ctx.lineCap = "butt"; }

/* ---------- scenes: draw(t, dur, p), t local to the beat ---------- */
const S = {};
S.title = (t, d, p) => {
  const n = p.title.length, y0 = H / 2 - (n - 1) * 60 - 30;
  p.title.forEach((l, i) => { const a = fadeIn(t, 0.15 + i * 0.45, 0.6); ctx.globalAlpha = a;
    text(l, 160, y0 + i * 120 + (1 - a) * 20, { px: 96, weight: 900, color: i === n - 1 ? C.sea : C.ink }); });
  ctx.globalAlpha = 1; underline(164, y0 + (n - 1) * 120 + 34, measure(p.title[n - 1], 96, false, 900), C.ember, ease(prog(t, 0.6 + n * 0.4, 1.6 + n * 0.4)));
  if (p.sub) { ctx.globalAlpha = fadeIn(t, 0.6 + n * 0.45, 0.6); text(p.sub, 164, y0 + n * 120 + 30, { px: 34, color: C.dim }); }
  ctx.globalAlpha = 1;
};
S.statement = (t, d, p) => {
  const n = p.lines.length, step = Math.min(1.6, (d * 0.55) / n), y0 = H / 2 - (n - 1) * 52 - (p.sub ? 30 : 0);
  p.lines.forEach((l, i) => { const a = fadeIn(t, 0.2 + i * step, 0.6), acc = (p.accent || []).includes(i); ctx.globalAlpha = a;
    text(l, W / 2, y0 + i * 104 + (1 - a) * 16, { px: 68, weight: acc ? 900 : 700, align: "center", color: acc ? C.ember : C.ink }); });
  if (p.sub) { ctx.globalAlpha = fadeIn(t, 0.4 + n * step, 0.8); text(p.sub, W / 2, y0 + n * 104 + 30, { px: 30, align: "center", color: C.dim }); }
  ctx.globalAlpha = 1;
};
S.bullets = (t, d, p) => {
  const n = p.items.length, step = (d * 0.72) / (n + 0.6), x = 300, y0 = 320 - (n > 3 ? 40 : 0);
  ctx.globalAlpha = fadeIn(t, 0.1); text(p.head, x, y0, { px: 56, weight: 900, color: C.sea });
  p.items.forEach((it, i) => { const a = fadeIn(t, 0.5 + i * step, 0.6), y = y0 + 130 + i * 128; ctx.globalAlpha = a;
    rect(x, y - 44, 56, 56, i % 2 ? C.sun : C.seaLight, 28); text(p.numbered ? String(i + 1) : "•", x + 28, y - 4, { px: 34, weight: 900, align: "center", color: C.ink });
    text(it, x + 90 + (1 - a) * 20, y, { px: 46 }); });
  ctx.globalAlpha = 1;
};
S.quote = (t, d, p) => {
  const n = p.lines.length, lh = 74, h = n * lh + 170, x = 220, w = W - 440, y = (H - h) / 2 - 20;
  card(x, y, w, h, p.src_short || "official guidance");
  const step = Math.min(1.2, (d * 0.5) / n);
  p.lines.forEach((l, i) => { ctx.globalAlpha = fadeIn(t, 0.3 + i * step, 0.6); const hot = (p.hl || []).includes(i);
    if (hot) { ctx.fillStyle = "rgba(224,160,48,0.35)"; ctx.fillRect(x + 70, y + 72 + i * lh, measure(l, 44, false, 700) + 20, 56); }
    text(l, x + 80, y + 114 + i * lh, { px: 44, weight: hot ? 700 : 400 }); });
  ctx.globalAlpha = fadeIn(t, 0.5 + n * step, 0.6); text(p.src, x + 80, y + h - 36, { px: 26, color: C.dim });
  if (p.foot) text(p.foot, W / 2, y + h + 86, { px: 40, align: "center", color: C.sea, weight: 700 });
  ctx.globalAlpha = 1;
};
S.equation = (t, d, p) => {
  card(360, 260, W - 720, 420, p.label || "the model");
  ctx.globalAlpha = fadeIn(t, 0.3, 0.6); text(p.eq, W / 2, 470, { px: 110, weight: 900, align: "center", color: C.ink });
  (p.where || []).forEach((w, i) => { ctx.globalAlpha = fadeIn(t, 1.0 + i * 0.6, 0.5); text(w, W / 2, 560 + i * 48, { px: 32, align: "center", color: C.dim }); });
  ctx.globalAlpha = fadeIn(t, d * 0.55, 0.6); if (p.foot) text(p.foot, W / 2, 790, { px: 42, align: "center", weight: 700, color: C.sea }); ctx.globalAlpha = 1;
};
S.endcard = (t, d, p) => {
  text("Earth Worked Out", 150, 300, { px: 104, weight: 900 }); underline(154, 330, measure("Earth Worked Out", 104, false, 900), C.ember, ease(prog(t, 0.3, 1.3)));
  text("Real physics, run on screen.", 154, 396, { px: 42, color: C.sea, weight: 700 });
  text(p.next_label || "Next", 154, 560, { px: 30, color: C.dim });
  (p.next || []).forEach((l, i) => text(l, 154, 626 + i * 64, { px: 48, weight: 700 }));
  text("Sources, data and the simulation code are in the description.", 154, 900, { px: 30, color: C.dim });
  ctx.setLineDash([10, 10]); rect(1220, 170, 560, 315, null, 10, C.faint, 3); ctx.beginPath(); ctx.arc(1500, 790, 170, 0, 7); ctx.strokeStyle = C.faint; ctx.stroke(); ctx.setLineDash([]);
};

/* ---------- episode 1 scenes: tsunami ---------- */
const PEOPLE_COL = [C.leaf, C.sun, C.sea, C.ember, C.deep];
function frontAt(s) { const F = EP.data.front; if (s <= 0) return 0; for (let i = 1; i < F.length; i++) if (F[i][0] >= s) { const a = F[i - 1], b = F[i]; return lerp(a[1], b[1], (s - a[0]) / (b[0] - a[0])); } return F[F.length - 1][1]; }
function figure(x, y, col, s = 1) {   // a small stick figure, drawn by code
  ctx.strokeStyle = col; ctx.fillStyle = col; ctx.lineWidth = 4 * s; ctx.lineCap = "round";
  ctx.beginPath(); ctx.arc(x, y - 46 * s, 9 * s, 0, 7); ctx.fill();
  ctx.beginPath(); ctx.moveTo(x, y - 36 * s); ctx.lineTo(x, y - 14 * s); ctx.moveTo(x, y - 14 * s); ctx.lineTo(x - 10 * s, y); ctx.moveTo(x, y - 14 * s); ctx.lineTo(x + 10 * s, y);
  ctx.moveTo(x, y - 30 * s); ctx.lineTo(x - 11 * s, y - 20 * s); ctx.moveTo(x, y - 30 * s); ctx.lineTo(x + 11 * s, y - 22 * s); ctx.stroke(); ctx.lineCap = "butt";
}
/* top-down strip: the beach on the left, land to the right; the water front and runners, all from the simulation */
S.racestrip = (t, d, p) => {
  const x0 = 200, x1 = W - 120, D = p.metres || 600, X = (m) => x0 + (m / D) * (x1 - x0), sp = p.speedup || 3, s = Math.max(0, (t - 1.0) * sp), rows = (p.who || [1, 2, 4]);
  text(p.head || "the water reaches the beach · you start running at the same moment · from the simulation", x0, 200, { px: 30, color: C.dim });
  rect(x0 - 160, 250, 160, 640, C.sea, 0); ctx.fillStyle = C.land; ctx.fillRect(x0, 250, x1 - x0, 640);
  for (let m = 0; m <= D; m += 100) { ctx.fillStyle = "rgba(31,42,48,0.25)"; ctx.fillRect(X(m), 250, 2, 640); text(m + " m", X(m), 930, { px: 24, align: "center", color: C.dim }); }
  const f = frontAt(s); ctx.fillStyle = "rgba(31,111,139,0.78)"; ctx.fillRect(x0, 250, Math.max(0, X(f) - x0), 640);
  ctx.strokeStyle = "#fbf8f1"; ctx.lineWidth = 5; ctx.beginPath(); for (let y = 250; y <= 890; y += 8) { const xx = X(f) + 8 * Math.sin(y / 30 + t * 4); y === 250 ? ctx.moveTo(xx, y) : ctx.lineTo(xx, y); } ctx.stroke();
  rows.forEach((pi, i) => { const P = EP.data.people[pi], v = P.m_per_s, pos = Math.min(D, (p.start || 0) + v * s), lane = 640 / rows.length, y = 250 + (i + 0.62) * lane, caught = pos < f && s > 0.5;
    if (i) { ctx.fillStyle = "rgba(31,42,48,0.35)"; ctx.fillRect(x0, 250 + i * lane, x1 - x0, 2); }
    const right = X(pos) > x1 - 420, lx = right ? X(pos) - 26 : X(pos) + 26, al = right ? "right" : "left";
    figure(X(pos), y, caught ? "#fbf8f1" : PEOPLE_COL[pi], 1.4);
    if (caught) { rect(lx - (right ? measure(P.who + " · caught", 34, false, 900) + 20 : 10), y - 58, measure(P.who + " · caught", 34, false, 900) + 30, 50, C.ember, 8); text(P.who + " · caught", lx + (right ? -5 : 5), y - 22, { px: 34, weight: 900, color: "#fbf8f1", align: al }); }
    else text(P.who + " · " + P.kmh.toFixed(0) + " km/h", lx, y - 22, { px: 34, weight: 900, color: C.ink, align: al }); });
  rect(W - 470, 120, 350, 70, C.ink, 8); text(`t + ${s.toFixed(0)} s   ×${sp}`, W - 295, 167, { px: 36, weight: 900, align: "center", color: "#fbf8f1", mono: true });
};
/* side view of the whole ocean: seabed to scale in depth, the water surface exaggerated so a 2 m wave is visible */
S.seaprofile = (t, d, p) => {
  const B = EP.data.bed, SN = EP.data.snaps, x0 = 140, x1 = W - 120, kmMax = 230, X = (km) => x0 + (km / kmMax) * (x1 - x0), y0 = 330, dy = 560, Yb = (z) => y0 + (-z / 4000) * dy, ex = p.ex || 40;
  text(p.head || "an idealised ocean, 230 km across · seabed to scale · wave height exaggerated " + ex + "×", x0, 210, { px: 30, color: C.dim });
  const k = p.snap !== undefined ? p.snap : clamp(Math.floor(prog(t, d * (p.from || 0.05), d * (p.to || 0.9)) * (SN.length - 1)), 0, SN.length - 1), s = SN[k];
  ctx.beginPath(); ctx.moveTo(X(0), y0); s.eta.forEach((e, i) => ctx.lineTo(X(B[i][0]), e == null ? Yb(B[i][1]) : y0 - e * ex)); ctx.lineTo(X(B[B.length - 1][0]), Yb(B[B.length - 1][1]));
  for (let i = B.length - 1; i >= 0; i--) ctx.lineTo(X(B[i][0]), Yb(Math.min(0, B[i][1]))); ctx.closePath(); ctx.fillStyle = C.seaLight; ctx.fill();
  ctx.beginPath(); B.forEach(([km, z], i) => i ? ctx.lineTo(X(km), z < 0 ? Yb(z) : y0 - z * 2) : ctx.moveTo(X(km), Yb(z))); ctx.lineTo(X(kmMax), y0 + dy + 40); ctx.lineTo(X(0), y0 + dy + 40); ctx.closePath(); ctx.fillStyle = C.rock; ctx.fill();
  line(s.eta.map((e, i) => [X(B[i][0]), e == null ? Yb(B[i][1]) : y0 - e * ex]), C.deep, 4);
  [["4,000 m deep", 20], ["continental slope", 115], ["shelf, about 100 m", 160], ["coast", 200]].forEach(([l, km]) => text(l, X(km), y0 + dy + 90, { px: 26, align: "center", color: C.dim }));
  rect(W - 400, 110, 280, 66, C.ink, 8); text(`${Math.round(s.t / 60)} min`, W - 260, 156, { px: 36, weight: 900, align: "center", color: "#fbf8f1", mono: true });
};
S.speedbars = (t, d, p) => {
  const R = EP.data.speeds, x0 = 560, y0 = 270, lh = 108, bw = 1000, max = 750;
  text("speed of the wave's crest, by water depth · simulated, against √(g × depth)", 200, y0 - 50, { px: 30, color: C.dim });
  R.forEach((r, i) => { const a = fadeIn(t, d * (0.06 + i * 0.12), 0.5), g = ease(prog(t, d * (0.06 + i * 0.12), d * (0.06 + i * 0.12) + 0.9)), y = y0 + i * lh; ctx.globalAlpha = a;
    text(r.band, x0 - 30, y + 50, { px: 34, align: "right", weight: 700 }); rect(x0, y + 12, (r.sim_kmh / max) * bw * g, 56, i < 2 ? C.deep : i < 4 ? C.sea : C.ember, 6);
    text(r.sim_kmh + " km/h", x0 + (r.sim_kmh / max) * bw * g + 20, y + 54, { px: 44, weight: 900, mono: true });
    ctx.fillStyle = C.ink; ctx.fillRect(x0 + (r.theory_kmh / max) * bw - 2, y + 4, 4, 72); });
  ctx.globalAlpha = fadeIn(t, d * 0.8, 0.5); text("black tick = theory", x0, y0 + R.length * lh + 30, { px: 26, color: C.dim }); ctx.globalAlpha = 1;
};
S.shoal = (t, d, p) => {
  const R = EP.data.heights, x0 = 600, y0 = 270, lh = 108, bw = 900, max = 6.5;
  text("highest point the wave reached, by place · same wave, from the simulation", 200, y0 - 50, { px: 30, color: C.dim });
  R.forEach((r, i) => { const a = fadeIn(t, d * (0.06 + i * 0.12), 0.5), g = ease(prog(t, d * (0.06 + i * 0.12), d * (0.06 + i * 0.12) + 0.9)), y = y0 + i * lh; ctx.globalAlpha = a;
    text(r.where, x0 - 30, y + 50, { px: 34, align: "right", weight: 700 }); rect(x0, y + 12, (r.m / max) * bw * g, 56, C.sea, 6);
    text(r.m.toFixed(1) + " m", x0 + (r.m / max) * bw * g + 20, y + 54, { px: 44, weight: 900, mono: true }); });
  ctx.globalAlpha = fadeIn(t, d * 0.8, 0.5); text(p.foot || "", W / 2, y0 + R.length * lh + 50, { px: 40, align: "center", weight: 700, color: C.ember }); ctx.globalAlpha = 1;
};
/* close-up of the coast: last 10 km of sea and the first 2.5 km of land */
S.shore = (t, d, p) => {
  const B = EP.data.near_bed, N = EP.data.near, x0 = 120, x1 = W - 100, a = -10000, b = 2500, X = (m) => x0 + ((m - a) / (b - a)) * (x1 - x0), y0 = 560, sc = 18, Y = (z) => y0 - z * sc;
  text(p.head || "the last 10 km of sea and the first 2.5 km of land · heights exaggerated 50×", x0, 190, { px: 30, color: C.dim });
  const i0 = N.findIndex((n) => n.t >= (p.t0 || 2900)), i1 = N.findIndex((n) => n.t >= (p.t1 || 3500)), k = Math.round(lerp(i0, i1 < 0 ? N.length - 1 : i1, prog(t, d * 0.05, d * 0.92))), s = N[k];
  ctx.beginPath(); ctx.moveTo(X(a), Y(0)); s.eta.forEach((e, i) => ctx.lineTo(X(B[i][0]), e == null ? Y(B[i][1]) : Y(e))); for (let i = B.length - 1; i >= 0; i--) ctx.lineTo(X(B[i][0]), Y(B[i][1])); ctx.closePath(); ctx.fillStyle = C.seaLight; ctx.fill();
  line(s.eta.map((e, i) => [X(B[i][0]), e == null ? Y(B[i][1]) : Y(e)]).filter((_, i) => s.eta[i] != null), C.deep, 4);
  ctx.beginPath(); B.forEach(([m, z], i) => i ? ctx.lineTo(X(m), Y(z)) : ctx.moveTo(X(m), Y(z))); ctx.lineTo(X(b), H - 120); ctx.lineTo(X(a), H - 120); ctx.closePath(); ctx.fillStyle = C.land; ctx.fill();
  line(B.map(([m, z]) => [X(m), Y(z)]), C.rock, 3);
  ctx.fillStyle = C.ink; ctx.fillRect(X(0) - 1, Y(0) - 40, 2, 60); text("shoreline", X(0), Y(0) - 52, { px: 24, align: "center", color: C.dim });
  [-10000, -5000, 0, 1000, 2000].forEach((m) => text((m / 1000) + " km", X(m), H - 80, { px: 24, align: "center", color: C.dim, mono: true }));
  if (p.mark) { ctx.globalAlpha = fadeIn(t, d * 0.7, 0.5); const mx = EP.data.max_runup_m; ctx.setLineDash([12, 10]); line([[X(0), Y(mx)], [X(b), Y(mx)]], C.ember, 3); ctx.setLineDash([]);
    text("highest point reached: " + mx + " m above sea level", X(b) - 20, Y(mx) - 16, { px: 30, weight: 900, color: C.ember, align: "right" }); ctx.globalAlpha = 1; }
  rect(W - 400, 100, 300, 66, C.ink, 8); text(`${(s.t / 60).toFixed(1)} min`, W - 250, 146, { px: 36, weight: 900, align: "center", color: "#fbf8f1", mono: true });
};
/* distance-time race chart */
S.racechart = (t, d, p) => {
  const F = EP.data.front, x0 = 300, y0 = 220, w = 1300, h = 620, tMax = p.tmax || 300, dMax = 1800, X = (s) => x0 + (s / tMax) * w, Y = (m) => y0 + h - (m / dMax) * h, g = ease(prog(t, d * 0.08, d * 0.7));
  text("distance from the shoreline, against time since the water reached it", x0, y0 - 36, { px: 30, color: C.dim }); rect(x0, y0, w, h, "rgba(251,248,241,0.7)", 6, C.ink, 2);
  for (let m = 0; m <= dMax; m += 300) { ctx.fillStyle = C.grid; ctx.fillRect(x0, Y(m), w, 1); text(m + " m", x0 - 14, Y(m) + 8, { px: 22, align: "right", color: C.dim, mono: true }); }
  for (let s = 0; s <= tMax; s += 60) text(s / 60 + " min", X(s), y0 + h + 34, { px: 22, align: "center", color: C.dim, mono: true });
  const fp = F.filter(([s]) => s <= tMax * g); ctx.beginPath(); ctx.moveTo(X(0), Y(0)); fp.forEach(([s, m]) => ctx.lineTo(X(s), Y(m))); ctx.lineTo(X(fp.length ? fp[fp.length - 1][0] : 0), Y(0)); ctx.closePath(); ctx.fillStyle = "rgba(31,111,139,0.25)"; ctx.fill();
  line(fp.map(([s, m]) => [X(s), Y(m)]), C.sea, 6); text("the water", X(70), Y(frontAt(70)) - 20, { px: 32, weight: 900, color: C.sea });
  (p.who || [0, 1, 2, 4]).forEach((pi, i) => { const P = EP.data.people[pi], v = P.m_per_s, a = fadeIn(t, d * (0.25 + i * 0.1), 0.4); ctx.globalAlpha = a; const sEnd = Math.min(tMax * g, dMax / v);
    line([[X(0), Y(0)], [X(sEnd), Y(v * sEnd)]], PEOPLE_COL[pi], 4, [14, 8]); text(P.who, X(sEnd) + 10, Y(v * sEnd) - 6, { px: 26, weight: 700, color: PEOPLE_COL[pi] }); });
  ctx.globalAlpha = 1;
};
S.headstart = (t, d, p) => {
  const P = EP.data.people.slice(0, 4), x = 220, w = W - 440, y = 300, lh = 130, key = p.key || "from_0m";
  text(p.head || "head start needed to stay ahead of the water all the way to its furthest reach (" + Math.floor(EP.data.max_inland_m).toLocaleString("en-US") + " m)", x, 230, { px: 30, color: C.dim });
  P.forEach((r, i) => { const a = fadeIn(t, d * (0.08 + i * 0.16), 0.5), yy = y + i * lh, s = r[key].head_start_needed_s; ctx.globalAlpha = a;
    card(x, yy, w, lh - 26); figure(x + 60, yy + 88, PEOPLE_COL[i], 0.9); text(`${r.who}, ${r.kmh.toFixed(0)} km/h`, x + 110, yy + 66, { px: 40, weight: 700 });
    const lab = s >= 60 ? `${Math.floor(s / 60)} min ${s % 60} s` : `${s} s`; text(lab, x + w - 40, yy + 68, { px: 52, weight: 900, align: "right", mono: true, color: s > 120 ? C.ember : C.ink }); });
  ctx.globalAlpha = fadeIn(t, d * 0.8, 0.5); text(p.foot || "", W / 2, y + 4 * lh + 50, { px: 38, align: "center", weight: 700, color: C.sea }); ctx.globalAlpha = 1;
};
S.drawback = (t, d, p) => {
  const S_ = EP.data.shoreline_trough, x0 = 300, y0 = 230, w = 1300, h = 600, t0 = S_[0][0], t1 = S_[S_.length - 1][0], X = (s) => x0 + ((s - t0) / (t1 - t0)) * w, lo = -150, hi = 1200, Y = (m) => y0 + h - ((m - lo) / (hi - lo)) * h, g = ease(prog(t, d * 0.08, d * 0.75));
  text("where the water's edge is, when the trough arrives first (metres; negative = the sea has drawn back)", x0, y0 - 36, { px: 28, color: C.dim }); rect(x0, y0, w, h, "rgba(251,248,241,0.7)", 6, C.ink, 2);
  ctx.fillStyle = C.ink; ctx.fillRect(x0, Y(0), w, 2); text("normal shoreline", x0 + 10, Y(0) - 10, { px: 22, color: C.dim });
  const pts = S_.filter(([s]) => s <= lerp(t0, t1, g)); line(pts.map(([s, m]) => [X(s), Y(m)]), C.sea, 6);
  const mn = S_.reduce((a, b) => (b[1] < a[1] ? b : a)); if (g * (t1 - t0) + t0 > mn[0]) { ctx.globalAlpha = fadeIn(t, d * 0.55, 0.5); text(`sea drawn back ${Math.round(-mn[1])} m`, X(mn[0]) - 20, Y(mn[1]) + 50, { px: 34, weight: 900, color: C.ember, align: "right" }); }
  ctx.globalAlpha = fadeIn(t, d * 0.75, 0.5); text(p.foot || "", W / 2, y0 + h + 90, { px: 40, align: "center", weight: 700, color: C.sea }); ctx.globalAlpha = 1;
};

/* ---------- frame ---------- */
/* ---------- ec02: hurricanes and the equator ---------- */
const MAP = { x0: 200, y0: 190, w: 1620, h: 600, lonL: 20, latT: 60, latB: -45 };
const mapX = (lon) => MAP.x0 + (((lon < MAP.lonL ? lon + 360 : lon) - MAP.lonL) / 360) * MAP.w;
const mapY = (lat) => MAP.y0 + ((MAP.latT - lat) / (MAP.latT - MAP.latB)) * MAP.h;
let trackCache = null, trackDrawn = 0;
function tracksUpTo(n) {        // offscreen layer holding the first n tracks; rebuilt from zero if asked for fewer (deterministic)
  if (!trackCache) { trackCache = document.createElement("canvas"); trackCache.width = W; trackCache.height = H; }
  const c = trackCache.getContext("2d"), TR = EP.data.tracks;
  if (n < trackDrawn) { c.clearRect(0, 0, W, H); trackDrawn = 0; }
  c.strokeStyle = "rgba(31,111,139,0.32)"; c.lineWidth = 1.4; c.lineJoin = "round";
  for (let i = trackDrawn; i < Math.min(n, TR.length); i++) { const tr = TR[i]; c.beginPath();
    for (let j = 0; j < tr.length; j++) { const x = mapX(tr[j][1]), y = mapY(tr[j][0]);
      if (j && Math.abs(x - mapX(tr[j - 1][1])) > W / 2) c.moveTo(x, y); else j ? c.lineTo(x, y) : c.moveTo(x, y); } c.stroke(); }
  trackDrawn = Math.max(trackDrawn, Math.min(n, TR.length)); return trackCache;
}
function mapFrame(band) {
  rect(MAP.x0, MAP.y0, MAP.w, MAP.h, "#fbf8f1", 6, C.faint, 2);
  [45, 30, 15, -15, -30].forEach((la) => { ctx.fillStyle = C.grid; ctx.fillRect(MAP.x0, mapY(la), MAP.w, 2);
    text(Math.abs(la) + "°" + (la > 0 ? "N" : "S"), MAP.x0 - 14, mapY(la) + 9, { px: 22, color: C.dim, align: "right" }); });
  if (band) { ctx.fillStyle = "rgba(217,85,44,0.10)"; ctx.fillRect(MAP.x0, mapY(5), MAP.w, mapY(-5) - mapY(5)); }
}
S.trackmap = (t, d, p) => {
  const N = EP.data.tracks.length, n = p.reveal ? Math.round(N * ease(prog(t, d * (p.from || 0.05), d * (p.to || 0.8)))) : N;
  text(p.head || "every tropical storm on record, " + EP.data.counts.first_season + " to today · NOAA IBTrACS · one line per storm", MAP.x0, 160, { px: 30, color: C.dim });
  mapFrame(p.band); ctx.drawImage(tracksUpTo(n), 0, 0);
  const ge = p.glow ? fadeIn(t, d * p.glow, 0.8) : 0.6;
  ctx.fillStyle = C.ember; ctx.globalAlpha = 0.35 + 0.65 * ge; ctx.fillRect(MAP.x0, mapY(0) - 3, MAP.w, 6); ctx.globalAlpha = 1;
  text("equator", MAP.x0 - 14, mapY(0) + 9, { px: 24, weight: 900, color: C.ember, align: "right" });
  rect(MAP.x0, MAP.y0 + MAP.h + 30, 560, 70, C.ink, 8);
  text("storms drawn: " + fmt(n), MAP.x0 + 28, MAP.y0 + MAP.h + 78, { px: 36, weight: 900, color: "#fbf8f1", mono: true });
  if (p.cross) { ctx.globalAlpha = fadeIn(t, d * p.cross, 0.6);
    text("crossing the equator: 0", MAP.x0 + MAP.w, MAP.y0 + MAP.h + 80, { px: 48, weight: 900, color: C.ember, align: "right" }); ctx.globalAlpha = 1; }
  if (p.note) text(p.note, MAP.x0 + MAP.w, MAP.y0 + MAP.h + 80, { px: 30, color: C.dim, align: "right" });
};
S.vhist = (t, d, p) => {
  const Hs = EP.data.hist, x0 = 200, y0 = 840, w = 1560, h = 560, n = Hs.length, bw = w / n, mx = Math.max(...Hs);
  text(p.head || "where each storm first reached tropical-storm strength · distance from the equator · NOAA IBTrACS", x0, 200, { px: 30, color: C.dim });
  const g = ease(prog(t, d * 0.05, d * 0.45));
  Hs.forEach((v, i) => { const bh = (v / mx) * h * g; rect(x0 + i * bw + 3, y0 - bh, bw - 6, bh, i < 5 ? C.ember : C.sea, 3);
    if (i % 5 === 0) text(i + "°", x0 + i * bw + bw / 2, y0 + 40, { px: 24, color: C.dim, align: "center" }); });
  ctx.fillStyle = C.ink; ctx.fillRect(x0, y0, w, 3);
  text("degrees from the equator (north or south)", x0 + w / 2, y0 + 86, { px: 26, color: C.dim, align: "center" });
  ctx.globalAlpha = fadeIn(t, d * 0.5, 0.6); const c = EP.data.counts;
  rect(x0 + 860, 330, 700, 150, "#fbf8f1", 8, C.ink, 2);
  text(c.gen_below5 + " of " + fmt(c.storms) + " storms", x0 + 890, 395, { px: 46, weight: 900, color: C.ember });
  text("started within 5° of the equator (" + (c.gen_below5_share * 100).toFixed(2) + "%)", x0 + 890, 450, { px: 30, color: C.ink });
  ctx.globalAlpha = 1;
};
S.fcurve = (t, d, p) => {
  const x0 = 240, y0 = 560, w = 1440, h = 300, L = 40, X = (la) => x0 + ((la + L) / (2 * L)) * w, f = (la) => 2 * 7.2921e-5 * Math.sin(la * Math.PI / 180), fm = f(L);
  const Y = (v) => y0 - (v / fm) * h;
  text(p.head || "the spin of the ground under your feet, around the vertical · f = 2 × Earth's spin × sin(latitude)", x0, 180, { px: 30, color: C.dim });
  ctx.fillStyle = C.ink; ctx.fillRect(x0, y0 - 1, w, 3); ctx.fillRect(X(0) - 1, y0 - h - 20, 3, 2 * h + 40);
  [-40, -30, -20, -10, 0, 10, 20, 30, 40].forEach((la) => text(Math.abs(la) + "°" + (la > 0 ? "N" : la < 0 ? "S" : ""), X(la), y0 + h + 60, { px: 24, color: C.dim, align: "center" }));
  const g = ease(prog(t, d * 0.05, d * 0.5)); const pts = []; for (let la = -L; la <= -L + 2 * L * g; la += 0.5) pts.push([X(la), Y(f(la))]);
  line(pts, C.sea, 7);
  text("turns anticlockwise", X(28), Y(fm) - 30, { px: 28, weight: 700, color: C.sea, align: "center" });
  text("turns clockwise", X(-22), Y(-fm) - 20, { px: 28, weight: 700, color: C.sea, align: "center" });
  (p.marks || []).forEach((m, i) => { const a = fadeIn(t, d * (0.5 + i * 0.1), 0.5); ctx.globalAlpha = a; const yy = Y(f(m));
    ctx.fillStyle = m === 0 ? C.ember : C.ink; ctx.beginPath(); ctx.arc(X(m), yy, 12, 0, 7); ctx.fill();
    const per = m === 0 ? "the ground does not turn at all" : "the ground turns once in " + Math.abs(Math.round(4 * Math.PI / f(m) / 3600)) + " h";
    const lab = Math.abs(m) + "°" + (m > 0 ? "N" : m < 0 ? "S" : "") + ": " + per, right = m >= 25 || m < 0;
    text(lab, right ? X(m) - 26 : X(m) + 26, yy + (m === 0 ? 50 : m < 0 ? 44 : m >= 25 ? -24 : 10), { px: 28, weight: 900, color: m === 0 ? C.ember : C.ink, align: right ? "right" : "left" }); ctx.globalAlpha = 1; });
};
S.hbars = (t, d, p) => {
  const R = p.rows, x0 = p.x0 || 560, y0 = p.y0 || 260, lh = p.lh || 100, bw = p.bw || 1000, max = p.max;
  text(p.head, 200, y0 - 50, { px: 30, color: C.dim });
  R.forEach((r, i) => { const s = d * (0.06 + i * (p.step || 0.1)), a = fadeIn(t, s, 0.5), g = ease(prog(t, s, s + 0.9)), y = y0 + i * lh; ctx.globalAlpha = a;
    text(r.label, x0 - 30, y + 50, { px: 34, align: "right", weight: 700 }); const len = Math.max(0, (r.value / max) * bw * g);
    rect(x0, y + 12, len, 56, r.col || C.sea, 6); text(r.txt, x0 + len + 20, y + 54, { px: 42, weight: 900, mono: true, color: r.tcol || C.ink });
    if (p.ticks && p.ticks[i] !== undefined && p.ticks[i] !== null) { ctx.fillStyle = C.ink; ctx.fillRect(x0 + (p.ticks[i] / max) * bw - 2, y + 4, 4, 72); } });
  ctx.globalAlpha = 1; if (p.foot) { ctx.globalAlpha = fadeIn(t, d * 0.75, 0.5); text(p.foot, 200, y0 + R.length * lh + 40, { px: 28, color: C.dim }); ctx.globalAlpha = 1; }
};
S.dipsim = (t, d, p) => {
  const D = EP.data.dip, lats = p.lats || [0, 15], ph = 300, x0 = 260, w = 1400, sk = D.sample_km, n = D.series["0"][0].eta.length, rmax = (n - 1) * sk;
  const k = Math.min(D.series["0"].length - 1, Math.floor(prog(t, d * 0.08, d * 0.85) * (D.series["0"].length - 1)));
  text(p.head || "a dip of low pressure, released at rest · dashed: the dip at the start · simulated", x0 - 60, 170, { px: 30, color: C.dim });
  rect(W - 470, 120, 350, 70, C.ink, 8); text("day " + (D.series["0"][k].t_h / 24).toFixed(1), W - 295, 167, { px: 36, weight: 900, align: "center", color: "#fbf8f1", mono: true });
  lats.forEach((la, j) => { const S0 = D.series[String(la)][k], top = 250 + j * (ph + 120), base = top + 90, sc = 190 / D.eta0;
    const X = (r) => x0 + w / 2 + (r / rmax) * (w / 2);
    ctx.fillStyle = "rgba(156,197,211,0.45)"; ctx.beginPath(); ctx.moveTo(x0, top + ph);
    for (let i = n - 1; i >= 0; i--) ctx.lineTo(X(-i * sk), base + S0.eta[i] * sc); for (let i = 0; i < n; i++) ctx.lineTo(X(i * sk), base + S0.eta[i] * sc);
    ctx.lineTo(x0 + w, top + ph); ctx.closePath(); ctx.fill();
    const S00 = D.series[String(la)][0], p0 = []; for (let i = n - 1; i >= 0; i--) p0.push([X(-i * sk), base + S00.eta[i] * sc]); for (let i = 0; i < n; i++) p0.push([X(i * sk), base + S00.eta[i] * sc]); line(p0, C.faint, 3, [10, 10]);
    const pts = []; for (let i = n - 1; i >= 0; i--) pts.push([X(-i * sk), base + S0.eta[i] * sc]); for (let i = 0; i < n; i++) pts.push([X(i * sk), base + S0.eta[i] * sc]); line(pts, C.ink, 4);
    ctx.fillStyle = C.rock; ctx.fillRect(x0, top + ph, w, 8);
    text(la === 0 ? "at the equator (0°)" : la + "° north", x0 - 60, top + 10, { px: 36, weight: 900, color: la === 0 ? C.ember : C.sea });
    const kept = S0.eta_centre / D.eta0; text("dip left at the centre: " + Math.max(0, kept * 100).toFixed(0) + "%   ·   wind: " + S0.vmax.toFixed(1) + " m/s", x0 + w, top + 10, { px: 30, weight: 700, align: "right" });
    if (la !== 0) { const sp = Math.min(1, S0.vmax / 1.4); ctx.save(); ctx.translate(X(0), base - 40); ctx.rotate(-t * 1.2 * sp); ctx.strokeStyle = C.sea; ctx.lineWidth = 5;
      ctx.beginPath(); ctx.arc(0, 0, 34, 0.3, 5.2); ctx.stroke(); ctx.restore(); }
    text("3,000 km", X(-rmax) + 6, top + ph + 44, { px: 22, color: C.dim }); text("3,000 km", X(rmax) - 6, top + ph + 44, { px: 22, color: C.dim, align: "right" }); });
};
S.table = (t, d, p) => {
  const x0 = p.x0 || 260, y0 = p.y0 || 260, lh = p.lh || 78, cols = p.cols;
  text(p.head, x0, y0 - 60, { px: 30, color: C.dim });
  p.hdr.forEach((h, j) => text(h, x0 + cols[j], y0, { px: 26, weight: 900, color: C.dim }));
  p.rows.forEach((r, i) => { ctx.globalAlpha = fadeIn(t, d * (0.05 + i * (p.step || 0.07)), 0.4); const y = y0 + 30 + i * lh, hi = (p.hl || []).includes(i);
    rect(x0 - 20, y, cols[cols.length - 1] + 360, lh - 12, hi ? "rgba(217,85,44,0.12)" : "#fbf8f1", 6, C.faint, 1);
    r.forEach((c, j) => text(String(c), x0 + cols[j], y + lh / 2 + 6, { px: 34, weight: j === 0 ? 900 : 400, mono: j > 0, color: hi ? C.ember : C.ink })); });
  ctx.globalAlpha = 1; if (p.foot) { ctx.globalAlpha = fadeIn(t, d * 0.75, 0.5); text(p.foot, x0, y0 + 60 + p.rows.length * lh, { px: 28, color: C.dim }); ctx.globalAlpha = 1; }
};
S.agnitrack = (t, d, p) => {
  const A = EP.data.agni, la0 = -1.5, la1 = Math.max(...A.map((a) => a[1])) + 1, lo0 = Math.min(...A.map((a) => a[2])) - 1, lo1 = Math.max(...A.map((a) => a[2])) + 1;
  const x0 = 200, y0 = 220, w = 1100, h = 700, X = (lo) => x0 + ((lo - lo0) / (lo1 - lo0)) * w, Y = (la) => y0 + ((la1 - la) / (la1 - la0)) * h;
  text(p.head || "Cyclone Agni, November 2004 · US Navy JTWC track in NOAA IBTrACS · every 3 hours", x0, 180, { px: 30, color: C.dim });
  rect(x0, y0, w, h, "#fbf8f1", 6, C.faint, 2); ctx.fillStyle = C.ember; ctx.fillRect(x0, Y(0) - 3, w, 6); text("equator", x0 + 12, Y(0) + 36, { px: 26, weight: 900, color: C.ember });
  for (let la = 2; la < la1; la += 2) { ctx.fillStyle = C.grid; ctx.fillRect(x0, Y(la), w, 2); text(la + "°N", x0 - 12, Y(la) + 8, { px: 22, color: C.dim, align: "right" }); }
  const n = Math.round(A.length * ease(prog(t, d * 0.05, d * 0.8))); let best = null;
  for (let i = 1; i < n; i++) { const w1 = A[i][3] || 20; line([[X(A[i - 1][2]), Y(A[i - 1][1])], [X(A[i][2]), Y(A[i][1])]], w1 >= 64 ? C.ember : w1 >= 34 ? C.sun : C.faint, 4 + w1 / 10); if (!best || A[i][1] < best[1]) best = A[i]; }
  if (best) { ctx.fillStyle = C.ink; ctx.beginPath(); ctx.arc(X(best[2]), Y(best[1]), 10, 0, 7); ctx.fill();
    text("closest: " + best[1].toFixed(1) + "°N, about " + Math.round(best[1] * 111) + " km from the equator", X(best[2]) - 16, Y(best[1]) + 36, { px: 28, weight: 900, align: "right" }); }
  const L = [[C.faint, "below storm strength"], [C.sun, "tropical storm, 34+ knots"], [C.ember, "hurricane strength, 64+ knots"]];
  L.forEach(([c, s], i) => { rect(x0 + w + 60, y0 + 40 + i * 60, 50, 14, c, 4); text(s, x0 + w + 130, y0 + 56 + i * 60, { px: 28 }); });
  if (p.foot) { ctx.globalAlpha = fadeIn(t, d * 0.7, 0.5); ctx.fillStyle = C.sea; font(34, SANS, 900); ctx.textAlign = "left"; wrapLines(ctx, p.foot, 480).forEach((l, i) => ctx.fillText(l, x0 + w + 60, y0 + 300 + i * 48)); ctx.globalAlpha = 1; }
};
S.hemispin = (t, d, p) => {
  const cx = W / 2, yN = 330, yS = 790, r = 150;
  ctx.fillStyle = C.ember; ctx.fillRect(160, 560 - 3, W - 320, 6); text("equator: no spin to borrow", 180, 540, { px: 30, weight: 900, color: C.ember });
  const spiral = (y, dir, col) => { ctx.save(); ctx.translate(cx, y); ctx.rotate(dir * t * 1.1); ctx.strokeStyle = col; ctx.lineWidth = 7; ctx.lineCap = "round";
    for (let a = 0; a < 3; a++) { ctx.beginPath(); for (let s = 0; s <= 1; s += 0.02) { const ang = a * 2.094 + dir * -s * 4.2, rr = 18 + s * r; s ? ctx.lineTo(rr * Math.cos(ang), rr * Math.sin(ang)) : ctx.moveTo(rr * Math.cos(ang), rr * Math.sin(ang)); } ctx.stroke(); }
    ctx.restore(); };
  spiral(yN, -1, C.sea); spiral(yS, 1, C.deep);
  text("north: storms turn anticlockwise", cx + 230, yN + 12, { px: 36, weight: 900 }); text("south: storms turn clockwise", cx + 230, yS + 12, { px: 36, weight: 900 });
  if (p.foot) { ctx.globalAlpha = fadeIn(t, d * 0.6, 0.5); text(p.foot, cx - 230, 560 + 70, { px: 30, color: C.dim, align: "right" }); ctx.globalAlpha = 1; }
};
/* ---------- ec03: hail ---------- */
const STORM = { x0: 220, y0: 200, w: 1480, h: 700, km: 15, top: 14000 };
const sX = (m) => STORM.x0 + ((m / 1000 + STORM.km) / (2 * STORM.km)) * STORM.w, sY = (z) => STORM.y0 + STORM.h - (z / STORM.top) * STORM.h;
function stormFrame(W) {
  rect(STORM.x0, STORM.y0, STORM.w, STORM.h, "#fbf8f1", 6, C.faint, 2);
  const rx = EP.data.rx_km * 1000;               // updraft strength as shading: same formula as the simulation (hump in z, Gaussian in x)
  for (let i = 0; i < 74; i++) for (let j = 0; j < 35; j++) {
    const x = -15000 + (i + 0.5) * 30000 / 74, z = (j + 0.5) * 14000 / 35; const hz = (z <= 1000 || z >= 13000) ? 0 : Math.pow(Math.sin(Math.PI * (z - 1000) / 12000), 1.2);
    const s = hz * Math.exp(-((x / rx) ** 2)); if (s < 0.04) continue;
    ctx.fillStyle = `rgba(31,111,139,${(0.42 * s).toFixed(3)})`; ctx.fillRect(sX(x - 205), sY(z + 200), STORM.w / 74 + 1, STORM.h / 35 + 1); }
  const lv = (z, lab, col) => { line([[STORM.x0, sY(z)], [STORM.x0 + STORM.w, sY(z)]], col, 3, [12, 10]); text(lab, STORM.x0 + STORM.w - 14, sY(z) - 12, { px: 24, weight: 700, color: col, align: "right" }); };
  lv(EP.data.freezing_m, "0 °C: below here hail melts", C.ember); lv(EP.data.m40_m, "−40 °C: above here no liquid water", C.dim);
  for (let z = 0; z <= 14000; z += 2000) text(z / 1000 + " km", STORM.x0 - 14, sY(z) + 8, { px: 22, color: C.dim, align: "right" });
  ctx.fillStyle = C.rock; ctx.fillRect(STORM.x0, sY(0), STORM.w, 8);
  text("blue = updraft, peak " + W + " m/s (" + Math.round(W * 3.6) + " km/h) · 30 km slice through the storm", STORM.x0, STORM.y0 - 22, { px: 28, color: C.dim });
}
S.hailstorm = (t, d, p) => {
  const R = EP.data.runs.find((r) => r.W === p.W), P = R.path, n = Math.max(1, Math.floor(P.length * prog(t, d * 0.04, d * (p.to || 0.9))));
  stormFrame(p.W); if (p.nopath) return;
  const pts = P.slice(0, n).map((q) => [sX(q[0]), sY(q[1])]); line(pts, C.ink, 3);
  const q = P[n - 1], r = 6 + q[2] * 0.35;
  ctx.fillStyle = "#e8f1f4"; ctx.strokeStyle = C.deep; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(sX(q[0]), sY(q[1]), r, 0, 7); ctx.fill(); ctx.stroke();
  rect(W - 520, 120, 400, 70, C.ink, 8);
  text(`${(q[0] === undefined ? 0 : n * 10 / 60).toFixed(0)} min · ${q[2].toFixed(0)} mm`, W - 320, 167, { px: 36, weight: 900, align: "center", color: "#fbf8f1", mono: true });
};
S.hailgrid = (t, d, p) => {
  const R = EP.data.runs.find((r) => r.W === p.W); stormFrame(p.W);
  const show = Math.floor(R.grid.length * ease(prog(t, d * 0.05, d * 0.6)));
  R.grid.slice(0, show).forEach(([x0, z0, o, mm]) => { const x = sX(x0), y = sY(z0);
    if (o !== "g" || mm <= 0) { ctx.fillStyle = "rgba(169,159,142,0.8)"; ctx.beginPath(); ctx.arc(x, y, 4, 0, 7); ctx.fill(); return; }
    ctx.fillStyle = mm >= 70 ? C.ember : mm >= 25 ? C.sun : C.sea; ctx.beginPath(); ctx.arc(x, y, 5 + mm / 9, 0, 7); ctx.fill(); });
  ctx.globalAlpha = fadeIn(t, d * 0.6, 0.5);
  const L = [["rgba(169,159,142,0.9)", "melted before the ground"], [C.sea, "under 25 mm"], [C.sun, "25 to 70 mm"], [C.ember, "baseball (70 mm) or bigger"]];
  L.forEach(([c, s], i) => { ctx.fillStyle = c; ctx.beginPath(); ctx.arc(STORM.x0 + 40, 990 + 0 * i, 0, 0, 0); ctx.fill();
    ctx.beginPath(); ctx.arc(STORM.x0 + 30 + i * 380, 960, 12, 0, 7); ctx.fill(); text(s, STORM.x0 + 52 + i * 380, 969, { px: 26 }); });
  text("each dot: where a 5 mm ice embryo started · " + R.melted + " of " + R.n + " melted · " + R.big[">=70"] + " grew past a baseball", STORM.x0, 1030, { px: 26, color: C.dim });
  ctx.globalAlpha = 1;
};
S.hailsizes = (t, d, p) => {
  const Z = EP.data.sizes, sc = p.sc || 2.0, base = 760; let x = 200;
  text(p.head || "to scale · NOAA's size names", 200, 200, { px: 30, color: C.dim });
  ctx.fillStyle = C.ink; ctx.fillRect(160, base + 2, W - 320, 3);
  Z.forEach(([name, mm], i) => { const a = fadeIn(t, d * (0.05 + i * 0.1), 0.5); ctx.globalAlpha = a; const r = (mm * sc) / 2, cx = x + r;
    ctx.fillStyle = i === Z.length - 1 ? "#dbe8ec" : "#eef4f6"; ctx.strokeStyle = C.deep; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(cx, base - r, r, 0, 7); ctx.fill(); ctx.stroke();
    text(name, cx, base + 50, { px: 28, weight: 900, align: "center" }); text(Math.round(mm) + " mm", cx, base + 88, { px: 26, align: "center", mono: true, color: C.dim });
    x = cx + r + (i < 3 ? 70 : 60); });
  ctx.globalAlpha = 1;
};
S.fallspeed = (t, d, p) => {
  const R = p.rows, x0 = 620, y0 = 280, lh = 140, bw = 1050, max = 220, X = (v) => x0 + (v / max) * bw;
  text("how fast a hailstone falls · bar: solid ice sphere, this model · band: NSSL, real stones in wind tunnels", 200, y0 - 60, { px: 28, color: C.dim });
  R.forEach((r, i) => { const s = d * (0.06 + i * 0.14), a = fadeIn(t, s, 0.5), g = ease(prog(t, s, s + 0.9)), y = y0 + i * lh; ctx.globalAlpha = a;
    text(r.label, x0 - 30, y + 48, { px: 32, align: "right", weight: 700 });
    rect(X(r.lo), y + 4, X(r.hi || r.lo + 50) - X(r.lo), 72, "rgba(224,160,48,0.35)", 6, null);
    if (!r.hi) text("NSSL: over " + r.lo + " km/h", X(r.lo) + 10, y - 4, { px: 22, color: C.dim });
    rect(x0, y + 22, (r.model / max) * bw * g, 36, C.deep, 4); text(r.model + " km/h", x0 + (r.model / max) * bw * g + 16, y + 52, { px: 34, weight: 900, mono: true }); });
  ctx.globalAlpha = fadeIn(t, d * 0.75, 0.5); text("real hailstones are lumpy and porous, so they fall slower than solid spheres", 200, y0 + R.length * lh + 30, { px: 28, color: C.sea, weight: 700 }); ctx.globalAlpha = 1;
};
function renderAt(T) {
  const tl = EP.timeline.beats; let k = 0;
  while (k < tl.length - 1 && T >= tl[k + 1].start) k++;
  const b = tl[k], beat = EP.storyboard.beats[k], t = Math.max(0, T - b.start), last = k === tl.length - 1, d = last ? (EP.timeline.total - b.start) : b.dur;
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
  // paper: a faint notebook grid that drifts very slowly, and a warm vignette
  const drift = (T * 2) % 48; ctx.fillStyle = C.grid;
  for (let x = -48 + drift; x < W; x += 48) ctx.fillRect(x, 0, 1, H); for (let y = -48 + drift * 0.4; y < H; y += 48) ctx.fillRect(0, y, W, 1);
  const g = ctx.createRadialGradient(W / 2, H / 2, 300, W / 2, H / 2, 1300); g.addColorStop(0, "rgba(243,237,226,0)"); g.addColorStop(1, "rgba(150,120,80,0.22)");
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const edge = Math.min(ease(prog(t, 0, 0.35)), last ? 1 : 1 - ease(prog(t, d - 0.25, d)));
  const z = 1 + 0.012 * prog(t, 0, d) + 0.02 * (1 - edge);
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-W / 2, -H / 2);
  S[beat.scene](t, b.speech + 0.01, beat.p || {});
  ctx.restore(); ctx.globalAlpha = 1;
  if (edge < 1) { ctx.globalAlpha = 1 - edge; ctx.fillStyle = C.bg; ctx.fillRect(0, 100, W, H - 112); ctx.globalAlpha = 1; }
  if (beat.chapter) {   // chapter tab, top left, like a notebook divider
    const fresh = k === 0 || EP.storyboard.beats[k - 1].chapter !== beat.chapter, s1 = fresh ? ease(prog(t, 0.05, 0.6)) : 1;
    const label = beat.chapter, w = measure(label, 26, false, 900) + 44; ctx.globalAlpha = s1;
    rect(60 - (1 - s1) * 40, 36, w, 46, C.sea, 6); text(label, 82 - (1 - s1) * 40, 68, { px: 26, weight: 900, color: "#fbf8f1" }); ctx.globalAlpha = 1;
  }
  ctx.fillStyle = C.paper2; ctx.fillRect(0, H - 10, W, 10); ctx.fillStyle = C.ember; ctx.fillRect(0, H - 10, W * (T / EP.timeline.total), 10);
}
function init() { const c = document.getElementById("c"); ctx = c.getContext("2d"); return document.fonts.ready.then(() => true); }
function frameJPEG(T, q) { renderAt(T); return document.getElementById("c").toDataURL("image/jpeg", q || 0.93).split(",")[1]; }

/* ---------- vertical Shorts ---------- */
let shortCanvas = null;
function wrapLines(c2, str, maxW) { const words = str.split(" "), lines = []; let cur = "";
  for (const w of words) { const t = cur ? cur + " " + w : w; if (c2.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; }
  if (cur) lines.push(cur); return lines; }
function frameShort(T, cfg) {
  renderAt(T);
  if (!shortCanvas) { shortCanvas = document.createElement("canvas"); shortCanvas.width = 1080; shortCanvas.height = 1920; }
  const c2 = shortCanvas.getContext("2d"), SW = 1080, SH = 1920, main = document.getElementById("c");
  c2.fillStyle = C.bg; c2.fillRect(0, 0, SW, SH);
  const sx = cfg.sx, sw = cfg.sw, sy = 104, sh = 968, dh = Math.round(sh * SW / sw), dy = 520;
  if (!cfg.tag) { c2.drawImage(main, sx, sy, sw, sh, 0, dy, SW, dh); c2.fillStyle = C.ink; c2.fillRect(0, dy - 3, SW, 3); c2.fillRect(0, dy + dh, SW, 3); }
  c2.textAlign = "center"; c2.textBaseline = "alphabetic";
  cfg.head.forEach((l, i) => { c2.font = `900 72px ${SANS}`; c2.fillStyle = i === cfg.head.length - 1 ? C.ember : C.ink; c2.fillText(l, SW / 2, 270 + i * 92); });
  if (cfg.tag) { c2.font = `900 96px ${SANS}`; c2.fillStyle = C.ink; c2.fillText("Earth Worked Out", SW / 2, 880);
    c2.font = `700 46px ${SANS}`; c2.fillStyle = C.sea; c2.fillText("Real physics, run on screen.", SW / 2, 960);
    c2.font = `700 50px ${SANS}`; c2.fillStyle = C.ink; wrapLines(c2, cfg.cap, 900).forEach((l, i) => c2.fillText(l, SW / 2, 1150 + i * 70)); }
  else if (cfg.cap) { c2.font = `700 50px ${SANS}`; const lines = wrapLines(c2, cfg.cap, 900), y0 = dy + dh + 110; lines.forEach((l, i) => { c2.fillStyle = C.ink; c2.fillText(l, SW / 2, y0 + i * 68); }); }
  c2.font = `900 34px ${SANS}`; c2.fillStyle = C.sea; c2.fillText("EARTH WORKED OUT", SW / 2, 130);
  return shortCanvas.toDataURL("image/jpeg", 0.93).split(",")[1];
}
function thumbShort(T, cfg, th) {
  frameShort(T, cfg); const c = shortCanvas.getContext("2d"), SW = 1080;
  c.fillStyle = C.bg; c.fillRect(0, 0, SW, 510); c.textAlign = "center";
  c.font = `900 34px ${SANS}`; c.fillStyle = C.sea; c.fillText("EARTH WORKED OUT", SW / 2, 110);
  th.big.forEach((l, i) => { let s = 150; c.font = `900 ${s}px ${SANS}`; while (c.measureText(l).width > 980) { s -= 4; c.font = `900 ${s}px ${SANS}`; }
    c.fillStyle = i === th.big.length - 1 ? C.ember : C.ink; c.fillText(l, SW / 2, 270 + i * 160); });
  c.font = `900 64px ${SANS}`; c.fillStyle = C.sea; wrapLines(c, th.small, 940).forEach((l, i) => c.fillText(l, SW / 2, 1520 + i * 84));
  return shortCanvas.toDataURL("image/jpeg", 0.92).split(",")[1];
}
