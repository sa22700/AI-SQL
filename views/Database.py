# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import flet as ft
import json
from core.DebugLog import log_error

def show_database(page: ft.Page, state, api, go) -> None:
    page.clean()
    page.scroll = ft.ScrollMode.ALWAYS
    rows_tf = ft.TextField(
        label="Rows (product_name;product_number;category;manufacturer;price per line)",
        multiline=True,
        min_lines=6,
        max_lines=10,
        width=700
    )
    status_txt = ft.Text("")
    result_tf = ft.TextField(
        label="Result",
        multiline=True,
        read_only=True,
        width=700,
        min_lines=10
    )

    async def run_db_click(e) -> None:
        rows = []
        for line in (rows_tf.value or "").splitlines():
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(";")]
            if len(parts) != 5:
                status_txt.value = f"Bad row format: {line}"
                page.update()
                return
            if not parts[0]:
                status_txt.value = "Product name is missing"
                page.update()
                return
            try:
                price = float(parts[4].replace(",", "."))
                if not 0 <= price < float("inf"):
                    raise ValueError()

            except ValueError:
                status_txt.value = f"Invalid price: {parts[4]}"
                page.update()
                return

            rows.append({
                "product_name": parts[0],
                "product_number": parts[1] or None,
                "category": parts[2] or None,
                "manufacturer": parts[3] or None,
                "price": price,
                "currency": "EUR",
                "attributes": {}
            })
        if not rows:
            status_txt.value = "No products provided"
            page.update()
            return
        status_txt.value = "Adding products..."
        page.update()
        results = []
        try:
            for row in rows:
                payload = {
                    "username": state.username,
                    "password": state.password,
                    **row
                }
                response = await api.database(payload)
                if response.status_code != 200:
                    status_txt.value = (
                        f"Added {len(results)} products. "
                        f"Error: {response.text}"
                    )
                    page.update()
                    return
                results.append(response.json())
            status_txt.value = (
                f"Successfully added {len(results)} products"
            )
            result_tf.value = json.dumps(
                results,
                indent=2,
                ensure_ascii=False
            )
            page.update()

        except Exception as ex:
            log_error(f"Request failed: {ex}")
            status_txt.value = (
                f"Added {len(results)} products. "
                f"Request failed: {ex}"
            )
            page.update()

    async def back_click(e) -> None:
        go("main menu")
    page.add(
        ft.Column(
            [
                ft.Text(f"Admin: {state.username}"),
                rows_tf,
                ft.Row(
                    [
                        ft.Button("Add products", on_click=run_db_click),
                        ft.Button("Back", on_click=back_click)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                status_txt,
                result_tf
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )
    page.update()