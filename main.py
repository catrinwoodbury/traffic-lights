import datetime
import time
from datetime import timedelta
import math
import json

with open("intervals.json") as interval_data:
    data = json.load(interval_data)

## use json file to format time when light turns greem
## convert time into datetime
testing = (data["intersections"][0]["directions"]["north"]["start_time"])
green_turn = str(testing)
year, month, day, hour, minute, second = map(int, green_turn.split('-'))
green_time = datetime.datetime(year, month, day, hour, minute, second)
print(green_time)

## user input desired arrival time
## convert time into datetime

arrival_time = input("Input your desired arrival time in YYYY-MM-DD-HH-MM-SS format: ")
year, month, day, hour, minute, second = map(int, arrival_time.split('-'))
turn_time = datetime.datetime(year, month, day, hour, minute, second)
print(turn_time)

## subtract the arrival time from the turn time
between_time = (turn_time) - (green_time)
print(between_time)

## convert time inbetween to seconds
totaltime = timedelta.total_seconds(between_time)
print(totaltime)

## how long the light is red/green for
greentime = (data["intersections"][0]["directions"]["north"]["green_time"])
redtime = (data["intersections"][0]["directions"]["north"]["red_time"])


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

