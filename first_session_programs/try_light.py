#!/usr/bin/env python3

import time
import matplotlib.pyplot as plt
from cued_ia_lego import *


# Try to find connected brick
try:
    brick = NXTBrick()
except Exception:
    exit()

# Light sensor connected to sensor port 1
# Turn LED on
sensor = Light(brick, PORT_1, illuminated=False)

# Create empty lists for the readingss and the times they were recorded
times = []
light_readings = []

# Display a message
print('Starting recording')

# Start time
t_start = time.perf_counter()
# Stop time
t_stop = t_start + 5
while time.perf_counter() < t_stop:
    # Append lists with current reading and time
    light_readings.append(sensor.get_lightness())
    times.append(time.perf_counter() - t_start)

# Turn off LED
sensor.set_illuminated(False)

# Display a message
print('Stopping recording')

# Plot the results
plt.plot(times, light_readings)
plt.grid(True)
plt.xlabel('time (s)')
plt.ylabel('light sensor reading')

# Display some information about the results
num_readings = len(light_readings)
print(f'The number of readings was: {num_readings}')
print(f'The recording rate (samples per second) was: {num_readings / 5 :.3f}')

print('Close the plot to finish')
plt.show()
