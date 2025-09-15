
Десктопное приложение для извлечения, обработки и управления государственными стандартами из различных форматов документов и веб-источников. [1](#0-0) 

## Основные возможности

- **Анализ документов**: Извлечение идентификаторов стандартов (ГОСТ, ISO, O'zDSt, UzTR) из PDF, DOCX, TXT и XLSX файлов с использованием регулярных выражений [2](#0-1) 
- **Многоформатная поддержка**: Обработка и генерация выходных данных в форматах PDF, DOCX, TXT и XLSX [3](#0-2) 
- **Веб-интеграция**: Поиск информации о стандартах в внешних базах данных через веб-скрапинг [4](#0-3) 
- **Графический интерфейс**: PyQt5-интерфейс с вкладочным рабочим процессом [5](#0-4) 
- **Пакетная обработка**: Обработка множественных стандартов одновременно с отслеживанием прогресса [6](#0-5) 

## Технологический стек

- **GUI Framework**: PyQt5 для компонентов десктопного интерфейса
- **Обработка документов**: PyMuPDF, python-docx, openpyxl для работы с различными форматами
- **Веб-автоматизация**: Selenium WebDriver с BeautifulSoup4 для парсинга HTML
- **Архитектура**: Многопоточная обработка с использованием Qt threading model [7](#0-6) 

## Архитектура приложения

Приложение следует слоистой архитектуре с четким разделением между пользовательским интерфейсом, движком обработки и внешними интеграциями:

- **Слой представления**: MainWindow и UI диалоги [8](#0-7) 
- **Слой обработки**: Пакет `read_state_standard` с функциями извлечения и обработки данных [9](#0-8) 
- **Фоновые воркеры**: Специализированные классы для поддержания отзывчивости UI [10](#0-9) 

## Поддерживаемые форматы стандартов

- **ГОСТ**: Российские государственные стандарты (ГОСТ, ГОСТ Р, ГОСТ ISO и др.)
- **ISO**: Международные стандарты ISO
- **O'z DSt**: Узбекские национальные стандарты
- **UzTR**: Технические регламенты Узбекистана [11](#0-10) 

## Установка и запуск

Приложение поддерживает автоматическую сборку исполняемых файлов для Windows через CI/CD с использованием PyInstaller.

**Notes**

Приложение использует многопоточную архитектуру Qt для обеспечения отзывчивости интерфейса во время длительных операций обработки документов. Основной движок обработки находится в пакете `read_state_standard`, который предоставляет унифицированный API для работы с различными форматами документов и извлечения стандартов с помощью регулярных выражений.

Wiki pages you might want to explore:
- [Overview (darkyz12345/actualization_app)](/wiki/darkyz12345/actualization_app#1)
- [Application Architecture (darkyz12345/actualization_app)](/wiki/darkyz12345/actualization_app#2)
- [Document Processing Engine (darkyz12345/actualization_app)](/wiki/darkyz12345/actualization_app#3)

### Citations

**File:** main.py (L1-31)
```python
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
```

**File:** read_state_standard/read_data.py (L21-25)
```python
    data = {'O`zDSt': r'(O`z DSt \S+|O`zDSt \S+)',
            'O’zDSt': r'(O’z DSt \S+|O’zDSt \S+)',
            'ГОСТ': r'(ГОСТ ISO \S+|ГОСТ Р МЭК \S+|ГОСТ Р \S+|ГОСТ IEC \S+|ГОСТ МЭК \S+|ГОСТ EN \S+|ГОСТ \S+|ГОСТ\S+)',
            'ISO': r'(ISO \S+)',
            'UzTR.': r'(UzTR.\S+)'}
```

**File:** read_state_standard/read_data.py (L44-101)
```python
def save_to_txt(standards: Iterator[str], destination: str, length: int, progress_bar: pyqtSignal):
    standards_iter = enumerate(standards, start=1)
    if '.txt' in destination:
        with open(destination, 'w', encoding='utf-8') as file:
            for i, standard in standards_iter:
                file.write(f'{i}) {standard}\n')
                time.sleep(0.0005)
                progress_percent = int(i / length * 100)
                progress_bar.emit(progress_percent)
        return
    elif '.xlsx' in destination:
        center_align = Alignment(horizontal='center', vertical='center')
        wb = Workbook()
        ws = wb.active
        ws['A1'] = '№'
        ws['B1'] = 'Найденные ГОСТЫ'
        ws.title = 'ГОСТы'
        for i, standard in standards_iter:
            ws.append([i, standard])
            time.sleep(0.0005)
            progress_percent = int(i / length * 100)
            progress_bar.emit(progress_percent)
        for row in ws['A']:
            row.alignment = center_align
        for row in ws['B']:
            row.alignment = center_align
        for col in ws.columns:
            max_length = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = max_length + 2  # +2 для отступа
        wb.save(destination)
        return
    document = Document()
    document.add_paragraph('Найденные ГОСТы').alignment = WD_ALIGN_PARAGRAPH.CENTER
    table = document.add_table(1, 2, "Table Grid")
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "№"
    hdr_cells[1].text = 'Название ГОСТа'
    for cell in hdr_cells:
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for paragraph in cell.paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for i, standard in standards_iter:
        row_cells = table.add_row().cells
        row_cells[0].text = str(i)
        row_cells[1].text = standard
        time.sleep(0.0005)
        for cell in row_cells:
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for paragraph in cell.paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        progress_percent = int(i / length * 100)
        progress_bar.emit(progress_percent)
    document.save(destination)
    return
```

**File:** read_state_standard/__init__.py (L1-4)
```python
from .read_data import read_data_from_docx, read_standards_from_txt, save_to_txt, read_data_for_search
from .selenium_search import get_info_st_list
from .save_table import save_table_to_file
from .read_pdf import read_data_from_pdf
```

**File:** ui/workers/workers.py (L1-66)
```python
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
```

**File:** read_state_standard/read_pdf.py (L14-20)
```python
    data = {
        'O`zDSt': r'(O`z DSt \S+|O`zDSt \S+)',
        'O’zDSt': r"(O’z DSt \S+|O’zDSt \S+|O'z DSt \S+|O'zDSt \S+)",
        'ГОСТ':   r'(ГОСТ ISO \S+|ГОСТ Р МЭК \S+|ГОСТ Р \S+|ГОСТ IEC \S+|ГОСТ МЭК \S+|ГОСТ EN \S+|ГОСТ \S+|ГОСТ\S+)',
        'ISO':    r'(ISO \S+)',
        'UzTR.':  r'(UzTR.\S+)'
    }
```
