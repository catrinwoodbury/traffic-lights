import json

with open ("intervals.json") as info:
    data = json.load(info)
    
lats_lngs = [latlng["lat,lng"] for latlng in data["intersections"]]

for i in data["intersections"]:
    ## calculate distance from polyline (polyline for distance between origin and destination) 
    ## if the distance is less than (a value) add to waypoints array
    print(lats_lngs)