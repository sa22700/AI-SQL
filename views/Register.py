# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import flet as ft
from core.DebugLog import log_error

def show_register(page: ft.Page, state, api, go) -> None:
    page.clean()
    new_user_tf = ft.TextField(label="New username", width=400)
    new_pass_tf = ft.TextField(label="New password", password=True, can_reveal_password=True, width=400)
    confirm_tf = ft.TextField(label="Confirm password", password=True, can_reveal_password=True, width=400)
    status_txt = ft.Text("")

    async def create_user_click(e) -> None:
        if not new_user_tf.value or not new_pass_tf.value or not confirm_tf.value:
            status_txt.value = "Missing fields"
            page.update()
            return
        payload = {
            "username": state.username,
            "password": state.password,
            "new_username": new_user_tf.value,
            "new_password": new_pass_tf.value,
            "confirm_password": confirm_tf.value
        }
        status_txt.value = "Creating user..."
        page.update()
        try:
            loader = await api.add_user(payload)
            if loader.status_code != 200:
                try:
                    status_txt.value = f"Create failed: {loader.json().get('detail')}"

                except Exception:
                    log_error(f"Create failed: {loader.text}")
                    status_txt.value = f"Create failed: {loader.text}"

                page.update()
                return
            data = loader.json()
            status_txt.value = f"OK: created user {data.get('username')}"
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
                new_user_tf,
                new_pass_tf,
                confirm_tf,
                ft.Row(
                    [
                        ft.Button("Create", on_click=create_user_click),
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
