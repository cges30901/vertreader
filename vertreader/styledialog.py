from vertreader.ui_styledialog import Ui_StyleDialog
from PyQt5.QtWidgets import QDialog, QColorDialog
from PyQt5.QtCore import pyqtSlot

class StyleDialog(QDialog, Ui_StyleDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    @pyqtSlot()
    def on_btnColor_clicked(self):
        color = QColorDialog.getColor()
        self.btnColor.setStyleSheet("border: none; background-color: " + color.name())
