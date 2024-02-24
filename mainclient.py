# This Python file uses the following encoding: utf-8

"""Graphical interface of the TCP client. A launcher first pops out and drives the first handshake with the server
running on the antenna's computer. Then the main window shows up (if connected to the server), allowing operation of
VEGA in an ergonomic way. This GUI allows to slew the Antenna Pointing Mechanism, acquire radio-astronomic data and
process it to plot Power Spectrum Diagram.
"""

import sys
import cv2
from lib_SRT.utils.degConversion import *
from os.path import expanduser
import time
from time import localtime, strftime

from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QVBoxLayout, QLabel
from PySide6.QtCore import Slot, QFileInfo, QTimer, Signal, QThread
from PySide6.QtNetwork import QTcpSocket
# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from GUI import ui_form_client
from GUI import ui_form_launcher

DEBUG = False
STUDENT_VERSION = True
VIDEOSOURCE = "rtsp://GroundStationEPFL:VegaStar2023@128.178.39.239/stream2"
VIDEO_RATE = 0.05  # Rate at which the video stream from camera is read


class Launcher(QWidget):
    """Widget showing at execution of the script. Manages the first handshake with the server. Allows to specify the
    server address and target port. If the server accepts the connexion, the Launcher hides and the main GUI shows.

    Note the Launcher does not have direct access to the TCP socket used for communication to the server. Instead, the
    TCP socket is owned by the MainClient object. To attempt connexion, the Launcher emits a Qt signal (connectAttempt)
    which is connected to the MainClient slot connectServ. This happens for reasons of necessary unicity of the
    reference to a QTCPsocket object and should not be changed."""

    connectAttempt = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = ui_form_launcher.Ui_Form()
        self.ui.setupUi(self)
        self.ui.label_Status.setText("")

        self.ui.pushButton_Connect.clicked.connect(self.ConnectClicked)

    def ConnectClicked(self):
        print("Trying to connect...")

        self.connectAttempt.emit()

    def updateStatus(self, msg):
        """Changes status displayed in the textbar. Allows to show error messages, or feedbacks from the server."""
        if type(msg) != str:
            raise TypeError(
                "Error : can only display strings in launcher's status")
        self.ui.label_Status.setText(msg)


class MainClient(QWidget):
    """Main class of the client GUI. It owns a Launcher object, and accesses its attributes to achieve connexion with
    the server via self.client_socket before showing.

    The window has 3 tabs : Motion, Measurements and Plot.

    - MOTION tab serves to slew the antenna to any coordinates given by user (systems available are AzAlt, RaDec and Galactic). When the "Track" box is checked, the antenna shall track the input coordinates irrespective of the coord system.

    - MEASUREMENTS tab serves to acquire data with the SDR. All parameters of the acquisition are tunable. See the antenna documentation for frequency ranges and specs of the SDR.

    - PLOT allows to show the Power Spectrum Diagram of the processed data from any chosen observation and according calibration file.

    Notice all 3 tabs are independent and methods from each can be triggered simultaneously, e.g. a measurement while
    slewing the antenna.

    See the SRT class documentation for more about calibration and observation process"""

    # I don't know why Sphinx adds line breaks in the HTML when using endlines in the bullet points and nowhere else...
    def __init__(self, parent=None):

        super().__init__(parent)

        self.measurementPrefix = ''
        self.measurementRepo = ''
        self.parent = parent
        self.SRTconnected = False

        self.ui = ui_form_client.Ui_Widget()
        self.ui.setupUi(self)
        self.hide()

        self.Launcher = Launcher()
        self.Launcher.show()
        self.Launcher.raise_()
        self.Launcher.connectAttempt.connect(self.connectServ)

        self.client_socket = QTcpSocket(self)
        self.client_socket.readyRead.connect(self.receiveMessage)
        self.client_socket.errorOccurred.connect(self.connexionError)
        self.client_socket.disconnected.connect(self.onDisconnected)

        if DEBUG: self.initGUI()
        self.ui.tabWidget.setTabEnabled(1,0)

        if STUDENT_VERSION:
            self.ui.checkBox_FFT.setChecked(0)
            self.ui.checkBox_Raw.setChecked(1)
            self.ui.checkBox_FFT.setEnabled(0)
            self.ui.checkBox_Raw.setEnabled(0)
            self.ui.MeasCheckboxFrame.hide()
            self.ui.lineEdit_measurement_directoryname.setEnabled(0)
            self.ui.tabWidget.removeTab(2)
            self.ui.lineEdit_measurement_directoryname.hide()
            self.ui.pushButton_openCamera.setEnabled(0)
            self.ui.textBrowser_log.hide()
            self.ui.label_26.hide()
            self.ui.label_28.setText("Note: filenames end in a timestamp automatically. The directory name will "
                                     "be a timestamp.")

    @Slot()
    def connectServ(self):
        """Slot activated when the "Connect" button of the launcher is pressed. Tries to connect to indicated IP address
        via TCP"""
        address = self.Launcher.ui.lineEdit_ipAddress.text()
        port = self.Launcher.ui.spinBox_port.value()
        self.Launcher.ui.label_Status.setText("Trying to connect...")
        self.Launcher.ui.pushButton_Connect.setEnabled(0)
        print(f"Attempting to connect to {address} on port {port}")
        self.client_socket.connectToHost(address, port)

    @Slot()
    def connexionError(self):
        """Triggered when self.socket_client returns error signal"""
        self.Launcher.updateStatus("Connexion failed")
        self.Launcher.ui.pushButton_Connect.setEnabled(1)

    # @Slot()
    # def onConnected(self):

    # @Slot()
    def initGUI(self):
        """Initializes the GUI appearance and features"""
        self.Launcher.hide()

        self.CalibFilePath = ''
        self.MeasureFilePath = ''
        self.WorkingDirectoryCalib = ''
        self.WorkingDirectoryMeasure = ''

        self.tracking = 0

        self.measureDuration = 0
        self.timerProgressBar = QTimer()
        self.timerProgressBar.timeout.connect(self.MeasureProgressBarUpdater)
        self.timerIterations = 0

        self.measuring = 0

        self.ui.pushButton_goHome.clicked.connect(self.GoHomeClicked)
        self.ui.pushButton_LaunchMeasurement.clicked.connect(
            self.LaunchMeasurementClicked)
        self.ui.pushButton_Plot.clicked.connect(self.PlotClicked)
        self.ui.pushButton_GoTo.clicked.connect(self.GoToClicked)
        self.ui.pushButton_StopTracking.clicked.connect(
            self.StopTrackingClicked)
        self.ui.pushButton_Connect.clicked.connect(self.ConnectClicked)
        self.ui.pushButton_Disconnect.clicked.connect(self.DisconnectClicked)
        self.ui.pushButton_Untangle.clicked.connect(self.untangleClicked)
        self.ui.pushButton_Standby.clicked.connect(self.standbyClicked)

        self.ui.pushButton_browseCalib.clicked.connect(self.BrowseCalibClicked)
        self.ui.pushButton_browseMeasureFile.clicked.connect(
            self.BrowseMeasureClicked)

        self.ui.pushButton_Plot.clicked.connect(self.PlotClicked)

        self.ui.comboBoxTracking.currentIndexChanged.connect(
            self.TrackingComboBoxChanged)
        self.ui.doubleSpinBox_TrackFirstCoordDecimal.valueChanged.connect(self.TrackFirstCoordDegreeChanged)
        self.ui.doubleSpinBox_TrackFirstCoord_h.valueChanged.connect(self.TrackFirstCoordHMSChanged)
        self.ui.doubleSpinBox_TrackFirstCoord_m.valueChanged.connect(self.TrackFirstCoordHMSChanged)
        self.ui.doubleSpinBox_TrackFirstCoord_s.valueChanged.connect(self.TrackFirstCoordHMSChanged)
        self.ui.doubleSpinBox_TrackSecondCoordDecimal.valueChanged.connect(self.TrackSecondCoordDegreeChanged)
        self.ui.doubleSpinBox_TrackSecondCoord_Deg.valueChanged.connect(self.TrackSecondCoordHMSChanged)
        self.ui.doubleSpinBox_TrackSecondCoord_m.valueChanged.connect(self.TrackSecondCoordHMSChanged)
        self.ui.doubleSpinBox_TrackSecondCoord_s.valueChanged.connect(self.TrackSecondCoordHMSChanged)

        self.ui.pushButton_Standby.setEnabled(0)
        self.ui.pushButton_Untangle.setEnabled(0)
        self.ui.pushButton_goHome.setEnabled(0)
        self.ui.pushButton_GoTo.setEnabled(0)
        self.ui.checkBox_Tracking.setEnabled(0)

        self.ui.tabWidget.setCurrentIndex(0)

        self.ui.pushButton_openCamera.clicked.connect(self.openCameraClicked)
        self.cameraThread = QCameraThread()
        self.cameraThread.closeSignalCameraThread.connect(self.cameraThreadFinished)

        self.show()

    def onDisconnected(self):
        """Triggered when the server disconnects the client, e.g. when admin closes the server, or at reboot"""
        self.addToLog("Disconnected from the server.")
        self.Launcher.updateStatus("Disconnected from the server.")

        self.initGUI()
        self.hide()
        self.Launcher.show()
        self.Launcher.ui.pushButton_Connect.setEnabled(1)
        # TODO self.client_socket disconnect?

    def sendServ(self, message):
        """Formats and sends a message to the server.

        :param message: command to send to the server. See class Server for more about commands formatting
        :type message: str"""
        if DEBUG: print(message)
        if (not self.SRTconnected) and message != "connect":
            self.addToLog("No antenna connected. Aborting...")
            return

        if message:
            message = '&' + message  # Adds a "begin" character
            self.client_socket.write(message.encode())

    def receiveMessage(self, verbose=False):
        """
        Decodes bytes sent by server to a string object which is processed by self.processMsg

        The need to process comes from concatenation of several server messages when received at too high frequency.
        To prevent this phenomenon, all messages in two-ways server-client communications begin with the character '&'.

        See self.processMsg for more about messages processing

        :param verbose: passed to processMsg for debugging, printing the received message to console
        """
        msg = self.client_socket.readAll().data().decode()
        self.processMsg(msg, verbose)

    def processMsg(self, msg, verbose):
        """
        Processes messages received from the server on the TCP socket.

        First checks for concatenated messages. If several initial '&' characters are found in msg, processes them
        one-by-one by the means of a recursive call.

        Second, triggers the correct signals/methods depending on the message. Possible actions can be : hide launcher
        and show main window ; enable grey buttons to allow sending a new slewing command ; update displayed coordinates
        ; print feedback from server to the log textbox.

        :param msg: string message received from server
        :type msg: str
        :param verbose: Debugging flag, prints msg to console
        :type verbose: bool
        """

        # Sort messages, sometimes several
        if '&' in msg:
            messages = msg.split('&')[1:]
            if len(messages) > 1:
                #print(f"Received concatenated messages : {messages}")
                for message in messages:
                    #print(f"processing msg {message}")
                    self.processMsg('&' + message, verbose)

                return

            else:
                msg = messages[0]

        else:
            self.addToLog(
                f"Warning : incorrectly formated message received : {msg}")
            return  # Ignores incorrectly formatted messages

        if verbose:
            print(msg)

        if msg == "CONNECTED":
            self.initGUI()
        elif msg == "BUSY":
            self.client_socket.disconnectFromHost()
            self.Launcher.ui.label_Status.setText(
                "Another client is already connected to the server. Try again later...")
        elif msg.startswith('PRINT'):
            msg = msg[6:]  # Gets rid of the "PRINT " statement
            self.addToLog(msg)

        elif '|' in msg:

            status, answer = msg.split('|')
            #print(status+"answer: "+answer)
            if status in ('WARNING', 'ERROR'):
                self.addToLog(status + ' ' + answer)

            if answer == 'connected':
                self.ui.pushButton_Disconnect.setEnabled(1)
                self.SRTconnected = True
                self.MovementFinished()
                self.ConnectedToMount()

            if answer == 'disconnected':
                self.ui.pushButton_Connect.setEnabled(1)
                self.SRTconnected = False
                self.DisconnectedFromMount()

            if answer == 'IDLE':
                print("new debug: IDLE received")
                self.MovementFinished()

            if "COORDS" in answer:
                #print(answer)
                az, alt, ra, dec, long, lat = answer.split(' ')[1:]
                self.setCurrentCoords(ra, dec, long, lat, az, alt)

            if answer == 'measurement_completed':
                self.MeasurementDone()

    def GoHomeClicked(self):
        self.MovementStarted()
        self.sendServ("goHome")

    def LaunchMeasurementClicked(self):
        """
        Sends to server the command to begin a measurement with parameters indicated in appropriate widgets by user.
        The progression bar corresponds to the input observation time and is not related to actual activity of the SDR.

        """

        if self.measuring:
            return
        self.measuring = 1
        self.ui.pushButton_LaunchMeasurement.setEnabled(0)

        self.measureDuration = self.ui.doubleSpinBox_duration.value()
        self.ui.progressBar_measurement.setValue(0)  # from 0 to 100
        self.timerIterations = 0
        # Launch timer to update progress bar
        self.timerProgressBar.start(1000)

        self.ui.label_MeasureStatus.setText('')  # measuring, saving, etc...

        """self.measurementRepo = self.ui.lineEdit_measurement_directoryname.text()
        if self.measurementRepo == '':
            self.measurementRepo = 'devnull'

        self.measurementPrefix = self.ui.lineEdit_measurementprefix.text()
        if self.measurementPrefix == '':
            self.measurementPrefix = 'devnull'"""


        print("Launch Measurement")
        self.addToLog(f"Started measurement | Center Freq.: {self.ui.doubleSpinBox_centerFreq.value()} MHz, "
                      f"Duration: {self.measureDuration} s")
        self.sendServ(f"measure {self.ui.lineEdit_measurement_directoryname.text()} "  # repo
                      f"{self.ui.lineEdit_measurementprefix.text()} "  # prefix
                      f"{self.ui.doubleSpinBox_rfgain.value()} "  # rf gain
                      f"{self.ui.doubleSpinBox_ifgain.value()} "  # if gain
                      f"{self.ui.doubleSpinBox_bbgain.value()} "  # bb gain
                      f"{self.ui.doubleSpinBox_centerFreq.value()*1e6} "  # fc
                      f"{self.ui.doubleSpinBox_Bandwidth.value()*1e6} "  # bw
                      f"{self.ui.spinBox_channels.value()} "  # channels
                      f"{self.ui.doubleSpinBox_tsample.value()} "  # sample_t
                      f"{self.ui.doubleSpinBox_duration.value()} "  # duration
                      f"{int(self.ui.checkBox_FFT.isChecked())} "  # obs_mode
                      f"{int(self.ui.checkBox_Raw.isChecked())} "
                      f"{int(STUDENT_VERSION)}")  # raw_mode

    def MeasurementDone(self):  # link to end of measurement thread!!
        """
        Triggered when the server confirms the measurement is over.
        """
        self.MeasureProgressBarUpdater(101)
        self.measuring = 0
        self.ui.pushButton_LaunchMeasurement.setEnabled(1)
        self.ui.progressBar_measurement.setValue(0)
        self.ui.label_MeasureStatus.setText("Done.")

    def PlotClicked(self):
        print("Plot Measurement")

    def addToLog(self, strInput):
        """
        Adds a string to the log text box with timestamp.

        :param strInput: message to log
        :return: str
        """

        self.ui.textBrowser_log.append(
            f"{strftime('%Y-%m-%d %H:%M:%S', localtime())}: " + strInput)

    def GoToClicked(self):
        """
        Processes and sends the command to slew VEGA to input coordinates. Depending on the coordinate system and if
        tracking is enabled, the sent command varies. See class ServerGUI for more about commands formatting.

        Note the signal MovementStarted has the effect to disable several buttons, waiting for the server to confirm
        the motion of the mount is over nefore allowing sending a new slew command.
        """

        # valeurs:
        self.MovementStarted()

        if self.ui.checkBox_Tracking.isChecked():
            self.tracking = 1
            self.ui.pushButton_StopTracking.setEnabled(1)
            self.ui.doubleSpinBox_TrackFirstCoordDecimal.setEnabled(0)
            self.ui.doubleSpinBox_TrackFirstCoord_h.setEnabled(0)
            self.ui.doubleSpinBox_TrackFirstCoord_m.setEnabled(0)
            self.ui.doubleSpinBox_TrackFirstCoord_s.setEnabled(0)
            self.ui.doubleSpinBox_TrackSecondCoordDecimal.setEnabled(0)
            self.ui.doubleSpinBox_TrackSecondCoord_Deg.setEnabled(0)
            self.ui.doubleSpinBox_TrackSecondCoord_m.setEnabled(0)
            self.ui.doubleSpinBox_TrackSecondCoord_s.setEnabled(0)
            self.ui.comboBoxTracking.setEnabled(0)
            self.ui.checkBox_Tracking.setEnabled(0)

            # valeurs
        else:
            self.tracking = 0
            self.ui.pushButton_StopTracking.setEnabled(0)
            # self.ui.doubleSpinBox_TrackFirstCoordDecimal.setEnabled(0)
            # self.ui.doubleSpinBox_TrackSecondCoordDecimal.setEnabled(0)

            # Do movement

            # self.ui.doubleSpinBox_TrackFirstCoord.setEnabled(1)
            # self.ui.doubleSpinBox_TrackSecondCoord.setEnabled(1)
        message = ''
        if self.ui.comboBoxTracking.currentIndex() == 2 and self.ui.checkBox_Tracking.isChecked():  # should not happen
            message = 'point'
        else:
            if self.ui.checkBox_Tracking.isChecked():
                message = 'track'
            else:
                message = 'point'

            if self.ui.comboBoxTracking.currentIndex() == 0:  # Ra Dec
                message += 'RA'

            if self.ui.comboBoxTracking.currentIndex() == 1:  # Galactic
                message += 'Gal'

            if self.ui.comboBoxTracking.currentIndex() == 2:  # Az Alt
                message += "AzAlt"

            message += f" {self.ui.doubleSpinBox_TrackFirstCoordDecimal.value()} {self.ui.doubleSpinBox_TrackSecondCoordDecimal.value()}"

        self.sendServ(message)

    def StopTrackingClicked(self):
        """
        Triggered  when the "Stop Tracking" button is pushed. Sends to the server the command to stop tracking the
        target.
        """

        self.tracking = 0
        self.ui.pushButton_StopTracking.setEnabled(0)
        self.ui.doubleSpinBox_TrackFirstCoordDecimal.setEnabled(1)
        self.ui.doubleSpinBox_TrackFirstCoord_h.setEnabled(1)
        self.ui.doubleSpinBox_TrackFirstCoord_m.setEnabled(1)
        self.ui.doubleSpinBox_TrackFirstCoord_s.setEnabled(1)
        self.ui.doubleSpinBox_TrackSecondCoordDecimal.setEnabled(1)
        self.ui.doubleSpinBox_TrackSecondCoord_Deg.setEnabled(1)
        self.ui.doubleSpinBox_TrackSecondCoord_m.setEnabled(1)
        self.ui.doubleSpinBox_TrackSecondCoord_s.setEnabled(1)
        self.ui.comboBoxTracking.setEnabled(1)
        self.ui.checkBox_Tracking.setEnabled(1)

        self.ui.pushButton_GoTo.setEnabled(1)
        self.ui.checkBox_Tracking.setEnabled(1)
        self.sendServ("stopTracking")
        self.addToLog("Tracking stopped")

    def MovementFinished(self):
        """
        Slot triggered when the server sends the message IDLE, meaning the mount has finished its slew and is ready for
        new slewing command.
        """

        self.ui.pushButton_StopTracking.setEnabled(0)
        self.ui.pushButton_Standby.setEnabled(1)
        self.ui.pushButton_Untangle.setEnabled(1)
        self.ui.pushButton_goHome.setEnabled(1)
        self.ui.pushButton_GoTo.setEnabled(1)
        self.ui.checkBox_Tracking.setEnabled(1)

    def MovementStarted(self):
        """
        Triggered when a slewing command is sent to server. Disables most button from Motion tab, waiting for the sever
        to send IDLE before re-enabling them.
        """

        self.ui.pushButton_Standby.setEnabled(0)
        self.ui.pushButton_Untangle.setEnabled(0)
        self.ui.pushButton_goHome.setEnabled(0)
        self.ui.pushButton_GoTo.setEnabled(0)
        self.ui.checkBox_Tracking.setEnabled(0)
        pass

    def ConnectClicked(self):
        """
        Sends the command to connect the mount. This usually triggers the water evacuation process.
        """
        self.sendServ("connect")
        self.ui.pushButton_Connect.setEnabled(0)


    def DisconnectClicked(self):
        """
        Sends the command to disconnect the mount. Usually triggers the untangling of cables and parking to standby
        (zenith) position.
        """

        self.ui.pushButton_Disconnect.setEnabled(0)
        self.sendServ("disconnect")
        self.DisconnectedFromMount()
        print("Disconnect")

    def ConnectedToMount(self):
        self.ui.ConnectedLabel.setText("Connected to SRT")
        self.ui.pushButton_Connect.setEnabled(0)
        self.ui.pushButton_Disconnect.setEnabled(1)
        self.ui.tabWidget.setTabEnabled(1, 1)

    def DisconnectedFromMount(self):
        self.ui.ConnectedLabel.setText("Disconnected from SRT")
        self.ui.pushButton_Connect.setEnabled(1)
        self.ui.pushButton_Disconnect.setEnabled(0)
        self.ui.tabWidget.setTabEnabled(1, 0)


    def TrackFirstCoordDegreeChanged(self, val):
        (h, m, s) = DegtoHMS(val)
        self.ui.doubleSpinBox_TrackFirstCoord_h.blockSignals(1)
        self.ui.doubleSpinBox_TrackFirstCoord_m.blockSignals(1)
        self.ui.doubleSpinBox_TrackFirstCoord_s.blockSignals(1)

        self.ui.doubleSpinBox_TrackFirstCoord_h.setValue(h)
        self.ui.doubleSpinBox_TrackFirstCoord_m.setValue(m)
        self.ui.doubleSpinBox_TrackFirstCoord_s.setValue(s)

        self.ui.doubleSpinBox_TrackFirstCoord_h.blockSignals(0)
        self.ui.doubleSpinBox_TrackFirstCoord_m.blockSignals(0)
        self.ui.doubleSpinBox_TrackFirstCoord_s.blockSignals(0)

    def TrackFirstCoordHMSChanged(self, val):
        self.ui.doubleSpinBox_TrackFirstCoordDecimal.blockSignals(1)
        self.ui.doubleSpinBox_TrackFirstCoordDecimal.setValue(HMStoDeg(self.ui.doubleSpinBox_TrackFirstCoord_h.value(),
                                                                       self.ui.doubleSpinBox_TrackFirstCoord_m.value(),
                                                                       self.ui.doubleSpinBox_TrackFirstCoord_s.value()))
        self.ui.doubleSpinBox_TrackFirstCoordDecimal.blockSignals(0)

    def TrackSecondCoordDegreeChanged(self, val):
        (h, m, s) = DegtoDMS(val)
        self.ui.doubleSpinBox_TrackSecondCoord_Deg.blockSignals(1)
        self.ui.doubleSpinBox_TrackSecondCoord_m.blockSignals(1)
        self.ui.doubleSpinBox_TrackSecondCoord_s.blockSignals(1)

        self.ui.doubleSpinBox_TrackSecondCoord_Deg.setValue(h)
        self.ui.doubleSpinBox_TrackSecondCoord_m.setValue(m)
        self.ui.doubleSpinBox_TrackSecondCoord_s.setValue(s)

        self.ui.doubleSpinBox_TrackSecondCoord_Deg.blockSignals(0)
        self.ui.doubleSpinBox_TrackSecondCoord_m.blockSignals(0)
        self.ui.doubleSpinBox_TrackSecondCoord_s.blockSignals(0)

    def TrackSecondCoordHMSChanged(self, val):
        self.ui.doubleSpinBox_TrackSecondCoordDecimal.blockSignals(1)
        self.ui.doubleSpinBox_TrackSecondCoordDecimal.setValue(
            DMStoDeg(self.ui.doubleSpinBox_TrackSecondCoord_Deg.value(),
                     self.ui.doubleSpinBox_TrackSecondCoord_m.value(),
                     self.ui.doubleSpinBox_TrackSecondCoord_s.value()))
        self.ui.doubleSpinBox_TrackSecondCoordDecimal.blockSignals(0)

    def TrackingComboBoxChanged(self, index):
        if index == 0:
            self.ui.LabelTrackingFirstCoord.setText("Ra")
            self.ui.LabelTrackingSecondCoord.setText("Dec")
            self.ui.checkBox_Tracking.setEnabled(1)
        if index == 1:
            self.ui.LabelTrackingFirstCoord.setText("l")
            self.ui.LabelTrackingSecondCoord.setText("b")
            self.ui.checkBox_Tracking.setEnabled(1)
        if index == 2:
            self.ui.LabelTrackingFirstCoord.setText("Az")
            self.ui.LabelTrackingSecondCoord.setText("Alt")
            self.ui.checkBox_Tracking.setChecked(0)
            self.ui.checkBox_Tracking.setEnabled(0)

    def BrowseCalibClicked(self):

        """Opens the file browser for the user to choose the calibration data file"""

        if self.WorkingDirectoryCalib:
            fileName = QFileDialog.getOpenFileName(self,
                                                   "Open Data file", self.WorkingDirectoryCalib, "Data Files (*.dat)")[
                0]
        else:
            fileName = QFileDialog.getOpenFileName(self,
                                                   "Open Data file", expanduser("~"), "Data Files (*.dat)")[0]
        print(fileName)
        print(QFileInfo(fileName).absoluteDir().absolutePath())
        self.WorkingDirectoryCalib = QFileInfo(
            fileName).absoluteDir().absolutePath()
        if fileName:
            self.CalibFilePath = fileName
            self.ui.lineEdit_CalibFile.setText(self.CalibFilePath)

    def BrowseMeasureClicked(self):
        """Opens the file browser for the user to choose the observation data file"""
        if self.WorkingDirectoryMeasure:
            fileName = QFileDialog.getOpenFileName(self,
                                                   "Open Data file", self.WorkingDirectoryMeasure,
                                                   "Data Files (*.dat)")[
                0]
        else:
            fileName = QFileDialog.getOpenFileName(self,
                                                   "Open Data file", expanduser("~"), "Data Files (*.dat)")[0]
        print(fileName)
        print(QFileInfo(fileName).absoluteDir().absolutePath())
        self.WorkingDirectoryMeasure = QFileInfo(
            fileName).absoluteDir().absolutePath()
        if fileName:
            self.MeasureFilePath = fileName
            self.ui.lineEdit_MeasureFile.setText(self.MeasureFilePath)

    def MeasureProgressBarUpdater(self, valueOverride=-1):  # ProgressBar updater
        self.timerIterations += 1
        if valueOverride == -1:
            value = self.timerIterations / (self.measureDuration+5) * 100
        else:
            value = valueOverride

        if 100 >= value >= 0:
            self.ui.progressBar_measurement.setValue(int(value))
            self.ui.label_MeasureStatus.setText("Measuring...")

        if value >= 100:
            self.timerProgressBar.stop()
            self.ui.progressBar_measurement.setValue(100)
            self.timerIterations = 0

            # self.MeasurementDone()  # %TODO Temporary! link to thread end

    def untangleClicked(self):
        """Sends command to untangle the cables of the mount by azimuthal rotation back to parking position"""
        self.sendServ("untangle")

    def standbyClicked(self):
        """Sends command to park the mount by elevation slew to zenith"""
        self.sendServ("standby")

    def setCurrentCoords(self, *args):
        """
        Internal methods. Updates displayed coordinates of the mount.

        :param args: a tuple containing the current coordinates to display in all systems
        :type args: tuple of str
        """

        args = [float(elt) for elt in args]

        Ra, Dec, GalL, GalB, Az, Alt = args

        self.ui.RaLabel.setText(f"{Ra:.2f}")
        self.ui.DecLabel.setText(f"{Dec:.2f}")
        self.ui.label_GalL.setText(f"{GalL:.2f}")
        self.ui.label_GalB.setText(f"{GalB:.2f}")
        self.ui.AltLabel.setText(f"{Alt:.2f}")
        self.ui.AzLabel.setText(f"{Az:.2f}")

    def openCameraClicked(self):
        """Triggered when the 'Open Camera' button is pushed by user. Opens/closes a window displaying the video stream
         of VEGA's camera. Notice the text switches to Close Camera, but the button is still the same"""

        if not self.cameraThread.on:
            self.cameraThread = QCameraThread()
            self.cameraThread.display_image_widget.closeSignal.connect(self.openCameraClicked)
            self.cameraThread.turnOn()
            # self.ui.pushButton_openCamera.setText("Close Camera")
            self.ui.pushButton_openCamera.setEnabled(0)
        else:
            self.cameraThread.turnOff()
            while self.cameraThread.isRunning():
                pass
            # self.cameraThread.exit()
            self.cameraThread = QCameraThread()
            # self.ui.pushButton_openCamera.setText("Open Camera")
            self.ui.pushButton_openCamera.setEnabled(1)

    def cameraThreadFinished(self):
        """Triggered when the camera window is closed"""

        print("triggered")
        self.ui.pushButton_openCamera.setText("Open Camera")
        while self.cameraThread.isRunning():
            pass
        print("check")
        self.cameraThread = QCameraThread()


class QCameraThread(QThread):
    """
    Thread handling the display of the camera stream
    """

    closeSignalCameraThread = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.on = False

        self.display_image_widget = DisplayImageWidget()
        # self.display_image_widget.closeSignal.connect(self.CustomClose)

    def turnOff(self):
        self.on = False
        if VIDEOSOURCE == '':
            return
        self.display_image_widget.close()

    def turnOn(self):
        self.on = True
        self.display_image_widget.show()
        self.start()

    """def CustomClose(self):
        print("customclosed")
        self.closeSignalCameraThread.emit()
        self.on=False"""

    def run(self):

        if VIDEOSOURCE == '':
            return

        self.cap = cv2.VideoCapture(VIDEOSOURCE)
        self.FRAME_WIDTH = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.FRAME_HEIGHT = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print('Frame Size: ', self.FRAME_WIDTH, 'x', self.FRAME_HEIGHT)

        self.ret = False
        self.frame = None
        if self.cap.isOpened():
            self.ret, self.frame = self.cap.read()

        while self.ret and self.on:
            # print("loading")
            self.ret, self.frame = self.cap.read()
            if self.frame is not None: self.display_image_widget.show_image(self.frame)
            time.sleep(VIDEO_RATE)
            # cv2.imshow('Camera', self.frame)


class DisplayImageWidget(QWidget):
    """
    Widget on which the camera stream is displayed
    """

    closeSignal = Signal()

    def __init__(self, parent=None):
        super(DisplayImageWidget, self).__init__(parent)

        self.image_frame = QLabel()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.image_frame)
        self.setLayout(self.layout)

    def closeEvent(self, event):
        """Override of the closeEvent method inherited from the Widget class in order to properly handle the destruction
        of the QCameraThread object"""

        event.ignore()
        self.closeSignal.emit()

    @Slot()
    def show_image(self, cap):
        """Slot in charge of refreshing the camera stream frame.
        """

        scale_percent = 100  # percent of original size
        width = int(cap.shape[1] * scale_percent / 100)
        height = int(cap.shape[0] * scale_percent / 100)
        dim = (width, height)

        # resize image
        resized = cv2.resize(cap, dim, interpolation=cv2.INTER_AREA)
        # cv2.imshow("1", cap)
        # cv2.waitKey(0)
        height, width, channel = resized.shape
        self.image_frame.setPixmap(
            QPixmap.fromImage(QImage(resized.data, width, height, 3 * width, QImage.Format_BGR888)))


if __name__ == "__main__":
    sys.argv[0] = 'VEGA - Callista'
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("VEGA - Callista")

    widgetMainClient = MainClient()
    # widgetMainClient.show()
    sys.exit(app.exec())
