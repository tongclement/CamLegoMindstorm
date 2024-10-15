
#!/usr/bin/env python3

import time
import numpy as np
import matplotlib.pyplot as plt
from cued_ia_lego import *

# Try to find connected brick
try:
    brick = NXTBrick()
except Exception:
    exit()


# Set up pitch motor position
motor_pitch = Motor(brick, PORT_B, power=40, speedreg=True, smoothstart=True, brake=True)
motor_pitch.reset_position()

pitches = {}

for x in range(0,10):
    motor_pitch.turn_to(-x*90)
    print(f"Motor Angle = {-x*90}")
    this_angle = int(input("Blade Angle"))
    pitches.update({-x*90:this_angle})
    #time.sleep(10)

print(f"Motor Angle List {pitches.keys()}")
print(f"Pitch Angle List {pitches.values()}")