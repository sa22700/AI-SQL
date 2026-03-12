import re

def clean_rows(rows) -> str:
    if not isinstance(rows, list) or not rows:
        return "No results"
    lines = []
    for row in rows:
        if isinstance(row, list):
            lines.append(" | ".join(str(cell) for cell in row))
        else:
            lines.append(str(row))
    return "\n".join(lines)

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