# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

from core.SQLuser import ask_user
from core.SQLcreate import database
from core.SQLcoder import sql_driver, load_model
from core.AddUser import add_new_user
from core.DebugLog import log_error
from core.DelUser import delete_user
from core.DelTable import drop_table
from core.DelParts import delete_part
from core.UpdParts import update_part
from ui.Utils import clean_rows

def print_result(result: dict | None) -> None:
    if result is None:
        print("No result returned.")
        return
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    if result.get("ok"):
        print("Operation completed successfully.")
        for key, value in result.items():
            if key != "ok":
                print(f"{key}: {value}")
        return
    print(result)

def main_menu() -> None:
    llm = None
    while True:
        print("\n--- Main Menu ---")
        print("1. Run SQL AI (SQLcoder)")
        print("2. Create new table (admin only)")
        print("3. Add new user (admin only)")
        print("4. Delete user (admin only)")
        print("5. Delete table (admin only)")
        print("6. Delete parts (admin only)")
        print("7. Update parts (admin only)")
        print("0. Logout / Exit")
        while True:
            try:
                choice = int(input("Choose action: "))
                break

            except ValueError:
                log_error("Invalid choice. Please enter a number.")
                print("Invalid choice. Please enter a number.")

        if choice == 1:
            if llm is None:
                try:
                    print("Loading model...")
                    llm = load_model()
                    print("Model loaded.")

                except Exception as e:
                    log_error(f"Failed to load model: {e}")
                    print(f"Failed to load model: {e}")
                    continue
                    
            result = sql_driver(llm)
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(result["sql"])
                print(clean_rows(result.get("rows", [])))
        elif choice == 2:
            result = database()
            print_result(result)
        elif choice == 3:
            result = add_new_user()
            print_result(result)
        elif choice == 4:
            result = delete_user()
            print_result(result)
        elif choice == 5:
            result = drop_table()
            print_result(result)
        elif choice == 6:
            result = delete_part()
            print_result(result)
        elif choice == 7:
            result = update_part()
            print_result(result)
        elif choice == 0:
            print("Logging out. Goodbye!")
            break
        else:
            print("Invalid choice.")

def start() -> None:
    try:
        auth = ask_user()
        if isinstance(auth, dict):
            if auth.get("ok"):
                main_menu()
            else:
                msg = auth.get("error", "Login failure")
                print(msg)
                log_error(msg)
            return
        if auth:
            main_menu()
        else:
            print("Login failure")
            log_error("Login failure")

    except Exception as e:
        log_error(f"Unexpected error in start(): {e}")
        print(f"Unexpected error: {e}")

if __name__ == '__main__':
    start()
