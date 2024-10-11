#!/usr/bin/env python3

import time
import matplotlib.pyplot as plt
from cued_ia_lego import *


# Try to find connected brick
try:
    brick = NXTBrick()
except Exception:
    exit()

# Set up motor
mA = Motor(brick, PORT_A, power=100, speedreg=False)
mA.reset_position()
mA.run()
motor_running = True

# Create empty lists for the readings and the times they were recorded
times = []
position_readings = []

# Display a message
print('Starting recording')


# Start time
t_start = time.perf_counter()
# Time to apply the brake
t_brake = t_start + 20
# Stop time
t_stop = t_start + 22
while time.perf_counter() < t_stop:
    # Append lists with current reading and time
    position_readings.append(mA.get_position())
    times.append(time.perf_counter() - t_start)
    # After 2.5 seconds, apply the brakes. This will only happen once,
    # because on the next iteration the motor will no longer be running.
    if motor_running and time.perf_counter() > t_brake:
        mA.idle()
        motor_running = False

# The brake is still applied at this point (try to turn the motor manually),
# consuming a lot of power, so now we will really turn it off
mA.idle()

# Get an estimate of the motor's rotation speed, by subtracting the previous
# position from the current position at each instance, and dividing by the
# time intervals
d_positions = diff(position_readings)
d_times = diff(times)
motor_speed = [0.0] + [d_positions[i] / d_times[i]
                       for i in range(len(d_times))]

# The speed estimate will be noisy - use a filter to smooth it
motor_speed = smooth(motor_speed, 0.05)

# Display a message
print('Stopping recording')

# Plot the results
plt.plot(times, position_readings, label='motor position')
plt.plot(times, motor_speed, label='motor speed')
plt.legend()
plt.grid(True)
plt.xlabel('time (s)')
plt.ylabel('motor position/speed')

# Display some information about the results
num_readings = len(position_readings)
print(f'The number of readings was: {num_readings}')
print(f'The recording rate (samples per second) was: {num_readings / 5 :.3f}')

print('Close the plot to finish')
plt.show()
