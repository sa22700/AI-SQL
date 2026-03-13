import flet as ft
from ui.Utils import clean_rows
from core.DebugLog import log_error

def show_query(page: ft.Page, state, api, go) -> None:
    page.clean()
    question_tf = ft.TextField(label="Question", multiline=True, min_lines=3, max_lines=6, width=600)
    status_txt = ft.Text("")
    result_tf = ft.Text("")

    async def run_click(e) -> None:
        if not question_tf.value:
            status_txt.value = "Question is missing"
            page.update()
            return
        status_txt.value = "Running..."
        page.update()
        try:
            loader = await api.aisql(state.username, state.password, question_tf.value)
            if loader.status_code != 200:
                status_txt.value = f"Error {loader.status_code}: {loader.text}"
                page.update()
                return
            data = loader.json()
            sql = data.get("sql")
            rows = data.get("rows")
            answer = clean_rows(rows)
            result_tf.value = f"Generated SQL:\n{sql}\n\nAnswer:\n{answer}"
            status_txt.value = "OK"
            page.update()

        except Exception as ex:
            log_error(f"Request failed: {ex}")
            status_txt.value = f"Request failed: {ex}"
            page.update()

    async def logout_click(e) -> None:
        state.username = ""
        state.password = ""
        go("login")

    async def exit_click(e) -> None:
        await page.window.destroy()

    async def back_click(e) -> None:
        go("main menu")

    page.add(
        ft.Column(
            [
                ft.Text(f"Logged in as: {state.username}"),
                question_tf,
                ft.Row(
                    [
                        ft.Button("Run", on_click=run_click),
                        ft.Button("Back", on_click=back_click),
                        ft.Button("Logout", on_click=logout_click),
                        ft.Button("Exit", on_click=exit_click)
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