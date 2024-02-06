# -*- coding: utf-8 -*-
"""
This module contains the main class for VEGA operation. To be instantiated only once by operation session.

The SRT owns the background threads QPing and QTracker. For more about those, see their respective modules.
"""

import requests
import json
from datetime import datetime
from . import virgo

from time import sleep
from astropy.io import fits

import skyfield
import matplotlib.pyplot as plt
from .SerialPort import *
from .QPing import QPing
from .QTracker import *
from multiprocessing import Process
from PySide6.QtCore import Signal, QObject


class Srt(QObject):
    """Class that monitors the interface between the user and the VEGA Small Radio Telescope.

    The features of the class include :

    - Slewing the APM in either a simple pointing or tracking motion
    - Acquiring data from the SDR
    - Processing data TODO : update the processing pipeline for more control than with virgo

    This class is intended to own and communicate with all threads sending commands to the APM. It also owns the
    SerialPort instance, and as such is the only one to properly speaking communicate with the APM. This is required
    to prevent multiple access to the Serial port.
    """

    trackMotionEnd = Signal()
    pauseTracking = Signal()

    def __init__(self, address, baud, timeout=None, parent=None):
        """
        :param address: Address of the port on which the APM is connected
        :type address: str
        :param baud: Baud rate at which data is communicated between SRT and APM
        :type: float
        :param timeout: Timeout duration of the connexion between SRT and APM
        :type timeout: float
        """

        super().__init__(parent)

        self.ser = SerialPort(address, baud, timeo=None)
        self.ser.disconnect()  # Keeps serial connection closed for safety

        self.timeout = timeout
        self.apmMsg = ""  # Stores last message from APM

        self.tracker = QTracker()

        self.tracker.start()

        self.tracking = False
        self.tracker.sendPointTo.connect(self.onTrackerSignal)
        self.trackMotionEnd.connect(self.tracker.turnOn)
        self.pauseTracking.connect(self.tracker.pause)

        self.ping = QPing()
        self.ping.start()  # Initializes pinger : still needs to be unpaused to begin pinging
        self.ping.sendPing.connect(self.onPingSignal)

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

        self.pending = False
        self.pingPending = False

        self.az, self.alt = 0, 0
        self.ra, self.dec = 0, 0
        self.long, self.lat = 0, 0

    def go_home(self, verbose=False):
        """Takes SRT to its home position and shuts motors off

        :return: Final feedback from APM
        :rtype: str"""
        if self.tracking:  # Stops tracking before
            self.stopTracking()

        self.untangle(verbose)
        return self.standby(verbose)

    def connectAPM(self, water=True):
        """
        Connects to serial port. Performs the check-in routines :

        - Unpause the QPing thread
        - Calibrate the Azimuthal encoder to NORTH
        - Untangle cables for safety and motor proper activation
        - By default launch the water evacuation process
        - Get all current coordinates from encoders

        :param water: Flag enabling the water evacuation process launch upon connection
        :type water: bool
        :return: Final feedback from APM
        :rtype: str
        """

        if self.ser.connected:
            return "SRT already connected"

        self.ser.connect()
        self.calibrate_north()  # Sets north offset
        msg = self.untangle()
        if water:  # Evacuates water in default mode
            msg = self.empty_water()

        # Get all current coords of the APM. This also resets the inactivity timer of the APM
        self.getAllCoords()

        self.ping.unpause()  # Starts pinging asa connected
        return msg

    def disconnectAPM(self):
        """Disconnects from serial port. Performs the check-out routines:

        - Stop all background threads (ping, tracker)
        - Park the mount
        - Close connection to serial port

        :return: Last feedback from APM
        :rtype: str
        """

        if not self.ser.connected:
            return "SRT already disconnected"

        self.stopTracking()

        msg = self.go_home()  # Gets SRT to home position
        self.ping.pause()  # Stop pinging

        self.ser.disconnect()  # Ciao

        return msg

    def send_APM(self, msg: str, verbose=False, save=True):
        """
        Private method monitoring the command transfer to APM via the serial port. This is the only method whatsoever
        envisioned to directly send commands to the APM.

        :param msg: Command to send to APM
        :type msg: str
        :param verbose: Debugging flag. When on, all transiting commands are printed to console
        :type verbose: bool
        :param save: When this flag is on, the last command sent is saved to the instance attribute self.apmMsg
        :type save: bool
        :return: Feedback from APM
        :rtype: str
        """

        # WAITS FOR PING RETURN

        print("DEBUG : waiting for ping to stop pending")
        while self.pingPending and msg != "ping":
            continue
        print("DEBUG : Ping stopped pending")
        self.pending = True

        if self.ser.connected:

            answer = self.ser.send_Ser(msg)  # Sends message to serial port

            self.pending = False

            # DEBUG Display answer (useful atm in cmd line)
            print(answer)

            if verbose:
                print(f"Message sent : {msg}")
            if save:
                self.apmMsg = answer  # Saves last answer from APM

            return answer

        else:
            print("APM disconnected. Aborted...")
            return ""

    def getAz(self):
        """Getter on current Azimuthal angle in degrees. In case of error
        returns -1.

        :return: Current azimuthal angle communicated by the APM encoder
        :rtype: float
        """

        try:
            az = float(self.send_APM("getAz "))
            self.az = az
            return az
        except ValueError:
            print("Error when trying to obtain current Azimuth")
            return -1

    def getAlt(self):
        """Getter on current Altitude in degrees. In case of error
        returns -1

        :return: Current elevation angle communicated by the APM encoder
        :rtype: float
        """

        try:
            alt = float(self.send_APM("getAlt "))
            self.alt = alt
            return alt
        except ValueError:
            print("Error when trying to obtain current Altitude")
            return -1

    def getAzAlt(self):
        """Getter on current position in AltAz coordinates,

        :return: Current azimuthal and elevation angles communicated by the APM encoders
        :rtype: (float, float)
        """

        az = self.getAz()
        alt = self.getAlt()

        return az, alt

    def getPos(self):
        """Returns current RaDec in degrees converted from AzAlt communicated by the APM encoders.

        :return: Current RA and DEC coordinates
        :rtype: (float, float)
        """

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
        """Returns current long/lat in galactic coordinates converted from AzAlt communicated by the APM encoders.

        :return: Current galactic longitude and latitude angles
        :rtype: (float, float)
        """

        az, alt = self.getAzAlt()
        long, lat = AzAlt2Gal(az, alt)

        return long, lat

    def getRA(self):
        """Returns current RA coordinate converted from AzAlt communicated by the APM encoders.

        :return: Current RA coordinate
        :rtype: float
        """

        ra, dec = self.getPos()

        return ra

    def getDec(self):
        """Returns current Dec converted from AzAlt communicated by the APM encoders

        :return: Current Dec coordinate
        :rtype: float
        """

        ra, dec = self.getPos()

        return dec

    def getAllCoords(self):
        """Refreshes all coordinates instance attributes from AzAlt communicated by the APM encoders."""

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
        """
        Getter on all stored current coordinates in all 3 systems : AzAlt, RaDec, Galactic. Handy for e.g. refreshing
        displayed coordinates on GUI. See mainclient.py for more.

        :return: Tuple with all coordinates in all 3 systems
        :rtype: (float, float, float, float, float, float)
        """

        return self.az, self.alt, self.ra, self.dec, self.long, self.lat

    def untangle(self, verbose=False):
        """
        Sends the command to untangle cables of the mount by azimuthal rotation back to initial position.

        :param verbose: Flag used by self.send_APM
        :type verbose: bool
        :return: Last feedback from APM
        :rtype: str
        """
        if self.tracking:  # Stops tracking before pointing
            self.stopTracking()

        if verbose:
            print("Untangling...")
        return self.send_APM("untangle ", verbose)

    def standby(self, verbose=False):
        """
        Sends the command to go back to zenith and switch off motors of the mount.

        :param verbose: Flag used by self.send_APM
        :type verbose: bool
        :return: Last feedback from APM
        :rtype: str
        """
        if self.tracking:  # Stops tracking before pointing
            self.stopTracking()

        if verbose:
            print("Going back to zenith and switching motors off...")
        return self.send_APM("stand_by ", verbose)

    def calibrate_north(self, value=NORTH, verbose=False):
        """
        Defines offset for North position in azimuthal microsteps. The curent estimation is stored in constant NORTH.

        :param verbose: Flag used by self.send_APM
        :type verbose: bool
        :return: Last feedback from APM
        :rtype: str
        """

        print(f"Calibrating North offset to value {value}")
        return self.send_APM("set_north_offset " + str(value) + " ", verbose)

    def pointAzAlt(self, az, alt, verbose=False):
        """
        Sends the command to slew to Azimuth and Altitude coordinates given in decimal degrees.

        :param az: Target Azimuth coordinate
        :type az: float
        :param alt: Target Altitude coordinate
        :type alt: float
        :param verbose: Flag used by self.send_APM
        :type verbose: bool
        :return: Last feedback from APM
        :rtype: str
        """

        if not self.tracking:  # Stops tracking before pointing
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

        print(f"{(time1 - time0) * 1000} ms")
        return answer

    def pointRaDec(self, ra, dec, verbose=False):
        """
        Sends the command to slew to Ra Dec coordinates given in respectively decimal hour,degrees.

        :param ra: Target RA coordinate
        :type ra: float
        :param dec: Target Dec coordinate
        :type dec: float
        :param verbose: Flag used by self.send_APM
        :type verbose: bool
        :return: Last feedback from APM
        :rtype: str
        """

        if verbose:
            print(f"Moving to RA={ra}, Dec = {dec}...")
        az, alt = RaDec2AzAlt(ra, dec)
        return self.pointAzAlt(az, alt, verbose)

    def pointGal(self, long, lat, verbose=False):
        """
        Sends the command to slew to Long Lat galactic coordinates given in decimal hours.

        :param long: Target longitude coordinate
        :type long: float
        :param lat: Target latitude coordinate
        :type lat: float
        :param verbose: Flag used by self.send_APM
        :type verbose: bool
        :return: Last feedback from APM
        :rtype: str
        """

        if verbose:
            print(f"Moving to long={long}, lat = {lat}...")
        az, alt = Gal2AzAlt(long, lat)
        return self.pointAzAlt(az, alt, verbose)

    def onTrackerSignal(self, az, alt):
        """
        Slot triggered when the QTracker thread emits signal to send a slewing command to APM.

        Emits the signal trackMotionEnd when the APM has returned, which in turns switches back the QTracker thread on.
        See QTracker class for more.

        :param az: Target Azimuth coordinate
        :type az: float
        :param alt: Target Altitude coordinate
        :type alt: float
        """

        if self.tracking:
            self.pointAzAlt(az, alt)
            if self.tracking:
                self.trackMotionEnd.emit()

    def onPingSignal(self):
        """Slot triggered when the QPing thread sends the signal to process the ping/pong with APM."""
        # WAITS FOR LAST MESSAGE
        while self.pending:
            continue

        self.pingPending = True
        self.send_APM("ping")
        self.pingPending = False

    def trackRaDec(self, ra, dec):
        """
        Starts tracking given coordinates in RaDec mode. See QTracker class for more about the tracking system.

        :param ra: Target RA coordinate
        :type ra: float
        :param dec: Target Dec coordinate
        :type dec: float
        """
        self.tracking = True  # Updates flag BEFORE pointing
        self.pointRaDec(
            ra, dec)  # Goes to destination before allowing other command
        # self.ping.pause()                   # Ping useless in tracking mode ACTUALLY its not, lets keep it

        if not self.tracker.isRunning():  # Launches tracker thread
            # OLD: At this point, APM not yet tracking : tracker's flag 'on' is still off
            self.tracker.start()

        self.tracker.setMode(1)
        self.tracker.setTarget(ra, dec)
        self.tracker.on = True  # Now tracking

    def trackGal(self, long, b):
        """
        Starts tracking given coordinates in Galactic mode. See QTracker class for more about the tracking system.

        :param long: Target longitude coordinate
        :type long: float
        :param b: Target latitude coordinate
        :type b: float
        """

        self.tracking = True  # Updates flag
        self.pointGal(
            long, b)  # Goes to destination before allowing other command
        # self.ping.pause()                   # Ping useless in tracking mode ACTUALLY its not, lets keep it

        if not self.tracker.isRunning():  # Launches tracker thread
            # At this point, APM not yet tracking : tracker's flag 'on' is still off
            self.tracker.start()

        mode = 2
        self.tracker.setMode(mode)
        self.tracker.setTarget(long, b)
        self.tracker.on = True  # Now tracking

    def trackSat(self, tle):
        """ 
        Starts tracking given a satellite TLE. See QTracker class for more about the tracking system.
        TODO: Implement satellite tracking

        :param tle: Target TLE
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

        # self.ping.pause()                   # Ping useless in tracking mode ACTUALLY its not, lets keep it
        self.tracking = True  # Updates flag

        if not self.tracker.isRunning():  # Launches tracker thread
            # At this point, APM not yet tracking : tracker's flag 'on' is still off
            self.tracker.start()

        mode = 3
        self.tracker.setMode(mode)
        self.tracker.setTarget(tle)
        self.tracker.on = True  # Now tracking

    def stopTracking(self):
        """
        Stops the tracking motion by pausing the QTracker thread. Unpauses the QPing thread. See QTracker class for more
        about the tracking system, QPing class for more about the ping system.

        """

        self.tracking = False  # Updates flag

        if self.tracker.isRunning():

            self.pauseTracking.emit()  # Kills tracker
            while self.tracker.pending:  # Waits for last answer from APM
                pass

        # del self.tracker                    # Deletes tracker
        # self.tracker = Tracker(self.ser)    # Prepares new tracker

        # self.ping.unpause()                 # Keep sending activity

    def empty_water(self):
        """
        Sends command to move the antenna to a position where water can flow out then goes back to
        parking position after a while. TODO : create constants with coordinates and flowing duration

        :return: An IDLE message. Handy for implementation of GUI
        :rtype: str

        """
        print("Emptying water procedure launched...")
        print("Rotating antenna towards South...")
        print(self.pointAzAlt(180, 89.9))
        print("Inclinating to evacuate water...")
        print(self.pointAzAlt(180, 5))
        timenow = time.time()
        while time.time() - timenow < 15:
            continue
        print(self.untangle())
        print(self.standby())
        print("Water evacuated. SRT is now ready for use.")
        return "IDLE"

    def waitObs(self):
        """
        Waits for the running observation to finish.
        Should only be used in command line; GUI must get
        rid of this another way round I guess...
        """

        if not self.observing:
            return

        self.obsProcess.join()
        self.observing = False

    def obsFinished(self):
        """
        Is connected to observing thread ending.
        :return:
        """
        print("Observation finished registered.")
        self.observing = False

    def stopObs(self):
        """
        Brute force kills the observation process. Be aware this can corrupt the data being acquired.
        """

        if not self.observing:
            print("ERROR : no observation to stop")
            return "ERROR : no observation to stop"

        self.obsProcess.terminate()
        self.obsFinished()
        print("Observation killed. Notice some recorded data might have been corrupted")

    def observe(self, repo=None, name=None, dev_args='hackrf=0,bias=1', rf_gain=48, if_gain=25, bb_gain=18, fc=1420e6,
                bw=2.4e6, channels=2048, t_sample=1, duration=60, overwrite=False, obs_mode=True, raw_mode=False):
        """
        Launches a parallelized observation process. All SRT methods are still callable in the meanwhile. See
        self.__observe() for more.

        :param repo: Name of the repository where to store data under DATA_PATH. If None, the name of the repo is by
            default an auto-generated timestamp
        :type repo: str
        :param name: Name of the .dat file in which the data is stored. If None, the name of the file is by default an
            auto-generated timestamp
        :type name: str
        :param dev_args: Device string used by GNU-RADIO to activate the SDR with input parameters. Default to
            'hackrf=0,bias=1' to indicate the SDR is a HackRF, and the bias-tee should be switched on to power the LNA. For
            more about the acquisition pipeline, refer to VEGA technical documentation
        :type dev_args: str
        :param rf_gain: RF gain used by the SDR
        :type rf_gain: float
        :param if_gain: Intermediate frequency gain used by the SDR
        :type if_gain: float
        :param bb_gain: Base-band gain used by the SDR
        :type bb_gain: float
        :param fc: Central frequency of the observation in MHz. Default set to H21 rest state radiation frequency.
        :type fc: float
        :param bw: Bandwidth of the observation in MHz. Notice this is the "period" of the Nyquist-Shannon signal to be
            sampled when measuring a Power Spectral Diagram
        :type bw: float
        :param channels: Numbers of channels to sample. Default value works fine
        :type: float
        :param t_sample: Sample duration in seconds
        :type: float
        :param duration: Total observation duration in seconds
        :type duration: float
        :param overwrite: Flag enabling overwriting of existing observation with same repo and name. If turned off, the
            new file with overlapping name will be added a suffix '_(i)' to its path with i an integer counter
        :type overwrite: bool
        :param obs_mode: Flag enabling processed output to be written to the repo.
        :type obs_mode: bool
        :param raw_mode: Flag enabling processed output to be written to the repo.
        :type raw_mode: bool
        """

        if self.observing:
            print("Already observing!")
            return

        self.observing = True
        self.obsProcess = QObsProcess()
        self.obsProcess.setParams(repo, name, dev_args, rf_gain, if_gain, bb_gain, fc, bw, channels, t_sample,
                                  duration, overwrite, obs_mode, raw_mode)
        self.obsProcess.setOrientation(self.ra,self.dec,self.az,self.alt)
        self.obsProcess.finished.connect(self.obsFinished)
        self.obsProcess.start()

        """
        self.obsProcess = Process(target=self.__observe, args=(
            repo, name, dev_args, rf_gain, if_gain, bb_gain, fc, bw, channels, t_sample, duration, overwrite, obs_mode,
            raw_mode))
        self.obsProcess.start()
        print(f"observing status : {self.observing}")"""

    def __observe(self, repo, name, dev_args, rf_gain, if_gain, bb_gain, fc, bw, channels, t_sample, duration,
                  overwrite, obs_mode=True, raw_mode=False):
        """
            Useless now.
            Private method that uses virgo library to observe with given parameters. 

            Recorded data is saved either under absolute path repo/name.dat, or
            relative path repo/name.dat under DATA_PATH directory. Parameters 
            are saved in a json file. See self.observe() for documentation of the method arguments.
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
            repo = DATA_PATH + repo
            if not os.path.isdir(repo):
                os.mkdir(repo)  # if not, create it
                print(f"Creating repository {repo}")

        repo = repo + '/'

        # If no indicated observation name
        if name == None:
            # Make the name to current timestamp
            name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

        name = name.strip('/')
        pathObs = repo + name

        # If overwrite flag turned off, create nth copy
        if (os.path.isfile(pathObs)) and (not overwrite):
            pathObs += "_(1)"
            while os.path.isfile(pathObs):
                digit = int(pathObs[pathObs.rfind('(') + 1:-1])
                digit += 1
                pathObs = pathObs[:pathObs.rfind('(') + 1] + str(digit) + ')'

        # Save parameters of observation for later analysis
        with open(pathObs + "_params.json", "w") as jsFile:
            json.dump(obs_params, jsFile)

        if obs_mode:
            obs_file = pathObs + '.dat'
        else:
            obs_file = "/dev/null"

        if raw_mode:
            raw_file = pathObs + '_raw.dat'
        else:
            raw_file = "/dev/null"

        virgo.observe(obs_parameters=obs_params, obs_file=obs_file, raw_file=raw_file)
        print(f"Observation complete. Data stored in {pathObs + '.dat'}")

        # /!\ SINCE multiprocessing CREATES A COPY OF THE SRT OBJECT, THE FOLLOWING
        # HAS NO EFFECT : TO BE IMPROVED
        self.observing = False

    def plotAll(self, repo, name, calib, n=20, m=35, f_rest=1420.4057517667e6,
                vlsr=False, dB=True, meta=False):
        """
        Plots full display of data using virgo library's virgo.plot function. Notice the method needs the calibration
        and the observation data files to be stored in the same repository to work properly.
        TODO: Implement better method with new acquisition pipeline.

        :param repo: Name of the repository under which data and params.json files are stored
        :type repo: str
        :param name: Name of the observation data file
        :type name: str
        :param calib: Name of the calibration data file
        :type calib: str
        :param n: TODO: understand this
        :type n: float
        :param m: TODO: understand this
        :type m: float
        :param f_rest: Center frequency at which the observation was performed. TODO: use params.json rather
        :param vlsr: TODO: understand this
        :param dB: Scales the calibrated plot in dB
        :param meta: TODO: understand this
        """

        # Formatting repo
        if not os.path.isdir(repo):
            repo = repo.strip('/')
            repo = DATA_PATH + repo + '/'

        if not repo.endswith('/'):
            repo += '/'

        # Load observation parameters
        if os.path.isfile(repo + f"/{name}_params.json"):

            with open(repo + f"/{name}_params.json", "r") as jsFile:
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

        calibPath = repo + calib
        obsPath = repo + obs

        if not os.path.isfile(calibPath):
            print(
                f"ERROR : no calibration file found at {calibPath}. Aborting...")
            return
        if not os.path.isfile(obsPath):
            print(
                f"ERROR : no observation file found at {obsPath} Aborting...")
            return

        plot_path = repo + f'plot_{name}.png'
        av_path = repo + f'average_{name}.png'
        cal_path = repo + f'calibrated_{name}.png'
        water_path = repo + f'waterfall_{name}.png'
        pow_path = repo + f'power_{name}.png'

        csv_path = repo + f'spectrum_{name}.csv'

        virgo.plot(obs_parameters=obs_params, n=n, m=m, f_rest=f_rest,
                   vlsr=vlsr, dB=dB, meta=meta,
                   obs_file=obsPath, cal_file=calibPath,
                   spectra_csv=csv_path, plot_file=plot_path, avplot_file=av_path,
                   calplot_file=cal_path, waterplot_file=water_path, powplot_file=pow_path)

        print(f"Plot saved under {plot_path}. CSV saved under {csv_path}.")

    # def obsPower(self, duration, intTime=1, bandwidth=1.024, fc=1420, repo=None, obs=None, gain=480):
    #     """ Observes PSD at center frequency fc for a duration in seconds with
    #     integration time of intTime. Bandwidth and center frequency fc are
    #     indicated in MHz
    #     OBSOLETE : uses library rtl-sdr"""
    #
    #     print(f"Observing for {duration} seconds...")
    #
    #     # If no indicated repository to save data
    #     if repo == None:
    #         # Make repo the default today's timestamp
    #         repo = datetime.today().strftime('%Y-%m-%d')
    #
    #     # Check if there exists a repo at this name
    #     if not os.path.isdir(DATA_PATH + repo):
    #         os.mkdir(DATA_PATH + repo)     # if not, create it
    #
    #     repo = DATA_PATH + repo + '/'
    #
    #     # If no indicated observation name
    #     if obs == None:
    #         # Make the name to current timestamp
    #         obs = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    #     # Check if there exists a repo at this name
    #     if not os.path.isdir(repo + obs):
    #         os.mkdir(repo + obs)     # if not, create it
    #
    #     obs = obs + '/'
    #
    #     fc *= 1e6  # MHz to Hz
    #     print(f"fc={fc}")
    #
    #     rate = bandwidth * 2e6
    #     print(f"rate = {rate}")
    #
    #     # Save parameters of observation for later analysis
    #     with open(repo+obs+"params.json", "w") as jsFile:
    #         d = {"fc": fc,
    #              "rate": rate, "channels": 1024,
    #              "gain": gain, "intTime": intTime}
    #         json.dump(d, jsFile)
    #
    #     nbSamples = rate * intTime
    #     m = np.floor(nbSamples/1024)    # Prefer a multiple of 1024 (channels)
    #     nbObs = int(np.ceil(duration/intTime))
    #
    #     for i in range(nbObs):
    #         # Collect data
    #         self.sdr.open()
    #         self.sdr.center_freq = fc
    #         self.sdr.sample_rate = rate
    #         self.gain = gain
    #         self.sdr.set_bias_tee(True)
    #         samples = self.sdr.read_samples(1024 * m)
    #
    #         print("DEBUG save")
    #         # Save data
    #         real = fits.Column(name='real', array=samples.real, format='1E')
    #         im = fits.Column(name='im', array=samples.imag, format='1E')
    #         table = fits.BinTableHDU.from_columns([real, im])
    #         table.writeto(repo + obs + "sample#" +
    #                       str(i) + '.fits', overwrite=True)
    #         self.sdr.close()
    #
    #     print(f"Observation complete. Data stored in {repo+obs}")
    #     print("Plotting averaged PSD")
    #     plotAvPSD(repo+obs)     # Plot averaged PSD


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
    """Plots the averaged PSD of the observation located in path
    EXPERIMENTAL : work in progress"""

    path = path.strip("/")
    obsName = path.split('/')[-1]  # Extract name of observation from path
    path = "/" + path + '/'  # Formatting

    # Allow for relative paths
    if not os.path.isdir(path):
        path = DATA_PATH + path

    if os.path.isfile(path + "params.json"):

        with open(path + "params.json", "r") as jsFile:
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

    for root, repo, files in os.walk(path):  # I did not find any other way...
        fitsFiles = [file for file in files if ".fits" in file]

    obsNb = len(fitsFiles)  # Number of files in observation

    firstFile = fitsFiles.pop(0)  # Pops the first element of the list
    real = fits.open(path + firstFile)[1].data.field('real').flatten()
    image = fits.open(path + firstFile)[1].data.field('im').flatten()

    for file in fitsFiles:
        data = fits.open(path + file)[1].data
        real += data.field('real').flatten()
        image += data.field('im').flatten()

    average = (real + 1.0j * image) / obsNb

    plt.psd(average, NFFT=channels, Fs=rate / 1e6, Fc=fc / 1e6)
    plt.xlabel('frequency (Mhz)')
    plt.ylabel('Relative power (db)')
    plt.savefig(path + "PSD.png", format="png")
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

class QObsProcess(QThread):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.raw_mode = None
        self.obs_mode = None
        self.overwrite = None
        self.obs_params = {
            'dev_args': '',
            'rf_gain': '',
            'if_gain': '',
            'bb_gain': '',
            'frequency': '',
            'bandwidth': '',
            'channels': '',
            't_sample': '',
            'duration': '',
            'loc': '',
            'ra': '',
            'dec': '',
            'az': '',
            'alt': ''
        }
        self.repo = None
        self.name = None
        self.ProcessObserving = False

    def setParams(self, repo, name, dev_args, rf_gain, if_gain, bb_gain, fc, bw, channels, t_sample, duration,
                  overwrite, obs_mode, raw_mode):

        self.repo = repo
        self.name = name
        self.overwrite = overwrite
        self.obs_mode = obs_mode
        self.raw_mode = raw_mode

        self.obs_params = {
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
            'ra': '',
            'dec': '',
            'az': '',
            'alt': ''
        }

    def setOrientation(self, ra, dec, az, alt):
        self.obs_params['ra'] = ra
        self.obs_params['dec'] = dec
        self.obs_params['az'] = az
        self.obs_params['alt'] = alt

    def run(self):
        self.ProcessObserving = True
        # If no indicated repository to save data
        repo = self.repo
        name = self.name
        overwrite = self.overwrite
        obs_params = self.obs_params
        obs_mode = self.obs_mode
        raw_mode = self.raw_mode

        # If no indicated repository to save data
        if repo is None:
            # Make repo the default today's timestamp
            repo = datetime.today().strftime('%Y-%m-%d')

        repo = repo.strip("/")

        # Check absolute path
        if not os.path.isdir(repo):
            # Check relative path
            repo = DATA_PATH + repo
            if not os.path.isdir(repo):
                os.mkdir(repo)  # if not, create it
                print(f"Creating repository {repo}")

        repo = repo + '/'

        # If no indicated observation name
        if name is None:
            # Make the name to current timestamp
            name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

        name = name.strip('/')
        pathObs = repo + name

        # If overwrite flag turned off, create nth copy
        if (os.path.isfile(pathObs)) and (not overwrite):
            pathObs += "_(1)"
            while os.path.isfile(pathObs):
                digit = int(pathObs[pathObs.rfind('(') + 1:-1])
                digit += 1
                pathObs = pathObs[:pathObs.rfind('(') + 1] + str(digit) + ')'

        # Save parameters of observation for later analysis
        with open(pathObs + "_params.json", "w") as jsFile:
            json.dump(obs_params, jsFile)

        if obs_mode:
            obs_file = pathObs + '.dat'
        else:
            obs_file = "/dev/null"

        if raw_mode:
            raw_file = pathObs + '_raw.dat'
        else:
            raw_file = "/dev/null"

        virgo.observe(obs_parameters=obs_params, obs_file=obs_file, raw_file=raw_file)
        print(f"Observation complete. Data stored in {pathObs + '.dat'}")

        self.ProcessObserving = False
