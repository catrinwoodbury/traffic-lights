import math
import datetime
from datetime import timedelta
import json
import requests
from googlemaps import convert
from numpy import arctan2,random,sin,cos,degrees

destination_x =   39.6047322 
origin_y = -105.0725764
origin_x = 39.6044273 
destination_y = -105.0737276
    
with open("api_key.json") as api:
    authent = json.load(api)
api_key = str(authent["api_key"])

with open("intervals.json") as interval_data:
    data = json.load(interval_data)

#starting_point = input("Enter the address of the starting location:\n")
#end_point = input("Enter the address of your destination:\n")
starting_point = "5795 W Canyon Dr, Littleton, CO 80128"
end_point = "6201 S Pierce St, Littleton, CO 80123"

arrival_time = input("Input your desired arrival time in YYYY-MM-DD-HH-MM-SS format: ")
year, month, day, hour, minute, second = map(int, arrival_time.split('-'))
time_arrival = datetime.datetime(year, month, day, hour, minute, second)


url_distance = "https://maps.googleapis.com/maps/api/distancematrix/json"
url_directions = "https://maps.googleapis.com/maps/api/directions/json"



###DIRECTIONS
parameters_directions = {"origin": starting_point, "destination": end_point,  "arrival_time": convert.time(time_arrival), "key": api_key}
response_directions = requests.get(url_directions, params=parameters_directions)
json_directions = (response_directions.json())
final_directions = json.dumps(json_directions, indent = 4)
#print(final_directions)

i = 1
end_lat = (json_directions["routes"][0]["legs"][0]["steps"][(i+1)]["end_location"]["lat"])  
print("end lat:", end_lat)               
end_lng = (json_directions["routes"][0]["legs"][0]["steps"][(i+1)]["end_location"]["lng"])
print("end lng:", end_lng)
start_lat = (json_directions["routes"][0]["legs"][0]["steps"][i]["start_location"]["lat"])
print("start lat:", start_lat)
start_lng = (json_directions["routes"][0]["legs"][0]["steps"][i]["start_location"]["lng"])     
print("start lng:", start_lng)


    
dL = (end_lng)-(start_lng)
X = cos(end_lat)* sin(dL)
Y = cos(start_lat)*sin(end_lat) - sin(start_lat)*cos(end_lat)* cos(dL)
bearing = arctan2(X,Y)
result = ((degrees(bearing) + 360) % 360)

print(result)

if 337.5 <= result <= 360:
    print("North")
if 0 <= result < 22.5:
    print("North")
if 22.5 <= result < 67.5:
    print("North-East")
if 67.5 <= result < 112.5:
    print("East")
if 112.5 <= result < 157.5:
    print("South-East")
if 157.5 <= result < 202.5:
    print("South")
if 202.5 <= result < 247.5:
    print("South-West")
if 247.5 <= result < 292.5:
    print("West")
if 292.5 <= result < 337.5:
    print("North-West")




