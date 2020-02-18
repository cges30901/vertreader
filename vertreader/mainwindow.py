# This Python file uses the following encoding: utf-8
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QAction, QMessageBox, QApplication
from ebooklib import epub
import tempfile
import zipfile
import os
from PyQt5.QtCore import QUrl, QEvent, pyqtSlot, Qt, QSettings
from PyQt5.QtGui import QIcon
from vertreader.ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, args):
        super().__init__()
        self.setWindowIcon(QIcon(os.path.dirname(os.path.abspath(__file__))+'/vertreader.svg'))
        self.setupUi(self)
        self.filename = args.file
        self.tempdir = ''
        self.book = None
        self.doc = []
        self.docIndex = 0
        self.toc = []
        self.need_scroll = False
        self.view.focusProxy().installEventFilter(self)
        QApplication.instance().aboutToQuit.connect(self.writeSettings)
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
            self.writeSettings()
            self.filename = filename
            self.open(filename)

    def open(self, filename):
        self.tempdir = tempfile.TemporaryDirectory().name
        self.doc = []
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

        settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "cges30901", "VertReader")
        settings.beginGroup(self.filename.replace('/', '>').replace('\\', '>'))
        self.docIndex = int(settings.value("index", 0))
        settings.endGroup()
        self.need_scroll = True
        self.setButtons()

        self.view.load(QUrl.fromLocalFile(self.doc[self.docIndex]))
        self.setWindowTitle("{} - VertReader".format(self.book.get_metadata('DC', 'title')[0][0]))

    @pyqtSlot(bool)
    def toc_triggered(self):
        sender = self.sender()
        for x in range(len(self.actionTOC)):
            if self.actionTOC[x] == sender:
                href_split = self.toc[x][1].split('#', 1)
                url = QUrl.fromLocalFile(href_split[0])
                if len(href_split) > 1:
                    url.setFragment(self.toc[x][1].split('#', 1)[1])
                self.view.load(url)

                self.docIndex = self.toc[x][3]
                self.setButtons()
                break

    @pyqtSlot(bool)
    def on_btnPrev_clicked(self):
        self.docIndex -= 1
        self.setButtons()
        self.view.load(QUrl.fromLocalFile(self.doc[self.docIndex]))

    @pyqtSlot(bool)
    def on_btnNext_clicked(self):
        self.docIndex += 1
        self.setButtons()
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

    @pyqtSlot()
    def writeSettings(self):
        # No need to write settings if no file is loaded
        if self.view.url().fileName() == 'blank':
            return
        settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "cges30901", "VertReader")
        # replace slash and backslash with '>'
        # because they have special meaning in QSettings
        settings.beginGroup(self.filename.replace('/', '>').replace('\\', '>'))
        settings.setValue("index", self.docIndex)
        settings.setValue("posX", self.view.page().scrollPosition().x()
            - self.view.page().contentsSize().width() + self.view.width())
        settings.setValue("posY", self.view.page().scrollPosition().y())
        settings.endGroup()

    @pyqtSlot(bool)
    def on_view_loadFinished(self):
        if self.need_scroll is True:
            self.need_scroll = False
            settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "cges30901", "VertReader")
            settings.beginGroup(self.filename.replace('/', '>').replace('\\', '>'))
            self.view.page().runJavaScript("window.scrollTo({0}, {1});"
                .format(settings.value("posX", 0), settings.value("posY", 0)))
            settings.endGroup()

    def setButtons(self):
        if self.docIndex == 0:
            self.btnPrev.setEnabled(False)
        else:
            self.btnPrev.setEnabled(True)
        if self.docIndex == len(self.doc) - 1:
            self.btnNext.setEnabled(False)
        else:
            self.btnNext.setEnabled(True)
