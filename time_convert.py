import datetime
import time
from datetime import timedelta
year = int(input("Enter a year: "))
month = int(input("Enter a month: "))
day = int(input("Enter a day: "))
hours = int(input("Enter the hour: "))
minutes = int(input("Enter the minutes: "))
seconds = int(input("Enter the seconds: "))

green_time = datetime.datetime(year, month, day, hours, minutes, seconds)
#print("Given Date:", green_time)
# print("UNIX timestamp:", (time.mktime(green_time.timetuple())))

#print("Enter desired time of arrival. ")
year1 = int(input("Enter a year: "))
month1 = int(input("Enter a month: "))
day1 = int(input("Enter a day: "))
hours1 = int(input("Enter the hour: "))
minutes1 = int(input("Enter the minutes: "))
seconds1 = int(input("Enter the seconds: "))

arrival_time = datetime.datetime(year1, month1, day1, hours1, minutes1, seconds1)
#print("Given Date:", arrival_time)

between_time = arrival_time - green_time
print(between_time)

seconds = timedelta.total_seconds(between_time)
print(seconds)