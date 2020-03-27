from vertreader.ui_searchdialog import Ui_SearchDialog
from PyQt5.QtWidgets import QDialog

class SearchDialog(QDialog, Ui_SearchDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
