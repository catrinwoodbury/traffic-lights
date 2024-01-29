import datetime
from math import sin, cos, sqrt, atan2, radians, acos
import json
import requests
from googlemaps import convert
## radius of the earth in km
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
starting_point = "8489 S Upham Way, Littleton, CO 80128"
end_point = "4887 S Wadsworth Wy #100, Littleton, CO 80123"

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
        print(type(lat1))
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
print(waypoints)    


## format: string
start_loc = convert.latlng(json_directions["routes"][0]["legs"][0]["start_location"])

location = start_loc.split()
print(location)

lat_2 = radians(float(start_loc[0]))
long_2 = radians(float(start_loc[1]))

for s in waypoints: 
    end = convert.normalize_lat_lng(s)
    lat1 = (end[0])
    long1 = (end[1])
    final = acos((sin(radians(lat1)) * sin(radians(lat_2))) + (cos(radians(lat1)) * cos(radians(lat_2))) * (cos(radians(long_2) - radians(long1)))) * Rad
    ## add the distance from start to the list
    dist.append(final)
    distances = list(set(dist))
    ## sort the list based on which point is the closest to the start
    print(distances)
sort = sorted(range(len(distances)), key=lambda k: distances[k])
print(sort)
 
wp = [waypoints[i] for i in sort]
print("Waypoints: ", wp )





optimize = "optimize:true|"
## calculate directions between the origin and destination through the way points
parameters_directions = {"origin": starting_point,
                        "destination": end_point,  
                        "arrival_time": convert.time(time_arrival),
                        "waypoints": optimize + convert.location_list(wp),
                        "key": api_key}
response_directions = requests.get(url_directions, params=parameters_directions)
json_directions = (response_directions.json())
final_directions = json.dumps(json_directions, indent = 4)
print(final_directions)

## closing file
f.close()