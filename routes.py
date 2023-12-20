import json
#with open('data.json') as access_json:
 #   read_content = json.load(access_json)
#lights = (read_content['lights'])
#print((lights[1]['latitude']))

with open("intervals.json") as interval_data:
    data = json.load(interval_data)
    gra = "north"
green_time = (data["intersections"][0]["directions"][gra]["green_time"])
print(green_time)
