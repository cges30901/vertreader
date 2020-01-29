# This Python file uses the following encoding: utf-8
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
import ebooklib
from ebooklib import epub
import tempfile
import zipfile
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import pyqtSlot
from vertreader.ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.filename = ''
        self.tempdir = tempfile.TemporaryDirectory().name
        self.book = None
        self.doc = []
        self.docIndex = 0

    @pyqtSlot()
    def on_action_Open_triggered(self):
        filename = QFileDialog.getOpenFileName(self, "", "",
            self.tr("EPUB documents (*.epub)"))[0]
        if filename:
            self.filename = filename
            self.open(filename)

    def open(self, filename):
        with zipfile.ZipFile(filename, "r") as zip_ref:
            zip_ref.extractall(self.tempdir)
            zip_ref.close()
        self.book = epub.read_epub(filename)
        for i in self.book.spine:
            item = self.book.get_item_with_id(i[0])
            self.doc.append(self.tempdir+"/OEBPS/"+item.get_name())
        if len(self.doc) > 1:
            self.btnNext.setEnabled(True)
        self.view.load(QUrl.fromLocalFile(self.doc[0]))

    @pyqtSlot(bool)
    def on_btnPrev_clicked(self):
        self.docIndex-=1
        self.btnNext.setEnabled(True)
        if self.docIndex == 1:
            self.btnPrev.setEnabled(False)
        self.view.load(QUrl.fromLocalFile(self.doc[self.docIndex]))

    @pyqtSlot(bool)
    def on_btnNext_clicked(self):
        self.docIndex+=1
        self.btnPrev.setEnabled(True)
        if self.docIndex == len(self.doc) - 1:
            self.btnNext.setEnabled(False)
        self.view.load(QUrl.fromLocalFile(self.doc[self.docIndex]))
