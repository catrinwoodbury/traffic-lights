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
waypoints = []
## open list
place_waypoints = []
original_index=[]
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
        end_lat = radians(end[0])
        end_lng = radians(end[1])
        ## calculates the distance between the intersection and polyline
        dlon = long2 - end_lng
        dlat = lat2 - end_lat
        a = sin(dlat / 2)**2 + cos(end_lat) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distances = radius * c
        ## convert to feet
        final = distances * 5280
        print(final)
        ## if the distance is less than or equal to 500 feet
        ## add the lat long coords to the waypoints list
        if final <= 500:
            indexes = coords.index(i)
            original_index.append(indexes)
            original_index = list(set(original_index))
## creates an unordered list of the lat longs of the waypoints
for i in original_index:
    waypoint = (coords[i])
    waypoint = tuple(waypoint)
    waypoints.append(waypoint)

start = (convert.normalize_lat_lng(json_directions["routes"][0]["legs"][0]["start_location"]))
start_lat = radians(float(start[0]))
start_lng = radians(float(start[1]))

for i in waypoints:
    end = convert.normalize_lat_lng(i)
    end_lat = radians(end[0])
    end_lng = radians(end[1])
    dlon = long2 - end_lng
    dlat = lat2 - end_lat
    a = sin(dlat / 2)**2 + cos(end_lat) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distances = radius * c
    ## convert to feet
    final = distances * 5280
    print(final)
    distance.append(final)

sort = sorted(range(len(distance)), key=lambda k: distance[k])
print("sort: ", sort)
## re-sort the original lat long list based on which waypoints are closest to the start
waypoints = [waypoints[i] for i in sort]
print("waypoints: ", type(waypoints[0]))

## sorts the original indexes based on which ones are closest to the start point
sorted_index = [original_index[i] for i in sort]
print(sorted_index)

bearing = [waypoints[i] for i in sort]

maneuver_list = [waypoints[i] for i in sort]

full_list = [waypoints[i] for i in sort]

steps = (json_directions["routes"][0]["legs"][0]["steps"])

for s in bearing:
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
                degree = atan2(X,Y)
                ## calculates the bearing inbetween the two lights
                result = ((degrees(degree) - 90) % 360)
                ## add the bearing to the original list
                ## the bearing represents the direction before the maneuver
                index = bearing.index(s)
                bearing[index] = result
                maneuver_list[index] = maneuver
            if maneuver == "turn-left":
                endlat = radians(i["end_location"]["lat"])
                endlng = radians(i["end_location"]["lng"])
                startlat = radians(i["start_location"]["lat"])
                startlng = radians(i["start_location"]["lng"])
                dL = (endlng)-(startlng)
                X = cos(endlat)* sin(dL)
                Y = cos(startlat)*sin(endlat) - sin(startlat)*cos(endlat)* cos(dL)
                degree = atan2(X,Y)
                ## calculates the bearing inbetween the two lights
                result = ((degrees(degree) + 90) % 360)
                ## add the bearing to the original list
                index = bearing.index(s)
                bearing[index] = result
                maneuver_list[index] = maneuver
print(type(bearing[0]))
for l in bearing:
    if type(l) == tuple:
        maneuver = "straight"
        index  = bearing.index(l)
        print(index)
        maneuver_list[index] = maneuver
        if index == 0:
            file = tuple(l)
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
            degree = atan2(X,Y)
            ## calculates the bearing inbetween the two lights
            result = ((degrees(degree) + 90) % 360)
            ## add the bearing to the original list
            index = bearing.index(l)
            bearing[index] = result
        else:
            for i in maneuver_list:
                if i == "straight":
                    index = maneuver_list.index(i)
                    turn = (maneuver_list[index - 1])
                    if turn == "turn-right":
                        result = (bearing[index - 1]) + 90
                        index = bearing.index(l)
                        bearing[index] = result
                    if turn == "turn-left":
                        result = (bearing[index - 1]) + 90
                        index = bearing.index(l)
                        bearing[index] = result
    else:
        continue
start = (convert.normalize_lat_lng(json_directions["routes"][0]["legs"][0]["start_location"]))
end = (convert.normalize_lat_lng(json_directions["routes"][0]["legs"][0]["end_location"]))
waypoints.insert(0, start)
lastvalue = len(waypoints) + 1
waypoints.insert(lastvalue , end)


print(bearing)
print(maneuver_list)
print(waypoints)

## reverses the order of all the lists
waypoints.reverse()
bearing.reverse()
maneuver_list.reverse()
maneuver_list_length = len((waypoints))- 2

time_values = []

for i in waypoints:
    ## if the lat lng is the final point on the route
    if waypoints.index(i) == (len(waypoint) - 1):
        break
    else:
        index = waypoints.index(i)
        final_point = convert.latlng(waypoints[index])
        start_point = convert.latlng(waypoints[(index-1)])
        parameters_distance1 = {"origins": start_point,
                            "destinations": final_point,  
                            "arrival_time": convert.time(time_arrival), 
                            "key": api_key}
        ## gets the api response
        response_directions = requests.get(url_distance, params=parameters_distance1)
        ## turns the api response into json formating 
        json_directions = (response_directions.json())
        final_directions = json.dumps(json_directions, indent = 4)
        ## grabs the time inbetween the lights from the api response
        duration = (json_directions["rows"][0]["elements"][0]["duration"]["value"])
        ## format the time inbetween in datetime format
        time = datetime.timedelta(seconds = duration)
        ## update the running time by subtracting the arrival time from the inbetween time
        time_arrival = time_arrival - time
        time_values.append(time_arrival)

print(time_values)
