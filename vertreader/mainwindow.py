# This Python file uses the following encoding: utf-8
from vertreader.ebooklib.ebooklib import epub
import tempfile
import zipfile
import os
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QAction, QMessageBox, QApplication, QActionGroup, QDialog, QLineEdit
from PyQt5.QtCore import QUrl, QEvent, pyqtSlot, Qt, QSettings
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
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
        self.doc_num = 0
        self.page_num_doc = 0
        self.toc = []
        self.need_scroll = False
        self.isSearching = False
        self.activeMatch_old = 0
        self.searchText_old = ""
        self.isLoaded = False
        self.isCalculating = False

        self.readSettings()

        self.view.focusProxy().installEventFilter(self)
        QApplication.instance().aboutToQuit.connect(self.writeSettings)
        self.view.page().findTextFinished.connect(self.findTextFinished)

        if self.filename:
            self.open(self.filename)

    def eventFilter(self, source, e):
        if source == self.view.focusProxy():
            if e.type() == QEvent.Resize:
                if not self.isLoaded:
                    return False
                # Reload when resized to paginate again
                self.view.reload()
                self.calculate_doc_size()
                self.page_num_doc = 0
            elif e.type() == QEvent.Wheel:
                if not self.isLoaded:
                    return True
                if e.angleDelta().y() > 0:
                    self.gotoPreviousPage()
                elif e.angleDelta().y() < 0:
                    self.gotoNextPage()
                return True
            elif e.type() == QEvent.KeyPress:
                if e.key() == Qt.Key_PageDown or e.key() == Qt.Key_Down:
                    self.gotoNextPage()
                    return True
                elif e.key() == Qt.Key_PageUp or e.key() == Qt.Key_Up:
                    self.gotoPreviousPage()
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
        self.isLoaded = False
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

        self.view.load(QUrl.fromLocalFile(self.doc[self.doc_num]))
        self.calculate_doc_size()
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

                self.doc_num = self.toc[x][3]
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
            settings.setValue("color", self.style['color'])
            settings.setValue("bgColor", self.style['bgColor'])
            settings.setValue("chbFont", self.style['chbFont'])
            settings.setValue("font", self.style['font'])
            settings.setValue("chbHeight", self.style['chbHeight'])
            settings.setValue("lineheight", self.style['height'])
            settings.setValue("chbMargin", self.style['chbMargin'])
            settings.setValue("margin", self.style['margin'])
            settings.setValue("chbIndent", self.style['chbIndent'])
            settings.setValue("indent", self.style['indent'])
            settings.setValue("doc_num", self.doc_num)
            settings.setValue("page_num_doc", self.page_num_doc)
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
        self.style = {'color': settings.value("color", "black"),
                      'bgColor': settings.value("bgColor", "white"),
                      'chbFont': settings.value("chbFont", False, type=bool),
                      'font': settings.value("font", ''),
                      'chbHeight': settings.value("chbHeight", False, type=bool),
                      'height': settings.value("lineheight", 1.2, type=float),
                      'chbMargin': settings.value("chbMargin", False, type=bool),
                      'margin': settings.value("margin", 8, type=int),
                      'chbIndent': settings.value("chbIndent", False, type=bool),
                      'indent': settings.value("indent", 2.0, type=float)}

        self.doc_num = int(settings.value("doc_num", 0))
        self.page_num_doc = int(settings.value("page_num_doc", 0))
        settings.endGroup()

    @pyqtSlot()
    def on_view_loadStarted(self):
        self.isLoaded = False

    @pyqtSlot(bool)
    def on_view_loadFinished(self):
        if self.view.url().toString() == "about:blank":
            return

        # Detect current doc_num after loading
        for index, item in enumerate(self.doc):
            if self.view.url().toLocalFile() == item:
                self.doc_num = index

        self.view.page().runJavaScript('document.body.style.color="{}"'.format(self.style['color']))
        self.view.page().runJavaScript('document.body.style.backgroundColor="{}"'.format(self.style['bgColor']))
        if self.style.get('chbFont'):
            self.view.page().runJavaScript('document.body.style.fontFamily="{}"'.format(self.style.get('font')))
        if self.style.get('chbHeight'):
            self.view.page().runJavaScript('''var p = document.getElementsByTagName("p");
                                              for (var i = 0; i < p.length; i++) {{
                                                  p[i].style.lineHeight = "{}";
                                              }}'''.format(self.style.get('height')))
        if self.style.get('chbMargin'):
            self.view.page().runJavaScript('document.body.style.margin="{}px"'.format(self.style.get('margin')))
        if self.style.get('chbIndent'):
            self.view.page().runJavaScript('''var p = document.getElementsByTagName("p");
                                              for (var i = 0; i < p.length; i++) {{
                                                  p[i].style.textIndent = "{}em";
                                              }}'''.format(self.style.get('indent')))

        # Support popup footnote
        with open(os.path.dirname(os.path.abspath(__file__))+'/footnote.js', 'r') as jsfile:
            js = jsfile.read()
        self.view.page().runJavaScript(js)

        self.view.page().runJavaScript('document.body.style.writingMode="vertical-rl"')

        def paginateFinished(callback):
            self.page_total_doc = callback[0]
            if callback[1] == 1:
                #pagination failed
                self.statusBar().showMessage(self.tr('Pagination failed. '
                    'Please report this issue to the developer.'), 3000)
            if self.page_num_doc == -1:
                self.viewScrollTo(0, "document.body.scrollHeight")
                self.page_num_doc = self.page_total_doc - 1

            self.isLoaded = True
            if not self.isCalculating:
                self.update_page_num_book()

        with open(os.path.dirname(os.path.abspath(__file__))+'/paginate_vertical.js', 'r') as jsfile:
            js = jsfile.read()
        window_width = self.view.size().width() / self.view.zoomFactor()
        window_height = self.view.size().height() / self.view.zoomFactor()
        self.view.page().runJavaScript("var window_width = {};var window_height = {};".format(window_width, window_height))
        self.view.page().runJavaScript('document.documentElement.style.height = "{}px";'.format(window_height))
        self.view.page().runJavaScript(js, paginateFinished)

        if self.need_scroll is True:
            self.need_scroll = False
            self.gotoPage_doc(self.page_num_doc)

        if self.isSearching:
            self.search()

    def on_slider_valueChanged(self, value):
        if value != self.page_num_book:
            self.gotoPage_book(value)

    def update_page_num_doc(self):
        pageHeight = self.view.size().height()
        self.page_num_doc = round(self.view.page().scrollPosition().y() / pageHeight)

    def update_page_num_book(self, dummy = None):
        if self.isCalculating == True:
            return

        def callback(result):
            self.page_num_book = 1
            for i in range(self.doc_num):
                self.page_num_book += self.page_cal_doc[i]
            pageHeight = self.view.size().height()
            self.page_num_doc = round(result * self.view.page().zoomFactor() / pageHeight)
            self.page_num_book += self.page_num_doc
            self.txtPageNum.setText("{}/{}".format(self.page_num_book, self.page_cal_book))
            self.slider.setValue(self.page_num_book)
        self.view.page().runJavaScript("window.scrollY",callback)

    def calculate_doc_size(self):
        if self.isCalculating == True:
            return
        self.isCalculating = True
        self.txtPageNum.setText(self.tr("Calculating..."))
        with open(os.path.dirname(os.path.abspath(__file__))+'/paginate_vertical.js', 'r') as jsfile:
            js = jsfile.read()

        view_cal = QWebEngineView(self)
        self.doc_num_cal = 0
        self.page_cal_doc = []

        def loadFinished():
            view_cal.page().runJavaScript('document.body.style.writingMode="vertical-rl"')

            def paginateFinished(callback):
                self.page_cal_doc.append(callback[0])
                if self.doc_num_cal + 1 < len(self.doc):
                    self.doc_num_cal = self.doc_num_cal + 1
                    view_cal.load(QUrl.fromLocalFile(self.doc[self.doc_num_cal]))
                else:
                    self.page_cal_book = 0
                    for i in range(len(self.doc)):
                        self.page_cal_book += self.page_cal_doc[i]
                    self.slider.setMaximum(self.page_cal_book)
                    self.isCalculating = False
                    self.update_page_num_book()

            window_width = self.view.size().width()/self.view.zoomFactor()
            window_height = self.view.size().height()/self.view.zoomFactor()
            view_cal.page().runJavaScript("var window_width = {}, window_height = {};".format(window_width, window_height))
            view_cal.page().runJavaScript('document.documentElement.style.height = "{}px";'.format(window_height))
            view_cal.page().runJavaScript(js, paginateFinished)
        view_cal.loadFinished.connect(loadFinished)
        view_cal.load(QUrl.fromLocalFile(self.doc[self.doc_num_cal]))

    @pyqtSlot()
    def on_action_Style_triggered(self):
        dlgStyle=StyleDialog(self)
        dlgStyle.spbZoom.setValue(self.view.zoomFactor())
        dlgStyle.color = self.style['color']
        dlgStyle.btnColor.setStyleSheet("border: none; background-color: " + self.style['color'])
        dlgStyle.bgColor = self.style['bgColor']
        dlgStyle.btnBgColor.setStyleSheet("border: none; background-color: " + self.style['bgColor'])
        dlgStyle.chbFont.setChecked(self.style['chbFont'])
        dlgStyle.boxFont.setCurrentFont(QFont(self.style['font']))
        dlgStyle.chbHeight.setChecked(self.style['chbHeight'])
        dlgStyle.spbHeight.setValue(self.style['height'])
        dlgStyle.chbMargin.setChecked(self.style['chbMargin'])
        dlgStyle.spbMargin.setValue(self.style['margin'])
        dlgStyle.chbIndent.setChecked(self.style['chbIndent'])
        dlgStyle.spbIndent.setValue(self.style['indent'])
        if dlgStyle.exec_()==QDialog.Accepted:
            self.view.setZoomFactor(dlgStyle.spbZoom.value())
            self.style = {'color': dlgStyle.color,
                          'bgColor': dlgStyle.bgColor,
                          'chbFont': dlgStyle.chbFont.isChecked(),
                          'font': dlgStyle.boxFont.currentFont().family(),
                          'chbHeight': dlgStyle.chbHeight.isChecked(),
                          'height': dlgStyle.spbHeight.value(),
                          'chbMargin': dlgStyle.chbMargin.isChecked(),
                          'margin': dlgStyle.spbMargin.value(),
                          'chbIndent': dlgStyle.chbIndent.isChecked(),
                          'indent': dlgStyle.spbIndent.value()}
            self.view.reload()
            self.calculate_doc_size()
            self.page_num_doc = 0

    def viewScrollTo(self, posX, posY):
        self.view.page().runJavaScript("window.scrollTo({}, {});"
            .format(posX, posY), self.update_page_num_book)

    def gotoPage_book(self, page):
        # page_num_book is 1-based
        page -= 1
        doc = 0
        for i in range(len(self.page_cal_doc)):
            if page<self.page_cal_doc[i]:
                break
            page -= self.page_cal_doc[i]
            doc += 1
        if self.doc_num == doc:
            self.gotoPage_doc(page)
        else:
            self.doc_num = doc
            self.page_num_doc = page
            self.need_scroll = True
            self.view.load(QUrl.fromLocalFile(self.doc[self.doc_num]))

    def gotoPage_doc(self, page):
        self.viewScrollTo(0, self.view.size().height() / self.view.zoomFactor() * page)

    def gotoPreviousPage(self):
        self.update_page_num_doc()

        self.page_num_doc -= 1

        if self.page_num_doc < 0:
            if self.doc_num > 0:
                self.doc_num -= 1
                self.view.load(QUrl.fromLocalFile(self.doc[self.doc_num]))
            else:
                self.page_num_doc = 0
        else:
            self.gotoPage_doc(self.page_num_doc)

    def gotoNextPage(self):
        self.update_page_num_doc()

        self.page_num_doc += 1

        if self.page_num_doc > self.page_total_doc - 1:
            if self.doc_num < len(self.doc) - 1:
                self.doc_num += 1
                self.page_num_doc = 0
                self.view.load(QUrl.fromLocalFile(self.doc[self.doc_num]))
            else:
                self.page_num_doc = self.page_total_doc - 1
        else:
            self.gotoPage_doc(self.page_num_doc)

    @pyqtSlot()
    def on_action_Search_triggered(self):
        self.dlgSearch=SearchDialog(self)
        self.dlgSearch.btnSearch.clicked.connect(self.searchStart)
        self.dlgSearch.show()

    @pyqtSlot()
    def searchStart(self):
        self.isSearching = True
        self.doc_num_old = self.doc_num
        self.page_num_old = self.page_num_doc

        # Show scroll bar so that scrolling works when searching
        self.view.page().runJavaScript("document.body.style.overflow = 'auto';")

        self.search()

    @pyqtSlot()
    def search(self):
        self.view.page().findText(self.dlgSearch.lneSearch.text(), QWebEnginePage.FindFlags())

    def findTextFinished(self, result):
        if result.numberOfMatches() == 0 or (self.activeMatch_old == result.numberOfMatches()
           and result.activeMatch() == 1 and self.searchText_old == self.dlgSearch.lneSearch.text()):

            if (self.doc_num == self.doc_num_old - 1 or
               self.doc_num_old == 0 and self.doc_num == len(self.doc) - 1):
                self.isSearching = False
                self.doc_num = self.doc_num_old
                self.page_num_doc = self.page_num_old
                self.need_scroll = True
                self.view.load(QUrl.fromLocalFile(self.doc[self.doc_num]))
                return
            if self.doc_num == len(self.doc) - 1:
                self.doc_num = 0
            else:
                self.doc_num += 1
            self.activeMatch_old = 0
            self.view.load(QUrl.fromLocalFile(self.doc[self.doc_num]))
        else:
            self.activeMatch_old = result.activeMatch()
            self.searchText_old = self.dlgSearch.lneSearch.text()
            self.isSearching = False

            # Hide scroll bar after search
            self.view.page().runJavaScript("document.body.style.overflow = 'hidden';")

        # Adjust position to prevent showing halves of two pages
        def callback(result):
            pageHeight = self.view.size().height()
            self.page_num_doc = round(result * self.view.page().zoomFactor() / pageHeight)
            self.gotoPage_doc(self.page_num_doc)
        self.view.page().runJavaScript("window.scrollY",callback)
