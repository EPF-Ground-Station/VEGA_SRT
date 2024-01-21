# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 13:04:18 2023

This script, when imported into the Python interpreter, allows to use the Srt object in a dynamic way,
just as using a command-line interface to the SRT. Intended for admin use only since all method of SRT
are accessible without any security filtering.

For external/sensible usage, prefer the GUI remote operation interface.

When imported into a script, resolves all references to the library. Therefore, it can be very handy
for automated measurement campaign scripts.
"""
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, dir_path[:-8])

from lib_SRT.Srt import *

SRT = Srt("/dev/ttyUSB0", 115200, timeout=1)
