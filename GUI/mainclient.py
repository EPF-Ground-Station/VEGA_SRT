# This Python file uses the following encoding: utf-8
import sys
from os.path import expanduser
from time import time, localtime, strftime

from PySide6.QtWidgets import QApplication, QWidget, QFileDialog
from PySide6.QtCore import Slot, QFileInfo, QTimer, Signal
# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
import ui_form_client
import ui_form_launcher


@Slot()
def say_hello():
    print("Button clicked, Hello!")


class Launcher(QWidget):
    signalConnected = Signal()
    def __init__(self, parent=None):


        super().__init__(parent)
        self.ui = ui_form_launcher.Ui_Form()
        self.ui.setupUi(self)
        self.ui.label_Status.setText("")

        self.ui.pushButton_Connect.clicked.connect(self.ConnectClicked)

    def ConnectClicked(self):
        print("Connect")
        if (self.ui.spinBox_port.value() == 1):
            self.connected = 1
            self.signalConnected.emit()
            self.close()
        else:
            self.ui.label_Status.setText("Error of type blabla")
            self.connected = 0

class MainClient(QWidget):

    def __init__(self, parent=None):

        self.parent = parent

        self.Launcher = Launcher()
        self.Launcher.show()
        self.Launcher.raise_()
        self.Launcher.signalConnected.connect(self.initGUI)

    @Slot()
    def initGUI(self):
        super().__init__(self.parent)
        self.ui = ui_form_client.Ui_Widget()
        self.ui.setupUi(self)

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
        self.ui.pushButton_LaunchMeasurement.clicked.connect(self.LaunchMeasurementClicked)
        self.ui.pushButton_Plot.clicked.connect(self.PlotClicked)
        self.ui.pushButton_GoTo.clicked.connect(self.GoToClicked)
        self.ui.pushButton_StopTracking.clicked.connect(self.StopTrackingClicked)
        self.ui.pushButton_Connect.clicked.connect(self.ConnectClicked)
        self.ui.pushButton_Disconnect.clicked.connect(self.DisconnectClicked)

        self.ui.pushButton_browseCalib.clicked.connect(self.BrowseCalibClicked)
        self.ui.pushButton_browseMeasureFile.clicked.connect(self.BrowseMeasureClicked)

        self.ui.pushButton_Plot.clicked.connect(self.PlotClicked)

        self.ui.comboBoxTracking.currentIndexChanged.connect(self.TrackingComboBoxChanged)

        self.ui.tabWidget.setCurrentIndex(0)

        self.show()

    def GoHomeClicked(self):
        print("Go Home")

    def LaunchMeasurementClicked(self):
        if self.measuring:
            return
        self.measuring = 1
        self.ui.pushButton_LaunchMeasurement.setEnabled(0)
        self.ui.doubleSpinBox_gain.value()
        self.ui.doubleSpinBox_tsample.value()
        self.ui.doubleSpinBox_Bandwidth.value()
        self.measureDuration = self.ui.doubleSpinBox_duration.value()
        self.ui.doubleSpinBox_centerFreq.value()
        self.ui.spinBox_channels.value()

        self.ui.progressBar_measurement.setValue(0)  # from 0 to 100
        self.timerIterations = 0
        self.timerProgressBar.start(1000)  # Launch timer to update progress bar

        self.ui.label_MeasureStatus.setText('')  # measuring, saving, etc...
        print("Launch Measurement")
        self.addToLog(f"Started measurement | Center Freq.: {self.ui.doubleSpinBox_centerFreq.value()} MHz, "
                      f"Duration: {self.measureDuration} s, Gain: {self.ui.doubleSpinBox_gain.value()} dB.")

    def MeasurementDone(self):  # link to end of measurement thread!!
        self.measuring = 0
        self.ui.pushButton_LaunchMeasurement.setEnabled(1)
        self.ui.progressBar_measurement.setValue(0)
        self.ui.label_MeasureStatus.setText("Done.")

    def PlotClicked(self):
        print("Plot Measurement")

    def addToLog(self, strInput):
        self.ui.textBrowser_log.append(f"{strftime('%Y-%m-%d %H:%M:%S', localtime())}: " + strInput)

    def GoToClicked(self):
        if self.ui.checkBox_Tracking.isChecked():
            self.tracking = 1
            self.ui.pushButton_StopTracking.setEnabled(1)
            self.ui.doubleSpinBox_TrackFirstCoord.setEnabled(0)
            self.ui.doubleSpinBox_TrackSecondCoord.setEnabled(0)
            self.ui.pushButton_GoTo.setEnabled(0)
            self.ui.checkBox_Tracking.setEnabled(0)
        else:
            self.tracking = 0
            self.ui.pushButton_StopTracking.setEnabled(0)

            self.ui.doubleSpinBox_TrackFirstCoord.setEnabled(0)
            self.ui.doubleSpinBox_TrackSecondCoord.setEnabled(0)

            # Do movement

            self.ui.doubleSpinBox_TrackFirstCoord.setEnabled(1)
            self.ui.doubleSpinBox_TrackSecondCoord.setEnabled(1)

        print("Go To")

    def StopTrackingClicked(self):
        self.tracking = 0
        self.ui.pushButton_StopTracking.setEnabled(0)
        self.ui.doubleSpinBox_TrackFirstCoord.setEnabled(1)
        self.ui.doubleSpinBox_TrackSecondCoord.setEnabled(1)

        self.ui.pushButton_GoTo.setEnabled(1)
        self.ui.checkBox_Tracking.setEnabled(1)
        print("Stop Tracking")

    def ConnectClicked(self):
        print("Connect")

    def DisconnectClicked(self):
        print("Disconnect")

    def TrackingComboBoxChanged(self, index):
        if index == 0:
            self.ui.LabelTrackingFirstCoord.setText("Ra")
            self.ui.LabelTrackingSecondCoord.setText("Dec")
        if index == 1:
            self.ui.LabelTrackingFirstCoord.setText("l")
            self.ui.LabelTrackingSecondCoord.setText("b")

    def BrowseCalibClicked(self):
        if self.WorkingDirectoryCalib:
            fileName = QFileDialog.getOpenFileName(self,
                                                   "Open Data file", self.WorkingDirectoryCalib, "Data Files (*.dat)")[
                0]
        else:
            fileName = QFileDialog.getOpenFileName(self,
                                                   "Open Data file", expanduser("~"), "Data Files (*.dat)")[0]
        print(fileName)
        print(QFileInfo(fileName).absoluteDir().absolutePath())
        self.WorkingDirectoryCalib = QFileInfo(fileName).absoluteDir().absolutePath()
        if fileName:
            self.CalibFilePath = fileName
            self.ui.lineEdit_CalibFile.setText(self.CalibFilePath)

    def BrowseMeasureClicked(self):
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
        self.WorkingDirectoryMeasure = QFileInfo(fileName).absoluteDir().absolutePath()
        if fileName:
            self.MeasureFilePath = fileName
            self.ui.lineEdit_MeasureFile.setText(self.MeasureFilePath)

    def MeasureProgressBarUpdater(self):  # ProgressBar updater
        self.timerIterations += 1
        value = self.timerIterations / self.measureDuration * 100
        if 100 >= value >= 0:
            self.ui.progressBar_measurement.setValue(int(value))
            self.ui.label_MeasureStatus.setText("Measuring...")

        if value >= 100:
            self.timerProgressBar.stop()
            self.ui.progressBar_measurement.setValue(100)
            self.timerIterations = 0

            self.MeasurementDone()  # %TODO Temporary! link to thread end






if __name__ == "__main__":
    sys.argv[0] = 'Astro Antenna'
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("Astro Antenna")

    widgetMainClient = MainClient()
    #widgetMainClient.show()
    sys.exit(app.exec())
