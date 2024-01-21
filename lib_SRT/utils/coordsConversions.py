
from ..define import *
from skyfield.api import load
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, ICRS
from astropy import units as u
TS = load.timescale()   # Loads skyfield timescale
def RaDec2AzAlt(ra, dec):
    """
    Utilitary method that transforms the input Right Ascension (RA) and Declination (Dec) coordinates to
    Azimuth (Az) and elevation (Alt) coordinates. AzAlt is computed taking into account the geolocation of VEGA,
    stored in global variables OBS_LAT, OBS_LON and OBS_HEIGHT.

    :param ra: Input RA coordinate in decimal hours
    :type ra: float
    :param dec: Input Dec coordinate in decimal degrees
    :type dec: float
    :return: Converted AzAlt coordinates
    :rtype: (float,float)
    """

    obs_loc = EarthLocation(
        # lat=46.52457*u.deg, lon=6.61650*u.deg, height=500*u.m)
        lat=OBS_LAT*u.deg, lon=OBS_LON * u.deg, height=OBS_HEIGHT*u.m)
    time_now = Time.now()  # + 2*u.hour Don't need to add the time difference
    coords = SkyCoord(ra*u.deg, dec*u.deg)
    altaz = coords.transform_to(AltAz(obstime=time_now, location=obs_loc))

    az, alt = [float(x) for x in altaz.to_string(
        'decimal', precision=4).split(' ')]

    return az, alt


def AzAlt2RaDec(az, alt):
    """
    Utilitary method that transforms the input Azimuth (Az) and Elevation (Alt) coordinates to
    Right Ascension (RA) and Declination (Dec) coordinates. AzAlt is computed taking into account the geolocation of VEGA,
    stored in global variables OBS_LAT, OBS_LON and OBS_HEIGHT.

    :param az: Input Az coordinate in decimal degrees
    :type az: float
    :param alt: Input Alt coordinate in decimal degrees
    :type alt: float
    :return: Converted RaDec coordinates
    :rtype: (float,float)
    """

    obs_loc = EarthLocation(
        # lat=46.52457*u.deg, lon=6.61650*u.deg, height=500*u.m)
        lat=OBS_LAT*u.deg, lon=OBS_LON * u.deg, height=OBS_HEIGHT*u.m)
    time_now = Time.now()  # + 2*u.hour Don't need to add the time difference
    altaz = AltAz(az=az*u.deg, alt=alt*u.deg,
                  obstime=time_now, location=obs_loc)
    coords = SkyCoord(altaz.transform_to(ICRS()))

    ra, dec = [float(x) for x in coords.to_string(
        decimal=True, precision=4).split(' ')]

    return ra, dec


def Gal2AzAlt(long, b):
    """
    Utilitary method that transforms the input galactic longitude (long) and latitude (b) coordinates to
    Azimuth (Az) and elevation (Alt) coordinates. AzAlt is computed taking into account the geolocation of VEGA,
    stored in global variables OBS_LAT, OBS_LON and OBS_HEIGHT.

    :param long: Input long coordinate in decimal hours
    :type long: float
    :param b: Input b coordinate in decimal degrees
    :type b: float
    :return: Converted AzAlt coordinates
    :rtype: (float,float)
    """

    obs_loc = EarthLocation(
        # lat=46.52457*u.deg, lon=6.61650*u.deg, height=500*u.m)
        lat=OBS_LAT*u.deg, lon=OBS_LON * u.deg, height=OBS_HEIGHT*u.m)
    time_now = Time.now()
    coords = SkyCoord(long*u.deg, b*u.deg)
    altazFrame = coords.transform_to(AltAz(obstime=time_now, location=obs_loc))

    galactic_coords = SkyCoord(
        l=long*u.deg, b=b*u.deg, frame='galactic')

    azalt_coords = galactic_coords.transform_to(altazFrame)

    az, alt = [float(x) for x in azalt_coords.to_string(
        'decimal', precision=4).split(' ')]

    return az, alt


def AzAlt2Gal(az, alt):
    """
    Utilitary method that transforms the input Azimuth (Az) and Elevation (Alt) coordinates to galactic longitude (long)
    and latitude (b) coordinates. AzAlt is computed taking into account the geolocation of VEGA,
    stored in global variables OBS_LAT, OBS_LON and OBS_HEIGHT.

    :param az: Input Az coordinate in decimal degrees
    :type az: float
    :param alt: Input Alt coordinate in decimal degrees
    :type alt: float
    :return: Converted galactic coordinates
    :rtype: (float,float)
    """

    obs_loc = EarthLocation(
        # lat=46.52457*u.deg, lon=6.61650*u.deg, height=500*u.m)
        lat=OBS_LAT*u.deg, lon=OBS_LON * u.deg, height=OBS_HEIGHT*u.m)
    time_now = Time.now()

    altaz = AltAz(az=az*u.deg, alt=alt*u.deg,
                  obstime=time_now, location=obs_loc)
    g = SkyCoord(0, 0, unit='rad', frame='galactic')
    coords = SkyCoord(altaz.transform_to(g))

    long, b = [float(x) for x in coords.to_string(
        decimal=True, precision=4).split(' ')]

    return long, b


def TLE2AzAlt(tle, delay=0):
    """Returns az and alt position of sat at current time given TLE

    :param tle: The target satellite TLE
    :type tle: ? TODO: find this
    :param delay: Delay in seconds to introduce in the TLE propagation in order to ope with the slew duration to
    the tracking path
    :type delay: float
    :return: The converted AzAlt coordinates
    :rtype: (float, float)
    """

    t = TS.now()
    if delay != 0:
        t = t.utc
        t = TS.utc(t.year, t.month, t.day, t.hour, t.minute, t.second+delay)

    pos = (tle - TOPOS_LOC).at(t).altaz()

    return pos[1].degrees, pos[0].degrees
