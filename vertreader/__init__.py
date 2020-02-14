# This Python file uses the following encoding: utf-8
import sys
import os
from PyQt5.QtCore import QTranslator, QLocale, QLibraryInfo
from PyQt5.QtWidgets import QApplication
from vertreader.mainwindow import MainWindow


def main():
    app = QApplication(sys.argv)

    translator = QTranslator()
    translator.load(QLocale(), "vertreader", "_",
        os.path.dirname(os.path.abspath(__file__))+"/language")
    app.installTranslator(translator)

    #load Qt translation
    qtTranslator=QTranslator()
    qtTranslator.load(QLocale(), "qt", "_",
        QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(qtTranslator)

    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
