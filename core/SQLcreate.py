# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import json
import psycopg
from psycopg.types.json import Jsonb
from core.Connection import connect_write
from core.DebugLog import log_error
from core.SQLAuth import require_admin

def get_manufacturer_id(cursor, manufacturer: str | None) -> int | None:
    manufacturer = (manufacturer or "").strip()
    if not manufacturer:
        return None
    cursor.execute("""
        INSERT INTO manufacturers (name)
        VALUES (%s)
        ON CONFLICT (name)
        DO UPDATE SET name = EXCLUDED.name
        RETURNING id;
        """, (manufacturer,))
    return cursor.fetchone()[0]

def get_category_id(cursor, category: str | None) -> int | None:
    category = (category or "").strip()
    if not category:
        return None
    cursor.execute("""
        INSERT INTO categories (name)
        VALUES (%s)
        ON CONFLICT (name)
        DO UPDATE SET name = EXCLUDED.name
        RETURNING id;
        """,(category,))
    return cursor.fetchone()[0]

def insert_product(
    cursor,
    product_name: str | None,
    product_number: str | None,
    manufacturer: str | None,
    category: str | None,
    price: float | str | None,
    currency: str,
    attributes: dict | None
) -> dict:
    product_name = (product_name or "").strip()
    product_number = (product_number or "").strip() or None
    currency = (currency or "EUR").strip().upper()
    attributes = attributes or {}
    if not product_name:
        raise ValueError("Product name cannot be empty")
    if len(currency) != 3:
        raise ValueError("Currency must contain three letters")
    if not isinstance(attributes, dict):
        raise ValueError("Attributes must be a JSON object")
    parsed_price = None
    if price is not None and str(price).strip():
        try:
            parsed_price = float(price)

        except (TypeError, ValueError):
            raise ValueError("Price must be a number")

        if parsed_price < 0:
            raise ValueError("Price cannot be negative")
    manufacturer_id = get_manufacturer_id(cursor, manufacturer)
    category_id = get_category_id(cursor, category)
    cursor.execute("""
        INSERT INTO products (
            manufacturer_id,
            category_id,
            product_name,
            product_number,
            price,
            currency,
            attributes
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING
            id,
            product_name,
            product_number,
            price,
            currency,
            attributes;
        """,
        (
            manufacturer_id,
            category_id,
            product_name,
            product_number,
            parsed_price,
            currency,
            Jsonb(attributes)
        )
    )
    row = cursor.fetchone()
    return {
        "id": row[0],
        "product_name": row[1],
        "product_number": row[2],
        "price": row[3],
        "currency": row[4],
        "attributes": row[5],
        "manufacturer": manufacturer,
        "category": category
    }

def database(
    admin_username: str | None = None,
    admin_password: str | None = None,
    product_name: str | None = None,
    product_number: str | None = None,
    manufacturer: str | None = None,
    category: str | None = None,
    price: float | str | None = None,
    currency: str = "EUR",
    attributes: dict | None = None
) -> dict:
    interactive = (
        admin_username is None
        and admin_password is None
        and product_name is None
        and product_number is None
        and manufacturer is None
        and category is None
        and price is None
        and attributes is None
    )
    try:
        auth = require_admin(
            admin_username=admin_username,
            admin_password=admin_password,
            interactive=interactive
        )
        if not auth.get("ok"):
            return auth
        inserted_products = []
        with connect_write() as conn:
            with conn.cursor() as cursor:
                if interactive:
                    while True:
                        product_name = input("Product name: ").strip()
                        product_number = input("Product number (optional): ").strip()
                        manufacturer = input("Manufacturer (optional): ").strip()
                        category = input("Category (optional): ").strip()
                        price = input("Price (optional): ").strip()
                        currency = (input("Currency (default EUR): ").strip() or "EUR")
                        raw_attributes = input("Attributes as JSON (optional): ").strip()
                        if raw_attributes:
                            try:
                                attributes = json.loads(raw_attributes)

                            except json.JSONDecodeError:
                                print("Invalid attributes JSON.")
                                continue

                        else:
                            attributes = {}
                        try:
                            product = insert_product(
                                cursor=cursor,
                                product_name=product_name,
                                product_number=product_number,
                                manufacturer=manufacturer,
                                category=category,
                                price=price,
                                currency=currency,
                                attributes=attributes
                            )

                        except ValueError as e:
                            print(str(e))
                            continue

                        inserted_products.append(product)
                        add_more = input("Add more products? (y/n): ").strip().lower()
                        if add_more != "y":
                            break
                else:
                    product = insert_product(
                        cursor=cursor,
                        product_name=product_name,
                        product_number=product_number,
                        manufacturer=manufacturer,
                        category=category,
                        price=price,
                        currency=currency,
                        attributes=attributes
                    )
                    inserted_products.append(product)
        return {
            "ok": True,
            "inserted": len(inserted_products),
            "products": inserted_products
        }

    except EOFError:
        return {"error": "Input ended unexpectedly"}

    except KeyboardInterrupt:
        return {"error": "Cancelled"}

    except psycopg.errors.UniqueViolation:
        return {"error": "Product number already exists for this manufacturer"}

    except ValueError as e:
        return {"error": str(e)}

    except psycopg.Error as e:
        log_error(f"Database error in database(): {e}")
        return {"error": str(e)}