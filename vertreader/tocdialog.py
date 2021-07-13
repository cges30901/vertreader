from PyQt5.QtWidgets import QDialog, QListWidget, QVBoxLayout

class TOCDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.listWidget = QListWidget(self)
        self.layout.addWidget(self.listWidget)
        self.setLayout(self.layout)
        self.setWindowTitle(self.tr("Table Of Contents"))
        self.resize(500, 500)
