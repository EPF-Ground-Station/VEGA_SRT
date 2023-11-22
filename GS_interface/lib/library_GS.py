# -*- coding: utf-8 -*-
"""
Library aimed at scripting Srt with Antenna pointing mechanism

@LL
"""



import requests
import os
import json
import serial
import time
from datetime import datetime
from . import virgo
from enum import Enum
from time import sleep
from threading import Thread
from astropy import units as u
from astropy.io import fits
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, ICRS
from skyfield.api import load, Topos
import skyfield
import matplotlib.pyplot as plt
import numpy as np
from multiprocessing import Process
from rtlsdr import *
from PySide6.QtCore import Slot, QFileInfo, QTimer, Signal, QThread, QObject

NORTH = 990000
TRACKING_RATE = 0.1  # Necessary delay for sending point_to to APM while tracking
PING_RATE = 60  # Ping every minute
DATA_PATH = os.path.expanduser("~") + "/RadioData/"  # Finds data dir of user
TLE_PATH = os.path.expanduser("~") + "/TLEs/"
OBS_LAT = 46.5194444
OBS_LON = 6.565
OBS_HEIGHT = 411.0
LOC = (OBS_LAT, OBS_LON, OBS_HEIGHT)
TOPOS_LOC = Topos(OBS_LAT, OBS_LON, OBS_HEIGHT)
# Delay used to point to future location of sat before tracking
SAT_INITIAL_DELAY = 15
TS = load.timescale()   # Loads skyfield timescale


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
    GAL = 2
    TLE = 3     # To be implemented


class BckgrndTask(Thread):
    """

    Methods :
        stop() : turns the stop flag on, allows to kill the thread when writing
        the run() method in daughter classes

        pause() : turns on flag off. allows to pause the thread in run()

        unpause() : turns on flag on
    """

    def __init__(self):

        Thread.__init__(self)
        self.on = False         # May pause the thread but does not kill it
        self.stop = False       # kills the thread
        self.pending = False    # flag on while waiting for answer from ser

        self.daemon = True

    def stop(self):             # Allows to kill the thread
        self.stop = True

    def pause(self):
        self.on = False

    def unpause(self):
        self.on = True


class BckgrndAPMTask(BckgrndTask):

    """Virtual class aimed at making parallel tasks on APM easier """

    def __init__(self, ser):
        BckgrndTask.__init__(self)  # serial port over which APM communicates
        self.ser = ser

    def setSer(self, ser):
        """Sets the serial port over which to communicate"""
        self.ser = ser


# class Ping(BckgrndAPMTask):

#     def __init__(self, ser):

#         BckgrndAPMTask.__init__(self, ser)

#     def run(self):

#         while not self.stop:

#             if self.on:

#                 self.pending = True         # Indicates waiting for an answer
#                 ans = self.ser.send_Ser("ping ")
#                 self.pending = False        # Answer received

#                 timeNow = time.time()       # Waits before pinging again
#                 while time.time() < timeNow + PING_RATE:
#                     pass


class QPing(QThread):

    sendPing = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        while not self.stop:
            sendPing.emit()
            timeNow = time.time()       # Waits before pinging again
            while time.time() < timeNow + PING_RATE:
                pass

    def stop(self):             # Allows to kill the thread
        self.stop = True

    def pause(self):
        self.on = False

    def unpause(self):
        self.on = True


class QTracker(QThread):

    sendPointTo = Signal(float, float)

    def __init__(self, _mode=TrackMode.RADEC, tle=None, parent=None):

        super().__init__(parent)

        self.stop = False
        self.on = False

        self.az = 0
        self.alt = 0
        self.a = 0      # RA in radec, LONG in gal
        self.b = 0      # DEC in radec, b in gal
        self.mode = _mode
        self.tle = tle
        self.satInRange = False  # Flag indicating whether sat is in fov
        self.pending = False

    def refresh_azalt(self):
        """Refreshes coords of target depending on tracking mode"""

        if self.mode.value == 1:  # if RADEC
            self.az, self.alt = RaDec2AzAlt(self.a, self.b)

        elif self.mode.value == 2:  # if GAL
            self.az, self.alt = Gal2AzAlt(self.a, self.b)

        elif self.mode.value == 3:  # if SAT

            self.az, self.alt = TLE2AzAlt(
                self.tle)    # , delay=TRACKING_RATE/2 Anticipate tracking rate

        # Checks if target is observable
        # if self.alt < 5:
        #     print("Tracker's target below 5° in elevation. Tracking aborted...")
        #     self.stop = True

    def turnOn(self):
        self.on = True

    def pause(self):
        self.on = False
        return
    def setMode(self, mode):
        """Sets tracking mode"""

        self.mode = TrackMode(mode)

    def setTarget(self, *args):
        """Sets target's coordinates"""

        # If coords mode
        if self.mode.value in (1, 2):
            if len(args) != 2:
                raise ValueError(
                    f"Tracker.setTarget() takes 2 arguments in coords mode, {len(args)} provided")
            else:
                self.a, self.b = args

        # if SAT mode
        else:
            if len(args) != 1:
                raise ValueError(
                    f"Tracker.setTarget() takes 1 arguments in SAT mode, {len(args)} provided")
            self.tle = args[0]

    def run(self):

        while not self.stop:
            self.pending = False
            if self.on:
                self.pending = True
                if self.mode.value != 3:    # If not sat

                    self.refresh_azalt()        # Refreshes coord
                    if self.alt < 5:  # If target not visible, wait for it
                        continue

                else:       # If sat
                    if not self.satInRange:
                        azFuture, altFuture = TLE2AzAlt(
                            self.tle, SAT_INITIAL_DELAY)
                        if altFuture < 5:
                            continue
                        else:
                            self.waitForSat(azFuture, altFuture)
                    else:
                        self.refresh_azalt()  # If sat in range, refresh azalt
                        if self.alt < 5:  # If sat not anymore in range
                            self.satInRange = False
                            print(
                                "Target satellite not anymore visible. Motion stopped...")
                            continue

                self.on = False  # Pauses the thread when pending
                self.sendPointTo.emit(self.az, self.alt)

                # delay next
                timeNow = time.time()
                while time.time() < timeNow + TRACKING_RATE:
                    pass

    @Slot()
    def onIdle(self):
        """Slot triggered when SRT is ready for next tracking motion"""

        self.on = True

# class Tracker(BckgrndAPMTask):
#     """
#     Thread that tracks some given sky coordinates. Only supports RADEC atm

#     Possible Improvements : Implement tracking satellites out of TLEs,
#     galactic coordinates, objects of solar system

#     """

#     def __init__(self, ser, _mode=TrackMode.RADEC, tle=None):

#         BckgrndAPMTask.__init__(self, ser)

#         self.az = 0
#         self.alt = 0
#         self.a = 0      # RA in radec, LONG in gal
#         self.b = 0      # DEC in radec, b in gal
#         self.mode = _mode
#         self.tle = tle
#         self.satInRange = False  # Flag indicating whether sat is in fov

#     def refresh_azalt(self):
#         """Refreshes coords of target depending on tracking mode"""

#         if self.mode.value == 1:  # if RADEC
#             self.az, self.alt = RaDec2AzAlt(self.a, self.b)

#         elif self.mode.value == 2:  # if GAL
#             self.az, self.alt = Gal2AzAlt(self.a, self.b)

#         elif self.mode.value == 3:  # if SAT

#             self.az, self.alt = TLE2AzAlt(
#                 self.tle)    # , delay=TRACKING_RATE/2 Anticipate tracking rate

#         # Checks if target is observable
#         # if self.alt < 5:
#         #     print("Tracker's target below 5° in elevation. Tracking aborted...")
#         #     self.stop = True

#     def setTarget(self, *args):
#         """Sets target's coordinates"""

#         # If coords mode
#         if self.mode.value in (1, 2):
#             if len(args) != 2:
#                 raise ValueError(
#                     f"Tracker.setTarget() takes 2 arguments in coords mode, {len(args)} provided")
#             else:
#                 self.a, self.b = args

#         # if SAT mode
#         else:
#             if len(args) != 1:
#                 raise ValueError(
#                     f"Tracker.setTarget() takes 1 arguments in SAT mode, {len(args)} provided")
#             self.tle = args[0]

#     def setMode(self, mode):
#         """Sets tracking mode"""

#         self.mode = TrackMode(mode)

#     def waitForSat(self, azFuture, altFuture):
#         """Anticipates sat's future position to optimize tracking rate"""

#         print(
#             f"Moving to target satellite at az {azFuture}, alt {altFuture}... ")
#         time_start = time.time()
#         self.pending = True
#         ans = self.ser.send_Ser(f"point_to {azFuture:2f} {altFuture:2f}")
#         self.pending = False
#         time_end = time.time()
#         delay = SAT_INITIAL_DELAY - (time_end - time_start)
#         if delay > 0:
#             time.sleep(delay)

#         self.satInRange = True
#         print("Sat in range. Tracking begins...")

#     def run(self):

#         while not self.stop:

#             if self.on:

#                 if self.mode.value != 3:    # If not sat

#                     self.refresh_azalt()        # Refreshes coord
#                     if self.alt < 5:  # If target not visible, wait for it
#                         continue

#                 else:       # If sat
#                     if not self.satInRange:
#                         azFuture, altFuture = TLE2AzAlt(
#                             self.tle, SAT_INITIAL_DELAY)
#                         if altFuture < 5:
#                             continue
#                         else:
#                             self.waitForSat(azFuture, altFuture)
#                     else:
#                         self.refresh_azalt()  # If sat in range, refresh azalt
#                         if self.alt < 5:  # If sat not anymore in range
#                             self.satInRange = False
#                             print(
#                                 "Target satellite not anymore visible. Motion stopped...")
#                             continue

#                 self.pending = True         # Indicates waiting for an answer
#                 ans = self.ser.send_Ser(f"point_to {self.az:2f} {self.alt:2f}")
#                 self.pending = False        # Answer received

#                 # delay next
#                 timeNow = time.time()
#                 while time.time() < timeNow + TRACKING_RATE:
#                     pass

#                 if "Err" in ans:
#                     print("Error while tracking. Tracking aborted...")
#                     self.stop = True


class Srt(QObject):

    """Class that supervizes interface btw user and Small Radio Telescope"""

    trackMotionEnd = Signal()
    pauseTracking = Signal()

    def __init__(self, adress, baud, timeo=None, parent=None):

        super().__init__(parent)

        self.ser = SerialPort(adress, baud, timeo=None)
        self.ser.disconnect()       # Keeps serial connection closed for safety

        self.timeout = timeo
        self.apmMsg = ""        # Stores last message from APM

        self.tracker = QTracker()

        self.tracker.start()

        self.tracking = False
        self.tracker.sendPointTo.connect(self.onTrackerSignal)
        self.trackMotionEnd.connect(self.tracker.turnOn)
        self.pauseTracking.connect(self.tracker.pause)

        self.ping = QPing()
        self.ping.start()   # Initializes pinger : still needs to be unpaused to begin pinging
        self.ping.sendPing.connect(self.onPingSignal)

        # Connect SDR and set default parameters
        self.sdr = RtlSdr()
        self.sdr.sample_rate = 2.048e6
        self.sdr.center_freq = 1420e06
        self.sdr.gain = 480
        self.sdr.set_bias_tee(True)
        self.sdr.close()

        # Declares process that runs observations
        self.obsProcess = None
        self.observing = False

        self.pending = False


        self.az, self.alt = 0,0
        self.ra, self.dec = 0,0
        self.long, self.lat = 0,0

    def go_home(self, verbose=False):
        """Takes SRT to its home position and shuts motors off"""
        if self.tracking:               # Stops tracking before
            self.stopTracking()

        self.untangle(verbose)
        self.standby(verbose)

    def connectAPM(self, water=True):
        """Connects to serial port"""

        if self.ser.connected:
            return "SRT already connected"

        self.ser.connect()
        self.ping.unpause()     # Starts pinging asa connected
        self.calibrate_north()  # Sets north offset
        msg = self.untangle()
        if water:               # Evacuates water in default mode
            msg = self.empty_water()

        self.getAllCoords()
        return msg

    def disconnectAPM(self):
        """Disconnects from serial port"""

        if not self.ser.connected:
            return "SRT already disconnected"

        self.stopTracking()

        msg = self.go_home()  # Gets SRT to home position
        self.ping.pause()           # Stop pinging

        self.ser.disconnect()       # Ciao

        return msg

    def send_APM(self, msg: str, verbose=False, save=True):
        """
        Utilitary function aimed at sending arbitrary messages to the pointing
        mechanism via serial port.

        Returns answer from APM. Saves it in apmMsg attr if save flag is on

        """

        self.pending = True

        if self.ser.connected:

            answer = self.ser.send_Ser(msg)  # Sends message to serial port

            self.pending = False

            # DEBUG Display answer (useful atm in cmd line)
            print(answer)

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
            self.az = az
            return az
        except ValueError:
            print("Error when trying to obtain current Azimuth")
            return -1

    def getAlt(self):
        """Getter on current Altitude in degrees. In case of error
        returns -1 """

        try:
            alt = float(self.send_APM("getAlt "))
            self.alt = alt
            return alt
        except ValueError:
            print("Error when trying to obtain current Altitude")
            return -1

    def getAzAlt(self):
        """Getter on current pozition in AltAz coordinates"""

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

        ra, dec = AzAlt2RaDec(az, alt)
        self.ra = ra
        self.dec = dec

        return ra, dec

    def getGal(self):
        """Returns current long/lat in galactic coords"""

        az, alt = self.getAzAlt()
        long, lat = AzAlt2Gal(az, alt)

        return long, lat

    def getRA(self):
        """Returns current RA"""

        ra, dec = self.getPos()

        return ra

    def getDec(self):
        """Returns current Dec"""

        ra, dec = self.getPos()

        return dec

    def getAllCoords(self):
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

        ra, dec = AzAlt2RaDec(az, alt)
        long, lat = AzAlt2Gal(az, alt)

        self.az, self.alt = az, alt
        self.ra, self.dec = ra, dec
        self.long, self.lat = long, lat

        return

    def returnStoredCoords(self):
        return (self.az, self.alt, self.ra, self.dec, self.long, self.lat)
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

    def pointAzAlt(self, az, alt, verbose=False):
        """
        Moves antenna to Azimuth and Altitude coordinates in degrees

        """

        if not self.tracking:               # Stops tracking before pointing
            self.stopTracking()

        alt %= 90
        if alt < 5:
            alt = 5
            print("WARNING : elevation too low. Security lower bound is 5°")

        if verbose:
            print(f"Moving to Az={az}, Alt = {alt}...")
        coord = str(az) + ' ' + str(alt)

        answer = self.send_APM("point_to " + coord, verbose)
        time0 = time.time()
        self.getAllCoords()
        time1 = time.time()

        print(f"{(time1-time0)*1000} ms")
        return answer

    def pointRaDec(self, ra, dec, verbose=False):
        """
        Moves antenna to Right Ascension and Declination coordinates in degrees

        """

        if verbose:
            print(f"Moving to RA={ra}, Dec = {dec}...")
        az, alt = RaDec2AzAlt(ra, dec)
        return self.pointAzAlt(az, alt, verbose)

    def pointGal(self, long, lat, verbose=False):
        """
        Moves antenna to galactic coordinates in degrees

        """

        if verbose:
            print(f"Moving to long={long}, lat = {lat}...")
        az, alt = Gal2AzAlt(long, lat)
        return self.pointAzAlt(az, alt, verbose)

    def onTrackerSignal(self, az, alt):

        if self.tracking:
            self.pointAzAlt(az, alt)
            if self.tracking:
                self.trackMotionEnd.emit()

    def onPingSignal(self):
        self.send_APM("ping")

    def trackRaDec(self, ra, dec):
        """
        Starts tracking given sky coordinates in RaDec mode

        """
        self.tracking = True    # Updates flag BEFORE pointing
        self.pointRaDec(
            ra, dec)            # Goes to destination before allowing other command
        self.ping.pause()                   # Ping useless in tracking mode


        if not self.tracker.isRunning():     # Launches tracker thread
            # OLD: At this point, APM not yet tracking : tracker's flag 'on' is still off
            self.tracker.start()

        self.tracker.setMode(1)
        self.tracker.setTarget(ra, dec)
        self.tracker.on = True              # Now tracking

    def trackGal(self, long, b):
        """
        Starts tracking given sky coordinates in Galactic mode

        """

        self.tracking = True                # Updates flag
        self.pointGal(
            long, b)  # Goes to destination before allowing other command
        self.ping.pause()                   # Ping useless in tracking mode


        if not self.tracker.isRunning():     # Launches tracker thread
            # At this point, APM not yet tracking : tracker's flag 'on' is still off
            self.tracker.start()

        mode = 2
        self.tracker.setMode(mode)
        self.tracker.setTarget(long, b)
        self.tracker.on = True              # Now tracking

    def trackSat(self, tle):
        """ 
        Starts tracking given a satellite TLE
        """

        if type(tle) != skyfield.sgp4lib.EarthSatellite:
            raise TypeError(
                "ERROR : STR.trackSat(tle) takes an EarthSatellite object as postional argument")

        # Position of sat in near future
        # azFuture, altFuture = TLE2AzAlt(tle, delay=SAT_INITIAL_DELAY)

        # inRange = False
        # while not inRange:

        #     startTime = time.time()
        #     self.pointAzAlt(TLE2AzAlt(tle, delay=SAT_INITIAL_DELAY))

        self.ping.pause()                   # Ping useless in tracking mode
        self.tracking = True                # Updates flag

        if not self.tracker.isRunning():     # Launches tracker thread
            # At this point, APM not yet tracking : tracker's flag 'on' is still off
            self.tracker.start()

        mode = 3
        self.tracker.setMode(mode)
        self.tracker.setTarget(tle)
        self.tracker.on = True              # Now tracking

    def stopTracking(self):
        """
        Stops tracking motion

        """

        self.tracking = False             # Updates flag

        if self.tracker.isRunning():

            self.pauseTracking.emit()        # Kills tracker
            while self.tracker.pending:    # Waits for last answer from APM
                pass

        #del self.tracker                    # Deletes tracker
        #self.tracker = Tracker(self.ser)    # Prepares new tracker

        self.ping.unpause()                 # Keep sending activity

    def empty_water(self):
        """
        Moves antenna to a position where water can flow out then goes back to
        rest position after a while

        """
        print("Emptying water procedure launched...")
        print("Rotating antenna towards South...")
        print(self.pointAzAlt(180, 89.9))
        print("Inclinating to evacuate water...")
        print(self.pointAzAlt(180, 5))
        sleep(15)
        print(self.untangle())
        print(self.standby())
        print("Water evacuated. SRT is now ready for use.")
        return "IDLE"

    def waitObs(self):
        """
        Waits for the observation to finish. 
        Should only be used in command line; GUI must get
        rid of this another way round I guess...
        """

        if not self.observing:
            return

        self.obsProcess.join()
        self.observing = False

    def stopObs(self):
        """
        Brute force kills the observation process
        """

        if not self.observing:
            print("ERROR : no observation to stop")
            return "ERROR : no observation to stop"

        self.obsProcess.terminate()
        self.observing = False
        print("Observation killed. Notice some recorded data might have been corrupted")

    def observe(self, repo=None, name=None, dev_args='rtl=0,bias=1', rf_gain=48, if_gain=25, bb_gain=18, fc=1420e6, bw=2.4e6, channels=2048, t_sample=1, duration=60, overwrite=False):
        """
        Launches a parallelized observation process. SRT's methods are still callable in the meanwhile

        Read SRT.__observe() docstring for more information.        
        """
        self.observing = True
        self.obsProcess = Process(target=self.__observe, args=(
            repo, name, dev_args, rf_gain, if_gain, bb_gain, fc, bw, channels, t_sample, duration, overwrite))
        self.obsProcess.start()
        print(f"observing status : {self.observing}")

    def __observe(self, repo, name, dev_args, rf_gain, if_gain, bb_gain, fc, bw, channels, t_sample, duration, overwrite):
        """
            Private method that uses virgo library to observe with given parameters. 

            Recorded data is saved either under absolute path repo/name.dat, or
            relative path repo/name.dat under DATA_PATH directory. Parameters 
            are saved in a json file
        """

        obs_params = {
            'dev_args': dev_args,
            'rf_gain': rf_gain,
            'if_gain': if_gain,
            'bb_gain': bb_gain,
            'frequency': fc,
            'bandwidth': bw,
            'channels': channels,
            't_sample': t_sample,
            'duration': duration,
            'loc': LOC,
            'ra_dec': '',
            'az_alt': ''
        }

        # If no indicated repository to save data
        if repo == None:
            # Make repo the default today's timestamp
            repo = datetime.today().strftime('%Y-%m-%d')

        repo = repo.strip("/")

        # Check absolute path
        if not os.path.isdir(repo):
            # Check relative path
            repo = DATA_PATH+repo
            if not os.path.isdir(repo):
                os.mkdir(repo)     # if not, create it
                print(f"Creating repository {repo}")

        repo = repo + '/'

        # If no indicated observation name
        if name == None:
            # Make the name to current timestamp
            name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

        name = name.strip('/')
        pathObs = repo+name

        # If overwrite flag turned off, create nth copy
        if (os.path.isfile(pathObs)) and (not overwrite):
            pathObs += "_(1)"
            while os.path.isfile(pathObs):
                digit = int(pathObs[pathObs.rfind('(')+1:-1])
                digit += 1
                pathObs = pathObs[:pathObs.rfind('(')+1] + str(digit) + ')'

        # Save parameters of observation for later analysis
        with open(pathObs+"_params.json", "w") as jsFile:
            json.dump(obs_params, jsFile)

        virgo.observe(obs_parameters=obs_params, obs_file=pathObs+'.dat')
        print(f"Observation complete. Data stored in {pathObs+'.dat'}")

        # /!\ SINCE multiprocessing CREATES A COPY OF THE SRT OBJECT, THE FOLLOWING
        # HAS NO EFFECT : TO BE IMPROVED
        self.observing = False

    def plotAll(self, repo, name, calib, n=20, m=35, f_rest=1420.4057517667e6,
                vlsr=False, dB=True, meta=False):
        """ 
        Plots full display of data using virgo library's virgo.plot function
        """

        # Formatting repo
        if not os.path.isdir(repo):
            repo = repo.strip('/')
            repo = DATA_PATH + repo + '/'

        if not repo.endswith('/'):
            repo += '/'

        # Load observation parameters
        if os.path.isfile(repo+f"/{name}_params.json"):

            with open(repo+f"/{name}_params.json", "r") as jsFile:
                obs_params = json.load(jsFile)

        elif not os.path.isdir(repo):
            print("ERROR : indicated repo does not relate to any recorded data")
            return

        else:
            print(
                f"ERROR : no parameter file found at {repo}. Data might have been corrupted. Try to clean {DATA_PATH}")
            return

        obs = name

        if not name.endswith('.dat'):
            obs += '.dat'

        if not calib.endswith('.dat'):
            calib += '.dat'

        calibPath = repo+calib
        obsPath = repo+obs

        if not os.path.isfile(calibPath):
            print(
                f"ERROR : no calibration file found at {calibPath}. Aborting...")
            return
        if not os.path.isfile(obsPath):
            print(
                f"ERROR : no observation file found at {obsPath} Aborting...")
            return

        plot_path = repo+f'plot_{name}.png'
        av_path = repo+f'average_{name}.png'
        cal_path = repo+f'calibrated_{name}.png'
        water_path = repo+f'waterfall_{name}.png'
        pow_path = repo+f'power_{name}.png'

        csv_path = repo+f'spectrum_{name}.csv'

        virgo.plot(obs_parameters=obs_params, n=n, m=m, f_rest=f_rest,
                   vlsr=vlsr, dB=dB, meta=meta,
                   obs_file=obsPath, cal_file=calibPath,
                   spectra_csv=csv_path, plot_file=plot_path, avplot_file=av_path,
                   calplot_file=cal_path, waterplot_file=water_path, powplot_file=pow_path)

        print(f"Plot saved under {plot_path}. CSV saved under {csv_path}.")

    def obsPower(self, duration, intTime=1, bandwidth=1.024, fc=1420, repo=None, obs=None, gain=480):
        """ Observes PSD at center frequency fc for a duration in seconds with
        integration time of intTime. Bandwidth and center frequency fc are
        indicated in MHz"""

        print(f"Observing for {duration} seconds...")

        # If no indicated repository to save data
        if repo == None:
            # Make repo the default today's timestamp
            repo = datetime.today().strftime('%Y-%m-%d')

        # Check if there exists a repo at this name
        if not os.path.isdir(DATA_PATH + repo):
            os.mkdir(DATA_PATH + repo)     # if not, create it

        repo = DATA_PATH + repo + '/'

        # If no indicated observation name
        if obs == None:
            # Make the name to current timestamp
            obs = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        # Check if there exists a repo at this name
        if not os.path.isdir(repo + obs):
            os.mkdir(repo + obs)     # if not, create it

        obs = obs + '/'

        fc *= 1e6  # MHz to Hz
        print(f"fc={fc}")

        rate = bandwidth * 2e6
        print(f"rate = {rate}")

        # Save parameters of observation for later analysis
        with open(repo+obs+"params.json", "w") as jsFile:
            d = {"fc": fc,
                 "rate": rate, "channels": 1024,
                 "gain": gain, "intTime": intTime}
            json.dump(d, jsFile)

        nbSamples = rate * intTime
        m = np.floor(nbSamples/1024)    # Prefer a multiple of 1024 (channels)
        nbObs = int(np.ceil(duration/intTime))

        for i in range(nbObs):
            # Collect data
            self.sdr.open()
            self.sdr.center_freq = fc
            self.sdr.sample_rate = rate
            self.gain = gain
            self.sdr.set_bias_tee(True)
            samples = self.sdr.read_samples(1024 * m)

            print("DEBUG save")
            # Save data
            real = fits.Column(name='real', array=samples.real, format='1E')
            im = fits.Column(name='im', array=samples.imag, format='1E')
            table = fits.BinTableHDU.from_columns([real, im])
            table.writeto(repo + obs + "sample#" +
                          str(i) + '.fits', overwrite=True)
            self.sdr.close()

        print(f"Observation complete. Data stored in {repo+obs}")
        print("Plotting averaged PSD")
        plotAvPSD(repo+obs)     # Plot averaged PSD


def RaDec2AzAlt(ra, dec):
    """
    Takes the star coordinates rightascension and declination as input and transforms them to altitude and azimuth coordinates.

    :param obs_loc an instance of the class EarthLocation containing the informations about the location of the observator
    :param coords an instance of the class SkyCoord with coordinates corresponding to the input coordinates of the function
    :param altaz another instance of the class Skycoord but with the original coordinates transformed to the corresponding altitude and azimuth
    :param coords_altaz string containing the Azimuth in the first position and Altitude in the second position. Both as decimal numbers

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
    Takes the star coordinates azimuth and altitude as input and transforms them to Ra Dec coordinates.

    :param obs_loc an instance of the class EarthLocation containing the informations about the location of the observator
    :param coords an instance of the class SkyCoord with coordinates corresponding to the input coordinates of the function
    :param altaz another instance of the class Skycoord but with the original coordinates transformed to the corresponding altitude and azimuth
    :param coords_altaz string containing the Azimuth in the first position and Altitude in the second position. Both as decimal numbers

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
    """Converts galactic coordinates to AzAlt"""

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
    """Converts AzAlt coordinates to galactic"""

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
    """Returns az and alt position of sat at current time given TLE"""

    t = TS.now()
    if delay != 0:
        t = t.utc
        t = TS.utc(t.year, t.month, t.day, t.hour, t.minute, t.second+delay)

    pos = (tle - TOPOS_LOC).at(t).altaz()

    return pos[1].degrees, pos[0].degrees


def loadTLE(name):
    """Loads TLEs from TLE_PATH"""

    url = f"https://www.celestrak.com/NORAD/elements/gp.php?NAME={name}&FORMAT=TLE"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            tle_data = response.text
        else:
            print(
                f"Failed to download TLE data from {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def plotAvPSD(path):
    """Plots the averaged PSD of the observation located in path"""

    path = path.strip("/")
    obsName = path.split('/')[-1]   # Extract name of observation from path
    path = "/" + path + '/'    # Formatting

    # Allow for relative paths
    if not os.path.isdir(path):
        path = DATA_PATH + path

    if os.path.isfile(path+"params.json"):

        with open(path+"params.json", "r") as jsFile:
            params = json.load(jsFile)
    elif not os.path.isdir(path):
        print("ERROR : path does not relate to any recorded observation")
        return
    else:
        print(
            f"ERROR : no parameter file found at {path}." +
            "Try giving the full path to an exisiting observation.")
        return

    # Extract data
    fc = params["fc"]
    rate = params["rate"]
    channels = params["channels"]

    for root, repo, files in os.walk(path):   # I did not find any other way...
        fitsFiles = [file for file in files if ".fits" in file]

    obsNb = len(fitsFiles)  # Number of files in observation

    firstFile = fitsFiles.pop(0)  # Pops the first element of the list
    real = fits.open(path+firstFile)[1].data.field('real').flatten()
    image = fits.open(path+firstFile)[1].data.field('im').flatten()

    for file in fitsFiles:
        data = fits.open(path+file)[1].data
        real += data.field('real').flatten()
        image += data.field('im').flatten()

    average = (real + 1.0j*image)/obsNb

    plt.psd(average, NFFT=channels, Fs=rate/1e6, Fc=fc/1e6)
    plt.xlabel('frequency (Mhz)')
    plt.ylabel('Relative power (db)')
    plt.savefig(path+"PSD.png", format="png")
    plt.show()
    print("Figure saved at " + path + "PSD.png")


# def getFreqP(path):
#     """Returns frequencies and power of PSD obtained with welch"""

#     path = path.strip("/")
#     path = '/' + path + '/'

#     with open(path+"params.json", "r") as jsFile:
#         params = json.load(jsFile)

#     # Extract data
#     fc = params["fc"]
#     rate = params["rate"]
#     channels = params["channels"]

#     # I did not find any other way...
#     for root, repo, files in os.walk(path):
#         fitsFiles = [file for file in files if ".fits" in file]

#     obsNb = len(fitsFiles)  # Number of files in observation

#     firstFile = fitsFiles.pop(0)  # Pops the first element of the list
#     real = fits.open(path+firstFile)[1].data.field('real').flatten()
#     image = fits.open(path+firstFile)[1].data.field('im').flatten()

#     for file in fitsFiles:
#         data = fits.open(path+file)[1].data
#         real += data.field('real').flatten()
#         image += data.field('im').flatten()

#     average = np.array((real + 1.0j*image)/obsNb)
#     intTime = 1
#     nperseg = int(intTime*rate)

#     # average = np.delete(average, round(np.floor(len(average)/2))
#     #                     )
#     # average = np.delete(average, round(np.ceil(len(average)/2)))

#     spectrum = np.fft.fft(average)
#     freq, psd = welch(average, rate, detrend=False)
#     freq += fc
#     return freq, psd
