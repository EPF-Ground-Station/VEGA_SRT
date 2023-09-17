# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 15:23:15 2023

@author: lgtle
"""

from skyfield.api import load
from SRT_inline import *
import time


SRT.connect()
sats = load.tle_file('lib/Beidou.tle')
iss = sats[6]

SRT.trackSat(iss)
time.sleep(120)
SRT.disconnect()
