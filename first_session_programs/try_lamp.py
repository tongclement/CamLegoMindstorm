#!/usr/bin/env python3

import time
from cued_ia_lego import *


# Try to find connected brick
try:
    brick = NXTBrick()
except Exception:
    exit()

# Lamp connected to port A
lamp = Lamp(brick, PORT_A)

# Switch the lamp on
lamp.switch(on=True)

# Sleep for 5 seconds
time.sleep(5)

# Switch the lamp off
lamp.switch(on=False)
