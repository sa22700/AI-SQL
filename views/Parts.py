import flet as ft
from core.DebugLog import log_error

def show_delete_part(page: ft.Page, state, api, go) -> None:
    page.clean()
    table_tf = ft.TextField(label="Table name", width=400)
    part_tf = ft.TextField(label="Part number to delete", width=400)
    confirm_cb = ft.Checkbox(label="I confirm delete", value=False)
    status_txt = ft.Text("")

    async def do_delete_click(e) -> None:
        table_name = (table_tf.value or "").strip()
        part_number = (part_tf.value or "").strip()
        if not table_name:
            status_txt.value = "Table missing"
            page.update()
            return
        if not part_number:
            status_txt.value = "Part number missing"
            page.update()
            return
        if not confirm_cb.value:
            status_txt.value = "Confirm delete first"
            page.update()
            return
        payload = {
            "username": state.username,
            "password": state.password,
            "table_name": table_name,
            "part_to_delete": part_number,
        }
        status_txt.value = "Deleting..."
        page.update()
        try:
            loader = await api.delete_part(payload)
            data = loader.json() if loader is not None else {}
            if not (200 <= loader.status_code < 300) or data.get("error"):
                detail = data.get("detail") or data.get("error")
                status_txt.value = f"Delete failed: {detail}"
                page.update()
                return
            status_txt.value = f"OK: deleted {data.get('deleted')} from {data.get('table')}"
            confirm_cb.value = False
            part_tf.value = ""
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
                table_tf,
                part_tf,
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