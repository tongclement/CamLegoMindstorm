#!/usr/bin/env python3
import math
import matplotlib.pyplot as plt
import time

x = [i / 100 for i in range(0, 630)]
y = [math.sin(i / 100) for i in range(0, 630)]
plt.plot(x, y)
plt.grid(True)
plt.xlabel('x')
plt.ylabel('sin(x)')
print('Close the plot to finish')
plt.show()

i = 0
t_start = time.perf_counter()
t_stop = time.perf_counter() + 5
print(f'The start time was {t_start:.0f} seconds')
while time.perf_counter() < t_stop:
	i = i + 1
print(f'The number of iterations per second was {i / 5 :.2f}')

