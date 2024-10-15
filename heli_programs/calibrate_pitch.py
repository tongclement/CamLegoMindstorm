#!/usr/bin/env python3

import pickle
import matplotlib.pyplot as plt
import numpy as np


# You need to edit the first two lines of this function, replacing the
# example data with actual data measured on your model. Start with the
# blades horizontal: this is the zero motor position. Then measure the
# blade angle for a number of different motor angles, covering the
# full range of motion you require in your lift experiment. The script
# fits cubic functions to both the forward and reverse mappings and
# saves the coefficients to file. This file is then loaded whenever we
# need to convert between motor angles and blade pitches.

# Measured blade angles in degrees
# (maybe rest a smartphone on the blades and use an app)
"""blade_angle = [-31, -25, -16, -7, -2, 7, 11, 18, 22.5, 29, 36, 42, 48,
               57, 68, 82]"""


#blade_angle = [0, 7, 13, 23, 35, 48, 60, 65, 82, 84]
#motor_angle = [0, -90, -180, -270, -360, -450, -540, -630, -720, -810]

blade_angle = [0, 4, 11, 15, 25, 35, 39, 48, 60, 66]
motor_angle = [0, -90, -180, -270, -360, -450, -540, -630, -720, -810]

"""
# Corresponding motor angles, in increments of 180 degrees
# (either write a program to drive the motor, or crank it manually)
motor_angle = [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
motor_angle = [180 * a for a in motor_angle]"""

# PitchToRotation cubic fit
pitch_to_rotation = np.polyfit(blade_angle, motor_angle, 3)
# Remove any offset - motor zero is defined as when the blades are horizontal
pitch_to_rotation[3] = 0

# RotationToPitch cubic fit
rotation_to_pitch = np.polyfit(motor_angle, blade_angle, 3)
# Remove any offset - motor zero is defined as when the blades are horizontal
rotation_to_pitch[3] = 0

# Save both sets of coefficients to a file in the current working directory
with open('angle_conversion.pickle', 'wb') as f:
    pickle.dump([pitch_to_rotation, rotation_to_pitch], f)

# Plot pitch_to_rotation
plt.figure(1)
x = np.linspace(min(blade_angle), max(blade_angle), 100)
y = [pitch_to_rotation[0] * p ** 3 +
     pitch_to_rotation[1] * p ** 2 +
     pitch_to_rotation[2] * p +
     pitch_to_rotation[3] for p in x]
plt.scatter(blade_angle, motor_angle)
plt.title('Motor angle vs Blade angle', fontweight='bold')
plt.xlabel('Blade Angle (deg)')
plt.ylabel('Motor Angle (deg)')
plt.plot(x, y)  # note offset is removed
plt.grid()

# Plot rotation_to_pitch
plt.figure(2)
x = np.linspace(min(motor_angle), max(motor_angle), 100)
y = [rotation_to_pitch[0] * r ** 3 +
     rotation_to_pitch[1] * r ** 2 +
     rotation_to_pitch[2] * r +
     rotation_to_pitch[3] for r in x]
plt.scatter(motor_angle, blade_angle)
plt.title('Blade angle vs Motor angle', fontweight='bold')
plt.xlabel('Motor Angle (deg)')
plt.ylabel('Blade Angle (deg)')
plt.plot(x, y)  # note offset is removed
plt.grid()

# Show plots
print('Close the plots to finish')
plt.show()
