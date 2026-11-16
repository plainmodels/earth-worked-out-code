"""Race the simulated flood front (results.json) against people moving at constant speeds, starting at the shoreline.
python3 race.py -> race.json.  For each speed: where the water catches them if they start the moment it reaches the
beach, and how many seconds of head start they need to stay ahead all the way to its furthest reach."""
import json, pathlib
H = pathlib.Path(__file__).resolve().parent; r = json.loads((H / "results.json").read_text())
fr = [f for f in r["front"] if f[1] > 0]
t0 = fr[0][0] - fr[0][1] / ((fr[5][1] - fr[0][1]) / (fr[5][0] - fr[0][0]))     # moment the water reaches the shoreline (back-interpolated)
F = [(0.0, 0.0)] + [(f[0] - t0, f[1]) for f in fr]                               # seconds since landfall, metres inland
reach = max(d for _, d in F)
def caught(speed, head, start=0.0):
    """Runner starts `start` metres inland and sets off `head` seconds before the water reaches the shoreline."""
    for t, d in F[1:]:
        if d >= start + speed * (t + head): return t, d
    return None
people = [("a brisk walk", 5), ("a jog", 10), ("a hard run", 20), ("a sprint", 25), ("Usain Bolt's top speed", 44.35)]
out = {"landfall_s_after_start": t0, "max_inland_m": reach, "people": []}
for name, kmh in people:
    v = kmh / 3.6; row = {"who": name, "kmh": kmh, "m_per_s": round(v, 2)}
    for start in (0, 100):
        c = caught(v, 0, start); need = 0
        while caught(v, need, start) and need < 3600: need += 1
        row[f"from_{start}m"] = {"caught": None if not c else {"s": round(c[0], 1), "m": round(c[1], 1)}, "head_start_needed_s": need}
        print(f"{name:24s} {kmh:5.1f} km/h from {start:3d} m:", ("caught after %.0f s at %.0f m" % c) if c else "never caught", "| head start needed", need, "s")
    out["people"].append(row)
out["front_profile"] = [[round(t, 1), round(d, 1)] for t, d in F]
out["front_speed_first_500m_ms"] = round(500 / next(t for t, d in F if d >= 500), 2)
(H / "race.json").write_text(json.dumps(out, indent=1))
