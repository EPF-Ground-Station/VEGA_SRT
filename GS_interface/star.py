import serial
from serial.tools import list_ports
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
import re
import argparse

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

    object = SkyCoord.from_name('M33')
    obs_loc = EarthLocation(lat= 46.52457*u.deg , lon = 6.61650*u.deg, height = 500*u.m)
    time_now = Time.now() #+ 2*u.hour Don't need to add the time difference 
    coords = SkyCoord(ra*u.deg, dec*u.deg)
    altaz = coords.transform_to(AltAz(obstime = time_now, location = obs_loc))
    print("Your Azimuth and Altitude coordinates are:")
    print(altaz.az)
    print(altaz.alt)

    return (altaz.az, altaz.alt)
            
        
def send_coord(coord):
            """
            Sends the TLE of the satelite selected to the Teensy which triggers the telescope to follow the specific satelite
            This code will only function if exactly one teensy is connected to the computer and thus available_ports contains one element.
            A serial port is characterized by the fact that one bit is sent at a time and the bits are sent in serie, which is how microprocessors work. 
            list_ports.comports lists all available ports of the computer
        
            :param available_ports : contains all the serial ports of the computer
            """
            available_ports = []

            DEBUG = True

            for port, desc_port, id in list_ports.comports():
                print(port)
                print(desc_port)
                if desc_port.find("Serial") > 0:
                    print("port available")
                    available_ports.append(port)

            if DEBUG:
                print(coord)
        
            if True:
                print("available_ports true")
                ser = serial.Serial("/dev/ttyACM0", 115200)
                ser.write(coord.encode())
                print("wrote")

            print(ser.readline().decode('utf-8'))
            print("read line")

        
        
if __name__ == "__main__":       
    ra, dec = parse_star_coordinates()
    #ra = 12.3
    #dec = 13.5
    print("Rightascencion as Decimal number = ", ra)
    print("Declination as Decimal number = ", dec)
    #az, alt = transform_skycoord_to_AltAz(ra, dec)
    # print(alt)
    # print(az)

    import time

    try:
        serial.Serial.reset_input_buffer()
        while True:
            az,alt = transform_skycoord_to_AltAz(ra, dec)
            s_az = str(az)
            s_alt = str(alt)
            coord =  s_az + " " + s_alt
            send_coord(coord)
            print(coord)
            #time.sleep(1)
            serial.Serial.read(timeout = None)
            serial.Serial.reset_input_buffer()
    except KeyboardInterrupt:
        print("Loop stopped by user.") #loop is interrupted with the command Ctrl + C 

