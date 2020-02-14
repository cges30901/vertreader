# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.view = QtWebEngineWidgets.QWebEngineView(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.view.sizePolicy().hasHeightForWidth())
        self.view.setSizePolicy(sizePolicy)
        self.view.setUrl(QtCore.QUrl("about:blank"))
        self.view.setObjectName("view")
        self.verticalLayout.addWidget(self.view)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnNext = QtWidgets.QPushButton(self.centralwidget)
        self.btnNext.setEnabled(False)
        self.btnNext.setObjectName("btnNext")
        self.horizontalLayout.addWidget(self.btnNext)
        self.btnPrev = QtWidgets.QPushButton(self.centralwidget)
        self.btnPrev.setEnabled(False)
        self.btnPrev.setObjectName("btnPrev")
        self.horizontalLayout.addWidget(self.btnPrev)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 35))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuTOC = QtWidgets.QMenu(self.menubar)
        self.menuTOC.setObjectName("menuTOC")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_Open = QtWidgets.QAction(MainWindow)
        self.action_Open.setObjectName("action_Open")
        self.menuFile.addAction(self.action_Open)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuTOC.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "VertReader"))
        self.btnNext.setText(_translate("MainWindow", "&Next"))
        self.btnPrev.setText(_translate("MainWindow", "&Previous"))
        self.menuFile.setTitle(_translate("MainWindow", "&File"))
        self.menuTOC.setTitle(_translate("MainWindow", "&TOC"))
        self.action_Open.setText(_translate("MainWindow", "&Open"))
from PyQt5 import QtWebEngineWidgets
