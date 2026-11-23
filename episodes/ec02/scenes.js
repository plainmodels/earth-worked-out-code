/* ec02 extra scenes: storms by month in each hemisphere (satellite era, 1980 on) */
S.ec02_months = (t, d, p) => {
  const M = EP.data.basins.by_month_sat, x0 = 260, y0 = 820, w = 1440, h = 520, bw = w / 12, mx = Math.max(...M.N, ...M.S);
  const names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  text(p.head || "month each storm first reached tropical-storm strength, 1980 on · NOAA IBTrACS", x0, 200, { px: 30, color: C.dim });
  const g = ease(prog(t, d * 0.05, d * 0.5));
  for (let i = 0; i < 12; i++) { const hn = (M.N[i] / mx) * h * g, hs = (M.S[i] / mx) * h * g, x = x0 + i * bw;
    rect(x + 8, y0 - hn, bw / 2 - 10, hn, C.sea, 3); rect(x + bw / 2 + 2, y0 - hs, bw / 2 - 10, hs, C.ember, 3);
    text(names[i], x + bw / 2, y0 + 40, { px: 26, color: C.dim, align: "center" }); }
  ctx.fillStyle = C.ink; ctx.fillRect(x0, y0, w, 3);
  rect(x0 + 20, 250, 26, 26, C.sea, 4); text("north of the equator", x0 + 60, 272, { px: 28, weight: 700 });
  rect(x0 + 380, 250, 26, 26, C.ember, 4); text("south of the equator", x0 + 420, 272, { px: 28, weight: 700 });
};
