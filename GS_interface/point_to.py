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


def parse_azel_coordinates():
    # Regular expression to validate the input format

    parser = argparse.ArgumentParser()
    parser.add_argument('-az', nargs=1, type=valid_float, metavar=('Deg'), help='Azimuth angle (degrees)')
    parser.add_argument('-el', nargs=1, type=valid_float, metavar=('Deg'), help='Elevation angle (degrees)')
    args = parser.parse_args()

    # Extracting the values from the input
    az_angle= args.az
    el_angle= args.el


    print('Azimuth angle:', az_angle)
    print('Elevation angle:', el_angle)


    return az_angle, el_angle

            
        
def send_coord(coord, ser):
            """
            Sends the Azimuth and Altitude coordinates calculated to the Teensy. 
        
            """
            
            DEBUG = True

            if DEBUG:
                print(coord)

            ser.write(("point_to " + coord).encode())
            print("wrote")

            # print(ser.readline().decode('utf-8'))
            # print("read line")

     
if __name__ == "__main__":
    az_angle, el_angle = parse_azel_coordinates()
    az_angle_str = string(az_angle)
    el_angle_str = string(el_angle)
    coords_str = [az_angle_str, el_angle_str]
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

            print(coords_str)

            print("wait for esp ack")
            print(ser.readline().decode('utf-8'))
            #ser.reset_input_buffer()

            print("wait for esp feedback")
            ser.read()
            ser.reset_input_buffer()
    except KeyboardInterrupt:
        # loop is interrupted with the command Ctrl + C
        print("Loop stopped by user.")
