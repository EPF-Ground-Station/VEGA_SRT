# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 21:40:19 2023

Script aimed at ensuring security of SRT by safety connexion-deconnexion

@author: lgtle
"""

from GS_interface.SRT_inline import *

SRT.connect(False)
SRT.disconnect()
