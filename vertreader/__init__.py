# This Python file uses the following encoding: utf-8
import sys
from PyQt5.QtWidgets import QApplication
from vertreader.mainwindow import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
