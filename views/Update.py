# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import flet as ft
from core.DebugLog import log_error

def show_update_part(page: ft.Page, state, api, go) -> None:
    page.clean()
    product_id_tf = ft.TextField(label="Product ID", width=400)
    product_name_tf = ft.TextField(label="New product name (optional)", width=400)
    product_number_tf = ft.TextField(label="New product number (optional)", width=400)
    manufacturer_tf = ft.TextField(label="New manufacturer (optional)", width=400)
    category_tf = ft.TextField(label="New category (optional)", width=400)
    price_tf = ft.TextField(label="New price (optional)", width=400)
    confirm_cb = ft.Checkbox(label="I confirm update", value=False)
    status_txt = ft.Text("")

    async def do_update_click(e) -> None:
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
            status_txt.value = ("Confirm update first")
            page.update()
            return
        product_name = (product_name_tf.value or "").strip() or None
        product_number = (product_number_tf.value or "").strip() or None
        manufacturer = (manufacturer_tf.value or "").strip() or None
        category = (category_tf.value or "").strip() or None
        price_raw = (price_tf.value or "").strip()
        price = None
        if price_raw:
            try:
                price = float(price_raw.replace(",", "."))

            except ValueError:
                log_error(f"Invalid price: {price_raw}")
                status_txt.value = "Invalid price"
                page.update()
                return

            if price < 0:
                status_txt.value = "Price cannot be negative"
                page.update()
                return
        if (
            product_name is None
            and product_number is None
            and manufacturer is None
            and category is None
            and price is None
        ):
            status_txt.value = "Nothing to update"
            page.update()
            return
        payload = {
            "username": state.username,
            "password": state.password,
            "product_id": product_id,
            "product_name": product_name,
            "product_number": product_number,
            "manufacturer": manufacturer,
            "category": category,
            "price": price,
            "confirm": True
        }
        status_txt.value = "Updating..."
        page.update()
        try:
            loader = await api.update_part(payload)
            data = (loader.json() if loader is not None else {})
            if (loader is None or not 200 <= loader.status_code < 300) or data.get("error"):
                detail = (
                    data.get("detail")
                    or data.get("error")
                    or getattr(loader, "text", "Unknown error")
                )
                status_txt.value = f"Update failed: {detail}"
                page.update()
                return
            updated = data.get("updated", {})
            updated_id = updated.get("id", product_id)
            status_txt.value = f"OK: updated product {updated_id}"
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
                ft.Divider(),
                product_name_tf,
                product_number_tf,
                manufacturer_tf,
                category_tf,
                price_tf,
                confirm_cb,
                ft.Row(
                    [
                        ft.Button("Update", on_click=do_update_click),
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