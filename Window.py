import flet as ft

def main(page: ft.Page):
    page.title = "AI-SQL"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.add(ft.TextField(label="Username"))
    page.add(ft.TextField(label="Password", password=True, can_reveal_password=True))

    page.add(ft.ElevatedButton("Login", on_click=lambda e: print("Login clicked")))
    page.add(ft.ElevatedButton("Register", on_click=lambda e: print("Register clicked")))

    async def exit_click(e):
        await page.window.destroy()

    page.add(ft.ElevatedButton("Exit", on_click=exit_click))


ft.run(main)
