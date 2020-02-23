from vertreader.ui_styledialog import Ui_StyleDialog
from PyQt5.QtWidgets import QDialog

class StyleDialog(QDialog, Ui_StyleDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
