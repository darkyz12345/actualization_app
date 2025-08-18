from PyQt5 import QtWidgets, QtCore
from ui.py import Ui_NotInputFileDialog, Ui_NotExecuteDialog, Ui_successfully_read, Ui_NotFoundedForSearchDialog, Ui_Dialog


class NotInputFileDialog(QtWidgets.QDialog, Ui_NotInputFileDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.accept)


class NotExecuteFileDialog(QtWidgets.QDialog, Ui_NotExecuteDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.accept)


class SuccessReadDilog(QtWidgets.QDialog, Ui_successfully_read):
    save_clicked = QtCore.pyqtSignal()
    watch_clicked = QtCore.pyqtSignal()
    to_clicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.save_btn.clicked.connect(self.on_save)
        self.watch_btn.clicked.connect(self.on_watch)
        self.to_btn.clicked.connect(self.on_to)

    def on_save(self):
        self.accept()
        self.save_clicked.emit()

    def on_watch(self):
        self.accept()

    def on_to(self):
        self.accept()
        self.to_clicked.emit()


class NotFoundedSearchDialog(QtWidgets.QDialog, Ui_NotFoundedForSearchDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.choose_btn.clicked.connect(self.accept)

class WarningExecuteDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)