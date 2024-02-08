import datetime
from math import sin, cos, sqrt, atan2, radians, degrees 
import json
import requests
from googlemaps import convert
from datetime import timedelta
import math

## radius of the earth in miles
Rad = 3959.87433
value = 0
wp = []
place_waypoints = []
dist =[]
green_count = 0
red_count = 0


## opens and grabs the api key
with open("api_key.json") as api:
    authent = json.load(api)
api_key = str(authent["api_key"])

## opens and parses the json intersection data
f = open('intervals.json', "r")
data = json.loads(f.read())
 
## start and end locations
starting_point = "9100 W Ken Caryl Ave, Littleton, CO 80128"
end_point = "5375 S Wadsworth Blvd, Lakewood, CO 80123"

## desired arrival time
arrival_time = input("Input your desired arrival time in YYYY-MM-DD-HH-MM-SS format: ")
year, month, day, hour, minute, second = map(int, arrival_time.split('-'))
time_arrival = datetime.datetime(year, month, day, hour, minute, second)

## base api urls
url_distance = "https://maps.googleapis.com/maps/api/distancematrix/json"
url_directions = "https://maps.googleapis.com/maps/api/directions/json"

## DIRECTIONS calculation for the entire route:
## parameters
parameters_directions = {"origin": starting_point,
                        "destination": end_point,  
                        "arrival_time": convert.time(time_arrival), 
                        "key": api_key}
response_directions = requests.get(url_directions, params=parameters_directions)
json_directions = (response_directions.json())
final_directions = json.dumps(json_directions, indent = 4)

## gets the polyline and decodes it from the entire route
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
        ## breaks lat long coords down 
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
        ## if the distance is less than or equal to 500 feet
        ## add the lat long coords to the waypoints list
        if final <= 500:
            wp.append(result)
            waypoints = list(set(wp))
sorting = sorted(range(len(waypoints)), key=lambda k: waypoints[k])
print(sorting)
testing = [waypoints[i] for i in sorting]
print(testing)

## gets the lat long coords of the start location
start_loc = (convert.normalize_lat_lng(json_directions["routes"][0]["legs"][0]["start_location"]))
## add the start location to the waypoints
wp.append(start_loc)

## gets the lat long coords of the end location
end_loc = (convert.normalize_lat_lng(json_directions["routes"][0]["legs"][0]["end_location"]))
## add the end location to the waypoints
wp.append(end_loc)

## make the waypoints list into a list
waypoints = list(set(wp))

## breaks the start location into lat longs
lat_2 = radians(float(start_loc[0]))
long_2 = radians(float(start_loc[1]))

## for each value in the waypoints list
for s in waypoints: 
    ## convert to form
    convert_wp = convert.normalize_lat_lng(s)
    lat1 = radians(convert_wp[0])
    long1 = radians(convert_wp[1])
    dlon = long_2 - long1
    dlat = lat_2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat_2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = Rad * c
    ## convert to feet
    final = distance * 5280
    ## add the distance from start to the list
    dist.append(final)
    ## sort the list based on which point is the closest to the start
sort = sorted(range(len(dist)), key=lambda k: dist[k])

## re-sort the original lat long list based on which waypoints are closest to the start
wp = [waypoints[i] for i in sort]

## final_value gives the index of the final value in the list
## subtracted by 2 because the end point from the last light to the end location will not have a light
final_value = len(wp) - 2

while final_value:
    final_point = convert.latlng(wp[final_value])
    light_point = convert.latlng(wp[final_value - 1])
    ## calc distance between end point and the lights
    parameters_distance1 = {"origins": light_point,
                        "destinations": final_point,  
                        "arrival_time": convert.time(time_arrival), 
                        "key": api_key}
    response_directions = requests.get(url_distance, params=parameters_distance1)
    json_directions = (response_directions.json())
    final_directions = json.dumps(json_directions, indent = 4)
    duration = (json_directions["rows"][0]["elements"][0]["duration"]["value"])
    ## format the time inbetween in datetime format
    time = datetime.timedelta(seconds = duration)
    ## update the running time by subtracting the arrival time from the inbetween time
    time_arrival = time_arrival - time
    ## get lat long values to calc cardinal directions
    cardinal_end_lat = (wp[final_value][0])
    cardinal_end_long = (wp[final_value][1])
    cardinal_start_lat = (wp[final_value - 1][0])
    cardinal_start_long = (wp[final_value -1][1])
    dL = (cardinal_end_long)-(cardinal_start_long)
    X = cos(cardinal_end_lat)* sin(dL)
    Y = cos(cardinal_start_lat)*sin(cardinal_end_lat) - sin(cardinal_start_lat)*cos(cardinal_end_lat)* cos(dL)
    bearing = atan2(X,Y)
    result = ((degrees(bearing) + 360) % 360)
    light = (sorting[value])
    ## locate which direction for the intersection in the data
    locations  = (data["intersections"][light]["name"])
    print("Location: ", locations)

    if 337.5 <= result <= 360:
        status = "north"
        print(status)
        testing = (data["intersections"][light]["directions"][status]["start_time"])
        green_turn = str(testing)
        year, month, day, hour, minute, second = map(int, green_turn.split('-'))
        green_time = datetime.datetime(year, month, day, hour, minute, second)
        light_time = (time_arrival) - (time)
        ## subtract the arrival time from the turn time
        between_time = (light_time) - (green_time)
        ## convert time inbetween to seconds
        totaltime = timedelta.total_seconds(between_time)
        ## how long the light is red/green for
        greentime = (data["intersections"][light]["directions"][status]["green_time"])
        redtime = (data["intersections"][light]["directions"][status]["red_time"])
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
            green_count = green_count + 1
            print( "The light will be GREEN for", timetochange, "more seconds.")
        else:
            timeinred = partialcycle - greentime
            redleft = round(redtime - timeinred, 3)
            red_count = red_count + 1
            print("The light will be RED for", redleft, "more seconds.")
            light_time = light_time - datetime.timedelta(seconds = redleft)
    if 0 <= result < 22.5:
        status = "north"
        print(status)
        testing = (data["intersections"][light]["directions"][status]["start_time"])
        green_turn = str(testing)
        year, month, day, hour, minute, second = map(int, green_turn.split('-'))
        green_time = datetime.datetime(year, month, day, hour, minute, second)
        light_time = (time_arrival) - (time)
        ## subtract the arrival time from the turn time
        between_time = (light_time) - (green_time)
        ## convert time inbetween to seconds
        totaltime = timedelta.total_seconds(between_time)
        ## how long the light is red/green for
        greentime = (data["intersections"][light]["directions"][status]["green_time"])
        redtime = (data["intersections"][light]["directions"][status]["red_time"])
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
            green_count = green_count + 1
            print( "The light will be GREEN for", timetochange, "more seconds.")
        else:
            timeinred = partialcycle - greentime
            redleft = round(redtime - timeinred, 3)
            red_count = red_count + 1
            print("The light will be RED for", redleft, "more seconds.")
            light_time = light_time - datetime.timedelta(seconds = redleft)
    if 22.5 <= result < 67.5:
        print("North-East")
    if 67.5 <= result < 112.5:
        status = "east"
        print(status)
        testing = (data["intersections"][light]["directions"][status]["start_time"])
        green_turn = str(testing)
        year, month, day, hour, minute, second = map(int, green_turn.split('-'))
        green_time = datetime.datetime(year, month, day, hour, minute, second)
        light_time = (time_arrival) - (time)
        ## subtract the arrival time from the turn time
        between_time = (light_time) - (green_time)
        ## convert time inbetween to seconds
        totaltime = timedelta.total_seconds(between_time)
        ## how long the light is red/green for
        greentime = (data["intersections"][light]["directions"][status]["green_time"])
        redtime = (data["intersections"][light]["directions"][status]["red_time"])
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
            green_count = green_count + 1
            print( "The light will be GREEN for", timetochange, "more seconds.")
        else:
            timeinred = partialcycle - greentime
            redleft = round(redtime - timeinred, 3)
            red_count = red_count + 1
            print("The light will be RED for", redleft, "more seconds.")
            light_time = light_time - datetime.timedelta(seconds = redleft)
    if 112.5 <= result < 157.5:
        print("South-East")
    if 157.5 <= result < 202.5:
        status = "south"
        print(status)
        testing = (data["intersections"][light]["directions"][status]["start_time"])
        green_turn = str(testing)
        year, month, day, hour, minute, second = map(int, green_turn.split('-'))
        green_time = datetime.datetime(year, month, day, hour, minute, second)
        light_time = (time_arrival) - (time)
        ## subtract the arrival time from the turn time
        between_time = (light_time) - (green_time)
        ## convert time inbetween to seconds
        totaltime = timedelta.total_seconds(between_time)
        ## how long the light is red/green for
        greentime = (data["intersections"][light]["directions"][status]["green_time"])
        redtime = (data["intersections"][light]["directions"][status]["red_time"])
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
            green_count = green_count + 1
            print( "The light will be GREEN for", timetochange, "more seconds.")
        else:
            timeinred = partialcycle - greentime
            redleft = round(redtime - timeinred, 3)
            red_count = red_count + 1
            print("The light will be RED for", redleft, "more seconds.")
            light_time = light_time - datetime.timedelta(seconds = redleft)
    if 202.5 <= result < 247.5:
        print("South-West")
    if 247.5 <= result < 292.5:
        status = "west"
        print(status)
        testing = (data["intersections"][light]["directions"][status]["start_time"])
        green_turn = str(testing)
        year, month, day, hour, minute, second = map(int, green_turn.split('-'))
        green_time = datetime.datetime(year, month, day, hour, minute, second)
        light_time = (time_arrival) - (time)
        ## subtract the arrival time from the turn time
        between_time = (light_time) - (green_time)
        ## convert time inbetween to seconds
        totaltime = timedelta.total_seconds(between_time)
        ## how long the light is red/green for
        greentime = (data["intersections"][light]["directions"][status]["green_time"])
        redtime = (data["intersections"][light]["directions"][status]["red_time"])
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
            green_count = green_count + 1
            print( "The light will be GREEN for", timetochange, "more seconds.")
        else:
            timeinred = partialcycle - greentime
            redleft = round(redtime - timeinred, 3)
            red_count = red_count + 1
            print("The light will be RED for", redleft, "more seconds.")
            light_time = light_time - datetime.timedelta(seconds = redleft)
    if 292.5 <= result < 337.5:
        print("North-West")
    ## use json file to format time when light turns greem
    ## convert time into datetime
    final_value -= 1
    value = value + 1
    if final_value == 0:
        break

print("Departure time: ", light_time)
print("You will hit ", green_count, "green lights")
print("You will hit ",  red_count, "red lights")
