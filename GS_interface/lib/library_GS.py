# -*- coding: utf-8 -*-
"""
Library aimed at scripting interface with SRT pointing mechanism
"""
import serial
from threading import Thread
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz


class Listening_daemon(Thread):
    """ Thread that continuously listens on the serial port and prints messages
    from ESP if disp flag is on """
    
    def __init__(self, ser):
        self.disp = False
        self.msg = ""
        self.stop = False
        Thread.__init__(self)
        self.daemon = True
        self.ser = ser
        
    def run(self):
        while not self.stop:
            self.msg = self.ser.readline().decode('utf-8')
            if self.disp: print(self.msg)



class Interface:
    
    """Class that supervizes interface between user and serial port"""
    
    def __init__(self, adress, baud, timeo=None):
        
        self.ser = serial.Serial(adress, baud, timeout=timeo) # Maybe optimize with available ports etc
        self.connected = False
        self.listener = Listening_daemon(self.ser)
    
    def connect(self):
        self.ser.open()
        self.connected = True
        self.listener.disp = True
        self.listener.start()
        
    def mute(self):
        self.listener.disp = False
    
    def disconnect(self):
        self.listener.disp = False
        self.listener.stop = True
        self.ser.close()
        del self.listener
        self.listener = Listening_daemon(self.ser)


ESP = Interface("/dev/ttyUSB0", 115200, 1)


def send_ser(msg:str, verbose = False):
    """Utilitary function aimed at sending arbitrary message to the pointing
    mechanism via serial port.

    """
    
    if ESP.ser.is_open:
        ESP.ser.reset_input_buffer()    #Discards remaining data in buffer
        ESP.ser.write((msg).encode())   #Sends message to serial 
    else:
        print("ESP disconnected. Aborted...")
    
    if verbose : print(f"Message written : {msg}")
    
    # ack = ser.readline().decode('utf-8')
    # if verbose : print(f"ESP ACK : {ack}", "Waiting for esp feedback")



def untangle(verbose = False):
            """
            Go back to resting position
        
            """

            return send_ser("untangle ", verbose)

           
def standby(verbose = False):
            """
            Go back to resting position
        
            """
            return send_ser("stand_by ", verbose)
        
        
def calibrate_north(value):
            """
            Defines offset for North position in azimuthal microsteps
        
            """

            send_ser("set_north_offset "+str(value))
            
def RaDec_to_AltAz(ra, dec, verbose=False):
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
    
    alt, az =[float(x) for x in  altaz.to_string('decimal').split(' ')]
    
    if verbose :
        print("Your Azimuth and Altitude coordinates are:")
        print(f"{alt} {az}")
    #print(altaz.az)
    #print(altaz.alt)

    return alt, az

def point_to_AzAlt(az, alt, verbose = False):
    """
    Moves antenna to Azimuth and Altitude coordinates in degrees
                
    """
    coord = str(az) + ' ' + str(alt)
    return send_ser("point_to " + coord, verbose)


def point_to_RaDec(ra, dec, verbose = False):
    """
    Moves antenna to Right Ascension and Declination coordinates in degrees
    
    """
            
    alt, az = RaDec_to_AltAz(ra, dec)
    return point_to_AzAlt(az, alt, verbose)

def empty_water():
    """
    Moves antenna to a position where water can flow out

    
    """
    point_to_AzAlt(180, 90)
    return point_to_AzAlt(180, 0)
    
