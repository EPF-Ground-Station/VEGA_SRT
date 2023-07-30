# -*- coding: utf-8 -*-
"""
Library aimed at scripting interface with SRT pointing mechanism
"""
import serial
from serial.tools import list_ports
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz

def send_ser(msg:str, verbose = False):
    """Utilitary function aimed at sending arbitrary message to the pointing
    mechanism via serial port.
    
    Returns : Serial ESP feedback    
    """
 
    
    ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=None) # Maybe optimize with available ports etc
    
    ser.reset_input_buffer()    #Discards remaining data in buffer
    ser.write((msg).encode())   #Sends message to serial 
    
    
    if verbose : print(f"Message written : {msg}","Waiting for esp ack")
    
    ack = ser.readline().decode('utf-8')
    if verbose : print(f"ESP ACK : {ack}", "Waiting for esp feedback")
    
    feedback = ser.read()
    if verbose : print(f"ESP feedback : {feedback}")
    
    return feedback

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
    return point_to_AzAlt(180, 0)
    
