import requests
import json
import googlemaps

with open("api_key.json") as api:
    data = json.load(api)
api_key = str(data["api_key"])
maps = googlemaps.Client(key = api_key)

#origin = input("Where will you begin your drive?\n")
#destination = input("Where will you end your drive?\n")
origin = "London"
destination = "40.6655101%2C-73.89188969999998"

distance = maps.directions(origin, destination)

mdistance = (distance[0]["legs"][0]["distance"]["text"])
duration = (distance[0]["legs"][0]["duration"]["text"])
print(mdistance)