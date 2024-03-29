import datetime
from math import sin, cos, sqrt, atan2, radians, degrees 
import json
import requests
from googlemaps import convert
from datetime import timedelta
import math

def initial_route(starting_point, end_point, time):
    with open("api_key.json") as api:
        authent = json.load(api)

    api_key = str(authent["api_key"])
    f = open('intervals.json', "r")
    data = json.loads(f.read())
    year, month, day, hour, minute, second = map(int, time.split('-'))
    time_arrival = datetime.datetime(year, month, day, hour, minute, second)
    url_directions = "https://maps.googleapis.com/maps/api/directions/json"
    parameters_directions = {"origin": starting_point,
                        "destination": end_point,  
                        "arrival_time": convert.time(time_arrival), 
                        "key": api_key}
    response_directions = requests.get(url_directions, params=parameters_directions)
    ## turns the request into json format
    json_directions = (response_directions.json())
    final_directions = json.dumps(json_directions, indent = 4)
    poly_line = (json_directions["routes"][0]["overview_polyline"]["points"])
    print(poly_line)
    decode = convert.decode_polyline(poly_line)
    coords = [cord["lat,lng"] for cord in data["intersections"]] 
    print(coords)

initial_route(starting_point= "6281 W Alder Ave, Littleton, CO 80128", end_point= "7034 W Roxbury Pl, Littleton, CO 80128", time= "2024-3-20-00-00-00")