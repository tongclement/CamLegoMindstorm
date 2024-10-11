#!/usr/bin/env python3

import time
import matplotlib.pyplot as plt
from cued_ia_lego import *


# Try to find connected brick
try:
    brick = NXTBrick()
except Exception:
    exit()

# Ultrasonic range sensor connected to sensor port 1
sensor = Ultrasonic(brick, PORT_1)

# Create empty lists for the readings and the times they were recorded
times = []
ultrasonic_readings = []

# Display a message
print('Starting recording')

# Start time
t_start = time.perf_counter()
# Stop time
t_stop = t_start + 20
while time.perf_counter() < t_stop:
    # Append lists with current reading and time
    ultrasonic_readings.append(sensor.get_distance())
    print(sensor.get_distance())
    times.append(time.perf_counter() - t_start)

# Display a message
print('Stopping recording')

# Plot the results
plt.plot(times, ultrasonic_readings)
plt.grid(True)
plt.xlabel('time (s)')
plt.ylabel('ultrasonic sensor reading')

# Display some information about the results
num_readings = len(ultrasonic_readings)
print(f'The number of readings was: {num_readings}')
print(f'The recording rate (samples per second) was: {num_readings / 5 :.3f}')

print('Close the plot to finish')
plt.show()
