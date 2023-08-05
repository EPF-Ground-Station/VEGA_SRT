# -*- coding: utf-8 -*-
"""
Library aimed at scripting Srt with Antenna pointing mechanism

@LL
"""


import serial
import time
from enum import Enum
from time import sleep
from threading import Thread
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, ICRS

NORTH = 990000
TRACKING_RATE = 0.1  # Necessary delay for sending point_to to APM while tracking
PING_RATE = 60  # Ping every minute


class SerialPort:

    """Class aimed at representing the interaction with the APM serial port"""

    def __init__(self, adress, baud, timeo=None):
        self.ser = serial.Serial(adress, baud, timeout=timeo)
        self.connected = False

    def connect(self):
        self.ser.open()
        self.connected = True

    def disconnect(self):
        self.connected = False
        self.ser.close()

    def listen(self):
        """Reads last message from SerialPort with appropriate processing"""

        status, feedback = self.ser.readline().decode('utf-8').split(" | ")

        if ("Err" in status) or ("Warn" in status):
            print(status + " : " + feedback)
            feedback = feedback.split("APM returned ")[-1]

        return feedback.strip()

    def send_Ser(self, msg: str):
        """Sends message msg through the serial port.

        Returns answer from SerialPort.

        """

        if self.connected:

            self.ser.reset_input_buffer()  # Discards remaining data in buffer
            self.ser.write((msg).encode())  # Sends message to serial

            answer = self.listen()

            return answer

        else:
            return ""


class TrackMode(Enum):
    """Tracking modes of SRT"""
    RADEC = 1
    TLE = 2     # To be implemented


class BckgrndAPMTask(Thread):
    """Virtual class aimed at making parallel tasks on APM easier 

    Methods :
        stop() : turns the stop flag on, allows to kill the thread when writing
        the run() method in daughter classes

        pause() : turns on flag off. allows to pause the thread in run()

        unpause() : turns on flag on
    """

    def __init__(self, ser):
        self.on = False         # May stop the thread but does not kill it
        self.stop = False       # kills the thread
        self.pending = False    # flag on while waiting for answer from ser
        self.ser = ser          # serial port over which APM communicates
        Thread.__init__(self)
        self.daemon = True

    def stop(self):             # Allows to kill the thread
        self.stop = True
        while self.pending:
            pass

    def pause(self):
        self.on = False
        while self.pending:
            pass

    def unpause(self):
        self.on = True


class Ping(BckgrndAPMTask):

    def __init__(self, ser):

        BckgrndAPMTask.__init__(self, ser)

    def run(self):

        while not self.stop:

            if self.on:

                self.pending = True         # Indicates waiting for an answer
                ans = self.ser.send_Ser("ping ")
                self.pending = False        # Answer received
                print(ans)

                timeNow = time.time()       # Waits before pinging again
                while time.time() < timeNow + PING_RATE:
                    pass


class Tracker(BckgrndAPMTask):
    """
    Thread that tracks some given sky coordinates. Only supports RADES atm

    Possible Improvements : Implement tracking satellites out of TLEs

    """

    def __init__(self, ser):
        self.az = 0
        self.alt = 0
        self.ra = 0
        self.dec = 0
        self.mode = TrackMode.RADEC
        BckgrndAPMTask.__init__(self, ser)

    def refresh_azalt(self):
        """Refreshes coords of target depending on tracking mode"""

        if self.mode.value == 1:  # if RADEC
            self.az, self.alt = RaDec_to_AzAlt(self.ra, self.dec)

    def setRADEC(self, ra, dec):
        """Sets target's coordinates in RADEC mode"""

        self.ra = ra
        self.dec = dec

    def run(self):

        while not self.stop:

            if self.on:
                self.refresh_azalt()        # Refreshes coord
                self.pending = True         # Indicates waiting for an answer
                ans = self.ser.send_Ser("point_to " + str(self.az) + " " +
                                        str(self.alt))
                self.pending = False        # Answer received

                # delay next
                timeNow = time.time()
                while time.time() < timeNow + TRACKING_RATE:
                    pass

                if "Err" in ans:
                    print("Error while tracking. Tracking aborted...")
                    self.stop = True


class Srt:

    """Class that supervizes interface btw user and Small Radio Telescope"""

    def __init__(self, adress, baud, timeo=None):

        self.ser = SerialPort(adress, baud, timeo=None)
        self.ser.disconnect()       # Keeps serial connection closed for safety

        self.timeout = timeo
        self.apmMsg = ""        # Stores last message from APM

        self.tracker = Tracker(self.ser)
        self.tracking = False

        self.ping = Ping(self.ser)
        self.ping.start()   # Initializes pinger : still needs to be unpaused to begin pinging

    def go_home(self, verbose=False):
        """Takes SRT to its home position and shuts motors off"""
        if self.tracking:               # Stops tracking before
            self.stopTracking()

        self.untangle(verbose)
        self.standby(verbose)

    def connect(self, water=True):
        """Connects to serial port"""
        self.ser.connect()
        self.ping.unpause()     # Starts pinging asa connected
        self.calibrate_north()  # Sets north offset
        if water:               # Evacuates water in default mode
            self.empty_water()
        else:
            self.untangle()

    def disconnect(self):
        """Disconnects from serial port"""

        self.go_home(verbose=True)  # Gets SRT to home position
        self.ping.pause()           # Stop pinging
        self.ser.disconnect()       # Ciao

    def send_APM(self, msg: str, verbose=False, save=True):
        """
        Utilitary function aimed at sending arbitrary messages to the pointing
        mechanism via serial port.

        Returns answer from APM. Saves it in apmMsg attr if save flag is on

        """

        if self.ser.connected:

            if self.tracking:
                self.tracker.pause()         # Pauses tracker
            else:
                self.ping.pause()            # Otherwise pauses ping

            answer = self.ser.send_Ser(msg)  # Sends message to serial port

            if self.tracking:
                self.tracker.unpause()       # Unpauses tracker
            else:
                self.ping.unpause()          # Otherwise unpauses ping

            print(answer)           # Display answer (useful atm in cmd line)

            if verbose:
                print(f"Message sent : {msg}")
            if save:
                self.apmMsg = answer      # Saves last answer from APM

            return answer

        else:
            print("APM disconnected. Aborted...")
            return ""

    def getAz(self):
        """Getter on current Azimuthal angle in degrees. In case of error
        returns -1 """

        try:
            az = float(self.send_APM("getAz "))
            return az
        except ValueError:
            print("Error when trying to obtain current Azimuth")
            return -1

    def getAlt(self):
        """Getter on current Altitude in degrees. In case of error
        returns -1 """

        try:
            alt = float(self.send_APM("getAlt "))
            return alt
        except ValueError:
            print("Error when trying to obtain current Altitude")
            return -1

    def getAzAlt(self):
        """Getter on current pozition un AltAz coordinates"""

        az = self.getAz()
        alt = self.getAlt()

        return az, alt

    def getPos(self):
        """Returns current RaDec in degrees"""

        try:
            alt = self.getAlt()
        except ValueError:
            print("Error when trying to obtain current Altitude")
            return -1
        try:
            az = self.getAz()
        except ValueError:
            print("Error when trying to obtain current Azimuth")
            return -1

        ra, dec = AzAlt_to_RaDec(az, alt)

        return ra, dec

    def getRA(self):
        """Returns current RA"""

        ra, dec = self.getPos()

        return ra

    def getDec(self):
        """Returns current Dec"""

        ra, dec = self.getPos()

        return dec

    def untangle(self, verbose=False):
        """
        Go back to resting position, untangling cables

        """
        if self.tracking:               # Stops tracking before pointing
            self.stopTracking()

        if verbose:
            print("Untangling...")
        return self.send_APM("untangle ", verbose)

    def standby(self, verbose=False):
        """
        Goes back to zenith and switches off motors

        """
        if self.tracking:               # Stops tracking before pointing
            self.stopTracking()

        if verbose:
            print("Going back to zenith and switching motors off...")
        return self.send_APM("stand_by ", verbose)

    def calibrate_north(self, value=NORTH, verbose=False):
        """
        Defines offset for North position in azimuthal microsteps
        EPFL current estimation : 990000

        """

        print(f"Calibrating North offset to value {value}")
        return self.send_APM("set_north_offset "+str(value) + " ", verbose)

    def point_to_AzAlt(self, az, alt, verbose=False):
        """
        Moves antenna to Azimuth and Altitude coordinates in degrees

        """

        if self.tracking:               # Stops tracking before pointing
            self.stopTracking()

        if verbose:
            print(f"Moving to Az={az}, Alt = {alt}...")
        coord = str(az) + ' ' + str(alt)
        return self.send_APM("point_to " + coord, verbose)

    def point_to_RaDec(self, ra, dec, verbose=False):
        """
        Moves antenna to Right Ascension and Declination coordinates in degrees

        """

        if verbose:
            print(f"Moving to RA={ra}, Dec = {dec}...")
        az, alt = RaDec_to_AzAlt(ra, dec)
        return self.point_to_AzAlt(az, alt, verbose)

    def trackRaDec(self, ra, dec):
        """
        Starts tracking given sky coordinates in RaDec mode

        """
        self.ping.pause()                   # Ping useless in tracking mode
        self.tracking = True                # Updates flag

        if not self.tracker.is_alive():     # Launches tracker thread
            # At this point, APM not yet tracking : tracker's flag 'on' is still off
            self.tracker.start()

        self.tracker.setRADEC(ra, dec)
        self.tracker.on = True              # Now tracking

    def stopTracking(self):
        """
        Stops tracking motion

        """

        self.tracking = False               # Updates flag
        self.ping.unpause()                 # Keep sending activity

        if self.tracker.is_alive():

            self.tracker.stop = True        # Kills tracker
            while self.tracker.pending:    # Waits for last answer from APM
                pass

        del self.tracker                    # Deletes tracker
        self.tracker = Tracker(self.ser)    # Prepares new tracker

    def empty_water(self):
        """
        Moves antenna to a position where water can flow out then goes back to
        rest position after a while

        """
        print("Emptying water procedure launched...")
        print("Rotating antenna towards South...")
        print(self.point_to_AzAlt(180, 90))
        print("Inclinating to evacuate water...")
        print(self.point_to_AzAlt(180, 0))
        sleep(15)
        print(self.untangle())
        print(self.standby())
        print("Water evacuated. SRT is now ready for use.")
        return


def RaDec_to_AzAlt(ra, dec, verbose=False):
    """
    Takes the star coordinates rightascension and declination as input and transforms them to altitude and azimuth coordinates.

    :param obs_loc an instance of the class EarthLocation containing the informations about the location of the observator
    :param coords an instance of the class SkyCoord with coordinates corresponding to the input coordinates of the function
    :param altaz another instance of the class Skycoord but with the original coordinates transformed to the corresponding altitude and azimuth
    :param coords_altaz string containing the Azimuth in the first position and Altitude in the second position. Both as decimal numbers

    """

    # object = SkyCoord.from_name('M33')
    obs_loc = EarthLocation(
        lat=46.52457*u.deg, lon=6.61650*u.deg, height=500*u.m)
    time_now = Time.now()  # + 2*u.hour Don't need to add the time difference
    coords = SkyCoord(ra*u.deg, dec*u.deg)
    altaz = coords.transform_to(AltAz(obstime=time_now, location=obs_loc))

    az, alt = [float(x) for x in altaz.to_string(
        'decimal', precision=4).split(' ')]

    if verbose:
        print("Your Azimuth and Altitude coordinates are:")
        print(f"{az} {alt}")

    return az, alt


def AzAlt_to_RaDec(az, alt, verbose=False):
    """
    Takes the star coordinates azimuth and altitude as input and transforms them to altitude and azimuth coordinates.

    :param obs_loc an instance of the class EarthLocation containing the informations about the location of the observator
    :param coords an instance of the class SkyCoord with coordinates corresponding to the input coordinates of the function
    :param altaz another instance of the class Skycoord but with the original coordinates transformed to the corresponding altitude and azimuth
    :param coords_altaz string containing the Azimuth in the first position and Altitude in the second position. Both as decimal numbers

    """

    # object = SkyCoord.from_name('M33')
    obs_loc = EarthLocation(
        lat=46.52457*u.deg, lon=6.61650*u.deg, height=500*u.m)
    time_now = Time.now()  # + 2*u.hour Don't need to add the time difference
    altaz = AltAz(az=az*u.deg, alt=alt*u.deg,
                  obstime=time_now, location=obs_loc)
    coords = SkyCoord(altaz.transform_to(ICRS()))

    ra, dec = [float(x) for x in coords.to_string(
        decimal=True, precision=4).split(' ')]

    print(coords)
    print(ra, dec)

    if verbose:
        print("Your Right Ascension and Declination coordinates are:")
        print(f"{ra} {dec}")

    return ra, dec


# SRT = Srt("/dev/ttyUSB0", 115200, 1)      # TODO handle error on adress/baud
#                                                 # Maybe optimize with available ports etc


# def send_APM(msg:str, verbose = False):
#     """Utilitary function aimed at sending arbitrary message to the pointing
#     mechanism via serial port.

#     """


#     if SRT.ser.is_open:
#         SRT.send_APM(msg)
#         if verbose : print(f"Message sent : {msg}")


#     else:
#         print("APM disconnected. Aborted...")


#     # ack = ser.readline().decode('utf-8')
#     # if verbose : print(f"SRT ACK : {ack}", "Waiting for SRT feedback")


# def untangle(verbose = False):
#             """
#             Go back to resting position

#             """
#             print("Untangling...")
#             return send_APM("untangle ", verbose)


# def standby(verbose = False):
#             """
#             Go back to resting position

#             """
#             return send_APM("stand_by ", verbose)


# def calibrate_north(value):
#             """
#             Defines offset for North position in azimuthal microsteps

#             """

#             send_APM("set_north_offset "+str(value))


# def point_to_AzAlt(az, alt, verbose = False):
#     """
#     Moves antenna to Azimuth and Altitude coordinates in degrees

#     """

#     print(f"Pointing to Az={az}, Alt = {alt}")
#     coord = str(az) + ' ' + str(alt)
#     return send_APM("point_to " + coord, verbose)


# def point_to_RaDec(ra, dec, verbose = False):
#     """
#     Moves antenna to Right Ascension and Declination coordinates in degrees

#     """

#     print(f"Pointing to RA={ra}, Dec = {dec}")
#     az, alt = RaDec_to_AzAlt(ra, dec)
#     return point_to_AzAlt(az, alt, verbose)

# def empty_water():
#     """
#     Moves antenna to a position where water can flow out


#     """
#     point_to_AzAlt(180, 90)
#     return point_to_AzAlt(180, 0)
