from vertreader.ui_styledialog import Ui_StyleDialog
from PyQt5.QtWidgets import QDialog, QColorDialog
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QColor

class StyleDialog(QDialog, Ui_StyleDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    @pyqtSlot()
    def on_btnColor_clicked(self):
        color = QColorDialog.getColor(QColor(self.color))
        if color.isValid():
            self.color = color.name()
            self.btnColor.setStyleSheet("border: none; background-color: " + self.color)
