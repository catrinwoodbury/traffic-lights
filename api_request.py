import requests
import json

with open("api_key.json") as api:
    data = json.load(api)

with open("intervals.json") as intervals:
    jsonfile = json.load(intervals)

## import api key
api_key = str(data["api_key"])

## import placeid's from intervals json file
destination = str(jsonfile["intersections"][2]["place_id"])

origin = str(jsonfile["intersections"][1]["place_id"])

url = "https://maps.googleapis.com/maps/api/distancematrix/json?" + "destinations=placeid:" + destination + "&origins=place_id:" + origin + "&key=" + api_key
## As is standard in URLs, all parameters are separated using the ampersand (&) character
response = requests.get(url)

jsonapi =(response.json())

final = json.dumps(jsonapi, indent = 4)

print(final)