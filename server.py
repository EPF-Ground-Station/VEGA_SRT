# from GS_interface.SRT_inline import *
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
SRT = ""


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
        print(type(self.port))

        self.server = QTcpServer(self)
        self.server.listen(self.IPAddress, self.port)
        self.client_socket = None
        self.original_stdout = sys.stdout

        self.server.newConnection.connect(self.handleConnection)

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

        else:
            other_client = self.server.nextPendingConnection()
            other_client.write("BUSY".encode())
            self.addToLog(
                f"New connection rejected for a client is already connected")
            other_client.disconnectFromHost()
            other_client.deleteLater()

    def sendClient(self, msg, verbose=True):

        if self.client_socket:
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

    def redirect_stdout(self):

        sys.stdout = StdoutRedirector(sys.stdout, self.send_to_client)

    def restore_stdout(self):
        sys.stdout = self.original_stdout

    def receiveMessage(self):
        if self.client_socket:
            msg = self.client_socket.readAll().data().decode()
            self.addToLog("Received: " + msg)

            # You can add your processing logic here
            if msg == "connect":
                if not SRT.ser.connected:
                    msg = SRT.connect()
                else:
                    self.sendWarning("SRT already connected")

                self.sendOK("connected")

            elif msg == 'disconnect':
                if SRT.ser.connected:
                    msg = SRT.disconnect()
                else:
                    self.sendWarning("SRT already disconnected")

                self.sendOK("disconnected")

            elif msg == 'goHome':
                msg = SRT.goHome()
                # Post processing

            if "Err" in msg:
                self.sendError(msg)
            else:
                self.sendOK(msg)

    def disconnectClient(self):
        if self.client_socket:
            self.addToLog("Client disconnected.")
            self.client_socket = None
            # Restore sys.stdout to its original state
            self.restore_stdout()

    def closeEvent(self, event):
        if self.client_socket:
            self.client_socket.disconnectFromHost()
            self.client_socket.deleteLater()
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
        self.server.listen(self.IPAddress, self.port)


if __name__ == "__main__":
    sys.argv[0] = 'Astro Antenna'
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("Astro Antenna")

    widgetServer = ServerGUI()
    widgetServer.show()
    sys.exit(app.exec())
