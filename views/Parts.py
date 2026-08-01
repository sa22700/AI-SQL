# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import flet as ft
from core.DebugLog import log_error

def show_delete_part(page: ft.Page, state, api, go) -> None:
    page.clean()
    product_id_tf = ft.TextField(label="Product ID",width=400)
    confirm_cb = ft.Checkbox(label="I confirm delete",value=False)
    status_txt = ft.Text("")

    async def do_delete_click(e) -> None:
        raw_product_id = (product_id_tf.value or "").strip()
        try:
            product_id = int(raw_product_id)

        except ValueError:
            status_txt.value = "Invalid product ID"
            page.update()
            return

        if product_id <= 0:
            status_txt.value = "Invalid product ID"
            page.update()
            return
        if not confirm_cb.value:
            status_txt.value = "Confirm delete first"
            page.update()
            return
        payload = {
            "username": state.username,
            "password": state.password,
            "product_id": product_id,
            "confirm": True
        }
        status_txt.value = "Deleting..."
        page.update()
        try:
            loader = await api.delete_part(payload)
            data = (loader.json() if loader is not None else {})
            if (loader is None or not (200 <= loader.status_code < 300) or data.get("error")):
                detail = (
                    data.get("detail")
                    or data.get("error")
                    or getattr(loader, "text", "Unknown error")
                )
                status_txt.value = f"Delete failed: {detail}"
                page.update()
                return
            deleted = data.get("deleted", {})
            product_name = deleted.get("product_name","Unknown product")
            deleted_id = deleted.get("id", product_id)
            status_txt.value = f"OK: deleted {product_name} (ID {deleted_id}"
            product_id_tf.value = ""
            confirm_cb.value = False
            page.update()

        except Exception as ex:
            log_error(f"Request failed: {ex}")
            status_txt.value = f"Request failed: {ex}"
            page.update()

    async def back_click(e) -> None:
        go("main menu")

    page.add(
        ft.Column(
            [
                ft.Text(f"Admin: {state.username}"),
                product_id_tf,
                confirm_cb,
                ft.Row(
                    [
                        ft.Button("Delete", on_click=do_delete_click),
                        ft.Button("Back", on_click=back_click)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                status_txt
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )
    page.update()