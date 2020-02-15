# This Python file uses the following encoding: utf-8
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QAction, QMessageBox
from ebooklib import epub
import tempfile
import zipfile
import os
from PyQt5.QtCore import QUrl, QEvent, pyqtSlot, Qt
from vertreader.ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, args):
        super().__init__()
        self.setupUi(self)
        self.filename = args.file
        self.tempdir = ''
        self.book = None
        self.doc = []
        self.docIndex = 0
        self.toc = []
        self.view.focusProxy().installEventFilter(self)
        if self.filename:
            self.open(self.filename)

    def eventFilter(self, source, e):
        if source == self.view.focusProxy():
            # The coordinate of javascript and Qt WebEngine is different.
            # In javascript, the beginning of document is 0.
            # In Qt WebEngine, the end of document is 0.
            # So I have to convert it to use javascript to scroll.
            pos_js = self.view.page().scrollPosition().x() - self.view.page().contentsSize().width() + self.view.width()

            if e.type() == QEvent.Wheel:
                self.view.page().runJavaScript("window.scrollTo({0}, {1});"
                    .format(pos_js + e.angleDelta().y(), self.view.page().scrollPosition().y()))
                return True
            elif e.type() == QEvent.KeyPress and e.key() == Qt.Key_PageUp:
                self.view.page().runJavaScript("window.scrollTo({0}, {1});"
                    .format(pos_js + self.view.width() * 0.9, self.view.page().scrollPosition().y()))
                return True
            elif e.type() == QEvent.KeyPress and e.key() == Qt.Key_PageDown:
                self.view.page().runJavaScript("window.scrollTo({0}, {1});"
                    .format(pos_js - self.view.width() * 0.9, self.view.page().scrollPosition().y()))
                return True
        return False

    @pyqtSlot()
    def on_action_Open_triggered(self):
        filename = QFileDialog.getOpenFileName(self, "", "",
            self.tr("EPUB documents (*.epub)"))[0]
        if filename:
            self.filename = filename
            self.open(filename)

    def open(self, filename):
        self.tempdir = tempfile.TemporaryDirectory().name
        self.doc = []
        self.docIndex = 0
        with zipfile.ZipFile(filename, "r") as zip_ref:
            zip_ref.extractall(self.tempdir)
            zip_ref.close()

        # This is used instead of epub.read_epub()
        # because I need reader.opf_dir
        reader = epub.EpubReader(filename)
        self.book = reader.load()
        reader.process()

        for i in self.book.spine:
            item = self.book.get_item_with_id(i[0])
            self.doc.append(os.path.join(self.tempdir, reader.opf_dir, item.get_name()))

        def get_toc(input, level):
            toc = []
            for a in input:
                if isinstance(a, tuple):
                    toc.extend(get_toc(a, level))
                elif isinstance(a, list):
                    toc.extend(get_toc(a, level + 1))
                else:
                    fullname = os.path.join(self.tempdir, reader.opf_dir, a.href)
                    for i in range(len(self.doc)):
                        if fullname.split('#')[0] == self.doc[i]:
                            toc.append([a.title, fullname, level, i])
                            break
            return toc
        self.toc = get_toc(self.book.toc, 0)
        self.actionTOC = [QAction('>' * self.toc[x][2] + self.toc[x][0]) for x in range(len(self.toc))]
        for x in self.actionTOC:
            x.triggered.connect(self.toc_triggered)
        self.menuTOC.addActions(self.actionTOC)

        self.btnPrev.setEnabled(False)
        if len(self.doc) > 1:
            self.btnNext.setEnabled(True)
        else:
            self.btnNext.setEnabled(False)
        self.view.load(QUrl.fromLocalFile(self.doc[0]))
        self.setWindowTitle("{} - VertReader".format(self.book.get_metadata('DC', 'title')[0][0]))

    @pyqtSlot(bool)
    def toc_triggered(self):
        sender = self.sender()
        for x in range(len(self.actionTOC)):
            if self.actionTOC[x] == sender:
                self.view.load(QUrl.fromLocalFile(self.toc[x][1].split('#')[0]))
                self.docIndex = self.toc[x][3]
                if self.docIndex == 0:
                    self.btnPrev.setEnabled(False)
                else:
                    self.btnPrev.setEnabled(True)
                if self.docIndex == len(self.doc) - 1:
                    self.btnNext.setEnabled(False)
                else:
                    self.btnNext.setEnabled(True)
                break

    @pyqtSlot(bool)
    def on_btnPrev_clicked(self):
        self.docIndex -= 1
        self.btnNext.setEnabled(True)
        if self.docIndex == 0:
            self.btnPrev.setEnabled(False)
        self.view.load(QUrl.fromLocalFile(self.doc[self.docIndex]))

    @pyqtSlot(bool)
    def on_btnNext_clicked(self):
        self.docIndex += 1
        self.btnPrev.setEnabled(True)
        if self.docIndex == len(self.doc) - 1:
            self.btnNext.setEnabled(False)
        self.view.load(QUrl.fromLocalFile(self.doc[self.docIndex]))

    @pyqtSlot()
    def on_action_About_triggered(self):
        version = "0.0.1"
        QMessageBox.about(self, self.tr("About"), self.tr(
'''<h3>VertReader {0}</h3>
<p>Author: Hsiu-Ming Chang</p>
<p>e-mail: cges30901@gmail.com</p>
<p>License: GPL v3</p>''').format(version))

    @pyqtSlot()
    def on_actionLibrary_triggered(self):
        QMessageBox.about(self, self.tr("Libraries used"),
            self.tr("<h3>Libraries:</h3>") +
'''<p>PyQt5 (GPL v3)</p>
<p>EbookLib (AGPL v3)<p>''')
