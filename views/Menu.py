import flet as ft

def show_page(page: ft.Page, state, api, go):
    page.clean()

    status_txt = ft.Text("")

    async def logout_click(e):
        state.username = ""
        state.password = ""
        go("login")

    async def exit_click(e):
        await page.window.destroy()

    def nav(route: str):
        async def _handler(e):
            go(route)
        return _handler

    page.add(
        ft.Column(
            [
                ft.Text(f"Logged in as: {state.username}"),
                ft.Row(
                    [
                        ft.Button("Query", on_click=nav("query")),
                        ft.Button("Database", on_click=nav("database")),
                        ft.Button("Add user", on_click=nav("register")),
                        ft.Button("Delete user", on_click=nav("delete")),
                        ft.Button("Delete table", on_click=nav("table")),
                        ft.Button("Delete parts", on_click=nav("parts")),
                        ft.Button("Update parts", on_click=nav("update")),
                        ft.Button("Logout", on_click=logout_click),
                        ft.Button("Exit", on_click=exit_click),
                    ],
                    wrap=True,
                    spacing=10,
                    run_spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                status_txt,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )
    )
    page.update()
