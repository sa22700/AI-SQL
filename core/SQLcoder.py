# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import os
import sys
import json
import psycopg2
from llama_cpp import Llama
from ui.Utils import clean_sql
from core.DebugLog import log_error
from core.Connection import connect_read, cuda_available, estimate_n_gpu_layers

def load_model() -> Llama:
    vram_gb = cuda_available()
    n_gpu_layers = estimate_n_gpu_layers(vram_gb)
    model_path = os.getenv("LLM_MODEL")
    if not model_path:
        raise RuntimeError("LLM_MODEL environment variable is not set")
    llm = Llama(
        model_path=model_path,
        use_mmap=False,
        n_gpu_layers=n_gpu_layers,
        n_ctx=4096
    )
    return llm

def sql_driver(llm: Llama, question: str | None = None) -> dict:
    conn = None
    cursor = None
    devnull = None
    old_stderr = sys.stderr
    try:
        schema_path = os.getenv("SCHEMA")
        if not schema_path:
            return {"error": "SCHEMA environment variable is not set"}
        conn = connect_read()
        conn.set_session(readonly=True, autocommit=False)
        cursor = conn.cursor()
        try:
            devnull = open(os.devnull, "w")
            sys.stderr = devnull
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            prompt = (
                "You are a PostgreSQL SQL generator.\n"
                "Return exactly one valid PostgreSQL SELECT query.\n"
                "Do not explain anything.\n"
                "Do not return markdown.\n"
                "Do not return code fences.\n"
                "Use only tables and columns listed below.\n"
                "Never invent table names or column names.\n"
                "Use ILIKE for text matching when searching by part name.\n\n"
                "Schema:\n"
            )
            for table in schema:
                table_name = table["table"]
                prompt += f"\nTable: {table_name}\n"
                for col in table["columns"]:
                    col_name = col["name"]
                    description = ""
                    if col_name == "part_name":
                        description = " (part name, e.g. Spark Plug, Air Filter)"
                    elif col_name == "part_number":
                        description = " (unique part code)"
                    elif col_name == "category":
                        description = " (category of the part)"
                    elif col_name == "price":
                        description = " (price in euros)"
                    elif col_name == "id":
                        description = " (unique row id)"
                    prompt += f"- {col_name}{description}\n"
            if question is None:
                while True:
                    question = (input("Type your SQL question: ") or "").strip()
                    if question:
                        break
                    print("Question cannot be empty.")
            else:
                question = (question or "").strip()
                if not question:
                    return {"error": "Question cannot be empty"}
            full_prompt = (
                f"{prompt}\n"
                f"Question: {question}\n"
                f"SQL:\n"
            )
            output = llm(
                full_prompt,
                max_tokens=128,
                temperature=0.0,
                echo=False,
                stop=["```", "\n\n", "Question:", "Answer:"]
            )
            sql_query = clean_sql(output["choices"][0]["text"])
            if not sql_query:
                return {"error": "Model did not return valid SELECT SQL"}
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            return {
                "sql": sql_query,
                "rows": [list(row) for row in rows]
            }
        finally:
            sys.stderr = old_stderr
            if devnull is not None:
                devnull.close()

    except psycopg2.Error as e:
        log_error(f"Error in sql_driver: {e}")
        return {"error": str(e)}

    except Exception as e:
        log_error(f"Unexpected error in sql_driver: {e}")
        return {"error": str(e)}

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()