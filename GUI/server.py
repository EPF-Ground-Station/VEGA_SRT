import sys
from os.path import expanduser
from time import time, localtime, strftime
from ...GS_interface.SRT_inline import *

from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QMainWindow
from PySide6.QtCore import Slot, QFileInfo, QTimer, Signal, QThread
from PySide6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress

from ui_form_server import Ui_MainWindow


class ServerGUI(QMainWindow):
    signalConnected = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.addToLog("Launched server.")

        self.ui.spinBox_port.valueChanged.connect(self.portChanged)

        self.IPAddress = QHostAddress("127.0.0.1")
        self.port = self.ui.spinBox_port.value()
        print(type(self.port))

        self.server = QTcpServer(self)
        self.server.listen(self.IPAddress, self.port)
        self.client_socket = None

        self.server.newConnection.connect(self.handleConnection)

    def handleConnection(self):
        if self.client_socket is None:
            self.client_socket = self.server.nextPendingConnection()
            self.client_socket.readyRead.connect(self.receiveMessage)
            self.client_socket.disconnected.connect(self.disconnectClient)
            self.addToLog("Client connected.")
            self.sendClient("CONNECTED", True)

        else:
            other_client = self.server.nextPendingConnection()
            other_client.write("BUSY".encode())
            self.addToLog(
                f"New connection rejected for a client is already connected")
            other_client.disconnectFromHost()
            other_client.deleteLater()

    def sendClient(self, msg, verbose=False):

        if self.client_socket:
            self.client_socket.write(msg.encode())
            if verbose:
                self.addToLog(f"Message sent : {msg}")
        else:
            self.addToLog(f"No connected client to send msg : {msg}")

    def receiveMessage(self):
        if self.client_socket:
            msg = self.client_socket.readAll().data().decode()
            self.addToLog("Received: " + msg)

            # You can add your processing logic here
            # if msg == "connect":

    def disconnectClient(self):
        if self.client_socket:
            self.addToLog("Client disconnected.")
            self.client_socket = None

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
