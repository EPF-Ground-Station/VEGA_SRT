# -*- coding: utf-8 -*-
"""
Library aimed at scripting Srt with Antenna pointing mechanism

@LL
"""

import os
import json
import serial
import time
from datetime import datetime
from rtlsdr import *
from enum import Enum
from time import sleep
from threading import Thread
from astropy import units as u
from astropy.io import fits
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, ICRS
import matplotlib.pyplot as plt
import numpy as np
import virgo
from multiprocessing import Process

NORTH = 990000
TRACKING_RATE = 0.1  # Necessary delay for sending point_to to APM while tracking
PING_RATE = 60  # Ping every minute
DATA_PATH = os.path.expanduser("~") + "/RadioData/"  # Finds data dir of user
OBS_LAT = 46.5194444
OBS_LON = 6.565
OBS_HEIGHT = 411.0
LOC = (OBS_LAT, OBS_LON, OBS_HEIGHT)


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


class BckgrndAPMTask(Thread):
    """Virtual class aimed at making parallel tasks on APM easier 

    Methods :
        stop() : turns the stop flag on, allows to kill the thread when writing
        the run() method in daughter classes

        pause() : turns on flag off. allows to pause the thread in run()

        unpause() : turns on flag on
    """

    def __init__(self, ser):
        self.on = False         # May pause the thread but does not kill it
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

                timeNow = time.time()       # Waits before pinging again
                while time.time() < timeNow + PING_RATE:
                    pass


class Tracker(BckgrndAPMTask):
    """
    Thread that tracks some given sky coordinates. Only supports RADEC atm

    Possible Improvements : Implement tracking satellites out of TLEs,
    galactic coordinates, objects of solar system

    """

    def __init__(self, ser, _mode=TrackMode.RADEC):
        self.az = 0
        self.alt = 0
        self.a = 0      # RA in radec, LONG in gal
        self.b = 0      # DEC in radec, b in gal
        self.mode = _mode
        BckgrndAPMTask.__init__(self, ser)

    def refresh_azalt(self):
        """Refreshes coords of target depending on tracking mode"""

        if self.mode.value == 1:  # if RADEC
            self.az, self.alt = RaDec2AzAlt(self.a, self.b)

        elif self.mode.value == 2:
            self.az, self.alt = Gal2AzAlt(self.a, self.b)

    def setTarget(self, a, b):
        """Sets target's coordinates in RADEC mode"""

        self.a = a
        self.b = b

    def setMode(self, mode):
        """Sets tracking mode"""

        self.mode = TrackMode(mode)

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

        # Connect SDR and set default parameters
        # self.sdr = RtlSdr()
        # self.sdr.sample_rate = 2.048e6
        # self.sdr.center_freq = 1420e06
        # self.sdr.gain = 480
        # self.sdr.set_bias_tee(True)
        # self.sdr.close()

        # Declares process that runs observations
        self.obsProcess = None
        self.observing = False

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
        self.untangle()
        if water:               # Evacuates water in default mode
            self.empty_water()

    def disconnect(self):
        """Disconnects from serial port"""

        self.go_home()  # Gets SRT to home position
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

    def pointAzAlt(self, az, alt, verbose=False):
        """
        Moves antenna to Azimuth and Altitude coordinates in degrees

        """

        if self.tracking:               # Stops tracking before pointing
            self.stopTracking()

        if verbose:
            print(f"Moving to Az={az}, Alt = {alt}...")
        coord = str(az) + ' ' + str(alt)
        return self.send_APM("point_to " + coord, verbose)

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

    def trackRaDec(self, ra, dec):
        """
        Starts tracking given sky coordinates in RaDec mode

        """
        self.pointRaDec(
            ra, dec)            # Goes to destination before allowing other command
        self.ping.pause()                   # Ping useless in tracking mode
        self.tracking = True                # Updates flag

        if not self.tracker.is_alive():     # Launches tracker thread
            # At this point, APM not yet tracking : tracker's flag 'on' is still off
            self.tracker.start()

        self.tracker.setMode(1)
        self.tracker.setTarget(ra, dec)
        self.tracker.on = True              # Now tracking

    def trackGal(self, long, b):
        """
        Starts tracking given sky coordinates in Galactic mode

        """
        self.pointGal(
            long, b)  # Goes to destination before allowing other command
        self.ping.pause()                   # Ping useless in tracking mode
        self.tracking = True                # Updates flag

        if not self.tracker.is_alive():     # Launches tracker thread
            # At this point, APM not yet tracking : tracker's flag 'on' is still off
            self.tracker.start()

        mode = 2
        self.tracker.setMode(mode)
        self.tracker.setTarget(long, b)
        self.tracker.on = True              # Now tracking

    def stopTracking(self):
        """
        Stops tracking motion

        """

        self.tracking = False               # Updates flag

        if self.tracker.is_alive():

            self.tracker.stop = True        # Kills tracker
            while self.tracker.pending:    # Waits for last answer from APM
                pass

        del self.tracker                    # Deletes tracker
        self.tracker = Tracker(self.ser)    # Prepares new tracker

        self.ping.unpause()                 # Keep sending activity

    def empty_water(self):
        """
        Moves antenna to a position where water can flow out then goes back to
        rest position after a while

        """
        print("Emptying water procedure launched...")
        print("Rotating antenna towards South...")
        print(self.pointAzAlt(180, 90))
        print("Inclinating to evacuate water...")
        print(self.pointAzAlt(180, 0))
        sleep(15)
        print(self.untangle())
        print(self.standby())
        print("Water evacuated. SRT is now ready for use.")
        return

    def waitObs(self):
        """
        Waits for the observation to finish. 
        Should only be used in command line; GUI must get
        rid of this another way round I guess...
        """

        if not self.observing:
            return

        self.obsProcess.join()

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

        self.obsProcess = Process(target=self.__observe, args=(
            repo, name, dev_args, rf_gain, if_gain, bb_gain, fc, bw, channels, t_sample, duration, overwrite))
        self.obsProcess.start()
        print(f"observing status : {self.observing}")

    def __observe(self, repo, name, dev_args, rf_gain, if_gain, bb_gain, fc, bw, channels, t_sample, duration, overwrite):
        """
            Private method that uses virgo library to observe with given parameters. 

            Recorded data is saved either under absolute path repo/name.dat, or
            relative path repo/name.dat under DATA_PATH directory.
        """

        self.observing = True

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
        csv_path = repo+'spectrum_{name}.csv'

        virgo.plot(obs_parameters=obs_params, n=n, m=m, f_rest=f_rest,
                   vlsr=vlsr, dB=dB, meta=meta,
                   obs_file=obsPath, cal_file=calibPath,
                   spectra_csv=csv_path, plot_file=plot_path)

        print(f"Plot saved under {plot_path}. CSV saved under {csv_path}.")


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
    coords = SkyCoord(altaz.transform_to('galactic'))

    long, b = [float(x) for x in coords.to_string(
        decimal=True, precision=4).split(' ')]

    return long, b


# def plotAvPSD(path):
#     """Plots the averaged PSD of the observation located in path"""

#     path = path.strip("/")
#     obsName = path.split('/')[-1]   # Extract name of observation from path
#     path = "/" + path + '/'    # Formatting

#     # Allow for relative paths
#     if not os.path.isdir(path):
#         path = DATA_PATH + path

#     if os.path.isfile(path+"params.json"):

#         with open(path+"params.json", "r") as jsFile:
#             params = json.load(jsFile)
#     elif not os.path.isdir(path):
#         print("ERROR : path does not relate to any recorded observation")
#         return
#     else:
#         print(
#             f"ERROR : no parameter file found at {path}." +
#             "Try giving the full path to an exisiting observation.")
#         return

#     # Extract data
#     fc = params["fc"]
#     rate = params["rate"]
#     channels = params["channels"]

#     for root, repo, files in os.walk(path):   # I did not find any other way...
#         fitsFiles = [file for file in files if ".fits" in file]

#     obsNb = len(fitsFiles)  # Number of files in observation

#     firstFile = fitsFiles.pop(0)  # Pops the first element of the list
#     real = fits.open(path+firstFile)[1].data.field('real').flatten()
#     image = fits.open(path+firstFile)[1].data.field('im').flatten()

#     for file in fitsFiles:
#         data = fits.open(path+file)[1].data
#         real += data.field('real').flatten()
#         image += data.field('im').flatten()

#     average = (real + 1.0j*image)/obsNb

#     plt.psd(average, NFFT=channels, Fs=rate/1e6, Fc=fc/1e6)
#     plt.xlabel('frequency (Mhz)')
#     plt.ylabel('Relative power (db)')
#     plt.savefig(path+"PSD.png", format="png")
#     plt.show()
#     print("Figure saved at " + path + "PSD.png")


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

    # def obsPower(self, duration, intTime=1, bandwidth=1.024, fc=1420, repo=None, obs=None, gain=480):
    #     """ Observes PSD at center frequency fc for a duration in seconds with
    #     integration time of intTime. Bandwidth and center frequency fc are
    #     indicated in MHz"""

    #     print(f"Observing for {duration} seconds...")

    #     # If no indicated repository to save data
    #     if repo == None:
    #         # Make repo the default today's timestamp
    #         repo = datetime.today().strftime('%Y-%m-%d')

    #     # Check if there exists a repo at this name
    #     if not os.path.isdir(DATA_PATH + repo):
    #         os.mkdir(DATA_PATH + repo)     # if not, create it

    #     repo = DATA_PATH + repo + '/'

    #     # If no indicated observation name
    #     if obs == None:
    #         # Make the name to current timestamp
    #         obs = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    #     # Check if there exists a repo at this name
    #     if not os.path.isdir(repo + obs):
    #         os.mkdir(repo + obs)     # if not, create it

    #     obs = obs + '/'

    #     fc *= 1e6  # MHz to Hz
    #     print(f"fc={fc}")

    #     rate = bandwidth * 2e6
    #     print(f"rate = {rate}")

    #     # Save parameters of observation for later analysis
    #     with open(repo+obs+"params.json", "w") as jsFile:
    #         d = {"fc": fc,
    #              "rate": rate, "channels": 1024,
    #              "gain": gain, "intTime": intTime}
    #         json.dump(d, jsFile)

    #     nbSamples = rate * intTime
    #     m = np.floor(nbSamples/1024)    # Prefer a multiple of 1024 (channels)
    #     nbObs = int(np.ceil(duration/intTime))

    #     for i in range(nbObs):
    #         # Collect data
    #         print("DEBUG open")
    #         self.sdr.open()
    #         print("DEBUG fc")
    #         self.sdr.center_freq = fc
    #         print("DEBUG rate")
    #         self.sdr.sample_rate = rate
    #         print("DEBUG gain")
    #         self.gain = gain
    #         print("DEBUG read")
    #         self.sdr.set_bias_tee(True)
    #         print(m)
    #         samples = self.sdr.read_samples(1024 * m)

    #         print("DEBUG save")
    #         # Save data
    #         real = fits.Column(name='real', array=samples.real, format='1E')
    #         im = fits.Column(name='im', array=samples.imag, format='1E')
    #         table = fits.BinTableHDU.from_columns([real, im])
    #         table.writeto(repo + obs + "sample#" +
    #                       str(i) + '.fits', overwrite=True)
    #         self.sdr.close()

    #     print(f"Observation complete. Data stored in {repo+obs}")
    #     print("Plotting averaged PSD")
    #     plotAvPSD(repo+obs)     # Plot averaged PSD
