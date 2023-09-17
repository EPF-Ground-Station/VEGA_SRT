# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'formLauncher.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLayout,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QSpinBox, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(400, 130)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QSize(400, 130))
        Form.setMaximumSize(QSize(400, 130))
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetFixedSize)
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.label)

        self.lineEdit_ipAddress = QLineEdit(Form)
        self.lineEdit_ipAddress.setObjectName(u"lineEdit_ipAddress")
        sizePolicy.setHeightForWidth(self.lineEdit_ipAddress.sizePolicy().hasHeightForWidth())
        self.lineEdit_ipAddress.setSizePolicy(sizePolicy)
        self.lineEdit_ipAddress.setMinimumSize(QSize(140, 0))

        self.horizontalLayout.addWidget(self.lineEdit_ipAddress)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.label_3)

        self.spinBox_port = QSpinBox(Form)
        self.spinBox_port.setObjectName(u"spinBox_port")
        sizePolicy.setHeightForWidth(self.spinBox_port.sizePolicy().hasHeightForWidth())
        self.spinBox_port.setSizePolicy(sizePolicy)
        self.spinBox_port.setMinimumSize(QSize(70, 0))
        self.spinBox_port.setMinimum(1)
        self.spinBox_port.setMaximum(65536)

        self.horizontalLayout.addWidget(self.spinBox_port)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.pushButton_Connect = QPushButton(Form)
        self.pushButton_Connect.setObjectName(u"pushButton_Connect")

        self.verticalLayout.addWidget(self.pushButton_Connect, 0, Qt.AlignHCenter)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SetFixedSize)
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")
        sizePolicy2.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.label_2)

        self.label_Status = QLabel(Form)
        self.label_Status.setObjectName(u"label_Status")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_Status.sizePolicy().hasHeightForWidth())
        self.label_Status.setSizePolicy(sizePolicy3)

        self.horizontalLayout_2.addWidget(self.label_Status)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.verticalLayout_2.addLayout(self.verticalLayout)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label.setText(QCoreApplication.translate("Form", u"IP Address", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Port", None))
        self.pushButton_Connect.setText(QCoreApplication.translate("Form", u"Connect", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Status:", None))
        self.label_Status.setText(QCoreApplication.translate("Form", u"TextLabel", None))
    # retranslateUi

