import datetime
from datetime import timedelta
import math
import json
import requests
from googlemaps import convert

with open("api_key.json") as api:
    authent = json.load(api)
api_key = str(authent["api_key"])

with open("intervals.json") as interval_data:
    data = json.load(interval_data)

starting_point = input("Enter the address of the starting location:\n")
end_point = input("Enter the address of your destination:\n")

arrival_time = input("Input your desired arrival time in YYYY-MM-DD-HH-MM-SS format: ")
year, month, day, hour, minute, second = map(int, arrival_time.split('-'))
time_arrival = datetime.datetime(year, month, day, hour, minute, second)


url_distance = "https://maps.googleapis.com/maps/api/distancematrix/json"
url_directions = "https://maps.googleapis.com/maps/api/directions/json"

olat = (data["intersections"][0]["lat"])
olng = (data["intersections"][0]["lng"])

dlat = (data["intersections"][1]["lat"])
dlng = (data["intersections"][1]["lng"])

origin = {"lat": olat, "lng": olng}
destination = {"lat":dlat, "lng": dlng}

###DIRECTIONS
parameters_directions = {"origin": starting_point, "destination": end_point,  "arrival_time": convert.time(time_arrival), "key": api_key}
response_directions = requests.get(url_directions, params=parameters_directions)
json_directions = (response_directions.json())
final_directions = json.dumps(json_directions, indent = 4)
print(final_directions)