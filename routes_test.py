import math
import datetime
from datetime import timedelta
import json
import requests
from googlemaps import convert
from numpy import arctan2,random,sin,cos,degrees

with open("api_key.json") as api:
    authent = json.load(api)
api_key = str(authent["api_key"])

routes_url = "https://routes.googleapis.com/directions/v2:computeRoutes/json?"

starting_point = "5795 W Canyon Dr, Littleton, CO 80128"
end_point = "6201 S Pierce St, Littleton, CO 80123"

arrival_time = input("Input your desired arrival time in YYYY-MM-DD-HH-MM-SS format: ")
year, month, day, hour, minute, second = map(int, arrival_time.split('-'))
time_arrival = datetime.datetime(year, month, day, hour, minute, second)

waypoints = [(39.60971159889172, -105.09142031890865), 
             (39.59517540890404, -105.09139250489149),
             (39.58063011413268, -105.08706490264349)]

parameters_directions = {"origin": starting_point,
                        "destination": end_point,  
                        "arrivalTime": convert.time(time_arrival),
                        "key": api_key}
response_directions = requests.get(routes_url, params=parameters_directions)
print(response_directions)
json_directions = (response_directions.json())
final_directions = json.dumps(json_directions, indent = 4)
print(final_directions)
