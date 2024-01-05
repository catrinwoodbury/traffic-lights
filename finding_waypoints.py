import json

with open ("intervals.json") as info:
    data = json.load(info)
    
lats = [latitudes["lat"] for latitudes in data["intersections"]]
longs = [longitudes["lng"] for longitudes in data["intersections"]]

print(lats, longs)