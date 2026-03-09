import re

def clean_rows(rows) -> str:
    if isinstance(rows, list) and rows and isinstance(rows[0], list) and rows[0]:
        v = rows[0][0]
        if v is None:
            return "No results"
        s = re.sub(r"[{}]", "", str(v)).strip()
        return s
    return str(rows)

def clean_sql(raw_text: str) -> str:
    s = re.sub(r"\s+", " ", str(raw_text).strip().strip("`")).strip()
    if s.lower().startswith("sql:"):
        s = s[4:].strip()
    s = s.rstrip(";").strip()
    if not s:
        return ""
    if ";" in s:
        return ""
    if not s.lower().startswith("select "):
        return ""
    return s