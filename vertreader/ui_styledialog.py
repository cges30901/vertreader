# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'styledialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_StyleDialog(object):
    def setupUi(self, StyleDialog):
        StyleDialog.setObjectName("StyleDialog")
        StyleDialog.resize(541, 455)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(StyleDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(StyleDialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.spbZoom = QtWidgets.QDoubleSpinBox(StyleDialog)
        self.spbZoom.setMinimum(0.25)
        self.spbZoom.setMaximum(5.0)
        self.spbZoom.setSingleStep(0.1)
        self.spbZoom.setProperty("value", 1.0)
        self.spbZoom.setObjectName("spbZoom")
        self.horizontalLayout.addWidget(self.spbZoom)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(StyleDialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.btnColor = QtWidgets.QPushButton(StyleDialog)
        self.btnColor.setStyleSheet("border: none")
        self.btnColor.setText("")
        self.btnColor.setObjectName("btnColor")
        self.horizontalLayout_2.addWidget(self.btnColor)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(StyleDialog)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.btnBgColor = QtWidgets.QPushButton(StyleDialog)
        self.btnBgColor.setStyleSheet("border: none")
        self.btnBgColor.setText("")
        self.btnBgColor.setObjectName("btnBgColor")
        self.horizontalLayout_3.addWidget(self.btnBgColor)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.chbVertical = QtWidgets.QCheckBox(StyleDialog)
        self.chbVertical.setObjectName("chbVertical")
        self.verticalLayout_2.addWidget(self.chbVertical)
        spacerItem3 = QtWidgets.QSpacerItem(20, 293, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem3)
        self.buttonBox = QtWidgets.QDialogButtonBox(StyleDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(StyleDialog)
        self.buttonBox.accepted.connect(StyleDialog.accept)
        self.buttonBox.rejected.connect(StyleDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(StyleDialog)

    def retranslateUi(self, StyleDialog):
        _translate = QtCore.QCoreApplication.translate
        StyleDialog.setWindowTitle(_translate("StyleDialog", "Style"))
        self.label.setText(_translate("StyleDialog", "Zoom Factor:"))
        self.label_2.setText(_translate("StyleDialog", "Text color:"))
        self.label_3.setText(_translate("StyleDialog", "Background color:"))
        self.chbVertical.setText(_translate("StyleDialog", "Force vertical writing"))