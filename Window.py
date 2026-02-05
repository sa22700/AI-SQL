import flet as ft
import os
import httpx

API_BASE = os.getenv("API_BASE")

def main(page: ft.Page):
    page.title = "AI-SQL"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    state = {"username": "", "password": ""}

    def show_login():
        page.clean()
        username_tf = ft.TextField(label="Username", width=400)
        password_tf = ft.TextField(label="Password", password=True, can_reveal_password=True, width=400)
        status_txt = ft.Text("")

        async def login_click(e):
            if not username_tf.value or not password_tf.value:
                status_txt.value = "Username/password puuttuu"
                page.update()
                return
            payload = {"username": username_tf.value, "password": password_tf.value}
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    loader = await client.post(f"{API_BASE}/login", json=payload)
                if loader.status_code != 200:
                    try:
                        status_txt.value = f"Login failed: {loader.json().get('detail')}"
                    except Exception:
                        status_txt.value = f"Login failed: {loader.text}"
                    page.update()
                    return
                state["username"] = username_tf.value
                state["password"] = password_tf.value
                show_query()

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
                            ft.ElevatedButton("Exit", on_click=exit_click),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    status_txt,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        page.update()

    def show_query():
        page.clean()
        question_tf = ft.TextField(label="Question", multiline=True, min_lines=3, max_lines=6, width=600)
        status_txt = ft.Text("")
        result_tf = ft.TextField(label="Result", multiline=True, read_only=True, width=600, min_lines=8)

        async def run_click(e):
            if not question_tf.value:
                status_txt.value = "Question puuttuu"
                page.update()
                return
            if not API_BASE:
                status_txt.value = "API_BASE puuttuu ympäristömuuttujista"
                page.update()
                return
            payload = {
                "username": state["username"],
                "password": state["password"],
                "question": question_tf.value,
            }
            status_txt.value = "Running..."
            page.update()
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    loader = await client.post(f"{API_BASE}/aisql", json=payload)
                if loader.status_code != 200:
                    status_txt.value = f"Error {loader.status_code}: {loader.text}"
                    page.update()
                    return
                data = loader.json()
                result_tf.value = f"Question:\n{data.get('sql')}\n\nAnswer:\n{data.get('rows')}"
                status_txt.value = "OK"
                page.update()

            except Exception as ex:
                status_txt.value = f"Request failed: {ex}"
                page.update()

        async def logout_click(e):
            state["username"] = ""
            state["password"] = ""
            show_login()

        async def exit_click(e):
            await page.window.destroy()

        page.add(
            ft.Column(
                [
                    ft.Text(f"Logged in as: {state['username']}"),
                    question_tf,
                    ft.Row(
                        [
                            ft.ElevatedButton("Run", on_click=run_click),
                            ft.ElevatedButton("Logout", on_click=logout_click),
                            ft.ElevatedButton("Exit", on_click=exit_click),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    status_txt,
                    result_tf,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        page.update()
    show_login()
ft.run(main)
