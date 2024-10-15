#!/usr/bin/env python3

import pickle
import time
import statistics
import numpy as np
import matplotlib.pyplot as plt
from cued_ia_lego import *


# You need to add a range of masses to the counterweight side of the
# see-saw at roughly the same distance from the pivot as the centre of
# the blades. The masses should range from zero up to the maximum lift
# force you anticipate measuring. For convenience, we suggest that the
# first mass is a Lego axle and the remaining are gear wheels that you
# can slot onto the axle. Edit the first line of the program to
# specify the actual mass increments you will be using, starting from
# zero. Two examples are given, decide which you prefer and comment
# out the other one.

# In this example, we just add masses one by one
mass_changes = [0.0,1.5,3.55,3.55,3.55,3.55]  # grams
mass_changes = [(160/200) * a for a in mass_changes]
# Moments Conversion - equivalent moment if placed at the same distance from the pivot to the center of the blades

# In this example, we add masses and then take them off
# Why might this be better?
# mass_changes = [0.0, 1.5, 1.186, 1.186, 1.186, 1.186, -1.186, -1.186,
#                 -1.186, -1.186, -1.5]  # grams

average_readings = []  # results list, initially empty
masses = []            # mass list
initial_mass = 0       # initial mass
reading_duration = 1   # light sensor recording duration (seconds)

# Try to find connected brick
try:
    brick = NXTBrick()
except Exception:
    exit()

# Light sensor connected to sensor port 1, LED active
light = Light(brick, PORT_1, illuminated=True)

# Prepare figure window
plt.figure(3)
plt.clf()
plt.xlim(0, 1000)
plt.ylim(-5, 40)

# Main loop over test masses
for mass_change in mass_changes:
    # Work out current test mass by summing increments
    masses.append(masses[-1] + mass_change if masses else initial_mass)

    # Display instructions and wait for the user to press enter
    print(f'Apply a {mass_change} gram increment '
          f'({masses[-1]} grams in total)')
    print('Wait for see-saw to settle')
    input('Then press Enter to continue...')
    print('')

    # Record the light sensor readings for the specified duration
    light_readings = []
    t_start = time.perf_counter()
    while time.perf_counter() < t_start + reading_duration:
        light_readings.append(light.get_lightness())
    average_readings.append(statistics.mean(light_readings))

    # Plot the recorded data
    plt.clf()
    plt.ylabel('Mass (g)')
    plt.xlabel('Light sensor reading')
    plt.title('Mass vs light sensor reading', fontweight='bold')
    plt.xlim(0, 1000)
    plt.ylim(-5, 40)
    plt.plot(average_readings, masses, 'rx')
    plt.pause(0.1)  # forces the figure to draw now

# Power down LED
light.set_illuminated(False)

# Fit a quadratic function to the data
force_conversion = np.polyfit(average_readings, masses, 2)

# Save the coefficients to a file in the current working directory
with open('force_conversion.pickle', 'wb') as f:
    pickle.dump(force_conversion, f)

# Plot the fitted quadratic
x = np.linspace(0, 1000, 100)
y = [force_conversion[0] * l ** 2 +
     force_conversion[1] * l +
     force_conversion[2] for l in x]
plt.plot(x, y, 'b')
plt.grid()

print('Close the plot to finish')
plt.show()