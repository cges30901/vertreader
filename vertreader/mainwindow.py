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
        self.isLoading = False

        self.color = "black"
        self.bgColor = "white"
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
            elif e.type() == QEvent.Wheel:
                if e.angleDelta().y() > 0:
                    self.gotoPage(-1)
                elif e.angleDelta().y() < 0:
                    self.gotoPage(1)
                return True
            elif e.type() == QEvent.KeyPress:
                if e.key() == Qt.Key_PageDown or e.key() == Qt.Key_Down:
                    self.gotoPage(1)
                    return True
                elif e.key() == Qt.Key_PageUp or e.key() == Qt.Key_Up:
                    self.gotoPage(-1)
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
            self.book.nav_item = next((item for item in self.book.items if isinstance(item, epub.EpubNav)), None)
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
                    if os.path.basename(a.href)[0] == '#':
                        # This is internal link of Navigation Document.
                        # I put filename in href to make it accessible in TOC menu.
                        a.href = self.book.nav_item.file_name + os.path.basename(a.href)
                    fullname = os.path.join(self.tempdir, reader.opf_dir, a.href)
                    for i in range(len(self.doc)):
                        if fullname.split('#')[0] == self.doc[i]:
                            # If content of <a> element is empty, epub is broken.
                            # To avoid concatenating None to str while creating
                            # self.actionTOC, make a.title empty string.
                            if(a.title is None):
                                a.title = ''
                            toc.append([a.title, fullname, level, i])
                            break
                        # Show warning if document for this TOC item is not found
                        if i == len(self.doc) - 1:
                            QMessageBox.warning(self, self.tr("Failed to read TOC"),
                                self.tr('Failed to read TOC: link to unrecognized item is "{}"').format(a.href))
            return toc
        self.toc = get_toc(self.book.toc, 0)
        self.actionTOC = []
        for x in range(len(self.toc)):
            self.actionTOC.append(QAction('>' * self.toc[x][2] + self.toc[x][0]))
            self.actionTOC[x].triggered.connect(self.toc_triggered)
        self.menuTOC.addActions(self.actionTOC)

        self.readSettings()
        self.need_scroll = True

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
                break

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
            settings.setValue("zoomFactor", self.view.zoomFactor())
            settings.setValue("color", self.color)
            settings.setValue("bgColor", self.bgColor)
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

        self.view.setZoomFactor(float(settings.value("zoomFactor", 0)))
        self.color = settings.value("color", self.color)
        self.bgColor = settings.value("bgColor", self.bgColor)
        self.docIndex = int(settings.value("docIndex", 0))
        self.pageIndex = int(settings.value("pageIndex", 0))
        self.posX = int(settings.value("posX", 0))
        self.posY = int(settings.value("posY", 0))
        settings.endGroup()

    @pyqtSlot()
    def on_view_loadStarted(self):
        self.isLoading = True

    @pyqtSlot(bool)
    def on_view_loadFinished(self):
        # Detect current docIndex after loading
        for index, item in enumerate(self.doc):
            if self.view.url().toLocalFile() == item:
                self.docIndex = index

        self.view.page().runJavaScript('document.body.style.color="{}"'.format(self.color))
        self.view.page().runJavaScript('document.body.style.backgroundColor="{}"'.format(self.bgColor))

        # Support popup footnote
        with open(os.path.dirname(os.path.abspath(__file__))+'/footnote.js', 'r') as jsfile:
            js = jsfile.read()
        self.view.page().runJavaScript(js)

        self.view.page().runJavaScript('document.body.style.writingMode="vertical-rl"')

        def paginateFinished(callback):
            self.pageCount = callback[0]
            if callback[1] == 1:
                #pagination failed
                QMessageBox.warning(self, self.tr("Pagination failed"),
                    self.tr('Pagination failed. Please report to developer.'))
            if self.pageIndex == -1:
                self.view.page().runJavaScript("window.scrollTo(0,document.body.scrollHeight);")
                self.pageIndex = self.pageCount - 1

            self.isLoading = False

        with open(os.path.dirname(os.path.abspath(__file__))+'/paginate_vertical.js', 'r') as jsfile:
            js = jsfile.read()
        self.view.page().runJavaScript(js, paginateFinished)

        if self.need_scroll is True:
            self.need_scroll = False
            self.view.page().runJavaScript("window.scrollTo({0}, {1});"
                .format(self.posX, float(self.posY) / self.view.zoomFactor()))

        if self.isSearching:
            self.search()

    @pyqtSlot()
    def on_action_Style_triggered(self):
        dlgStyle=StyleDialog(self)
        dlgStyle.spbZoom.setValue(self.view.zoomFactor())
        dlgStyle.color = self.color
        dlgStyle.btnColor.setStyleSheet("border: none; background-color: " + self.color)
        dlgStyle.bgColor = self.bgColor
        dlgStyle.btnBgColor.setStyleSheet("border: none; background-color: " + self.bgColor)
        if dlgStyle.exec_()==QDialog.Accepted:
            self.view.setZoomFactor(dlgStyle.spbZoom.value())
            self.color = dlgStyle.color
            self.bgColor = dlgStyle.bgColor
            self.view.reload()
            self.pageIndex = 0

    def gotoPage(self, diff = 0):
        # Do not turn page if view is still loading
        if self.isLoading == True:
            return

        pageHeight = self.view.page().contentsSize().height() / self.pageCount
        self.pageIndex = round(self.view.page().scrollPosition().y() / pageHeight)

        # Change page number
        if diff < 0:
            self.pageIndex -= 1
        elif diff > 0:
            self.pageIndex += 1

        if self.pageIndex < 0:
            if self.docIndex > 0:
                self.docIndex -= 1
                self.view.load(QUrl.fromLocalFile(self.doc[self.docIndex]))
            else:
                self.pageIndex = 0
            return

        if self.pageIndex > self.pageCount - 1:
            if self.docIndex < len(self.doc) - 1:
                self.docIndex += 1
                self.pageIndex = 0
                self.view.load(QUrl.fromLocalFile(self.doc[self.docIndex]))
            else:
                self.pageIndex = self.pageCount - 1
            return

        self.view.page().runJavaScript("window.scrollTo({0}, {1});"
            .format(self.view.page().scrollPosition().x(), pageHeight / self.view.zoomFactor() * self.pageIndex))

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
