import json
import googlemaps
from googlemaps import convert

with open("intervals.json") as interval_data:
    data = json.load(interval_data)

coords = (data["intersections"][0]["lat,lng"])

def convert(file):
    return tuple(file)

print(convert(coords))
#print(poly)



