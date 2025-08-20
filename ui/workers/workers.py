from PyQt5 import QtCore
from read_state_standard import read_data_from_docx, save_to_txt, read_data_for_search, get_info_st_list, save_table_to_file, read_data_from_pdf

class ReadWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal(list)
    progress = QtCore.pyqtSignal(int)

    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def run(self):
        # data = read_data_from_docx(self.filename, progress_bar=self.progress)
        data = read_data_from_pdf(self.filename, self.progress)
        self.finished.emit(data)

class SaveFileWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal(int)
    progress = QtCore.pyqtSignal(int)

    def __init__(self, filename, data, length):
        super().__init__()
        self.filename = filename
        self.data = data
        self.length = length

    def run(self):
        res = save_to_txt(self.data, self.filename, self.length, self.progress)
        self.finished.emit(100)

class SearchReadWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal(list)
    progress = QtCore.pyqtSignal(int)

    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def run(self):
        data = read_data_for_search(self.filename, self.progress)
        self.finished.emit(data)

class ParserSearchWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal(dict)
    progress = QtCore.pyqtSignal(int)

    def __init__(self, list_standard):
        super().__init__()
        self.list_standard = list_standard

    def run(self):
        res = get_info_st_list(self.list_standard, self.progress)
        self.finished.emit(res)

class SaveTableWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal(int)
    progress = QtCore.pyqtSignal(int)

    def __init__(self, filename, model):
        super().__init__()
        self.model = model
        self.filename = filename

    def run(self):
        save_table_to_file(self.filename, self.model, self.progress)