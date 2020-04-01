# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'searchdialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SearchDialog(object):
    def setupUi(self, SearchDialog):
        SearchDialog.setObjectName("SearchDialog")
        SearchDialog.resize(496, 118)
        self.horizontalLayout = QtWidgets.QHBoxLayout(SearchDialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lneSearch = QtWidgets.QLineEdit(SearchDialog)
        self.lneSearch.setObjectName("lneSearch")
        self.horizontalLayout.addWidget(self.lneSearch)
        self.btnSearch = QtWidgets.QPushButton(SearchDialog)
        self.btnSearch.setObjectName("btnSearch")
        self.horizontalLayout.addWidget(self.btnSearch)

        self.retranslateUi(SearchDialog)
        QtCore.QMetaObject.connectSlotsByName(SearchDialog)

    def retranslateUi(self, SearchDialog):
        _translate = QtCore.QCoreApplication.translate
        SearchDialog.setWindowTitle(_translate("SearchDialog", "Search"))
        self.btnSearch.setText(_translate("SearchDialog", "Search"))
