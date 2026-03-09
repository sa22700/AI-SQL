import flet as ft
import json

def show_database(page: ft.Page, state, api, go) -> None:
    page.clean()
    table_tf = ft.TextField(label="Table name", width=400)
    create_cb = ft.Checkbox(label="Create table", value=True)
    fetch_cb = ft.Checkbox(label="Fetch after", value=True)
    rows_tf = ft.TextField(
        label="Rows (part_name;part_number;category;price per line)",
        multiline=True,
        min_lines=6,
        max_lines=10,
        width=700
    )
    status_txt = ft.Text("")
    result_tf = ft.TextField(label="Result", multiline=True, read_only=True, width=700, min_lines=10)

    async def run_db_click(e) -> None:
        table_name = (table_tf.value or "").strip()
        if not table_name:
            status_txt.value = "Table name missing"
            page.update()
            return
        rows = []
        for line in (rows_tf.value or "").splitlines():
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(";")]
            if len(parts) != 4:
                status_txt.value = f"Bad row format: {line}"
                page.update()
                return
            try:
                price = float(parts[3].replace(",", "."))

            except ValueError:
                status_txt.value = f"Bad price: {parts[3]}"
                page.update()
                return

            rows.append(
                {
                    "part_name": parts[0],
                    "part_number": parts[1],
                    "category": parts[2],
                    "price": price
                }
            )
        payload = {
            "username": state.username,
            "password": state.password,
            "create_table": bool(create_cb.value),
            "table_name": table_name,
            "rows": rows,
            "fetch": bool(fetch_cb.value)
        }
        status_txt.value = "Running..."
        page.update()
        try:
            loader = await api.database(payload)
            if loader.status_code != 200:
                try:
                    status_txt.value = f"DB failed: {loader.json().get('detail')}"

                except Exception:
                    status_txt.value = f"DB failed: {loader.text}"

                page.update()
                return
            data = loader.json()
            status_txt.value = "OK"
            result_tf.value = json.dumps(data, indent=2, ensure_ascii=False)
            page.update()

        except Exception as ex:
            status_txt.value = f"Request failed: {ex}"
            page.update()

    async def back_click(e) -> None:
        go("main menu")

    page.add(
        ft.Column(
            [
                ft.Text(f"Admin: {state.username}"),
                table_tf,
                ft.Row([create_cb, fetch_cb]),
                rows_tf,
                ft.Row(
                    [
                        ft.Button("Run DB", on_click=run_db_click),
                        ft.Button("Back", on_click=back_click)
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
