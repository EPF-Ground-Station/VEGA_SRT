# -*- coding: utf-8 -*-
"""
Created on Sun Aug 20 16:01:42 2023

@author: lgtle
"""
import virgo
import os
from SRT_inline import *

OBS_LAT = 46.5194
OBS_LON = 6.565
OBS_HEIGHT = 411.0

loc = (OBS_LAT, OBS_LON, OBS_HEIGHT)

repo = "Tests"
obs = "TestVirgo"

if not os.path.isdir(DATA_PATH + repo):
    os.mkdir(DATA_PATH + repo)     # if not, create it

repo = DATA_PATH + repo + '/'

# If no indicated observation name
if obs == None:
    # Make the name to current timestamp
    obs = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# Check if there exists a repo at this name
if not os.path.isdir(repo + obs):
    os.mkdir(repo + obs)     # if not, create it

obs = obs + '/'
path = repo+obs

SRT.connect(False)
SRT.trackGal(100.7075, 65.32)  # Moves to calibration target
obs = {
    'dev_args': '',
    'rf_gain': 480,
    'if_gain': 0,
    'bb_gain': 0,
    'frequency': 1420e6,
    'bandwidth': 2.4e6,
    'channels': 2048,
    't_sample': 1,
    'duration': 60,
    'loc': loc,
    'ra_dec': '',
    'az_alt': ''
}

# avg_ylim=(-5,15), cal_ylim=(-20,260), rfi=[(1419.2e6, 1419.3e6), (1420.8e6, 1420.9e6)]

virgo.observe(obs_parameters=obs, obs_file=path+'calibration.dat')

SRT.trackGal(84.29, 2)  # Moves to Deneb

virgo.observe(obs_parameters=obs, obs_file=path+'observation.dat')

virgo.plot(obs_parameters=obs, n=20, m=35, f_rest=1420.4057517667e6,
           vlsr=False, dB=True, meta=False,
           obs_file=path+'observation.dat', cal_file=path+'calibration.dat',
           spectra_csv=path+'spectrum.csv', plot_file=path+'plot.png')

SRT.disconnect()
