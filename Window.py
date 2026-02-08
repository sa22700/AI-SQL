import os
import flet as ft
from ui.State import AppState
from ui.Api import ApiClient
from views.Login import show_login
from views.Query import show_query
from views.Register import show_register
from views.Delete import show_delete
from views.Database import show_database

API_BASE = os.getenv("API_BASE")

def main(page: ft.Page):
    page.title = "AI-SQL"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    state = AppState()
    api = ApiClient(API_BASE)

    def go(view: str):
        routes[view]()

    def route_login() -> None:
        show_login(page, state, api, go)

    def route_query() -> None:
        show_query(page, state, api, go)

    def route_register() -> None:
        show_register(page, state, api, go)

    def route_delete() -> None:
        show_delete(page, state, api, go)

    def route_database() -> None:
        show_database(page, state, api, go)

    routes = {
        "login": route_login,
        "query": route_query,
        "register": route_register,
        "delete": route_delete,
        "database": route_database
    }
    go("login")
ft.run(main)
