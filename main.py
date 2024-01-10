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


###DISTANCE MATRIX
parameters = {"origins": convert.location_list(origin), "destinations": convert.location_list(destination), "departure_time": 1704115851, "key": api_key}
response = requests.get(url_distance, params=parameters)
jsonapi =(response.json())
final = json.dumps(jsonapi, indent = 4)
light_to_light = (jsonapi["rows"][0]["elements"][0]["duration"]["value"])


### Determine Cardinal Degree of Direction1
destination_x =   39.6047322 
origin_x = 39.6044273 
destination_y = -105.0737276
origin_y = -105.0725764

cardinal_degree = (math.degrees(math.atan2(((destination_y)-(origin_y)),((destination_x)-(origin_x)))))
if cardinal_degree < 0:
    cardinal_degree = cardinal_degree + 360
    print(cardinal_degree)
else:
    print(cardinal_degree)

if 337.5 <= cardinal_degree <= 360:
    cdirection = "North"
    print(cdirection)
if 0 <= cardinal_degree < 22.5:
    cdirection = "North"
    print(cdirection)
if 22.5 <= cardinal_degree < 67.5:
    cdirection = "North-East"
    print(cdirection)
if 67.5 <= cardinal_degree < 112.5:
    cdirection = "East"
    print(cdirection)
if 112.5 <= cardinal_degree < 157.5:
    cdirection = "South-East"
    print(cdirection)
if 157.5 <= cardinal_degree < 202.5:
    cdirection = "South"
    print(cdirection)
if 202.5 <= cardinal_degree < 247.5:
    cdirection = "South-West"
    print(cdirection)
if 247.5 <= cardinal_degree < 292.5:
    cdirection = "West"
    print(cdirection)
if 292.5 <= cardinal_degree < 337.5:
    cdirection = "North-West"
    print(cdirection)




## use json file to format time when light turns greem
## convert time into datetime
testing = (data["intersections"][0]["directions"]["north"]["start_time"])
green_turn = str(testing)
year, month, day, hour, minute, second = map(int, green_turn.split('-'))
green_time = datetime.datetime(year, month, day, hour, minute, second)


## user input desired arrival time
## convert time into datetime

light_time = (time_arrival) - datetime.timedelta(seconds = light_to_light)

## subtract the arrival time from the turn time
between_time = (light_time) - (green_time)

## convert time inbetween to seconds
totaltime = timedelta.total_seconds(between_time)

## how long the light is red/green for
greentime = (data["intersections"][1]["directions"]["north"]["green_time"])
redtime = (data["intersections"][1]["directions"]["north"]["red_time"])


## the amount of time inbetween the time when the light turned green and the arrival at the light

## how many seconds the light takes to run one cycle
cycletime = greentime + redtime

## the number of cycles the light completes in the time between 
## when the light turned green and the arrival at the light
rawnum = totaltime / cycletime

## the number of complete cycles that can be run in that time
truncated_value = math.floor(rawnum)

## the decimal of the number of incomplete cycles that can be run in that time
leftover = rawnum - truncated_value

## the number of seconds into the new cycle the light is
partialcycle = leftover * cycletime

## determines if light is red or green and tells user how much longer the light will be red or green for
if partialcycle <= greentime:
    timetochange = round(greentime - partialcycle, 3)
    print( "The light will be GREEN for", timetochange, "more seconds.")
else:
    timeinred = partialcycle - greentime
    redleft = round(redtime - timeinred, 3)
    print("The light will be RED for", redleft, "more seconds.")

