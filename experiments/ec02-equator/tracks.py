"""ec02: what the record shows. Reads NOAA NCEI IBTrACS v04r01 (ibtracs.ALL.list.v04r01.csv, public domain) from data/.

A point counts as a tropical storm or stronger when NATURE is 'TS' and the highest maximum wind reported by any agency
(WMO_WIND, USA_WIND, TOKYO_WIND, CMA_WIND, ... any *_WIND column) is at least 34 knots. Crossings are also counted for any
recorded point (disturbances and depressions included). For each storm: where it first reached that strength (genesis), how close to the equator it ever was at that
strength, and whether it had such points in both hemispheres (a crossing). -> tracks.json
"""
import csv, json, collections, pathlib
src = pathlib.Path(__file__).parent / "data" / "ibtracs.ALL.list.v04r01.csv"
storms = collections.defaultdict(list)
with open(src, newline="") as fh:
    rd = csv.DictReader(fh); next(rd)                                  # second line holds units
    wcols = [c for c in rd.fieldnames if c.endswith("_WIND") and not c.startswith("REUNION_R")]
    for row in rd:
        ws = []
        for c in wcols:
            try: ws.append(float(row[c]))
            except ValueError: pass
        w = max(ws) if ws else 0.0
        try: lat = float(row["LAT"]); lon = float(row["LON"])
        except ValueError: continue
        storms[row["SID"]].append((row["ISO_TIME"], lat, lon, w, row["NATURE"], int(row["SEASON"]), row["NAME"], row["BASIN"]))
gen_hist = collections.Counter(); closest = []; crossings = []; n_ts = 0; lines = []; first_season = 9999
any_cross = []
for sid, pts in storms.items():
    if any(p[1] > 0 for p in pts) and any(p[1] < 0 for p in pts): any_cross.append((sid, pts[0][6], pts[0][5], round(max(p[3] for p in pts)), pts[0][7]))
    ts = [p for p in pts if p[4] == "TS" and p[3] >= 34]
    if not ts: continue
    n_ts += 1; first_season = min(first_season, ts[0][5])
    g = ts[0]; gen_hist[int(abs(g[1]))] += 1
    m = min(ts, key=lambda p: abs(p[1])); closest.append((abs(m[1]), sid, m[6], m[5], m[1], m[2], m[3]))
    if any(p[1] > 0 for p in ts) and any(p[1] < 0 for p in ts): crossings.append(sid)
    if len(lines) < 100000: lines.append([[round(p[1], 1), round(p[2], 1)] for p in ts[::2]])
closest.sort()
out = {"source": "NOAA NCEI IBTrACS v04r01, ibtracs.ALL.list.v04r01.csv", "storms_at_ts_strength": n_ts, "first_season": first_season,
       "genesis_abs_lat_hist": {k: gen_hist[k] for k in range(0, 46)}, "crossings_at_ts_strength": crossings,
       "closest_to_equator": [{"abs_lat": c[0], "sid": c[1], "name": c[2], "season": c[3], "lat": c[4], "lon": c[5], "wind_kt": c[6]} for c in closest[:12]],
       "share_genesis_below_5deg": round(sum(gen_hist[k] for k in range(5)) / n_ts, 4), "tracks": lines, "storms_total": len(storms), "crossings_any_strength": any_cross}
json.dump(out, open(pathlib.Path(__file__).parent / "tracks.json", "w"))
print(len(storms), "systems in file;", len(any_cross), "have points on both sides at any strength:", any_cross[:10])
print(n_ts, "storms since", first_season, "| crossings:", len(crossings), "| below 5 deg at genesis:", out["share_genesis_below_5deg"])
for c in out["closest_to_equator"][:8]: print(c)
