# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import os
import uvicorn
from core.DebugLog import log_error
from core.SchemaBuilder import schema_builder
from dotenv import load_dotenv
from core.CheckDB import check_users_table

load_dotenv()

def main() -> None:
    try:
        schema_result = schema_builder()
        if not schema_result.get("ok"):
            raise RuntimeError(
                "Schema creation failed: "
                f"{schema_result.get('error', 'Unknown error')}"
            )
        user_schema = check_users_table()
        if not user_schema.get("ok"):
            raise RuntimeError(
                f"User table creation failed: "
                f"{user_schema.get('error')}"
            )
        print("Database schema is ready.")
        app = os.environ['UVICORN_APP']
        host = os.environ['UVICORN_HOST']
        port = int(os.environ['UVICORN_PORT'])
        reload_ = True
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload_,
            log_level=os.environ['UVICORN_LOG_LEVEL'],
        )
    except Exception as ex:
        log_error(f"Error: {ex}")
        print(f"Error: {ex}")

if __name__ == "__main__":
    main()