"""Write ec02/storyboard.json. Numbers come from data.json (IBTrACS analysis and the simulations), so a re-run updates the narration."""
import json, math, pathlib
H = pathlib.Path(__file__).resolve().parent; D = json.loads((H / "data.json").read_text())
c = D["counts"]; dip = D["dip"]; kept = dict(zip(dip["lats"], dip["kept"])); th = dict(zip(dip["lats"], dip["theory"]))
sp = {r["lat"]: r["v"]["50"] for r in D["spin"]["rows"]}; cl = D["closest"]
agni = D["agni"]; a_min = min(agni, key=lambda a: a[1]); a_max = max((a for a in agni if a[3]), key=lambda a: a[3])
a_km = round(a_min[1] * 111); vam = next(x for x in cl if x["name"] == "VAMEI")
foucault = lambda la: round(4 * math.pi / (2 * 7.2921e-5 * math.sin(math.radians(la))) / 3600)
pc = lambda x: f"{max(0, x) * 100:.0f}" if x >= 0.01 or x <= 0 else f"{x * 100:.1f}"
B = []
def beat(id, chapter, scene, p, text, visual, say=None):
    b = {"id": id, "chapter": chapter, "scene": scene, "p": p, "text": text, "visual": visual}
    if say: b["say"] = say
    elif "Vamei" in text: b["say"] = text.replace("Vamei", "Vah-may")
    B.append(b)

beat("b01", "", "trackmap", {"reveal": True, "from": 0.03, "to": 0.75, "glow": 0.8},
     f"This is every tropical storm on record. {c['storms']:,} of them, from {c['first_season']} to this month, one line each, drawn from NOAA's global archive. They fill the oceans on both sides of the planet. Now look at the line in the middle.",
     "all storm tracks drawn in, oldest first; the equator glows at the end")
beat("b02", "", "trackmap", {"band": True, "cross": 0.3, "note": None},
     f"That is the equator. Storms come close to it. Not one is recorded crossing it. I checked every record in the archive: {c['systems']:,} storm systems, weak ones included, and not a single one has a position on both sides of the line.",
     "the map again with a band of 5 degrees either side; 'crossing the equator: 0'")
beat("b03", "", "title", {"title": ["Why hurricanes never", "cross the equator"], "sub": "the record, a spinning-planet simulation, and the storm that came within " + str(a_km) + " km"},
     "There is no wall there. So why does nothing cross?", "title card")
beat("b04", "In this video", "bullets", {"head": "We will find out", "items": ["Where a hurricane's spin comes from", "Why the equator has none to give", "What a simulation does with a dip in the air", f"The storm that came within {a_km} km"]},
     f"We will find out where a hurricane's spin comes from, why the equator has none to give, what a simulation of a spinning planet does with a simple dip in the air, and what happened to the storm that came within {a_km} kilometres of the line.",
     "four bullets")

ch = "1 · The record"
beat("b05", ch, "vhist", {},
     f"Start with the record. For every storm, I found the place where it first became a tropical storm, with winds of at least 34 knots, about 63 kilometres an hour. Two thirds start between 10 and 20 degrees from the equator. Close to the equator, the bars almost vanish. Only {c['gen_below5']} of {c['storms']:,} storms started within 5 degrees of it.",
     "histogram of formation latitude; the bars within 5 degrees in red", say=None)
beat("b06", ch, "quote", {"lines": ["The textbooks say that cyclones such as hurricanes", "don't form within 300 kilometers", "(about 186 miles) of the equator."], "hl": [1], "src": "NASA Earth Observatory, “A Rare Cyclone on the Equator” (2003)", "src_short": "NASA", "foot": f"in the record: {c['gen_below3']} storms started within 3 degrees"},
     f"NASA puts the textbook rule like this: hurricanes don't form within 300 kilometres of the equator. In the archive, only {c['gen_below3']} storms started within 3 degrees, about 330 kilometres, and none of them crossed. So something near the equator stops storms from starting, and stops them from going over.",
     "NASA quote card")

ch = "2 · Borrowed spin"
beat("b07", ch, "equation", {"label": "where a storm's spin comes from", "eq": "f = 2 Ω sin(latitude)", "where": ["Ω: how fast the Earth spins, once a day", "f: how fast the ground turns around the vertical, where you stand"], "foot": "a hurricane borrows this spin"},
     "A hurricane is air spinning around a centre of low pressure. The spin has to come from somewhere, and it comes from the planet. The Earth turns once a day, and wherever you stand, the ground under you is slowly turning around the vertical line through your feet. How fast depends on latitude. Meteorologists call it the Coriolis parameter, f: twice the Earth's spin, times the sine of the latitude.",
     "equation card")
beat("b08", ch, "fcurve", {"marks": [30, 15, 5, 0]},
     f"Here is that spin, from 40 degrees south to 40 north. At 30 degrees, the ground turns once every {foucault(30)} hours. At 15 degrees, once every {foucault(15)}. At 5 degrees, once in {foucault(5)} hours. And at the equator it does not turn at all. North of the line it turns anticlockwise, south of it clockwise.",
     "curve of f against latitude, crossing zero at the equator", say=None)
beat("b09", ch, "hbars", {"head": "wind 50 km from the centre, if air drawn in from 500 km kept all the spin it borrowed · no friction, an upper limit",
                         "rows": [{"label": f"{la}°" if la else "0°, equator", "value": sp[la], "txt": f"{sp[la]:.0f} m/s", "col": C} for la, C in [(0, "#d9552c"), (1.5, "#1f6f8b"), (5, "#1f6f8b"), (10, "#1f6f8b"), (15, "#0f3f52"), (20, "#0f3f52")]],
                         "max": 130, "foot": "the same rule that speeds up a skater pulling in her arms"},
     f"That slow turn is enough. Air pulled in toward a low-pressure centre speeds up as it gets closer, like a skater pulling in her arms. Bring air in from 500 kilometres to 50, and at 15 degrees it could reach {sp[15]:.0f} metres a second, if nothing slowed it down. At 5 degrees, {sp[5]:.0f}. At the equator, the answer is zero. There is no spin to borrow, so there is nothing to speed up.",
     "bars: maximum spin-up by latitude; the equator bar is empty")
beat("b10", ch, "statement", {"lines": ["A hurricane runs on borrowed spin.", "At the equator,", "the planet lends none."], "accent": [2]},
     "A hurricane runs on borrowed spin, and at the equator the planet lends none. That is the idea. Now let's test it.",
     "statement")

ch = "3 · The simulation"
beat("b11", ch, "equation", {"label": "what the simulation does", "eq": "a dip, released at rest", "where": ["a layer of air with a dip in it: low pressure", "the same equations as the tsunami episode, plus the spin f"], "foot": "run at 0, 1.5, 5, 10, 15 and 20 degrees"},
     "I wrote a simulation of a layer of air on a spinning planet. In the middle I made a dip: a patch of low pressure, six hundred kilometres wide, with no wind at all. Then I let it go, at six different latitudes, and watched for four days.",
     "equation card")
beat("b12", ch, "dipsim", {"lats": [0, 15]},
     f"At the equator, air rushes in to fill the dip, and the dip spreads out as waves and disappears. After four days there is nothing left: the air is flat again, and there is no wind. At 15 degrees, the same dip does something different. The incoming air is turned sideways by the spin, and starts to circle. The circling wind holds part of the dip in place. After four days, {pc(kept[15])} percent of it is still there.",
     "two cross-sections of the air layer, 0 and 15 degrees, over four days")
beat("b13", ch, "hbars", {"head": "how much of the dip was still there after 4 days · simulated (bars) and the textbook formula (black ticks)",
                         "rows": [{"label": f"{la}°", "value": max(0, kept[la]) * 100, "txt": f"{pc(kept[la])}%", "col": "#d9552c" if la == 0 else "#1f6f8b"} for la in dip["lats"]],
                         "ticks": [th[la] * 100 for la in dip["lats"]], "max": 25, "foot": "the simulation and the formula for a spinning layer agree"},
     f"Here are all six runs. Nothing at the equator. {pc(kept[1.5])} percent at one and a half degrees, about {pc(kept[5])} percent at 5, {pc(kept[10])} at 10, {pc(kept[15])} at 15 and {pc(kept[20])} at 20. The black ticks are the textbook formula for a spinning layer, and the simulation lands on them. The closer to the equator, the less the planet can hold.",
     "bars of dip kept by latitude with theory ticks")
beat("b14", ch, "hemispin", {"foot": "the spin a storm borrows changes sign at the line"},
     "The simulation shows one more thing. In the north the wind circles anticlockwise. South of the equator f is negative, and the same equations turn the wind the other way: clockwise. Every hurricane in the north turns one way and every cyclone in the south turns the other, because the spin they borrow changes sign at the equator.",
     "two spirals: anticlockwise north, clockwise south, the equator between")

ch = "4 · The closest storms"
beat("b15", ch, "table", {"head": "closest any storm came to the equator at tropical-storm strength · NOAA IBTrACS", "hdr": ["storm", "year", "closest", "wind"], "cols": [0, 420, 640, 960],
                         "rows": [[(x["name"].title() if x["name"] != "UNNAMED" else ("Agni" if x["season"] == 2004 else "unnamed")), x["season"], f"{abs(x['lat']):.1f}°{'N' if x['lat'] > 0 else 'S'}", f"{x['wind_kt']:.0f} kt"] for x in cl[:6]], "hl": [0, 1],
                         "foot": "one point every 3 to 6 hours along each track"},
     f"So which storms came closest? Top of the list is Cyclone Agni, in the Arabian Sea in 2004, at {a_min[1]:.1f} degrees north. Then Typhoon Vamei, 2001, at {vam['lat']:.1f} degrees. A few others came within three degrees, on both sides. None of them crossed.",
     "table of the six closest storms")
beat("b16", ch, "agnitrack", {"foot": f"it only grew strong as it moved away from the equator"},
     f"Here is Agni's track from the US military's Joint Typhoon Warning Center. It drifted south and west until it was about {a_km} kilometres from the equator, with winds of {a_min[3]:.0f} knots. Then it turned north. And only as it moved away from the equator did it strengthen, to {a_max[3]:.0f} knots, hurricane strength, by about {a_max[1]:.0f} degrees north. India's weather service puts its birth a little further north, near one and a half degrees.",
     "Agni's track, coloured by wind; closest point marked", say=None)
beat("b17", ch, "quote", {"lines": ["…a combination of topography and meteorology,", "rather than Earth's rotation", "helped jump start the cyclone."], "hl": [1], "src": "NASA Earth Observatory, “A Rare Cyclone on the Equator” (2003), on Typhoon Vamei", "src_short": "NASA", "foot": "a monsoon surge squeezed between Malaysia and Borneo"},
     "Vamei is the other famous exception. According to NASA, a combination of topography and meteorology, rather than Earth's rotation, helped jump start it: a blast of monsoon air squeezed between Malaysia and Borneo gave it the spin the planet could not. The researchers put the odds of that happening again at about once every 100 to 400 years.",
     "NASA quote card")

ch = "5 · Why not across?"
beat("b18", ch, "fcurve", {"marks": [5, 0, -5], "head": "a storm drifting toward the equator: its source of spin shrinks to zero, then reverses"},
     "Now imagine a storm that does reach the line. Its spin came from the planet, and that supply shrinks to nothing as it approaches. One step further, and the planet pushes spin the other way. To survive, it would have to stop and spin up the other way, and near the equator there is almost nothing to spin up with.",
     "the f curve again, marks either side of zero")
beat("b19", ch, "statement", {"lines": ["There is no wall at the equator.", "There is just no spin to borrow,", "and storms drift away from it."], "accent": [1], "sub": "the drift has a name: beta drift"},
     "There is also a push. Because the planet's spin changes with latitude, a spinning storm tends to drift away from the equator on its own, toward the pole, an effect meteorologists call beta drift. So storms are nudged away from the line, and the few that wander close have no spin to keep going.",
     "statement")
beat("b20", ch, "trackmap", {"band": True, "head": "the same 8,457 storms · the band within 5 degrees of the equator"},
     f"Which is exactly the picture we started with: storms on both sides, and a thin empty band in the middle that none of the {c['storms']:,} has crossed.",
     "the full map again with the band")

ch = "6 · Where and when"
BA = D["basins"]; BB = BA["by_basin_all"]; MN = BA["by_month_sat"]
mon = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
pk = lambda L: sorted(range(12), key=lambda i: -L[i])[:2]
nN, nS = sorted(pk(MN["N"])), sorted(pk(MN["S"]))
bas = [("WP", "western Pacific", 1), ("NA", "North Atlantic", 1), ("SI", "south Indian", 0), ("EP", "eastern Pacific", 1), ("SP", "south Pacific", 0), ("NI", "north Indian", 1), ("SA", "South Atlantic", 0)]
beat("b20a", ch, "hbars", {"head": "storms that reached tropical-storm strength, by the ocean basin where they did · NOAA IBTrACS, 1851 to 2026",
                          "rows": [{"label": nm, "value": BB.get(k, 0), "txt": f"{BB.get(k, 0):,}", "col": "#1f6f8b" if north else "#d9552c"} for k, nm, north in bas],
                          "max": 2600, "lh": 92, "step": 0.08, "foot": "blue: north of the equator · red: south"},
     f"Here is where those storms form, counted basin by basin. The western Pacific has {BB['WP']:,}. The North Atlantic, {BB['NA']:,}. The south Indian Ocean, {BB['SI']:,}. The eastern Pacific, {BB['EP']:,}. The south Pacific, {BB['SP']:,}, and the north Indian Ocean, {BB['NI']:,}. And the South Atlantic: {BB.get('SA', 0)}.",
     "bars of storm counts by basin")
beat("b20b", ch, "ec02_months", {},
     f"Since 1980, the era of routine satellite coverage, {round(BA['north_share_sat'] * 100)} percent of storms formed north of the equator. And look at when. North of the line, the busiest months are {mon[nN[0]]} and {mon[nN[1]]}. South of it, {mon[nS[0]]} and {mon[nS[1]]}. Each hemisphere has its storm season in its own summer, so the equator is also the line where the storm calendar flips by six months.",
     "monthly counts, north and south")
beat("b20c", ch, "quote", {"lines": ["The National Hurricane Center in Miami estimated the storm", "was a category I hurricane (named Catarina), making it", "the first hurricane in the South Atlantic in the satellite record."], "hl": [2], "src": "NASA Earth Observatory, “A Rare Tropical Storm in the South Atlantic” (2024)", "src_short": "NASA", "foot": "the archive marks two later South Atlantic systems, 2010 and 2011, as disturbances"},
     "That single South Atlantic storm is Catarina, which struck southern Brazil in March 2004. NASA calls it the first hurricane in the South Atlantic in the satellite record. The archive holds two later South Atlantic systems, from 2010 and 2011, that reached 45 knots, but it labels them as disturbances, so my count leaves them out, and NASA describes a few more weak storms there since. Either way, the South Atlantic is one of the quietest oceans for storms on the planet.",
     "NASA quote card")

ch = "Limits"
beat("b21", ch, "bullets", {"head": "Limits", "numbered": True, "items": ["The simulation is dry air with no thunderstorms", "Real storms also need warm sea and still air above", f"The record is thin before satellites: 'never' means never recorded"]},
     "The limits. My simulation is a layer of dry air. It has no thunderstorms, no warm sea, no winds that tear storms apart, all things real hurricanes depend on. It shows only the one ingredient that vanishes at the equator. And the archive is thin before weather satellites, in the 1960s, so never means never recorded.",
     "numbered limits")
beat("b22", "Three things", "bullets", {"head": "Three things", "numbered": True, "items": ["A hurricane's spin is borrowed from the planet", "At the equator the planet lends none", f"Of {c['systems']:,} recorded storm systems, none crossed"]},
     f"Three things. A hurricane's spin is borrowed from the planet. At the equator, the planet lends none, which is why storms almost never form there. And of {c['systems']:,} storm systems on record, not one has crossed.",
     "numbered summary")
beat("b23", "", "endcard", {"next_label": "Next on Earth Worked Out", "next": ["Why hail can grow bigger", "than a baseball"]},
     "This is Earth Worked Out: real physics, run on screen. The storm analysis and the simulation code are linked below. Next time: why hail can grow bigger than a baseball.",
     "end card with space for YouTube end-screen elements")

sb = {"episode": "ec02", "title": "Why Hurricanes Never Cross the Equator", "voice": "am_michael", "lang": "en-us", "speed": 0.95, "gap": 0.6, "tail": 11, "beats": B}
(H / "storyboard.json").write_text(json.dumps(sb, indent=1, ensure_ascii=False))
print(len(B), "beats", sum(len(b["text"].split()) for b in B), "words")
