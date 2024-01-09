import math

destination_x = 39.579280
origin_x = 39.580670 
destination_y = -105.072787
origin_y = -105.070955

P1X= (40.716366666666666,-73.91161666666666)
P2 =(40.716483333333336, -73.91175)
    
angle = math.atan2((-73.91175-(-73.911616)),(40.716483-40.71636))

degree = math.degrees(angle)

cardinal_degree = 90 - (degree)

if cardinal_degree >= 0:
    print("north")


print(cardinal_degree)