import flet as ft

def show_update_part(page: ft.Page, state, api, go) -> None:
    page.clean()
    table_tf = ft.TextField(label="Table name", width=400)
    partnum_tf = ft.TextField(label="Part number", width=400)
    partname_tf = ft.TextField(label="New part name (optional)", width=400)
    category_tf = ft.TextField(label="New category (optional)", width=400)
    price_tf = ft.TextField(label="New price (optional)", width=400)
    confirm_cb = ft.Checkbox(label="I confirm update", value=False)
    status_txt = ft.Text("")

    async def do_update_click(e) -> None:
        table_name = (table_tf.value or "").strip()
        part_number = (partnum_tf.value or "").strip()
        if not table_name:
            status_txt.value = "Table missing"
            page.update()
            return
        if not part_number:
            status_txt.value = "Part number missing"
            page.update()
            return
        if not confirm_cb.value:
            status_txt.value = "Confirm update first"
            page.update()
            return
        part_name = (partname_tf.value or "").strip()
        category = (category_tf.value or "").strip()
        price_raw = (price_tf.value or "").strip()
        part_name = part_name if part_name != "" else None
        category = category if category != "" else None
        price = None
        if price_raw != "":
            try:
                price = float(price_raw)

            except ValueError:
                status_txt.value = "Invalid price"
                page.update()
                return

        if part_name is None and category is None and price is None:
            status_txt.value = "Nothing to update"
            page.update()
            return
        payload = {
            "admin_username": state.username,
            "admin_password": state.password,
            "table_name": table_name,
            "part_number": part_number,
            "part_name": part_name,
            "category": category,
            "price": price,
            "confirm": False
        }
        status_txt.value = "Updating..."
        page.update()
        try:
            loader = await api.update_part(payload)
            data = loader.json() if loader is not None else {}
            if not (200 <= loader.status_code < 300) or data.get("error"):
                detail = data.get("detail") or data.get("error") or getattr(loader, "text", "Unknown error")
                status_txt.value = f"Update failed: {detail}"
                page.update()
                return
            status_txt.value = "OK: updated"
            confirm_cb.value = False
            page.update()

        except Exception as ex:
            status_txt.value = f"Request failed: {ex}"
            page.update()

    async def back_click(e) -> None:
        go("main menu")

    page.add(
        ft.Column(
            [
                ft.Text(f"Admin: {state.username}"),
                table_tf,
                partnum_tf,
                ft.Divider(),
                partname_tf,
                category_tf,
                price_tf,
                confirm_cb,
                ft.Row(
                    [
                        ft.Button("Update", on_click=do_update_click),
                        ft.Button("Back", on_click=back_click),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                status_txt,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )
    page.update()