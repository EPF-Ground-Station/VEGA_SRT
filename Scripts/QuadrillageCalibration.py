from skyfield.api import load
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, ICRS, get_sun, get_body
from astropy import units as u




from SRT_inline import *

TS = load.timescale()  # Loads skyfield timescale
import math
import matplotlib.pyplot as plt

# la bonne fonction a utiliser ici est la fonction
# quadrillage plus correction
# il est nécessaire avant de l'uiliser d'ajuster les valeur de latitude longitude et hauteur de l'observateur

lati = 46.52457
long = 6.61650
haigt = 500


def RaDec2AzAlt(ra, dec, lati, long, height):
    """
    Utilitary method that transforms the input Right Ascension (RA) and Declination (Dec) coordinates to
    Azimuth (Az) and elevation (Alt) coordinates. AzAlt is computed taking into account the geolocation of VEGA,
    stored in global variables OBS_LAT, OBS_LON and OBS_HEIGHT.
    """

    obs_loc = EarthLocation(
        # lat=46.52457*u.deg, lon=6.61650*u.deg, height=500*u.m)
        lat=lati * u.deg, lon=long * u.deg, height=height * u.m)
    time_now = Time.now()  # + 2*u.hour Don't need to add the time difference
    coords = SkyCoord(ra * u.deg, dec * u.deg)
    altaz = coords.transform_to(AltAz(obstime=time_now, location=obs_loc))

    az, alt = [float(x) for x in altaz.to_string(
        'decimal', precision=4).split(' ')]

    return az, alt


def AzAlt2RaDec(az, alt, lati, long, height):
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
        lat=lati * u.deg, lon=long * u.deg, height=height * u.m)
    time_now = Time.now()  # + 2*u.hour Don't need to add the time difference
    altaz = AltAz(az=az * u.deg, alt=alt * u.deg,
                  obstime=time_now, location=obs_loc)
    coords = SkyCoord(altaz.transform_to(ICRS()))

    ra, dec = [float(x) for x in coords.to_string(
        decimal=True, precision=4).split(' ')]

    return ra, dec


def correction(ra, dec, correct_alt, correct_az):
    az, alt = RaDec2AzAlt(ra, dec, lati, long, haigt)
    corr_az = az + correct_az
    corr_alt = alt + correct_alt
    # correction qui garanti que l'angle obtenue est entre -90 et 90 degré (la altitude alt)
    while corr_alt > 90:
        corr_alt -= 180
    while corr_alt < -90:
        corr_alt += 180
    corr_ra, corr_dec = AzAlt2RaDec(corr_az, corr_alt, lati, long, haigt)
    return corr_ra, corr_dec


# Calcule la distance euclidienne entre deux points dans un plan 2D.

def distance_entre_points(x_centre, y_centre, x2, y2):
    return math.sqrt((x2 - x_centre) ** 2 + (y2 - y_centre) ** 2)


# fonction quadrillage qui a prend un nombre de point correspondnt au rayon du cercle dessiné par exemple 1 crée un cercle de 5 points
def quadrillage(nb_points, pas, ra_centre, dec_centre):
    if (nb_points >= 10):
        print("trop de pts")
        return
        # s'assure que le nombre de point est pair afin de pouvoir quadriller sous forme d'un carré
    # if(nb_points % 2 != 0):
    #     nb_points +=1
    if (pas == 0):
        print("le même point")
        return
    L = []
    # Boucle pour générer les coordonnées du quadrillage
    for y in range(-nb_points, nb_points + 1):

        for x in range(-nb_points, nb_points + 1):
            if (distance_entre_points(x, y, 0, 0) <= nb_points):
                # Calcul des coordonnées AzAlt en appliquant les correction
                corr_ra, corr_dec = correction(ra_centre, dec_centre, y * pas, x * pas)
                # Ajout des coordonnées à la liste
                L.append((corr_ra, corr_dec))

    return L


# fonction prenant en entrée des coordonnées de la potentielle correction(en alt az )
# pour effectuer un quadrillage centré en  cette zone
# est pris en entré le ra dec donné par une application donné par exemple stellarium et la correction a tester
# renvoie des données en ra dec
def quadrillage_plus_correction(nb_points, pas, ra_centre, dec_centre, correction_alt, correction_az):
    centre_effectif_en_ra, centre_en_dec = correction(ra_centre, dec_centre, correction_alt, correction_az)
    L = quadrillage(nb_points, pas, centre_effectif_en_ra, centre_en_dec)
    return L


def quadrillageSoleil(nb_points, pas, correction_alt, correction_az):

    SRT.connectAPM(False)

    observing_location = EarthLocation(lat=46.57 * u.deg, lon=7.65 * u.deg, height=600)

    if (nb_points >= 10):
        print("trop de pts")
        return
        # s'assure que le nombre de point est pair afin de pouvoir quadriller sous forme d'un carré
    # if(nb_points % 2 != 0):
    #     nb_points +=1
    if (pas == 0):
        print("le même point")
        return
    L = []
    # Boucle pour générer les coordonnées du quadrillage
    for y in range(-nb_points, nb_points + 1):

        for x in range(-nb_points, nb_points + 1):
            if (distance_entre_points(x, y, 0, 0) <= nb_points):
                # Calcul des coordonnées AzAlt en appliquant les correction

                observing_time = Time(datetime.utcnow(), scale='utc', location=observing_location)
                sun = get_body('sun', observing_time, observing_location)
                ra_sun = sun.ra.degree
                dec_sun = sun.dec.degree
                corr_ra, corr_dec = correction(ra_sun, dec_sun, correction_alt+ y * pas,correction_az+ x * pas)
                SRT.trackRaDec(corr_ra,corr_dec)

                SRT.observe(repo="SunCalib3", prefix=f"x={x}_y={y}_", duration=60)
                print(f"observing ({x},{y})")
                SRT.waitObs()
                SRT.stopTracking()
                # Ajout des coordonnées à la liste
                L.append((corr_ra, corr_dec))

    return L

quadrillageSoleil(7,1, -3.0, -2.0)