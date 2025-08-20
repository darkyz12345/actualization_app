import re
import fitz  # PyMuPDF
from PyQt5.QtCore import pyqtSignal

def read_data_from_pdf(source_path: str, progress_bar: pyqtSignal) -> list[str]:
    """
    Reads state standard names from a .pdf file.

    :param source_path: Path to the source .pdf file containing the state standard names.
    :param progress_bar: PyQt signal to emit progress percentage.
    :return: A list of unique state standard names read from the source file.
    """
    # Словарь шаблонов (как у тебя в docx-версии)
    data = {
        'O`zDSt': r'(O`z DSt \S+|O`zDSt \S+)',
        'O’zDSt': r"(O’z DSt \S+|O’zDSt \S+|O'z DSt \S+|O'zDSt \S+)",
        'ГОСТ':   r'(ГОСТ ISO \S+|ГОСТ Р МЭК \S+|ГОСТ Р \S+|ГОСТ IEC \S+|ГОСТ МЭК \S+|ГОСТ EN \S+|ГОСТ \S+|ГОСТ\S+)',
        'ISO':    r'(ISO \S+)',
        'UzTR.':  r'(UzTR.\S+)'
    }

    doc = fitz.open(source_path)
    length = len(doc)
    standard_set = set()

    for i, page in enumerate(doc, start=1):
        text = page.get_text("text")
        for pattern in data.values():
            matches = re.findall(pattern, text)
            standard_set.update(matches)

        # Прогресс
        progress_percent = int(i / length * 100)
        progress_bar.emit(progress_percent)

    # Нормализация (приводим варианты к единому виду)
    normalized = []
    for s in standard_set:
        s = s.replace("’", "'").replace("`", "'")  # разные апострофы
        s = re.sub(r"\s+", " ", s)                 # убрать лишние пробелы
        s = s.replace("O'zDst", "O'z DSt").replace("O’zDSt", "O'z DSt").replace("O’z DSt", "O'z DSt")
        normalized.append(s.strip())

    return sorted(set(normalized))
