"""ec02 data.json from experiments/ec02-equator (results.json, spin.json, tracks.json, IBTrACS csv for Agni's full track)."""
import json, math, csv, pathlib
import numpy as np
H = pathlib.Path(__file__).resolve().parent; X = H.parent / "experiments" / "ec02-equator"
R = json.loads((X / "results.json").read_text()); SP = json.loads((X / "spin.json").read_text()); T = json.loads((X / "tracks.json").read_text()); BA = json.loads((X / "basins.json").read_text())
OM, Cg, R0 = 7.2921e-5, R["c_m_s"], R["R0_km"] * 1e3
tq = np.linspace(0, 12, 4000)
def theory(lat):                      # linear Rossby adjustment of a Gaussian dip: centre kept = int (r/L^2) K0(r/L) exp(-r^2/R0^2) dr
    f = 2 * OM * math.sin(math.radians(lat))
    if f == 0: return 0.0
    L = Cg / f; x = np.linspace(R0 * 1e-4, 8 * R0, 6000); k0 = np.trapezoid(np.exp(-np.outer(x / L, np.cosh(tq))), tq, axis=1)
    return float(np.trapezoid(x / L ** 2 * k0 * np.exp(-(x / R0) ** 2), x))
dip = {"lats": [r["lat"] for r in R["runs"]], "kept": [r["kept_fraction"] for r in R["runs"]], "theory": [round(theory(r["lat"]), 4) for r in R["runs"]],
       "eta0": R["runs"][0]["eta0_m_equiv"], "sample_km": R["dr_km"] * 6, "series": {str(r["lat"]): r["series"] for r in R["runs"] if r["lat"] in (0, 5, 15)}}
agni = []
with open(X / "data" / "ibtracs.ALL.list.v04r01.csv", newline="") as fh:
    rd = csv.DictReader(fh); next(rd)
    for row in rd:
        if row["SID"] == "2004332N02072":
            w = row["USA_WIND"].strip() or row["WMO_WIND"].strip()
            agni.append([row["ISO_TIME"], float(row["LAT"]), float(row["LON"]), float(w) if w else None])
hist = [T["genesis_abs_lat_hist"][str(k)] for k in range(0, 41)]
data = {"counts": {"systems": T["storms_total"], "storms": T["storms_at_ts_strength"], "first_season": T["first_season"],
                   "crossings_any": len(T["crossings_any_strength"]), "crossings_ts": len(T["crossings_at_ts_strength"]),
                   "gen_below5": sum(hist[:5]), "gen_below5_share": T["share_genesis_below_5deg"], "gen_below3": sum(hist[:3])},
        "hist": hist, "tracks": T["tracks"], "closest": T["closest_to_equator"][:8], "agni": agni, "spin": SP, "dip": dip, "basins": BA}
(H / "data.json").write_text(json.dumps(data, separators=(",", ":")))
print(data["counts"], "agni points", len(agni), "theory", dip["theory"], "kept", dip["kept"])
