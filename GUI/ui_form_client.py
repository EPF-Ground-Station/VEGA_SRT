# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'formMainClient.ui'
##
## Created by: Qt User Interface Compiler version 6.3.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFrame, QGraphicsView, QGridLayout, QHBoxLayout,
    QLabel, QLayout, QLineEdit, QProgressBar,
    QPushButton, QSizePolicy, QSpacerItem, QSpinBox,
    QTabWidget, QTextBrowser, QVBoxLayout, QWidget)

class Ui_Widget(object):
    def setupUi(self, Widget):
        if not Widget.objectName():
            Widget.setObjectName(u"Widget")
        Widget.resize(802, 840)
        self.verticalLayout = QVBoxLayout(Widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(Widget)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.tabWidget = QTabWidget(Widget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_home = QWidget()
        self.tab_home.setObjectName(u"tab_home")
        self.verticalLayout_3 = QVBoxLayout(self.tab_home)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.graphicsView = QGraphicsView(self.tab_home)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setMinimumSize(QSize(400, 300))

        self.horizontalLayout_2.addWidget(self.graphicsView)

        self.line_5 = QFrame(self.tab_home)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.VLine)
        self.line_5.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_2.addWidget(self.line_5)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_4 = QLabel(self.tab_home)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)

        self.DecLabel = QLabel(self.tab_home)
        self.DecLabel.setObjectName(u"DecLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.DecLabel.sizePolicy().hasHeightForWidth())
        self.DecLabel.setSizePolicy(sizePolicy)
        self.DecLabel.setMinimumSize(QSize(40, 0))
        self.DecLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.DecLabel, 1, 2, 1, 1)

        self.RaLabel = QLabel(self.tab_home)
        self.RaLabel.setObjectName(u"RaLabel")
        sizePolicy.setHeightForWidth(self.RaLabel.sizePolicy().hasHeightForWidth())
        self.RaLabel.setSizePolicy(sizePolicy)
        self.RaLabel.setMinimumSize(QSize(40, 0))
        self.RaLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.RaLabel, 1, 1, 1, 1)

        self.label_2 = QLabel(self.tab_home)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.label_6 = QLabel(self.tab_home)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 2, 0, 1, 1)

        self.AltLabel = QLabel(self.tab_home)
        self.AltLabel.setObjectName(u"AltLabel")
        sizePolicy.setHeightForWidth(self.AltLabel.sizePolicy().hasHeightForWidth())
        self.AltLabel.setSizePolicy(sizePolicy)
        self.AltLabel.setMinimumSize(QSize(40, 0))
        self.AltLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.AltLabel, 0, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 3, 1, 1, 1)

        self.label_GalB = QLabel(self.tab_home)
        self.label_GalB.setObjectName(u"label_GalB")
        sizePolicy.setHeightForWidth(self.label_GalB.sizePolicy().hasHeightForWidth())
        self.label_GalB.setSizePolicy(sizePolicy)
        self.label_GalB.setMinimumSize(QSize(40, 0))
        self.label_GalB.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_GalB, 2, 2, 1, 1)

        self.label_GalL = QLabel(self.tab_home)
        self.label_GalL.setObjectName(u"label_GalL")
        sizePolicy.setHeightForWidth(self.label_GalL.sizePolicy().hasHeightForWidth())
        self.label_GalL.setSizePolicy(sizePolicy)
        self.label_GalL.setMinimumSize(QSize(40, 0))
        self.label_GalL.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_GalL, 2, 1, 1, 1)

        self.AzLabel = QLabel(self.tab_home)
        self.AzLabel.setObjectName(u"AzLabel")
        sizePolicy.setHeightForWidth(self.AzLabel.sizePolicy().hasHeightForWidth())
        self.AzLabel.setSizePolicy(sizePolicy)
        self.AzLabel.setMinimumSize(QSize(40, 0))
        self.AzLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.AzLabel, 0, 2, 1, 1)


        self.horizontalLayout_2.addLayout(self.gridLayout)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(-1, 0, -1, -1)
        self.pushButton_goHome = QPushButton(self.tab_home)
        self.pushButton_goHome.setObjectName(u"pushButton_goHome")
        self.pushButton_goHome.setEnabled(0)

        self.horizontalLayout_5.addWidget(self.pushButton_goHome)

        self.pushButton_Untangle = QPushButton(self.tab_home)
        self.pushButton_Untangle.setObjectName(u"pushButton_Untangle")
        self.pushButton_Untangle.setEnabled(0)

        self.horizontalLayout_5.addWidget(self.pushButton_Untangle)

        self.pushButton_Standby = QPushButton(self.tab_home)
        self.pushButton_Standby.setObjectName(u"pushButton_Standby")
        self.pushButton_Standby.setEnabled(0)

        self.horizontalLayout_5.addWidget(self.pushButton_Standby)


        self.verticalLayout_3.addLayout(self.horizontalLayout_5)

        self.line_3 = QFrame(self.tab_home)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_3.addWidget(self.line_3)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(-1, 0, -1, -1)
        self.comboBoxTracking = QComboBox(self.tab_home)
        self.comboBoxTracking.addItem("")
        self.comboBoxTracking.addItem("")
        self.comboBoxTracking.addItem("")
        self.comboBoxTracking.setObjectName(u"comboBoxTracking")
        


        self.horizontalLayout_6.addWidget(self.comboBoxTracking)

        self.LabelTrackingFirstCoord = QLabel(self.tab_home)
        self.LabelTrackingFirstCoord.setObjectName(u"LabelTrackingFirstCoord")
        sizePolicy.setHeightForWidth(self.LabelTrackingFirstCoord.sizePolicy().hasHeightForWidth())
        self.LabelTrackingFirstCoord.setSizePolicy(sizePolicy)
        self.LabelTrackingFirstCoord.setMinimumSize(QSize(20, 0))

        self.horizontalLayout_6.addWidget(self.LabelTrackingFirstCoord)

        self.doubleSpinBox_TrackFirstCoord = QDoubleSpinBox(self.tab_home)
        self.doubleSpinBox_TrackFirstCoord.setObjectName(u"doubleSpinBox_TrackFirstCoord")
        self.doubleSpinBox_TrackFirstCoord.setDecimals(3)
        self.doubleSpinBox_TrackFirstCoord.setMinimum(-1000.000000000000000)
        self.doubleSpinBox_TrackFirstCoord.setMaximum(1000.000000000000000)

        self.horizontalLayout_6.addWidget(self.doubleSpinBox_TrackFirstCoord)

        self.LabelTrackingSecondCoord = QLabel(self.tab_home)
        self.LabelTrackingSecondCoord.setObjectName(u"LabelTrackingSecondCoord")
        sizePolicy.setHeightForWidth(self.LabelTrackingSecondCoord.sizePolicy().hasHeightForWidth())
        self.LabelTrackingSecondCoord.setSizePolicy(sizePolicy)
        self.LabelTrackingSecondCoord.setMinimumSize(QSize(30, 0))

        self.horizontalLayout_6.addWidget(self.LabelTrackingSecondCoord)

        self.doubleSpinBox_TrackSecondCoord = QDoubleSpinBox(self.tab_home)
        self.doubleSpinBox_TrackSecondCoord.setObjectName(u"doubleSpinBox_TrackSecondCoord")
        self.doubleSpinBox_TrackSecondCoord.setDecimals(3)
        self.doubleSpinBox_TrackSecondCoord.setMinimum(-1000.000000000000000)
        self.doubleSpinBox_TrackSecondCoord.setMaximum(1000.000000000000000)

        self.horizontalLayout_6.addWidget(self.doubleSpinBox_TrackSecondCoord)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_7)

        self.pushButton_GoTo = QPushButton(self.tab_home)
        self.pushButton_GoTo.setObjectName(u"pushButton_GoTo")
        self.pushButton_GoTo.setEnabled(0)

        self.horizontalLayout_6.addWidget(self.pushButton_GoTo)

        self.checkBox_Tracking = QCheckBox(self.tab_home)
        self.checkBox_Tracking.setObjectName(u"checkBox_Tracking")
        self.checkBox_Tracking.setEnabled(0)

        self.horizontalLayout_6.addWidget(self.checkBox_Tracking)

        self.line_2 = QFrame(self.tab_home)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.VLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_6.addWidget(self.line_2)

        self.pushButton_StopTracking = QPushButton(self.tab_home)
        self.pushButton_StopTracking.setObjectName(u"pushButton_StopTracking")
        self.pushButton_StopTracking.setEnabled(False)
        self.pushButton_StopTracking.setCheckable(False)
        self.pushButton_StopTracking.setFlat(False)

        self.horizontalLayout_6.addWidget(self.pushButton_StopTracking)


        self.verticalLayout_3.addLayout(self.horizontalLayout_6)

        self.line = QFrame(self.tab_home)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_3.addWidget(self.line)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.pushButton_Connect = QPushButton(self.tab_home)
        self.pushButton_Connect.setObjectName(u"pushButton_Connect")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton_Connect.sizePolicy().hasHeightForWidth())
        self.pushButton_Connect.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.pushButton_Connect)

        self.pushButton_Disconnect = QPushButton(self.tab_home)
        self.pushButton_Disconnect.setObjectName(u"pushButton_Disconnect")
        sizePolicy1.setHeightForWidth(self.pushButton_Disconnect.sizePolicy().hasHeightForWidth())
        self.pushButton_Disconnect.setSizePolicy(sizePolicy1)
        self.pushButton_Disconnect.setEnabled(False)

        self.horizontalLayout.addWidget(self.pushButton_Disconnect)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(-1, 0, -1, -1)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.ConnectedLabel = QLabel(self.tab_home)
        self.ConnectedLabel.setObjectName(u"ConnectedLabel")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.ConnectedLabel.sizePolicy().hasHeightForWidth())
        self.ConnectedLabel.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.ConnectedLabel)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_4)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)


        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.tabWidget.addTab(self.tab_home, "")
        self.tab_measure = QWidget()
        self.tab_measure.setObjectName(u"tab_measure")
        self.verticalLayout_4 = QVBoxLayout(self.tab_measure)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setSizeConstraint(QLayout.SetMinimumSize)
        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_6, 0, 0, 1, 1)

        self.label_3 = QLabel(self.tab_measure)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(0, 21))
        self.label_3.setMaximumSize(QSize(100000, 16777215))

        self.gridLayout_2.addWidget(self.label_3, 0, 1, 1, 1)

        self.label_5 = QLabel(self.tab_measure)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(0, 21))
        self.label_5.setMaximumSize(QSize(10000, 16777215))

        self.gridLayout_2.addWidget(self.label_5, 0, 3, 1, 1)

        self.label_8 = QLabel(self.tab_measure)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setMaximumSize(QSize(10000, 16777215))

        self.gridLayout_2.addWidget(self.label_8, 1, 3, 1, 1)

        self.doubleSpinBox_duration = QDoubleSpinBox(self.tab_measure)
        self.doubleSpinBox_duration.setObjectName(u"doubleSpinBox_duration")
        self.doubleSpinBox_duration.setMaximumSize(QSize(70, 16777215))
        self.doubleSpinBox_duration.setMaximum(3600.000000000000000)
        self.doubleSpinBox_duration.setValue(60.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_duration, 1, 4, 1, 1)

        self.doubleSpinBox_tsample = QDoubleSpinBox(self.tab_measure)
        self.doubleSpinBox_tsample.setObjectName(u"doubleSpinBox_tsample")
        self.doubleSpinBox_tsample.setMaximumSize(QSize(70, 16777215))
        self.doubleSpinBox_tsample.setMaximum(3600.000000000000000)
        self.doubleSpinBox_tsample.setValue(1.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_tsample, 1, 2, 1, 1)

        self.doubleSpinBox_Bandwidth = QDoubleSpinBox(self.tab_measure)
        self.doubleSpinBox_Bandwidth.setObjectName(u"doubleSpinBox_Bandwidth")
        self.doubleSpinBox_Bandwidth.setMinimumSize(QSize(0, 21))
        self.doubleSpinBox_Bandwidth.setMaximumSize(QSize(70, 16777215))
        self.doubleSpinBox_Bandwidth.setDecimals(2)
        self.doubleSpinBox_Bandwidth.setValue(2.460000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_Bandwidth, 0, 4, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_5, 0, 5, 1, 1)

        self.label_7 = QLabel(self.tab_measure)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMaximumSize(QSize(10000, 16777215))

        self.gridLayout_2.addWidget(self.label_7, 1, 1, 1, 1)

        self.label_10 = QLabel(self.tab_measure)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setMaximumSize(QSize(10000, 16777215))

        self.gridLayout_2.addWidget(self.label_10, 2, 3, 1, 1)

        self.label_9 = QLabel(self.tab_measure)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setMaximumSize(QSize(10000, 16777215))

        self.gridLayout_2.addWidget(self.label_9, 2, 1, 1, 1)

        self.doubleSpinBox_gain = QDoubleSpinBox(self.tab_measure)
        self.doubleSpinBox_gain.setObjectName(u"doubleSpinBox_gain")
        self.doubleSpinBox_gain.setMaximumSize(QSize(70, 16777215))
        self.doubleSpinBox_gain.setDecimals(1)
        self.doubleSpinBox_gain.setValue(48.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_gain, 2, 2, 1, 1)

        self.spinBox_channels = QSpinBox(self.tab_measure)
        self.spinBox_channels.setObjectName(u"spinBox_channels")
        self.spinBox_channels.setMaximumSize(QSize(70, 16777215))
        self.spinBox_channels.setMaximum(4096)
        self.spinBox_channels.setSingleStep(16)
        self.spinBox_channels.setValue(2048)

        self.gridLayout_2.addWidget(self.spinBox_channels, 2, 4, 1, 1)

        self.doubleSpinBox_centerFreq = QDoubleSpinBox(self.tab_measure)
        self.doubleSpinBox_centerFreq.setObjectName(u"doubleSpinBox_centerFreq")
        self.doubleSpinBox_centerFreq.setMinimumSize(QSize(0, 21))
        self.doubleSpinBox_centerFreq.setMaximumSize(QSize(70, 16777215))
        self.doubleSpinBox_centerFreq.setDecimals(1)
        self.doubleSpinBox_centerFreq.setMaximum(2000.000000000000000)
        self.doubleSpinBox_centerFreq.setValue(1420.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_centerFreq, 0, 2, 1, 1)


        self.verticalLayout_4.addLayout(self.gridLayout_2)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(-1, 0, -1, -1)
        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_8)

        self.pushButton_LaunchMeasurement = QPushButton(self.tab_measure)
        self.pushButton_LaunchMeasurement.setObjectName(u"pushButton_LaunchMeasurement")

        self.horizontalLayout_9.addWidget(self.pushButton_LaunchMeasurement)

        self.pushButton_StopMeasurement = QPushButton(self.tab_measure)
        self.pushButton_StopMeasurement.setObjectName(u"pushButton_StopMeasurement")

        self.horizontalLayout_9.addWidget(self.pushButton_StopMeasurement)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_9)


        self.verticalLayout_4.addLayout(self.horizontalLayout_9)

        self.label_17 = QLabel(self.tab_measure)
        self.label_17.setObjectName(u"label_17")

        self.verticalLayout_4.addWidget(self.label_17, 0, Qt.AlignHCenter)

        self.progressBar_measurement = QProgressBar(self.tab_measure)
        self.progressBar_measurement.setObjectName(u"progressBar_measurement")
        self.progressBar_measurement.setValue(0)

        self.verticalLayout_4.addWidget(self.progressBar_measurement)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(-1, 0, -1, -1)
        self.label_18 = QLabel(self.tab_measure)
        self.label_18.setObjectName(u"label_18")
        sizePolicy3 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_18.sizePolicy().hasHeightForWidth())
        self.label_18.setSizePolicy(sizePolicy3)

        self.horizontalLayout_8.addWidget(self.label_18)

        self.label_MeasureStatus = QLabel(self.tab_measure)
        self.label_MeasureStatus.setObjectName(u"label_MeasureStatus")
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.label_MeasureStatus.sizePolicy().hasHeightForWidth())
        self.label_MeasureStatus.setSizePolicy(sizePolicy4)

        self.horizontalLayout_8.addWidget(self.label_MeasureStatus)


        self.verticalLayout_4.addLayout(self.horizontalLayout_8)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)

        self.tabWidget.addTab(self.tab_measure, "")
        self.tab_plot = QWidget()
        self.tab_plot.setObjectName(u"tab_plot")
        self.verticalLayout_5 = QVBoxLayout(self.tab_plot)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_11 = QLabel(self.tab_plot)
        self.label_11.setObjectName(u"label_11")
        sizePolicy.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy)
        self.label_11.setMinimumSize(QSize(110, 0))

        self.horizontalLayout_3.addWidget(self.label_11)

        self.lineEdit_CalibFile = QLineEdit(self.tab_plot)
        self.lineEdit_CalibFile.setObjectName(u"lineEdit_CalibFile")
        self.lineEdit_CalibFile.setReadOnly(True)

        self.horizontalLayout_3.addWidget(self.lineEdit_CalibFile)

        self.pushButton_browseCalib = QPushButton(self.tab_plot)
        self.pushButton_browseCalib.setObjectName(u"pushButton_browseCalib")

        self.horizontalLayout_3.addWidget(self.pushButton_browseCalib)


        self.verticalLayout_5.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_16 = QLabel(self.tab_plot)
        self.label_16.setObjectName(u"label_16")
        sizePolicy.setHeightForWidth(self.label_16.sizePolicy().hasHeightForWidth())
        self.label_16.setSizePolicy(sizePolicy)
        self.label_16.setMinimumSize(QSize(110, 0))

        self.horizontalLayout_7.addWidget(self.label_16)

        self.lineEdit_MeasureFile = QLineEdit(self.tab_plot)
        self.lineEdit_MeasureFile.setObjectName(u"lineEdit_MeasureFile")
        self.lineEdit_MeasureFile.setReadOnly(True)

        self.horizontalLayout_7.addWidget(self.lineEdit_MeasureFile)

        self.pushButton_browseMeasureFile = QPushButton(self.tab_plot)
        self.pushButton_browseMeasureFile.setObjectName(u"pushButton_browseMeasureFile")

        self.horizontalLayout_7.addWidget(self.pushButton_browseMeasureFile)


        self.verticalLayout_5.addLayout(self.horizontalLayout_7)

        self.line_6 = QFrame(self.tab_plot)
        self.line_6.setObjectName(u"line_6")
        self.line_6.setFrameShape(QFrame.HLine)
        self.line_6.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_5.addWidget(self.line_6)

        self.pushButton_Plot = QPushButton(self.tab_plot)
        self.pushButton_Plot.setObjectName(u"pushButton_Plot")

        self.verticalLayout_5.addWidget(self.pushButton_Plot, 0, Qt.AlignHCenter)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(-1, 0, -1, -1)
        self.graphicsView_4 = QGraphicsView(self.tab_plot)
        self.graphicsView_4.setObjectName(u"graphicsView_4")

        self.gridLayout_3.addWidget(self.graphicsView_4, 3, 0, 1, 1)

        self.graphicsView_3 = QGraphicsView(self.tab_plot)
        self.graphicsView_3.setObjectName(u"graphicsView_3")

        self.gridLayout_3.addWidget(self.graphicsView_3, 1, 1, 1, 1)

        self.graphicsView_2 = QGraphicsView(self.tab_plot)
        self.graphicsView_2.setObjectName(u"graphicsView_2")

        self.gridLayout_3.addWidget(self.graphicsView_2, 1, 0, 1, 1)

        self.label_12 = QLabel(self.tab_plot)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_3.addWidget(self.label_12, 0, 0, 1, 1, Qt.AlignHCenter)

        self.graphicsView_5 = QGraphicsView(self.tab_plot)
        self.graphicsView_5.setObjectName(u"graphicsView_5")

        self.gridLayout_3.addWidget(self.graphicsView_5, 3, 1, 1, 1)

        self.label_13 = QLabel(self.tab_plot)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_3.addWidget(self.label_13, 0, 1, 1, 1, Qt.AlignHCenter)

        self.label_14 = QLabel(self.tab_plot)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout_3.addWidget(self.label_14, 2, 0, 1, 1, Qt.AlignHCenter)

        self.label_15 = QLabel(self.tab_plot)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_3.addWidget(self.label_15, 2, 1, 1, 1, Qt.AlignHCenter)


        self.verticalLayout_5.addLayout(self.gridLayout_3)

        self.tabWidget.addTab(self.tab_plot, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.line_4 = QFrame(Widget)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.HLine)
        self.line_4.setFrameShadow(QFrame.Sunken)

        self.verticalLayout.addWidget(self.line_4)

        self.textBrowser_log = QTextBrowser(Widget)
        self.textBrowser_log.setObjectName(u"textBrowser_log")
        sizePolicy5 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.textBrowser_log.sizePolicy().hasHeightForWidth())
        self.textBrowser_log.setSizePolicy(sizePolicy5)
        self.textBrowser_log.setMinimumSize(QSize(0, 200))

        self.verticalLayout.addWidget(self.textBrowser_log)


        self.retranslateUi(Widget)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Widget)
    # setupUi

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", u"Widget", None))
        self.label.setText(QCoreApplication.translate("Widget", u"Radio Antenna Connection Software ", None))
        self.label_4.setText(QCoreApplication.translate("Widget", u"Ra/Dec", None))
        self.DecLabel.setText(QCoreApplication.translate("Widget", u"-", None))
        self.RaLabel.setText(QCoreApplication.translate("Widget", u"-", None))
        self.label_2.setText(QCoreApplication.translate("Widget", u"Alt/Az", None))
        self.label_6.setText(QCoreApplication.translate("Widget", u"Gal. Coords", None))
        self.AltLabel.setText(QCoreApplication.translate("Widget", u"-", None))
        self.label_GalB.setText(QCoreApplication.translate("Widget", u"-", None))
        self.label_GalL.setText(QCoreApplication.translate("Widget", u"-", None))
        self.AzLabel.setText(QCoreApplication.translate("Widget", u"-", None))
        self.pushButton_goHome.setText(QCoreApplication.translate("Widget", u"Go Home", None))
        self.pushButton_Untangle.setText(QCoreApplication.translate("Widget", u"Untangle", None))
        self.pushButton_Standby.setText(QCoreApplication.translate("Widget", u"Standby", None))
        self.comboBoxTracking.setItemText(0, QCoreApplication.translate("Widget", u"Ra/Dec", None))
        self.comboBoxTracking.setItemText(1, QCoreApplication.translate("Widget", u"Galactic", None))
        self.comboBoxTracking.setItemText(2, QCoreApplication.translate("Widget", u"Az/Alt", None))

        self.LabelTrackingFirstCoord.setText(QCoreApplication.translate("Widget", u"Ra", None))
        self.LabelTrackingSecondCoord.setText(QCoreApplication.translate("Widget", u"Dec", None))
        self.pushButton_GoTo.setText(QCoreApplication.translate("Widget", u"Go To", None))
        self.checkBox_Tracking.setText(QCoreApplication.translate("Widget", u"Tracking", None))
        self.pushButton_StopTracking.setText(QCoreApplication.translate("Widget", u"Stop Tracking", None))
        self.pushButton_Connect.setText(QCoreApplication.translate("Widget", u"Connect", None))
        self.pushButton_Disconnect.setText(QCoreApplication.translate("Widget", u"Disconnect", None))
        self.ConnectedLabel.setText(QCoreApplication.translate("Widget", u"Connected to []", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_home), QCoreApplication.translate("Widget", u"Home", None))
        self.label_3.setText(QCoreApplication.translate("Widget", u"Center Frequency (MHz)", None))
        self.label_5.setText(QCoreApplication.translate("Widget", u"Bandwidth (MHz)", None))
        self.label_8.setText(QCoreApplication.translate("Widget", u"Duration", None))
        self.label_7.setText(QCoreApplication.translate("Widget", u"Sample Time", None))
        self.label_10.setText(QCoreApplication.translate("Widget", u"Channels", None))
        self.label_9.setText(QCoreApplication.translate("Widget", u"Gain", None))
        self.pushButton_LaunchMeasurement.setText(QCoreApplication.translate("Widget", u"Launch Measurement", None))
        self.pushButton_StopMeasurement.setText(QCoreApplication.translate("Widget", u"Stop measurement", None))
        self.label_17.setText(QCoreApplication.translate("Widget", u"Progress", None))
        self.label_18.setText(QCoreApplication.translate("Widget", u"Status:", None))
        self.label_MeasureStatus.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_measure), QCoreApplication.translate("Widget", u"Measurement", None))
        self.label_11.setText(QCoreApplication.translate("Widget", u"Calibration File", None))
        self.pushButton_browseCalib.setText(QCoreApplication.translate("Widget", u"Browse...", None))
        self.label_16.setText(QCoreApplication.translate("Widget", u"Measurement File", None))
        self.pushButton_browseMeasureFile.setText(QCoreApplication.translate("Widget", u"Browse...", None))
        self.pushButton_Plot.setText(QCoreApplication.translate("Widget", u"Plot", None))
        self.label_12.setText(QCoreApplication.translate("Widget", u"Average Spectrum", None))
        self.label_13.setText(QCoreApplication.translate("Widget", u"Calibrated Average Spectrum", None))
        self.label_14.setText(QCoreApplication.translate("Widget", u"Dynamic Spectrum (Waterfall)", None))
        self.label_15.setText(QCoreApplication.translate("Widget", u"TextLabel", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_plot), QCoreApplication.translate("Widget", u"Plot", None))
    # retranslateUi

