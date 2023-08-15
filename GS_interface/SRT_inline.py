# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 13:04:18 2023

Import this script to python interpreter to use all methods of SRT, configured
for EPFL SRT
"""

from lib.library_GS import *
import time

SRT = Srt("/dev/ttyUSB0", 115200, 1)
time1 = time.time_ns()
SRT.getAlt()
diff = time.time_ns() - time1
print(f"Time elapsed for getAlt : {diff}")
