# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import psycopg
from psycopg import sql
from core.Connection import connect_write
from core.DebugLog import log_error
from core.SQLAuth import require_admin
from core.SQLcreate import get_manufacturer_id, get_category_id

def update_part(
    product_id: int | None = None,
    product_name: str | None = None,
    product_number: str | None = None,
    manufacturer: str | None = None,
    category: str | None = None,
    price: float | None = None,
    admin_username: str | None = None,
    admin_password: str | None = None,
    confirm: bool = True
) -> dict:
    interactive = (
        product_id is None
        and product_name is None
        and product_number is None
        and manufacturer is None
        and category is None
        and price is None
        and admin_username is None
        and admin_password is None
    )
    try:
        auth = require_admin(
            admin_username=admin_username,
            admin_password=admin_password,
            interactive=interactive
        )
        if not auth.get("ok"):
            return auth
        if interactive:
            raw_id = input("Product id to update: ").strip()
            try:
                product_id = int(raw_id)

            except ValueError:
                return {"error": "Invalid product id"}

            raw = input("New product name (empty = no change): ").strip()
            product_name = raw or None
            raw = input("New product number (empty = no change): ").strip()
            product_number = raw or None
            raw = input("New manufacturer (empty = no change): ").strip()
            manufacturer = raw or None
            raw = input("New category (empty = no change): ").strip()
            category = raw or None
            raw = input("New price (empty = no change): ").strip()
            if raw:
                try:
                    price = float(raw)

                except ValueError:
                    return {"error": "Invalid price"}

        try:
            product_id = int(product_id)

        except (TypeError, ValueError):
            return {"error": "Invalid product id"}

        if product_id <= 0:
            return {"error": "Invalid product id"}

        requested_changes = [
            product_name,
            product_number,
            manufacturer,
            category,
            price
        ]
        if all(value is None for value in requested_changes):
            return {"error": "Nothing to update"}
        if interactive:
            answer = (input(f"Update product {product_id}? (y/n): ")or "").strip().lower()
            if answer != "y":
                return {"error": "Cancelled"}
        elif not confirm:
            return {"error": "Confirmation required"}
        with connect_write() as conn:
            with conn.cursor() as cursor:
                sets = []
                params = []
                if product_name is not None:
                    product_name = product_name.strip()
                    if not product_name:
                        return {"error": "Product name cannot be empty"}
                    sets.append(sql.SQL("product_name = %s"))
                    params.append(product_name)
                if product_number is not None:
                    product_number = product_number.strip()
                    if product_number:
                        sets.append(sql.SQL("product_number = %s"))
                        params.append(product_number)
                if manufacturer is not None:
                    manufacturer_id = get_manufacturer_id(cursor, manufacturer)
                    sets.append(sql.SQL("manufacturer_id = %s"))
                    params.append(manufacturer_id)
                if category is not None:
                    category_id = get_category_id(cursor, category)
                    sets.append(sql.SQL("category_id = %s"))
                    params.append(category_id)
                if price is not None:
                    try:
                        price = float(price)

                    except (TypeError, ValueError):
                        return {"error": "Invalid price"}

                    if price < 0:
                        return {"error": "Price cannot be negative"}
                    sets.append(sql.SQL("price = %s"))
                    params.append(price)
                if not sets:
                    return {"error": "Nothing to update"}
                params.append(product_id)
                update_sql = (
                    sql.SQL("UPDATE products SET ")
                    + sql.SQL(", ").join(sets)
                    + sql.SQL("""
                        WHERE id = %s
                        RETURNING
                            id,
                            manufacturer_id,
                            category_id,
                            product_name,
                            product_number,
                            price;
                        """)
                )
                cursor.execute(update_sql, tuple(params))
                row = cursor.fetchone()
                if not row:
                    return {"error": "Product not found"}
                columns = [column[0] for column in cursor.description]
        return {
            "ok": True,
            "updated": dict(zip(columns, row))
        }

    except EOFError:
        return {"error": "Input ended unexpectedly"}

    except KeyboardInterrupt:
        return {"error": "Cancelled"}

    except psycopg.errors.UniqueViolation:
        return {"error": "Product number already exists for this manufacturer"}

    except psycopg.Error as e:
        log_error(f"Database error in update_part(): {e}")
        return {"error": str(e)}