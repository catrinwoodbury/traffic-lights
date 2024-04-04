def final_time():
    while 0 <= empty_value_one < ((len(copy_intersections)) - 2):
            departure = estimated_time
            starting_point = (copy_intersections[empty_value_one])
            end_point = (copy_intersections[(empty_value_one + 1)])
            final = convert.latlng(end_point)
            begining = convert.latlng(starting_point)
            print("final: ", final)
            print("begining: ", begining)

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

            bearing_value = (copy_bearings[empty_value])
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

            move = (copy_manuvers[empty_value_one])

            green_turn = (data["intersections"][empty_value_one]["directions"][bearing][move]["start_time"])
            year, month, day, hour, minute, second = map(int, green_turn.split('-'))
            ## formats the time the light turns green in date time format
            turned_at = datetime.datetime(year, month, day, hour, minute, second)

            between_time = departure - turned_at
            totaltime = timedelta.total_seconds(between_time)

            green = (data["intersections"][empty_value]["directions"][bearing][move]["green_time"])
            green_time = sum(green) / len(green)
            print(green_time)
            red = (data["intersections"][empty_value]["directions"][bearing][move]["red_time"])
            red_time = sum(red) / len(red)
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
                print( "The light will be GREEN for", timetochange, "more seconds.")
            else:
                timeinred = partialcycle - green_time
                redleft = round(red_time - timeinred, 3)
                red_count = red_count + 1
                print("The light will be RED for", redleft, "more seconds.")
                departure = (datetime.timedelta(seconds = redleft)) + departure