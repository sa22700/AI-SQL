import json
import os
from core.DebugLog import log_error

SCHEMA_PATH = os.getenv('SCHEMA')

def schema_reader(filepath: str = SCHEMA_PATH) -> list:
    if not os.path.exists(filepath):
        log_error(f"Schema file not found: {filepath}")
        return []
    try:
        with open(filepath, "r", encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []

    except json.JSONDecodeError:
        log_error(f"Error reading schema file: {filepath}")
        return []

    except OSError as e:
        log_error(f"Error reading schema file: {filepath} ({e})")
        return []

def schema_builder(schema_data: list, filepath: str = SCHEMA_PATH ) -> dict:
    temp_path = filepath +'.tmp'
    try:
        with open(temp_path, "w", encoding='utf-8') as f:
            json.dump(schema_data, f, ensure_ascii=False, indent=2)
        os.replace(temp_path, filepath)
        return {'ok': True}

    except OSError as e:
        log_error(f"Error writing schema file: {filepath} ({e})")
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        except OSError:
            pass
        return {'error': str(e)}

def schema_tables(table_name: str, columns: list, filepath: str = SCHEMA_PATH, interactive: bool = False) -> dict:
    schema = schema_reader(filepath)
    exist = any((entry.get("table") == table_name) for entry in schema if isinstance(entry, dict))
    if exist:
        if interactive:
            print(f"Table '{table_name}' already exists in schema.")
        return {"ok": True, "action": "exists", "table": table_name}
    schema.append({'table': table_name, 'columns': columns})
    write_result = schema_builder(schema, filepath)
    if 'error' in write_result:
        return  {'error': write_result['error'], 'table': table_name}
    if interactive:
        print(f"Schema for table {table_name} saved.")
    return {'ok': True, 'action': 'created', 'table': table_name}

def column_builder() -> dict:
    return {
        "table": "",
        "columns": [
            {"name": "id",
             "type": "SERIAL",
             "primary_key": True
             },
            {"name": "part_name",
             "type": "TEXT"
             },
            {"name": "part_number",
             "type": "TEXT",
             "unique": True
             },
            {"name": "category",
             "type": "TEXT"
             },
            {"name": "price",
             "type": "DOUBLE PRECISION"
             }
        ]
    }
