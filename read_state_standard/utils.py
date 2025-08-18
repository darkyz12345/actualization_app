def clean_text(text: str) -> str:
    replacements = {
        '‘': '`', "'": '`', 'ʻ': '`', '’': '`',
        ' – ': '-', '- ': '-', '  ': ' ', '— ': '-'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def mult(data: list[bool]) -> bool:
    res = 1
    for item in data:
        res *= item
    return res