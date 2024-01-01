import requests
import json
from googlemaps import convert

with open("api_key.json") as api:
    authent = json.load(api)
api_key = str(authent["api_key"])

with open ("intervals.json") as info:
    data = json.load(info)

url = "https://maps.googleapis.com/maps/api/distancematrix/json"

olat = (data["intersections"][2]["lat"])
olng = (data["intersections"][2]["lng"])

dlat = (data["intersections"][1]["lat"])
dlng = (data["intersections"][1]["lng"])

origin = {"lat": olat, "lng": olng}
destination = {"lat":dlat, "lng": dlng}

parameters = {"origins": convert.location_list(origin), "destinations": convert.location_list(destination), "departure_time": 1704115851, "key": api_key}

response = requests.get(url, params=parameters)

jsonapi =(response.json())

final = json.dumps(jsonapi, indent = 4)

duration = (jsonapi["rows"][0]["elements"][0]["duration"]["text"])

print(duration)