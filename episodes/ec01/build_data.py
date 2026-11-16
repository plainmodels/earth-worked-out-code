"""ec01/data.json from the simulation results (experiments/ec01-tsunami)."""
import json, math, pathlib
H = pathlib.Path(__file__).resolve().parent; X = H.parent / "experiments/ec01-tsunami"
R = json.loads((X / "results.json").read_text()); T = json.loads((X / "results_trough.json").read_text()); RC = json.loads((X / "race.json").read_text())
bands = [("4,000 m", 3000, 4100), ("1,000-3,000 m", 1000, 3000), ("150-1,000 m", 150, 1000), ("60-150 m", 60, 150), ("20-60 m", 20, 60), ("5-20 m", 5, 20)]
speeds = []
for lab, lo, hi in bands:
    s = [(v, th) for d, v, th in R["crest_speed_vs_theory"] if lo <= d < hi]
    speeds.append({"band": lab, "sim_kmh": round(3.6 * sum(a for a, _ in s) / len(s)), "theory_kmh": round(3.6 * sum(b for _, b in s) / len(s))})
heights = [{"where": lab, "m": round(max(v for _, v in R["series"][k]), 1)} for lab, k in
           [("deep ocean, 4,000 m", "deep_4000m"), ("continental slope", "slope_mid"), ("shelf edge, 100 m", "shelf_edge"), ("mid-shelf, 60 m", "mid_shelf"), ("near shore, 20 m", "near_20m"), ("the beach", "beach")]]
fr = RC["front_profile"]
d = {"bed": R["model"]["bed_every_1km"], "snaps": R["snaps"][::2], "near": R["near"][::2], "near_bed": R["near_bed"],
     "speeds": speeds, "heights": heights, "front": fr, "max_inland_m": R["max_inland_m"], "max_runup_m": round(R["max_runup_m"], 1),
     "people": RC["people"], "landfall_s": RC["landfall_s_after_start"],
     "shoreline_trough": [v for v in T["series"]["shoreline"] if 2400 <= v[0] <= 3700][::3], "trough_inland_m": T["max_inland_m"], "trough_runup_m": round(T["max_runup_m"], 1)}
(H / "data.json").write_text(json.dumps(d)); print("data.json", round(len(json.dumps(d)) / 1e6, 2), "MB;", speeds[0], speeds[-1], heights[-1])
