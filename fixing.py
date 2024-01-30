import datetime
from math import sin, cos, sqrt, atan2, radians, acos
import json
import requests
from googlemaps import convert
from datetime import timedelta
import math

## radius of the earth in miles
wp = []
place_waypoints = []
Rad = 3959.87433
dist =[]
## opens and grabs the api key
with open("api_key.json") as api:
    authent = json.load(api)
api_key = str(authent["api_key"])

## opens and parses the json intersection data
f = open('intervals.json', "r")
data = json.loads(f.read())
 
## start and end locations

starting_point = "8126 S Wadsworth Blvd, Littleton, CO 80128"
end_point = "5375 S Wadsworth Blvd, Lakewood, CO 80123"
## desired arrival time
arrival_time = input("Input your desired arrival time in YYYY-MM-DD-HH-MM-SS format: ")
year, month, day, hour, minute, second = map(int, arrival_time.split('-'))
time_arrival = datetime.datetime(year, month, day, hour, minute, second)

## base api urls
url_distance = "https://maps.googleapis.com/maps/api/distancematrix/json"
url_directions = "https://maps.googleapis.com/maps/api/directions/json"

## DIRECTIONS calculation:
## parameters
parameters_directions = {"origin": starting_point,
                        "destination": end_point,  
                        "arrival_time": convert.time(time_arrival), 
                        "key": api_key}
response_directions = requests.get(url_directions, params=parameters_directions)
json_directions = (response_directions.json())
final_directions = json.dumps(json_directions, indent = 4)
print(final_directions)



## gets the polyline and decodes it from the final directions
poly_line = (json_directions["routes"][0]["overview_polyline"]["points"])
decode = convert.decode_polyline(poly_line)

## locates all lat long values in intersection data
coords = [cord["lat,lng"] for cord in data["intersections"]] 
## for each lat long value
for i in coords:
    file = tuple(i)
    result = convert.normalize_lat_lng(file)
    ## breaks tuple into specific lat long coords
    lat2 = radians(result[0])
    long2 = radians(result[1])

    ## for each lat long coord in the polyline
    for s in decode:
        end = convert.normalize_lat_lng(s)
        lat1 = radians(end[0])
        long1 = radians(end[1])
        ## calculates the distance between the intersection and polyline
        dlon = long2 - long1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = Rad * c
        ## convert to feet
        final = distance * 5280
        print(final)
        ## if the distance is less than or equal to 500 feet
        ## add the lat long coords to the waypoints list
        if final <= 500:
            wp.append(result)
            waypoints = list(set(wp))
print(waypoints)    


start_locat = convert.latlng(json_directions["routes"][0]["legs"][0]["start_location"])
location = start_locat.split()
print(location)

end_loc = convert.latlng(convert.normalize_lat_lng(json_directions["routes"][0]["legs"][0]["end_location"]))
wp.append(end_loc)
start_loc = convert.latlng(convert.normalize_lat_lng(json_directions["routes"][0]["legs"][0]["start_location"]))
wp.append(start_loc)
waypoints = list(set(wp))
print(waypoints)

lat_2 = radians(float(location[0]))
long_2 = radians(float(location[1]))

for s in waypoints: 
    end = convert.normalize_lat_lng(s)
    lat1 = radians(end[0])
    long1 = radians(end[1])
    dlon = long_2 - long1
    dlat = lat_2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat_2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = Rad * c
    ## convert to feet
    final = distance * 5280
    print(final)
    ## add the distance from start to the list
    dist.append(final)
    distances = list(set(dist))
    ## sort the list based on which point is the closest to the start
    print(distances)
sort = sorted(range(len(distances)), key=lambda k: distances[k])
print(sort)

wp = [waypoints[i] for i in sort]
print(wp)


final_value = len(wp) - 1

light_final = convert.latlng(wp[final_value])
print(light_final)

## calc distance between start point and light number 1
parameters_distance1 = {"origins": light_final,
                        "destinations": end_point,  
                        "arrival_time": convert.time(time_arrival), 
                        "key": api_key}
response_directions = requests.get(url_distance, params=parameters_distance1)
json_directions = (response_directions.json())
final_directions = json.dumps(json_directions, indent = 4)
time = (json_directions["rows"][0]["elements"][0]["duration"]["value"])
print(time)


## use json file to format time when light turns greem
## convert time into datetime
testing = (data["intersections"][0]["directions"]["north"]["start_time"])
green_turn = str(testing)
year, month, day, hour, minute, second = map(int, green_turn.split('-'))
green_time = datetime.datetime(year, month, day, hour, minute, second)

## user input desired arrival time
## convert time into datetime

light_time = (time_arrival) - datetime.timedelta(seconds = time)

## subtract the arrival time from the turn time
between_time = (light_time) - (green_time)

## convert time inbetween to seconds
totaltime = timedelta.total_seconds(between_time)

current_time = light_time

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
    current_time = light_time - datetime.timedelta(seconds = redleft)
    print(current_time)


list_value = final_value - 1

while list_value >= 0:
    light = convert.latlng(wp[list_value])
    origin = convert.latlng(wp[list_value + 1])
    parameters_distance1 = {"origins": origin,
                        "destinations": light,  
                        "arrival_time": convert.time(time_arrival), 
                        "key": api_key}
    response_directions = requests.get(url_distance, params=parameters_distance1)
    json_directions = (response_directions.json())
    final_directions = json.dumps(json_directions, indent = 4)
    time = datetime.timedelta(seconds = json_directions["rows"][0]["elements"][0]["duration"]["value"])
    print(time)
    current_time = current_time - time


    list_value -= 1

end_light = convert.latlng(wp[0])
parameters_distance2 = {"origins": end_light,
                        "destinations": end_point,  
                        "arrival_time": convert.time(time_arrival), 
                        "key": api_key}
response_directions2 = requests.get(url_distance, params=parameters_distance1)
json_directions2 = (response_directions.json())
final_directions2 = json.dumps(json_directions, indent = 4)
time2 = (json_directions["rows"][0]["elements"][0]["duration"]["value"])
print(time2)
