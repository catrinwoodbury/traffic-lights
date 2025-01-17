from dotenv import load_dotenv
import os
from math import sin, cos, sqrt, atan2, radians, degrees 
import json
import requests
from googlemaps import convert
import datetime
from datetime import timedelta
import math

## radius of the earth in miles
radius = 3959.87433
## API directions request
url_directions = "https://maps.googleapis.com/maps/api/directions/json"
## API distance request
url_distance = "https://maps.googleapis.com/maps/api/distancematrix/json"


## gets the api key
def get_api_key():
    load_dotenv(dotenv_path='api_key.env')
    api_key = os.getenv('API_KEY')
    return(api_key)

def get_directions(starting_point, end_point, end_time):

    
    ## DIRECTIONS calculation for the entire route:
    ## parameters
    parameters_directions = {"origin": starting_point,
                        "destination": end_point,  
                        "arrival_time": convert.time(end_time), 
                        "key": get_api_key()}
    ## gets the request
    response_directions = requests.get(url_directions, params=parameters_directions)
    ## turns the request into json format
    json_directions = (response_directions.json())
    final_directions = json.dumps(json_directions, indent = 4)
    return(json_directions)


def polyline_extraction(directions):
    ## gets the polyline and turns it into lat longs for the entire route
    poly_line = (directions["routes"][0]["overview_polyline"]["points"])
    decoded_polyline = convert.decode_polyline(poly_line)
    return(decoded_polyline)


def get_json_data():
    ## opens and parses the json data
    with open('intervals.json', 'r') as f:
        data = json.load(f)
    return(data)

def distance_calc(lat1, long1, lat2, long2):
## calculates the distance between the intersection and polyline
        dlon = long2 - long1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        ## radius of the earth in miles
        distances = radius * c
        ## convert to feet
        final = distances * 5280
        return(final)

def extract_intersections(data, decoded_polyline):
    intersections = []
    original_index_list =[]
    ## locates all lat long values in intersection data
    coords = [cord["lat,lng"] for cord in data["intersections"]] 
    ## for each lat long value
    for i in coords:
        ## turns the lat long into a tuple
        tupled_lat_long = tuple(i)
        ## converts to google map lat long format
        normalized_lat_long = convert.normalize_lat_lng(tupled_lat_long)
        ## breaks tuple into specific lat long coords
        lat2 = radians(normalized_lat_long[0])
        long2 = radians(normalized_lat_long[1])
    ## for each lat long coord in the polyline
        for s in decoded_polyline:
            ## breaks lat long coords down 
            end_point = convert.normalize_lat_lng(s)
            end_lat = radians(end_point[0])
            end_lng = radians(end_point[1])
            distance_between = distance_calc(end_lat, end_lng, lat2, long2)
            if distance_between <= 50:
                ## create a list of the original intersection indexes
                indexes = coords.index(i)
                original_index_list.append(indexes)
                original_index_list = list(set(original_index_list))
                ## create a list of the intersections on the route
                intersections.append(tuple(i))
    intersections = list(set(intersections))
    return intersections, original_index_list

def calc_bearing(endlong, startlong, endlat, startlat):
    dL = (endlong)-(startlong)
    X = cos(endlat)* sin(dL)
    Y = cos(startlat)*sin(endlat) - sin(startlat)*cos(endlat)* cos(dL)
    degree = atan2(X,Y)
    return degree

def get_distance(beginning, end, time):
    parameters_distance = {"origins": beginning,
                                "destinations": end,  
                                "arrival_time": convert.time(time), 
                                "key": get_api_key()}
    response_distance = requests.get(url_distance, params=parameters_distance)
    ## turns the api response into json formating 
    json_distance = (response_distance.json())
    final_distance = json.dumps(json_distance, indent = 4)
    return json_distance
    

def route(starting_point, end_point, time_arrival):
    ## empty lists
    original_index_list = []
    distance = []
    maneuver_list = []
    red_count = 0
    green_count = 0

    data = get_json_data()

    year, month, day, hour, minute, second = map(int, str(time_arrival).split('-'))
    time_arrival = datetime.datetime(year, month, day, hour, minute, second)
    ## gets directions from the api
    directions = get_directions(starting_point, end_point, time_arrival)

    ## decodes the directions polyline into lat longs
    decoded_polyline = polyline_extraction(directions)
    
    ## creates duplicate variable for later use
    user_time_arrival = time_arrival
    
    ## extracts intersections and their indexes that are along the route
    intersections, original_index_list = extract_intersections(data, decoded_polyline)
    
    ## gets the start location in google maps format 
    start = (convert.normalize_lat_lng(directions["routes"][0]["legs"][0]["start_location"]))
    ## breaks the start location down into individual lat lngs 
    start_lat = radians(start[0])
    start_long = radians(start[1])

    ## calculates the distance between the start location and each intersection
    for i in intersections:
        end = convert.normalize_lat_lng(i)
        end_lat = radians(end[0])
        end_long = radians(end[1])
        final = distance_calc(end_lat, end_long, start_lat, start_long)
        ## creates a list of the distances
        distance.append(final)
    
    sort = sorted(range(len(distance)), key=lambda k: distance[k])
    ## re-sort the original lat long list based on which waypoints are closest to the start
    intersections = [intersections[i] for i in sort]
    bearing_list = [intersections[i] for i in sort]
    maneuver_list = [intersections[i] for i in sort]
    sorted_index =[original_index_list[i] for i in sort]
    steps = (directions["routes"][0]["legs"][0]["steps"])

    ## reverses these lists
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
            final = distance_calc(lat1, long1, lat2, long2)
            ## determines if the step applies to the intersection
            if final <= 50:
                maneuver = (i["maneuver"])
                if maneuver == "turn-right":
                    endlat = radians(i["end_location"]["lat"])
                    endlong = radians(i["end_location"]["lng"])
                    startlat = radians(i["start_location"]["lat"])
                    startlong = radians(i["start_location"]["lng"])
                    degree = calc_bearing(endlong, startlong, endlat, startlat)
                    ## calculates the bearing inbetween the two lights
                    result = ((degrees(degree) - 90) % 360)
                    index = bearing_list.index(s)
                    bearing_list[index] = result
                    ## adds the manuever to a list of manuevers
                    maneuver_list[index] = maneuver
                if maneuver == "turn-left":
                    endlat = radians(i["end_location"]["lat"])
                    endlong = radians(i["end_location"]["lng"])
                    startlat = radians(i["start_location"]["lat"])
                    startlong = radians(i["start_location"]["lng"])
                    degree = calc_bearing(endlong, startlong, endlat, startlat)
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
            ## sets the maneuver of all other bearing values to straight
            index  = bearing_list.index(l)
            maneuver_list[index] = maneuver
            if index == 0:
                tupleing = tuple(intersections[0])
                ## converts to google map lat long format
                result = convert.normalize_lat_lng(tupleing)
                ## breaks tuple into specific lat long coords
                startlat = radians(directions["routes"][0]["legs"][0]["start_location"]["lat"])
                startlong = radians(directions["routes"][0]["legs"][0]["start_location"]["lng"])
                endlat = radians(result[0])
                endlong = radians(result[1])
                degree = calc_bearing(endlong, startlong, endlat, startlat)

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

    start = (convert.normalize_lat_lng(directions["routes"][0]["legs"][0]["start_location"]))
    end = (convert.normalize_lat_lng(directions["routes"][0]["legs"][0]["end_location"]))
    intersections.insert(0, start)
    lastvalue = len(intersections)
    intersections.insert(lastvalue , end)


  
    ## creates an empty value
    empty_value = 0

    very_end = convert.latlng(intersections[-1])
    last_light = convert.latlng(intersections[-2])
    
    
    json_directions = get_distance(last_light, very_end,time_arrival)
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
       
        ## turns the api response into json formating 
        json_distance = get_distance(begining, final, time_arrival)

        ## turns the api response into json formating 
        # json_distance = get_distance(begining, final, time_arrival)
        # final_distance = json.dumps(json_distance, indent = 4)
        ## grabs the time inbetween the lights from the api response
        duration = (json_distance["rows"][0]["elements"][0]["duration"]["value"])
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
                    ## turns the api response into json formating 
                    json_distance = get_distance(begining, final, departure)
                    final_distance = json.dumps(json_distance, indent = 4)
                    ## grabs the time inbetween the lights from the api response
                    duration = (json_distance["rows"][0]["elements"][0]["duration"]["value"])
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
                   

                    ## turns the api response into json formating 
                    json_distance = get_distance(begining, final, departure)
                    final_distance = json.dumps(json_distance, indent = 4)

                    ## grabs the time inbetween the lights from the api response
                    duration = (json_distance["rows"][0]["elements"][0]["duration"]["value"])
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

        return(("Green Lights: ", green_count1), ("Red Lights: ", red_count1), (rounded_arrival_time))
                
        ## while the estimated_time is greater than the rounded time minus two minutes
    while minimum_time <= estimated_time <= (rounded + added_time):
        listing = final_time()
        arrival_time = (listing[2])
        
        if arrival_time < user_time_arrival:
            print("Departure Time: ", estimated_time.strftime("%m/%d/%Y, %H:%M:%S"))
            print(listing[0])
            print(listing[1])
            print(listing[2].strftime("%m/%d/%Y, %H:%M:%S"))

        
        estimated_time = estimated_time - one_min_change

    
route(starting_point = "8131 S Pierce St, Littleton, CO 80128", end_point = "5960 S Eaton Ln, Littleton, CO 80123", time_arrival = "2024-12-29-4-10-00")
