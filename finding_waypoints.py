import json

with open ("intervals.json") as info:
    data = json.load(info)
    
lats_lngs = [latitudes["lat,lng"] for latitudes in data["intersections"]]


print(lats_lngs)