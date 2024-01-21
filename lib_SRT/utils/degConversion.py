"""
Utilitary functions of conversion of different formats for angular degrees
"""


import math

def HMStoDeg(h,m,s):
    """Converts coordinates from time format (HH:MM:SS) to decimal degrees """
    return h*360/24+m*6/24+s/240

def DegtoHMS(deg):
    """Converts coordinates from decimal degrees to time format (HH:MM:SS) """
    h = math.trunc(deg/(360/24))
    m = math.trunc((deg-360/24*h)/(6/24))
    s = math.trunc((deg-h*360.0/24-m*6/24)/(1/240)*100)/100
    return (h,m,s)

def DMStoDeg(d,m,s):
    """Converts coordinates from hour degrees (DD:MM:SS) to decimal degrees """
    return d+m/60+s/3600

def DegtoDMS(deg):
    """Converts coordinates from decimal degrees to hour degrees (DD:MM:SS)"""
    d = math.trunc(deg)
    m = math.trunc((deg-d)*60)
    s = math.trunc((deg-d-m/60)*3600*100)/100
    return (d,m,s)