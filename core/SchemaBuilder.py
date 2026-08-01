# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import psycopg
from core.Connection import connect_write
from core.DebugLog import log_error

def schema_builder() -> dict:
    try:
        with connect_write() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS manufacturers (
                        id BIGSERIAL PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE
                    );
                    """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS categories (
                        id BIGSERIAL PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE
                    );
                    """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        id BIGSERIAL PRIMARY KEY,
                        manufacturer_id BIGINT
                            REFERENCES manufacturers(id)
                            ON DELETE SET NULL,
                        category_id BIGINT
                            REFERENCES categories(id)
                            ON DELETE SET NULL,
                        product_name TEXT NOT NULL,
                        product_number TEXT,
                        price DOUBLE PRECISION
                            CHECK (price >= 0),
                        currency CHAR(3) NOT NULL
                            DEFAULT 'EUR',
                        attributes JSONB NOT NULL
                            DEFAULT '{}'::jsonb,
                        UNIQUE (
                            manufacturer_id,
                            product_number
                        )
                    );
                    """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS
                    products_manufacturer_id
                    ON products (manufacturer_id);
                    """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS
                    products_category_id
                    ON products (category_id);
                    """)
        return {"ok": True}

    except psycopg.Error as e:
        log_error(f"Error creating product schema: {e}")
        return {"error": str(e)}