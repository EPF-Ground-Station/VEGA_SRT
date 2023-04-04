import serial
from serial.tools import list_ports
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
import re
import argparse
import time

def name_input(name):
     object = SkyCoord.from_name(name)


def parse_star_coordinates():
    # Regular expression to validate the input format
    coord_pattern = re.compile(r'^[0-9]{1,2}\s[0-9]{1,2}\s[0-9]+\.[0-9]+$')

    def valid_coordinate(coord_str):
        if not re.match(coord_pattern, coord_str):
            raise argparse.ArgumentTypeError(f"Invalid coordinate format: {coord_str}")
        try:
            return float(coord_str)
        except ValueError:
            raise argparse.ArgumentTypeError(f"Invalid float value: {coord_str}")
        
    def valid_float(coord_str):
        try:
            return float(coord_str)
        except ValueError:
            raise argparse.ArgumentTypeError(f"Invalid float value: {coord_str}")

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', nargs=3, type=valid_float, metavar=('HH', 'MM', 'SS.SSSS'), help='Right Ascension (hh mm ss.ss)')
    parser.add_argument('-d', nargs=3, type=valid_float, metavar=('DD', 'MM', 'SS.SSSS'), help='Declination (dd mm ss.ss)')
    args = parser.parse_args()

    # Extracting the values from the input
    ra_hours, ra_minutes, ra_seconds = args.r
    dec_degrees, dec_minutes, dec_seconds = args.d


    print('Right ascension:', ra_hours, ra_minutes, ra_seconds)
    print('Declination:', dec_degrees, dec_minutes, dec_seconds)

    ra = 15*(ra_hours + ra_minutes/60 + ra_seconds/3600)
    dec = dec_degrees + dec_minutes /60 + dec_seconds / 3600

    return ra, dec


def transform_skycoord_to_AltAz(ra, dec):
    """
    Takes the star coordinates rightascension and declination as input and transforms them to altitude and azimuth coordinates. 

    :param obs_loc an instance of the class EarthLocation containing the informations about the location of the observator
    :param coords an instance of the class SkyCoord with coordinates corresponing to the input coordinates of the function
    :param altaz another instance of the class Skycoord but with the original coordinates transformed to the corresponing altitude and azimuth 
    :param coords_altaz string containing the Azimuth in the first position and Altitude in the second position. Both as decimal numbers

    """

    #object = SkyCoord.from_name('M33')
    obs_loc = EarthLocation(lat= 46.52457*u.deg , lon = 6.61650*u.deg, height = 500*u.m)
    time_now = Time.now() #+ 2*u.hour Don't need to add the time difference 
    coords = SkyCoord(ra*u.deg, dec*u.deg)
    altaz = coords.transform_to(AltAz(obstime = time_now, location = obs_loc))
    coords_altaz = altaz.to_string('decimal')
    print("Your Azimuth and Altitude coordinates are:")
    print(coords_altaz)
    #print(altaz.az)
    #print(altaz.alt)

    return (coords_altaz)
            
        
def send_coord(coord, ser):
            """
            Sends the Azimuth and Altitude coordinates calculated to the Teensy. 
        
            """
            
            DEBUG = True

            if DEBUG:
                print(coord)

            ser.write(coord.encode())
            print("wrote")

            # print(ser.readline().decode('utf-8'))
            # print("read line")

     
if __name__ == "__main__":
    #ra, dec = parse_star_coordinates()
    #print("Rightascencion as Decimal number = ", ra)
    #print("Declination as Decimal number = ", dec)
    #coords_altaz = transform_skycoord_to_AltAz(ra, dec)

    available_ports = []

    for port, desc_port, id in list_ports.comports():
        print(port)
        print(desc_port)
        if desc_port.find("Serial") > 0:
            print("port available")
            available_ports.append(port)

    if True:
        print("available_ports true")
        ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=None)

    try:
        ser.reset_input_buffer()
        while True:
            coords_altaz = transform_skycoord_to_AltAz(ra, dec)
            send_coord(coords_altaz, ser)
            print(coords_altaz)
            #time.sleep(1)
            print("wait for esp feedback")
            ser.read()
            ser.reset_input_buffer()
    except KeyboardInterrupt:
        # loop is interrupted with the command Ctrl + C
        print("Loop stopped by user.")
