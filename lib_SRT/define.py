"""Definition of parameters used when instantiating the SRT object"""

import os
from skyfield.api import Topos



NORTH = 990000
TRACKING_RATE = 0.1  # Necessary delay for sending point_to to APM while tracking
PING_RATE = 60  # Ping every minute
DATA_PATH = "/mnt/PhData/dev/RadioData/"  # Finds data dir of user
DATA_PATH_STUDENT = "/mnt/PhData/TP3_SMR/TP/"
TLE_PATH = os.path.expanduser("~") + "/TLEs/"
OBS_LAT = 46.5194444
OBS_LON = 6.565
OBS_HEIGHT = 411.0
LOC = (OBS_LAT, OBS_LON, OBS_HEIGHT)
TOPOS_LOC = Topos(OBS_LAT, OBS_LON, OBS_HEIGHT)
# Delay used to point to future location of sat before tracking
SAT_INITIAL_DELAY = 15