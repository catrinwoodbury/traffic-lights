import datetime
from math import sin, cos, sqrt, atan2, radians
import json
import requests
from googlemaps import convert
## radius of the earth in km
wp = []
place_waypoints = []
R = 6373.0

with open("api_key.json") as api:
    authent = json.load(api)
api_key = str(authent["api_key"])

f = open('intervals.json', "r")
# Reading from file
data = json.loads(f.read())
 
starting_point = "7179 S Cody Way, Littleton, CO 80128"
end_point = "5375 S Wadsworth Blvd, Lakewood, CO 80123"

arrival_time = input("Input your desired arrival time in YYYY-MM-DD-HH-MM-SS format: ")
year, month, day, hour, minute, second = map(int, arrival_time.split('-'))
time_arrival = datetime.datetime(year, month, day, hour, minute, second)


url_distance = "https://maps.googleapis.com/maps/api/distancematrix/json"
url_directions = "https://maps.googleapis.com/maps/api/directions/json"
url_roads = "https://roads.googleapis.com/v1/snapToRoads"

###DIRECTIONS
parameters_directions = {"origin": starting_point,
                        "destination": end_point,  
                        "arrival_time": convert.time(time_arrival), 
                        "key": api_key}
response_directions = requests.get(url_directions, params=parameters_directions)
json_directions = (response_directions.json())
final_directions = json.dumps(json_directions, indent = 4)
#print(final_directions)


poly_line = (json_directions["routes"][0]["overview_polyline"]["points"])
decode = convert.decode_polyline(poly_line)
## through the json list
coords = [cord["lat,lng"] for cord in data["intersections"]] 
for i in coords:
    file = tuple(i)
    result = convert.normalize_lat_lng(file)
    lat1 = radians(result[0])
    long1 = radians(result[1])
    for s in decode:
        end = convert.normalize_lat_lng(s)
        lat2 = radians(end[0])
        long2 = radians(end[1])
        dlon = long2 - long1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        ## convert to feet
        final = distance * 3280.84
        if final <= 400:
            wp.append(result)
            waypoints = list(set(wp))
for v in waypoints:
    parameters_roads = {"path": convert.location_list(v),
                        "interpolate": True,
                        "key": api_key}
    response_roads = requests.get(url_roads, params=parameters_roads)
    json_roads = (response_roads.json())
    final_roads = json.dumps(json_roads, indent = 4)
    print(final_roads)
    
#print(waypoints)    
#parameters_directions = {"origin": starting_point,
                        #"destination": end_point,  
                        #"arrival_time": convert.time(time_arrival),
                        #"waypoints": "optimize:true|" + convert.location_list(waypoints), 
                        #"key": api_key}
#response_directions = requests.get(url_directions, params=parameters_directions)
#json_directions = (response_directions.json())
#final_directions = json.dumps(json_directions, indent = 4)
#print(final_directions)

## closing file
f.close()