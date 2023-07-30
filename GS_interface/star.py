from lib.library_GS import point_to_RaDec
from threading import Thread
import re
import argparse

# def name_input(name):
#      object = SkyCoord.from_name(name)


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


def tracking_daemon(ra, dec, verbose):
    
    """Will be continuously executed while the program is running"""
    
    while True :
        point_to_RaDec(ra, dec, verbose=True)

     
if __name__ == "__main__":
    ra, dec = parse_star_coordinates()

    # available_ports = []

    # for port, desc_port, id in list_ports.comports():
    #     print(port)
    #     print(desc_port)
    #     if desc_port.find("Serial") > 0:
    #         print("port available")
    #         available_ports.append(port)

    # if True:
    #     print("available_ports true")
    #     ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=None)


    try:
        daemon = Thread(target = tracking_daemon, daemon=True)
        daemon.start()      # Launches infinite loop to track coordinates

        print("Press ENTER to stop tracking : ")
        print(input())      # Daemon will stop as user press ENTER

        print("Tracking stopped")
            

    except KeyboardInterrupt:
        # loop is interrupted with the command Ctrl + C
        print("Tracking force-stopped by user.")
