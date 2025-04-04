import json
import os
from DebugLog import log_error

def schema_reader(filepath=os.path.join(os.path.dirname(__file__), "schema.json")):
    if not os.path.exists(filepath):
        log_error(f"Schema file not found: {filepath}")
        return []

    with open(filepath, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            log_error(f"Error reading schema file: {filepath}")
            return []

def schema_builder(schema_data, filepath=os.path.join(os.path.dirname(__file__), "schema.json")):
    with open(filepath, "w") as f:
        json.dump(schema_data, f, indent=2)

def schema_tables(table_name, columns, filepath=os.path.join(os.path.dirname(__file__), "schema.json")):
    schema = schema_reader(filepath)

    if any(entry["table"] == table_name for entry in schema):
        print(f"Table '{table_name}' already exists in schema.")
        return

    schema.append({
        "table": table_name,
        "columns": columns
    })

    schema_builder(schema, filepath)
    print(f"Schema for table '{table_name}' saved.")

def column_builder():
    return [
        {"name": "id", "type": "SERIAL", "primary_key": True},
        {"name": "part_name", "type": "TEXT"},
        {"name": "part_number", "type": "TEXT", "unique": True},
        {"name": "category", "type": "TEXT"},
        {"name": "price", "type": "DOUBLE PRECISION"}
    ]
