#!/usr/bin/env python3

import time
import matplotlib.pyplot as plt
from cued_ia_lego import *


# Try to find connected brick
try:
    brick = NXTBrick()
except Exception:
    exit()

# Touch sensor connected to sensor port 1
sensor = Touch(brick, PORT_1)

# Create empty lists for the readings and the times they were recorded
times = []
touch_readings = []

# Display a message
print('Starting recording')

# Start time
t_start = time.perf_counter()
# Stop time
t_stop = t_start + 5
while time.perf_counter() < t_stop:
    # Append lists with current reading and time
    touch_readings.append(1 if sensor.is_pressed() else 0)
    times.append(time.perf_counter() - t_start)

# Display a message
print('Stopping recording')

# Plot the results as a continuous line and also discrete points
plt.plot(times, touch_readings)
plt.plot(times, touch_readings, 'x')
plt.grid(True)
plt.xlabel('time (s)')
plt.ylabel('touch sensor reading')

# Display some information about the results
num_readings = len(touch_readings)
print(f'The number of readings was: {num_readings}')
print(f'The recording rate (samples per second) was: {num_readings / 5 :.3f}')

print('Close the plot to finish')
plt.show()
