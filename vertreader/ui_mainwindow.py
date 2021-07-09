# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


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
        self.slider = QtWidgets.QSlider(self.centralwidget)
        self.slider.setMinimum(1)
        self.slider.setMaximum(1)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setObjectName("slider")
        self.horizontalLayout.addWidget(self.slider)
        self.txtPageNum = QtWidgets.QLabel(self.centralwidget)
        self.txtPageNum.setText("")
        self.txtPageNum.setObjectName("txtPageNum")
        self.horizontalLayout.addWidget(self.txtPageNum)
        self.verticalLayout.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 35))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuTOC = QtWidgets.QMenu(self.menubar)
        self.menuTOC.setObjectName("menuTOC")
        self.menu_Help = QtWidgets.QMenu(self.menubar)
        self.menu_Help.setObjectName("menu_Help")
        self.menu_View = QtWidgets.QMenu(self.menubar)
        self.menu_View.setObjectName("menu_View")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_Open = QtWidgets.QAction(MainWindow)
        self.action_Open.setObjectName("action_Open")
        self.action_About = QtWidgets.QAction(MainWindow)
        self.action_About.setObjectName("action_About")
        self.actionLibrary = QtWidgets.QAction(MainWindow)
        self.actionLibrary.setObjectName("actionLibrary")
        self.action_Style = QtWidgets.QAction(MainWindow)
        self.action_Style.setObjectName("action_Style")
        self.action_Metadata = QtWidgets.QAction(MainWindow)
        self.action_Metadata.setObjectName("action_Metadata")
        self.action_Search = QtWidgets.QAction(MainWindow)
        self.action_Search.setObjectName("action_Search")
        self.menuFile.addAction(self.action_Open)
        self.menuFile.addAction(self.action_Metadata)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.action_Search)
        self.menu_Help.addAction(self.action_About)
        self.menu_Help.addAction(self.actionLibrary)
        self.menu_View.addAction(self.action_Style)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menu_View.menuAction())
        self.menubar.addAction(self.menuTOC.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "VertReader"))
        self.menuFile.setTitle(_translate("MainWindow", "&File"))
        self.menuTOC.setTitle(_translate("MainWindow", "&TOC"))
        self.menu_Help.setTitle(_translate("MainWindow", "&Help"))
        self.menu_View.setTitle(_translate("MainWindow", "&View"))
        self.action_Open.setText(_translate("MainWindow", "&Open"))
        self.action_About.setText(_translate("MainWindow", "&About"))
        self.actionLibrary.setText(_translate("MainWindow", "Libraries used"))
        self.action_Style.setText(_translate("MainWindow", "&Style"))
        self.action_Metadata.setText(_translate("MainWindow", "&Metadata"))
        self.action_Search.setText(_translate("MainWindow", "&Search"))
from PyQt5 import QtWebEngineWidgets
