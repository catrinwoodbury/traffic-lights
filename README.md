## traffic-lights


## To add waypoints to route
Find the nearest location by drive time

We want to dispatch the nearest technician to the customer location. To do that, we’ll parse the distance matrix JSON to find the shortest drive time.


Add this code after the console.log of the Distance Matrix callback:

let routes = response.rows[0].elements;
          const leastseconds = 86400; // 24 hours
          let drivetime = "";
          let closest = "";
​
          for (let i=0; i<routes.length; i++) {
            const routeseconds = routes[i].elements[0].duration.value;
            if (routeseconds > 0 && routeseconds < leastseconds) {
              leastseconds = routeseconds; // this route is the shortest (so far)
              drivetime = routes[i].elements[0].duration.text; // hours and minutes
              closest = response.originAddresses[i]; // city name from destinations
            }
          }
          alert("The closest location is " + closest + " (" + drivetime + ")");


### for each lat long calc distance from poly line
if distance is less than (a value) add lat long to waypoints array

## https://stackoverflow.com/questions/45924890/get-distance-along-polyline-from-lat-lng-point