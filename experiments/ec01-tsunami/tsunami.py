"""How fast would you need to run to escape a tsunami?  python3 tsunami.py -> results.json  (about 2 minutes)

A 1D shallow-water simulation (finite volume, HLL fluxes, hydrostatic reconstruction for wetting and drying, so the
same code handles the open ocean, the shore and dry land). The seabed is an idealised but typical profile: 4,000 m deep
ocean, a continental slope, a 50 km shelf at about 100 m, a 1-in-100 beach and land rising at 1 in 200.
A single wave with a 2 m crest and a 100 km length starts in the deep ocean and travels towards the coast.
It records: the crest speed against the theory sqrt(g * depth), the wave height as it shoals, the flooding front on
land (position and speed second by second), and how far inland and how high it reaches.
This is a model, not a forecast for any real coast: real coasts, bays and waves differ."""
import json, math, numpy as np, pathlib, sys
MODE = sys.argv[1] if len(sys.argv) > 1 else "crest"   # "crest": a crest arrives first; "trough": the sea draws back first
H = pathlib.Path(__file__).resolve().parent
g = 9.81
L, dx = 230_000.0, 25.0                      # domain length (m) and cell size (m); x = 0 is far offshore
x = np.arange(0, L, dx) + dx / 2; n = len(x)
SHORE = 200_000.0                            # where the still sea meets the land
def bed(x):                                  # bed elevation z (m), sea level = 0
    z = np.empty_like(x)
    d = SHORE - x                            # distance offshore
    z[:] = -4000.0
    slope = (d < 110_000) & (d >= 60_000)    # continental slope: 4000 m -> 100 m over 50 km
    z[slope] = -100.0 - (d[slope] - 60_000) / 50_000 * 3900.0
    shelf = (d < 60_000) & (d >= 2_000)      # shelf: 100 m -> 20 m
    z[shelf] = -20.0 - (d[shelf] - 2_000) / 58_000 * 80.0
    near = (d < 2_000) & (d >= 0)            # nearshore and beach: 20 m -> 0 at 1 in 100
    z[near] = -d[near] / 100.0
    land = d < 0                             # land rising inland at 1 in 200
    z[land] = -d[land] / 200.0
    return z
z = bed(x)
A, LAM, X0 = 2.0, 100_000.0, 40_000.0        # crest height, wave length, crest start
eta0 = A * np.exp(-((x - X0) / (LAM / 4)) ** 2)
if MODE == "trough":                         # a leading trough, then the crest: the sea draws back before the wave arrives
    eta0 = A * (np.exp(-((x - X0) / (LAM / 4)) ** 2) - np.exp(-((x - X0 - LAM / 2) / (LAM / 4)) ** 2))
h = np.maximum(eta0 - z, 0.0) * (z < 0)      # water depth (land starts dry)
hu = np.zeros(n)
# a wave travelling towards the coast: u = c * eta / h (linear long wave)
c0 = np.sqrt(g * np.maximum(-z, 1e-9)); hu[z < 0] = (c0 * eta0)[z < 0]
DRY = 1e-3
def step(h, hu, dt):
    u = np.where(h > DRY, hu / np.maximum(h, DRY), 0.0)
    eta = h + z
    # hydrostatic reconstruction at interfaces i+1/2
    zf = np.maximum(z[:-1], z[1:])
    hL = np.maximum(0.0, eta[:-1] - zf); hR = np.maximum(0.0, eta[1:] - zf)
    uL, uR = u[:-1], u[1:]
    cL, cR = np.sqrt(g * hL), np.sqrt(g * hR)
    sL = np.minimum(uL - cL, uR - cR); sR = np.maximum(uL + cL, uR + cR)
    FL1, FR1 = hL * uL, hR * uR
    FL2, FR2 = hL * uL * uL + 0.5 * g * hL * hL, hR * uR * uR + 0.5 * g * hR * hR
    den = np.where(sR - sL > 1e-12, sR - sL, 1e-12)
    F1 = np.where(sL >= 0, FL1, np.where(sR <= 0, FR1, (sR * FL1 - sL * FR1 + sL * sR * (hR - hL)) / den))
    F2 = np.where(sL >= 0, FL2, np.where(sR <= 0, FR2, (sR * FL2 - sL * FR2 + sL * sR * (hR * uR - hL * uL)) / den))
    # bed-slope source terms from the reconstruction (well balanced)
    hn, hun = h.copy(), hu.copy()
    hn[1:-1] -= dt / dx * (F1[1:] - F1[:-1])
    S_left = 0.5 * g * (h[1:-1] ** 2 - hR[:-1] ** 2)     # at interface i-1/2, right state
    S_right = 0.5 * g * (hL[1:] ** 2 - h[1:-1] ** 2)     # at interface i+1/2, left state
    hun[1:-1] -= dt / dx * (F2[1:] - F2[:-1] - S_right - S_left)
    hn = np.maximum(hn, 0.0); hun[hn <= DRY] = 0.0
    # Manning friction (n = 0.025), applied implicitly so it never reverses the flow
    un = np.where(hn > DRY, hun / np.maximum(hn, DRY), 0.0)
    cf = g * 0.025 ** 2 / np.maximum(hn, DRY) ** (4 / 3)
    hun = hn * un / (1 + dt * cf * np.abs(un))
    return hn, hun, np.abs(un).max() + np.sqrt(g * hn.max())
t, T_END, out_every = 0.0, 3600.0 * 1.2, 2.0
gauges = {"deep_4000m": 60_000, "slope_mid": 115_000, "shelf_edge": 140_000, "mid_shelf": 170_000, "near_20m": 198_000, "beach": SHORE}
gi = {k: int(v / dx) for k, v in gauges.items()}
series = {k: [] for k in gauges}; series["shoreline"] = []; near = []; front = []; snaps = []; crest_track = []
next_out = 0.0; maxeta = np.where(z < 0, eta0, -1e9); h0 = h.copy()
dt = 0.0
while t < T_END:
    u = np.where(h > DRY, hu / np.maximum(h, DRY), 0.0)
    smax = (np.abs(u) + np.sqrt(g * h)).max()
    dt = 0.45 * dx / smax
    h, hu, _ = step(h, hu, dt); t += dt
    eta = np.where(h > DRY, h + z, np.nan)
    maxeta = np.where(h > DRY, np.maximum(maxeta, h + z), maxeta)
    if t >= next_out:
        next_out += out_every
        for k, i in gi.items(): series[k].append([round(t, 1), round(float(h[i] + z[i]) if h[i] > DRY else 0.0, 3)])
        wet = np.where(h > 0.01)[0]; shore_now = float(x[wet.max()] - SHORE) if len(wet) else 0.0   # negative = sea has drawn back
        series.setdefault("shoreline", []).append([round(t, 1), round(shore_now, 1)])
        wet_land = np.where((z >= 0) & (h > 0.01))[0]
        fx = float(x[wet_land.max()] - SHORE) if len(wet_land) else 0.0
        fi = wet_land.max() if len(wet_land) else None
        front.append([round(t, 1), round(fx, 1), round(float(hu[fi] / h[fi]) if fi is not None else 0.0, 3), round(float(h[fi]) if fi is not None else 0.0, 3)])
        sea = (z < -5) & (x < SHORE)
        ci = int(np.nanargmax(np.where(sea, h + z, -1e9)))
        crest_track.append([round(t, 1), round(float(x[ci]), 1), round(float(h[ci] + z[ci]), 3), round(float(-z[ci]), 1)])
        if t > 2600 and int(t) % 4 < out_every:      # close-up of the last 10 km of sea and the first 2.5 km of land, every 4 s
            near.append({"t": round(t, 1), "eta": [None if not (h[i] > DRY) else round(float(h[i] + z[i]), 3) for i in range(int(190_000 / dx), int(202_500 / dx), 4)]})
        if int(t) % 60 < out_every:
            sel = slice(0, n, 40)
            snaps.append({"t": round(t, 1), "eta": [None if not (h[i] > DRY) else round(float(h[i] + z[i]), 3) for i in range(0, n, 40)]})
res = {"model": {"dx_m": dx, "domain_km": L / 1000, "shore_km": SHORE / 1000, "crest_m": A, "wavelength_km": LAM / 1000, "manning_n": 0.025,
                 "bed_every_1km": [[round(float(x[i]) / 1000, 2), round(float(z[i]), 1)] for i in range(0, n, 40)]},
       "gauges_m": gauges, "series": series, "front": front, "crest_track": crest_track, "snaps": snaps, "near": near,
       "near_bed": [[round((float(x[i]) - SHORE), 1), round(float(z[i]), 2)] for i in range(int(190_000 / dx), int(202_500 / dx), 4)],
       "max_inland_m": max(f[1] for f in front), "max_runup_m": float(np.nanmax(np.where((z >= 0) & (maxeta > z), maxeta, np.nan))) if np.any((z >= 0) & (maxeta > z)) else 0.0}
# crest speed against theory, per depth band (from the crest track, while the crest is in water deeper than 5 m)
ct = np.array(crest_track); spd = []
for a, b in zip(ct[:-15], ct[15:]):
    if b[1] > a[1] and a[3] > 5:
        v = (b[1] - a[1]) / (b[0] - a[0]); spd.append([round(float(a[3]), 1), round(float(v), 2), round(math.sqrt(g * a[3]), 2)])
res["crest_speed_vs_theory"] = spd
(H / ("results.json" if MODE == "crest" else "results_trough.json")).write_text(json.dumps(res))
print("max inland", res["max_inland_m"], "m; max runup", round(res["max_runup_m"], 2), "m; front samples", len(front))
fr = [f for f in front if f[1] > 0]
if fr: print("front first on land at t =", fr[0][0], "s; peak front speed", max(f[2] for f in fr), "m/s")
for k, s in series.items(): print(k, "max", max(v for _, v in s))
