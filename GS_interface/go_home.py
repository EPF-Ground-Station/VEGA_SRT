import serial
from serial.tools import list_ports
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
import re
import argparse
import time


        
def untangle(ser):
            """
            Go back to resting position
        
            """

            ser.write(("untangle ").encode())
            print("wrote")

            # print(ser.readline().decode('utf-8'))
            # print("read line")

def standby(ser):
            """
            Go back to resting position
        
            """

            ser.write(("stand_by ").encode())
            print("wrote")

            # print(ser.readline().decode('utf-8'))
            # print("read line")

if __name__ == "__main__":
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
            untangle(ser)
            standby(ser)
            print("wait for esp ack")
            print(ser.readline().decode('utf-8'))
            #ser.reset_input_buffer()

            print("wait for esp feedback")
        ser.read()
        ser.reset_input_buffer()
    untangle(ser)
    standby(ser)
    except KeyboardInterrupt:
        # loop is interrupted with the command Ctrl + C
        print("Loop stopped by user.")
