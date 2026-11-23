"""ec02 extension: where and when storms form, from the same IBTrACS file as tracks.py (same strength rule).
For every storm that reached tropical-storm strength: its basin code at formation (IBTrACS BASIN: NA North Atlantic, EP eastern
Pacific, WP western Pacific, NI north Indian, SI south Indian, SP south Pacific, SA south Atlantic), hemisphere, and the month it
first reached that strength. Counts only seasons 1980 onward for the monthly profile (satellite era). -> basins.json
"""
import csv, json, collections, pathlib
src = pathlib.Path(__file__).parent / "data" / "ibtracs.ALL.list.v04r01.csv"
first = {}
with open(src, newline="") as fh:
    rd = csv.DictReader(fh); next(rd); wcols = [c for c in rd.fieldnames if c.endswith("_WIND") and not c.startswith("REUNION_R")]
    for row in rd:
        sid = row["SID"]
        if sid in first or row["NATURE"] != "TS": continue
        ws = []
        for c in wcols:
            try: ws.append(float(row[c]))
            except ValueError: pass
        if not ws or max(ws) < 34: continue
        try: lat = float(row["LAT"])
        except ValueError: continue
        first[sid] = {"basin": row["BASIN"].strip() or "NA", "lat": lat, "month": int(row["ISO_TIME"][5:7]), "season": int(row["SEASON"]), "name": row["NAME"]}
all_b = collections.Counter(v["basin"] for v in first.values())
sat = [v for v in first.values() if v["season"] >= 1980]
by_month = {"N": [0] * 12, "S": [0] * 12}
for v in sat: by_month["N" if v["lat"] > 0 else "S"][v["month"] - 1] += 1
sa = sorted([(v["season"], v["name"], round(v["lat"], 1)) for v in first.values() if v["basin"] == "SA"])
out = {"storms": len(first), "by_basin_all": dict(all_b), "sat_era_storms": len(sat), "sat_by_basin": dict(collections.Counter(v["basin"] for v in sat)),
       "by_month_sat": by_month, "south_atlantic": sa, "north_share_sat": round(sum(by_month["N"]) / len(sat), 3)}
json.dump(out, open(pathlib.Path(__file__).parent / "basins.json", "w"), indent=1)
print(out["storms"], out["by_basin_all"]); print("since 1980:", out["sat_era_storms"], out["sat_by_basin"], "north share", out["north_share_sat"])
print("N by month", by_month["N"]); print("S by month", by_month["S"]); print("SA:", sa)
