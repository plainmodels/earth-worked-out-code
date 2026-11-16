"""Write ec01/storyboard.json. Numbers come from data.json (the simulation), so a re-run updates the narration."""
import json, pathlib
H = pathlib.Path(__file__).resolve().parent; D = json.loads((H / "data.json").read_text())
P = {p["who"]: p for p in D["people"]}; walk, jog, run, sprint, bolt = (D["people"][i] for i in range(5))
def ms(s): m, s = divmod(int(s), 60); return (f"{m} minute{'s' if m != 1 else ''} and {s} seconds" if m else f"{s} seconds")
def first(m): return next(s for s, d in D["front"] if d >= m)
inland, runup = int(D["max_inland_m"]), D["max_runup_m"]
v500 = 500 / first(500) * 3.6; t1k = first(1000)
deep, near = D["speeds"][0], D["speeds"][-1]; hts = D["heights"]
sh = D["shoreline_trough"]; mn = min(sh, key=lambda v: v[1]); back = round(-mn[1]); start_back = next(v[0] for v in sh if v[1] < -20)
land_back = next(v[0] for v in sh if v[1] > 0 and v[0] > mn[0]); warn = round((land_back - start_back) / 60)
travel = round(D["landfall_s"] / 60)
B = []
def beat(id, chapter, scene, p, text, visual, say=None, sfx=None):
    b = {"id": id, "chapter": chapter, "scene": scene, "p": p, "text": text, "visual": visual}
    if say: b["say"] = say
    if sfx: b["sfx"] = sfx
    B.append(b)

beat("b01", "", "racestrip", {"who": [1, 2, 4], "metres": 400, "speedup": 2},
     f"The water has just reached the beach. You are standing at the edge of it, and you start running. How fast do you have to be? I built a simulation of the ocean, the shore and the land to find out. A jogger is overtaken almost at once. So is someone running hard. Only one runner here stays ahead, and he is running at the top speed of Usain Bolt.",
     "top-down race from the simulation", sfx=[[0.7, "hit"]])
beat("b02", "", "statement", {"lines": ["Once the water is on the beach,", "the race is already lost.", "The real race starts earlier."], "accent": [2]},
     "Once the water is on the beach, the race is already lost. The real race starts much earlier, and in this video we will find out where. Every number comes from a simulation I wrote and ran, and you can run it yourself.",
     "the thesis")
beat("b03", "", "title", {"title": ["How fast would you need", "to run from a tsunami?"], "sub": "a simulation of the ocean, the shore and the land"},
     "How fast would you need to run to escape a tsunami?", "title card", sfx=[[0.1, "hit"]])
beat("b04", "In this video", "bullets", {"head": "We will find out", "items": ["Why a tsunami crosses the ocean at the speed of a jet", "Why it grows taller as it slows down", "The race: you against the water, metre by metre", "Where your head start really comes from"]},
     "We will find out why a tsunami crosses the ocean at the speed of a jet, why it grows taller as it slows down, how the race between you and the water actually goes, metre by metre, and where your head start really comes from.",
     "what this video covers")

ch = "1 · The model"
beat("b05", ch, "seaprofile", {"snap": 0, "head": "the model's ocean, 230 km across · seabed to scale · wave height exaggerated 40×"},
     "First, the model. This is a slice through an ocean, two hundred and thirty kilometres from the open sea to dry land. The deep ocean is four kilometres deep. Then the continental slope climbs to a shelf about a hundred metres deep, the shelf runs for sixty kilometres, and a gentle beach rises onto land. It is idealised, not a real coast, but every part of it is typical of real ones.",
     "the ocean profile")
beat("b06", ch, "equation", {"label": "the equations the simulation solves", "eq": "water in = water out", "where": ["plus: push from the slope of the water surface", "minus: friction with the seabed and the ground"], "foot": "the same rules from the deep ocean to dry land"},
     "The simulation solves the shallow-water equations. They sound complicated, but they say something simple: water is never created or destroyed, and it is pushed by the slope of its own surface, while the seabed drags on it. The same rules work over four kilometres of water, over a beach, and over land that is dry until the wave arrives.",
     "the model in words")

ch = "2 · Jet speed"
beat("b07", ch, "seaprofile", {"from": 0.0, "to": 0.95},
     f"Into this ocean I put a single wave: a crest two metres high and about a hundred kilometres long. That is a big tsunami, but in the deep ocean it is barely a bump: two metres of height spread over a hundred kilometres. Watch how fast it goes. It covers the deep ocean in minutes, and then it runs into the slope.",
     "the wave crossing the ocean", sfx=[[0.3, "tick"]])
beat("b08", ch, "speedbars", {},
     f"Here is what the simulation measured. Over four kilometres of water, the crest moved at {deep['sim_kmh']} kilometres an hour. That is airliner speed. Over the shelf it slowed to about a hundred, and in the last twenty metres of water, to {near['sim_kmh']} kilometres an hour. The black ticks are a one-line formula: the square root of gravity times the depth. The simulation and the formula agree.",
     "speed against depth")
beat("b09", ch, "quote", {"lines": ["The speed of tsunami waves depends on ocean depth", "rather than the distance from the source of the wave."], "hl": [0], "src": "NOAA National Ocean Service, “What is a tsunami?”", "src_short": "NOAA", "foot": "deep water: as fast as a jet plane"},
     "This is not a quirk of my model. NOAA, the United States ocean agency, puts it plainly: the speed of a tsunami depends on the depth of the ocean, not on how far it has come. Over deep water, it says, a tsunami can travel as fast as a jet plane.",
     "NOAA on tsunami speed")

ch = "3 · Slower, taller"
beat("b10", ch, "shoal", {"foot": f"from {hts[0]['m']:.0f} m in the deep ocean to {hts[-1]['m']} m at the beach"},
     f"And as the wave slows, it grows. The same water that was two metres high in the deep ocean was {hts[2]['m']} metres high at the edge of the shelf, and {hts[-1]['m']} metres at the beach. The energy that was spread through four kilometres of water is squeezed into a few metres, and the back of the wave, still in deeper water and still moving faster, catches up with the front.",
     "height against place")
beat("b11", ch, "shore", {"t0": 2900, "t1": 3330, "head": "the last 10 km of sea and the first 2.5 km of land · heights exaggerated 50×"},
     "Here is the last ten kilometres, closer up. The wave arrives as a rising wall of water, much steeper than it was at sea. And it does not stop at the shoreline. Unlike an ordinary wave, which breaks and slides back, a tsunami is a hundred kilometres long. There is so much water behind the front that it simply keeps coming, onto the land.",
     "the wave reaching the coast")

ch = "4 · On land"
beat("b12", ch, "shore", {"t0": 3080, "t1": 3520, "mark": True, "head": "the flood on land, second by second · heights exaggerated 50×"},
     f"On land, the front of the water moved at about {round(v500)} kilometres an hour over the first five hundred metres. It reached a kilometre inland in {ms(t1k)}. It slowed as it climbed, and stopped {inland:,} metres from the shoreline, at a height of {runup} metres above sea level.",
     "the flood running inland", sfx=[[0.4, "hit"]])
beat("b13", ch, "statement", {"lines": [f"{round(v500)} km/h over the first 500 m.", f"{inland:,} m inland.", f"{runup} m above sea level."], "accent": [0]},
     f"That first number matters most. {round(v500)} kilometres an hour is faster than most people can run at all, and it is the speed of the water at exactly the moment you would start running.",
     "the three numbers")

ch = "5 · The race"
beat("b14", ch, "racechart", {"who": [0, 1, 2, 4], "tmax": 300},
     f"So, the race. Here is the water's front, metre by metre, against time. And here are four people who start running from the water's edge the moment it arrives: someone walking briskly, someone jogging, someone running hard, and someone running at Usain Bolt's top speed. The walker, the jogger and the hard runner are all overtaken within a second or two. Only the Bolt line stays above the water.",
     "the race chart")
beat("b15", ch, "racestrip", {"who": [1, 2, 3], "start": 100, "metres": 600, "speedup": 3, "head": "the same race, but you start 100 m up the beach · from the simulation"},
     f"Give yourself a hundred metres. You are up the beach when the water reaches the shoreline. Now the jogger is caught after {round(jog['from_100m']['caught']['s'])} seconds. The hard runner lasts {round(run['from_100m']['caught']['s'])} seconds. Even a sprinter at twenty-five kilometres an hour is caught after about a minute, half a kilometre inland.",
     "a 100 metre start")
beat("b16", ch, "quote", {"lines": ["He could keep the maximum velocity", "in five 10 m sections (50–100 m)."], "hl": [0], "src": "Štuhec et al., Bioengineering (2023), analysis of Bolt's 9.58 s world record", "src_short": "the fastest human", "foot": "peak: 12.32 m/s, about 44 km/h, for about 50 metres"},
     "And that one runner who escapes? A detailed analysis of Usain Bolt's world record measured his top speed at twelve point three metres a second, about forty-four kilometres an hour, and found he held it for about fifty metres. The water here keeps going for more than a kilometre and a half. Nobody can outrun it from the beach.",
     "the limits of the fastest human")
beat("b17", ch, "headstart", {"foot": "the head start is the whole game"},
     f"So the real question is how much of a head start you need. Starting from the water's edge, to stay ahead of the water all the way to where it stops, a sprinter needs {sprint['from_0m']['head_start_needed_s']} seconds. A hard runner, {run['from_0m']['head_start_needed_s']}. A jogger, {ms(jog['from_0m']['head_start_needed_s'])}. Someone walking needs {ms(walk['from_0m']['head_start_needed_s'])}.",
     "head start needed")

ch = "6 · The head start"
beat("b18", ch, "drawback", {"foot": f"in this run the sea drew back for about {warn} minutes before the water returned"},
     f"Where does a head start come from? Sometimes the ocean gives you one. I ran the model again with a trough arriving first instead of a crest. Before the wave arrived, the sea drained away from the beach, {back} metres in this run, and it stayed out for about {warn} minutes before the water came back and flooded the land.",
     "the sea drawing back", sfx=[[0.6, "hit"]])
beat("b19", ch, "quote", {"lines": ["…drains away suddenly, showing the ocean floor", "like a very low tide… a tsunami is possible", "and could arrive within minutes."], "hl": [0, 2], "src": "US National Weather Service, “During a Tsunami”", "src_short": "official guidance", "foot": "natural warnings: a strong or long earthquake, the sea drawing back, a loud roar"},
     "That is one of the natural warnings the US National Weather Service lists. A strong or long earthquake, the ocean draining away and showing the sea floor, or a loud roar from the sea: any of these means a tsunami is possible and could arrive within minutes. Its advice is not to wait for an official warning.",
     "the official natural warnings")
beat("b20", ch, "statement", {"lines": [f"In this model the wave took {travel} minutes", "to cross 160 km of ocean.", "Near the source, there is far less time."], "accent": [2], "sub": "warning time depends on how far away the earthquake is"},
     f"The other head start is distance. In this model the wave took {travel} minutes to cross a hundred and sixty kilometres of ocean, and warning centres use that time to send alerts. But when the earthquake is close to the coast, the water can arrive in minutes, which is why the shaking itself is the warning.",
     "warning time")

ch = "7 · Up, not only away"
beat("b21", ch, "shore", {"t0": 3300, "t1": 3520, "mark": True, "head": "how high the water reached, compared with how far · heights exaggerated 50×"},
     f"One more thing the simulation shows. The water reached {inland:,} metres inland, but only {runup} metres up. On a gentle coast, going up can be much quicker than going away. The official advice says the same: go as high or as far inland as you can, and follow the evacuation signs.",
     "height versus distance")
beat("b22", ch, "quote", {"lines": ["The first wave may not be", "the last or the largest."], "hl": [0, 1], "src": "US National Weather Service, “During a Tsunami”", "src_short": "official guidance"},
     "And once you are safe, stay there. The Weather Service is blunt about it: the first wave may not be the last, or the largest, and the danger can last for hours.",
     "the first wave is not the last")
beat("b23", ch, "bullets", {"head": "Limits", "numbered": True, "items": ["One idealised coast, in one dimension", "One wave; real tsunamis are trains of waves", "Real bays, rivers and buildings change everything"]},
     "Limits. This is one idealised coast, simulated in one dimension, so it cannot show bays that focus the water, or rivers that carry it far inland. It uses one wave, where real tsunamis are a train of waves. And real towns, with buildings and debris, change how the water moves. The numbers show the shape of the problem, not a forecast for any real beach.",
     "limits")

ch = "Three things"
beat("b24", ch, "bullets", {"head": "Three things", "numbered": True, "items": [f"On land the water moves at about {round(v500)} km/h at first", "From the beach, you cannot outrun it", "Strong shaking or a vanishing sea: go up or inland, now"]},
     f"Three things. One: on land, the water moved at about {round(v500)} kilometres an hour at first, faster than nearly anyone can run. Two: from the beach, you cannot outrun it; the race is won or lost before the water arrives. Three: strong shaking, or a sea that suddenly drains away, means go up or inland, now, without waiting to be told.",
     "three points")
beat("b25", "", "endcard", {"next_label": "Next on Earth Worked Out", "next": ["Why hurricanes never", "cross the equator"]},
     "This is Earth Worked Out: real physics, run on screen. The simulation code is linked below. Next time: why hurricanes never cross the equator.",
     "end card with space for YouTube end-screen elements")

sb = {"episode": "ec01", "title": "How Fast Would You Need to Run to Escape a Tsunami?", "voice": "af_bella", "lang": "en-us", "speed": 0.95, "gap": 0.6, "tail": 11, "beats": B}
(H / "storyboard.json").write_text(json.dumps(sb, indent=1, ensure_ascii=False))
print(len(B), "beats", sum(len(b["text"].split()) for b in B), "words")
