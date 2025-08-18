from PyQt5 import QtWidgets

def iter_all_items(list_widget: QtWidgets.QListWidget):
    for i in range(list_widget.count()):
        yield list_widget.item(i).text().split(') ')[-1]

def get_list_items(list_widget: QtWidgets.QListWidget):
    return [list_widget.item(i).text().split(') ')[-1] for i in range(list_widget.count())]