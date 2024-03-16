import keyboard
from datetime import datetime

i =1
while i <= 10:
    while True:
        if keyboard.read_key() == "1":
            start_time = datetime.now()
            break
    while True:
        if keyboard.read_key() == "2":
            red_turn = datetime.now()
            green_time = red_turn - start_time
            break
    while True:
        if keyboard.read_key() == "3":
            end_time = datetime.now()
            red_time = end_time - red_turn
            break
    i = i + 1
