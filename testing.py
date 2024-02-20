import keyboard
from datetime import datetime

while True:
    if keyboard.read_key() == "1":
        green_turn1 = datetime.now()
        print("The light turned green at ", green_turn1)
        break
while True:
    if keyboard.read_key() == "2":
        red_turn = datetime.now()
        print(red_turn)
        green_time = red_turn - green_turn1
        print("green time: ", green_time)
        break
while True:
    if keyboard.read_key() == "3":
        green_turn2 = datetime.now()
        print(green_turn2)
        red_time = green_turn2 - red_turn
        print("red time: ", red_time)
        break
    
12