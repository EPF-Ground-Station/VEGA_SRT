# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 15:23:15 2023

@author: lgtle
"""

from SRT_inline import *
import time


def timeStamp(message, file=None):
    #
    # This function provides a standard time-stamped output statement
    #
    timeStamp = time.strftime("[%H:%M:%S]")
    print(timeStamp, message, file=file)


SRT.connect(False)
sats = load.tle_file('lib/Beidou.tle')
iss = sats[6]
print(iss)

SRT.trackSat(iss)

f = open("logBeidou.txt", "w")

for i in range(240):
    time.sleep(1)
    az, alt = SRT.getAzAlt()

    timeStamp(f"{az}, {alt}", f)

f.close()

# time.sleep(120)
SRT.disconnect()
