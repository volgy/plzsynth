#!/usr/bin/env python
import random
from time import sleep

from plzsynth import PLZPLLADF

start = 35e6    # start frequency in Hz
end = 88e6      # stop frequency in Hz
dwell_time = 1  # dwell time in seconds
gain = 4        # maximum gain

device = PLZPLLADF()
print(f"Using {device}")
print("Press Ctrl-C to stop")

while True:
    freq = random.uniform(start, end) #  select random frequency
    print(f"Freq: {freq / 1e6:.3f} MHz")

    device.start_tone(freq, gain)
    sleep(dwell_time)
    device.stop()
