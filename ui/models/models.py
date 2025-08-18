from PyQt5.QtGui import QStandardItem
from PyQt5.QtCore import Qt

class CenteredItem(QStandardItem):
    def __init__(self, text=""):
        super().__init__(str(text))
        self.setTextAlignment(Qt.AlignCenter)  # Центрируем сразу при создании
