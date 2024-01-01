import datetime
import time
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


url = "https://maps.googleapis.com/maps/api/distancematrix/json"

olat = (data["intersections"][0]["lat"])
olng = (data["intersections"][0]["lng"])

dlat = (data["intersections"][1]["lat"])
dlng = (data["intersections"][1]["lng"])

origin = {"lat": olat, "lng": olng}
destination = {"lat":dlat, "lng": dlng}

parameters = {"origins": convert.location_list(origin), "destinations": convert.location_list(destination), "departure_time": 1704115851, "key": api_key}

response = requests.get(url, params=parameters)

jsonapi =(response.json())

final = json.dumps(jsonapi, indent = 4)

light_to_light = (jsonapi["rows"][0]["elements"][0]["duration"]["value"])



## use json file to format time when light turns greem
## convert time into datetime
testing = (data["intersections"][0]["directions"]["north"]["start_time"])
green_turn = str(testing)
year, month, day, hour, minute, second = map(int, green_turn.split('-'))
green_time = datetime.datetime(year, month, day, hour, minute, second)


## user input desired arrival time
## convert time into datetime

arrival_time = input("Input your desired arrival time in YYYY-MM-DD-HH-MM-SS format: ")
year, month, day, hour, minute, second = map(int, arrival_time.split('-'))
turn_time = datetime.datetime(year, month, day, hour, minute, second)

light_time = (turn_time) - datetime.timedelta(seconds = light_to_light)

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

