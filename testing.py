import datetime
from datetime import timedelta
import math
import json
import requests
from googlemaps import convert
import polyline

with open("api_key.json") as api:
    authent = json.load(api)
api_key = str(authent["api_key"])

with open("intervals.json") as interval_data:
    data = json.load(interval_data)

##starting_point = input("Enter the address of the starting location:\n")
##end_point = input("Enter the address of your destination:\n")

starting_point = "6201 S Pierce St, Littleton, CO 80123"
end_point = "5775 W Canyon Dr, Littleton, CO 80128"

arrival_time = input("Input your desired arrival time in YYYY-MM-DD-HH-MM-SS format: ")
year, month, day, hour, minute, second = map(int, arrival_time.split('-'))
#time_arrival = datetime.datetime(year, month, day, hour, minute, second)


url_distance = "https://maps.googleapis.com/maps/api/distancematrix/json"
url_directions = "https://maps.googleapis.com/maps/api/directions/json"

###DIRECTIONS
parameters_directions = {"origin": starting_point, "destination": end_point,  "arrival_time": convert.time(time_arrival), "key": api_key}
response_directions = requests.get(url_directions, params=parameters_directions)
json_directions = (response_directions.json())
final_directions = json.dumps(json_directions, indent = 4)
#print(final_directions)


poly_line = (json_directions["routes"][0]["overview_polyline"]["points"])
decode = convert.decode_polyline(poly_line)
#print(decode)

coords = (data["intersections"][0]["lat,lng"])

poly = convert.normalize_lat_lng(decode[0])
file = convert.latlng(coords)

file1 = str(file)
print(file1)
res = file1.split(', ')

#print(poly)
print(res)


