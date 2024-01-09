import math

destination_x =   39.6044273 
origin_x = 39.575384 
destination_y =  -105.0725764  
origin_y = -105.0620071 

    
cardinal_degree = (math.degrees(math.atan2(((destination_y)-(origin_y)),((destination_x)-(origin_x)))))


if cardinal_degree < 0:
    new_degree = cardinal_degree + 360
    print(new_degree)
else:
    print(cardinal_degree)