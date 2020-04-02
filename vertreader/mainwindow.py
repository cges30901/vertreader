# This Python file uses the following encoding: utf-8
from vertreader.ebooklib.ebooklib import epub
import tempfile
import zipfile
import os
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QAction, QMessageBox, QApplication, QActionGroup, QDialog, QLineEdit
from PyQt5.QtCore import QUrl, QEvent, pyqtSlot, Qt, QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from vertreader.ui_mainwindow import Ui_MainWindow
from vertreader.styledialog import StyleDialog
from vertreader.searchdialog import SearchDialog


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, args):
        super().__init__()
        self.setWindowIcon(QIcon(os.path.dirname(os.path.abspath(__file__))+'/vertreader.svg'))
        self.setupUi(self)
        group = QActionGroup(self)
        group.addAction(self.actionPaged)
        group.addAction(self.actionScroll)

        self.filename = args.file
        self.tempdir = ''
        self.book = None
        self.doc = []
        self.docIndex = 0
        self.pageIndex = 0
        self.toc = []
        self.need_scroll = False
        self.isSearching = False
        self.activeMatch_old = 0
        self.searchText_old = ""

        self.color = "black"
        self.bgColor = "white"
        self.isVertical = True
        self.readSettings()

        self.view.focusProxy().installEventFilter(self)
        QApplication.instance().aboutToQuit.connect(self.writeSettings)
        self.view.page().findTextFinished.connect(self.findTextFinished)

        if self.filename:
            self.open(self.filename)

    def eventFilter(self, source, e):
        if source == self.view.focusProxy():
            if e.type() == QEvent.Resize:
                # Reload when resized to paginate again
                self.view.reload()
                self.pageIndex = 0
            if self.actionPaged.isChecked():
                if e.type() == QEvent.Wheel:
                    if e.angleDelta().y() > 0:
                        self.pageIndex -= 1
                        self.gotoPage()
                    elif e.angleDelta().y() < 0:
                        self.pageIndex += 1
                        self.gotoPage()
                    return True
                elif e.type() == QEvent.KeyPress:
                    if e.key() == Qt.Key_PageDown or e.key() == Qt.Key_Down:
                        self.pageIndex += 1
                        self.gotoPage()
                        return True
                    elif e.key() == Qt.Key_PageUp or e.key() == Qt.Key_Up:
                        self.pageIndex -= 1
                        self.gotoPage()
                        return True
            elif self.actionScroll.isChecked() and self.isVertical:
                # The coordinate of javascript and Qt WebEngine is different.
                # In javascript, the beginning of document is 0.
                # In Qt WebEngine, the end of document is 0.
                # So I have to convert it to use javascript to scroll.
                pos_js = self.view.page().scrollPosition().x() - self.view.page().contentsSize().width() + self.view.width()
                # Adjust position according to zoomFactor
                pos_js /= self.view.zoomFactor()

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
            else: # No need to scroll manually in continuous mode and horizontal writing
                return False
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

        try:
            with zipfile.ZipFile(filename, "r") as zip_ref:
                zip_ref.extractall(self.tempdir)
                zip_ref.close()
        except Exception as e:
            QMessageBox.warning(self, self.tr("Failed to extract"), str(e))
            return

        # This is used instead of epub.read_epub()
        # because I need reader.opf_dir
        try:
            reader = epub.EpubReader(filename)
            self.book = reader.load()
            reader.process()
        except Exception as e:
            QMessageBox.warning(self, self.tr("Failed to read EPUB with EbookLib"), str(e))
            return

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
                        # Show warning if document for this TOC item is not found
                        if i == len(self.doc) - 1:
                            QMessageBox.warning(self, self.tr("Failed to read TOC"),
                                self.tr("Link to unrecognized item is: ") + a.href)
            return toc
        self.toc = get_toc(self.book.toc, 0)
        self.actionTOC = [QAction('>' * self.toc[x][2] + self.toc[x][0]) for x in range(len(self.toc))]
        for x in self.actionTOC:
            x.triggered.connect(self.toc_triggered)
        self.menuTOC.addActions(self.actionTOC)

        self.readSettings()
        self.need_scroll = True
        self.setButtons()

        self.view.load(QUrl.fromLocalFile(self.doc[self.docIndex]))
        self.setWindowTitle(self.tr("{} - VertReader").format(self.book.get_metadata('DC', 'title')[0][0]))

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
        self.pageIndex = 0
        self.setButtons()
        self.view.load(QUrl.fromLocalFile(self.doc[self.docIndex]))

    @pyqtSlot(bool)
    def on_btnNext_clicked(self):
        self.docIndex += 1
        self.pageIndex = 0
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
    def on_action_Metadata_triggered(self):
        try:
            if self.book.get_metadata('DC', 'title'):
                title = self.book.get_metadata('DC', 'title')[0][0]
            else:
                title = self.tr("N/A")
            if self.book.get_metadata('DC', 'creator'):
                author = self.book.get_metadata('DC', 'creator')[0][0]
            else:
                author = self.tr("N/A")
            if self.book.get_metadata('DC', 'description'):
                description = self.book.get_metadata('DC', 'description')[0][0]
            else:
                description = self.tr("N/A")
            QMessageBox.information(self, self.tr("Metadata"),
                self.tr('''Title: {0}
Author: {1}
Description: {2}''').format(title, author, description))
        except Exception as e:
            QMessageBox.warning(self, self.tr("Failed to read metadata"), str(e))

    @pyqtSlot()
    def on_actionLibrary_triggered(self):
        QMessageBox.about(self, self.tr("Libraries used"),
            self.tr("<h3>Libraries:</h3>") +
'''<p>PyQt5 (GPL v3)</p>
<p>EbookLib (AGPL v3)<p>''')

    @pyqtSlot()
    def writeSettings(self):
        def writeGroup(group):
            settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "cges30901", "VertReader")
            settings.beginGroup(group)
            settings.setValue("isMaximized", self.isMaximized())
            settings.setValue("width", self.width())
            settings.setValue("height", self.height())
            settings.setValue("ispagedview", self.actionPaged.isChecked())
            settings.setValue("zoomFactor", self.view.zoomFactor())
            settings.setValue("color", self.color)
            settings.setValue("bgColor", self.bgColor)
            settings.setValue("isVertical", self.isVertical)
            settings.setValue("docIndex", self.docIndex)
            settings.setValue("pageIndex", self.pageIndex)
            settings.setValue("posX", self.view.page().scrollPosition().x()
                - self.view.page().contentsSize().width() + self.view.width())
            settings.setValue("posY", self.view.page().scrollPosition().y())
            settings.endGroup()

        # Also saves last used settings in Global group
        writeGroup("Global")
        # replace slash and backslash with '>'
        # because they have special meaning in QSettings
        writeGroup(self.filename.replace('/', '>').replace('\\', '>'))

    def readSettings(self):
        settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "cges30901", "VertReader")
        if self.filename:
            settings.beginGroup(self.filename.replace('/', '>').replace('\\', '>'))
        else:
            settings.beginGroup("Global")

        if settings.value("isMaximized", self.isMaximized(), type = bool) == True:
            self.showMaximized()
        else:
            self.showNormal()
            self.resize(int(settings.value("width", self.width())), int(settings.value("height", self.height())))
        if settings.value("ispagedview", self.actionPaged.isChecked(), type = bool) == True:
            self.actionPaged.setChecked(True)
            self.actionScroll.setChecked(False)
        else:
            self.actionPaged.setChecked(False)
            self.actionScroll.setChecked(True)

        self.view.setZoomFactor(float(settings.value("zoomFactor", 0)))
        self.color = settings.value("color", self.color)
        self.bgColor = settings.value("bgColor", self.bgColor)
        self.isVertical = settings.value("isVertical", self.isVertical, type = bool)
        self.docIndex = int(settings.value("docIndex", 0))
        self.pageIndex = int(settings.value("pageIndex", 0))
        self.posX = int(settings.value("posX", 0))
        self.posY = int(settings.value("posY", 0))
        settings.endGroup()

    @pyqtSlot(bool)
    def on_view_loadFinished(self):
        self.view.page().runJavaScript('document.body.style.color="{}"'.format(self.color))
        self.view.page().runJavaScript('document.body.style.backgroundColor="{}"'.format(self.bgColor))
        if self.isVertical:
            self.view.page().runJavaScript('document.body.style.writingMode="vertical-rl"')
        else:
            self.view.page().runJavaScript('document.body.style.writingMode="horizontal-tb"')

        if self.actionPaged.isChecked():
            def paginateFinished(callback):
                self.pageCount = callback
                if self.pageIndex == -1:
                    if self.isVertical:
                        self.view.page().runJavaScript("window.scrollTo(0,document.body.scrollHeight);")
                    else:
                        self.view.page().runJavaScript("window.scrollTo(document.body.scrollWidth,0);")
                    self.pageIndex = self.pageCount - 1

            if self.isVertical:
                with open(os.path.dirname(os.path.abspath(__file__))+'/paginate_vertical.js', 'r') as jsfile:
                    js = jsfile.read()
                self.view.page().runJavaScript(js, paginateFinished)
            else:
                with open(os.path.dirname(os.path.abspath(__file__))+'/paginate_horizontal.js', 'r') as jsfile:
                    js = jsfile.read()
                self.view.page().runJavaScript(js, paginateFinished)

        if self.need_scroll is True:
            self.need_scroll = False
            self.view.page().runJavaScript("window.scrollTo({0}, {1});"
                .format(self.posX, float(self.posY) / self.view.zoomFactor()))

        if self.isSearching:
            self.search()

    def setButtons(self):
        if self.docIndex == 0:
            self.btnPrev.setEnabled(False)
        else:
            self.btnPrev.setEnabled(True)
        if self.docIndex == len(self.doc) - 1:
            self.btnNext.setEnabled(False)
        else:
            self.btnNext.setEnabled(True)

    @pyqtSlot()
    def on_actionPaged_triggered(self):
        self.view.reload()

    @pyqtSlot()
    def on_actionScroll_triggered(self):
        self.view.reload()

    @pyqtSlot()
    def on_action_Style_triggered(self):
        dlgStyle=StyleDialog(self)
        dlgStyle.spbZoom.setValue(self.view.zoomFactor())
        dlgStyle.color = self.color
        dlgStyle.btnColor.setStyleSheet("border: none; background-color: " + self.color)
        dlgStyle.bgColor = self.bgColor
        dlgStyle.btnBgColor.setStyleSheet("border: none; background-color: " + self.bgColor)
        dlgStyle.btnVertical.setChecked(self.isVertical)
        dlgStyle.btnHorizontal.setChecked(not self.isVertical)
        if dlgStyle.exec_()==QDialog.Accepted:
            self.view.setZoomFactor(dlgStyle.spbZoom.value())
            self.color = dlgStyle.color
            self.bgColor = dlgStyle.bgColor
            self.isVertical = dlgStyle.btnVertical.isChecked()
            self.view.reload()
            self.pageIndex = 0

    def gotoPage(self):
        if self.isVertical:
            # prevent crash if javascript failed to get pageCount
            if not self.pageCount:
                self.pageCount = round(self.view.page().contentsSize().height() / self.view.height())
            pageHeight = self.view.page().contentsSize().height() / self.pageCount / self.view.zoomFactor()
        else:
            if not self.pageCount:
                self.pageCount = round(self.view.page().contentsSize().width() / self.view.width())
            pageWidth = self.view.page().contentsSize().width() / self.pageCount / self.view.zoomFactor()

        if self.pageIndex < 0:
            if self.docIndex > 0:
                self.docIndex -= 1
                self.setButtons()
                self.view.load(QUrl.fromLocalFile(self.doc[self.docIndex]))
            else:
                self.pageIndex = 0
            return

        if self.pageIndex > self.pageCount - 1:
            if self.docIndex < len(self.doc) - 1:
                self.docIndex += 1
                self.pageIndex = 0
                self.setButtons()
                self.view.load(QUrl.fromLocalFile(self.doc[self.docIndex]))
            else:
                self.pageIndex = self.pageCount - 1
            return

        if self.isVertical:
            self.view.page().runJavaScript("window.scrollTo({0}, {1});"
                .format(self.view.page().scrollPosition().x(), pageHeight * self.pageIndex))
        else:
            self.view.page().runJavaScript("window.scrollTo({0}, {1});"
                .format(pageWidth * self.pageIndex, self.view.page().scrollPosition().y()))

    @pyqtSlot()
    def on_action_Search_triggered(self):
        self.dlgSearch=SearchDialog(self)
        self.dlgSearch.btnSearch.clicked.connect(self.searchStart)
        self.dlgSearch.show()

    @pyqtSlot()
    def searchStart(self):
        self.isSearching = True
        self.docIndex_old = self.docIndex
        self.posX = self.view.page().scrollPosition().x() - self.view.page().contentsSize().width() + self.view.width()
        self.posY = self.view.page().scrollPosition().y()

        # Show scroll bar so that scrolling works when searching
        if self.actionPaged.isChecked():
            self.view.page().runJavaScript("document.body.style.overflow = 'auto';")

        self.search()

    @pyqtSlot()
    def search(self):
        def callback(found):
            pass
        self.view.page().findText(self.dlgSearch.lneSearch.text(), QWebEnginePage.FindFlags(), callback)

    def findTextFinished(self, result):
        if result.numberOfMatches() == 0 or (self.activeMatch_old == result.numberOfMatches()
           and result.activeMatch() == 1 and self.searchText_old == self.dlgSearch.lneSearch.text()):

            if (self.docIndex == self.docIndex_old - 1 or
               self.docIndex_old == 0 and self.docIndex == len(self.doc) - 1):
                self.isSearching = False
                self.docIndex = self.docIndex_old
                self.need_scroll = True
                self.view.load(QUrl.fromLocalFile(self.doc[self.docIndex]))
                return
            if self.docIndex == len(self.doc) - 1:
                self.docIndex = 0
            else:
                self.docIndex += 1
            self.activeMatch_old = 0
            self.view.load(QUrl.fromLocalFile(self.doc[self.docIndex]))
        else:
            self.activeMatch_old = result.activeMatch()
            self.searchText_old = self.dlgSearch.lneSearch.text()
            self.isSearching = False

            # Hide scroll bar after search
            if self.actionPaged.isChecked():
                self.view.page().runJavaScript("document.body.style.overflow = 'hidden';")
