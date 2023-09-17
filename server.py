from GS_interface.lib.library_GS import *
import sys
from os.path import expanduser
from time import time, localtime, strftime
import io
from GUI.ui_form_server import Ui_MainWindow
import socket
from PySide6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress, QNetworkInterface, QAbstractSocket
from PySide6.QtCore import Slot, QFileInfo, QTimer, Signal, QThread
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QMainWindow
import os

sys.path.append("../")

"""
THIS SCRIPT RUNS THE SERVER IN CHARGE OF COMMUNICATING WITH THE APM

"""

SRT = Srt("/dev/ttyUSB0", 115200, 1)


class StdoutRedirector(io.StringIO):
    def __init__(self, target, callback):
        super().__init__()
        self.target = target
        self.callback = callback

    def write(self, message):

        message = "PRINT|" + message
        self.target.write(message)
        self.target.flush()
        self.callback(message)


class MotionThread(QThread):

    """Thread that parallelizes the execution of long-durationed motion tasks"""

    beginMotion = Signal()
    endMotion = Signal(str, str)

    def __init__(self,  cmd: str, a=None, b=None, parent=None):
        super().__init__(parent)

        self.cmd = cmd
        self.a = a
        self.b = b

    def run(self):  # TODO : Standby, Untangle, measurement

        self.beginMotion.emit()

        if self.cmd == "pointRA":
            self.a, self.b = RaDec2AzAlt(self.a, self.b)

        if self.cmd == "pointGal":
            self.a, self.b = Gal2AzAlt(self.a, self.b)

        if "point" in self.cmd:
            feedback = SRT.pointAzAlt(self.a, self.b)

        elif self.cmd == "goHome":
            feedback = SRT.goHome()

        elif self.cmd == "trackRA":
            feedback = SRT.trackRaDec(self.a, self.b)
        elif self.cmd == "trackGal":
            feedback = SRT.trackGal(self.a, self.b)

        elif self.cmd == "connect":
            feedback = SRT.connect()

        elif self.cmd == "disconnect":
            feedback = SRT.disconnect()

        elif self.cmd == "wait":
            pass

        feedback = str(feedback)
        self.endMotion.emit(self.cmd, feedback)


class BckgrndServTask(BckgrndTask):

    """ Background thread able to send messages to the client. 

    self.wait : Flag that indicates the message should be delayed until new order.
    Avoids spamming SRT with multiple commands. Flag risen and lowered by the
    main server thread only"""

    def __init__(self, client):

        BckgrndTask.__init__(self)
        self.client_socket = client
        self.wait = False

    def setClient(self, client):
        self.client_socket = client


class PositionThread(BckgrndServTask):

    """Thread that updates continuously the current coordinates of the antenna """

    def __init__(self, client):
        """No need to indicate a particular serial port for the thread will use 
        the global variable SRT which handles waiting for tracker/ping"""

        BckgrndServTask.__init__(self, client)

    def run(self):
        while not self.stop:

            if self.on:
                self.pending = True         # Indicates waiting for an answer
                self.sendPos()
                self.pending = False        # Answer received

                # delay next
                timeNow = time.time()
                while time.time() < timeNow + TRACKING_RATE:
                    pass

    def sendClient(self, msg, verbose=True):

        if self.client_socket:

            while self.wait:
                pass

            self.client_socket.write(msg.encode())
            if verbose:
                self.addToLog(f"Message sent : {msg}")
        else:
            self.addToLog(f"No connected client to send msg : {msg}")

    def sendOK(self, msg):

        msg = "OK|" + msg
        self.sendClient(msg)

    def sendWarning(self, msg):

        msg = "WARNING|" + msg
        self.sendClient(msg)

    def sendError(self, msg):

        msg = "ERROR|"+msg
        self.sendClient(msg)

    def sendPos(self):
        """Sends position in all coordinates to client"""

        az, alt = SRT.getAzAlt()
        ra, dec = SRT.getPos()
        long, lat = SRT.getGal()

        if (-1 in az) or (-1 in alt):
            self.sendError(
                "Error while trying to get current coordinates. Hardware may be damaged. Please report this event to the person in charge ASAP")

        msg = f"COORDS {az} {alt} {ra} {dec} {long} {lat}"
        self.sendOK(msg)


class ServerGUI(QMainWindow):
    signalConnected = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.addToLog("Launched server.")

        self.ui.spinBox_port.valueChanged.connect(self.portChanged)

        ipaddress = self.get_ipv4_address()
        self.setIPAddress(ipaddress)
        self.IPAddress = QHostAddress(ipaddress)
        self.port = self.ui.spinBox_port.value()

        self.server = QTcpServer(self)
        self.server.listen(self.IPAddress, self.port)
        self.client_socket = None
        self.original_stdout = sys.stdout

        self.server.newConnection.connect(self.handleConnection)

        self.motionThread = MotionThread("wait")
        self.motionThread.endMotion.connect(self.sendEndMotion)
        # When in motion, stop asking for position. Tracking not affected
        self.motionThread.beginMotion.connect(self.pausePosThread)

        self.posThread = PositionThread(self.client_socket)
        self.posThread.start()

    def get_ipv4_address(self):
        try:
            # Get a list of all network interfaces
            interfaces = QNetworkInterface.allInterfaces()
            for interface in interfaces:
                # Check if the interface is not loopback and is running
                if not interface.flags() & QNetworkInterface.InterfaceFlag.IsLoopBack and \
                   interface.flags() & QNetworkInterface.InterfaceFlag.IsRunning:
                    addresses = interface.addressEntries()
                    for address in addresses:
                        if address.ip().protocol() == QAbstractSocket.NetworkLayerProtocol.IPv4Protocol:
                            return address.ip().toString()
            return "Not Found"
        except Exception as e:
            return str(e)

    def handleConnection(self):
        if self.client_socket is None:
            self.client_socket = self.server.nextPendingConnection()
            self.client_socket.readyRead.connect(self.receiveMessage)
            self.client_socket.disconnected.connect(self.disconnectClient)
            self.addToLog("Client connected.")
            self.sendClient("CONNECTED", True)
            # Redirect sys.stdout to send print statements to the client
            self.redirect_stdout()
            self.posThread.setClient(self.client_socket)

        else:
            other_client = self.server.nextPendingConnection()
            other_client.write("BUSY".encode())
            self.addToLog(
                f"New connection rejected for a client is already connected")
            other_client.disconnectFromHost()
            other_client.deleteLater()

    def disconnectClient(self):
        if self.client_socket:
            self.addToLog("Client disconnected.")
            del self.client_socket
            self.client_socket = None
            # Restore sys.stdout to its original state
            self.restore_stdout()
            self.motionThread = MotionThread("disconnect")
            self.motionThread.start()
            self.posThread.setClient(None)

    def sendClient(self, msg, verbose=True):
        """Send message to client"""

        if self.client_socket:

            # Pauses the thread spamming the position getter
            if self.posThread.on:
                self.posThread.pause()

            # Waits for the previous request to have returned to avoid multiple
            # requests on the APM
            while self.posThread.pending:
                pass

            # Sends the message
            self.client_socket.write(msg.encode())
            if verbose:
                self.addToLog(f"Message sent : {msg}")

            # If tracking, the position spamming thread should be turned back on
            if SRT.tracking:
                self.posThread.unpause()

        else:
            self.addToLog(f"No connected client to send msg : {msg}")

    def sendOK(self, msg):

        msg = "OK|" + msg
        self.sendClient(msg)

    def sendWarning(self, msg):

        msg = "WARNING|" + msg
        self.sendClient(msg)

    def sendError(self, msg):

        msg = "ERROR|"+msg
        self.sendClient(msg)

    def pausePosThread(self):
        """Blocks the posThread from sending messages to the client. Called
        at beginning of motion to avoid spamming SRT with multiple commands"""

        self.posThread.wait = True  # Blocks the Pos Thread

    def sendEndMotion(self, cmd, feedback):
        """Sends message to client when motion is ended

        This is a slot connected to signal self.motionThread.endMotion"""

        self.sendClient("PRINT|" + feedback)

        if cmd == "connect":
            self.sendOK("connected")
        elif cmd == "disconnect":
            self.sendOK("disconnected")

        self.posThread.wait = False     # Unblocks the posThread
        self.sendPos()      # Sends updated position
        self.sendOK("IDLE")

    def sendPos(self):
        self.posThread.sendPos()

    def redirect_stdout(self):

        sys.stdout = StdoutRedirector(sys.stdout, self.sendClient)

    def restore_stdout(self):
        sys.stdout = self.original_stdout

    def receiveMessage(self):
        if self.client_socket:
            msg = self.client_socket.readAll().data().decode()
            self.addToLog("Received: " + msg)

            args = msg.split(" ")
            cmd = args[0]

            # Processing of command
            if cmd in ("connect", "pointRA", "pointGal ", "pointAzAlt", "trackRA", "trackGal", "goHome", "untangle", "standby", "disconnect"):

                if not self.motionThread.isRunning():

                    if len(args) > 1:
                        a, b = float(args[1]), float(args[2])
                        self.motionThread = MotionThread(cmd, a, b)
                    elif len(args) == 1:
                        self.motionThread = MotionThread(cmd)
                    else:
                        raise ValueError(
                            "ERROR : invalid command passed to server")
                    self.motionThread.start()

                else:
                    self.sendWarning("MOVING")

    def closeEvent(self, event):
        if self.client_socket:
            self.client_socket.disconnectFromHost()
        self.server.close()
        event.accept()

    def addToLog(self, strInput):
        self.ui.textBrowser_log.append(
            f"{strftime('%Y-%m-%d %H:%M:%S', localtime())}: " + strInput)

    def setIPAddress(self, stringIn):
        self.ui.lineEdit_IP.setText(stringIn)

    def portChanged(self):
        print("Port changed.")
        self.port = self.ui.spinBox_port.value()
        self.server.close()
        self.server.listen(self.IPAddress, self.port)


if __name__ == "__main__":
    sys.argv[0] = 'Astro Antenna'
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("Astro Antenna")

    widgetServer = ServerGUI()
    widgetServer.show()
    sys.exit(app.exec())
