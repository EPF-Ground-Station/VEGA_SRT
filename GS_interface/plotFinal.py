# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 09:06:24 2023

@author: lgtle
"""
import virgo

OBS_LAT = 46.5194
OBS_LON = 6.565
OBS_HEIGHT = 411.0

loc = (OBS_LAT, OBS_LON, OBS_HEIGHT)


obs = {
    'dev_args': 'rtl=0,bias=1',
    'rf_gain': 48,
    'if_gain': 25,
    'bb_gain': 18,
    'frequency': 1420e6,
    'bandwidth': 2.4e6,
    'channels': 2048,
    't_sample': 1,
    'duration': 60,
    'loc': loc,
    'ra_dec': '',
    'az_alt': ''
}

virgo.plot(obs_parameters=obs, n=20, m=35, f_rest=1420.4057517667e6,
           vlsr=False, dB=True, meta=False,
           obs_file='observation.dat', cal_file='calibration.dat',
           spectra_csv='spectrum.csv', plot_file='plot.png')
