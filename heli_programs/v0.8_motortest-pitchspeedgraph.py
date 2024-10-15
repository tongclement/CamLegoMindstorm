#!/usr/bin/env python3

import time
import matplotlib.pyplot as plt
from cued_ia_lego import *
import csv


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
target_pitch_motor_absolute_angle = 0
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
t_brake = 29.7
t_stop = t_start + 29.7
motor_rotor.run(power=100)

for x in range(0,10):
    t_brake = x*10
    t_stop = t_start + x*10
    while time.perf_counter() < t_stop:
        position_readings.append(motor_rotor.get_position())
        times.append(time.perf_counter() - t_start)
        current_time_elapsed = time.perf_counter() - t_start
        # motor_rotor.run(power=int(current_time_elapsed / 5) * 20)
        motor_pitch.turn_to(x * 90)
        print(f"Time Elapse {current_time_elapsed}, Current Power Setting {int(current_time_elapsed / 5) * 20}")
    print(f"test of motor angle pitch {x*90}")
# Turn off the motor
motor_rotor.idle()
motor_armed = False

# Calculate rotation speed
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

target_pitch_motor_absolute_angle = -0
motor_pitch.turn_to(target_pitch_motor_absolute_angle)

# Display some information about the results
num_readings = len(position_readings)
print(f'The number of readings was: {num_readings}')
print(f'The recording rate (samples per second) was: {num_readings / 5:.3f}')

print('Close the plot to finish')
plt.show()

# Export to CSV
with open('motor_test_data_small_blade.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Time (s)', 'Motor Position', 'Motor Speed', 'Smoothed Motor Speed'])
    for i in range(len(times)):
        writer.writerow([times[i], position_readings[i], motor_speed[i], motor_speed[i]])

print('Data exported to motor_test_data.csv')