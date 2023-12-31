import requests
import json
from googlemaps import convert

with open("api_key.json") as api:
    data = json.load(api)
api_key = str(data["api_key"])


url = "https://maps.googleapis.com/maps/api/distancematrix/json"
#origin = input("Where will you begin your drive?\n")
#destination = input("Where will you end your drive?\n")
origin = {"lat":39.580704, "lng": -105.087087}
destination = {"lat":39.609722, "lng": -105.091334}

parameters = {"origins": convert.location_list(origin), "destinations": convert.location_list(destination), "departure_time": 1704115851, "key": api_key}


response = requests.get(url, params=parameters)

jsonapi =(response.json())

final = json.dumps(jsonapi, indent = 4)

duration = (jsonapi["rows"][0]["elements"][0]["duration"]["text"])

print(final)