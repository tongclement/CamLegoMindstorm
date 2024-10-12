#!/usr/bin/env python3

import time
import matplotlib.pyplot as plt
from cued_ia_lego import *


# Try to find connected brick
try:
    brick = NXTBrick()
except Exception:
    exit()

# Set up rotor motor
#motor_rotor = Motor(brick, PORT_A, power=100, speedreg=True, smoothstart=True, brake=False) #Speedreg is normally True
motor_rotor = Motor(brick, PORT_A, power=100, speedreg=False, smoothstart=True, brake=False) #Speedreg is normally True
motor_rotor.reset_position()

# Set up pitch motor position
motor_pitch = Motor(brick, PORT_B, power=40, speedreg=True,
                    smoothstart=True, brake=True) #Note: If motor needs to be inverted, set the power to negative
motor_pitch.reset_position()
pitch_abs_pos = 0
target_pitch_motor_absolute_angle=-00
#gear ratio: 16:24 - but irrelevant as you also need to calculate the 2 bar lift if you want to do it mathematically
motor_pitch.turn_to(target_pitch_motor_absolute_angle) # absolute degrees of motor rotation - call this line of code anywhere anytime to change the pitch

#time.sleep(3)

motor_rotor.run()
motor_armed = True #set to False for emergency stop, originally named motor_running

# Create empty lists for the readings and the times they were recorded
times = []
position_readings = []

# Display a message
print('Starting recording')

#Set Pitch to desired position (initially pitch should be manually pushed to he bottom-most position)
# Interrupt any currently active pitch adjustment
motor_pitch.brake()


# program setting that configures how long the helicopter running
# Start time
t_start = time.perf_counter()

# Time to apply the brake
t_brake = t_start + 42
# Stop time
t_stop = t_start + 45


while time.perf_counter() < t_stop:
    # Append lists with current reading and time
    position_readings.append(motor_rotor.get_position())
    times.append(time.perf_counter() - t_start)

    current_time_elapsed = time.perf_counter()-t_start
    motor_rotor.run(power=int(current_time_elapsed/5)*20)
    print(f"Time Elapse {current_time_elapsed}, Current Power Setting {int(current_time_elapsed/7)*20}")

    # After 2.5 seconds, apply the brakes. This will only happen once,
    # because on the next iteration the motor will no longer be running.
    if motor_armed and time.perf_counter() > t_brake:
        motor_rotor.idle()
        motor_armed = False


# The brake is still applied at this point (try to turn the motor manually),
# consuming a lot of power, so now we will really turn it off
motor_rotor.idle()

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
