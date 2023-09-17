# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 15:23:15 2023

@author: lgtle
"""

from skyfield.api import load
from SRT_inline import *
import time


SRT.connect()
sats = load.tle_file('lib/ISS.tle')
iss = sats[0]

SRT.trackSat(iss)

f = open("logISS.txt", "w")

for i in range(240):
    time.sleep(1)
    az, alt = SRT.getAzAlt()

    timeStamp(f"{az}, {alt}", f)

f.close()
SRT.disconnect()
