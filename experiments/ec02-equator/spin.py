"""ec02: how much spin can inflowing air pick up from the planet? Exact angular-momentum bookkeeping, no friction.

A ring of air at rest relative to the ground at radius R0 has absolute angular momentum M = f R0^2 / 2 (from the Earth's
spin, f = 2 Omega sin(lat)). Pulled in to radius r while keeping M, its wind is v = f (R0^2 - r^2) / (2 r).
Real storms lose much of this to friction; this is the upper limit the planet's spin allows. -> spin.json
"""
import json, math
OM = 7.2921e-5; R0 = 500e3
lats = [0, 1.5, 5, 10, 15, 20, 30]; radii = [400e3, 300e3, 200e3, 100e3, 50e3, 30e3]
out = {"R0_km": R0 / 1e3, "rows": []}
for lat in lats:
    f = 2 * OM * math.sin(math.radians(lat))
    row = {"lat": lat, "f": f, "v": {str(int(r / 1e3)): round(f * (R0 ** 2 - r ** 2) / (2 * r), 1) for r in radii},
           "inertial_period_h": round(2 * math.pi / f / 3600, 1) if f else None}   # inertial period 2 pi / f (half the Foucault-pendulum day)
    out["rows"].append(row); print(lat, row["v"], "inertial period", row["inertial_period_h"], "h")
json.dump(out, open("spin.json", "w"), indent=1)
