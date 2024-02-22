import datetime
from math import sin, cos, sqrt, atan2, radians, degrees 
import json
import requests
from googlemaps import convert
from datetime import timedelta
import math

## radius of the earth in miles
radius = 3959.87433
## open value
value = 0
## open list
wp = []
## open list
place_waypoints = []
## open list
distance =[]
## open value
green_count = 0
## open value
red_count = 0
string_list = []
## opens and grabs the api key
with open("api_key.json") as api:
    authent = json.load(api)
api_key = str(authent["api_key"])

## opens and parses the json intersection data
f = open('intervals.json', "r")
data = json.loads(f.read())
 
## start and end locations
starting_point = "6281 W Alder Ave, Littleton, CO 80128"
end_point = "7034 W Roxbury Pl, Littleton, CO 80128"

## desired arrival time
input_time = input("Input your desired arrival time in YYYY-MM-DD-HH-MM-SS format: ")
year, month, day, hour, minute, second = map(int, input_time.split('-'))
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
## gets the request
response_directions = requests.get(url_directions, params=parameters_directions)
## turns the request into json format
json_directions = (response_directions.json())
final_directions = json.dumps(json_directions, indent = 4)


## gets the polyline and turns it into lat longs for the entire route
poly_line = (json_directions["routes"][0]["overview_polyline"]["points"])
decode = convert.decode_polyline(poly_line)

## locates all lat long values in intersection data
coords = [cord["lat,lng"] for cord in data["intersections"]] 

## for each lat long value
for i in coords:
    ## turns the lat long into a tuple
    file = tuple(i)
    ## converts to google map lat long format
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
        distances = radius * c
        ## convert to feet
        final = distances * 5280
        print(final)
        ## if the distance is less than or equal to 500 feet
        ## add the lat long coords to the waypoints list
        if final <= 500:
            wp.append(result)
            waypoints = list(set(wp))

## creates a list of the original indexes of just the lights that are reordered based on the distance from the start location
sorting = sorted(range(len(waypoints)), key=lambda k: waypoints[k])
## creates a list of the lat longs of the lights ordered based on distance from the start location
ordered = [waypoints[i] for i in sorting]
print(ordered)

maneuver_list = [waypoints[i] for i in sorting]

full_list = [waypoints[i] for i in sorting]

steps = (json_directions["routes"][0]["legs"][0]["steps"])

for s in ordered:
    file = tuple(s)
    ## converts to google map lat long format
    result = convert.normalize_lat_lng(file)
    ## breaks tuple into specific lat long coords
    lat2 = radians(result[0])
    long2 = radians(result[1])
    # for each step in the directions
    for i in steps:
        lat1 = radians(i["start_location"]["lat"])
        long1 = radians(i["start_location"]["lng"])
        dlon = long2 - long1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distances = radius * c
        ## convert to feet
        final = distances * 5280
        print(final)
        if final <= 100:
            maneuver = (i["maneuver"])
            print(maneuver)           
            if maneuver == "turn-right":
                endlat = radians(i["end_location"]["lat"])
                endlng = radians(i["end_location"]["lng"])
                startlat = radians(i["start_location"]["lat"])
                startlng = radians(i["start_location"]["lng"])
                dL = (endlng)-(startlng)
                X = cos(endlat)* sin(dL)
                Y = cos(startlat)*sin(endlat) - sin(startlat)*cos(endlat)* cos(dL)
                bearing = atan2(X,Y)
                ## calculates the bearing inbetween the two lights
                result = ((degrees(bearing) - 90) % 360)
                ## add the bearing to the original list
                index = ordered.index(s)
                ordered[index] = result
                maneuver_list[index] = maneuver
                print(ordered)
            if maneuver == "turn-left":
                endlat = radians(i["end_location"]["lat"])
                endlng = radians(i["end_location"]["lng"])
                startlat = radians(i["start_location"]["lat"])
                startlng = radians(i["start_location"]["lng"])
                dL = (endlng)-(startlng)
                X = cos(endlat)* sin(dL)
                Y = cos(startlat)*sin(endlat) - sin(startlat)*cos(endlat)* cos(dL)
                bearing = atan2(X,Y)
                ## calculates the bearing inbetween the two lights
                result = ((degrees(bearing) + 90) % 360)
                ## add the bearing to the original list
                index = ordered.index(s)
                ordered[index] = result
                maneuver_list[index] = maneuver
                print(ordered)
for l in ordered:
    maneuver = "straight"
    index  = ordered.index(l)
    maneuver_list[index] = maneuver
    
    if type(l) == tuple:
        if index == 0:
            file = tuple(i)
            ## converts to google map lat long format
            result = convert.normalize_lat_lng(file)
            ## breaks tuple into specific lat long coords
            startlat = radians(json_directions["routes"][0]["legs"][0]["start_location"]["lat"])
            startlng = radians(json_directions["routes"][0]["legs"][0]["start_location"]["lng"])
            endlat = radians(result[0])
            endlng = radians(result[1])
            dL = (endlng)-(startlng)
            X = cos(endlat)* sin(dL)
            Y = cos(startlat)*sin(endlat) - sin(startlat)*cos(endlat)* cos(dL)
            bearing = atan2(X,Y)
            ## calculates the bearing inbetween the two lights
            result = ((degrees(bearing) + 90) % 360)
            ## add the bearing to the original list
            index = ordered.index(s)
            ordered[index] = result
        else:
            result = (ordered[index - 1])
            index = ordered.index(s)
            ordered[index] = result
    else:
        continue

print(ordered)
print(maneuver_list)