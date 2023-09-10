import sys
from os.path import expanduser
from time import time, localtime, strftime

from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QMainWindow
from PySide6.QtCore import Slot, QFileInfo, QTimer, Signal, QThread

from ui_form_server import Ui_MainWindow


class ServerGUI(QMainWindow):
    signalConnected = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.addToLog("Launched server.")
        self.ui.spinBox_port.value()
        self.ui.spinBox_port.valueChanged.connect(self.portChanged)

        self.setIPAddress("123.456.789.101")


    def addToLog(self, strInput):
        self.ui.textBrowser_log.append(f"{strftime('%Y-%m-%d %H:%M:%S', localtime())}: " + strInput)


    def setIPAddress(self, stringIn):
        self.ui.lineEdit_IP.setText(stringIn)
    def portChanged(self):
        print("Port changed.")


if __name__ == "__main__":
    sys.argv[0] = 'Astro Antenna'
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("Astro Antenna")

    widgetServer = ServerGUI()
    widgetServer.show()
    sys.exit(app.exec())
