"""ec02: does the planet's spin let a low-pressure dip survive? Axisymmetric rotating shallow water (Rossby adjustment).

A dip in the 'surface' of a layer of air (equivalent depth H, gravity-wave speed c = sqrt(gH) = 50 m/s) is released at rest.
Without rotation the dip radiates away as gravity waves and the surface goes flat. With rotation f = 2 Omega sin(lat) part of it
is held in balance by a spinning wind. Nonlinear equations in r (u radial, v azimuthal, h depth), staggered grid, forward-backward
time stepping, a sponge at the outer edge so waves leave. Run: python adjust.py  -> results.json
"""
import json, math, numpy as np
OM, G = 7.2921e-5, 9.81
C = 50.0; H = C * C / G                    # equivalent depth for a 50 m/s first-mode gravity wave (~255 m)
R0, ETA0 = 600e3, 0.2 * H                # dip: Gaussian, 600 km wide, 20% of the layer depth
DR, RMAX, DT, DAYS = 5e3, 8000e3, 40.0, 4.0

def run(lat, snaps_every_h=3):
    f = 2 * OM * math.sin(math.radians(lat))
    n = int(RMAX / DR); rc = (np.arange(n) + 0.5) * DR; re = np.arange(n + 1) * DR     # h,v at centres; u at edges
    h = H - ETA0 * np.exp(-(rc / R0) ** 2); u = np.zeros(n + 1); v = np.zeros(n)
    sp = np.clip((rc - 0.75 * RMAX) / (0.25 * RMAX), 0, 1) ** 2 * 2e-3                   # sponge
    spe = np.interp(re, rc, sp)
    steps = int(DAYS * 86400 / DT); every = int(snaps_every_h * 3600 / DT); out = []
    for k in range(steps + 1):
        if k % every == 0:
            out.append({"t_h": round(k * DT / 3600, 2), "eta_centre": round(float(H - h[0]), 3),
                        "vmax": round(float(np.max(np.abs(v))), 3), "r_vmax_km": round(float(rc[np.argmax(np.abs(v))] / 1e3), 1),
                        "eta": [round(float(H - x), 2) for x in h[: int(3000e3 / DR): 6]],
                        "v": [round(float(x), 2) for x in v[: int(3000e3 / DR): 6]]})
        # continuity (flux form, r h u at edges)
        he = np.empty(n + 1); he[1:-1] = 0.5 * (h[1:] + h[:-1]); he[0] = h[0]; he[-1] = h[-1]
        flux = re * he * u; h = h - DT * (flux[1:] - flux[:-1]) / (rc * DR); h = h - DT * sp * (h - H)
        # radial momentum at edges (pressure gradient, Coriolis + curvature on v interpolated to edges)
        ve = np.zeros(n + 1); ve[1:-1] = 0.5 * (v[1:] + v[:-1])
        dhdr = np.zeros(n + 1); dhdr[1:-1] = (h[1:] - h[:-1]) / DR
        dudr = np.zeros(n + 1); dudr[1:-1] = (u[2:] - u[:-2]) / (2 * DR)
        u = u + DT * (-G * dhdr + f * ve + np.where(re > 0, ve ** 2 / np.maximum(re, 1), 0) - u * dudr) - DT * spe * u
        u[0] = 0.0; u[-1] = 0.0
        # azimuthal momentum at centres: dv/dt = -(f + v/r) u - u dv/dr
        uc = 0.5 * (u[1:] + u[:-1]); dvdr = np.gradient(v, DR)
        v = v + DT * (-(f + v / rc) * uc - uc * dvdr) - DT * sp * v
    return {"lat": lat, "f": f, "rossby_radius_km": (C / f / 1e3) if f else None, "eta0_m_equiv": ETA0,
            "kept_fraction": round(out[-1]["eta_centre"] / ETA0, 4), "series": out}

if __name__ == "__main__":
    res = {"c_m_s": C, "H_m": H, "R0_km": R0 / 1e3, "dr_km": DR / 1e3, "days": DAYS, "runs": []}
    for lat in [0, 1.5, 5, 10, 15, 20]:
        r = run(lat); res["runs"].append(r)
        print(f"lat {lat:>4}: kept {r['kept_fraction']*100:5.1f}% of the dip after {DAYS:.0f} days, max wind {r['series'][-1]['vmax']:.1f} m/s"
              f" at {r['series'][-1]['r_vmax_km']} km; Rossby radius {r['rossby_radius_km'] and round(r['rossby_radius_km'])} km", flush=True)
    json.dump(res, open("results.json", "w"))
