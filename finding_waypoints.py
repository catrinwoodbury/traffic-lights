import json

with open ("intervals.json") as info:
    data = json.load(info)
    
waypoints = [latitudes["latlng"] for latitudes in data["intersections"]] 

print(waypoints)