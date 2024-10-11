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
sensor = Light(brick, PORT_1, illuminated=True)

# Set up motor
mA = Motor(brick, PORT_A)
mA.reset_position()

# Create empty list for the light sensor readings
light_readings = []

# Start motor
mA.turn(1000, power=40, brake=True)

# Start time
t_start = time.perf_counter()
# Keep iterating while the motor is running
while not mA.is_ready():
    # Append list with current reading
    light_readings.append(sensor.get_lightness())
    print(sensor.get_lightness())
# Stop time
t_stop = time.perf_counter()

# Turn off LED
sensor.set_illuminated(False)

# Move the motor back to its starting position
mA.turn_to(0, power=100, brake=True)
mA.wait_for()

# Set the threshold for black/white discrimination
thresh = 250

# Plot the light sensor readings and the threshold
plt.subplot(2, 1, 1)
plt.plot(light_readings)
plt.plot([thresh for i in light_readings], 'g--')
plt.grid(True)

# On a second graph, display the detected bar code
plt.subplot(2, 1, 2)
# Generate the barcode
barcode = [[int(reading > thresh) for reading in light_readings], ] * 2
plt.imshow(barcode, cmap='gray', aspect='auto')
plt.axis('off')

# Display some information about the results
num_readings = len(light_readings)
print(f'The number of readings was: {num_readings}')
print(f'The recording rate (samples per second) was: {num_readings / (t_stop - t_start) :.3f}')

print('Close the plot to finish')
plt.show()
