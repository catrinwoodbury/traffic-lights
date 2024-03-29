import datetime
from math import sin, cos, sqrt, atan2, radians, degrees 
import json
import requests
from googlemaps import convert
from datetime import timedelta
import math

def route(starting_point, end_point, input_time):
    ## empty lists
    original_index_list = []
    intersections = []
    distance = []
    maneuver_list = []

    ## radius of the earth in miles
    radius = 3959.87433

    ## gets the api key
    with open("api_key.json") as api:
        authent = json.load(api)
    api_key = str(authent["api_key"])

    ## opens and parses the json database
    f = open('intervals.json', "r")
    data = json.loads(f.read())

    year, month, day, hour, minute, second = map(int, str(input_time).split('-'))
    time_arrival = datetime.datetime(year, month, day, hour, minute, second)

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
            ## radius of the earth in miles
            distances = radius * c
            ## convert to feet
            final = distances * 5280
            if final <= 500:
                print("i", i)
                ## create a list of the original intersection indexes
                indexes = coords.index(i)
                original_index_list.append(indexes)
                original_index_list = list(set(original_index_list))
                ## create a list of the intersections on the route
                intersections.append(tuple(i))
    intersections = list(set(intersections))
    print(intersections)
    ## gets the start location in google maps format 
    start = (convert.normalize_lat_lng(json_directions["routes"][0]["legs"][0]["start_location"]))
    ## breaks the start location down into individual lat lngs 
    start_lat = radians(float(start[0]))
    start_lng = radians(float(start[1]))
    
    ## calculates the distance between the start location and each intersection
    for i in intersections:
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
        ## creates a list of the distances
        distance.append(final)
    
    sort = sorted(range(len(distance)), key=lambda k: distance[k])
    ## re-sort the original lat long list based on which waypoints are closest to the start
    intersections = [intersections[i] for i in sort]
    bearing_list = [intersections[i] for i in sort]
    maneuver_list = [intersections[i] for i in sort]

    steps = (json_directions["routes"][0]["legs"][0]["steps"])

    for s in bearing_list:
        tupleing = tuple(s)
        ## converts to google map lat long format
        result = convert.normalize_lat_lng(tupleing)
        ## breaks tuple into specific lat long coords
        lat2 = radians(result[0])
        long2 = radians(result[1])
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
            if final <= 100:
                maneuver = (i["maneuver"])
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
                    index = bearing_list.index(s)
                    print(index)
                    bearing_list[index] = result
                    ## adds the manuever to a list of manuevers
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
                    index = bearing_list.index(s)
                    print(index)
                    bearing_list[index] = result
                    ## adds the manuever to a list of manuevers
                    maneuver_list[index] = maneuver
    ## all other manuevers that are not left or right must be straight
    for l in bearing_list:
        if type(l) == tuple:
            maneuver = "straight"
            index  = bearing_list.index(l)
            maneuver_list[index] = maneuver
            if index == 0:
                tupleing = tuple(intersections[index])
                ## converts to google map lat long format
                result = convert.normalize_lat_lng(tupleing)
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
                result = (degrees(degree) % 360)
                 ## add the bearing to the original list
                bearing_list[index] = result
            else:
                turn = (maneuver_list[index - 1])
                if turn == "turn-right":
                    result = (bearing_list[index - 1]) + 90
                    index = bearing_list.index(l)
                    bearing_list[index] = result
                if turn == "turn-left":
                    result = (bearing_list[index - 1]) - 90
                    index = bearing_list.index(l)
                    bearing_list[index] = result

    start = (convert.normalize_lat_lng(json_directions["routes"][0]["legs"][0]["start_location"]))
    end = (convert.normalize_lat_lng(json_directions["routes"][0]["legs"][0]["end_location"]))
    intersections.insert(0, start)
    lastvalue = len(intersections)
    intersections.insert(lastvalue , end)


    ## Reverses the order of a list
    intersections[::-1]
    bearing_list[::-1]
    maneuver_list[::-1]

    print(intersections)
    ## creates an empty value
    empty_value = 0

    while empty_value < (len(intersections) - 2):
        print(empty_value)
        waypoint = (intersections[empty_value])
        print(waypoint)
        ## if the waypoint is the endpoint:
        if empty_value == 0:
            starting_point = (intersections[1])
            end_point = (intersections[0])
        else:
            starting_point = (intersections[(empty_value + 1)])
            end_point = (intersections[empty_value])

        final = convert.latlng(end_point)

        begining = convert.latlng(starting_point)

        print("final: ", final)
        print("begining: ", begining)

        parameters_distance = {"origins": begining,
                            "destinations": final,  
                            "arrival_time": convert.time(time_arrival), 
                            "key": api_key}
        
        url_distance = "https://maps.googleapis.com/maps/api/distancematrix/json"

        ## gets the api response
        response_directions = requests.get(url_distance, params=parameters_distance)
        ## turns the api response into json formating 
        json_directions = (response_directions.json())
        final_directions = json.dumps(json_directions, indent = 4)
        ## grabs the time inbetween the lights from the api response
        duration = (json_directions["rows"][0]["elements"][0]["duration"]["value"])
        time = datetime.timedelta(seconds = duration)
        ## update the running time by subtracting the arrival time from the inbetween time
        time_arrival -= time

        bearing_value = (bearing_list[empty_value])
        if 315 <= bearing_value <= 360:
            bearing = "north"
        if 0 <= bearing_value < 45:
            bearing = "north"
        if 45 <= bearing_value < 135:
            bearing = "east"
        if 135 <= bearing_value < 225:
            bearing = "south"
        if 225 <= bearing_value < 315:
            bearing = "west"
        else:
            print("error: ", bearing_value)
        print(bearing)
        empty_value += 1

route(starting_point ="6281 W Alder Ave, Littleton, CO 80128", end_point ="7034 W Roxbury Pl, Littleton, CO 80128", input_time = "2024-3-31-00-00-00")
