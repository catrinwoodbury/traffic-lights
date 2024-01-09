import math

destination_x =   39.6047322 
origin_x = 39.6044273 
destination_y = -105.0737276
origin_y = -105.0725764

    
cardinal_degree = (math.degrees(math.atan2(((destination_y)-(origin_y)),((destination_x)-(origin_x)))))


if cardinal_degree < 0:
    cardinal_degree = cardinal_degree + 360
    print(cardinal_degree)
else:
    print(cardinal_degree)

if 337.5 <= cardinal_degree <= 360:
    print("North")
if 0 <= cardinal_degree < 22.5:
    print("North")
if 22.5 <= cardinal_degree < 67.5:
    print("North-East")
if 67.5 <= cardinal_degree < 112.5:
    print("East")
if 112.5 <= cardinal_degree < 157.5:
    print("South-East")
if 157.5 <= cardinal_degree < 202.5:
    print("South")
if 202.5 <= cardinal_degree < 247.5:
    print("South-West")
if 247.5 <= cardinal_degree < 292.5:
    print("West")
if 292.5 <= cardinal_degree < 337.5:
    print("North-West")