# -*- coding: utf-8 -*-

################################################################################
# Form generated from reading UI file 'formServerGUI.ui'
##
# Created by: Qt User Interface Compiler version 6.3.1
##
# WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QLineEdit,
                               QMainWindow, QMenuBar, QSizePolicy, QSpacerItem,
                               QSpinBox, QStatusBar, QTextBrowser, QVBoxLayout,
                               QWidget)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(374, 339)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.lineEdit_IP = QLineEdit(self.centralwidget)
        self.lineEdit_IP.setObjectName(u"lineEdit_IP")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.lineEdit_IP.sizePolicy().hasHeightForWidth())
        self.lineEdit_IP.setSizePolicy(sizePolicy1)
        self.lineEdit_IP.setMinimumSize(QSize(180, 0))
        self.lineEdit_IP.setReadOnly(True)

        self.gridLayout.addWidget(self.lineEdit_IP, 0, 1, 1, 1)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.spinBox_port = QSpinBox(self.centralwidget)
        self.spinBox_port.setObjectName(u"spinBox_port")
        sizePolicy1.setHeightForWidth(
            self.spinBox_port.sizePolicy().hasHeightForWidth())
        self.spinBox_port.setSizePolicy(sizePolicy1)
        self.spinBox_port.setMinimumSize(QSize(70, 0))
        self.spinBox_port.setMaximum(65536)
        self.spinBox_port.setValue(50885)

        self.gridLayout.addWidget(self.spinBox_port, 1, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 2, 1, 1)

        self.verticalLayout.addLayout(self.gridLayout)

        self.textBrowser_log = QTextBrowser(self.centralwidget)
        self.textBrowser_log.setObjectName(u"textBrowser_log")
        sizePolicy.setHeightForWidth(
            self.textBrowser_log.sizePolicy().hasHeightForWidth())
        self.textBrowser_log.setSizePolicy(sizePolicy)
        self.textBrowser_log.setMinimumSize(QSize(350, 200))

        self.verticalLayout.addWidget(self.textBrowser_log)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 374, 24))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate(
            "MainWindow", u"MainWindow", None))
        self.label_2.setText(QCoreApplication.translate(
            "MainWindow", u"Port", None))
        self.lineEdit_IP.setText(QCoreApplication.translate(
            "MainWindow", u"101.188.67.134", None))
        self.label.setText(QCoreApplication.translate(
            "MainWindow", u"IP Address", None))
    # retranslateUi
