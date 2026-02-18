import flet as ft
import asyncio
import threading
from ui.Utils import clean_rows
from ui.Whisper import record_audio, transcribe_audio, SR

def show_query(page: ft.Page, state, api, go):
    page.clean()
    question_tf = ft.TextField(label="Question", multiline=True, min_lines=3, max_lines=6, width=600)
    status_txt = ft.Text("")
    result_tf = ft.Text(label="Result", multiline=True, read_only=True, width=600, min_lines=8)
    record_btn = ft.Button("Record")
    rec_state = {
        "recording": False,
        "stop_event": None,
        "task": None
    }

    async def _record_worker(stop_event: threading.Event):
        audio = await asyncio.to_thread(record_audio, SR, stop_event)
        text = await asyncio.to_thread(transcribe_audio, audio, "en")
        question_tf.value = text
        status_txt.value = "Speech OK"
        rec_state["recording"] = False
        rec_state["stop_event"] = None
        rec_state["task"] = None
        record_btn.text = "Record"
        page.update()

    async def record_toggle(e):
        if not rec_state["recording"]:
            rec_state["recording"] = True
            rec_state["stop_event"] = threading.Event()
            record_btn.text = "Stop"
            status_txt.value = "Recording..."
            page.update()
            rec_state["task"] = asyncio.create_task(_record_worker(rec_state["stop_event"]))
            return
        if rec_state["stop_event"] is not None:
            status_txt.value = "Stopping..."
            rec_state["stop_event"].set()
            page.update()
    record_btn.on_click = record_toggle

    async def run_click(e):
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
            status_txt.value = f"Request failed: {ex}"
            page.update()

    async def logout_click(e):
        state.username = ""
        state.password = ""
        go("login")

    async def exit_click(e):
        await page.window.destroy()

    async def go_database(e):
        go("database")

    async def go_register(e):
        go("register")

    async def go_delete(e):
        go("delete")

    page.add(
        ft.Column(
            [
                ft.Text(f"Logged in as: {state.username}"),
                question_tf,
                ft.Row(
                    [
                        record_btn,
                        ft.Button("Run", on_click=run_click),
                        ft.Button("Database", on_click=go_database),
                        ft.Button("Add user", on_click=go_register),
                        ft.Button("Delete user", on_click=go_delete),
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
