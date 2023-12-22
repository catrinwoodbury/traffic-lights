import requests
import json

response = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json?destinations=40.659569%2C-73.933783%7C40.729029%2C-73.851524%7C40.6860072%2C-73.6334271%7C40.598566%2C-73.7527626&origins=40.6655101%2C-73.89188969999998&key=AIzaSyCqhq6c811qavWvjC3vpEVuoZcZtcJO_0Q")

jsonapi =(response.json())

final = json.dumps(jsonapi, indent = 4)

print(final)