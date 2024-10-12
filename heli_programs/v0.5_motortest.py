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

# Set up rotor motor
motor_rotor = Motor(brick, PORT_A, power=100, speedreg=False, smoothstart=True, brake=False)
motor_rotor.reset_position()

# Set up pitch motor position
motor_pitch = Motor(brick, PORT_B, power=40, speedreg=True, smoothstart=True, brake=True)
motor_pitch.reset_position()
target_pitch_motor_absolute_angle = -400
motor_pitch.turn_to(target_pitch_motor_absolute_angle)

motor_rotor.run()
motor_armed = True

# Create empty lists for the readings and the times they were recorded
times = []
position_readings = []

# Display a message
print('Starting recording')

# Interrupt any currently active pitch adjustment
motor_pitch.brake()

# Start time
t_start = time.perf_counter()
# Stop time
t_brake=29.7
t_stop = t_start + 29.7

while time.perf_counter() < t_stop:
    position_readings.append(motor_rotor.get_position())
    times.append(time.perf_counter() - t_start)
    if motor_armed and time.perf_counter() > (t_brake):
        motor_rotor.idle()
        motor_armed = False

    current_time_elapsed = time.perf_counter() - t_start
    motor_rotor.run(power=int(current_time_elapsed / 5) * 20)
    print(f"Time Elapse {current_time_elapsed}, Current Power Setting {int(current_time_elapsed / 5) * 20}")



# Turn off the motor
motor_rotor.idle()

# Calculate rotation speed
d_positions = np.diff(position_readings)
d_times = np.diff(times)
motor_speed = np.zeros(len(d_times) + 1)  # Initialize motor speed array
motor_speed[1:] = d_positions / d_times  # Populate with speed values

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
print(f'The recording rate (samples per second) was: {num_readings / 5:.3f}')

print('Close the plot to finish')
plt.show()

# Export to CSV
import pandas as pd

data = {
    'Time (s)': times,
    'Motor Position': position_readings,
    'Motor Speed': motor_speed
}

df = pd.DataFrame(data)
df.to_csv('motor_test_data.csv', index=False)
print('Data exported to motor_test_data.csv')