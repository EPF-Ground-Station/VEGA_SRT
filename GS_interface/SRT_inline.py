# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 13:04:18 2023

Import this script to python interpreter to use all methods of SRT, configured
for EPFL SRT
"""

from lib.library_GS import *

SRT = Srt("/dev/ttyUSB0", 115200, 1)
