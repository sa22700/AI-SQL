import flet as ft

def show_delete(page: ft.Page, state, api, go):
    page.clean()
    username_del_tf = ft.TextField(label="Username to delete", width=400)
    confirm_cb = ft.Checkbox(label="I confirm delete", value=False)
    status_txt = ft.Text("")

    async def do_delete_click(e):
        user = (username_del_tf.value or "").strip()
        if not user:
            status_txt.value = "Username missing"
            page.update()
            return
        if not confirm_cb.value:
            status_txt.value = "Confirm delete first"
            page.update()
            return
        payload = {
            "admin_username": state.username,
            "admin_password": state.password,
            "username_to_delete": user
        }
        status_txt.value = "Deleting..."
        page.update()
        try:
            loader = await api.delete_user(payload)
            if not (200 <= loader.status_code < 300):
                try:
                    status_txt.value = f"Delete failed: {loader.json().get('detail')}"

                except Exception:
                    status_txt.value = f"Delete failed: {loader.text}"

                page.update()
                return
            data = loader.json()
            status_txt.value = f"OK: deleted {data.get('deleted')}"
            confirm_cb.value = False
            page.update()

        except Exception as ex:
            status_txt.value = f"Request failed: {ex}"
            page.update()

    async def back_click(e):
        go("query")

    page.add(
        ft.Column(
            [
                ft.Text(f"Admin: {state.username}"),
                username_del_tf,
                confirm_cb,
                ft.Row(
                    [
                        ft.ElevatedButton("Delete", on_click=do_delete_click),
                        ft.ElevatedButton("Back", on_click=back_click)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                status_txt
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )
    page.update()
