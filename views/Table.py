import flet as ft

def show_delete_table(page: ft.Page, state, api, go) -> None:
    page.clean()
    table_del_tf = ft.TextField(label="Table to delete", width=400)
    confirm_cb = ft.Checkbox(label="I confirm delete", value=False)
    status_txt = ft.Text("")

    async def do_delete_click(e) -> None:
        table_name = (table_del_tf.value or "").strip()
        if not table_name:
            status_txt.value = "Table missing"
            page.update()
            return
        if not confirm_cb.value:
            status_txt.value = "Confirm delete first"
            page.update()
            return
        payload = {
            "admin_username": state.username,
            "admin_password": state.password,
            "table_name": table_name,
            "cascade": False,
            "confirm": False,
        }
        status_txt.value = "Deleting..."
        page.update()
        try:
            loader = await api.drop_table(payload)
            data = loader.json() if loader is not None else {}
            if not (200 <= loader.status_code < 300) or data.get("error"):
                detail = data.get("detail") or data.get("error") or getattr(loader, "text", "Unknown error")
                status_txt.value = f"Delete failed: {detail}"
                page.update()
                return
            status_txt.value = f"OK: dropped {data.get('dropped')}"
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
                table_del_tf,
                confirm_cb,
                ft.Row(
                    [
                        ft.Button("Delete", on_click=do_delete_click),
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