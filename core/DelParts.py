# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import psycopg
from core.Connection import connect_write
from core.DebugLog import log_error
from core.SQLAuth import require_admin

def delete_part(
    product_id: int | None = None,
    admin_username: str | None = None,
    admin_password: str | None = None,
    confirm: bool = False
) -> dict:
    interactive = (
        product_id is None
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
            raw_id = input("Product id to delete: ").strip()
            try:
                product_id = int(raw_id)

            except ValueError:
                return {"error": "Invalid product id"}

        try:
            product_id = int(product_id)

        except (TypeError, ValueError):
            return {"error": "Invalid product id"}

        if product_id <= 0:
            return {"error": "Invalid product id"}
        if interactive:
            answer = (input(f"Delete product {product_id}? (y/n): ")or "").strip().lower()
            if answer != "y":
                return {"error": "Cancelled"}
        elif not confirm:
            return {"error": "Confirmation required"}
        with connect_write() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM products
                    WHERE id = %s
                    RETURNING
                        id,
                        product_name,
                        product_number;
                    """,(product_id,))
                row = cursor.fetchone()
                if not row:
                    return {"error": "Product not found"}
        return {
            "ok": True,
            "deleted": {
                "id": row[0],
                "product_name": row[1],
                "product_number": row[2]
            }
        }

    except EOFError:
        return {"error": "Input ended unexpectedly"}

    except KeyboardInterrupt:
        return {"error": "Operation cancelled"}

    except psycopg.Error as e:
        log_error(f"Database error in delete_part(): {e}")
        return {"error": str(e)}