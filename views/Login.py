import flet as ft

def show_login(page: ft.Page, state, api, go):
    page.clean()
    username_tf = ft.TextField(label="Username", width=400)
    password_tf = ft.TextField(label="Password", password=True, can_reveal_password=True, width=400)
    status_txt = ft.Text("")

    async def login_click(e):
        if not username_tf.value or not password_tf.value:
            status_txt.value = "Username or password is missing"
            page.update()
            return
        try:
            loader = await api.login(username_tf.value, password_tf.value)
            if loader.status_code != 200:
                try:
                    status_txt.value = f"Login failed: {loader.json().get('detail')}"

                except Exception:
                    status_txt.value = f"Login failed: {loader.text}"

                page.update()
                return
            state.username = username_tf.value
            state.password = password_tf.value
            go("query")

        except Exception as ex:
            status_txt.value = f"Request failed: {ex}"
            page.update()

    async def exit_click(e):
        await page.window.destroy()

    page.add(
        ft.Column(
            [
                username_tf,
                password_tf,
                ft.Row(
                    [
                        ft.ElevatedButton("Login", on_click=login_click),
                        ft.ElevatedButton("Exit", on_click=exit_click)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                status_txt
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )
    page.update()