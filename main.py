from dotenv import load_dotenv
import os
import datetime
from math import sin, cos, sqrt, atan2, radians, degrees 
import json
import requests
from googlemaps import convert
from datetime import timedelta
import math

## gets the api key
load_dotenv(dotenv_path='api_key.env')
api_key = os.getenv('API_KEY')
print("API KEY? " , api_key)

def route(starting_point, end_point, input_time):
    ## empty lists
    original_index_list = []
    intersections = []
    distance = []
    maneuver_list = []
    red_count = 0
    green_count = 0
    ## radius of the earth in miles
    radius = 3959.87433

    ## opens and parses the json database
    f = open('intervals.json', "r")
    data = json.loads(f.read())

    year, month, day, hour, minute, second = map(int, str(input_time).split('-'))
    time_arrival = datetime.datetime(year, month, day, hour, minute, second)

    user_time_arrival = time_arrival

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
            if final <= 800:
                ## create a list of the original intersection indexes
                indexes = coords.index(i)
                original_index_list.append(indexes)
                original_index_list = list(set(original_index_list))
                ## create a list of the intersections on the route
                intersections.append(tuple(i))
    intersections = list(set(intersections))
    ## gets the start location in google maps format 
    start = (convert.normalize_lat_lng(json_directions["routes"][0]["legs"][0]["start_location"]))
    ## breaks the start location down into individual lat lngs 
    
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
    sorted_index =[original_index_list[i] for i in sort]
    steps = (json_directions["routes"][0]["legs"][0]["steps"])

    maneuver_list = maneuver_list[::-1]
    bearing_list = bearing_list[::-1]

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
            if final <= 150:
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
                tupleing = tuple(intersections[0])
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
                (bearing_list[0]) = result
            else:
                turn = (maneuver_list[index - 1])
                if turn == "turn-right":
                    subtracted_index = (index - 1)
                    result = (((bearing_list[subtracted_index]) + 90) % 360)
                    index2 = bearing_list.index(l)
                    bearing_list[index2] = result
                if turn == "turn-left":
                    result = (((bearing_list[subtracted_index]) - 90) % 360)
                    index2 = bearing_list.index(l)
                    bearing_list[index2] = result
                if turn == "straight":
                    subtracted_index = (index - 1)
                    result = (bearing_list[subtracted_index])
                    index2 = bearing_list.index(l)
                    bearing_list[index2] = result

    start = (convert.normalize_lat_lng(json_directions["routes"][0]["legs"][0]["start_location"]))
    end = (convert.normalize_lat_lng(json_directions["routes"][0]["legs"][0]["end_location"]))
    intersections.insert(0, start)
    lastvalue = len(intersections)
    intersections.insert(lastvalue , end)


  
    ## creates an empty value
    empty_value = 0

    very_end = convert.latlng(intersections[-1])
    last_light = convert.latlng(intersections[-2])
    
    url_distance = "https://maps.googleapis.com/maps/api/distancematrix/json"
    parameters_distance = {"origins": last_light,
                                "destinations": very_end,  
                                "arrival_time": convert.time(time_arrival), 
                                "key": api_key}
    response_directions = requests.get(url_distance, params=parameters_distance)
    ## turns the api response into json formating 
    json_directions = (response_directions.json())
    final_directions = json.dumps(json_directions, indent = 4)
    
    ## grabs the time inbetween the lights from the api response
    duration = (json_directions["rows"][0]["elements"][0]["duration"]["value"])

    time = datetime.timedelta(seconds = duration)
    time_arrival = time_arrival - time


    copy_manuvers = maneuver_list
    copy_intersections = intersections
    copy_bearings = bearing_list

    maneuver_list = maneuver_list[::-1]
    intersections = intersections[::-1]
    bearing_list = bearing_list[::-1]
    rev_original_index_list = original_index_list[::-1]

    print("MANEUVER: ", maneuver_list)
    print("INTERSECTIONS: ", intersections)
    print("BEARINGS: ", bearing_list)
    print("REVERSED INDEXES: ", rev_original_index_list)



    while empty_value <= (len(intersections) - 2):
        waypoint = (intersections[empty_value])
        ## if the waypoint is the endpoint:
        if empty_value == 0:
            empty_value += 1
            continue
        else:
            starting_point = (intersections[(empty_value + 1)])
            end_point = (intersections[empty_value])

        final = convert.latlng(end_point)
        begining = convert.latlng(starting_point)

      

        parameters_distance = {"origins": begining,
                            "destinations": final,  
                            "arrival_time": convert.time(time_arrival), 
                            "key": api_key}
        

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


        bearing_value = (bearing_list[empty_value -1])
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

        move = (maneuver_list[empty_value - 1])
        value = (rev_original_index_list[empty_value - 1])
        green_turn = (data["intersections"][value]["directions"][bearing][move]["start_time"])
        year, month, day, hour, minute, second = map(int, green_turn.split('-'))
        ## formats the time the light turns green in date time format
        turned_at = datetime.datetime(year, month, day, hour, minute, second)

        between_time = time_arrival - turned_at
        totaltime = timedelta.total_seconds(between_time)

        green = (data["intersections"][value]["directions"][bearing][move]["green_time"])
        
        green_time = sum(green) / len(green)
        green_time = round(green_time)
        red = (data["intersections"][value]["directions"][bearing][move]["red_time"])
        red_time = sum(red) / len(red)
        red_time = round(red_time)
        cycletime = green_time + red_time
        rawnum = totaltime / cycletime
        ## the number of complete cycles that can be run in that time
        truncated_value = math.floor(rawnum)
        ## the decimal of the number of incomplete cycles that can be run in that time
        leftover = rawnum - truncated_value
        ## the number of seconds into the new cycle the light is
        partialcycle = leftover * cycletime
        ## determines if light is red or green and tells user how much longer the light will be red or green for
        if partialcycle <= green_time:
            timetochange = round(green_time - partialcycle, 3)
            green_count = green_count + 1
        else:
            timeinred = partialcycle - green_time
            redleft = round(red_time - timeinred, 3)
            red_count = red_count + 1
            time_arrival -= datetime.timedelta(seconds = redleft)
        empty_value += 1

    rounded = time_arrival + timedelta(seconds=(60 - time_arrival.second) % 60)
    print("rounded: ", rounded)

    ## add two minutes to the rounded time
    added_time = datetime.timedelta(minutes=3)

    ## amount that each trial will change by
    one_min_change = datetime.timedelta(minutes=1)

    ## the rounded time plus two minues
    estimated_time = rounded + added_time
    ## the rounded time nimus two minutes
    minimum_time = rounded - added_time

   


    def final_time(empty_value_one = 0, green_count1 = 0, red_count1 = 0):
        departure = estimated_time
        while 0 <= empty_value_one <= ((len(copy_intersections)) - 2):

                if empty_value_one == 0:
                    starting_point = (copy_intersections[0])
                    end_point = (copy_intersections[1])
                    final = convert.latlng(end_point)
                    begining = convert.latlng(starting_point)
                    parameters_distance = {"origins": begining,
                                        "destinations": final,  
                                        "departure_time": convert.time(departure), 
                                        "traffic_model": "best_guess",
                                        "key": api_key}
                    

                    ## gets the api response
                    response_directions = requests.get(url_distance, params=parameters_distance)
                    ## turns the api response into json formating 
                    json_directions = (response_directions.json())
                    final_directions = json.dumps(json_directions, indent = 4)
                    ## grabs the time inbetween the lights from the api response
                    duration = (json_directions["rows"][0]["elements"][0]["duration"]["value"])
                    time = datetime.timedelta(seconds = duration)
                    ## update the running time by subtracting the arrival time from the inbetween time
                    departure = departure + time
                    empty_value_one += 1
                    continue
                
                else: 
                    starting_point = (copy_intersections[empty_value_one])
                    end_point = (copy_intersections[(empty_value_one + 1)])
                    final = convert.latlng(end_point)
                    begining = convert.latlng(starting_point)
                   

                    parameters_distance = {"origins": begining,
                                            "destinations": final,  
                                            "departure_time": convert.time(departure), 
                                            "traffic_model": "best_guess",
                                            "key": api_key}
                        

                    ## gets the api response
                    response_directions = requests.get(url_distance, params=parameters_distance)
                    ## turns the api response into json formating 
                    json_directions = (response_directions.json())
                    final_directions = json.dumps(json_directions, indent = 4)
                    ## grabs the time inbetween the lights from the api response
                    duration = (json_directions["rows"][0]["elements"][0]["duration"]["value"])
                    time = datetime.timedelta(seconds = duration)
                    ## update the running time by subtracting the arrival time from the inbetween time
                    departure = departure + time

                    bearing_value = (copy_bearings[(empty_value_one - 1)])
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

                    move = (copy_manuvers[(empty_value_one - 1)])

                    value = (original_index_list[(empty_value_one - 1)])
                    green_turn = (data["intersections"][value]["directions"][bearing][move]["start_time"])
                    year, month, day, hour, minute, second = map(int, green_turn.split('-'))
                    ## formats the time the light turns green in date time format
                    turned_at = datetime.datetime(year, month, day, hour, minute, second)

                    between_time = departure - turned_at
                    totaltime = timedelta.total_seconds(between_time)

                    green = (data["intersections"][value]["directions"][bearing][move]["green_time"])
                    green_time = sum(green) / len(green)
                    green_time = round(green_time)
                    red = (data["intersections"][value]["directions"][bearing][move]["red_time"])
                    red_time = sum(red) / len(red)
                    red_time = round(red_time)
                    cycletime = green_time + red_time
                    rawnum = totaltime / cycletime
                    ## the number of complete cycles that can be run in that time
                    truncated_value = math.floor(rawnum)
                    ## the decimal of the number of incomplete cycles that can be run in that time
                    leftover = rawnum - truncated_value
                    ## the number of seconds into the new cycle the light is
                    partialcycle = leftover * cycletime
                    ## determines if light is red or green and tells user how much longer the light will be red or green for
                    if partialcycle <= green_time:
                        timetochange = round(green_time - partialcycle, 3)
                        green_count1 = green_count1 + 1
                        ## print( "The light will be GREEN for", timetochange, "more seconds.")
                    else:
                        timeinred = partialcycle - green_time
                        redleft = round(red_time - timeinred, 3)
                        red_count1 = red_count1 + 1
                        ## print("The light will be RED for", redleft, "more seconds.")
                        departure = (datetime.timedelta(seconds = redleft)) + departure
                    #year, month, day, hour, minute, second = map(int, str(departure).split(','))
                    #estimated_arrival_time = datetime.datetime(year, month, day, hour, minute, second)
                    empty_value_one += 1
                    rounded_arrival_time = departure + timedelta(seconds=(60 - departure.second) % 60)

        return(green_count1, red_count1, (rounded_arrival_time))
                
        ## while the estimated_time is greater than the rounded time minus two minutes
    while minimum_time <= estimated_time <= (rounded + added_time):
        listing = final_time()
        arrival_time = (listing[2])
        
        if arrival_time < user_time_arrival:
            print("Departure Time: ", estimated_time)
            print(listing)
        
        estimated_time = estimated_time - one_min_change

    
route(starting_point = "8131 S Pierce St, Littleton, CO 80128", end_point = "5960 S Eaton Ln, Littleton, CO 80123", input_time = "2024-12-24-13-10-00")
