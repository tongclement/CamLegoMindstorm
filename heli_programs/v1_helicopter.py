#!/usr/bin/env python3

import os.path
import pickle
import time
import statistics
import numpy as np
import matplotlib.pyplot as plt
from cued_ia_lego import *


# This is the main script for the helicopter experiment. Edit the
# parameters at the top of the file to try different blade pitch angles,
# fan speeds etc. Make sure the blades are horizontal before running.

# Blade angles to test
test_angles = [0, 10, 20, 30, 40, 50, 60, 70, 80]  # (degrees)
# Time to spin blades for each test
test_duration = 10  # (seconds)
# Time to record data, in this example between 50% and 90% of the way through
# the test_duration
recording_window = [0.5, 0.9]
# Time to wait between tests
inter_test_pause = 3  # (seconds)
# Power of the pitch changing motor, you may need to change the sign depending
# on how your motor is mounted
pitch_power = -40
# Power of the fan (blade spinning) motor
fan_power = 100

# Check if angle conversion data exists, run blade pitch calibration if not
if os.path.isfile('angle_conversion.pickle'):
    with open('angle_conversion.pickle', 'rb') as f:
        angle_conversion = pickle.load(f)
    pitch_to_rotation = angle_conversion[0]
    rotation_to_pitch = angle_conversion[1]
else:
    print('Please run the calibrate_pitch.py script first')
    exit()

# Check if force conversion data exists, run lift calibration if not
if os.path.isfile('force_conversion.pickle'):
    with open('force_conversion.pickle', 'rb') as f:
        force_conversion = pickle.load(f)
else:
    print('Please run the calibrate_lift.py script first')
    exit()

# Try to find connected brick
try:
    brick = NXTBrick()
except Exception:
    exit()

# Light sensor connected to sensor port 1, LED active
light = Light(brick, PORT_1, illuminated=True)

# Set up parameters for the blade fan motor
motor_fan = Motor(brick, PORT_A, power=fan_power, speedreg=True,
                  smoothstart=True)

# Set up parameters for the blade pitch motor
motor_pitch = Motor(brick, PORT_B, power=pitch_power, speedreg=True,
                    smoothstart=True, brake=True)

# Main loop over tests, start timer, reset state variables
results = [[], [], []]

num_tests = len(test_angles)
current_test = 0

motor_pitch.reset_position()
pitch_abs_pos = 0

while current_test < num_tests:
    # Interrupt any currently active pitch adjustment
    motor_pitch.brake()

    # Set blade pitch angle
    target_angle = test_angles[current_test]
    target_motor_position = (pitch_to_rotation[0] * target_angle ** 3 +
                             pitch_to_rotation[1] * target_angle ** 2 +
                             pitch_to_rotation[2] * target_angle +
                             pitch_to_rotation[3])
    motor_adjustment = target_motor_position - pitch_abs_pos
    motor_pitch.turn(round(motor_adjustment))

    # Wait for the inter-test pause, then spin up the blades
    time.sleep(inter_test_pause)
    motor_fan.run()

    # During the recording window, record the current time, motor positions
    # and light sensor readings
    test_start = time.perf_counter()
    times = []
    pitch_positions = []
    light_readings = []
    fan_positions = []
    while time.perf_counter() < test_start + test_duration:
        if (test_start + recording_window[0] * test_duration) < time.perf_counter() < \
           (test_start + recording_window[1] * test_duration):
            times.append(time.perf_counter())
            pitch_pos = motor_pitch.get_position()
            pitch_abs_pos = pitch_pos if pitch_power >= 0 else -pitch_pos
            pitch_positions.append(pitch_abs_pos)
            light_readings.append(light.get_lightness())
            fan_positions.append(motor_fan.get_position())

    # Stop the blade fan motor, record the mean pitch angle, mean light sensor
    # reading and mean fan motor speed
    motor_fan.idle()
    results[0].append(statistics.mean(pitch_positions))
    results[1].append(statistics.mean(light_readings))
    results[2].append((fan_positions[-1] - fan_positions[0]) /
                      (times[-1] - times[0]))
    current_test += 1

# Return blades to starting angle
if not motor_pitch.is_ready():
    motor_pitch.brake()
    motor_pitch.wait_for()
motor_pitch.turn_to(0)
motor_pitch.wait_for()
motor_pitch.idle()

# Power down LED
light.set_illuminated(False)

# Convert pitch motor positions to degrees
pitch = [rotation_to_pitch[0] * p ** 3 +
         rotation_to_pitch[1] * p ** 2 +
         rotation_to_pitch[2] * p +
         rotation_to_pitch[3] for p in results[0]]

# Convert light sensor readings to lift in Newtons
g = 0.00980665
lift = [g * (force_conversion[0] * l ** 2 +
             force_conversion[1] * l +
             force_conversion[2]) for l in results[1]]

# Estimate the lift at zero pitch, deviations from zero are caused mainly by:
# (a) calibration errors/drift, or
# (b) the blades not being horizontal at the start of the run.
_, _, offset = np.polyfit(pitch, lift, 2)
# Remove any nonzero offset
# (or comment out this line of code if you would prefer not to)
lift = [l - offset for l in lift]

# Plot lift vs pitch
plt.figure(1)
plt.clf()
plt.plot(pitch, lift)
plt.ylabel('Lift (N)')
plt.xlabel('Pitch angle (deg)')
plt.title('Lift vs Pitch', fontweight='bold')
plt.grid()

# Plot speed vs pitch
plt.figure(2)
plt.clf()
plt.plot(pitch, results[2])
plt.ylabel('Motor speed (deg/sec)')
plt.xlabel('Pitch angle (deg)')
plt.title('Speed vs Pitch', fontweight='bold')
plt.grid()

print('Close the plots to finish')
plt.show()
