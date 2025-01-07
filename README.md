# Predictive Navigation System 
This Python script calculates the estimated departure time from a location, factoring in traffic lights and their signal phase lengths (green/red light durations) along a user-provided route. The program uses Google Maps Directions API and Distance Matrix API to calculate the route and distance between intersections, while taking into account traffic signal timings to estimate the best route and timing. The script then returns the user with various departure times, and the number of red/green traffic signals the user is expected to encounter.

## Features
- Calculates travel time and traffic light cycles for an entire route.
- Uses Google Maps API to obtain directions and distances.
- Extracts real-time intersection data from a JSON file to calculate optimal timings.
- Predicts the best departure time based on traffic light cycles and arrival time constraints.

## Requirements 
This project requires the following Python libraries:
- requests
- googlemaps
- dotenv
- math
- datetime
