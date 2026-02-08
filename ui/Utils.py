import re

def clean_rows(rows) -> str:
    if isinstance(rows, list) and rows and isinstance(rows[0], list) and rows[0]:
        v = rows[0][0]
        if v is None:
            return "No results"
        s = re.sub(r"[{}]", "", str(v)).strip()
        return s
    return str(rows)
