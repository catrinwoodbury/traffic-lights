import datetime
from datetime import timedelta
import math
import json
import requests
from googlemaps import convert
from google.maps import routing

with open("api_key.json") as api: 
    authent = json.load(api)
api_key = str(authent["api_key"])

with open("intervals.json") as interval_data:
    data = json.load(interval_data)

waypoints = [(39.60971159889172, -105.09142031890865), 
             (39.58063011413268, -105.08706490264349), 
             (39.59517540890404, -105.09139250489149)]

starting_point = "4827 S Wadsworth Blvd, Littleton, CO 80123"
end_point = "7444 W Chatfield Ave Suite L, Littleton, CO 80128"

arrival_time = input("Input your desired arrival time in YYYY-MM-DD-HH-MM-SS format: ")
year, month, day, hour, minute, second = map(int, arrival_time.split('-'))
time_arrival = datetime.datetime(year, month, day, hour, minute, second)

url_distance = "https://maps.googleapis.com/maps/api/distancematrix/json"
url_directions = "https://maps.googleapis.com/maps/api/directions/json"

url_routes = "https://routes.googleapis.com/directions/v2:computeRoutes/json"

parameters_routes = {"origin": starting_point, 
                         "destination": end_point,  
                         "intermediates": "optimize:true|" + "via: true|" + convert.location_list(waypoints),
                         "arrivalTime": convert.time(time_arrival),
                         "key": api_key}
response_directions = requests.get(url_routes, params=parameters_routes)
json_directions = (response_directions.json())
final_directions = json.dumps(json_directions, indent = 4)
print(final_directions)
