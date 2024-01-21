

from enum import Enum
from PySide6.QtCore import Slot, Signal, QThread
from ..utils.coordsConversions import *
import time

class TrackMode(Enum):
    """Tracking modes of SRT. Specifies the coordinate system to use while tracking. For now 3 options are foreseen:
    RaDec, Galactic coordinates, and TLE (satellites) tracking. TODO: Implement satellite tracking"""
    RADEC = 1
    GAL = 2
    TLE = 3     # To be implemented




class QTracker(QThread):
    """
    QThread monitoring the background commands during a track. Envisioned trackable targets are : tuples (a,b) of
    coordinates in any of the RaDec or Galactic coordinates (More might be added in future), or satellites TLEs (TODO)

    Target (a,b) or TLE are given at initialisation of the thread by user input, or modified by call to setTarget.
    During tracking, current corresponding AzAlt coordinates are regularly refreshed and the slew command to those is
    sent to APM. The rate at which these commands are sent is fixed by the TRACKING_RATE constant.

    TODO: Implement satellite tracking
    """

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
        """Refreshes AzAlt coords of target depending on the tracking mode"""

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
        """Allows to turn on tracking"""
        self.on = True

    def pause(self):
        """Allows to pause tracking"""
        self.on = False
        return
    def setMode(self, mode):
        """Sets the tracking mode.

        :param mode: Desired mode of tracking (RaDec, Gal or TLE)
        :type mode: TrackMode"""

        self.mode = TrackMode(mode)

    def setTarget(self, *args):
        """Sets target's coordinates. TODO: Implement TLE, document type of args in this case

        :param args: The target to track
        :type args: (float, float) """

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
        """Main loop of the thread. If the self.on flag is on, the tracking signal is emitted for the SRT instance to
         send the slew-to-AzAlt command to the APM every TRACKING_RATE seconds, OR as soon as the APM is IDLE.

         Notice the self.on flag is turned off after sending a slewing command. This accounts for the time the APM
         takes to execute the command and return IDLE to the SRT instance. When the IDLE feedback is received, the SRT
         instance emits a signal which turns the self.on flag back on.

         See self.onIdle and SRT class for more."""

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
                            self.waitForSat(azFuture, altFuture) # TODO: implement this
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
        """Slot triggered when SRT is ready for the next tracking motion"""

        self.on = True
