# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import os
import psycopg
from contextlib import redirect_stderr
from llama_cpp import Llama
from core.Connection import connect_read
from core.DebugLog import log_error
from ui.Utils import clean_sql

def load_model() -> Llama:
    model_path = os.getenv("LLM_MODEL")
    if not model_path:
        raise RuntimeError("LLM_MODEL environment variable is not set")
    return Llama(
        model_path=model_path,
        use_mmap=True,
        n_gpu_layers=-1,
        n_ctx=8192,
        use_mlock=True,
        verbose=False
    )

def sql_driver(llm: Llama,question: str | None = None) -> dict:
    try:
        prompt_path = os.getenv("SQL_PROMPT")
        schema_context = os.getenv("SCHEMA_CONTEXT")
        if not prompt_path:
            return {"error": "SQL_PROMPT environment variable is not set"}
        if not schema_context:
            return {"error": "SCHEMA_CONTEXT environment variable is not set"}
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
        with open(prompt_path, "r", encoding="utf-8") as file:
            prompt = file.read().strip()
        with open(schema_context, "r", encoding="utf-8") as file:
            context = file.read().strip()
        if not prompt:
            return {"error": "SQL prompt file is empty"}
        if not context:
            return {"error": "Schema context file is empty"}
        full_prompt = (
            f"{prompt}\n\n"
            f"Database schema:\n"
            f"{context}\n\n"
            f"Question: {question}\n"
            f"SQL:\n"
        )
        with (open(os.devnull, "w") as devnull,
            redirect_stderr(devnull)):
            output = llm(
                full_prompt,
                temperature=0.0,
                max_tokens=256,
                echo=False,
                stop=["```", "\n\n", "Question:", "Answer:"]
            )
        sql_query = clean_sql(output["choices"][0]["text"])
        if not sql_query:
            return {"error": "Model did not return valid SELECT SQL"}
        if not sql_query.lstrip().casefold().startswith("select "):
            return {"error": "Only SELECT queries are allowed"}
        with connect_read() as conn:
            conn.read_only = True
            with conn.cursor() as cursor:
                cursor.execute(sql_query)
                columns = [description[0] for description in cursor.description]
                rows = [list(row) for row in cursor.fetchall()]
        return {
            "sql": sql_query,
            "columns": columns,
            "rows": rows
        }

    except FileNotFoundError as e:
        log_error(f"File error in sql_driver: {e}")
        return {"error": str(e)}

    except KeyboardInterrupt:
        return {"error": "Cancelled"}

    except RuntimeError as e:
        log_error(f"Error in sql_driver: {e}")
        return {"error": str(e)}

    except psycopg.Error as e:
        log_error(f"Database error in sql_driver: {e}")
        return {"error": str(e)}

    except Exception as e:
        log_error(
            f"Unexpected error in sql_driver: {e}"
        )
        return {"error": str(e)}