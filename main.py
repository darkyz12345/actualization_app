import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from ui.py import Ui_Actualization
from ui.py import resoursec_rc
from ui.dialogs import NotInputFileDialog, NotExecuteFileDialog, SuccessReadDilog, NotFoundedSearchDialog, \
    WarningExecuteDialog
from read_state_standard import read_data_from_docx
from ui.workers import ReadWorker, SaveFileWorker, SearchReadWorker, ParserSearchWorker, SaveTableWorker
from ui import iter_all_items
from ui.models import CenteredItem
from ui.utils import get_list_items


class MainWindow(QtWidgets.QMainWindow, Ui_Actualization):
    def __init__(self):
        super().__init__()
        self.headers = ["ГОСТ", "Описание", "Статус", "Актуальность", "URL"]
        self.filename_searched = ''
        self.save_filename = None
        self.worker = None
        self.thread = None
        self.filename = ''
        self.setupUi(self)
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(self.headers)
        self.result_table_view.setModel(self.model)
        self.result_table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.result_table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # self.model.appendRow([CenteredItem('1'), CenteredItem('1'), CenteredItem('1'), CenteredItem('1')])
        self.tabWidget.setCurrentWidget(self.reading_file_tab)
        self.input_file_btn.clicked.connect(self.open_file_dialog)
        self.clear_btn.clicked.connect(self.clear_selected_path_btn)
        self.run_btn.clicked.connect(self.execute_read_btn)
        self.progress_dialog = QtWidgets.QProgressDialog("Обработка файла...", "Отмена", 0, 100, self)
        self.progress_dialog.setWindowTitle("Подождите")
        self.progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.close()
        self.save_btn.clicked.connect(self.on_save_btn)
        self.choose_group.setVisible(False)
        self.file_radio_btn.toggled.connect(self.change_radio_btn_1)
        self.search_radio_btn.toggled.connect(self.change_radio_btn_2)
        self.choose_btn.clicked.connect(self.on_choose_btn)
        self.delete_btn.clicked.connect(self.on_delete_btn)
        self.run_read_btn.clicked.connect(self.on_run_read_btn)
        self.run_btn_2.clicked.connect(self.on_run_btn_2)
        self.save_serch_btn.clicked.connect(self.on_save)

    def on_save(self):
        if self.model.rowCount():
            options = QtWidgets.QFileDialog.Options()
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                'Выберите, куда сохранить файл',
                '',
                'Документы (*.docx);;Электронные таблицы (*.xlsx)',
                options=options
            )
            if filename:
                if not (('.txt' in filename) or ('.docx' in filename) or ('.xlsx' in filename)):
                    filename = filename + _.split('*')[-1][:-1]
                self.save_filename_table = filename
                # print(self.save_filename)
                self.progress_dialog.setValue(0)
                self.progress_dialog.show()
                self.thread = QtCore.QThread()
                self.worker = SaveTableWorker(self.save_filename_table, self.model)
                self.worker.moveToThread(self.thread)
                self.worker.progress.connect(self.progress_dialog.setValue)
                # self.worker.finished.connect(self.on_finished_save_btn)
                self.worker.finished.connect(self.thread.quit)
                self.worker.finished.connect(self.worker.deleteLater)
                self.thread.started.connect(self.worker.run)
                self.thread.start()
            return
        print("Not founded")

    def on_run_btn_2(self):
        if self.founded_list_widget.count() == 0:
            dlg = NotFoundedSearchDialog()
            result = dlg.exec_()
            if result == QtWidgets.QDialog.Accepted:
                self.on_choose_btn()
            return
        dlg = WarningExecuteDialog()
        res = dlg.exec_()
        if res == QtWidgets.QDialog.Rejected:
            return
        self.progress_dialog.setValue(0)
        self.progress_dialog.show()
        self.thread = QtCore.QThread()
        self.worker = ParserSearchWorker(get_list_items(self.founded_list_widget))
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.progress_dialog.setValue)
        self.worker.finished.connect(self.on_finish_run_btn_2)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def on_finish_run_btn_2(self, res):
        self.list_group.setVisible(False)
        self.choose_group.setVisible(False)
        self.model.removeRows(0, self.model.rowCount())
        for key, value in res.items():
            self.model.appendRow([CenteredItem(key)] + [CenteredItem(v) for v in value.values()])

    def on_run_read_btn(self):
        if self.filename_searched == '':
            dlg = NotExecuteFileDialog()
            result = dlg.exec_()
            if result == QtWidgets.QDialog.Accepted:
                self.on_choose_btn()
            return
        self.progress_dialog.setValue(0)
        self.progress_dialog.show()
        self.thread = QtCore.QThread()
        self.worker = SearchReadWorker(self.filename_searched)
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.progress_dialog.setValue)
        self.worker.finished.connect(self.on_finish_read_search)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def on_finish_read_search(self, res):
        self.progress_dialog.close()
        self.list_group.setVisible(True)
        self.founded_list_widget.clear()
        for i, item in enumerate(res, start=1):
            self.founded_list_widget.addItem(f'{i}) {item}')

    def on_delete_btn(self):
        if self.choose_lbl.text():
            self.choose_lbl.setText('')
            self.filename = ''
        else:
            dialog = NotInputFileDialog()
            result = dialog.exec_()

    def on_choose_btn(self):
        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Выберите файл(файл должен быть создан этой программой)",
            "",
            "Текстовые файлы (*.txt);;Документы (*.docx);;Электронные таблицы (*.xlsx)",
            options=options
        )
        if filename:
            self.filename_searched = filename
            self.choose_lbl.setText(filename.split('/')[-1])

    def change_radio_btn_1(self):
        self.founded_list_widget.clear()
        self.choose_group.setVisible(True)
        self.list_group.setVisible(False)

    def change_radio_btn_2(self):
        items = [self.founded_list.item(i).text() for i in range(self.founded_list.count())]
        for item in items:
            self.founded_list_widget.addItem(item)
        self.choose_group.setVisible(False)
        self.list_group.setVisible(True)

    def open_file_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Выберите файл(поддерживается пока что только формат docx)",
            "",
            "Документы (*.docx)",
            options=options
        )
        if filename:
            self.filename = filename
            self.selected_file_lbl.setText(filename.split('/')[-1])

    def clear_selected_path_btn(self):
        if self.selected_file_lbl.text():
            self.selected_file_lbl.setText('')
            self.filename = ''
        else:
            dialog = NotInputFileDialog()
            result = dialog.exec_()

    def execute_read_btn(self):
        if self.filename == '':
            dlg = NotExecuteFileDialog()
            result = dlg.exec_()
            if result == QtWidgets.QDialog.Accepted:
                self.open_file_dialog()
            return
        self.progress_dialog.setValue(0)
        self.progress_dialog.show()
        self.thread = QtCore.QThread()
        self.worker = ReadWorker(self.filename)
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.progress_dialog.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def on_finished(self, result):
        self.progress_dialog.close()
        self.founded_list.clear()
        for i, item in enumerate(result, start=1):
            self.founded_list.addItem(f'{i}) {item}')
        dialog = SuccessReadDilog()
        dialog.save_clicked.connect(self.on_save_btn)
        dialog.to_clicked.connect(self.handle_to)
        result = dialog.exec_()

    def handle_to(self):
        items = [self.founded_list.item(i).text() for i in range(self.founded_list.count())]
        for item in items:
            self.founded_list_widget.addItem(item)
        self.tabWidget.setCurrentWidget(self.selenium_tab)

    def on_save_btn(self):
        if self.founded_list.count():
            options = QtWidgets.QFileDialog.Options()
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                'Выберите, куда сохранить файл',
                '',
                'Текстовые файлы (*.txt);;Документы (*.docx);;Электронные таблицы (*.xlsx)',
                options=options
            )
            if filename:
                if not (('.txt' in filename) or ('.docx' in filename) or ('.xlsx' in filename)):
                    filename = filename + _.split('*')[-1][:-1]
                self.save_filename = filename
                print(self.save_filename)
                self.progress_dialog.setValue(0)
                self.progress_dialog.show()
                self.thread = QtCore.QThread()
                self.worker = SaveFileWorker(self.save_filename, iter_all_items(self.founded_list),
                                             self.founded_list.count())
                self.worker.moveToThread(self.thread)
                self.worker.progress.connect(self.progress_dialog.setValue)
                self.worker.finished.connect(self.on_finished_save_btn)
                self.worker.finished.connect(self.thread.quit)
                self.worker.finished.connect(self.worker.deleteLater)
                self.thread.started.connect(self.worker.run)
                self.thread.start()
            return
        print("Not founded")

    def on_finished_save_btn(self):
        self.progress_dialog.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.showMaximized()
    sys.exit(app.exec_())
