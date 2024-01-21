

from PySide6.QtCore import Signal, QThread
from .define import PING_RATE
import time


class QPing(QThread):
    """
    QThread monitoring the recurrent ping handshake with the APM. The APM is programmed to park the radiotelescope
    automatically after a certain inactivity duration. In order to prevent this parking process to trigger during
    e.g. a static measurement, or user lasting hesitation, a ping/pong is regularly performed with APM in the background
    in order to reset its inactivity timer while the SRT object is "connected".

    The rate at which these interactions are executed is fixed by the PING_RATE constant.

    Notice the thread is paused during tracking motion : since the QTracker threads sends commands continuously at high
    rate, the ping is useless in this case, and would only slow down communication with APM. See QTracker for more.
    """

    sendPing = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stop = False
        self.on = False

    def run(self):
        """
        Main loop of the thread. If the self.on flag is on, the ping signal is emitted for the SRT instance to ping the
        APM. In any case, PING_RATE seconds are waited before next iteration.
        """
        while not self.stop:
            if self.on:
                self.sendPing.emit()
            # Waits in any case
            timeNow = time.time()       # Waits before pinging again
            while time.time() < timeNow + PING_RATE:
                pass

    def stop(self):
        """
        Allows to kill the thread by switching on the stop flag
        """
        self.stop = True

    def pause(self):
        """Pauses the emission of ping signal in the main loop"""
        self.on = False

    def unpause(self):
        """Enables the emission of ping signal in the main loop"""
        self.on = True
